# Contract: FND-006 Cloud Run Foundation Deployment

## Purpose

Define the externally visible deployment and hosted verification expectations
for the foundation MCP service. This contract does not change the MCP protocol;
it formalizes the minimum checks and evidence required before a hosted revision
is considered ready.

## Deployment Outcome Contract

A deployment run is considered successful only when all of the following are
true:

1. A new hosted revision is created from the current codebase.
2. The revision has explicit runtime settings for:
   - execution identity
   - environment profile
   - non-secret configuration inputs
   - secret references
   - minimum instances
   - maximum instances
   - request concurrency
   - request timeout
3. The hosted endpoint is available for verification.
4. A verification record exists for every required post-deploy check.

## Required Post-Deploy Checks

The hosted verification flow MUST run in this order:

1. `liveness`
   - Target: hosted `/healthz`
   - Expected result: healthy status response
2. `readiness`
   - Target: hosted `/readyz`
   - Expected result: ready status response when deployment inputs are valid
3. `initialize`
   - Target: hosted MCP endpoint
   - Expected result: declared server capabilities returned successfully
4. `list-tools`
   - Target: hosted MCP endpoint
   - Expected result: baseline tool names and descriptions returned successfully
5. `baseline-tool-call`
   - Target: hosted MCP endpoint
   - Expected result: at least one baseline tool returns a successful structured response

If `liveness` or `readiness` fails, MCP verification MUST NOT be reported as
passing for that revision.

## Verification Evidence Contract

Each verification run MUST record:

- `revisionName`
- `endpointUrl`
- `executedAt` timestamp per check
- `checkName`
- `result` (`pass` or `fail`)
- operator-readable outcome summary

For failed checks, the verification record MUST also identify:

- the failed stage
- whether the failure was deployment-time, readiness-time, or MCP-time
- the next remediation action or referenced operator guidance

## Stability Expectations

- Existing `/healthz`, `/readyz`, and MCP response contracts remain unchanged.
- Hosted deployment work MUST NOT introduce new mandatory client request fields.
- Hosted verification evidence MUST be sufficient for an operator to determine
  whether the revision is safe for MCP client use without inspecting source
  code.

## Testable Assertions

- Contract tests can verify that deployment documentation requires all runtime
  settings and verification evidence fields.
- Integration tests can verify that hosted verification helpers execute the
  required check order and stop reporting success when prerequisite checks fail.
- Manual or hosted acceptance validation can verify that a real revision passes
  liveness, readiness, initialize, list-tools, and baseline-tool-call.
