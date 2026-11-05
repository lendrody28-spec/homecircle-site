"""Read aloud: lines, clip manifest, sync check, clip maker.

Clips are DRAFTS until Hale approves the voice licences and the wording is locked.
Usage:
  python3 tools/ra.py make  [--only ID,ID] [--voices A,B]   # engines run in their own venvs (tools/tts/gen.py)
  python3 tools/ra.py check                                 # also run by build.py
"""
import hashlib, html.parser, json, os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tools" / "audio-manifest.json"
AUDIO = ROOT / "assets" / "audio"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FORBIDDEN = {"AU": [r"\b911\b", r"\b988\b", r"nine one one", r"nine eight eight"], "US": [r"\b000\b", r"triple zero", r"13 11 14", r"thirteen,? eleven,? fourteen", r"(?<!Crisis )(?<!Crisis &amp; )(?<!Crisis & )\bLifeline\b"]}

def norm(s): return re.sub(r"\s+", " ", s).strip()

def key(text):  # FNV-1a 32-bit, same as readaloud.js key()
    h = 0x811C9DC5
    for ch in norm(text):
        for unit in ch.encode("utf-16-le").__iter__() and [ord(ch)] if ord(ch) < 0x10000 else _surrogates(ch):
            h ^= unit; h = (h * 0x01000193) & 0xFFFFFFFF
    return f"{h:08x}"

def _surrogates(ch):
    c = ord(ch) - 0x10000
    return [0xD800 + (c >> 10), 0xDC00 + (c & 0x3FF)]

class _Node:
    def __init__(self, tag, attrs, parent):
        self.tag = tag.upper(); self.cls = (dict(attrs).get("class") or "").split(); self.kids = []; self.parent = parent
class _Tree(html.parser.HTMLParser):
    """Body fragment -> element tree (text nodes are str), enough to mirror readaloud.js textOf()/chunksOf()."""
    def __init__(self):
        super().__init__(convert_charrefs=True); self.root = _Node("ROOT", [], None); self.cur = self.root
    def handle_starttag(self, tag, attrs):
        n = _Node(tag, attrs, self.cur); self.cur.kids.append(n)
        if tag not in VOID: self.cur = n
    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(_Node(tag, attrs, self.cur))
    def handle_endtag(self, tag):
        n = self.cur
        while n is not self.root and n.tag != tag.upper(): n = n.parent
        if n is not self.root: self.cur = n.parent
    def handle_data(self, d): self.cur.kids.append(d)

HEAD = re.compile(r"^(H[1-6]|SUMMARY)$")
def _stop_after(out, frm):
    for i in range(len(out) - 1, frm - 1, -1):
        if re.search(r"\S", out[i]):
            if not re.search(r"[.!?:;,]\s*$", out[i]): out[i] = re.sub(r"\s*$", ".", out[i], count=1)
            return

def text_of(node, skip=()):
    """Same as readaloud.js textOf(): text nodes joined by a space; skips script/style/.ra-skip/.tag; headings end with a full stop."""
    out = []
    def walk(n):
        for c in n.kids:
            if isinstance(c, str): out.append(c)
            elif c.tag not in ("SCRIPT", "STYLE") and "ra-skip" not in c.cls and "tag" not in c.cls and c not in skip:
                frm = len(out); walk(c)
                if HEAD.match(c.tag): _stop_after(out, frm)
    walk(node)
    t = norm(" ".join(out))
    if HEAD.match(node.tag):
        o = [t]; _stop_after(o, 0); t = o[0]
    return t

def page_chunks(body):
    """Same as readaloud.js chunksOf(): children, a .grid split into cards, each card's <details>/.state-line read separately."""
    p = _Tree(); p.feed(body); p.close(); out = []
    for c in p.root.kids:
        if isinstance(c, str) or "ra-bar" in c.cls or "ra-skip" in c.cls: continue
        if "grid" in c.cls:
            for k in c.kids:
                if isinstance(k, str) or "ra-skip" in k.cls: continue
                more = [d for d in k.kids if not isinstance(d, str) and (d.tag == "DETAILS" or "state-line" in d.cls)]
                out.append(text_of(k, more)); out += [text_of(d) for d in more]
        else: out.append(text_of(c))
    return [t for t in out if t]

def node(js):
    return json.loads(subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, check=True).stdout)

def speakable_all(texts):
    return node("const R=require('./assets/readaloud.js');process.stdout.write(JSON.stringify(%s.map(R.speakable)))" % json.dumps(texts))

def kai_lines(region):
    js = """global.self=global;require('./assets/kai-data.js');const C=require('./assets/kai-crisis.js');const K=require('./assets/kai-engine.js');
const B=K.BUTTON_COPY||{};const out=[];const add=(id,t)=>{if(t&&!out.some(x=>x.text===t))out.push({id,text:t})};
add('kai.firstOpen',B.firstOpen);
for(const id of ['struggling','cravings','meeting']){const r=K.buttonReply(id,{});add('kai.start.'+id,r&&r.text)}
const R=C.region(%s).replies;for(const k in R)add('kai.crisis.'+k,R[k]);
process.stdout.write(JSON.stringify(out))""" % json.dumps(region)
    return node(js)

def current_lines(region, help_body):
    lines = kai_lines(region)
    if help_body is not None:
        lines += [{"id": f"help.{i:02d}", "text": t} for i, t in enumerate(page_chunks(help_body))]
    return lines

def load():
    return json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"lines": [], "voices": {}}

def voice_id(vi):
    """Everything that shapes the sound. Part of the clip's hashed name, so a settings change re-records."""
    keys = ("engine", "package", "weights", "lang", "voice", "speed", "loudnorm", "codec")
    return json.dumps({k: vi.get(k) for k in keys}, sort_keys=True)

def clip_name(vi, spoken):
    return hashlib.sha256((voice_id(vi) + "\n" + spoken).encode()).hexdigest()[:12] + ".mp3"

def check(region, lines):
    """Raise SystemExit on any mismatch. Returns (missing list, report)."""
    m = load(); errs, missing = [], []
    if m.get("region") and m["region"] != region: errs.append(f"manifest is for {m['region']}, site is {region}")
    by_id = {l["id"]: l for l in m.get("lines", [])}
    cur_ids = {l["id"] for l in lines}
    voices = m.get("voices", {})
    spoken_now = dict(zip([l["id"] for l in lines], speakable_all([l["text"] for l in lines]))) if lines else {}
    for l in m.get("lines", []):
        for pat in FORBIDDEN[region]:
            if re.search(pat, l["text"], re.I) or re.search(pat, l.get("spoken", ""), re.I):
                errs.append(f"{l['id']}: {region} clip text contains forbidden {pat!r} (cross-country)")
    for l in lines:
        e = by_id.get(l["id"])
        if not e:
            missing.append(l["id"]); continue
        if e["text"] != l["text"]:
            errs.append(f"{l['id']}: text changed (clip says {e['text'][:60]!r}, page says {l['text'][:60]!r})"); continue
        if e["spoken"] != spoken_now[l["id"]]:
            errs.append(f"{l['id']}: spoken script is stale")
        for v in voices:
            c = e.get("clips", {}).get(v)
            if not c: missing.append(f"{l['id']} [{v}]"); continue
            f = AUDIO / c["file"]
            if c["file"] != clip_name(voices[v], e["spoken"]): errs.append(f"{l['id']} [{v}]: clip name doesn't match its text hash")
            elif not f.exists(): errs.append(f"{l['id']} [{v}]: {c['file']} missing")
            elif hashlib.sha256(f.read_bytes()).hexdigest() != c["sha256"]: errs.append(f"{l['id']} [{v}]: file contents changed")
    stale = [i for i in by_id if i not in cur_ids and not by_id[i].get("sample")]
    for i in stale: errs.append(f"{i}: clip for a line that no longer exists")
    if m.get("complete") and missing: errs.append("lines without a clip in every voice: " + ", ".join(missing))
    if errs: raise SystemExit("read-aloud clip check FAILED:\n  " + "\n  ".join(errs))
    return missing

def page_clips(lines_on_page, base):
    """JSON for one page: only this site's manifest, only lines on this page, both voices."""
    m = load(); by_text = {l["text"]: l for l in m.get("lines", [])}
    out = {"clips": {v: {} for v in m.get("voices", {})}, "voices": {}}
    for t in lines_on_page:
        e = by_text.get(t)
        if not e: continue
        for v, c in e.get("clips", {}).items():
            out["clips"].setdefault(v, {})[key(t)] = c["file"]
    s = m.get("sampleText")
    if s: out["voices"]["sample"] = key(s)
    out["clips"] = {v: c for v, c in out["clips"].items() if c}
    if not out["clips"]: return ""
    j = json.dumps(out, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="ra-clips" data-base="{base}">{j}</script>'

def sizes(lines_on_page):
    m = load(); by_text = {l["text"]: l for l in m.get("lines", [])}; tot = {}
    for t in set(lines_on_page):
        for v, c in by_text.get(t, {}).get("clips", {}).items(): tot[v] = tot.get(v, 0) + c["bytes"]
    return tot

def _measure(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    t = r.stderr[r.stderr.rindex("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", t).group(1)), float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", t).group(1))

def _loudnorm(wav, out, ln):
    """Two-pass loudness normalisation to ln["I"] LUFS with a true-peak ceiling of ln["TP"] dBTP, then mono MP3 48 kbps CBR.
    Pass 1 measures the source (EBU R128). Pass 2 applies the gain plus a 4x-oversampled peak limiter.
    The encoded file is re-measured and the gain/limiter corrected (max 10 rounds) so encoder overshoot cannot slip through."""
    I, TP = ln["I"], ln["TP"]
    mi, _ = _measure(wav)
    gain, lim = I - mi, TP - 1.5
    for _ in range(10):
        af = f"aresample=96000,volume={gain:.2f}dB,alimiter=limit={10 ** (lim / 20):.4f}:attack=1:release=60:level=false,aresample=24000"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(wav), "-af", af, "-ac", "1", "-c:a", "libmp3lame", "-b:a", "48k",
                        "-id3v2_version", "0", "-map_metadata", "-1", "-fflags", "+bitexact", str(out)], check=True)
        oi, otp = _measure(out)
        if abs(oi - I) <= 0.5 and otp <= TP: return oi, otp
        if otp > TP: lim -= (otp - TP) + 0.3
        gain += I - oi
    return oi, otp

def synth(vi, jobs):
    """jobs: [(spoken, out_mp3)]. Runs the engine in its own venv (tools/tts/gen.py)."""
    if not jobs: return
    tmp = Path(os.environ.get("RA_TMP", "/workspace/tts-work/ra-gen")); tmp.mkdir(parents=True, exist_ok=True); tmp.mkdir(exist_ok=True)
    js = [{"spoken": sp, "wav": str(tmp / (Path(o).stem + ".wav"))} for sp, o in jobs]
    py = os.environ.get(vi["venvEnv"], vi["venvDefault"])
    subprocess.run([py, str(ROOT / "tools" / "tts" / "gen.py"), vi["engine"], vi["lang"], vi["voice"], str(vi["speed"])],
                   input=json.dumps(js), text=True, check=True, capture_output=True)
    for j, (sp, o) in zip(js, jobs): _loudnorm(j["wav"], o, vi["loudnorm"])

def make(region, lines, only=None, voices_only=None):
    m = load(); m["region"] = region
    by_id = {l["id"]: l for l in m.get("lines", [])}
    spoken = speakable_all([l["text"] for l in lines])
    AUDIO.mkdir(parents=True, exist_ok=True)
    new, todo = [], {v: [] for v in m["voices"]}
    for l, sp in zip(lines, spoken):
        old = by_id.get(l["id"])
        if only and l["id"] not in only:
            if old: new.append(old)
            continue
        e = {"id": l["id"], "text": l["text"], "spoken": sp, "status": "DRAFT", "clips": {}}
        for v, vi in m["voices"].items():
            name = clip_name(vi, sp); f = AUDIO / name
            if voices_only and v not in voices_only and not f.exists(): continue
            if not f.exists(): todo[v].append((sp, str(f)))
            e["clips"][v] = name
        new.append(e)
    for v, jobs in todo.items():
        uniq = list(dict(jobs).items())
        synth(m["voices"][v], [(sp, o) for sp, o in uniq])
    for e in new:
        for v, c in list(e["clips"].items()):
            name = c if isinstance(c, str) else c["file"]; f = AUDIO / name
            e["clips"][v] = {"file": name, "bytes": f.stat().st_size, "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
    m["lines"] = new
    used = {c["file"] for l in new for c in l["clips"].values()}
    for f in [*AUDIO.glob("*.m4a"), *AUDIO.glob("*.mp3")]:
        if f.name not in used: f.unlink()
    MANIFEST.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    region = os.environ.get("RA_REGION", "AU")
    help_html = ROOT / "help.html"
    body = None
    if help_html.exists() and region == "AU":
        t = help_html.read_text(); a = t.index('<main id="main"><div class="wrap">\n') + len('<main id="main"><div class="wrap">\n'); b = t.index("\n</div></main>")
        body = t[a:b]
    lines = current_lines(region, body)
    if cmd == "make":
        only = None
        if "--only" in sys.argv: only = set(sys.argv[sys.argv.index("--only") + 1].split(","))
        make(region, lines, only)
    print("missing:", check(region, lines) or "none")
