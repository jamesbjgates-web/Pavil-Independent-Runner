"""Check exact approved test coverage in a proposed report.

This is a pure validator, not an executor or proof that tests ran.
"""
import json


def approved_names(suite_bytes):
    if not isinstance(suite_bytes, bytes) or not 0 < len(suite_bytes) <= 1048576:
        raise ValueError("invalid approved suite bytes")
    suite = json.loads(suite_bytes)
    if not isinstance(suite, dict):
        raise ValueError("invalid approved suite")
    tests = suite.get("tests")
    if not isinstance(tests, list) or not 1 <= len(tests) <= 500:
        raise ValueError("invalid approved test count")
    names = set()
    for test in tests:
        name = test if isinstance(test, str) else test.get("name") if isinstance(test, dict) else None
        if not isinstance(name, str):
            raise ValueError("invalid approved test")
        if not name or len(name) > 256 or name in names:
            raise ValueError("duplicate or invalid approved test name")
        names.add(name)
    return names


def check_report_coverage(suite_bytes, report_bytes):
    names = approved_names(suite_bytes)
    if not isinstance(report_bytes, bytes) or not 0 < len(report_bytes) <= 1048576:
        raise ValueError("invalid report bytes")
    report = json.loads(report_bytes)
    if not isinstance(report, dict) or report.get("status") != "PASSED":
        raise ValueError("report failed")
    tests = report.get("tests")
    if not isinstance(tests, list) or len(tests) != len(names):
        raise ValueError("incomplete report")
    observed = set()
    for test in tests:
        if not isinstance(test, dict) or test.get("status") != "PASSED":
            raise ValueError("failed test case")
        name = test.get("name")
        if not isinstance(name, str) or name not in names or name in observed:
            raise ValueError("unapproved or repeated test")
        observed.add(name)
    return observed == names
