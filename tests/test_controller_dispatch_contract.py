import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from controller_dispatch_contract import build_dispatch


class ControllerDispatchTests(unittest.TestCase):
    def test_approved_request(self):
        payload = json.loads(build_dispatch("a"*32, "b"*32, "c"*64, "d"*64))
        self.assertEqual(payload["ref"], "main")
        self.assertEqual(payload["inputs"]["execution_id"], "b"*32)

    def test_wrong_ref_denied(self):
        with self.assertRaises(ValueError):
            build_dispatch("a"*32, "b"*32, "c"*64, "d"*64, "untrusted")

    def test_invalid_pin_denied(self):
        with self.assertRaises(ValueError):
            build_dispatch("a"*32, "b"*32, "bad", "d"*64)


if __name__ == "__main__":
    unittest.main()
