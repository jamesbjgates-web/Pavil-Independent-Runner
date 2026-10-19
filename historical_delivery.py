"""Authenticated immutable historical delivery; never invent Dell execution IDs."""
import base64, hashlib, hmac, json, secrets, time, urllib.request
from historical_recovery_contract import HISTORICAL_JOB, HISTORICAL_SUITE, HISTORICAL_ARTIFACT
ROOT = "https://controller.pspt.ltd"
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None
def headers(method, path, body, secret):
    if len(secret) < 32: raise ValueError("transport key unavailable")
    stamp, nonce = str(int(time.time())), secrets.token_hex(16)
    canonical = "\n".join((method, path, stamp, nonce, hashlib.sha256(body).hexdigest()))
    return {"X-Pavil-Timestamp": stamp, "X-Pavil-Nonce": nonce,
            "X-Pavil-Signature": hmac.new(secret, canonical.encode(), hashlib.sha256).hexdigest()}
def fetch(kind, secret):
    if kind not in ("suite","artifact"): raise ValueError("kind invalid")
    pin = HISTORICAL_SUITE if kind=="suite" else HISTORICAL_ARTIFACT
    path = "/v1/independent-runner/historical/{}/{}".format(kind,HISTORICAL_JOB)
    hdr = headers("GET",path,b"",secret)
    hdr["X-Pavil-Content-Sha256"]=pin
    req = urllib.request.Request(ROOT+path,headers=hdr,method="GET")
    with urllib.request.build_opener(NoRedirect).open(req,timeout=30) as response:
        if response.geturl()!=ROOT+path: raise ValueError("redirect denied")
        raw=response.read(3_000_001)
    if len(raw)>3_000_000: raise ValueError("response oversized")
    data=json.loads(raw)
    if data.get("ok") is not True or data.get("job_id")!=HISTORICAL_JOB or data.get("recovery_kind")!="historical_provenance_v1" or data.get(kind+"_sha256")!=pin:
        raise ValueError("delivery identity invalid")
    value=base64.b64decode(data[kind+"_base64"],validate=True)
    if not value or len(value)>2097152 or hashlib.sha256(value).hexdigest()!=pin:
        raise ValueError("delivery checksum invalid")
    return value
