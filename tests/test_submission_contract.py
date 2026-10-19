import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from runner_contract import digest
from submission_contract import build_submission

KEY = b"x" * 32
JOB = "a" * 32
EXECUTION = "b" * 32
SUITE = "c" * 64
MANIFEST = "d" * 64
ARTIFACT = b"synthetic-artifact"


def report(status="PASSED", execution=EXECUTION):
    return json.dumps({"job_id": JOB, "execution_id": execution,
                       "suite_sha256": SUITE,
                       "artifact_sha256": digest(ARTIFACT),
                       "status": status, "tests": [{"name": "synthetic-pin", "status": "PASSED"}]}).encode()


class SubmissionTests(unittest.TestCase):
    def submit(self, value):
        return build_submission(JOB, EXECUTION, MANIFEST, SUITE,
                                ARTIFACT, value, KEY, KEY)

    def test_submission_binds_execution(self):
        body, headers = self.submit(report())
        parsed = json.loads(body)
        self.assertEqual(parsed["execution_id"], EXECUTION)
        self.assertEqual(parsed["evidence"]["job_id"], JOB)\n        self.assertEqual(parsed["evidence"]["execution_id"], EXECUTION)
        self.assertEqual(len(parsed["evidence"]["hmac_sha256"]), 64)
        self.assertEqual(len(headers["X-Pavil-Signature"]), 64)

    def test_failed_report_denied(self):
        with self.assertRaises(ValueError):
            self.submit(report(status="FAILED"))

    def test_missing_test_results_denied(self):
        data = json.loads(report())
        del data["tests"]
        with self.assertRaises(ValueError):
            self.submit(json.dumps(data).encode())

    def test_failed_test_case_denied(self):
        data = json.loads(report())
        data["tests"][0]["status"] = "FAILED"
        with self.assertRaises(ValueError):
            self.submit(json.dumps(data).encode())

    def test_duplicate_test_case_denied(self):
        data = json.loads(report())
        data["tests"].append(dict(data["tests"][0]))
        with self.assertRaises(ValueError):
            self.submit(json.dumps(data).encode())

    def test_wrong_execution_denied(self):
        with self.assertRaises(ValueError):
            self.submit(report(execution="e" * 32))


if __name__ == "__main__":
    unittest.main()
