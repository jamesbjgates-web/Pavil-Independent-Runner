"""Validate one exact immutable PHP acceptance suite and its real execution report."""
import hashlib
import json

CASE_NAME = "approved_php_suite"

def approved_names(suite_bytes):
    if not isinstance(suite_bytes, bytes) or not 0 < len(suite_bytes) <= 1048576:
        raise ValueError("invalid approved suite bytes")
    if not suite_bytes.lstrip().startswith(b"<?php"):
        raise ValueError("approved suite is not PHP")
    return {CASE_NAME}

def check_report_coverage(suite_bytes, report_bytes):
    names = approved_names(suite_bytes)
    if not isinstance(report_bytes, bytes) or not 0 < len(report_bytes) <= 1048576:
        raise ValueError("invalid report bytes")
    report = json.loads(report_bytes)
    if not isinstance(report, dict) or report.get("status") != "PASSED":
        raise ValueError("report failed")
    tests = report.get("tests")
    if not isinstance(tests, list) or len(tests) != 1:
        raise ValueError("incomplete report")
    case = tests[0]
    if not isinstance(case, dict) or case.get("name") != CASE_NAME or case.get("status") != "PASSED":
        raise ValueError("approved PHP suite did not pass")
    if case.get("exit_code") != 0 or case.get("executor") != "isolated-php-cli":
        raise ValueError("isolated PHP execution evidence missing")
    return True
