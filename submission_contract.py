"""Fail-closed independent runner submission contract. No I/O."""
import base64
import json
import secrets
import time
from runner_contract import digest, sign_evidence, sign_transport
from report_coverage import check_report_coverage


def build_submission(job_id, execution_id, manifest_pin, suite_pin,
                     artifact, report, evidence_key, transport_key, *, approved_suite):
    if not artifact or len(artifact) > 10485760:
        raise ValueError("invalid artifact")
    if not report or len(report) > 1048576:
        raise ValueError("invalid test report")
    if digest(approved_suite) != suite_pin:
        raise ValueError("approved suite pin mismatch")
    if not check_report_coverage(approved_suite, report):
        raise ValueError("approved suite coverage mismatch")
    data = json.loads(report)
    if not isinstance(data, dict):
        raise ValueError("invalid test report")
    if (data.get("job_id") != job_id or
            data.get("execution_id") != execution_id or
            data.get("suite_sha256") != suite_pin or
            data.get("artifact_sha256") != digest(artifact) or
            data.get("status") != "PASSED"):
        raise ValueError("test report binding failed")
    tests = data.get("tests")
    if not isinstance(tests, list) or not 1 <= len(tests) <= 500:
        raise ValueError("test coverage unavailable")
    seen = set()
    for case in tests:
        if not isinstance(case, dict):
            raise ValueError("invalid test case")
        name = case.get("name")
        if not isinstance(name, str) or not name or name in seen:
            raise ValueError("duplicate or unnamed test case")
        if case.get("status") != "PASSED":
            raise ValueError("test case not passed")
        seen.add(name)
    evidence = {
        "verifier": "controller-independent-runner",
        "job_id": job_id,
        "manifest_sha256": manifest_pin,
        "suite_sha256": suite_pin,
        "artifact_sha256": digest(artifact),
        "test_run_sha256": digest(report),
        "status": "PASSED",
        "issued_epoch": int(time.time()),
        "nonce": secrets.token_hex(16),
    }
    # Controller submission requires this additional execution binding.
    # The signed report digest commits to the same execution ID.
    evidence_signature = sign_evidence(evidence, evidence_key)
    evidence["execution_id"] = execution_id
    evidence["hmac_sha256"] = evidence_signature
    request = {
        "job_id": job_id,
        "execution_id": execution_id,
        "evidence": evidence,
        "artifact_base64": base64.b64encode(artifact).decode(),
        "test_report_base64": base64.b64encode(report).decode(),
    }
    body = json.dumps(request, separators=(",", ":")).encode()
    stamp = int(time.time())
    nonce = secrets.token_hex(16)
    headers = {
        "Content-Type": "application/json",
        "X-Pavil-Timestamp": str(stamp),
        "X-Pavil-Nonce": nonce,
        "X-Pavil-Signature": sign_transport(body, transport_key, stamp, nonce),
    }
    return body, headers
