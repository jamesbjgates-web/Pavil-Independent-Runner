"""Sandbox-only entrypoint. No network, tokens or Controller access."""
import json
from pathlib import Path
from isolated_php_executor import execute

metadata = json.loads(Path("/input/metadata.json").read_text())
suite = Path("/input/suite.php").read_bytes()
artifact = Path("/input/candidate.php").read_bytes()
# The approved dispatcher suite uses a repository-relative include.
# Select its immutable layout only when the approved suite pin matches.
DISPATCHER_SUITE_PIN = "66e240cd3e8f081098b3e916e35e52093cc83bd325abbf0aa57432f8f5e212d8"
layout = "dispatcher_contract" if metadata["suite_sha256"] == DISPATCHER_SUITE_PIN else "flat"
report = execute(metadata["job_id"], metadata["execution_id"],
                 metadata["suite_sha256"], artifact, suite, layout=layout)
Path("/output/report.json").write_bytes(report)
