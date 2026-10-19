"""Independent historical recovery evidence. Never represents a Dell execution ID."""
import hashlib
import hmac
import json
import secrets
import time

FIELDS = ("verifier", "recovery_kind", "job_id", "manifest_sha256",
          "suite_sha256", "artifact_sha256", "test_run_sha256",
          "status", "issued_epoch", "nonce")

def sign_historical(job_id, manifest_pin, suite_pin, artifact, report, key):
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("runner evidence key unavailable")
    if not artifact or not report:
        raise ValueError("evidence bytes missing")
    evidence = {
        "verifier": "controller-independent-runner",
        "recovery_kind": "historical_provenance_v1",
        "job_id": job_id,
        "manifest_sha256": manifest_pin,
        "suite_sha256": suite_pin,
        "artifact_sha256": hashlib.sha256(artifact).hexdigest(),
        "test_run_sha256": hashlib.sha256(report).hexdigest(),
        "status": "PASSED",
        "issued_epoch": int(time.time()),
        "nonce": secrets.token_hex(16),
    }
    canonical = {name: evidence[name] for name in FIELDS}
    encoded = json.dumps(canonical, separators=(",", ":")).encode()
    evidence["hmac_sha256"] = hmac.new(key, encoded, hashlib.sha256).hexdigest()
    return evidence

# Only this single legacy job is eligible for the historical recovery protocol.
HISTORICAL_JOB = "5e912acdd6cf8267011821980cf39b6d"
HISTORICAL_MANIFEST = "ed73768a56ac4901b51cf03369c8289f5405d43c76394b748441bcbb29d3bd7e"
HISTORICAL_SUITE = "66e240cd3e8f081098b3e916e35e52093cc83bd325abbf0aa57432f8f5e212d8"
HISTORICAL_ARTIFACT = "1417695e408e13ceb421d66995131f6b90897ab3056e2aa1899ce123607050d3"

def sign_verified_historical(artifact, suite, report, key):
    """Only sign evidence after independently checking immutable bytes and test report."""
    if not artifact or hashlib.sha256(artifact).hexdigest() != HISTORICAL_ARTIFACT:
        raise ValueError("historical artifact pin mismatch")
    if not suite or hashlib.sha256(suite).hexdigest() != HISTORICAL_SUITE:
        raise ValueError("historical suite pin mismatch")
    if not report or len(report) > 1048576:
        raise ValueError("historical report missing or oversized")
    try:
        data = json.loads(report)
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("historical report invalid") from exc
    if not isinstance(data, dict) or (
        data.get("job_id") != HISTORICAL_JOB or
        data.get("recovery_kind") != "historical_provenance_v1" or
        data.get("suite_sha256") != HISTORICAL_SUITE or
        data.get("artifact_sha256") != HISTORICAL_ARTIFACT or
        data.get("status") != "PASSED" or
        "execution_id" in data
    ):
        raise ValueError("historical report binding invalid")
    tests = data.get("tests")
    if not isinstance(tests, list) or len(tests) != 1 or not isinstance(tests[0], dict):
        raise ValueError("historical test coverage invalid")
    test = tests[0]
    if (test.get("name") != "approved_php_suite" or
        test.get("status") != "PASSED" or
        type(test.get("exit_code")) is not int or test["exit_code"] != 0 or
        test.get("executor") != "isolated-php-cli"):
        raise ValueError("historical approved suite not passed")
    return sign_historical(HISTORICAL_JOB, HISTORICAL_MANIFEST,
                           HISTORICAL_SUITE, artifact, report, key)
