"""Generate platform-specific hash lock from the reviewed downloaded wheel set."""
import email
import hashlib
import json
from pathlib import Path
import sys
import zipfile

root = Path(__file__).parent
entries = []
for wheel in sorted(Path(sys.argv[1]).glob("*.whl")):
    with zipfile.ZipFile(wheel) as archive:
        info = email.message_from_bytes(archive.read(next(n for n in archive.namelist() if n.endswith(".dist-info/METADATA"))))
    entries.append(dict(name=info["Name"], version=info["Version"], file=wheel.name,
                        sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(),
                        requires_dist=info.get_all("Requires-Dist", [])))
assert not any(e["name"].lower() in {"minisbd", "onnxruntime", "torch", "stanza", "spacy"} for e in entries)
lock = "# Windows x64 / CPython 3.12; install --require-hashes --no-deps.\n"
lock += "\n".join(f'{e["name"]}=={e["version"]} --hash=sha256:{e["sha256"]}' for e in entries) + "\n"
(root / "requirements.lock").write_text(lock, encoding="utf-8")
(root / "wheel-inputs.json").write_text(json.dumps(entries, indent=2), encoding="utf-8")
print(f"Locked {len(entries)} wheels including Argos and build dependencies")
