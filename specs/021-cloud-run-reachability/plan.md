# Implementation Plan: Cloud Run Public Reachability for Remote MCP

**Branch**: `021-cloud-run-reachability` | **Date**: 2026-03-24 | **Spec**: [spec.md](~/Projects/youtube-mcp-server/specs/021-cloud-run-reachability/spec.md)
**Input**: Feature specification from `/specs/021-cloud-run-reachability/spec.md`

## Summary

Make the Cloud Run hosted MCP service intentionally publicly reachable for trusted remote consumers without collapsing that concern into MCP authentication. The implementation will extend the existing GCP provider adapter, deployment workflow, hosted verification path, and operator documentation so public invocation intent is explicit, public-reachability evidence is reviewable, and Cloud Run platform denial remains distinguishable from MCP bearer-token denial at the application boundary.

Canonical terms for this feature are `public invocation`, `cloud-level denial`, `MCP-layer authentication denial`, `remote consumer connection point`, and `verification evidence`.

## Technical Context

**Language/Version**: Python 3.11 for service, deployment, and verification tooling; Terraform-compatible IaC definitions for the GCP provider adapter  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Python standard library HTTP tooling, Terraform-compatible assets under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py`  
**Storage**: In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted session durability; file-based infrastructure definitions, contracts, and operator verification evidence  
**Testing**: `pytest` for unit, contract, and integration suites; documentation and workflow verification for deployment, public reachability, and hosted verification evidence  
**Target Platform**: Local development, hosted-like local verification, and GCP-hosted Cloud Run deployments intended for remote MCP consumption  
**Project Type**: Python web service with provider-specific infrastructure automation, hosted verification tooling, and operator runbooks  
**Performance Goals**: Preserve the PRD hosted availability and latency expectations while adding a repeatable public-access workflow that operators can verify quickly and diagnose on the first attempt  
**Constraints**: Public Cloud Run reachability must remain separate from MCP bearer-token authentication; minimal local execution must stay provider-free; hosted verification must distinguish platform denial from MCP denial; secrets must remain secret-backed and absent from logs and docs; the design should extend existing deployment and verification assets rather than invent a parallel workflow  
**Scale/Scope**: One MCP service, one primary hosted provider adapter (`gcp`), one public remote connection point per hosted environment, three execution modes (`minimal_local`, `hosted_like_local`, `hosted`), and one operator workflow covering success plus two distinct denial paths

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

Pre-design gate result: PASS. This feature changes operator-facing hosted deployment and verification behavior, so the contract surface is the Cloud Run public-access workflow and the hosted reachability-verification evidence, while the existing MCP bearer-token contract remains in force. Full-suite proof command: `pytest`.

## Project Structure

### Documentation (this feature)

```text
specs/021-cloud-run-reachability/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cloud-run-public-access-contract.md
│   └── hosted-reachability-verification-contract.md
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
    ├── infrastructure_contract.py
    ├── security.py
    └── transport/
        └── http.py

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service, GCP provider adapter, and hosted verification workflow. FND-021 planning adds design artifacts around `infrastructure/gcp`, `scripts/`, `src/mcp_server/`, and the existing test suites rather than introducing a new runtime or deployment surface.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current gap explicitly by showing that the repository documents hosted deployment and MCP authentication, but does not yet define an explicit operator contract for Cloud Run public invocation or a clear evidence model separating cloud-level denial from MCP-layer denial.
- **Green**: Resolve the planning decisions for public invocation ownership, verification ordering, denial classification, contract boundaries, and quickstart evidence in `research.md`.
- **Refactor**: Remove ambiguous wording around public access versus authentication, align the new terminology with FND-013, FND-019, and FND-020, and confirm the decisions support a minimal design handoff into data model, contracts, and quickstart artifacts.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for the Cloud Run public-access workflow and the hosted reachability-verification evidence, plus any missing entity relationships needed to reason about public invocation intent, connection points, and denial interpretation.
- **Green**: Produce `data-model.md`, contract documents in `/contracts/`, and `quickstart.md` that define intentional public invocation, remote consumer connection expectations, and operator-visible proof for both platform denial and MCP-layer denial.
- **Refactor**: Normalize public-access terminology, evidence fields, and remediation language across the design artifacts, then rerun the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing public-access deployment inputs, missing verification evidence for public reachability, and missing separation between cloud-level denial and MCP-layer denial in operator documentation and hosted checks.
- **Green**: Organize implementation around the minimum path that makes those tests pass: extend the GCP provider adapter and deployment handoff to express public invocation intent, extend the hosted verifier and evidence model, and update README and runbooks without weakening the existing MCP authentication contract.
- **Refactor**: Remove duplicated public-access guidance between infrastructure docs, deployment docs, and verification evidence, then run the full repository suite with `pytest` after implementation changes.

## User Story Delivery Strategy

### User Story 1 - Reach the Hosted MCP Service from a Trusted Remote Consumer

- **Red**: Add failing contract and integration coverage proving the hosted service can still be deployed without explicit public-invocation intent or without evidence that remote consumers can reach it publicly.
- **Green**: Add the minimum deployment, infrastructure, and verification artifacts required to make public reachability explicit and reviewable for trusted remote consumers.
- **Refactor**: Remove duplicated connection-point guidance, keep the operator workflow concise, and rerun `pytest`.

### User Story 2 - Configure Public Access Intentionally and Reproducibly

- **Red**: Add failing checks proving public access is still implicit, undocumented, or only inferable from provider defaults and console behavior.
- **Green**: Add operator-facing contracts and runbook updates that define public invocation as an intentional, reviewable part of the hosted workflow.
- **Refactor**: Tighten the provider-adapter handoff so public reachability evidence remains visible in normal review artifacts, then rerun `pytest`.

### User Story 3 - Distinguish Reachability Failures from Authentication Failures

- **Red**: Add failing verification and contract coverage proving operators cannot yet distinguish cloud-level denial from MCP bearer-token denial in a reproducible way.
- **Green**: Extend verification evidence and quickstart flows so one success path and two distinct failure paths demonstrate the separation clearly.
- **Refactor**: Consolidate denial terminology across verification, contracts, and operator docs, confirm no secret-bearing diagnostics are added, and rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate any deployment-input, public-access intent, or verification-evidence helpers introduced for Cloud Run reachability.
- Contract coverage should lock the Cloud Run public-access contract and the hosted reachability-verification contract documented in `/specs/021-cloud-run-reachability/contracts/`.
- Integration coverage should verify the deployment handoff, hosted verification ordering, and operator-facing distinction between cloud-level denial and MCP-layer denial.
- Regression coverage should preserve the existing bearer-token security contract, unauthenticated `/health` and `/ready` behavior, deployment-record output model, and local-first workflows from FND-013, FND-019, and FND-020.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: public-reachability verification must produce operator-usable evidence that distinguishes platform denial from MCP denial without requiring source inspection.
- Security: public Cloud Run reachability must not replace or weaken the existing MCP bearer-token boundary, and no new logs or artifacts may expose tokens or secret values.
- Simplicity: the design extends the current GCP provider adapter, deploy script, verifier, and docs; it does not introduce a second hosted runtime, a second verifier, or a new authentication mechanism.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design artifacts keep Cloud Run public access as an operator and provider-adapter concern, preserve the existing MCP bearer-token contract, and extend the current deployment-to-verification workflow instead of creating a parallel path. The required full-suite completion command remains `pytest`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
