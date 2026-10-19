"""Independent immutable delivery client. Never logs secrets or retrieved bytes."""
import base64
import hashlib
import hmac
import json
import re
import secrets
import time
import urllib.error
import urllib.request

_HEX32 = re.compile(r"^[0-9a-f]{32}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ROOT = "https://controller.pspt.ltd"


def signed_get_headers(path, secret, execution_id, sha256, *, now=None, nonce=None):
    if not re.fullmatch(r"/v1/independent-runner/(suite|artifact)/[0-9a-f]{32}", path):
        raise ValueError("invalid delivery path")
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise ValueError("transport secret unavailable")
    if not isinstance(execution_id, str) or not _HEX32.fullmatch(execution_id):
        raise ValueError("invalid execution id")
    if not isinstance(sha256, str) or not _HEX64.fullmatch(sha256):
        raise ValueError("invalid content pin")
    stamp = int(time.time()) if now is None else now
    token = secrets.token_hex(16) if nonce is None else nonce
    if type(stamp) is not int or not _HEX32.fullmatch(token):
        raise ValueError("invalid timestamp or nonce")
    canonical = "\n".join(("GET", path, str(stamp), token, hashlib.sha256(b"").hexdigest()))
    signature = hmac.new(secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()
    return {"X-Pavil-Timestamp": str(stamp), "X-Pavil-Nonce": token,
            "X-Pavil-Signature": signature,
            "X-Pavil-Execution-Id": execution_id,
            "X-Pavil-Content-Sha256": sha256}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def retrieve(kind, job_id, execution_id, sha256, secret, *, opener=None):
    if kind not in ("suite", "artifact") or not isinstance(job_id, str) or not _HEX32.fullmatch(job_id):
        raise ValueError("invalid delivery selector")
    path = "/v1/independent-runner/{}/{}".format(kind, job_id)
    request = urllib.request.Request(_ROOT + path,
        headers=signed_get_headers(path, secret, execution_id, sha256),
        method="GET")
    transport = urllib.request.build_opener(_NoRedirect).open if opener is None else opener
    try:
        with transport(request, timeout=30) as response:
            if response.geturl() != _ROOT + path:
                raise ValueError("delivery redirect denied")
            raw = response.read(3_000_001)
    except urllib.error.HTTPError as error:
        raise ValueError("delivery denied (HTTP {})".format(error.code)) from None
    if len(raw) > 3_000_000:
        raise ValueError("delivery response oversized")
    result = json.loads(raw)
    if not isinstance(result, dict) or result.get("ok") is not True:
        raise ValueError("delivery unavailable")
    if result.get("job_id") != job_id or result.get("execution_id") != execution_id:
        raise ValueError("delivery identity mismatch")
    if result.get(kind + "_sha256") != sha256:
        raise ValueError("delivery pin mismatch")
    encoded = result.get(kind + "_base64")
    if not isinstance(encoded, str):
        raise ValueError("delivery bytes missing")
    payload = base64.b64decode(encoded, validate=True)
    if not payload or len(payload) > 2_097_152 or hashlib.sha256(payload).hexdigest() != sha256:
        raise ValueError("delivery checksum mismatch")
    return payload
