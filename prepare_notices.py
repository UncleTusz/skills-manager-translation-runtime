"""Build-time offline license integrity checks; remove unused GPU loader only."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).parent
payload = ROOT / "dist/1.0.1-r2/translation-worker"
destination = payload / "licenses/upstream"
destination.mkdir(parents=True, exist_ok=True)
for entry in json.loads((ROOT / "notice-inputs.json").read_text(encoding="utf-8")):
    source = ROOT / "third-party-notices" / entry["path"]
    if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
        raise ValueError("Vendored upstream notice mismatch")
    shutil.copy2(source, destination / entry["path"])
shutil.copy2(ROOT / "notice-inputs.json", destination / "notice-inputs.json")
# CPU-only inference has no cudnn dependency. Do not distribute an unused GPU DLL.
gpu = payload / "_internal/ctranslate2/cudnn64_9.dll"
if gpu.is_file():
    gpu.unlink()
print("Verified vendored notices; CPU-only payload prepared")
