"""Run INSIDE the engine's venv. Reads JSON jobs [{"spoken":..., "wav":...}] on stdin.
  melo:   /workspace/tts-venvs/melo/bin/python tools/tts/gen.py melo EN_V2 EN-AU 0.9
  kokoro: /workspace/tts-venvs/kokoro/bin/python tools/tts/gen.py kokoro a am_michael 0.9
Settings must match tools/audio-manifest.json "voices" so re-recorded clips match the set."""
import json, os, sys
engine, lang, voice, speed = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
jobs = json.load(sys.stdin)
import numpy as np, soundfile as sf
if engine == "melo":
    os.environ.setdefault("NLTK_DATA", "/workspace/tts-work/nltk_data")
    import nltk; nltk.data.path.insert(0, os.environ["NLTK_DATA"])
    from melo.api import TTS
    m = TTS(language=lang, device="cpu"); sid = m.hps.data.spk2id[voice]
    for j in jobs: m.tts_to_file(j["spoken"], sid, j["wav"], speed=speed, quiet=True)
elif engine == "kokoro":
    os.environ.setdefault("ESPEAK_DATA_PATH", "/workspace/tts-work/espeak-prefix/usr/lib/x86_64-linux-gnu/espeak-ng-data")
    from kokoro import KPipeline
    p = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    for j in jobs:
        a = [x[2] for x in p(j["spoken"], voice=voice, speed=speed)]
        sf.write(j["wav"], np.concatenate(a), 24000)
else:
    sys.exit("unknown engine " + engine)
print("ok", len(jobs))
