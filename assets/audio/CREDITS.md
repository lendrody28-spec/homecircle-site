# Read-aloud audio: licences and credits

These clips were made offline, on our own machine, from HomeCircle's own text. No cloud or paid text-to-speech service was used, and no clip copies a real or well-known person's voice. The exact model versions and settings for each voice are in `tools/audio-manifest.json` (`voices`), so a re-recorded clip will match the others.

## Voice A: MeloTTS English v2, speaker EN-AU (Australian, female)
- Software: MeloTTS 0.1.2, https://github.com/myshell-ai/MeloTTS, commit 209145371cff8fc3bd60d7be902ea69cbdb7965a
- Weights: https://huggingface.co/myshell-ai/MeloTTS-English-v2, revision a53e3509c4ee4ff16d79272feb2474ff864e18f3
- Settings: language EN_V2, speaker EN-AU, speed 0.9
- Licence: MIT, Copyright (c) 2024 MyShell.ai. Full text: `licences/MeloTTS-MIT-LICENSE.txt` (from https://github.com/myshell-ai/MeloTTS/blob/main/LICENSE). Model card: "This library is under MIT License, which means it is free for both commercial and non-commercial use."

## Voice B: Kokoro-82M v1.0, voice am_michael (American, male)
- Software: kokoro 0.9.4 and misaki 0.9.4 (https://github.com/hexgrad/kokoro)
- Weights: https://huggingface.co/hexgrad/Kokoro-82M, revision f3ff3571791e39611d31c381e3a41a3af07b4987 (kokoro-v1_0.pth, voices/am_michael.pt)
- Settings: lang_code "a" (American English), voice am_michael, speed 0.9
- Licence: Apache License 2.0. Full text: `licences/Kokoro-Apache-2.0-LICENSE.txt` (from https://www.apache.org/licenses/LICENSE-2.0.txt). Model card: "This is an Apache-licensed model".
- Kokoro v1.0 was trained partly on these CC BY datasets, credited here with thanks:
  - Koniwa (`tnc`), https://github.com/koniwa/koniwa, licensed CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/)
  - SIWIS French Speech Synthesis Database, https://datashare.ed.ac.uk/handle/10283/2353, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

## Loudness
All clips: two-pass ffmpeg loudnorm to -16 LUFS integrated, -1.5 dBTP true peak, LRA 11, then AAC 48 kbps mono in .m4a.

Thanks to MyShell.ai (MeloTTS) and hexgrad (Kokoro).
