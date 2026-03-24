# Contract: AWS Provider Adapter

## Purpose

Define the planning-grade secondary provider adapter used to prove the shared platform contract is not locked to the current GCP implementation.

## Actors

- Maintainer evaluating a secondary hosted provider path
- Reviewer checking whether the shared platform contract is concrete enough
- Operator comparing hosted deployment expectations across providers

## Adapter Scope

- This adapter is planning-grade for FND-020 rather than production-ready.
- It must show how AWS would satisfy the shared platform contract without introducing a separate application deployment model.
- It must identify gaps, assumptions, and unsupported areas explicitly.

## Required Capability Mapping

The adapter must describe how AWS would provide:

- A managed hosted runtime for the MCP service container through AWS App Runner or an equivalent managed container runtime
- Hosted ingress and service endpoint behavior
- Runtime identity and permission assignment for the service
- Secret-backed configuration injection for protected runtime values through AWS Secrets Manager or an equivalent secret-binding path
- Observability integration for logs and deployment/runtime diagnosis
- Redis-compatible durable session support for hosted session continuity through Amazon ElastiCache for Redis or an equivalent managed Redis-compatible service

## Provider-Specific Inputs

The adapter may define provider-specific inputs such as:

- Account or environment identifiers
- Regional deployment target
- Runtime-networking preferences
- Provider-specific identity references
- Provider-specific session-store configuration

These inputs must be documented as adapter details, not as changes to the shared application deployment model.

## Required Outputs

The adapter must describe how AWS would hand off:

- Hosted service endpoint reference
- Runtime identity reference
- Secret binding references
- Durable session connection reference or equivalent
- Scaling and timeout settings exposed to operators
- Verification evidence comparable to the primary provider path

## Failure Contract

- If AWS cannot satisfy a required shared capability with the current design, the adapter must mark that capability as partial or unsupported.
- If the AWS path would require application-specific deployment semantics that differ from the shared model, the adapter must document that as a portability violation.
- If the adapter cannot explain how local and hosted-like local workflows remain unaffected, it is incomplete.

## Verification Evidence

Successful use of this contract produces:

- A documented capability-by-capability mapping from the shared platform contract into the AWS adapter
- A clear list of assumptions, gaps, and deferred production-hardening items
- Evidence that the shared contract remains understandable outside the GCP-specific implementation
