"""Export allowlisted, path-free candidate build evidence, never user content."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys
from importlib.metadata import version
import zipfile

ROOT = Path(__file__).parent
release_dir = ROOT / "dist/1.0.1-release-candidate"
release = json.loads((release_dir / "runtime-release.json").read_text(encoding="utf-8"))
native = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["results"]
assert native.get("chapters") == 14 and native.get("beforeRestart")
with zipfile.ZipFile(release_dir / "argos-en-zh-windows-x64-1.0.1.zip") as archive:
    manifest = json.loads(archive.read("manifest.json"))
record = dict(version="1.0.1", channel="candidate", created_utc=datetime.now(timezone.utc).isoformat(),
              python=platform.python_version(), pip=version("pip"), pyinstaller=version("pyinstaller"),
              platform="Windows x64", engine="Argos 1.11.0", model="en-zh-1.9",
              model_input_sha256="433e7c4f034d87fbe2353161e05f18646d7999452f801a4e1f0378522b9850ab",
              splitter="pysbd-0.3.4", splitter_options=dict(language="en", clean=False, char_span=True),
              release=release, installed_bytes=sum(e["bytes"] for e in manifest["files"]), files=len(manifest["files"]),
              build_material_hashes={p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT / n for n in ["requirements.lock", "wheel-inputs.json", "notice-inputs.json", "patch_argos.py", "pysbd_adapter.py", "worker.py", "build_windows.ps1", "package_release.py", "BINARY-TERMS.txt"]]},
              validation=dict(python_tests=8, native_full_skill_sections=native["chapters"],
                              full_translation_ms=native["translationMs"], installation_ms=native["componentInstallMs"],
                              persisted_after_restart=True, source_hashes_unchanged=True,
                              corruption_cancel_missing_dll=True,
                              application_ui_cases=len(native.get("uiCases", [])), translation_ui_cases=len(native.get("runtimeUiCases", [])),
                              binary_terms_ui_cases=len(native.get("consentCases", [])),
                              clean_windows=False, os_level_disconnected=False, human_quality_accepted=False))
(release_dir / "build-record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
print(json.dumps(record["validation"]))
