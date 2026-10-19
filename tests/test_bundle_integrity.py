import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bundle_integrity import verify_bundle
from runner_contract import digest

ARTIFACT = b"synthetic"
SUITE = json.dumps({"tests": [{"name": "example"}]}).encode()


class BundleIntegrityTests(unittest.TestCase):
    def test_pinned_bundle(self):
        pins = {"artifact_sha256": digest(ARTIFACT),
                "suite_sha256": digest(SUITE)}
        self.assertEqual(verify_bundle(pins, ARTIFACT, SUITE), 1)

    def test_modified_artifact_denied(self):
        pins = {"artifact_sha256": digest(ARTIFACT),
                "suite_sha256": digest(SUITE)}
        with self.assertRaises(ValueError):
            verify_bundle(pins, b"altered", SUITE)

    def test_modified_suite_denied(self):
        pins = {"artifact_sha256": digest(ARTIFACT),
                "suite_sha256": digest(SUITE)}
        with self.assertRaises(ValueError):
            verify_bundle(pins, ARTIFACT, b"altered")


if __name__ == "__main__":
    unittest.main()
