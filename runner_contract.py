"""Public contract helpers. No network calls or access to Pavil secrets."""
import hashlib
import hmac
import json
import re

HEX32 = re.compile(r"^[0-9a-f]{32}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_FIELDS = ("verifier", "job_id", "manifest_sha256",
                   "suite_sha256", "artifact_sha256", "test_run_sha256",
                   "status", "issued_epoch", "nonce")


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def sign_evidence(fields, secret):
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("independent evidence secret unavailable")
    if set(fields) != set(EVIDENCE_FIELDS):
        raise ValueError("unexpected evidence fields")
    if fields["verifier"] != "controller-independent-runner":
        raise ValueError("untrusted verifier")
    if fields["status"] != "PASSED":
        raise ValueError("tests not passed")
    if not HEX32.fullmatch(fields["job_id"]) or not HEX32.fullmatch(fields["nonce"]):
        raise ValueError("invalid identifier")
    for name in ("manifest_sha256", "suite_sha256",
                 "artifact_sha256", "test_run_sha256"):
        if not HEX64.fullmatch(fields[name]):
            raise ValueError("invalid SHA-256")
    if type(fields["issued_epoch"]) is not int:
        raise ValueError("invalid issue timestamp")
    canonical = {key: fields[key] for key in EVIDENCE_FIELDS}
    encoded = json.dumps(canonical, separators=(",", ":"), ensure_ascii=False).encode()
    return hmac.new(secret, encoded, hashlib.sha256).hexdigest()


def sign_transport(body, secret, timestamp, nonce):
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("independent transport secret unavailable")
    if not HEX32.fullmatch(nonce) or type(timestamp) is not int:
        raise ValueError("invalid transport metadata")
    message = "\n".join(("POST", "/v1/independent-runner/submit",
                         str(timestamp), nonce, digest(body)))
    return hmac.new(secret, message.encode(), hashlib.sha256).hexdigest()
