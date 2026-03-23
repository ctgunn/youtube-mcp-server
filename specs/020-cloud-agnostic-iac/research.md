# Research: Cloud-Agnostic Infrastructure Module Strategy

## Implementation Targets

- The shared platform contract is the stable review surface for hosted runtime, network ingress, runtime identity, secret-backed configuration, observability integration, and durable session support.
- The current GCP path remains the first complete provider adapter and continues to hand deployment inputs to `scripts/deploy_cloud_run.sh`.
- The AWS path is the planning-grade secondary provider adapter used to prove portability.
- The execution modes remain `minimal_local`, `hosted_like_local`, and `hosted`.

## Decision 1: Define the infrastructure model around shared platform capabilities

- **Decision**: Organize FND-020 around a shared platform contract that names provider-neutral capabilities first: hosted runtime, networking and ingress, runtime identity, secret-backed configuration, observability integration, and durable session support.
- **Rationale**: The existing FND-019 foundation already contains all of these concepts, but they currently appear inside GCP-specific Terraform files and README guidance. Naming the shared capabilities first creates a stable contract that can outlive any one provider adapter.
- **Alternatives considered**:
  - Keep the design GCP-first and add provider notes later. Rejected because that would preserve the current portability gap and make future provider work start from provider-specific assumptions.
  - Define portability only at the deployment-script layer. Rejected because the infrastructure contract must include runtime, secrets, networking, observability, and durable session requirements, not just deployment inputs.

## Decision 2: Preserve the current GCP foundation as the first complete provider adapter

- **Decision**: Treat `infrastructure/gcp` as the first complete provider adapter rather than replacing it or pretending it is already portable.
- **Rationale**: The repository already has a functioning GCP foundation contract, Terraform variables and outputs, and integration tests that feed `scripts/deploy_cloud_run.sh`. Recasting that work as a provider adapter keeps the current path intact while making its provider-specific assumptions explicit.
- **Alternatives considered**:
  - Rewrite the GCP foundation immediately into a deeper multi-provider module tree. Rejected because FND-020 is a strategy and design slice, not a full infrastructure rewrite.
  - Replace the current GCP deploy handoff with a new provider-neutral deployment engine. Rejected because the existing deployment script is already a validated consumer of GCP outputs and should remain stable until a real multi-provider implementation requires change.

## Decision 3: Use AWS as the planning-grade secondary provider path

- **Decision**: Use `aws` as the secondary provider path for planning and contract purposes.
- **Rationale**: A second provider path needs to prove that the platform model is not locked to Cloud Run, Secret Manager, and Memorystore semantics. AWS is a meaningful contrast because it can satisfy the same capability categories through a different provider surface while still fitting the project's managed container-runtime, secret-backed configuration, observability, and Redis-compatible session requirements.
- **Alternatives considered**:
  - Leave the secondary provider unspecified. Rejected because the feature acceptance criteria require at least one secondary path strong enough to prove portability.
  - Use a generic `secondary` placeholder with no provider identity. Rejected because it would be too abstract to test whether the shared contract is concrete enough.

## Decision 4: Keep the application deployment model separate from provider provisioning

- **Decision**: Preserve one application deployment model and keep it separate from provider provisioning responsibilities.
- **Rationale**: The current platform already separates infrastructure provisioning from the application deployment script and hosted verification flow. That separation is a portability asset: providers should supply the inputs and guarantees the application deployment model expects, not redefine the deployment model itself.
- **Alternatives considered**:
  - Collapse provisioning and deployment into provider-specific full-stack workflows. Rejected because that would make each provider a separate platform design and violate the feature goal.
  - Make local execution consume cloud-provider modules. Rejected because the PRD and FND-019 require local execution to remain first-class and independent of cloud provisioning.

## Decision 5: Treat execution modes as part of the shared contract, not side documentation

- **Decision**: Model `minimal_local`, `hosted_like_local`, and `hosted` as explicit execution modes that all relate to the same shared platform contract.
- **Rationale**: The repository already distinguishes minimal local and hosted-like local paths in `README.md` and `infrastructure/local/README.md`. FND-020 needs to connect those paths to the hosted provider model so portability work does not accidentally make local development depend on provider modules.
- **Alternatives considered**:
  - Keep local and hosted workflows documented separately with no shared vocabulary. Rejected because that would leave portability ambiguous and make local-first guarantees easy to erode.
  - Treat hosted-like local verification as part of a provider adapter. Rejected because it is an execution mode used for verification, not a cloud provider.

## Decision 6: Extend the existing contract-test style for portability work

- **Decision**: Continue using markdown contract documents plus `pytest` contract and integration tests as the main planning-to-implementation bridge for FND-020.
- **Rationale**: Existing features already lock infrastructure and operational expectations through markdown contracts in `specs/*/contracts/` and tests under `tests/contract/` and `tests/integration/`. Reusing that pattern keeps this feature aligned with the constitution and the repository's current workflow.
- **Alternatives considered**:
  - Use diagrams or prose only. Rejected because the repository already relies on contract docs as reviewable artifacts with testable expectations.
  - Introduce a new planning-only schema format. Rejected because it adds complexity without a clear need in this slice.

## Provider Expansion Guidance

- New provider work must begin by mapping the provider to the shared platform contract rather than by redefining the application deployment workflow.
- Partial or unsupported capability mappings must be documented before a provider path is described as production-ready.
- Local execution and hosted-like local verification must remain unaffected by provider-specific implementation choices.
