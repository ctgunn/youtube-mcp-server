# Research: Terraform-Managed Hosted Networking for Durable Sessions

## Implementation Targets

- Terraform owns the supported GCP durable-session network layer instead of treating network resources as external operator-supplied prerequisites.
- Terraform outputs remain the canonical handoff into deployment and hosted verification rather than introducing a second rollout path.
- Hosted deployment evidence must make the managed network path reviewable without turning every network artifact into runtime configuration.
- Minimal local and hosted-like local workflows remain separate from provider-specific hosted GCP networking.

## Decision 1: Treat hosted networking as a managed provider-adapter resource set

- **Decision**: Model the supported GCP durable-session network layer as a Terraform-managed provider-adapter resource set that includes the hosted network path required by Cloud Run and the durable Redis-backed session backend.
- **Rationale**: The current GCP adapter provisions Redis but still expects operator-supplied network references for the authorized network and Cloud Run connector path. FND-027 closes that reproducibility gap by making the hosted network path reviewable and provisioned from versioned infrastructure definitions.
- **Alternatives considered**:
  - Keep VPC, subnet, and connector references as external `.tfvars` inputs. Rejected because that preserves the undocumented manual prerequisite boundary that FND-027 is supposed to remove.
  - Treat the Redis session backend alone as sufficient infrastructure coverage. Rejected because durable sessions still depend on the runtime connectivity path, not just backend existence.

## Decision 2: Preserve the existing Terraform-to-deploy-to-verify chain

- **Decision**: Extend the current `terraform apply -> terraform output -> scripts/deploy_cloud_run.sh -> hosted verification` workflow instead of creating a separate networking bootstrap or verification path.
- **Rationale**: FND-025 already established the checked-in deployment chain, and the current deploy helpers already consume Terraform outputs from `INFRA_OUTPUTS_FILE`. Reusing that path keeps rollout logic reviewable in one place and avoids an additional operator-only networking workflow.
- **Alternatives considered**:
  - Add a separate networking-only bootstrap script outside the existing deployment chain. Rejected because it would duplicate the infrastructure handoff surface and make rollout review less coherent.
  - Make hosted verification inspect Terraform state directly. Rejected because the repository already uses deployment records and exported outputs as the reviewable evidence surface.

## Decision 3: Expand outputs and deployment evidence for networking, not runtime behavior

- **Decision**: Add explicit networking outputs and deployment evidence fields that prove the managed network layer exists, while keeping runtime env configuration limited to what the application actually needs.
- **Rationale**: Current deployment evidence preserves the session connectivity model and store URL, but not the underlying network resources that prove the path is Terraform-managed. FND-027 needs first-class reviewable evidence for the network layer without bloating runtime config or changing session semantics.
- **Alternatives considered**:
  - Continue exposing only `sessionConnectivityModel` plus the Redis URL. Rejected because that shows declared intent but not that the required network layer was provisioned.
  - Pass every Terraform network artifact into the application runtime as env vars. Rejected because most of that information is evidence for deployment review and verification, not runtime behavior.

## Decision 4: Keep FND-027 inside the GCP provider-adapter boundary

- **Decision**: Treat FND-027 as a GCP-specific infrastructure enhancement under `infrastructure/gcp/` rather than a redesign of the shared platform contract or the local execution model.
- **Rationale**: FND-020 already established the provider-adapter boundary, and FND-022 already defined the provider-specific connectivity expectations. The missing work is concrete GCP network provisioning, not a new abstraction layer.
- **Alternatives considered**:
  - Re-open the shared cross-provider infrastructure strategy. Rejected because the current gap is implementation of the GCP adapter, not the shared capability model.
  - Expand the feature to cover additional providers. Rejected because the spec explicitly bounds the work to the supported GCP path.

## Decision 5: Preserve local-first development as a separate contract boundary

- **Decision**: Keep `minimal_local` and `hosted_like_local` workflows out of the hosted GCP networking requirement and document them as separate execution paths.
- **Rationale**: The constitution and prior infrastructure features require local execution to remain first-class. Cloud provider network provisioning should remain a hosted-only concern and must not leak into the local developer workflow or its documentation.
- **Alternatives considered**:
  - Use hosted GCP networking requirements as the default development path. Rejected because it would violate the local-first guarantee and add unnecessary operator friction.
  - Treat hosted-like local Redis usage as proof of hosted network correctness. Rejected because it validates application behavior, not the provider-specific Cloud Run network path.

## Decision 6: Separate three contract surfaces for reviewability

- **Decision**: Define three explicit contract artifacts for FND-027: one for managed hosted-network provisioning, one for networking output handoff into deployment/verification, and one for removal of manual networking prerequisites from the supported GCP runbook.
- **Rationale**: The feature changes three distinct review surfaces: which network resources Terraform owns, how those resources are exposed to downstream rollout evidence, and what operators are still expected to provide manually. Keeping them separate makes planning, testing, and review more precise.
- **Alternatives considered**:
  - Use a single combined networking contract. Rejected because it would blur infrastructure ownership, rollout evidence, and operator workflow boundaries.
  - Extend only the existing runtime session-connectivity contract from FND-022. Rejected because that contract does not fully describe Terraform ownership or the manual-prerequisite boundary.
