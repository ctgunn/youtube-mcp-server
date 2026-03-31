# Research: Automated Hosted Deployment Orchestration

## Implementation Targets

- One checked-in workflow definition must orchestrate the existing Terraform, deployment, and hosted verification path instead of replacing any part of it.
- Terraform outputs remain the handoff between infrastructure reconciliation and application rollout.
- Hosted verification remains a required release gate after rollout.
- Bootstrap prerequisites and secret responsibilities must stay explicit and reviewable.

## Decision 1: Reuse the existing deploy script and deployment helper as the canonical rollout path

- **Decision**: Treat `scripts/deploy_cloud_run.sh` plus `src/mcp_server/deploy.py` as the canonical hosted deployment path that automation must call.
- **Rationale**: The repository already validates deployment inputs, merges Terraform outputs, builds the deployment command, emits a structured deployment record, and classifies failures as `input_validation`, `deployment_execution`, or `metadata_capture`. Reusing this path preserves tested behavior and keeps rollout logic reviewable in one place.
- **Alternatives considered**:
  - Call the platform deployment command directly from the workflow. Rejected because it would bypass repository validation, deployment-record generation, and existing failure semantics.
  - Add a second deployment entrypoint for automation only. Rejected because it would duplicate rollout logic and increase drift risk.

## Decision 2: Reuse the existing hosted verification CLI as the post-rollout release gate

- **Decision**: Treat `scripts/verify_cloud_run_foundation.py` and the underlying hosted verification flow in `src/mcp_server/deploy.py` as the required post-deploy verification path.
- **Rationale**: The repository already has a session-aware hosted verification flow that checks reachability, readiness, secret access, session continuity, initialize correctness, and MCP behavior. FND-025 needs to elevate that path into automated release gating, not replace it with narrower health checks.
- **Alternatives considered**:
  - Use ad hoc HTTP probes or only `/health` and `/ready`. Rejected because they do not prove the hosted MCP contract.
  - Mark deployment success before verification runs. Rejected because the feature requires verification to gate rollout success.

## Decision 3: Reconcile infrastructure first and pass Terraform outputs into the deploy script

- **Decision**: Keep the deployment chain ordered as Terraform reconcile -> Terraform output export -> deploy script -> hosted verification.
- **Rationale**: Earlier infrastructure features already document that Terraform provisions the platform foundation and exports deployment-ready values, while the deploy script owns application rollout using those outputs plus the image reference. This preserves the intended infrastructure/application boundary.
- **Alternatives considered**:
  - Embed deploy-time values directly in workflow configuration. Rejected because it weakens the repository's reviewed handoff contract.
  - Make Terraform own image rollout. Rejected because the repository intentionally separates infrastructure reconciliation from application deployment.

## Decision 4: Keep secret resource wiring automated, but keep secret values operator-managed

- **Decision**: Automation may provision secret references, runtime identity wiring, and deploy-time secret configuration, but secret contents remain outside push-triggered automation and under operator control.
- **Rationale**: Existing documentation and hosted dependency contracts already separate secret references from secret contents. Preserving that boundary avoids leaking secret material into workflow configuration and keeps least-privilege review intact.
- **Alternatives considered**:
  - Fully automate secret value creation or rotation. Rejected because it blurs ownership and expands the security surface.
  - Treat missing secret values as a manual concern outside workflow outcomes. Rejected because the feature requires clear failure reporting before rollout can be considered successful.

## Decision 5: Surface bootstrap and failure conditions as explicit workflow gates

- **Decision**: The workflow must fail clearly for missing bootstrap prerequisites, invalid deployment inputs, failed infrastructure reconciliation, failed application rollout, failed metadata capture, and failed hosted verification.
- **Rationale**: Operators need stage-specific failure outcomes to distinguish configuration gaps from cloud runtime issues and hosted MCP contract failures. The existing deployment and verification helpers already provide stage-aware signals that the workflow should preserve.
- **Alternatives considered**:
  - Collapse all failure causes into one generic deployment failure. Rejected because it would erase remediation guidance already present in the repository.
  - Allow best-effort success when deployment completes but verification fails. Rejected because it violates the feature acceptance criteria.

## Decision 6: Introduce one checked-in push-triggered workflow under the repository automation surface

- **Decision**: Add one checked-in repository workflow definition for the intended deployment branch and treat it as the authoritative automation surface for hosted rollout.
- **Rationale**: FND-025 requires deployment automation to live in version control and evolve alongside application and infrastructure changes. The workflow definition becomes the reviewable orchestration layer above the existing Terraform, deploy, and verify entrypoints.
- **Alternatives considered**:
  - Keep deployment automation external to the repository. Rejected because it would not satisfy the checked-in automation requirement.
  - Trigger hosted deployment from every branch. Rejected because the spec bounds the feature to one intended deployment branch.
