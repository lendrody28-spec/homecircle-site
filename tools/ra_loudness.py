"""Loudness check for every read-aloud clip: integrated -16 LUFS (+/-1) and true peak <= -1.5 dBTP.
python3 tools/ra_loudness.py  (exit 1 on any failure). Also writes spoken-script sidecars to tools/audio-scripts/."""
import json, re, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools")); import ra

def measure(f):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(f), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    s = r.stderr[r.stderr.rindex("Summary:"):]
    return float(re.search(r"I:\s+(-?[\d.]+) LUFS", s).group(1)), float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", s).group(1))

def sidecars(m):
    d = ROOT / "tools" / "audio-scripts"; d.mkdir(exist_ok=True)
    for old in d.glob("*.txt"): old.unlink()
    for l in m["lines"]:
        for v, c in l["clips"].items():
            vi = m["voices"][v]
            (d / (c["file"][:-4] + ".txt")).write_text(f"DRAFT\nid: {l['id']}\nvoice: {v} ({vi['engine']} {vi['voice']}, speed {vi['speed']})\nfile: assets/audio/{c['file']}\n\nOn screen:\n{l['text']}\n\nSpoken script:\n{l['spoken']}\n")

if __name__ == "__main__":
    m = ra.load(); bad = []; rows = []
    for l in m["lines"]:
        for v, c in l["clips"].items():
            I, TP = measure(ra.AUDIO / c["file"]); rows.append((l["id"], v, c["file"], I, TP))
            if not (-17.0 <= I <= -15.0) or TP > -1.5: bad.append(rows[-1])
    sidecars(m)
    Is = [r[3] for r in rows]; TPs = [r[4] for r in rows]
    print(f"loudness: {len(rows)} clips, integrated {min(Is):.1f}..{max(Is):.1f} LUFS, true peak max {max(TPs):.1f} dBTP")
    for b in bad: print("  FAIL", *b)
    sys.exit(1 if bad else 0)
