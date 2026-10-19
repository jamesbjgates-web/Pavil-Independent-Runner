# Pavil Independent Runner

Public, zero-cost GitHub Actions test-execution scaffold for Pavil engineering.

## Security boundary

- The public repository contains **no proprietary Controller code, job payloads, secrets or test artifacts**.
- The workflow is **manual-only** and initially executes **only synthetic self-tests**.
- A successful self-test is **NOT** independent attestation of any Pavil job.
- Candidate source, suite and test-report bytes must not be passed through workflow inputs, committed to the public repository, printed to logs or uploaded as public artifacts.
- Real independent verification requires a dedicated private authenticated input channel, verified immutable pins, an approved isolated test executor and Controller evidence submission. Until implemented and reviewed, the workflow must remain fail-closed.
- No production release or Controller job-state transition is performed by this repository.

## Operation

Open **Actions → Independent Runner Preflight → Run workflow**. This checks the runner environment and its failure handling using non-sensitive sample data; it does not contact Pavil infrastructure.

Do not enable automatic runs on untrusted pull requests or supply Controller credentials until the security and attestation integration has been completed.

## Evidence request builder

`submission_contract.py` builds an authenticated JSON submission matching
`/v1/independent-runner/submit`, with a distinct evidence HMAC and transport
HMAC. It performs no network calls, does not acquire or execute candidates,
and must **never** be called merely because a synthetic preflight passed.

**Not yet implemented:** independently acquiring the approved immutable suite
and candidate, executing each approved test in a restricted environment,
validating complete test coverage, and providing secret credentials through a
trusted private channel. No GitHub Actions job may submit evidence before these
requirements are satisfied. Public repository logs and artifacts must never
contain candidate bytes, secrets, or full reports.
