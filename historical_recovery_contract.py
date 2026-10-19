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
