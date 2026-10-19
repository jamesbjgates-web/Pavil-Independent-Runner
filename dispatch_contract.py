"""Validate metadata for an independently authorised verification request.

No Controller credentials, job contents or proprietary code are accepted
through public GitHub workflow inputs.
"""
import re

HEX32 = re.compile(r"^[0-9a-f]{32}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def validate_dispatch(job_id, execution_id, manifest_sha256, suite_sha256):
    if not HEX32.fullmatch(job_id) or not HEX32.fullmatch(execution_id):
        raise ValueError("invalid job or execution identifier")
    if not HEX64.fullmatch(manifest_sha256) or not HEX64.fullmatch(suite_sha256):
        raise ValueError("invalid immutable pin")
    return {"job_id": job_id, "execution_id": execution_id,
            "manifest_sha256": manifest_sha256, "suite_sha256": suite_sha256}
