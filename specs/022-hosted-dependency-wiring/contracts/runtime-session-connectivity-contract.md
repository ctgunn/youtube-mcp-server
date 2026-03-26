# Contract: Runtime Session Connectivity

## Purpose

Define the operator-facing and provider-adapter contract for how the hosted runtime reaches the durable session backend required for hosted session continuity.

## Actors

- Operator provisioning hosted session connectivity
- Maintainer reviewing the provider-specific connectivity model
- Hosted runtime using the durable session backend for session continuity

## Workflow Scope

- This contract applies to hosted environments that claim durable hosted session support.
- It covers the provider-specific connectivity path between the hosted runtime and the durable session backend.
- It does not redefine the session protocol itself; it preserves the session behavior established by earlier MCP transport work.

## Required Inputs

The session-connectivity workflow must define or document:

- Hosted environment
- Hosted service name
- Durable session backend type
- Session backend connection reference
- Provider-specific connectivity model or network path
- Whether durable session health is required for readiness
- Verification step proving the hosted runtime can reach the session backend

## Workflow Guarantees

- Hosted environments claiming durable session support must define a reviewable connectivity path to the durable session backend.
- The connectivity model must be documented clearly enough for operators to understand prerequisites and remediation paths.
- Hosted readiness and verification must distinguish session-connectivity failures from secret-access failures.
- Hosted verification for a compliant environment must prove both backend reachability and at least one hosted session continuation flow.
- Environments that do not support durable hosted sessions must not be described as fully compliant with durable session requirements.

## Failure Contract

- If the hosted runtime cannot reach the durable session backend, readiness or hosted verification must fail with a session-connectivity diagnosis.
- If the provider-specific connectivity model is not documented or reviewable, the contract is violated.
- If an environment claims durable sessions but does not prove connectivity and continuation behavior, the rollout is incomplete.
- If session-connectivity failures are reported as generic configuration or secret failures, the contract is violated.

## Verification Evidence

Successful use of this contract produces:

- Reviewable evidence of the durable session backend type and connection reference
- Operator-facing documentation of the provider-specific connectivity model
- Hosted readiness or verification evidence proving the backend is reachable
- Hosted verification evidence proving at least one durable session continuation flow succeeds in the intended hosted mode
