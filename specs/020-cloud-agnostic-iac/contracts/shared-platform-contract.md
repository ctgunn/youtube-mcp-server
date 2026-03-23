# Contract: Shared Platform Contract

## Purpose

Define the provider-neutral infrastructure contract for hosting the MCP service so maintainers can reason about portability without changing the application deployment model.

## Actors

- Operator provisioning hosted infrastructure
- Maintainer adapting provider-specific infrastructure modules
- Developer using local or hosted-like execution paths
- Reviewer validating portability and provider boundaries

## Required Shared Capabilities

Every supported hosted provider path must map to these capabilities:

- Hosted runtime capable of running the MCP service
- Network ingress and service endpoint exposure for hosted MCP traffic
- Runtime identity used by the hosted service
- Secret-backed runtime configuration for protected values
- Observability integration sufficient for deployment and runtime diagnosis
- Durable shared session support for hosted MCP session continuity

## Shared Inputs

The shared contract must define provider-neutral inputs for:

- Environment profile
- Service name
- Region or deployment locality
- Hosted scaling settings
- Authentication and allowed-origin policy inputs
- Session durability settings
- Secret reference declarations

Provider adapters may introduce extra provider-specific inputs, but they must not replace these shared inputs.

## Shared Outputs

Every production-capable provider adapter must produce or document how to obtain:

- Service identifier for deployment and verification
- Hosted endpoint reference
- Runtime identity reference
- Secret reference names or bindings
- Durable session connection reference or equivalent secret-backed handoff
- Scaling and timeout settings actually applied
- Operator-visible evidence needed for deployment and hosted verification

## Workflow Guarantees

- All provider adapters must preserve one consistent application deployment model.
- Local execution must remain available without provisioning any provider adapter.
- Hosted-like local verification must remain available as a separate path when durable shared-state behavior needs to be exercised outside cloud deployment.
- Provider-specific enhancements must remain clearly separate from mandatory shared capabilities.

## Failure Contract

- If a provider cannot satisfy a required shared capability, the adapter must mark that capability as partial or unsupported before being treated as production-ready.
- If a provider-specific module requires different application deployment semantics, it is outside this contract and must not be presented as a compliant adapter.
- If local execution would require cloud-provider prerequisites, the design is non-compliant with the shared contract.

## Verification Evidence

Successful use of this contract produces:

- A shared capability inventory that reviewers can trace across provider adapters
- A provider-specific mapping for each required capability
- Documentation showing how local, hosted-like local, and hosted deployment modes relate to the same shared model
