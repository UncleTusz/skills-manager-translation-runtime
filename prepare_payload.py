"""Prepare reviewed, fixed model inputs. No runtime package-index updates."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).parent
MODEL_SHA = "433e7c4f034d87fbe2353161e05f18646d7999452f801a4e1f0378522b9850ab"


def prepare(downloads):
    source = downloads / "translate-en_zh-1_9.argosmodel"
    if hashlib.sha256(source.read_bytes()).hexdigest() != MODEL_SHA:
        raise ValueError("Reviewed model digest mismatch")
    target = ROOT / "payload-1.0.1" / "models" / "translate-en_zh-1_9"
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as archive:
        for info in archive.infolist():
            relative = Path(info.filename).relative_to("translate-en_zh-1_9")
            if ".." in relative.parts or relative.is_absolute():
                raise ValueError("Unsafe model path")
            # pySBD is rule-based and needs no segmentation model.
            if not relative.parts or relative.parts[0] in {"stanza", "minisbd"}:
                continue
            dest = target / relative
            if info.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                data = archive.read(info)
                if dest.exists() and dest.read_bytes() != data:
                    raise ValueError("Existing model payload differs; refusing overwrite")
                if not dest.exists():
                    dest.write_bytes(data)
    print(json.dumps({"model_sha256": MODEL_SHA, "model_bytes": source.stat().st_size,
                      "splitter": "pysbd", "splitter_version": "0.3.4"}))


if __name__ == "__main__":
    prepare(Path(sys.argv[1]))
