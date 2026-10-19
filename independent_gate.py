"""Independent delivery, isolated execution, and signed submission entrypoint."""
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from independent_delivery import retrieve_approved_pair
from runner_contract import digest
from submission_contract import build_submission

def required(name):
    value = os.environ.get(name, "")
    if not value:
        raise ValueError(name + " unavailable")
    return value

def main():
    job = required("JOB_ID")
    execution = required("EXECUTION_ID")
    manifest = required("MANIFEST_SHA256")
    suite_pin = required("SUITE_SHA256")
    delivery = required("PAVIL_DELIVERY_SECRET").encode()
    evidence = required("PAVIL_EVIDENCE_SECRET").encode()
    transport = required("PAVIL_TRANSPORT_SECRET").encode()
    if min(map(len, (delivery, evidence, transport))) < 32:
        raise ValueError("private runner credentials unavailable")
    pair = retrieve_approved_pair(job, execution, suite_pin, delivery)
    with tempfile.TemporaryDirectory(prefix="pavil-gate-") as directory:
        root = Path(directory)
        incoming = root / "in"
        outgoing = root / "out"
        incoming.mkdir(mode=0o700)
        outgoing.mkdir(mode=0o700)
        (incoming / "suite.php").write_bytes(pair["suite"])
        (incoming / "candidate.php").write_bytes(pair["artifact"])
        (incoming / "metadata.json").write_text(json.dumps({
            "job_id": job, "execution_id": execution,
            "suite_sha256": suite_pin}))
        # No secrets, network, writable root, host filesystem or extra capabilities.
        # PHP code can only read immutable inputs and write the report volume.
        cmd = ["docker", "run", "--rm", "--network", "none",
               "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
               "--pids-limit", "64", "--memory", "256m", "--cpus", "1",
               "--user", "65534:65534",
               "--mount", "type=bind,src="+str(incoming)+",dst=/input,readonly",
               "--mount", "type=bind,src="+str(outgoing)+",dst=/output",
               "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
               "pavil-php-verifier:local",
               "python3", "/runner/sandbox_entry.py"]
        incoming.chmod(0o755)
        outgoing.chmod(0o777)
        for item in incoming.iterdir():
            item.chmod(0o444)
        result = subprocess.run(cmd, capture_output=True, timeout=100, check=False)
        if result.returncode:
            raise ValueError("ISOLATED_ACCEPTANCE_FAILED")
        report = (outgoing / "report.json").read_bytes()
        body, headers = build_submission(job, execution, manifest, suite_pin,
                                         pair["artifact"], report, evidence,
                                         transport, approved_suite=pair["suite"])
        request = urllib.request.Request(
            "https://controller.pspt.ltd/v1/independent-runner/submit",
            data=body, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            answer = json.load(response)
        if not isinstance(answer, dict) or answer.get("ok") is not True:
            raise ValueError("CONTROLLER_DID_NOT_ACCEPT_VERIFICATION")
        print("CONTROLLER_VERIFICATION_ACCEPTED", job)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("INDEPENDENT_VERIFICATION_FAILED:", type(exc).__name__, file=sys.stderr)
        raise SystemExit(1)
