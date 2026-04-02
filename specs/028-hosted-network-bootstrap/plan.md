# Implementation Plan: Automated Hosted Network Bootstrap Reconciliation

**Branch**: `028-hosted-network-bootstrap` | **Date**: 2026-03-31 | **Spec**: [spec.md](~/Projects/youtube-mcp-server/specs/028-hosted-network-bootstrap/spec.md)
**Input**: Feature specification from `/specs/028-hosted-network-bootstrap/spec.md`

## Summary

Treat managed hosted networking as an explicit part of the existing push-triggered deployment chain rather than an implied Terraform side effect. The implementation will refine the current repository-managed rollout path so the primary automatic pipeline and manual fallback both make network bootstrap ownership, remaining one-time bootstrap inputs, and failure-stage boundaries operator-visible without adding a second deploy mechanism or changing the hosted MCP runtime contract.

Canonical terms for this feature are `network bootstrap stage`, `bootstrap input set`, `hosted deployment run`, `failure boundary`, `automatic hosted pipeline`, and `hosted automation boundary`.

## Technical Context

**Language/Version**: Python 3.11 for service, deployment, verification, and workflow-support tooling; checked-in workflow definitions for automated and fallback hosted rollout  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Terraform-compatible IaC under `infrastructure/gcp`, `cloudbuild.yaml`, `.github/workflows/hosted-deploy.yml`, deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, `scripts/verify_cloud_run_foundation.py`  
**Storage**: In-memory runtime state for the service; Redis-compatible shared ephemeral state for hosted sessions; file-based workflow definitions, Terraform assets, deployment records, verification evidence, and planning artifacts  
**Testing**: `pytest` for unit, integration, and contract coverage; `ruff check .`; hosted verification via `PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py --deployment-record <deployment-record>`  
**Target Platform**: Local developer workflow plus the supported GCP-hosted Cloud Run deployment path, with `cloudbuild.yaml` as the primary push-triggered automation surface and `.github/workflows/hosted-deploy.yml` as the manual fallback  
**Project Type**: Python web service with provider-specific infrastructure automation, repository-managed deployment workflows, and hosted verification tooling  
**Performance Goals**: Preserve the current Terraform-to-deploy-to-verify flow while ensuring operators can identify bootstrap inputs, confirm network reconciliation happens before rollout, and classify bootstrap/network failures before later deployment or verification failures  
**Constraints**: Reuse the existing stage model and repository entrypoints; do not introduce a second deployment path; keep secret values and bearer tokens out of workflow outputs and logs; preserve Terraform outputs as the canonical infrastructure handoff; keep local-first development separate from hosted bootstrap concerns; preserve current application-layer auth and hosted MCP behavior  
**Scale/Scope**: One primary automatic hosted pipeline, one manual fallback workflow, one GCP provider adapter, one managed hosted network bootstrap boundary per environment, one deployment record per rollout, and one operator-facing failure taxonomy that spans bootstrap, reconcile, deploy, and verification stages

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

Pre-design gate result: PASS. This feature changes the hosted deployment pipeline contract, operator bootstrap boundary, and failure-stage reporting surface rather than MCP message payloads. Full-suite proof command: `pytest`. Repository quality-gate evidence remains `pytest` and `ruff check .`.

## Project Structure

### Documentation (this feature)

```text
specs/028-hosted-network-bootstrap/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── hosted-network-bootstrap-pipeline-contract.md
│   ├── hosted-network-bootstrap-failure-boundary-contract.md
│   └── hosted-network-bootstrap-prerequisite-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
.github/
└── workflows/

infrastructure/
├── gcp/
└── local/

scripts/
├── deploy_cloud_run.sh
├── dev_local.sh
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

cloudbuild.yaml
```

**Structure Decision**: Keep the existing single Python service, GCP provider adapter, primary Cloud Build pipeline, manual GitHub Actions fallback, deploy helpers, and hosted verification tooling. FND-028 extends the semantics and evidence of the current rollout chain rather than introducing new infrastructure modules or a second bootstrap mechanism.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current gap explicitly by showing that the repository already reconciles networking in the hosted pipeline but still treats network bootstrap as generic infrastructure work instead of a clearly classified operator-facing stage boundary.
- **Green**: Resolve the planning decisions for primary versus fallback workflow ownership, managed network bootstrap semantics within `infrastructure_reconcile`, remaining one-time bootstrap inputs, and failure-stage taxonomy in `research.md`.
- **Refactor**: Remove ambiguity between bootstrap-input failure, managed network reconcile failure, deployment failure, and hosted verification failure so later implementation work stays inside one reviewed rollout contract.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for ordered bootstrap reconciliation, required network-bootstrap visibility in the automatic hosted pipeline, and operator-readable failure boundaries.
- **Green**: Produce `data-model.md`, contract documents in `/contracts/`, and `quickstart.md` that define the hosted deployment run, network bootstrap stage, bootstrap input boundary, and failure classification expectations for the existing rollout path.
- **Refactor**: Normalize bootstrap, reconcile, deploy, and verification terminology across design artifacts and rerun the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing pipeline language for managed network bootstrap, missing failure-stage distinction between bootstrap/network and later rollout layers, and stale documentation that still implies separate recurring network provisioning.
- **Green**: Organize implementation around the minimum path that makes those tests pass: refine pipeline and bootstrap contracts, update helper classification and evidence surfaces if needed, and align operator documentation with the reviewed automatic workflow.
- **Refactor**: Remove duplicated bootstrap and stage-boundary wording across workflow definitions, deployment helpers, contracts, and runbooks, then rerun the full repository suite with `pytest` after implementation changes.

## User Story Delivery Strategy

### User Story 1 - Reconcile Network Prerequisites Before Hosted Rollout

- **Red**: Add failing contract and integration coverage proving the automatic hosted pipeline does not explicitly guarantee managed network reconciliation before application rollout for environments that require durable session connectivity.
- **Green**: Add the minimum workflow and contract changes required so the primary automatic pipeline and fallback workflow both present network bootstrap as part of the ordered hosted deployment chain before deploy.
- **Refactor**: Tighten stage naming and artifact wording so operators can trace one deployment run from bootstrap reconciliation into deployment and verification without inferring hidden steps, then rerun `pytest`.

### User Story 2 - Distinguish Bootstrap Failure from Application Failure

- **Red**: Add failing tests proving bootstrap-input failures, managed network reconcile failures, deploy failures, and hosted verification failures are not yet operator-visible as distinct failure classes.
- **Green**: Add the minimum failure-classification and contract updates required so deployment evidence and workflow outputs distinguish bootstrap/network failures from later rollout failures.
- **Refactor**: Consolidate failure taxonomy across workflow artifacts, deployment records, and runbook guidance so the same stage names and remediation boundaries appear everywhere, then rerun `pytest`.

### User Story 3 - Publish One Clear Bootstrap Boundary for Hosted Automation

- **Red**: Add failing documentation and contract checks proving the supported hosted path does not yet clearly distinguish one-time bootstrap inputs from recurring managed network reconciliation.
- **Green**: Add the minimum runbook and contract updates required so remaining external inputs are explicit, limited, and clearly separate from the recurring automated hosted deployment path.
- **Refactor**: Remove stale language that implies separate recurring manual networking setup and align operator guidance with the automatic primary pipeline plus manual fallback, then rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate helper logic that classifies deployment stages, missing bootstrap prerequisites, and any new operator-visible failure taxonomy used by workflow artifacts or deployment records.
- Contract coverage should lock the hosted-network bootstrap pipeline contract, failure-boundary contract, and prerequisite contract documented in `/specs/028-hosted-network-bootstrap/contracts/`.
- Integration coverage should verify the automatic hosted pipeline and fallback workflow preserve ordered `infrastructure_reconcile -> terraform_output_export -> deploy -> hosted_verification` behavior and block deployment success when bootstrap or reconcile prerequisites fail.
- Regression coverage should preserve the deployment-stage ordering from FND-025, the managed networking handoff from FND-027, the secret/session distinction from FND-022, and local-first workflow boundaries from FND-019 and FND-026.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: workflow artifacts, deployment records, and verification evidence must make it possible to identify whether failure occurred before reconciliation started, during managed network bootstrap, during application deploy, or during hosted verification.
- Security: automation may reference secret names, workload identities, and infrastructure outputs, but it must never emit secret values or bearer tokens in workflow outputs, deployment records, or operator guidance.
- Simplicity: the design extends `cloudbuild.yaml`, `.github/workflows/hosted-deploy.yml`, `scripts/deploy_cloud_run.sh`, `scripts/verify_cloud_run_foundation.py`, and `src/mcp_server/deploy.py`. It does not add a second deployment helper, a second verifier, or a second infrastructure handoff model.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design keeps FND-028 inside the existing automatic Cloud Build pipeline, the manual GitHub Actions fallback, and the current Terraform-to-deploy-to-verify chain. It sharpens stage semantics and failure reporting without changing the hosted MCP contract. The required full-suite completion command remains `pytest`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
