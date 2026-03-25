# Implementation Plan: Hosted Dependency Wiring for Secrets and Durable Sessions

**Branch**: `022-hosted-dependency-wiring` | **Date**: 2026-03-24 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/022-hosted-dependency-wiring/spec.md)
**Input**: Feature specification from `/specs/022-hosted-dependency-wiring/spec.md`

## Summary

Close the gap between foundational GCP infrastructure and a truly deployable hosted runtime by wiring the Cloud Run runtime identity to secret-backed configuration and wiring the hosted service to the durable session backend with explicit, diagnosable provider-specific connectivity. The implementation will extend the existing GCP provider adapter, deployment handoff, readiness behavior, hosted verification flow, and operator runbooks so secret-access failures and session-connectivity failures are reviewable, distinct, and actionable before remote MCP consumers encounter them.

Canonical terms for this feature are `runtime identity`, `secret access binding`, `durable session connectivity path`, `dependency readiness state`, and `hosted verification evidence`.

## Technical Context

**Language/Version**: Python 3.11 for service, deployment, and verification tooling; Terraform-compatible IaC definitions for the GCP provider adapter  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis client, Python standard library HTTP/config/logging tooling, Terraform-compatible assets under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py`  
**Storage**: In-memory runtime state for request handling; Redis-compatible shared ephemeral state for hosted session durability; secret-backed runtime configuration; file-based infrastructure definitions, contracts, and operator evidence artifacts  
**Testing**: `pytest` for unit, contract, and integration suites; hosted verification and documentation/workflow validation for dependency wiring evidence  
**Target Platform**: Local development, hosted-like local verification, and GCP-hosted Cloud Run deployments with Secret Manager-backed configuration and durable hosted session support  
**Project Type**: Python web service with provider-specific infrastructure automation, hosted verification tooling, and operator runbooks  
**Performance Goals**: Preserve existing hosted readiness and session-continuation expectations while letting operators diagnose missing secret access or missing session connectivity on the first verification pass  
**Constraints**: Least-privilege runtime secret access; no secret values in code, logs, or artifacts; readiness must distinguish secret-access failures from session-backend failures; minimal local execution must remain provider-free; extend the current GCP adapter, deploy script, runtime readiness path, and hosted verifier instead of creating parallel workflows  
**Scale/Scope**: One MCP service, one primary hosted provider adapter (`gcp`), one runtime identity per hosted environment, one durable Redis-backed session dependency per hosted environment, and one hosted verification workflow covering success plus two dependency failure classes

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

Pre-design gate result: PASS. This feature changes hosted deployment, readiness, and operator verification behavior at the provider-adapter boundary, so explicit contracts are required for runtime secret access, session connectivity, and hosted dependency verification. Full-suite proof command: `pytest`.

## Project Structure

### Documentation (this feature)

```text
specs/022-hosted-dependency-wiring/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── runtime-secret-access-contract.md
│   ├── runtime-session-connectivity-contract.md
│   └── hosted-dependency-verification-contract.md
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
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── deploy.py
    ├── health.py
    ├── infrastructure_contract.py
    ├── observability.py
    └── transport/
        ├── http.py
        ├── session_store.py
        └── streaming.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service, GCP provider adapter, deployment workflow, and hosted verification tooling. FND-022 planning concentrates on `infrastructure/gcp`, `scripts/`, `src/mcp_server/`, and the existing test suites rather than adding a new runtime or infrastructure layer.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current gap explicitly by showing that the repository creates Secret Manager objects, a runtime service account, and a Redis session backend, but does not yet define the actual runtime secret-read path, Cloud Run-to-session-backend network path, or separate verification evidence for those two dependency failures.
- **Green**: Resolve the planning decisions for runtime secret-access ownership, dependency failure classification, connectivity-model terminology, verification ordering, and contract boundaries in `research.md`.
- **Refactor**: Remove ambiguous wording around generic configuration failures versus provider-wiring failures, align terminology with FND-015, FND-019, FND-020, and FND-021, and confirm the design handoff stays inside the current deployment and readiness model.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for runtime secret access, session connectivity, and hosted dependency verification, plus any missing entities needed to reason about runtime identity, access bindings, readiness state, and verification evidence.
- **Green**: Produce `data-model.md`, contract documents in `/contracts/`, and `quickstart.md` that define least-privilege secret access, provider-specific session connectivity, and operator-visible proof for healthy, secret-failure, and session-failure paths.
- **Refactor**: Normalize dependency terminology, evidence fields, and remediation language across the design artifacts, then rerun the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing secret-access IAM wiring, missing runtime secret injection, missing session-connectivity plumbing, and missing readiness or verification distinction between secret-access and session-connectivity failures.
- **Green**: Organize implementation around the minimum path that makes those tests pass: extend the GCP adapter to express secret-read bindings and session-connectivity plumbing, extend the runtime readiness path and hosted verifier to classify dependency failures, and update README and runbooks without altering MCP auth semantics.
- **Refactor**: Remove duplicated dependency-wiring guidance between infrastructure docs, deployment docs, readiness diagnostics, and verification evidence, then run the full repository suite with `pytest` after implementation changes.

## User Story Delivery Strategy

### User Story 1 - Run the Hosted Service with Working Secret and Session Dependencies

- **Red**: Add failing contract and integration coverage proving the hosted deployment can still exist without a defined secret-read path or without a defined session-connectivity path.
- **Green**: Add the minimum provider-specific wiring, deployment handoff, and verification artifacts required for the runtime to access required secrets and complete a durable hosted session continuation flow.
- **Refactor**: Remove duplicate dependency definitions across Terraform, deployment, and runtime configuration, then rerun `pytest`.

### User Story 2 - Detect Missing Secret or Session Wiring Quickly

- **Red**: Add failing checks proving readiness and hosted verification still collapse dependency failures into generic configuration or startup errors.
- **Green**: Add the minimum readiness and hosted-verification behavior required to distinguish secret-access denial from session-backend-connectivity denial.
- **Refactor**: Tighten failure classification and remediation wording so operators can diagnose the first failing dependency without source inspection, then rerun `pytest`.

### User Story 3 - Understand the Required Hosted Connectivity Model

- **Red**: Add failing contract and documentation checks proving the runtime identity, secret-access model, and session-connectivity model are still implicit or under-documented.
- **Green**: Add the minimum contract and quickstart/runbook detail required to explain the provider-specific dependency model and its verification evidence.
- **Refactor**: Consolidate operator-facing wiring guidance into one coherent handoff and rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate dependency classification helpers, deployment-input validation, readiness payload distinctions, and any non-secret evidence models introduced for provider wiring.
- Contract coverage should lock the runtime secret-access contract, runtime session-connectivity contract, and hosted dependency-verification contract documented in `/specs/022-hosted-dependency-wiring/contracts/`.
- Integration coverage should verify the Terraform output and deploy handoff, readiness behavior, and hosted verification flow for healthy, secret-failure, and session-failure states.
- Regression coverage should preserve the existing MCP authentication contract, public `/health` and `/ready` behavior, durable session semantics from FND-015, and public-reachability behavior from FND-021.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: readiness and hosted verification must produce operator-usable evidence that distinguishes secret-access failures from session-connectivity failures without exposing secret values.
- Security: the runtime identity must use least-privilege secret access, verification artifacts must never include secret values or bearer tokens, and MCP-layer authentication remains unchanged.
- Simplicity: the design extends the existing GCP Terraform adapter, deploy script, runtime readiness path, and hosted verifier; it does not introduce a second hosted runtime, a second dependency verifier, or a new secret-management mechanism.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design artifacts keep dependency wiring as a provider-adapter and hosted-runtime concern, preserve the existing MCP auth and session contracts, and extend the current deployment-to-readiness-to-verification workflow instead of creating a parallel path. The required full-suite completion command remains `pytest`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
