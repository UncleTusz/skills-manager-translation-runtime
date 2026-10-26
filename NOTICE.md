# Runtime Attribution

CANDIDATE 1.0.1: clean Windows / OS-disconnected and human quality acceptance
are separate gates. The old MiniSBD-based internal 1.0.0 ZIP is not distributed.
This notice does not relicense the private main application.

This repository contains runtime build materials only. It does not contain
Skill Manager application source, API keys or user Skill documents.

- Argos Translate 1.11.0: MIT, https://github.com/argosopentech/argos-translate
- CTranslate2: MIT, https://github.com/OpenNMT/CTranslate2
- SentencePiece: Apache-2.0, https://github.com/google/sentencepiece
- pySBD 0.3.4: MIT, copyright Nipun Sadvilkar,
  https://github.com/nipunsadvilkar/pySBD ; English rules, clean=False.
- CPython 3.12.13: PSF License; NumPy includes BSD/MIT and third-party notices.
- Sacremoses 0.1.1: MIT, copyright alvations (included wheel LICENSE).
- tqdm: MPL-2.0 AND MIT; its complete unmodified source wheel accompanies the
  notices for convenient source access. No tqdm modifications.
- Other runtime and build dependency copyright/license texts are included.
- Intel OpenMP DLL: Intel EULA (August 2024), not MIT. See BINARY-TERMS.txt and
  licenses/upstream/Intel-LICENSE.txt. The supplied DLL matches the licensed
  intel-openmp 2025.3.0 wheel byte-for-byte. These vendor terms are not imposed
  on the authored MIT source or the private main application.
- Argos English-Chinese model 1.9 derives from OPUS-MT, CC-BY-4.0.
  Authors: Joerg Tiedemann and Santhosh Thottingal.
  OPUS-MT: Building open translation services for the World. EAMT 2020, Lisbon.
  https://creativecommons.org/licenses/by/4.0/
  Original distribution: https://argos-net.com/v1/translate-en_zh-1_9.argosmodel
  Model weights unchanged; unused Stanza sentence resources omitted. Original
  model README is retained. No sentence-segmentation model is needed.

`patch_argos.py` verifies exact upstream SHA256 values before adding the explicit
pySBD backend, removing MiniSBD import/class and disabling implicit fallback.
The exact patch and adapter are shipped. Torch, Stanza, SpaCy, MiniSBD and
ONNX Runtime are not packaged. English pySBD rule data is bundled, not fetched.
The unused cuDNN loader is omitted; CPU inference only. Additional upstream
CTranslate2/SentencePiece/native dependency notices are version/hash-bound in
notice-inputs.json and included in licenses/upstream. The SentencePiece model is
loaded from unchanged bytes to support Unicode Windows installation paths.
The worker enforces en-zh and disables network connections, including during
initialization. There is no model index, pip install or API fallback at runtime.

Third-party package notices are copied into the ZIP's licenses directory.
PyInstaller's bootloader exception permits distribution of the frozen worker.
See https://pyinstaller.org/en/stable/license.html and the included licenses.

Recorded model digests are publisher-reviewed build input digests, not claimed
to be official upstream signatures. Skill Manager pins the release ZIP and
file-manifest digests. Review and build a new version to change them.
