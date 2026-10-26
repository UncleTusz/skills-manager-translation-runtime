"""MIT-licensed adapter. Segment original offsets; never clean or drop text."""
from importlib.metadata import version
import pysbd

NAME = "pysbd"
VERSION = "0.3.4"


class PySBDSentencizer:
    def __init__(self, pkg):
        if pkg.from_code != "en" or version(NAME) != VERSION:
            raise RuntimeError("Only English pySBD 0.3.4 is supported")
        self.segmenter = pysbd.Segmenter(language="en", clean=False, char_span=True)

    def split_sentences(self, text):
        spans = self.segmenter.segment(text)
        pieces, cursor = [], 0
        for span in spans:
            if not cursor <= span.start < span.end <= len(text):
                raise ValueError("Invalid pySBD source offsets")
            if text[cursor:span.start].strip():
                raise ValueError("pySBD omitted non-whitespace content")
            pieces.append(text[cursor:span.end])
            cursor = span.end
        if text[cursor:].strip():
            raise ValueError("pySBD omitted trailing content")
        if cursor < len(text):
            if pieces:
                pieces[-1] += text[cursor:]
            else:
                pieces.append(text)
        if "".join(pieces) != text:
            raise ValueError("Sentence segmentation changed input")
        return pieces

    def __str__(self):
        return "PySBDSentencizer"
