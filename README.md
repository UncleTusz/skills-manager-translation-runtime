# English-to-Chinese runtime 1.0.1 (candidate)

Independent Windows x64 offline translation component. No Skill Manager main
application code, user Skill files, credentials or Agent directories belong here.
Only the en-zh 1.9 model is included. First-use download requires consent in the
main application; installation does not require Python, pip or an API key.

## Engine and patch

- CPython 3.12.13, Argos Translate 1.11.0, unchanged en-zh 1.9 model weights.
- pySBD 0.3.4 English rules, `clean=False`, source-offset segmentation. No external
  SBD model. The adapter asserts exact character preservation and rejects gaps.
- `patch_argos.py` checks four unmodified Argos wheel source SHA256 values before
  adding explicit PYSBD selection and Unicode-safe model-byte loading. Wrong
  upstream files or repeat patching fail.
- No MiniSBD, ONNX Runtime, Stanza, SpaCy or Torch; no fallback sentence backend.
- Worker blocks Python socket connect/DNS before importing Argos. It never runs
  pip, updates a model index or falls back to a network translation API.
  This is application-level isolation, NOT proof of OS-level disconnected testing.

## Rebuild (fresh checkout and environment only)

Use Windows x64 CPython 3.12.13. Create a **fresh** venv; never reuse the historical
MiniSBD environment. Install the reviewed wheel lock (runtime AND build tools):

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip download --only-binary=:all: --require-hashes --no-deps -r requirements.lock -d wheels
.venv/Scripts/python.exe -m pip install --no-index --find-links wheels --require-hashes --no-deps -r requirements.lock
Invoke-WebRequest https://argos-net.com/v1/translate-en_zh-1_9.argosmodel -OutFile downloads/translate-en_zh-1_9.argosmodel
./build_windows.ps1 -Python .venv/Scripts/python.exe -Downloads downloads
```

Create `downloads/` before the model fetch. The model input SHA256 is
`433e7c4f034d87fbe2353161e05f18646d7999452f801a4e1f0378522b9850ab`.
`prepare_payload.py` verifies it and omits unused Stanza resources. No weight edits.
`wheel-inputs.json` records exact wheel names, hashes and original declared
dependencies. Argos's optional upstream backend dependencies are intentionally
not installed, hence `--no-deps`. The patch enforces our English-only backend.

Build refuses existing output directories; existing model payload must exactly
match reviewed input bytes. Packaging uses exclusive
ZIP creation; it never overwrites a candidate. Its final output is in
`dist/1.0.1-release-candidate/`. Old internal 1.0.0 and intermediate 1.0.1 files are not
releases and must not be uploaded. Version 1.0.1 is pinned, never a latest URL.

## Protocol

UTF-8 JSONL protocol 1, one request per line, maximum 1 MiB, request IDs required.
`hello` reports version `1.0.1`, engine `argos`, model `1.9`, splitter `pysbd`,
splitter_version `0.3.4`. `translate` accepts en->zh only, 1-64 independently
identified segments of at most 6000 UTF-8 bytes. `shutdown` exits normally.
The host serializes jobs, applies bounded waits and kills/reaps on cancellation
or failure. Errors never echo request text. Health checks initialize real models.

## Acceptance status

Candidate/prerelease only. Unit tests and existing-machine standalone/native
tests are not clean Windows certification or human translation-quality approval.
The host preserves Markdown technical literals and stores drafts separately;
Argos's output still requires human review, especially negations and requirements.
See candidate Release notes for actual evidence and remaining gates.

## Licenses

Authored glue is MIT. Argos and pySBD copyright/licenses, Python's license,
dependency inventory and third-party notices are in the ZIP `licenses/` directory.
The OPUS-MT model is CC-BY-4.0 with original README/attribution. tqdm's unmodified
source wheel accompanies its MPL/MIT notice. See `NOTICE.md`. This repository
does not change the private main application's license.
The Intel OpenMP binary additionally carries vendor terms; `BINARY-TERMS.txt`
explains their narrow scope. The app displays these before installation.

Additional native dependency licenses are vendored under `third-party-notices/`
and verified offline against `notice-inputs.json`. `fetch_notices.py` is a
maintainer-only provenance helper, never run by the app or Worker. The unused
cuDNN loader is excluded from the CPU-only distribution.
