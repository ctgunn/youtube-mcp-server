# Research: Automated Hosted Network Bootstrap Reconciliation

## Implementation Targets

- Preserve the current repository-managed Terraform-to-deploy-to-verify chain instead of creating a separate network bootstrap path.
- Make managed hosted networking an explicit part of the automatic hosted rollout contract, not an implied side effect of generic infrastructure reconciliation.
- Keep the primary automatic pipeline and the manual fallback aligned on stage order, bootstrap boundary, and failure reporting.
- Clarify which one-time bootstrap inputs remain external after the hosted network layer itself became Terraform-managed.

## Decision 1: Treat Cloud Build as the primary automatic deployment path and GitHub Actions as a manual fallback

- **Decision**: Keep `cloudbuild.yaml` as the primary push-triggered hosted deployment pipeline and `.github/workflows/hosted-deploy.yml` as a manual fallback that preserves the same repository-managed rollout chain.
- **Rationale**: The current repository already treats Cloud Build as the automatic deployment surface and GitHub Actions as an operator-invoked fallback. FND-028 needs to refine the semantics of that existing chain, not redefine workflow ownership.
- **Alternatives considered**:
  - Promote the GitHub Actions workflow to a second automatic deployment path. Rejected because it would create duplicate push-triggered behavior and blur the primary rollout contract.
  - Design FND-028 around only one workflow file. Rejected because the repository already documents and tests both automation surfaces as part of the supported operator story.

## Decision 2: Keep managed network bootstrap inside the existing `infrastructure_reconcile` stage

- **Decision**: Define network bootstrap as an explicit required responsibility of the existing `infrastructure_reconcile` stage rather than adding a separate new workflow stage.
- **Rationale**: The current deployment model already runs Terraform apply before deploy in both automation surfaces, and the managed network layer is already provisioned under `infrastructure/gcp/`. FND-028 needs sharper stage semantics and reviewability, not a new stage that duplicates current behavior.
- **Alternatives considered**:
  - Add a distinct `network_bootstrap` workflow stage before `infrastructure_reconcile`. Rejected because the network layer is already part of Terraform-managed infrastructure reconciliation and would split one coherent Terraform step into two conceptual stages without implementation benefit.
  - Leave network ownership implicit inside generic infrastructure reconciliation. Rejected because operators need a clear contract that managed networking is a required part of the hosted rollout path.

## Decision 3: Preserve Terraform outputs as the canonical handoff into deployment

- **Decision**: Continue using Terraform outputs as the canonical infrastructure handoff into `scripts/deploy_cloud_run.sh` and hosted verification rather than introducing a bootstrap-specific handoff artifact.
- **Rationale**: The repository already exports managed network references, and `src/mcp_server/deploy.py` already maps those outputs into deploy inputs and deployment evidence. FND-028 is about pipeline semantics and failure boundaries, not about replacing a working handoff contract.
- **Alternatives considered**:
  - Add a second bootstrap-only JSON artifact for network reconcile evidence. Rejected because it would duplicate information already exported through Terraform outputs and deployment records.
  - Push all network-bootstrap evidence into deployment-only runtime configuration. Rejected because the existing output and deployment-record surfaces are already sufficient and more reviewable.

## Decision 4: Narrow the remaining external bootstrap boundary to non-network prerequisites

- **Decision**: Document the remaining one-time bootstrap inputs as repository/cloud access prerequisites, environment-specific Terraform variable files, and operator-managed secret values, while explicitly excluding recurring manual hosted-network provisioning from that boundary.
- **Rationale**: FND-027 already moved the supported hosted network layer into Terraform-managed infrastructure. The remaining gap is operator clarity that the external prerequisites are no longer about creating VPC, subnet, or connector resources by hand.
- **Alternatives considered**:
  - Keep describing network resource names and CIDRs as recurring manual operator tasks. Rejected because those are environment inputs to Terraform, not a separate manual provisioning workflow.
  - Claim that no bootstrap inputs remain outside automation. Rejected because workload identity, environment-specific variables, and secret values still require one-time setup outside recurring deployment runs.

## Decision 5: Use a four-part failure taxonomy across the hosted deployment path

- **Decision**: Model operator-visible failure boundaries as `bootstrap_input_failure`, `network_reconcile_failure`, `deployment_failure`, and `hosted_verification_failure`.
- **Rationale**: The repository already distinguishes deploy and verification failures reasonably well, but bootstrap inputs and managed network reconciliation remain too easy to collapse into one generic infrastructure failure. A four-part taxonomy makes the feature acceptance criteria concrete without redesigning the current stage model.
- **Alternatives considered**:
  - Reuse only the current stage names without a finer failure taxonomy. Rejected because operators still need to distinguish failures before reconciliation starts from failures during managed network reconcile.
  - Add many detailed cloud-specific failure subtypes. Rejected because the feature needs a simple operator-facing boundary, not an exhaustive implementation taxonomy.

## Decision 6: Split FND-028 contracts by review surface

- **Decision**: Define three contracts for FND-028: one for the hosted network-bootstrap pipeline behavior, one for failure-boundary expectations, and one for remaining bootstrap prerequisites.
- **Rationale**: The feature spans three distinct review concerns: ordered workflow behavior, stage-specific failure interpretation, and external prerequisite ownership. This matches the repository’s planning pattern from FND-025 and FND-027.
- **Alternatives considered**:
  - Write a single combined FND-028 contract. Rejected because it would blur stage ordering, failure semantics, and bootstrap ownership into one harder-to-review artifact.
  - Extend only the FND-025 deployment pipeline contract. Rejected because FND-028 adds a narrower, feature-scoped emphasis on managed network bootstrap semantics and failure boundaries.
