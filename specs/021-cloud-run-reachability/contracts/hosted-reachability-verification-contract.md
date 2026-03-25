# Contract: Hosted Reachability Verification

## Purpose

Define the operator-facing verification contract that proves public Cloud Run reachability and distinguishes cloud-level denial from MCP-layer authentication denial.

## Actors

- Operator running hosted verification after deployment
- Reviewer validating rollout evidence
- Maintainer diagnosing failed remote MCP onboarding

## Verification Order

The hosted verification flow for a public remote MCP environment must run in this order:

1. `reachability`
   - Target: public hosted connection point
   - Expected result: service is reachable at the platform layer
2. `liveness`
   - Target: hosted `/health`
   - Expected result: healthy hosted response
3. `readiness`
   - Target: hosted `/ready`
   - Expected result: ready hosted response when configuration is valid
4. `mcp-authenticated`
   - Target: protected hosted `/mcp`
   - Expected result: authenticated MCP request succeeds
5. `mcp-denied`
   - Target: protected hosted `/mcp` without valid credentials
   - Expected result: MCP-layer denial that proves application authentication remains in force

If `reachability`, `liveness`, or `readiness` fails, authenticated MCP success must not be reported for that environment.

## Denial Interpretation

### Cloud-Level Denial

- Applies when the hosted service is not publicly reachable as intended.
- Occurs before the request reaches MCP handling.
- Must be reported as a platform-access or public-access failure.
- Must include remediation guidance aimed at public invocation or connection-point configuration.

### MCP-Layer Denial

- Applies only after the request reaches the hosted application.
- Reuses the existing hosted security categories such as `unauthenticated`, `invalid_credential`, `origin_denied`, and `malformed_security_input`.
- Must include remediation guidance aimed at bearer-token or origin policy configuration.

## Required Evidence Fields

Each hosted verification run must record:

- `revisionName`
- `endpointUrl` or equivalent connection point
- ordered `checkName` values
- `result` per check
- whether the request reached the application layer for failed access checks
- failure layer (`cloud_platform` or `mcp_application`) when access is denied
- operator-readable remediation for the first failed check

## Workflow Guarantees

- Operators must be able to prove public reachability separately from authenticated MCP success.
- Operators must be able to reproduce one successful authenticated path and one denial path caused by missing or invalid MCP credentials.
- Verification evidence must make it clear whether a failed request stopped at the platform layer or at the MCP application layer.
- Verification artifacts must not include bearer tokens or secret values.

## Failure Contract

- If an environment intended for public remote MCP access cannot pass the `reachability` check, the rollout is not complete.
- If an authenticated MCP request fails after reachability succeeds, the failure must be attributed to the MCP application layer rather than to platform reachability.
- If evidence does not record the failure layer and remediation guidance, the verification run is incomplete.

## Verification Evidence

Successful use of this contract produces:

- A reviewable verification artifact for the hosted revision
- One clear proof that the service is publicly reachable as intended
- One clear proof that `/mcp` remains protected by bearer-token authentication
- One clear operator-visible distinction between cloud-level denial and MCP-layer denial
