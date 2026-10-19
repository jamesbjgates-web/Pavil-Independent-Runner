"""Fail-closed contract tests; no Controller access or credentials."""
import hashlib
import hmac
import json
import unittest
from unittest.mock import patch
from historical_recovery_contract import sign_historical

class RecoveryContractTests(unittest.TestCase):
    def setUp(self):
        self.key = b"x" * 32
        self.artifact = b"candidate"
        self.report = b'{"status":"PASSED"}'
    def test_signature_matches_controller_canonical_fields(self):
        with patch("historical_recovery_contract.time.time", return_value=1000), patch("historical_recovery_contract.secrets.token_hex", return_value="a"*32):
            signed = sign_historical("b"*32, "c"*64, "d"*64, self.artifact, self.report, self.key)
        signature = signed.pop("hmac_sha256")
        self.assertNotIn("execution_id", signed)
        self.assertEqual(signed["recovery_kind"], "historical_provenance_v1")
        expected = hmac.new(self.key, json.dumps(signed, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
        self.assertEqual(signature, expected)
        signed["status"] = "FAILED"
        altered = hmac.new(self.key, json.dumps(signed, separators=(",", ":")).encode(), hashlib.sha256).hexdigest()
        self.assertNotEqual(signature, altered)
    def test_missing_key_denied(self):
        with self.assertRaises(ValueError):
            sign_historical("b"*32, "c"*64, "d"*64, self.artifact, self.report, b"short")
    def test_missing_bytes_denied(self):
        with self.assertRaises(ValueError):
            sign_historical("b"*32, "c"*64, "d"*64, b"", self.report, self.key)
        with self.assertRaises(ValueError):
            sign_historical("b"*32, "c"*64, "d"*64, self.artifact, b"", self.key)

if __name__ == "__main__":
    unittest.main()
