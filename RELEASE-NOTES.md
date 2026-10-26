# 1.0.1 Candidate: English-to-Chinese offline runtime

Windows x64 component only; not a main-application installer. First-use download
is approximately 109.16 MiB, installed payload approximately 199.99 MiB. Only the
unchanged en-zh 1.9 model is included.

## Changes

- Argos 1.11.0 with pySBD 0.3.4 English rules, clean=False and exact source spans.
- Hash-bound patches fail closed; no MiniSBD, ONNX Runtime, Stanza, SpaCy or Torch.
- Unicode-safe SentencePiece loading without modifying model weights.
- Standalone CPython Worker; no external Python, pip or API key required by design.
- MIT-authored adapter/build material, complete model/dependency notices and
  narrowly scoped Intel OpenMP binary terms. See BINARY-TERMS.txt and licenses.

## Evidence And Limits

Eight Python tests and existing-machine frozen Worker tests passed. An isolated
Debug host translated a full 14-section Skill, preserved technical Markdown and
source hashes, and retained drafts after restart. Integrity, cancellation, missing
DLL, source-change and stale-revision checks passed. See build-record.json for
which package and tests were actually recorded; main-host UI tests are not
independent clean-environment certification.

This is a prerelease, NOT production acceptance. A clean Windows environment
without external Python and OS-level disconnected execution are still unverified.
The Worker disables Python network connections, but that does not prove OS-level
offline behavior of every native dependency.

Human translation quality is NOT accepted: terminology can be incorrect. In a
sample, "under 100" became an age reference; React, repo and GitHub stars were
misinterpreted. Review every generated draft, especially negations, conditions
and operational requirements. There is no automatic paid-API fallback.

No private main application source, user Skill content, credentials, Agent data,
old MiniSBD package or earlier intermediate ZIP is part of this release.
