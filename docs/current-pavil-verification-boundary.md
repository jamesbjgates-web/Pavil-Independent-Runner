# Current Pavil candidate verification boundary (draft, 2026-10-30)

This specification applies only to the current HostPapa bridge and Dell Ubuntu worker. It is not a migration of the previous Controller.

## Verified current evidence
- Candidate: `auto_m57_001`; objective: `bridge_observability_v1`.
- Generated files: `bridge_observability.py`, `test_bridge_observability.py`, `README.md`, `manifest.json`.
- Manifest states AI review approved and **tests not executed at generation time**.
- Subsequent local tests: 5 passed; these are **not GitHub CI attestation**.
- This public repository contains no current candidate source.

## Boundary rules
1. Candidate and approved test-suite bytes remain in a **private, authenticated** staging location. Never place them in public repository commits, workflow inputs, logs, artifacts or PRs.
2. The verification worker must retrieve a *pinned* candidate and suite by immutable digests, authenticate their provenance, and reject mismatches before any execution.
3. Run untrusted candidate tests only inside a hardened, ephemeral sandbox with no production mounts, no secrets, no outbound network and bounded CPU/memory/time. GitHub-hosted runners alone are not proof of adequate sandboxing.
4. Generate a machine-readable result containing job ID, candidate and suite digests, test counts, exit status, verifier identity, execution policy version, nonce and timestamp. Authenticate it using a credential available **only to the trusted verifier**.
5. The current Controller must independently validate the result, replay protection, digests, approved job identity and verifier authorization. A test pass must never itself grant deployment authority.
6. On missing pins, missing isolation, unsupported inputs, timeout, signature failure or incomplete test coverage: **fail closed** and request review.

## Integration prerequisites (not yet verified)
- Actual current bridge API for approved immutable candidate retrieval and evidence submission.
- Approved private storage and authentication channel.
- Hardened isolated test executor and resource limits.
- Independent Controller-side result verifier and replay protection.
- Non-production end-to-end test with recorded evidence.

## Explicit exclusions
- No production Controller deployment or state transition.
- No automatic execution of candidate source on Dell host.
- No reuse of legacy Controller code, keys or job evidence.
- No assertion that the current synthetic GitHub workflow verifies `auto_m57_001`.

## Next acceptance test
An approved non-production candidate must be fetched privately, checked against immutable pins, tested inside the isolated executor, and returned as an authenticated receipt accepted by the **current** Controller. Record the job ID, digest, CI run ID, test summary and Controller acknowledgement.