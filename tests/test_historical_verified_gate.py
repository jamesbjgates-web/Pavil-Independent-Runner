"""Fail-closed historical attestation regression checks."""
import unittest
from historical_recovery_contract import sign_verified_historical

class HistoricalVerifiedGateTests(unittest.TestCase):
    def setUp(self):
        self.key = b"r" * 32

    def test_wrong_artifact_denied(self):
        with self.assertRaisesRegex(ValueError, "artifact pin"):
            sign_verified_historical(b"tampered", b"suite", b"{}", self.key)

    def test_missing_artifact_denied(self):
        with self.assertRaisesRegex(ValueError, "artifact pin"):
            sign_verified_historical(b"", b"suite", b"{}", self.key)

    def test_altered_suite_not_accepted_as_artifact(self):
        with self.assertRaises(ValueError):
            sign_verified_historical(b"unapproved candidate", b"unapproved suite",
                                     b'{"status":"PASSED"}', self.key)

if __name__ == "__main__":
    unittest.main()
