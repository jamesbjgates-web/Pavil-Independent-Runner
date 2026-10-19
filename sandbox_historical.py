"""Historical suite execution inside networkless, credential-free Docker."""
import hashlib, json
from pathlib import Path
from isolated_php_executor import execute
from historical_recovery_contract import HISTORICAL_JOB, HISTORICAL_SUITE, HISTORICAL_ARTIFACT
artifact=Path("/input/candidate.php").read_bytes()
suite=Path("/input/suite.php").read_bytes()
if hashlib.sha256(artifact).hexdigest()!=HISTORICAL_ARTIFACT or hashlib.sha256(suite).hexdigest()!=HISTORICAL_SUITE:
    raise ValueError("immutable inputs changed")
# The executor's temporary execution ID is a local sandbox test-run identifier,
# not an original Dell execution ID; it is deliberately excluded from the report.
local=execute(HISTORICAL_JOB,"0"*32,HISTORICAL_SUITE,artifact,suite)
data=json.loads(local)
data.pop("execution_id",None)
data["recovery_kind"]="historical_provenance_v1"
Path("/output/report.json").write_bytes(json.dumps(data,separators=(",",":")).encode())
