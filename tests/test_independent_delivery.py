"""Unit tests for immutable runner retrieval without external network calls."""
import base64
import hashlib
import hmac
import io
import json
import unittest
from independent_delivery import retrieve, signed_get_headers


class FakeResponse:
    def __init__(self, url, data):
        self.url, self.data = url, data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False
    def geturl(self):
        return self.url
    def read(self, size):
        return self.data


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.job = "a" * 32
        self.execution = "b" * 32
        self.secret = b"k" * 32
        self.bytes = b'{"tests":["one"]}'
        self.pin = hashlib.sha256(self.bytes).hexdigest()

    def test_get_signature_matches_controller_canonical(self):
        path = "/v1/independent-runner/suite/" + self.job
        headers = signed_get_headers(path, self.secret, self.execution,
                                     self.pin, now=12345, nonce="c" * 32)
        canonical = "\n".join(("GET", path, "12345", "c" * 32,
                                hashlib.sha256(b"").hexdigest()))
        expected = hmac.new(self.secret, canonical.encode(), hashlib.sha256).hexdigest()
        self.assertEqual(headers["X-Pavil-Signature"], expected)

    def test_valid_pinned_bytes(self):
        body = json.dumps({"ok": True, "job_id": self.job,
                           "execution_id": self.execution,
                           "suite_sha256": self.pin,
                           "suite_base64": base64.b64encode(self.bytes).decode()}).encode()
        def open_ok(request, timeout):
            return FakeResponse(request.full_url, body)
        self.assertEqual(retrieve("suite", self.job, self.execution,
                                  self.pin, self.secret, opener=open_ok), self.bytes)

    def test_redirect_rejected(self):
        def redirected(request, timeout):
            return FakeResponse("https://elsewhere.invalid/", b"{}")
        with self.assertRaisesRegex(ValueError, "redirect"):
            retrieve("suite", self.job, self.execution, self.pin,
                     self.secret, opener=redirected)

    def test_default_transport_installs_no_redirect_handler(self):
        from unittest.mock import patch
        from independent_delivery import _NoRedirect
        handlers = []
        def build_opener(*args):
            handlers.extend(args)
            class StubOpener:
                def open(self, request, timeout):
                    raise ValueError("stopped before network")
            return StubOpener()
        with patch("independent_delivery.urllib.request.build_opener", side_effect=build_opener):
            with self.assertRaisesRegex(ValueError, "stopped before network"):
                retrieve("suite", self.job, self.execution, self.pin, self.secret)
        self.assertEqual(len(handlers), 1)
        self.assertIsInstance(handlers[0], _NoRedirect)
        self.assertIsNone(handlers[0].redirect_request(None, None, 302, "", {}, "https://elsewhere.invalid"))

    def test_checksum_rejected(self):
        body = json.dumps({"ok": True, "job_id": self.job,
                           "execution_id": self.execution,
                           "suite_sha256": self.pin,
                           "suite_base64": base64.b64encode(b"wrong").decode()}).encode()
        def bad(request, timeout):
            return FakeResponse(request.full_url, body)
        with self.assertRaisesRegex(ValueError, "checksum"):
            retrieve("suite", self.job, self.execution, self.pin,
                     self.secret, opener=bad)

    def test_short_secret_rejected(self):
        with self.assertRaisesRegex(ValueError, "secret"):
            signed_get_headers("/v1/independent-runner/suite/" + self.job,
                               b"short", self.execution, self.pin)


if __name__ == "__main__":
    unittest.main()
