"""Run immutable PHP acceptance suite against immutable candidate bytes in an isolated CLI."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from report_coverage import approved_names, CASE_NAME
from runner_contract import digest

def execute(job_id, execution_id, suite_pin, artifact, suite):
    approved_names(suite)
    if digest(suite) != suite_pin:
        raise ValueError("approved suite pin mismatch")
    if not isinstance(artifact, bytes) or not 0 < len(artifact) <= 10485760:
        raise ValueError("invalid candidate artifact")
    if not artifact.lstrip().startswith(b"<?php"):
        raise ValueError("candidate is not PHP")
    with tempfile.TemporaryDirectory(prefix="pavil-independent-") as directory:
        root = Path(directory)
        source = root / "candidate.php"
        test = root / "approved_suite.php"
        source.write_bytes(artifact)
        test.write_bytes(suite)
        os.chmod(source, 0o400)
        os.chmod(test, 0o400)
        # The workflow runs inside a dedicated container with no network and
        # no host mounts or credentials. Do not execute on the Actions host.
        result = subprocess.run(
            ["php", "-d", "allow_url_fopen=0", "-d", "display_errors=stderr",
             "-d", "memory_limit=128M", str(test), str(source)],
            cwd=directory, capture_output=True, timeout=45, check=False,
        )
    if result.returncode != 0:
        raise ValueError("APPROVED_PHP_SUITE_FAILED")
    report = {"job_id": job_id, "execution_id": execution_id,
              "suite_sha256": suite_pin, "artifact_sha256": digest(artifact),
              "status": "PASSED", "tests": [
                  {"name": CASE_NAME, "status": "PASSED",
                   "exit_code": 0, "executor": "isolated-php-cli"}]}
    return json.dumps(report, separators=(",", ":")).encode()
