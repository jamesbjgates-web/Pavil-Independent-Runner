"""Sandbox-only entrypoint. No network, tokens or Controller access."""
import json
from pathlib import Path
from isolated_php_executor import execute

metadata = json.loads(Path("/input/metadata.json").read_text())
suite = Path("/input/suite.php").read_bytes()
artifact = Path("/input/candidate.php").read_bytes()
report = execute(metadata["job_id"], metadata["execution_id"],
                 metadata["suite_sha256"], artifact, suite)
Path("/output/report.json").write_bytes(report)
