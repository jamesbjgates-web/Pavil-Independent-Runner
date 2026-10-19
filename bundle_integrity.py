"""Verify the integrity of a privately delivered test bundle.

This helper performs no network requests and never executes the candidate.
A trusted independent executor must separately run the approved suite.
"""
import json
from runner_contract import digest


def verify_bundle(bundle, artifact, suite):
    if not isinstance(bundle, dict):
        raise ValueError("bundle manifest missing")
    for key, data in (("artifact_sha256", artifact), ("suite_sha256", suite)):
        expected = bundle.get(key)
        if not isinstance(expected, str) or digest(data) != expected:
            raise ValueError("immutable input pin mismatch")
    tests = json.loads(suite).get("tests")
    if not isinstance(tests, list) or not tests:
        raise ValueError("approved suite unavailable")
    return len(tests)
