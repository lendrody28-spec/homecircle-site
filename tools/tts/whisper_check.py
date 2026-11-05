"""Run INSIDE the whisper venv: /workspace/tts-venvs/whisper/bin/python tools/tts/whisper_check.py < jobs.json > out.json
jobs: [{"file": path}] -> [{"file", "text", "words": [[word, start, end], ...]}]  (faster-whisper base, int8, CPU)"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("base", device="cpu", compute_type="int8")
out = []
for j in json.load(sys.stdin):
    pcm = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", j["file"], "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    segs, _ = m.transcribe(np.frombuffer(pcm, np.float32), language="en", beam_size=5, word_timestamps=True, temperature=0.0, condition_on_previous_text=False)
    words = [[w.word, round(w.start, 2), round(w.end, 2)] for s in segs for w in s.words]
    out.append({"file": j["file"], "text": "".join(w[0] for w in words).strip(), "words": words})
json.dump(out, sys.stdout)
