import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dispatch_contract import validate_dispatch


class DispatchContractTests(unittest.TestCase):
    def test_valid_metadata(self):
        data = validate_dispatch("a"*32, "b"*32, "c"*64, "d"*64)
        self.assertEqual(data["job_id"], "a"*32)

    def test_invalid_job_denied(self):
        with self.assertRaises(ValueError):
            validate_dispatch("invalid", "b"*32, "c"*64, "d"*64)

    def test_invalid_suite_pin_denied(self):
        with self.assertRaises(ValueError):
            validate_dispatch("a"*32, "b"*32, "c"*64, "bad")


if __name__ == "__main__":
    unittest.main()
