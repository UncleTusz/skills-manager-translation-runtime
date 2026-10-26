"""Internal real-engine smoke test, not a released component acceptance test."""
import json
import os
from pathlib import Path
import subprocess
import time


root = Path(__file__).parent
exe = Path(os.environ.get("RUNTIME_WORKER_EXE", root / "dist" / "1.0.1-r2" / "translation-worker" / "translation-worker.exe"))
env = {key: value for key, value in os.environ.items()
       if key.upper() in {"SYSTEMROOT", "WINDIR", "TEMP", "TMP", "COMSPEC",
                          "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "LOCALAPPDATA", "APPDATA"}}
env["PATH"] = str(Path(os.environ["SYSTEMROOT"]) / "System32")
started = time.perf_counter()
worker = subprocess.Popen([str(exe)], cwd=exe.parent, env=env, stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def request(message):
    worker.stdin.write(json.dumps(message).encode("utf-8") + b"\n")
    worker.stdin.flush()
    frame = worker.stdout.readline()
    if not frame:
        raise RuntimeError(worker.stderr.read().decode("utf-8", errors="replace"))
    result = json.loads(frame.decode("utf-8"))
    assert result["request_id"] == message["request_id"] and result["ok"], result
    return result


try:
    hello = request(dict(request_id="hello", type="hello"))
    cold_ms = round((time.perf_counter() - started) * 1000)
    assert hello["ready"] and hello["engine"] == "argos" and hello["model_version"] == "1.9"
    assert (hello["version"], hello["splitter"], hello["splitter_version"]) == ("1.0.1", "pysbd", "0.3.4")
    translation_started = time.perf_counter()
    result = request(dict(request_id="translate", type="translate", source_lang="en", target_lang="zh",
                          segments=[dict(id="first", text="Read the source document and save the translation separately."),
                                    dict(id="second", text="Do not change the original file.")]))
    assert [item["id"] for item in result["results"]] == ["first", "second"]
    assert all(any("\u4e00" <= char <= "\u9fff" for char in item["text"])
               for item in result["results"])
    translation_ms = round((time.perf_counter() - translation_started) * 1000)
    request(dict(request_id="shutdown", type="shutdown"))
    worker.wait(timeout=10)
    assert worker.returncode == 0
    evidence = dict(engine="argos", model_version=hello["model_version"], cold_ms=cold_ms,
                    translation_ms=translation_ms, results=result["results"], process_exited=True,
                    python_on_worker_path=False, release_acceptance=False,
                    splitter="pysbd-0.3.4", caveat="Candidate; clean Windows/OS-level network isolation and human quality acceptance pending")
    (root / "native-worker-1.0.1-test.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(evidence, ensure_ascii=False))
finally:
    if worker.poll() is None:
        worker.kill()
        worker.wait()
