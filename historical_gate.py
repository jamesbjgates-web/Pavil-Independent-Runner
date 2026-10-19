"""Explicitly dispatched single-job historical recovery. Never marks release eligible."""
import base64, json, os, subprocess, sys, tempfile, urllib.request
from pathlib import Path
from historical_delivery import fetch, headers, ROOT, NoRedirect
from historical_recovery_contract import HISTORICAL_JOB, sign_verified_historical

def key(name):
    value=os.environ.get(name,"").encode()
    if len(value)<32: raise ValueError(name+" unavailable")
    return value

def main():
    delivery=key("PAVIL_DELIVERY_SECRET")
    transport=key("PAVIL_TRANSPORT_SECRET")
    evidence=key("PAVIL_EVIDENCE_SECRET")
    suite=fetch("suite",delivery)
    artifact=fetch("artifact",delivery)
    with tempfile.TemporaryDirectory(prefix="pavil-historical-") as directory:
        root=Path(directory)
        incoming=root/"in"; outgoing=root/"out"
        incoming.mkdir(mode=0o700); outgoing.mkdir(mode=0o700)
        (incoming/"suite.php").write_bytes(suite)
        (incoming/"candidate.php").write_bytes(artifact)
        incoming.chmod(0o755);outgoing.chmod(0o777)
        for item in incoming.iterdir():item.chmod(0o444)
        cmd=["docker","run","--rm","--network","none","--read-only",
             "--cap-drop","ALL","--security-opt","no-new-privileges",
             "--pids-limit","64","--memory","256m","--cpus","1",
             "--user","65534:65534",
             "--mount","type=bind,src="+str(incoming)+",dst=/input,readonly",
             "--mount","type=bind,src="+str(outgoing)+",dst=/output",
             "--tmpfs","/tmp:rw,noexec,nosuid,size=16m",
             "pavil-php-verifier:local","python3","/runner/sandbox_historical.py"]
        result=subprocess.run(cmd,capture_output=True,timeout=100,check=False)
        if result.returncode:raise ValueError("HISTORICAL_ISOLATED_SUITE_FAILED")
        report=(outgoing/"report.json").read_bytes()
    signed=sign_verified_historical(artifact,suite,report,evidence)
    data={"job_id":HISTORICAL_JOB,"recovery_kind":"historical_provenance_v1",
          "evidence":signed,"artifact_base64":base64.b64encode(artifact).decode(),
          "test_report_base64":base64.b64encode(report).decode()}
    body=json.dumps(data,separators=(",",":")).encode()
    path="/v1/independent-runner/historical/submit"
    request=urllib.request.Request(ROOT+path,data=body,
        headers={**headers("POST",path,body,transport),"Content-Type":"application/json"},method="POST")
    with urllib.request.build_opener(NoRedirect).open(request,timeout=30) as response:
        if response.geturl()!=ROOT+path:raise ValueError("redirect denied")
        answer=json.load(response)
    if answer.get("ok") is not True or answer.get("job_id")!=HISTORICAL_JOB or answer.get("release_eligible") is not False:
        raise ValueError("HISTORICAL_VERIFICATION_NOT_CONFIRMED")
    print("HISTORICAL_CONTROLLER_VERIFIED",HISTORICAL_JOB)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        print("HISTORICAL_GATE_FAILED:",type(exc).__name__,file=sys.stderr)
        raise SystemExit(1)
