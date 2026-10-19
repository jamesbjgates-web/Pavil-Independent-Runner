import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from report_coverage import check_report_coverage


def encoded(value):
    return json.dumps(value).encode()


SUITE = encoded({"tests": [{"name": "alpha"}, {"name": "beta"}]})
REPORT = {"status": "PASSED", "tests": [
    {"name": "alpha", "status": "PASSED"},
    {"name": "beta", "status": "PASSED"}]}


class CoverageTests(unittest.TestCase):
    def test_exact_coverage(self):
        self.assertTrue(check_report_coverage(SUITE, encoded(REPORT)))

    def test_string_named_approved_suite(self):
        suite = encoded({"tests": ["alpha", "beta"]})
        self.assertTrue(check_report_coverage(suite, encoded(REPORT)))

    def test_missing_case(self):
        data = dict(REPORT, tests=REPORT["tests"][:1])
        with self.assertRaises(ValueError):
            check_report_coverage(SUITE, encoded(data))

    def test_duplicate_case(self):
        data = dict(REPORT, tests=[REPORT["tests"][0]] * 2)
        with self.assertRaises(ValueError):
            check_report_coverage(SUITE, encoded(data))

    def test_unapproved_case(self):
        data = dict(REPORT, tests=[REPORT["tests"][0],
                                   {"name": "gamma", "status": "PASSED"}])
        with self.assertRaises(ValueError):
            check_report_coverage(SUITE, encoded(data))

    def test_failed_case(self):
        data = dict(REPORT, tests=[REPORT["tests"][0],
                                   {"name": "beta", "status": "FAILED"}])
        with self.assertRaises(ValueError):
            check_report_coverage(SUITE, encoded(data))


if __name__ == "__main__":
    unittest.main()
