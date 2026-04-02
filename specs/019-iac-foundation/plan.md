# Implementation Plan: Infrastructure as Code Foundation

**Branch**: `019-iac-foundation` | **Date**: 2026-03-21 | **Spec**: [spec.md](~/Projects/youtube-mcp-server/specs/019-iac-foundation/spec.md)
**Input**: Feature specification from `/specs/019-iac-foundation/spec.md`

## Summary

Add a first-class Infrastructure as Code foundation for the hosted MCP platform so Cloud Run runtime resources, secret/config integration points, and the durable session backend can be provisioned reproducibly from versioned definitions. The implementation will keep the existing Python deployment and verification scripts as the application rollout path, add a GCP-focused infrastructure layer under `infrastructure/gcp`, add a separate local hosted-like dependency path under `infrastructure/local`, and preserve the existing minimal local runtime path without requiring cloud provisioning.

## Technical Context

**Language/Version**: Python 3.11 for service and verification tooling; Terraform-compatible IaC definitions for infrastructure provisioning  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis client, Google Cloud Run deployment surface, Secret Manager integration points, Redis-compatible shared session backend, Docker Compose for hosted-like local dependency startup  
**Storage**: In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted sessions; file-based infrastructure definitions and operator documentation  
**Testing**: `pytest` for unit, integration, and contract suites; documentation and workflow verification for provisioning, deployment, and local hosted-like setup  
**Target Platform**: Local developer environments plus Google Cloud Run hosted deployments, with local Docker-compatible dependency startup for hosted-like verification  
**Project Type**: Python web service with infrastructure automation and operator runbooks  
**Performance Goals**: Preserve the PRD hosted latency expectations while making infrastructure provisioning reproducible within the spec targets of 60 minutes for provisioning and 30 minutes for deployment  
**Constraints**: Minimal local runtime must remain usable without cloud provisioning; secrets must stay out of source and logs; hosted durability requirements must be met with shared state; infrastructure layout must fit the existing `infrastructure/gcp` and `infrastructure/local` directories and stay simple enough to extend in FND-020  
**Scale/Scope**: One MCP service, three runtime profiles (`dev`, `staging`, `prod`), one durable hosted session backend path, one hosted-like local dependency path, and one operator-facing provisioning plus deployment workflow

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

Pre-design gate result: PASS. This feature updates operator-facing infrastructure and deployment contracts rather than MCP protocol contracts, so new contracts are defined for provisioning inputs, outputs, and verification expectations in `/specs/019-iac-foundation/contracts/`. Full-suite proof command: `pytest`.

## Project Structure

### Documentation (this feature)

```text
specs/019-iac-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── gcp-hosted-foundation-contract.md
│   └── local-hosted-dependency-contract.md
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
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── deploy.py
    └── transport/
        └── session_store.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service structure under `src/` and `tests/`, and add the missing IaC layer in the already-created `infrastructure/gcp` and `infrastructure/local` directories. This keeps cloud provisioning, local hosted-like dependency startup, application deployment, and verification clearly separated without introducing a new app package layout.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current gaps explicitly by documenting that `infrastructure/` is empty, that hosted prerequisites are assumed rather than provisioned, and that there is no reproducible hosted-like local dependency path today.
- **Green**: Resolve the planning decisions for IaC tool choice, GCP resource scope, local hosted-like dependency strategy, and operator contract boundaries in `research.md`.
- **Refactor**: Remove ambiguous scope statements, align terminology with the spec and README, and confirm the research decisions preserve a clean handoff into data model, contracts, and quickstart artifacts.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for operator-facing provisioning and local hosted-like dependency setup, plus any missing entity relationships needed to reason about environments, secrets, and session infrastructure.
- **Green**: Produce `data-model.md`, operator-facing contract documents in `/contracts/`, and `quickstart.md` with separate minimal-local, hosted-like-local, provisioning, deployment, and hosted-verification flows.
- **Refactor**: Normalize input names, outputs, and failure modes across the design artifacts, and re-run the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing infrastructure asset checks, provisioning contract checks, local hosted-like setup verification, and documentation coverage tests.
- **Green**: Organize implementation around the minimum path that makes those tests pass: create GCP IaC assets, create local hosted-like dependency assets, wire operator docs to the new paths, and keep the existing deployment and verification scripts as consumers of documented outputs.
- **Refactor**: Consolidate duplicated config knowledge between IaC assets, scripts, and docs, then run the full repository suite with `pytest` after implementation changes.

## User Story Delivery Strategy

### User Story 1 - Provision the Hosted Platform from Versioned Definitions

- **Red**: Add failing contract and integration coverage proving required hosted resources are not yet defined in versioned infrastructure and that documented provisioning cannot be completed from repo assets alone.
- **Green**: Add the minimum GCP infrastructure definitions and operator documentation needed to provision the hosted application runtime, runtime identity, secret integration points, and durable session backend.
- **Refactor**: Remove duplicated provisioning assumptions from scripts and docs, and rerun `pytest`.

### User Story 2 - Deploy the Application Through a Reproducible Hosted Path

- **Red**: Add failing checks proving the deployment path still depends on undocumented pre-created resources or source edits.
- **Green**: Align IaC outputs and operator documentation with the existing deployment script so application rollout uses documented injectable inputs only.
- **Refactor**: Simplify deploy documentation and runtime input handling, and rerun `pytest`.

### User Story 3 - Preserve a First-Class Local Path While Documenting Hosted-Like Verification

- **Red**: Add failing checks proving there is no reproducible local dependency path for hosted-like session verification and that local prerequisites are not clearly separated.
- **Green**: Add local infrastructure assets and docs that start the durable dependency path separately from the minimal local runtime path.
- **Refactor**: Remove overlapping local/hosted instructions, confirm observability and security guidance still applies, and rerun `pytest`.

## Coverage Strategy

- Unit coverage will validate infrastructure input mapping, required input validation, and any local dependency bootstrap helpers added for this feature.
- Integration coverage will exercise provisioning/deployment workflow expectations and verify the app can consume the documented outputs without source edits.
- Contract coverage will lock the operator-facing provisioning and local hosted-like setup contracts documented in `/contracts/`.
- Regression coverage will preserve the existing Cloud Run deploy script behavior, readiness/config validation behavior, and hosted verification flow.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: provisioning and deployment workflows must produce operator-usable outputs and must not remove the structured deployment/verification evidence already required by existing scripts.
- Security: infrastructure definitions and docs must treat `YOUTUBE_API_KEY`, `MCP_AUTH_TOKEN`, and session backend connection data as secret-backed inputs, not hard-coded values.
- Simplicity: the design stays GCP-first under `infrastructure/gcp` and adds only one local hosted-like dependency path under `infrastructure/local`; broader provider abstraction is deferred to FND-020.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design artifacts keep the feature within a GCP-first infrastructure foundation, define operator-facing contracts, preserve local-first development, and maintain the mandatory `pytest` full-suite completion gate.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
