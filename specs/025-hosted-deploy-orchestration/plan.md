# Implementation Plan: Automated Hosted Deployment Orchestration

**Branch**: `025-hosted-deploy-orchestration` | **Date**: 2026-03-30 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/025-hosted-deploy-orchestration/spec.md)
**Input**: Feature specification from `/specs/025-hosted-deploy-orchestration/spec.md`

## Summary

Turn hosted deployment into one checked-in push-triggered workflow that runs repository quality gates, builds and publishes the application image, reconciles the hosted platform through Terraform, deploys through the existing repository deployment path, and blocks success unless hosted verification passes. The implementation will extend the current GCP provider adapter, deployment handoff, verification CLI, and operator runbooks without introducing a second rollout path or collapsing the secret-management boundary.

Canonical terms for this feature are `deployment branch`, `deployment workflow run`, `bootstrap prerequisite`, `infrastructure reconciliation output`, `hosted verification gate`, and `secret wiring boundary`.

## Technical Context

**Language/Version**: Python 3.11 for service, deployment, and verification tooling; checked-in CI workflow definition for push-triggered orchestration  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Terraform-compatible IaC under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, `scripts/verify_cloud_run_foundation.py`, container image build/publish tooling, repository-hosted workflow automation  
**Storage**: In-memory runtime state for request handling; Redis-compatible shared ephemeral state for hosted sessions; file-based Terraform definitions, workflow definitions, deployment records, verification evidence, and specification artifacts  
**Testing**: `pytest` for unit, contract, and integration coverage; `ruff check .`; hosted verification via `PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py --deployment-record <deployment-record>`  
**Target Platform**: Local developer workflow plus GCP-hosted Cloud Run deployment triggered from a checked-in repository workflow on the intended deployment branch  
**Project Type**: Python web service with provider-specific infrastructure automation, hosted verification tooling, and repository-managed deployment orchestration  
**Performance Goals**: Preserve the existing hosted rollout and verification path while ensuring a qualifying branch push produces one reviewable deployment run, fails before rollout on broken prerequisites, and never reports success when hosted verification fails  
**Constraints**: Reuse Terraform outputs plus `scripts/deploy_cloud_run.sh` and `scripts/verify_cloud_run_foundation.py`; do not bypass repository deployment logic with an image-only update; keep secret values out of code, logs, and committed automation; preserve local verification paths; make failure stages operator-readable  
**Scale/Scope**: One intended deployment branch, one checked-in hosted deployment workflow, one primary GCP provider adapter, one hosted deployment record per rollout, and one hosted verification gate covering reachability, readiness, secret access, session continuity, and MCP behavior

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

Pre-design gate result: PASS. This feature changes the hosted deployment contract, bootstrap expectations, and operator-facing release gate, so explicit deployment contracts are required. Full-suite proof command: `pytest`.

## Project Structure

### Documentation (this feature)

```text
specs/025-hosted-deploy-orchestration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── hosted-deployment-pipeline-contract.md
│   └── deployment-bootstrap-boundary-contract.md
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
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── deploy.py
    ├── infrastructure_contract.py
    └── transport/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service, GCP provider adapter, deployment helpers, and hosted verification tooling. FND-025 adds a checked-in workflow definition under `.github/workflows/` and updates the current deployment/verification path rather than creating a parallel deployment mechanism.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current deployment gap explicitly by showing that the repository has Terraform, deploy, and verify entrypoints, but no checked-in push-triggered workflow that chains them together and fails on hosted verification.
- **Green**: Resolve the planning decisions for workflow ownership, infrastructure-to-deploy handoff, verification gating, bootstrap prerequisites, and secret-boundary responsibilities in `research.md`.
- **Refactor**: Remove ambiguity between infrastructure reconciliation, application rollout, and hosted verification responsibilities so later implementation work stays inside one repository-managed rollout path.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for workflow trigger behavior, ordered deployment stages, bootstrap prerequisites, and the boundary between secret wiring and operator-managed secret values.
- **Green**: Produce `data-model.md`, contract documents in `/contracts/`, and `quickstart.md` that define the workflow stages, artifacts, operator responsibilities, and failure gates needed for push-triggered hosted deployment.
- **Refactor**: Normalize deployment terminology, artifact naming, and failure-stage wording across the design artifacts, then rerun the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing workflow trigger coverage, missing Terraform-output handoff, direct image-only deployment bypass, missing hosted verification gate, and missing bootstrap or secret-boundary documentation.
- **Green**: Organize implementation around the minimum path that makes those tests pass: add one checked-in workflow definition, reuse the existing deploy/verify scripts, wire Terraform outputs into rollout, publish deployment and verification artifacts, and update operator documentation.
- **Refactor**: Remove duplicated deployment instructions between workflow definitions, scripts, and README sections, then run the full repository suite with `pytest` after implementation changes.

## User Story Delivery Strategy

### User Story 1 - Deploy the Hosted Platform from a Branch Push

- **Red**: Add failing contract and integration coverage proving the repository still lacks one push-triggered deployment workflow that reconciles infrastructure, deploys the current revision, and blocks completion on hosted verification failure.
- **Green**: Add the minimum checked-in workflow definition and repository handoff needed to run tests, build/publish the image, apply Terraform, deploy through `scripts/deploy_cloud_run.sh`, and verify through `scripts/verify_cloud_run_foundation.py`.
- **Refactor**: Tighten artifact naming and stage boundaries so operators can trace one deployment run end to end, then rerun `pytest`.

### User Story 2 - Review and Trust Deployment Logic in Version Control

- **Red**: Add failing checks proving the rollout still depends on manual or image-only deployment behavior that bypasses repository logic or Terraform-output handoff.
- **Green**: Add the minimum workflow and contract changes required so maintainers can review infrastructure reconciliation, application rollout, and hosted verification as one version-controlled path.
- **Refactor**: Consolidate duplicate deployment-handoff logic between workflow configuration, deploy helpers, and documentation, then rerun `pytest`.

### User Story 3 - Distinguish Automation from Secret Value Management

- **Red**: Add failing documentation and contract checks proving bootstrap prerequisites and secret ownership remain implicit or that automation appears to own secret contents.
- **Green**: Add the minimum bootstrap guidance and workflow failure handling required to distinguish automation-managed secret reference wiring from operator-managed secret value population and rotation.
- **Refactor**: Tighten operator-facing remediation language so missing secret values, missing permissions, and unreachable session backends remain distinct failure classes, then rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate workflow-stage outcome mapping, deployment-record handling, Terraform-output consumption helpers, and bootstrap/failure classification helpers introduced for the workflow path.
- Contract coverage should lock the hosted deployment pipeline contract and bootstrap-boundary contract documented in `/specs/025-hosted-deploy-orchestration/contracts/`.
- Integration coverage should verify workflow-stage handoff across tests, image publication metadata, Terraform output export, deploy-script invocation, and hosted verification failure propagation.
- Regression coverage should preserve the deploy-script contract, hosted verification contract, secret-access and session-connectivity diagnostics from FND-022, public reachability behavior from FND-021, and initialize-session correctness from FND-024.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: each workflow run must expose the failing stage, retain the deployment record and hosted verification evidence, and keep release-gate outcomes reviewable without reading raw cloud logs first.
- Security: automation may wire secret references, identities, and permissions, but it must never commit, print, or generate secret values; hosted verification evidence must remain free of secrets and bearer tokens.
- Simplicity: the feature extends the existing Terraform, deploy script, verification CLI, and README guidance. It does not add a second deploy script, a second verifier, or a separate non-repository deployment path.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design keeps deployment automation inside the repository-managed rollout path, preserves the hosted verification gate, and maintains the security boundary between infrastructure-managed secret wiring and operator-managed secret values. The required full-suite completion command remains `pytest`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
