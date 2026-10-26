"""Hash-bound Argos 1.11.0 patch: explicit English pySBD, no backend fallback."""
import hashlib
import importlib.util
from pathlib import Path

HASHES = {
    "sbd.py": "df579427d9c8cc8890a80a67291e7876948f959dd0509dfb74b85173406de9d2",
    "settings.py": "58e83f5a20738f960e00a39e8881aada795cbbe399d613a931f7f6f175d96ff8",
    "translate.py": "2ec5aa4b83cf0bc697e0ece47e10eaf79dcb8db734299d830d75a18cf802c8db",
    "tokenizer.py": "e56ac286bd7a9a5524236e67728a9b417e06799585cb492e019b1dbda0e479ff",
}


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Argos patch context mismatch")
    return text.replace(old, new)


def patch():
    root = Path(importlib.util.find_spec("argostranslate").submodule_search_locations[0])
    sources = {}
    for name, expected in HASHES.items():
        data = (root / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Unmodified Argos 1.11.0 required: {name}")
        sources[name] = data.decode("utf-8")
    sbd = once(sources["sbd.py"], "import stanza\n", "stanza = None  # Excluded from this English-only runtime.\n")
    sbd = once(sbd, "from minisbd import SBDetect, models as minisbd_models\n", "from argostranslate.pysbd_adapter import PySBDSentencizer\n")
    sbd = once(sbd, 'minisbd_models.cache_dir = str(settings.data_dir / "minisbd")\n', "")
    begin, end = sbd.index("class MiniSBDSentencizer("), sbd.index("class StanzaSentencizer(")
    sbd = sbd[:begin] + sbd[end:]
    settings = once(sources["settings.py"], "    MINISBD = 5 # Use only MiniSBD\n", "    PYSBD = 6  # English rule-based splitter; no resource download.\n")
    settings = once(settings, '    "MINISBD": ChunkType.MINISBD,\n', '    "PYSBD": ChunkType.PYSBD,\n')
    translate = once(sources["translate.py"], "from argostranslate.sbd import SpacySentencizerSmall, StanzaSentencizer, MiniSBDSentencizer", "from argostranslate.sbd import PySBDSentencizer")
    begin = translate.index("        Sentencizer = None\n")
    end = translate.index("    def hypotheses(", begin)
    translate = translate[:begin] + '''        if settings.chunk_type != settings.ChunkType.PYSBD:
            raise RuntimeError("This runtime requires explicit PYSBD; no fallback")
        self.sentencizer = PySBDSentencizer(pkg)

''' + translate[end:]
    tokenizer = once(sources["tokenizer.py"], "spm.SentencePieceProcessor(model_file=str(self.model_file))", "spm.SentencePieceProcessor(model_proto=self.model_file.read_bytes())")
    for name, text in {"sbd.py": sbd, "settings.py": settings, "translate.py": translate, "tokenizer.py": tokenizer}.items():
        (root / name).write_bytes(text.encode("utf-8"))
    (root / "pysbd_adapter.py").write_bytes(Path(__file__).with_name("pysbd_adapter.py").read_bytes())
    print("Verified upstream hashes; applied explicit pySBD backend patch")


if __name__ == "__main__":
    patch()
