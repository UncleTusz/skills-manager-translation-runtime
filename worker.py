"""Offline Argos en-zh worker. No user Python, network or API credentials."""
import json
import os
from pathlib import Path
import socket
import sys

VERSION = "1.0.1"
PROTOCOL = 1
LIMIT = 1024 * 1024


def deny_network(*_args, **_kwargs):
    raise RuntimeError("Offline runtime: networking is disabled")


def backend(root):
    packages = root / "models"
    package_dirs = list(packages.glob("*/metadata.json"))
    if len(package_dirs) != 1:
        raise RuntimeError("Exactly one bundled en-zh model is required")
    model = package_dirs[0].parent
    metadata = json.loads(package_dirs[0].read_text(encoding="utf-8"))
    if (metadata.get("from_code"), metadata.get("to_code")) != ("en", "zh"):
        raise RuntimeError("Unsupported bundled model")
    if str(metadata.get("package_version")) != "1.9":
        raise RuntimeError("Unexpected bundled model version")
    os.environ.update(ARGOS_PACKAGES_DIR=str(packages), ARGOS_DEVICE_TYPE="cpu",
                      ARGOS_CHUNK_TYPE="PYSBD", ARGOS_MODEL_PROVIDER="OPENNMT",
                      ARGOS_DATA_DIR=str(root / "data"), ARGOS_DEBUG="0",
                      HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    for name in ["XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME"]:
        os.environ.setdefault(name, str(root.parent / "worker-state" / name.lower()))
    socket.create_connection = deny_network
    socket.socket.connect = deny_network
    socket.socket.connect_ex = deny_network
    socket.getaddrinfo = deny_network
    from argostranslate import translate
    from importlib.metadata import version
    if version("pysbd") != "0.3.4":
        raise RuntimeError("Wrong pySBD version")
    translation = translate.get_translation_from_codes("en", "zh")
    # Load all lazy DLL/model resources before reporting healthy.
    if not translation.translate("Hello world.").strip():
        raise RuntimeError("Translation health check returned empty output")
    return translation.translate, str(metadata["package_version"])


def process(req, translate, model_version):
    rid = req.get("request_id")
    if not isinstance(rid, str) or not 1 <= len(rid) <= 128:
        raise ValueError("Invalid request_id")
    typ = req.get("type")
    if typ == "hello":
        return dict(request_id=rid, ok=True, protocol=PROTOCOL, version=VERSION,
                    model_version=model_version, engine="argos", ready=True,
                    splitter="pysbd", splitter_version="0.3.4")
    if typ == "shutdown":
        return dict(request_id=rid, ok=True, shutdown=True)
    if typ != "translate" or req.get("source_lang") != "en" or req.get("target_lang") != "zh":
        raise ValueError("Only en-zh translation is supported")
    segments = req.get("segments")
    if not isinstance(segments, list) or not 1 <= len(segments) <= 64:
        raise ValueError("Expected 1-64 segments")
    seen = set()
    for item in segments:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("text"), str):
            raise ValueError("Invalid segment")
        if not item["id"] or item["id"] in seen or len(item["text"].encode("utf-8")) > 6000:
            raise ValueError("Invalid, duplicate or oversized segment; input was not truncated")
        seen.add(item["id"])
    results = []
    for item in segments:
        output = translate(item["text"])
        if not isinstance(output, str) or not output.strip():
            raise ValueError("Empty translation")
        results.append(dict(id=item["id"], text=output))
    return dict(request_id=rid, ok=True, results=results)


def serve(reader, writer, translate, model_version):
    while True:
        line = reader.readline(LIMIT + 1)
        if not line:
            return
        if len(line) > LIMIT or not line.endswith(b"\n"):
            raise ValueError("Invalid JSONL frame")
        rid = None
        try:
            req = json.loads(line.decode("utf-8"))
            if not isinstance(req, dict):
                raise ValueError("Expected JSON object")
            rid = req.get("request_id")
            response = process(req, translate, model_version)
        except Exception:
            # Never log Skill text, model output or request bodies.
            response = dict(request_id=rid, ok=False, error="WORKER_REQUEST_FAILED")
        writer.write(json.dumps(response, ensure_ascii=False).encode("utf-8") + b"\n")
        writer.flush()
        if response.get("shutdown"):
            return


if __name__ == "__main__":
    root = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).parent / "payload-1.0.1"
    try:
        translate, model_version = backend(root)
        serve(sys.stdin.buffer, sys.stdout.buffer, translate, model_version)
    except Exception as exc:
        print(f"WORKER_INIT_FAILED: {type(exc).__name__}", file=sys.stderr, flush=True)
        sys.exit(12)
