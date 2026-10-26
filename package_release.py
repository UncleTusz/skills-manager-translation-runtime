"""Collect licenses and produce an immutable release ZIP plus app trust anchor."""
import hashlib
from importlib import metadata
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).parent
payload = ROOT / "dist" / "1.0.1-r2" / "translation-worker"
licenses = payload / "licenses"
licenses.mkdir(exist_ok=True)
inputs = json.loads((ROOT / "wheel-inputs.json").read_text(encoding="utf-8"))
inventory = []
for distribution in metadata.distributions():
    name = distribution.metadata["Name"]
    inventory.append(dict(name=name, version=distribution.version,
                          license=distribution.metadata.get("License-Expression") or distribution.metadata.get("License")))
    for file in distribution.files or []:
        if any(token in file.name.lower() for token in ["license", "licence", "copying", "notice"]):
            source = distribution.locate_file(file)
            if source.is_file():
                target = licenses / name / str(file).replace("..", "_").replace(":", "_")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
(licenses / "dependency-inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
python_license = Path(sys.base_prefix) / "LICENSE.txt"
if not python_license.is_file():
    raise ValueError("CPython license missing")
shutil.copy2(python_license, licenses / "CPython-LICENSE.txt")
# Include actual unmodified MPL-covered source, not just a remote source URL.
tqdm = next(e for e in inputs if e["name"].lower() == "tqdm")
wheel_dir = ROOT / "wheels"
if not wheel_dir.is_dir():
    wheel_dir = Path(sys.prefix).parent / "wheels"
wheel = wheel_dir / tqdm["file"]
if hashlib.sha256(wheel.read_bytes()).hexdigest() != tqdm["sha256"]:
    raise ValueError("tqdm source wheel digest mismatch")
shutil.copy2(wheel, licenses / wheel.name)
for name in ["NOTICE.md", "LICENSE", "BINARY-TERMS.txt", "requirements.lock", "wheel-inputs.json", "patch_argos.py", "pysbd_adapter.py"]:
    path = ROOT / name
    if path.is_file():
        shutil.copy2(path, licenses / name)
entries = []
for file in sorted(payload.rglob("*")):
    if not file.is_file() or file.name == "manifest.json":
        continue
    entries.append(dict(path=file.relative_to(payload).as_posix(), bytes=file.stat().st_size,
                        sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
for entry in entries:
    if any(token in entry["path"].lower() for token in ["minisbd", "onnxruntime", "en.onnx", "torch", "spacy", "stanza"]):
        raise ValueError(f"Excluded dependency in package: {entry['path']}")
manifest = json.dumps(dict(version="1.0.1", files=entries), ensure_ascii=True, separators=(",", ":")).encode()
(payload / "manifest.json").write_bytes(manifest)
name = "argos-en-zh-windows-x64-1.0.1.zip"
release_dir = ROOT / "dist" / "1.0.1-release-candidate"
release_dir.mkdir(exist_ok=True)
output = release_dir / name
with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for file in sorted(payload.rglob("*")):
        if file.is_file():
            archive.write(file, file.relative_to(payload).as_posix())
release = dict(version="1.0.1", url=f"https://github.com/UncleTusz/skills-manager-translation-runtime/releases/download/v1.0.1/{name}", bytes=output.stat().st_size,
               sha256=hashlib.sha256(output.read_bytes()).hexdigest(), manifest_sha256=hashlib.sha256(manifest).hexdigest())
(release_dir / "runtime-release.json").write_text(json.dumps(release, indent=2), encoding="utf-8")
print(json.dumps(dict(**release, installed_bytes=sum(e["bytes"] for e in entries), files=len(entries))))
