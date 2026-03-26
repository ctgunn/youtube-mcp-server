# Contract: Runtime Secret Access

## Purpose

Define the operator-facing and provider-adapter contract for how the hosted runtime identity reads required secret-backed configuration in a deployed environment.

## Actors

- Operator provisioning and deploying a hosted environment
- Maintainer reviewing runtime secret-access wiring before rollout
- Hosted runtime consuming required secret-backed configuration

## Workflow Scope

- This contract applies to hosted environments that rely on secret-backed runtime configuration.
- It covers runtime identity, secret-access bindings, and post-deploy verification.
- It does not define secret values or expose them in documentation or evidence artifacts.

## Required Inputs

The runtime secret-access workflow must define or document:

- Hosted environment
- Hosted service name
- Runtime identity reference
- Required secret names for that environment
- reviewable secret-access bindings for the runtime identity
- Runtime secret reference path used by the deployed service
- Verification step proving the runtime can access required secrets after deployment

## Workflow Guarantees

- Every hosted environment must identify which runtime identity reads required secrets.
- Required secrets must be wired through a reviewable provider-specific path rather than undocumented manual configuration alone.
- The access scope must be limited to the secret reads required for the hosted service to operate.
- Hosted readiness and verification must distinguish secret-access failures from session-connectivity failures.
- Secret values must never appear in deployment evidence, readiness payloads, logs, or verification artifacts.

## Failure Contract

- If the runtime identity lacks required secret permissions, the hosted deployment must fail readiness or verification with a secret-access diagnosis.
- If a required secret reference is missing or invalid, the hosted deployment must fail readiness or verification with a secret-access diagnosis.
- If review artifacts do not show which runtime identity accesses which required secrets, the contract is violated.
- If verification cannot prove the runtime can access required secrets after deployment, the hosted rollout is incomplete.

## Verification Evidence

Successful use of this contract produces:

- Reviewable evidence of the runtime identity used by the hosted service
- Reviewable evidence of the required secret names and secret-access bindings
- Hosted readiness or verification evidence proving secret access succeeds without exposing secret values
- Operator-facing remediation guidance for failed secret-access checks
