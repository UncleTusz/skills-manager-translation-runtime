"""One-time maintainer fetch; the build only uses vendored hash-locked notices."""
import hashlib
import json
from pathlib import Path
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).parent
sources = {
    "CTranslate2-MIT.txt": "https://raw.githubusercontent.com/OpenNMT/CTranslate2/v4.8.3/LICENSE",
    "SentencePiece-Apache.txt": "https://raw.githubusercontent.com/google/sentencepiece/v0.2.2/LICENSE",
    "SentencePiece-darts.txt": "https://raw.githubusercontent.com/google/sentencepiece/v0.2.2/third_party/darts_clone/LICENSE",
    "SentencePiece-esaxx.txt": "https://raw.githubusercontent.com/google/sentencepiece/v0.2.2/third_party/esaxx/LICENSE",
    "SentencePiece-protobuf.txt": "https://raw.githubusercontent.com/google/sentencepiece/v0.2.2/third_party/protobuf-lite/LICENSE",
    "oneDNN-Apache.txt": "https://raw.githubusercontent.com/oneapi-src/oneDNN/v3.1.1/LICENSE",
    "CT2-cpu_features.txt": "https://raw.githubusercontent.com/google/cpu_features/8a494eb1e158ec2050e5f699a504fbc9b896a43b/LICENSE",
    "CT2-spdlog.txt": "https://raw.githubusercontent.com/gabime/spdlog/76fb40d95455f249bd70824ecfcae7a8f0930fa3/LICENSE",
    "CT2-ruy.txt": "https://raw.githubusercontent.com/google/ruy/363f252289fb7a1fba1703d99196524698cb884d/LICENSE",
    "CT2-cxxopts.txt": "https://raw.githubusercontent.com/jarro2783/cxxopts/44380e5a44706ab7347f400698c703eb2a196202/LICENSE",
    "CT2-cutlass.txt": "https://raw.githubusercontent.com/NVIDIA/cutlass/bbe579a9e3beb6ea6626d9227ec32d0dae119a49/LICENSE.txt",
    "CT2-cccl.txt": "https://raw.githubusercontent.com/NVIDIA/cccl/b5fe509fd11a925f90d6495176707cc1184eed9d/LICENSE",
    "CT2-BS_thread_pool.hpp": "https://raw.githubusercontent.com/OpenNMT/CTranslate2/v4.8.3/third_party/BS_thread_pool.hpp",
    "CT2-avx_mathfun.h": "https://raw.githubusercontent.com/OpenNMT/CTranslate2/v4.8.3/third_party/avx_mathfun.h",
    "CT2-avx512_mathfun.h": "https://raw.githubusercontent.com/OpenNMT/CTranslate2/v4.8.3/third_party/avx512_mathfun.h",
    "CT2-neon_mathfun.h": "https://raw.githubusercontent.com/OpenNMT/CTranslate2/v4.8.3/third_party/neon_mathfun.h",
    "OpenSSL-Apache.txt": "https://raw.githubusercontent.com/openssl/openssl/openssl-3.5.7/LICENSE.txt",
    "libffi-MIT.txt": "https://raw.githubusercontent.com/libffi/libffi/v3.4.8/LICENSE",
    "model-CC-BY-4.0.txt": "https://raw.githubusercontent.com/creativecommons/creativecommons.org/main/docroot/legalcode/by_4.0.txt",
}
directory = ROOT / "third-party-notices"
directory.mkdir(exist_ok=True)
records = []
for name, url in sources.items():
    data = urllib.request.urlopen(url, timeout=60).read()
    (directory / name).write_bytes(data)
    records.append(dict(path=name, url=url, sha256=hashlib.sha256(data).hexdigest()))
wheel = Path(sys.argv[1])
with zipfile.ZipFile(wheel) as archive:
    for name in archive.namelist():
        if "license" in name.lower() or "licence" in name.lower():
            data = archive.read(name)
            output = "Intel-" + Path(name).name
            (directory / output).write_bytes(data)
            records.append(dict(path=output, url="https://pypi.org/project/intel-openmp/2025.3.0/", wheel_sha256=hashlib.sha256(wheel.read_bytes()).hexdigest(), sha256=hashlib.sha256(data).hexdigest()))
(ROOT / "notice-inputs.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
print(f"Vendored {len(records)} version-bound notices")
