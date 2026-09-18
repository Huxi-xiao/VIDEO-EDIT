#!/usr/bin/env python3
import importlib.util, json, shutil, sys

checks = {
    "python_3_10_plus": sys.version_info >= (3,10),
    "ffmpeg": shutil.which("ffmpeg") is not None,
    "ffprobe": shutil.which("ffprobe") is not None,
    "node": shutil.which("node") is not None,
    "npm": shutil.which("npm") is not None,
    "npx": shutil.which("npx") is not None,
    "whisper_cli": shutil.which("whisper") is not None,
    "faster_whisper_python": importlib.util.find_spec("faster_whisper") is not None,
}
print(json.dumps(checks, ensure_ascii=False, indent=2))
print("\nBasic render requires Python + ffmpeg + ffprobe.")
print("Local transcription: faster-whisper or Whisper CLI.")
print("Styled Motion rendering: Node/npm/npx + renderer npm install.")
if not checks["python_3_10_plus"]:
    raise SystemExit(2)
