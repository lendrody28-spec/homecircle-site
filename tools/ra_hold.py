"""Re-key the read-aloud manifest after Help page lines move, without recording anything.

Lines whose text already has a clip keep it (matched by text, new id). New or changed lines get no clip and are
marked clipsHeld, so the page falls back to the device voice, the same as pages without clips.
They go on the next Voice B re-record list (`python3 tools/ra.py make --only ID,...`).
Usage: python3 tools/ra_hold.py   (then python3 tools/build.py)
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ra as RA

HOLD_NOTE = "New or changed wording (accessibility options, 10 Nov 2026). No Voice B clip yet: device voice reads it. Thursday Voice B re-record."

def main():
    t = (ROOT / "help.html").read_text()
    a = t.index('<main id="main"><div class="wrap">\n') + len('<main id="main"><div class="wrap">\n'); b = t.index("\n</div></main>")
    lines = RA.current_lines("AU", t[a:b])
    m = RA.load(); by_text = {l["text"]: l for l in m["lines"]}
    spoken = RA.speakable_all([l["text"] for l in lines])
    new, held = [], []
    for l, sp in zip(lines, spoken):
        old = by_text.get(l["text"])
        if old:
            e = dict(old); e["id"] = l["id"]; new.append(e); continue
        new.append({"id": l["id"], "text": l["text"], "spoken": sp, "status": "DRAFT", "clips": {},
                    "clipsHeld": {v: HOLD_NOTE for v in m["voices"]}})
        held.append(l["id"])
    keep = [l for l in m["lines"] if l.get("sample")]
    m["lines"] = new + [l for l in keep if l["id"] not in {n["id"] for n in new}]
    RA.MANIFEST.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
    print("held (no clip yet):", ", ".join(held) or "none")
    for h in held:
        print(" ", h, "|", next(l["text"] for l in new if l["id"] == h))

if __name__ == "__main__":
    main()
