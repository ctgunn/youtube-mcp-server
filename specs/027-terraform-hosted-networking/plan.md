# Implementation Plan: Terraform-Managed Hosted Networking for Durable Sessions

**Branch**: `027-terraform-hosted-networking` | **Date**: 2026-03-30 | **Spec**: [spec.md](~/Projects/youtube-mcp-server/specs/027-terraform-hosted-networking/spec.md)
**Input**: Feature specification from `/specs/027-terraform-hosted-networking/spec.md`

## Summary

Promote the supported GCP durable-session network layer from a manual prerequisite into a first-class Terraform-managed provider artifact. The implementation will extend the existing `infrastructure/gcp` adapter so it provisions the VPC, subnet, and Cloud Run connectivity path required for Redis-backed hosted sessions, exports those resources through the existing Terraform-output handoff, and updates deployment evidence and operator guidance without creating a second deployment path or changing MCP session semantics.

Canonical terms for this feature are `hosted network layer`, `managed network resource set`, `cloud run connectivity path`, `networking output set`, and `manual prerequisite boundary`.

## Technical Context

**Language/Version**: Python 3.11 for service, deployment, and verification tooling; Terraform-compatible IaC definitions for the GCP provider adapter  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis client, Terraform-compatible assets under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, and hosted verification tooling  
**Storage**: In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted sessions; file-based Terraform definitions, deployment records, verification evidence, and specification artifacts  
**Testing**: `pytest` for unit, contract, and integration coverage; `ruff check .`; hosted verification through the existing deployment-record-driven verification flow  
**Target Platform**: Local developer workflows plus the supported GCP-hosted Cloud Run deployment path for durable Redis-backed sessions  
**Project Type**: Python web service with provider-specific infrastructure automation, deployment handoff tooling, and hosted verification artifacts  
**Performance Goals**: Preserve the current hosted deploy-to-verify flow while ensuring the durable-session network layer is reproducible from Terraform in one supported GCP provisioning pass and remains reviewable through outputs and documentation  
**Constraints**: Reuse the existing Terraform-output handoff into `scripts/deploy_cloud_run.sh`; do not create a parallel deployment path; keep secret values and bearer tokens out of plans, outputs, logs, and evidence; preserve local-first development; maintain existing MCP authentication and hosted session behavior; treat missing managed networking as a deployment-blocking condition for durable-session environments  
**Scale/Scope**: One primary GCP provider adapter, one durable Redis-backed session model, one managed hosted network layer per environment, one deployment-output handoff into the existing rollout path, and one operator runbook that removes manual network prerequisites from the supported GCP flow

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Pre-design gate result: PASS. The feature changes provider-adapter provisioning, deployment evidence, and operator-facing infrastructure workflow boundaries rather than MCP payload schemas. Required full-suite proof command: `pytest`.

## Project Structure

### Documentation (this feature)

```text
specs/027-terraform-hosted-networking/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── hosted-networking-provisioning-contract.md
│   ├── hosted-networking-output-handoff-contract.md
│   └── hosted-networking-prerequisite-boundary-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
infrastructure/
├── gcp/
└── local/

scripts/
├── deploy_cloud_run.sh
└── verify_cloud_run_foundation.py

src/
└── mcp_server/
    ├── deploy.py
    ├── infrastructure_contract.py
    └── transport/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service, the `infrastructure/gcp` provider adapter, the current deploy script, and the existing hosted verification path. FND-027 extends the GCP adapter and its documented output handoff instead of introducing a new infrastructure module family or a second rollout workflow.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current gap explicitly by showing that the GCP adapter provisions Redis but still relies on operator-supplied network references for the authorized network and Cloud Run connector path.
- **Green**: Resolve the planning decisions for managed GCP network ownership, deployment-output handoff, verification evidence boundaries, and local-versus-hosted workflow separation in `research.md`.
- **Refactor**: Remove ambiguity between Terraform-managed networking, deployment evidence, and operator prerequisites so later implementation work stays inside one provider-adapter and deploy-script chain.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for managed hosted network coverage, deployment-output evidence, and the removal of manual networking prerequisites from the supported GCP runbook.
- **Green**: Produce `data-model.md`, contract documents in `/contracts/`, and `quickstart.md` that define the managed network resource set, the output handoff into deployment and verification, and the runbook boundary between local development and hosted GCP networking.
- **Refactor**: Normalize networking terminology, handoff artifact names, and failure/remediation wording across the design artifacts, then rerun the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing Terraform-managed network resources, missing IaC output coverage for network evidence, missing deployment-record/network handoff evidence, and stale documentation that still requires manual VPC, subnet, or connector setup.
- **Green**: Organize implementation around the minimum path that makes those tests pass: add Terraform-managed network resources, wire them into the existing Redis and Cloud Run path, extend infrastructure outputs and deploy evidence, and update the GCP runbook plus verification expectations.
- **Refactor**: Remove duplicated networking assumptions between Terraform inputs, outputs, deploy helpers, and runbooks, then run the full repository suite with `pytest` after implementation changes.

## User Story Delivery Strategy

### User Story 1 - Provision Hosted Networking with Infrastructure Code

- **Red**: Add failing contract and integration coverage proving the supported GCP durable-session path still depends on pre-existing manually created VPC, subnet, or connector resources.
- **Green**: Add the minimum Terraform-managed network resources and Redis/Cloud Run wiring needed so a clean supported GCP environment can provision the durable-session network layer in one reviewed apply path.
- **Refactor**: Consolidate duplicated network references and naming rules across the GCP adapter, then rerun `pytest`.

### User Story 2 - Feed Hosted Networking Outputs into Deployment and Verification

- **Red**: Add failing tests proving Terraform outputs and deployment evidence still expose only the abstract connectivity model rather than the managed network artifacts needed for review and verification.
- **Green**: Add the minimum output-contract and deploy-evidence changes required so rollout and hosted verification can trace the managed network path from Terraform reconciliation into deployment artifacts.
- **Refactor**: Tighten output naming, alias mapping, and evidence wording so networking metadata stays reviewable without becoming runtime-only configuration, then rerun `pytest`.

### User Story 3 - Remove Manual Networking Prerequisites from the GCP Runbook

- **Red**: Add failing documentation and contract checks proving the supported GCP path still tells operators to supply manual networking prerequisites for durable sessions.
- **Green**: Add the minimum README and operator-guidance updates required so the supported GCP path documents Terraform-managed networking before application rollout and keeps local paths separate.
- **Refactor**: Remove stale prerequisite wording and align failure/remediation guidance with the managed-network contract, then rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate Terraform-output alias mapping, deployment-input normalization, and any helper logic that classifies managed-network evidence for deployment records.
- Contract coverage should lock the hosted-network provisioning contract, the hosted-network output handoff contract, and the manual-prerequisite boundary contract documented in `/specs/027-terraform-hosted-networking/contracts/`.
- Integration coverage should verify the GCP Terraform adapter provisions the durable-session network layer, exports the required networking outputs, and preserves the existing deploy-script and hosted-verification ordering.
- Regression coverage should preserve the Terraform-to-deploy-to-verify chain from FND-025, the secret/session failure distinction from FND-022, and the local-first boundaries from FND-019 and FND-026.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: deployment records, Terraform outputs, and hosted verification artifacts must make the managed network path reviewable enough that operators can distinguish missing network provisioning from later runtime failures.
- Security: plans, outputs, deployment records, and verification evidence must remain free of secret values and bearer tokens; the feature must not weaken application-layer authentication or secret-access controls while changing the network path.
- Simplicity: the design extends the existing GCP Terraform adapter, deploy script, verification CLI, and README guidance. It does not introduce a second session model, a second deploy script, or a separate non-Terraform networking workflow.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design keeps FND-027 inside the existing GCP provider-adapter and Terraform-output handoff boundaries, preserves the current deploy-to-verify ordering, and keeps local workflows separate from hosted networking concerns. The required full-suite completion command remains `pytest`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
