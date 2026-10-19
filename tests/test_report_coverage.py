import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from report_coverage import check_report_coverage


def encoded(value):
    return json.dumps(value).encode()


SUITE = b"<?php // approved test fixture"
REPORT = {"status": "PASSED", "tests": [
    {"name": "approved_php_suite", "status": "PASSED",
     "exit_code": 0, "executor": "isolated-php-cli"}]}


class CoverageTests(unittest.TestCase):
    def test_exact_coverage(self):
        self.assertTrue(check_report_coverage(SUITE, encoded(REPORT)))

    def test_string_named_approved_suite(self):
        suite = b"<?php // alternate approved PHP fixture"
        self.assertTrue(check_report_coverage(suite, encoded(REPORT)))

    def test_missing_case(self):
        data = dict(REPORT, tests=[])
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
                                   {"name": "approved_php_suite", "status": "FAILED"}])
        with self.assertRaises(ValueError):
            check_report_coverage(SUITE, encoded(data))


if __name__ == "__main__":
    unittest.main()
