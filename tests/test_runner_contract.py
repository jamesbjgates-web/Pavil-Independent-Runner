import hashlib
import hmac
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runner_contract import digest, sign_evidence, sign_transport

KEY = b"k" * 32


class SigningContractTests(unittest.TestCase):
    def sample(self):
        return dict(verifier="controller-independent-runner",
                    job_id="a"*32, manifest_sha256="b"*64,
                    suite_sha256="c"*64, artifact_sha256="d"*64,
                    test_run_sha256="e"*64, status="PASSED",
                    issued_epoch=1700000000, nonce="f"*32)

    def test_evidence_signature(self):
        signature = sign_evidence(self.sample(), KEY)
        self.assertEqual(len(signature), 64)

    def test_failed_status_denied(self):
        data = self.sample()
        data["status"] = "FAILED"
        with self.assertRaises(ValueError):
            sign_evidence(data, KEY)

    def test_missing_key_denied(self):
        with self.assertRaises(ValueError):
            sign_evidence(self.sample(), b"short")

    def test_transport_canonicalization(self):
        body = b'{"synthetic":true}'
        nonce = "1"*32
        message = ("POST\n/v1/independent-runner/submit\n"
                   "1700000000\n" + nonce + "\n" + digest(body))
        expected = hmac.new(KEY, message.encode(), hashlib.sha256).hexdigest()
        self.assertEqual(sign_transport(body, KEY, 1700000000, nonce), expected)


if __name__ == "__main__":
    unittest.main()
