import io
import json
import unittest
from worker import process, serve


class ProtocolTests(unittest.TestCase):
    def test_frames_and_shutdown(self):
        requests = [dict(request_id="one", type="hello"), dict(request_id="two", type="translate", source_lang="en", target_lang="zh", segments=[dict(id="s1", text="Hello")]), dict(request_id="stop", type="shutdown")]
        reader = io.BytesIO(b"".join(json.dumps(r).encode() + b"\n" for r in requests))
        writer = io.BytesIO()
        serve(reader, writer, lambda _: "中文", "test-only")
        rows = [json.loads(line) for line in writer.getvalue().splitlines()]
        self.assertEqual([r["request_id"] for r in rows], ["one", "two", "stop"])
        self.assertEqual((rows[0]["splitter"], rows[0]["splitter_version"]), ("pysbd", "0.3.4"))
        self.assertEqual(rows[1]["results"][0]["id"], "s1")

    def test_invalid_contract(self):
        for segments in [[], [dict(id="x", text="a"), dict(id="x", text="b")], [dict(id="x", text="a" * 6001)]]:
            with self.assertRaises(ValueError):
                process(dict(request_id="r", type="translate", source_lang="en", target_lang="zh", segments=segments), lambda x: x, "test-only")
        with self.assertRaises(ValueError):
            serve(io.BytesIO(b"x" * (1024 * 1024 + 1)), io.BytesIO(), lambda x: x, "test-only")

    def test_bad_json_does_not_leak_text_and_next_request_survives(self):
        writer = io.BytesIO()
        serve(io.BytesIO(b'{"private":"not valid json"\n{"request_id":"end","type":"shutdown"}\n'), writer, lambda x: x, "test-only")
        data = writer.getvalue()
        self.assertNotIn(b"private", data)
        self.assertNotIn(b"not valid json", data)
        self.assertTrue(json.loads(data.splitlines()[-1])["shutdown"])


if __name__ == "__main__":
    unittest.main()
