# Implementation Plan: Remote MCP Security and Transport Hardening

**Branch**: `013-remote-mcp-security` | **Date**: 2026-03-16 | **Spec**: [~/Projects/youtube-mcp-server/specs/013-remote-mcp-security/spec.md](~/Projects/youtube-mcp-server/specs/013-remote-mcp-security/spec.md)
**Input**: Feature specification from `/specs/013-remote-mcp-security/spec.md`

## Summary

Harden the hosted MCP entry point so remote consumers must satisfy an explicit origin policy and authentication contract before accessing protected MCP flows. The plan adds security configuration and request-evaluation rules at the hosted transport boundary, documents the client contract in MCP-facing artifacts, expands observability for security decisions, and proves the behavior through unit, integration, contract, and end-to-end verification using Red-Green-Refactor sequencing.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, Python standard library transport/config/logging modules  
**Storage**: In-memory runtime state only; configuration and secrets are environment/secret-backed  
**Testing**: `pytest` with unit, integration, and contract suites  
**Target Platform**: Local development and Google Cloud Run hosted Linux runtime  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve existing hosted MCP responsiveness targets while rejecting unauthorized requests before tool execution; maintain readiness and streaming verification within existing operational expectations  
**Constraints**: No persistent storage, no secret leakage in logs or responses, preserve existing `/health`, `/ready`, and `/mcp` routes, maintain MCP streamable HTTP compatibility, keep valid hosted client behavior backward compatible except for new security enforcement  
**Scale/Scope**: Single hosted MCP service supporting production third-party consumption, concurrent streaming sessions, and operator-managed security configuration across `dev`, `staging`, and `prod`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with full regression test re-run
- [x] Integration and regression coverage strategy is documented
- [x] Observability, security, and simplicity constraints are addressed

## Project Structure

### Documentation (this feature)

```text
specs/013-remote-mcp-security/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hosted-mcp-security.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── observability.py
    ├── protocol/
    ├── tools/
    └── transport/

tests/
├── contract/
├── integration/
└── unit/

scripts/
├── deploy_cloud_run.sh
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Use the existing single-package Python service under `src/mcp_server` with test coverage split across `tests/unit`, `tests/integration`, and `tests/contract`. Feature artifacts remain isolated under `specs/013-remote-mcp-security`.

## Phase 0: Research and Decision Closure

### Research Focus

- Define the hosted authentication approach for third-party MCP consumers.
- Define how origin-aware handling should differentiate browser and non-browser clients.
- Define stable failure categories, status behavior, and observability fields for security decisions.
- Define the minimum deployment/runtime configuration changes and verification expectations needed for Cloud Run.

### Planned Red-Green-Refactor Flow

- **Red**: Identify missing or weakly defined security decisions by comparing the feature spec against the current hosted runtime, origin handling, auth behavior, README guidance, and existing tests.
- **Green**: Resolve each open decision in `research.md` with one chosen approach, rationale, and rejected alternatives so Phase 1 design can proceed without unresolved clarifications.
- **Refactor**: Collapse overlapping decisions into one coherent hosted security model and ensure the design keeps the smallest change surface needed for FND-013.

### Research Outputs

- `research.md` with final decisions for origin policy, authentication strategy, failure taxonomy, observability, and rollout guidance.

## Phase 1: Design and Contracts

### Design Focus

- Model the policy/configuration and request-decision objects needed for transport hardening.
- Define the external hosted contract for `/mcp`, `/health`, and `/ready` as it changes under security enforcement.
- Provide a concrete quickstart and verification flow for success and denied-access paths.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing contract and test expectations implied by the research decisions, including origin denial, missing-auth denial, malformed security input handling, and successful authenticated MCP initialization/tool calls.
- **Green**: Produce `data-model.md`, `contracts/hosted-mcp-security.md`, and `quickstart.md` with the minimal design and operator guidance required to implement those tests.
- **Refactor**: Remove duplicated or overly detailed design elements, verify that contract language remains implementation-aware but not implementation-bound, and re-check constitution compliance.

### Design Outputs

- `data-model.md`
- `contracts/hosted-mcp-security.md`
- `quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Protect the Hosted MCP Entry Point

- **Red**: Add failing unit tests for origin and authentication policy evaluation, integration tests for hosted request rejection before MCP processing, and contract tests for stable denial statuses and payloads.
- **Green**: Implement transport-bound security configuration loading, request classification for browser versus non-browser callers, auth enforcement, and denial behavior for invalid requests.
- **Refactor**: Consolidate request validation helpers, keep denial logic centralized, and rerun unit, integration, and contract regressions for hosted routing and MCP transport behavior.

### User Story 2 - Give Integrators a Clear Consumption Contract

- **Red**: Add failing docs/contract verification that expects authenticated examples, origin-aware guidance, and explicit unsupported-flow behavior in user-facing docs.
- **Green**: Update README and hosted verification guidance to show required credentials, origin expectations, and successful connection steps for supported clients.
- **Refactor**: Remove duplicated guidance between docs and contracts, confirm terminology is consistent across spec artifacts, and rerun documentation-linked integration checks.

### User Story 3 - Diagnose Security Failures Predictably

- **Red**: Add failing integration and contract tests asserting request identifiers, denial categories, and security-safe client-visible errors for representative failure paths.
- **Green**: Implement observability and failure mapping changes so denial decisions are inspectable without leaking sensitive values.
- **Refactor**: Simplify log/event field generation, ensure no redundant security metadata is emitted, and rerun observability regressions alongside hosted route tests.

### Regression Strategy

- Preserve existing `/health`, `/ready`, and valid `/mcp` behavior except where new auth or origin checks intentionally reject unsafe requests.
- Re-run the full hosted regression suite for request routing, readiness, observability, streamable transport, and Cloud Run verification after the feature lands.
- Validate that security denials occur before tool dispatch and do not create false-positive success metrics for protected MCP calls.

### Rollback and Mitigation

- Keep the security changes scoped to hosted request entry logic and runtime configuration so operators can roll back by redeploying the prior revision if a client compatibility issue appears.
- Document required environment/secret changes clearly so rollout failures are diagnosable via readiness and structured runtime events.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with full regression test re-run
- [x] Integration and regression coverage strategy is documented
- [x] Observability, security, and simplicity constraints are addressed

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
