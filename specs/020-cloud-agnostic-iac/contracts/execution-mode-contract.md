# Contract: Execution Modes

## Purpose

Define how local execution, hosted-like local verification, and hosted deployment relate to the same shared platform contract without forcing cloud-provider prerequisites into the default developer workflow.

## Actors

- Developer using the minimum local runtime
- Developer or operator running hosted-like local verification
- Operator preparing hosted deployment on a provider adapter

## Modes

The canonical execution modes in this feature are `minimal_local`, `hosted_like_local`, and `hosted`.

### Minimal Local Runtime

- Uses the application with local configuration only
- Requires no cloud-provider module
- Uses process-local session behavior unless the user intentionally selects a different mode
- Must remain the lightest-weight supported execution path

### Hosted-Like Local Verification

- Starts local shared-state dependencies when durable-session behavior must be exercised
- Uses repository-defined local assets rather than cloud provisioning
- Reuses the shared platform vocabulary for runtime, session, and verification expectations
- Remains distinct from cloud-hosted deployment

### Hosted Deployment

- Consumes one provider adapter that maps to the shared platform contract
- Produces deployment and verification evidence visible to operators
- Must preserve the same application deployment model regardless of provider

## Workflow Guarantees

- Choosing minimal local execution must not require provider provisioning or provider-specific configuration.
- Choosing hosted-like local verification must document the extra dependency steps and expected evidence clearly.
- Choosing hosted deployment must identify which provider adapter is responsible for satisfying each shared capability.

## Failure Contract

- If the minimal local mode requires cloud-provider inputs, the execution-mode contract is violated.
- If the hosted-like local mode becomes indistinguishable from hosted cloud deployment, the contract is violated.
- If hosted deployment cannot be traced back to the shared platform contract, the provider adapter is non-compliant.

## Verification Evidence

Successful use of this contract produces:

- One documented minimum local run path
- One documented hosted-like local verification path
- One documented provider-backed hosted path that maps to the shared platform contract
