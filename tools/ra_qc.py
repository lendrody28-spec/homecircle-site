"""Whisper number check for every read-aloud clip, plus the crisis 4-second rule (Sage).
  python3 tools/ra_qc.py            -> tools/audio-qc.json and tools/audio-listen-list.md
Whisper often writes digits, so 'triple zero', 'triple 0' and '000' all count as 000."""
import json, os, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); import ra
W = {"zero": "0", "oh": "0", "o": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
     "ten": "10", "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18", "nineteen": "19",
     "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90"}

def runs(text):
    """Transcript -> list of digit runs (adjacent number words/digits joined)."""
    t = text.lower().replace("-", " ")
    t = re.sub(r"\btriple\s*(zero|0|oh)\b", " 000 ", t)
    t = re.sub(r"\btriple\s*(\d)\b", lambda m: " " + m.group(1) * 3 + " ", t)
    toks = re.findall(r"[a-z]+|\d+|[^\sa-z\d]", t)
    out, cur = [], ""
    for i, k in enumerate(toks):
        if k == "hundred" and cur: cur += "00"; continue
        d = k if k.isdigit() else W.get(k)
        if d is not None:
            if cur and len(d) == 2 and d.endswith("0") and False: pass
            cur += d; continue
        if k in (",", ".") and cur and i + 1 < len(toks) and (toks[i + 1].isdigit() or toks[i + 1] in W): continue
        if cur: out.append(cur); cur = ""
    if cur: out.append(cur)
    return out

def expected(text):
    t = re.sub(r"1800RESPECT", "1800", text)
    return [re.sub(r"\D", "", n) for n in re.findall(r"\d[\d ]*\d|\d", t)]

def main():
    m = ra.load(); jobs = []
    for l in m["lines"]:
        for v, c in l["clips"].items(): jobs.append({"file": str(ra.AUDIO / c["file"]), "id": l["id"], "voice": v, "text": l["text"]})
    py = os.environ.get("WHISPER_PY", "/workspace/tts-venvs/whisper/bin/python")
    r = subprocess.run([py, str(ROOT / "tools" / "tts" / "whisper_check.py")], input=json.dumps([{"file": j["file"]} for j in jobs]), capture_output=True, text=True, check=True)
    res = {x["file"]: x for x in json.loads(r.stdout)}
    report, fails, crisis = [], [], []
    for j in jobs:
        w = res[j["file"]]; got = runs(w["text"]); exp = expected(j["text"])
        missing = [e for e in exp if not any(e in g for g in got)]
        row = {"id": j["id"], "voice": j["voice"], "file": Path(j["file"]).name, "heard": w["text"], "expectedNumbers": exp, "missingNumbers": missing}
        if j["id"].startswith("kai.crisis."):
            t0 = None; ws = w["words"]
            for i, (wd, s, e) in enumerate(ws):
                a = wd.strip().lower().strip(".,")
                nxt = ws[i + 1][0].strip().lower().strip(".,") if i + 1 < len(ws) else ""
                if re.search(r"000|triple.?(zero|0)", a) or (a == "triple" and nxt in ("zero", "0", "oh")):
                    t0 = s; break
            row["tripleZeroAt"] = t0; row["tripleZeroWithin4s"] = t0 is not None and t0 <= 4.0
            crisis.append(row)
        if missing or row.get("tripleZeroWithin4s") is False: fails.append(row)
        report.append(row)
    (ROOT / "tools" / "audio-qc.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n")
    print(f"clips checked: {len(report)}; number misses: {sum(1 for r in report if r['missingNumbers'])}")
    for c in crisis: print(f"  crisis {c['id']} [{c['voice']}]: triple zero at {c['tripleZeroAt']}s -> {'OK' if c['tripleZeroWithin4s'] else 'FAIL'}")
    for f in fails: print("  FLAG", f["id"], f["voice"], f["file"], "missing", f["missingNumbers"], "| heard:", f["heard"][:160])
    return report


def retake(rows, tries=4):
    """Re-record flagged clips (same settings, same name; the engine's own randomness gives a new take), keep the best."""
    import hashlib
    m = ra.load()
    for t in range(tries):
        bad = [r for r in rows if r["missingNumbers"] or r.get("tripleZeroWithin4s") is False or re.search(r"\b(core|court|cool)\b", r["heard"], re.I)]
        if not bad: break
        print(f"retake round {t + 1}: {len(bad)} clips")
        for r in bad:
            l = next(x for x in m["lines"] if x["id"] == r["id"]); vi = m["voices"][r["voice"]]
            ra.synth(vi, [(l["spoken"], str(ra.AUDIO / r["file"]))])
        rows = main()
    m = ra.load()
    for l in m["lines"]:
        for v, c in l["clips"].items():
            f = ra.AUDIO / c["file"]; c["bytes"] = f.stat().st_size; c["sha256"] = hashlib.sha256(f.read_bytes()).hexdigest()
    ra.MANIFEST.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
    return rows

if __name__ == "__main__":
    rows = main()
    if "--retake" in sys.argv: retake(rows)
