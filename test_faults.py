"""Real frozen-process failures. Does not touch installed application data."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parent
BUNDLE = ROOT / "dist/1.0.1-r2/translation-worker"


class FaultTests(unittest.TestCase):
    def test_repeat_upstream_patch_fails_without_writing(self):
        import argostranslate
        root = Path(argostranslate.__file__).parent
        before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob("*.py")}
        process = subprocess.run([sys.executable, str(ROOT / "patch_argos.py")], capture_output=True, timeout=20)
        self.assertNotEqual(process.returncode, 0)
        self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob("*.py")})

    def test_initialization_failures_and_crash_reap(self):
        env = dict(os.environ, PATH=str(Path(os.environ["SYSTEMROOT"]) / "System32"))
        with tempfile.TemporaryDirectory(prefix="pysbd-fault-") as temporary:
            bundle = Path(temporary) / "component"
            shutil.copytree(BUNDLE, bundle)
            exe = bundle / "translation-worker.exe"
            metadata = bundle / "models/translate-en_zh-1_9/metadata.json"
            original = metadata.read_bytes()
            data = json.loads(original)
            data["from_code"] = "fr"
            metadata.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run([str(exe)], input=b'{"type":"hello","request_id":"h"}\n', capture_output=True, env=env, timeout=60)
            self.assertEqual(result.returncode, 12)
            self.assertIn(b"WORKER_INIT_FAILED", result.stderr)
            metadata.write_bytes(original)
            dll = bundle / "_internal/python312.dll"
            held = bundle / "held-python312.dll"
            dll.rename(held)
            try:
                result = subprocess.run([str(exe)], input=b"", capture_output=True, env=env, timeout=60)
                self.assertNotEqual(result.returncode, 0)
            finally:
                held.rename(dll)
            process = subprocess.Popen([str(exe)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
            try:
                process.stdin.write(b'{"type":"hello","request_id":"h"}\n')
                process.stdin.flush()
                self.assertTrue(json.loads(process.stdout.readline())["ready"])
                process.kill()
                process.wait(timeout=10)
                self.assertIsNotNone(process.returncode)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait(timeout=10)
                process.stdin.close()
                process.stdout.close()
                process.stderr.close()


if __name__ == "__main__":
    unittest.main()
