# Contract: Hosted Dependency Verification

## Purpose

Define the hosted verification contract that proves runtime secret access and durable session connectivity are wired correctly for a deployed environment.

## Actors

- Operator running hosted verification after deployment
- Reviewer validating rollout evidence
- Maintainer diagnosing hosted dependency-wiring failures

## Verification Order

The hosted dependency verification flow for an environment claiming durable hosted session support must run in this order:

1. `deployment-evidence`
   - Target: deployment record and provider-adapter outputs
   - Expected result: runtime identity, secret references, and session backend references are present
2. `secret-access`
   - Target: hosted runtime secret-backed configuration path
   - Expected result: runtime can access required secrets without exposing values
3. `readiness`
   - Target: hosted `/ready`
   - Expected result: ready hosted response when dependency wiring is healthy
4. `session-connectivity`
   - Target: durable session backend path
   - Expected result: hosted runtime can reach the required shared backend
5. `session-continuation`
   - Target: protected hosted `/mcp`
   - Expected result: at least one hosted session continuation flow succeeds

If `deployment-evidence`, `secret-access`, `readiness`, or `session-connectivity` fails, session-continuation success must not be reported for that environment.

## Failure Interpretation

### Secret-Access Failure

- Applies when the hosted runtime cannot read required secret-backed configuration.
- Must include categories such as missing permission, missing reference, or invalid reference.
- Must include remediation guidance aimed at runtime identity or secret-reference wiring.

### Session-Connectivity Failure

- Applies when the hosted runtime cannot reach the durable session backend required for the selected hosted mode.
- Must include categories such as backend unconfigured, backend unreachable, or dependency client unavailable.
- Must include remediation guidance aimed at the provider-specific connectivity path.

## Required Evidence Fields

Each hosted dependency verification run must record:

- `revisionName`
- `serviceName`
- ordered `checkName` values
- `result` per check
- failure layer (`secret_access` or `session_connectivity`) when dependency checks fail
- operator-readable remediation for the first failed dependency check
- a statement that no secret values are included in the artifact

## Workflow Guarantees

- Operators must be able to prove that required secrets are accessible before treating the hosted deployment as ready.
- Operators must be able to prove that the durable session backend is reachable before treating hosted session continuity as reliable.
- Operators must be able to reproduce one healthy path, one secret-access failure path, and one session-connectivity failure path.
- Verification artifacts must remain free of secret values and bearer tokens.

## Failure Contract

- If an environment claiming durable hosted session support cannot pass the secret-access check, the rollout is not complete.
- If an environment claiming durable hosted session support cannot pass the session-connectivity check, the rollout is not complete.
- If the first failing dependency is not classified or does not include remediation guidance, the verification run is incomplete.
- If session continuation is reported as healthy without preceding dependency proof, the verification contract is violated.

## Verification Evidence

Successful use of this contract produces:

- A reviewable verification artifact for the hosted revision
- One clear proof that required runtime secrets are accessible
- One clear proof that the durable session backend is reachable
- One clear proof that a hosted session continuation flow succeeds when both dependency paths are healthy
- One clear operator-visible distinction between secret-access failures and session-connectivity failures
