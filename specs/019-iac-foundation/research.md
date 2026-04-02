# Research: Infrastructure as Code Foundation

## Decision 1: Use Terraform-compatible definitions for the first IaC foundation

- **Decision**: Define the hosted infrastructure foundation using Terraform-compatible configuration under `infrastructure/gcp`.
- **Rationale**: The repository already has dedicated `infrastructure/gcp` and `infrastructure/local` directories but no assets inside them, which makes a file-based declarative IaC tool the cleanest way to add reproducible infrastructure without disturbing the Python application layout. A Terraform-compatible approach fits the spec's requirement for versioned infrastructure definitions, clear operator inputs, and future provider-specific adapters.
- **Alternatives considered**:
  - Extend `scripts/deploy_cloud_run.sh` into an imperative infrastructure bootstrap script. Rejected because it would keep provisioning logic embedded in shell flows and weaken reviewability.
  - Use only manual cloud console documentation. Rejected because FND-019 explicitly exists to eliminate console-only setup.

## Decision 2: Keep application deployment separate from infrastructure provisioning

- **Decision**: Preserve `scripts/deploy_cloud_run.sh` as the application deployment path and make the new infrastructure layer produce the inputs that deployment path needs.
- **Rationale**: The repository already contains a validated deployment script, deployment metadata model, and verification workflow in [scripts/deploy_cloud_run.sh](~/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh) and [src/mcp_server/deploy.py](~/Projects/youtube-mcp-server/src/mcp_server/deploy.py). FND-019 needs reproducible infrastructure, not a wholesale replacement of the existing application rollout contract.
- **Alternatives considered**:
  - Move both provisioning and deployment into one IaC apply step. Rejected because it would blur the contract between platform provisioning and application rollout and make the existing deployment evidence harder to preserve.
  - Replace the Python deployment workflow entirely. Rejected because the current deploy and verification scripts already match earlier foundation slices and should remain stable consumers of infra outputs.

## Decision 3: Provision the durable hosted session dependency as a Redis-compatible managed backend

- **Decision**: Treat the durable session backend as a required hosted dependency in the GCP infrastructure plan and model its operator-facing output as a secret-backed connection endpoint.
- **Rationale**: Hosted session durability is already implemented in the runtime through a Redis-backed store, and configuration explicitly distinguishes `memory` from `redis` backends in [src/mcp_server/config.py](~/Projects/youtube-mcp-server/src/mcp_server/config.py) and [src/mcp_server/transport/session_store.py](~/Projects/youtube-mcp-server/src/mcp_server/transport/session_store.py). FND-019 therefore has to provision a Redis-compatible shared-state path rather than assuming it exists.
- **Alternatives considered**:
  - Use the shared in-memory `memory://` testing mode for hosted infrastructure. Rejected because it is useful for tests but does not satisfy durable multi-instance hosted behavior.
  - Leave the session backend as an external manual prerequisite. Rejected because the spec requires durable hosted dependencies to be reproducible from versioned infrastructure.

## Decision 4: Add a separate local hosted-like dependency path using Docker Compose

- **Decision**: Add a reproducible local hosted-like dependency workflow under `infrastructure/local` using Docker Compose to start a Redis-compatible service for durable-session verification.
- **Rationale**: The current repository supports a minimal local path with in-memory runtime defaults, but it does not yet provide a reproducible local dependency bootstrap for hosted-like session testing. Docker Compose is a simple, file-based way to add that path while keeping it separate from the minimal local run workflow required by the PRD.
- **Alternatives considered**:
  - Rely exclusively on `memory://` shared in-memory session state for local hosted-like verification. Rejected because it does not exercise the real durable-session backend contract.
  - Require developers to provision cloud infrastructure even for hosted-like local testing. Rejected because the PRD requires local execution to remain first-class.

## Decision 5: Define operator-facing contracts around inputs, outputs, and failure modes

- **Decision**: Document two explicit operator-facing contracts: one for GCP hosted foundation provisioning and one for local hosted-like dependency startup.
- **Rationale**: This feature changes operator workflows rather than MCP protocol payloads. The constitution still requires explicit contracts for external behavior changes, so the plan will treat provisioning inputs, deployment outputs, secret expectations, and failure modes as the external contract surface.
- **Alternatives considered**:
  - Rely only on README prose. Rejected because it would not give reviewers a stable contract artifact to validate.
  - Treat the feature as purely internal and skip contracts. Rejected because the provisioning and verification workflows are directly user-facing to operators and maintainers.
