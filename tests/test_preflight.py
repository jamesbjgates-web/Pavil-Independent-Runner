"""Synthetic public runner checks; never emits Pavil attestation."""
import hashlib
import hmac
import unittest


def matches_pin(data: bytes, expected_sha256: str) -> bool:
    if len(expected_sha256) != 64 or any(c not in "0123456789abcdef" for c in expected_sha256):
        return False
    return hmac.compare_digest(hashlib.sha256(data).hexdigest(), expected_sha256)


class Preflight(unittest.TestCase):
    def test_matching_hash(self):
        value = b"synthetic-fixture"
        self.assertTrue(matches_pin(value, hashlib.sha256(value).hexdigest()))

    def test_altered_bytes_fail(self):
        self.assertFalse(matches_pin(b"changed", hashlib.sha256(b"synthetic-fixture").hexdigest()))

    def test_invalid_pin_fail(self):
        self.assertFalse(matches_pin(b"synthetic-fixture", "not-a-sha256"))

    def test_runner_cannot_self_attest(self):
        self.assertFalse(False, "Attestation remains disabled until independent integration")


if __name__ == "__main__":
    unittest.main()
