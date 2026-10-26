from types import SimpleNamespace
import unittest
from pysbd_adapter import PySBDSentencizer


class SplitterTests(unittest.TestCase):
    def test_english_boundaries(self):
        splitter = PySBDSentencizer(SimpleNamespace(from_code="en"))
        for text, count in [
            ("Dr. Smith works in the U.S. He is ready.", 2),
            ("My name is Jonas E. Smith. Read p. 55.", 2),
            ("Use version 1.9. Price is 3.14 dollars.", 2),
            ('He said, "Do not delete." Keep it (including notes).', 2),
            ("First line.\r\nSecond line.\n", 2),
        ]:
            with self.subTest(text=text):
                pieces = splitter.split_sentences(text)
                self.assertEqual("".join(pieces), text)
                self.assertEqual(len(pieces), count)

    def test_no_loss_or_cleaning(self):
        splitter = PySBDSentencizer(SimpleNamespace(from_code="en"))
        for text in ["\n  1. Read the source.\n  2. Save separately.\n", "\t\n", "",
                     "This is English. 中文内容保持。 Next sentence.",
                     "word " * 5000 + "Do not change the file.",
                     "Do  not   clean.\n\nKeep <tag> & spaces.\t"]:
            self.assertEqual("".join(splitter.split_sentences(text)), text)

    def test_wrong_language_refused(self):
        with self.assertRaises(RuntimeError):
            PySBDSentencizer(SimpleNamespace(from_code="zh"))


if __name__ == "__main__":
    unittest.main()
