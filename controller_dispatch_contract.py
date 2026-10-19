"""Controller-side GitHub workflow dispatch request contract.

This is a pure request builder. The Controller must store a narrowly scoped
token privately, enforce job eligibility and perform HTTPS I/O separately.
"""
import json
from dispatch_contract import validate_dispatch


def build_dispatch(job_id, execution_id, manifest_sha256, suite_sha256,
                   workflow_ref="main"):
    fields = validate_dispatch(job_id, execution_id,
                               manifest_sha256, suite_sha256)
    if workflow_ref != "main":
        raise ValueError("unapproved workflow ref")
    payload = {"ref": workflow_ref, "inputs": fields}
    return json.dumps(payload, separators=(",", ":")).encode()
