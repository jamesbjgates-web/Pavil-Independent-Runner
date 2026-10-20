"""Offline, no-network checks for stage-specific independent-gate diagnostics."""
import io
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr
from unittest.mock import patch

import independent_gate as gate


class GateDiagnosticsTests(unittest.TestCase):
    def test_delivery_failure_is_bounded(self):
        def denied(*args):
            raise ValueError("secret material must never appear")
        with self.assertRaises(gate.GateFailure) as ctx:
            gate.guarded("CONFIDENTIAL_DELIVERY", denied)
        self.assertEqual(ctx.exception.stage, "CONFIDENTIAL_DELIVERY")
        self.assertEqual(ctx.exception.code, "VALUE_INVALID")
        self.assertNotIn("secret material", str(ctx.exception))

    def test_missing_inputs_fail_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                gate.required("JOB_ID")

    def test_runner_never_starts_without_credentials(self):
        env = {"JOB_ID": "a" * 32, "EXECUTION_ID": "b" * 32,
               "MANIFEST_SHA256": "c" * 64, "SUITE_SHA256": "d" * 64,
               "PAVIL_DELIVERY_SECRET": "short",
               "PAVIL_EVIDENCE_SECRET": "short",
               "PAVIL_TRANSPORT_SECRET": "short"}
        with patch.dict(os.environ, env, clear=True):
            with patch.object(gate, "retrieve_approved_pair") as retrieve:
                with self.assertRaises(ValueError):
                    gate.main()
                retrieve.assert_not_called()

    def test_delivery_stage_reports_only_safe_code(self):
        env = {"JOB_ID": "a" * 32, "EXECUTION_ID": "b" * 32,
               "MANIFEST_SHA256": "c" * 64, "SUITE_SHA256": "d" * 64,
               "PAVIL_DELIVERY_SECRET": "x" * 32,
               "PAVIL_EVIDENCE_SECRET": "y" * 32,
               "PAVIL_TRANSPORT_SECRET": "z" * 32}
        with patch.dict(os.environ, env, clear=True):
            with patch.object(gate, "retrieve_approved_pair",
                              side_effect=ValueError("private body")):
                with self.assertRaises(gate.GateFailure) as ctx:
                    gate.main()
        self.assertEqual((ctx.exception.stage, ctx.exception.code),
                         ("CONFIDENTIAL_DELIVERY", "VALUE_INVALID"))
        self.assertNotIn("private body", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
