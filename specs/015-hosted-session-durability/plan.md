# Implementation Plan: Hosted MCP Session Durability

**Branch**: `015-hosted-session-durability` | **Date**: 2026-03-18 | **Spec**: [~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/spec.md](~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/spec.md)
**Input**: Feature specification from `/specs/015-hosted-session-durability/spec.md`

## Summary

Harden hosted MCP session continuity so Cloud Run deployments no longer depend on a single process retaining in-memory session state. The plan introduces a shared durable session backend for hosted session metadata and replayable stream state, keeps the existing FastAPI-based MCP surface intact, defines the external continuity contract for initialization, follow-up `GET`/`POST`, reconnect, and invalid-session behavior, and proves the result through Red-Green-Refactor coverage that simulates cross-instance continuation instead of same-process-only success paths.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, Python standard library JSON/HTTP/config/logging modules, Redis-compatible shared session store client  
**Storage**: In-memory runtime state for local-only execution plus Redis-compatible shared ephemeral state for hosted session metadata, stream cursors, and replayable event history  
**Testing**: `pytest` driving existing unit, integration, and contract suites plus hosted verification flows  
**Target Platform**: Local development and Google Cloud Run hosted Linux runtime backed by a shared low-latency session store  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve the PRD hosted latency targets while keeping session lookup and reconnect overhead low enough that simple hosted follow-up requests remain within the current sub-3-second p95 expectation for non-transcript flows  
**Constraints**: Preserve MCP transport and protocol semantics from FND-009 and FND-010, preserve hosted security controls from FND-013, eliminate process-local session fragility for the supported deployment model, fail safely when the shared session backend is unavailable, and keep the design simple enough to operate on Cloud Run without requiring sticky routing  
**Scale/Scope**: One hosted MCP service with durable hosted session continuity across multiple Cloud Run instances, follow-up `GET` and `POST` support, reconnect-safe replay for recent events, and explicit documentation for supported versus unsupported deployment topologies

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
specs/015-hosted-session-durability/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hosted-session-durability-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── deploy.py
    ├── health.py
    ├── observability.py
    ├── security.py
    ├── protocol/
    │   ├── envelope.py
    │   └── methods.py
    ├── tools/
    │   └── dispatcher.py
    └── transport/
        ├── http.py
        └── streaming.py

tests/
├── contract/
├── integration/
└── unit/

scripts/
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Extend the existing single-package Python service under `src/mcp_server` by replacing process-local hosted session assumptions with a shared session persistence abstraction. Keep hosted request handling in `cloud_run_entrypoint.py` and `transport/http.py`, move session durability concerns behind the transport/session layer, and preserve the current `tests/unit`, `tests/integration`, and `tests/contract` split for Red-Green-Refactor coverage.

## Phase 0: Research and Decision Closure

### Research Focus

- Choose the smallest session durability strategy that survives Cloud Run instance routing without requiring sticky affinity.
- Decide how active session metadata, stream replay cursors, and recent server events are represented in shared state.
- Define when readiness should block hosted traffic because durable-session guarantees cannot be met.
- Define reconnect and invalid-session outcomes that remain MCP-safe and operator-diagnosable.
- Define how to simulate cross-instance continuation in automated tests and hosted verification without building a separate service tier.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the current process-local `StreamManager`, hosted entrypoint flow, deployment verification flow, and existing session tests against the FND-015 spec to enumerate every continuation gap, reconnect gap, and missing operator signal.
- **Green**: Resolve each design choice in `research.md`, including the shared session backend, TTL strategy, replay boundary, readiness gating, and supported deployment topology, leaving no unresolved clarifications.
- **Refactor**: Collapse overlapping durability decisions into one minimal continuity model that later YouTube tool flows can reuse without reintroducing affinity or per-instance assumptions.

### Research Outputs

- `research.md` with final decisions for durable session storage, replay boundaries, topology constraints, readiness behavior, observability, and regression coverage.

## Phase 1: Design and Contracts

### Design Focus

- Model the durable hosted session, stream replay state, deployment policy, and verification evidence entities required by FND-015.
- Define the external MCP contract changes for session initialization, continuation, reconnect, invalid-session, and readiness behavior.
- Provide a concrete quickstart that demonstrates Red-Green-Refactor checks, local multi-instance verification with shared session state, and hosted deployment verification for durable sessions.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing contract and design expectations for cross-instance continuation, reconnect replay, readiness when durable backing state is unavailable, and operator-visible unsupported-topology behavior.
- **Green**: Produce `data-model.md`, `contracts/hosted-session-durability-contract.md`, and `quickstart.md` with the minimum design detail needed to implement those failing tests.
- **Refactor**: Remove duplicated wording across the plan, contract, and quickstart; confirm the new session strategy does not weaken hosted security or expand protocol scope; and re-check that the design remains the simplest shape that satisfies the spec.

### Design Outputs

- `data-model.md`
- `contracts/hosted-session-durability-contract.md`
- `quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Continue an Active Hosted Session

- **Red**: Add failing unit and integration tests proving a session initialized on one app instance can be resumed by a different instance that shares the durable backend, and that follow-up `GET` and `POST` flows no longer fail because the second process lacks local memory.
- **Green**: Implement the minimum shared session persistence, replayable event lookup, and hosted session validation needed for valid session continuation and stable invalid-session errors.
- **Refactor**: Consolidate session-store access and replay logic, remove leftover direct in-memory session assumptions from hosted paths, and rerun the targeted plus regression suites.

### User Story 2 - Operate Within a Documented Deployment Topology

- **Red**: Add failing readiness, configuration, and deployment-verification tests proving operators receive a clear not-ready or unsupported-topology signal when durable session guarantees cannot be satisfied in hosted environments.
- **Green**: Implement the minimum runtime configuration, readiness checks, deployment documentation, and verification output needed to make the supported topology explicit and enforceable.
- **Refactor**: Simplify topology validation and operator messaging, remove duplicated constraint wording across config and docs, and rerun readiness, deployment, and security regression suites.

### User Story 3 - Reconnect and Verify Session Durability

- **Red**: Add failing contract, integration, and hosted verification checks for reconnect with a valid session, replay from a recent event cursor, and explicit failure when replay history is no longer available.
- **Green**: Implement the minimum reconnect-safe replay behavior and hosted verification updates needed to satisfy those checks without changing the established MCP transport contract beyond the new durability guarantees.
- **Refactor**: Consolidate reconnect error mapping, tighten observability around replay and expiry decisions, and rerun the full unit, contract, and integration suites.

### Regression Strategy

- Preserve existing `/health`, `/ready`, `initialize`, `tools/list`, `tools/call`, protected `/mcp`, and hosted security behavior outside the intentional changes to session durability and readiness enforcement.
- Re-run the full unit, contract, and integration suites after targeted durability tests pass to prove no regressions in protocol alignment, transport semantics, retrieval tools, readiness, or security handling.
- Verify that session durability work does not weaken the denial boundaries from FND-013 or alter the successful discovery/invocation behavior introduced in FND-014.

### Rollback and Mitigation

- Keep the feature scoped to hosted session state management, configuration, readiness, and verification artifacts so operators can roll back by redeploying the prior revision if the shared session backend or new readiness rules cause integration issues.
- Use stable structured session-state errors and explicit verification evidence so rollout issues can be diagnosed quickly and distinguished from generic transport or tool failures.

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
