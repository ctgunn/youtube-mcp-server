# Implementation Plan: Initialize Session Correctness

**Branch**: `024-initialize-session-correctness` | **Date**: 2026-03-27 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/spec.md)
**Input**: Feature specification from `/specs/024-initialize-session-correctness/spec.md`

## Summary

Tighten the hosted MCP initialize lifecycle so `MCP-Session-Id` is issued only after a successful initialize handshake and no usable hosted session state is created for malformed, invalid, or otherwise rejected initialize requests. The plan keeps the existing FastAPI-hosted MCP service, streamable `/mcp` route, security model, and session store intact while moving session creation behind initialize success, adding explicit failure-path coverage, and aligning hosted verification plus documentation with the corrected lifecycle.

Canonical terms for this feature are `initialize request`, `initialize outcome`, `hosted session`, `continuation session identifier`, `session creation gate`, and `hosted verification evidence`.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis-compatible session store support, Python standard-library JSON/HTTP/config/logging tooling, existing MCP transport/protocol/tooling modules under `src/mcp_server/`  
**Storage**: In-memory runtime state for local execution plus shared ephemeral session state through the existing hosted session store abstraction; no new persistent storage introduced for this slice  
**Testing**: `pytest` for unit, contract, and integration suites; `ruff check .` for linting; hosted verification via `scripts/verify_cloud_run_foundation.py` and verification-flow tests  
**Target Platform**: Local development plus hosted Linux runtime on Google Cloud Run serving authenticated remote MCP traffic  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve the existing single-request initialize path and current hosted continuation behavior while eliminating invalid session creation; no additional initialize round trip or new transport surface  
**Constraints**: Keep the existing `/mcp` route, MCP streamable HTTP behavior, authentication model, session header names, and durable-session architecture; preserve protocol-aligned initialize responses; avoid introducing a second session lifecycle or fallback session issuance path  
**Scale/Scope**: One hosted MCP service, one initialize handshake boundary, and one session-creation rule spanning request routing, session storage, verifier checks, contract tests, integration tests, and operator documentation

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

Pre-design gate result: PASS. FND-024 changes externally visible hosted MCP behavior because it changes when `MCP-Session-Id` may appear and whether continuation state exists after a rejected initialize request. The plan keeps the correction inside the existing initialize and session seams instead of introducing a second handshake mechanism. Full-suite proof commands before completion: `python3 -m pytest` and `ruff check .`.

## Project Structure

### Documentation (this feature)

```text
specs/024-initialize-session-correctness/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── initialize-session-correctness-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── deploy.py
    ├── protocol/
    │   ├── envelope.py
    │   └── methods.py
    └── transport/
        ├── http.py
        ├── session_store.py
        └── streaming.py

tests/
├── contract/
│   ├── test_hosted_mcp_security_contract.py
│   └── test_streamable_http_contract.py
├── integration/
│   ├── test_cloud_run_verification_flow.py
│   ├── test_hosted_http_routes.py
│   ├── test_mcp_request_flow.py
│   └── test_streamable_http_transport.py
└── unit/
    └── test_method_routing.py

scripts/
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Extend the existing single-package Python service under `src/mcp_server` by changing only the hosted initialize/session lifecycle seam and its existing verification surfaces. Preserve the current `tests/unit`, `tests/contract`, and `tests/integration` layout so Red-Green-Refactor coverage stays explicit at the protocol, hosted route, and verifier boundaries.

## Implementation Phases

### Phase 0 - Research and Lifecycle Closure

- **Red**: Capture the current mismatch between the intended FND-024 behavior and the repo’s current initialize flow by documenting that `execute_hosted_request()` creates a session for any `initialize` request before checking whether the protocol response succeeded.
- **Green**: Resolve the planning decisions for the initialize success gate, the definition of a failed initialize path, retry-after-failure behavior, observability expectations, and hosted verification evidence in `research.md`.
- **Refactor**: Collapse overlapping lifecycle terms from FND-009, FND-010, and FND-015 into one consistent handshake/session vocabulary so later implementation work does not preserve conflicting definitions of session creation.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for initialize success, malformed initialize, invalid initialize, unauthorized initialize, continuation after failure, and hosted verifier evidence before implementation tasks begin.
- **Green**: Produce `data-model.md`, `contracts/initialize-session-correctness-contract.md`, and `quickstart.md` that define the corrected initialize/session lifecycle, the expected failure boundaries, and the verification evidence precisely enough to drive failing tests first.
- **Refactor**: Normalize lifecycle terminology, request/response examples, verification check names, and failure categories across all design artifacts, then re-run the constitution check against the completed design.

### Phase 2 - Implementation Strategy Preview

- **Red**: Identify the failing tests implementation must add first for initialize rejection without session creation, successful initialize with one session, retry-after-failure behavior, continuation denial for non-issued sessions, and hosted verifier evidence.
- **Green**: Organize implementation around the minimum change set that makes those tests pass: gate session creation on initialize success in `cloud_run_entrypoint.py`, add any helper or protocol predicates needed to identify successful initialize outcomes safely, update hosted verifier expectations, and update tests and documentation-backed examples.
- **Refactor**: Remove duplicated lifecycle checks across request routing, tests, and verifier code, preserve the existing transport and security model, and rerun `python3 -m pytest` plus `ruff check .` after implementation changes are complete.

## User Story Delivery Strategy

### User Story 1 - Receive a Session Only After Successful Initialize

- **Red**: Add failing contract and integration tests proving malformed, invalid, or otherwise rejected initialize requests still return `MCP-Session-Id` or leave behind usable hosted session state.
- **Green**: Implement the minimum initialize gating changes needed so only successful initialize responses issue `MCP-Session-Id` and create session state.
- **Refactor**: Consolidate the initialize success predicate so response handling, header emission, and session-store writes all derive from one rule, then rerun `python3 -m pytest`.

### User Story 2 - Trust Hosted Session Lifecycle State

- **Red**: Add failing integration and verifier-flow tests proving continuation can still occur after a failed initialize or that retry-after-failure behavior reuses invalid prior state.
- **Green**: Implement the minimum lifecycle changes needed so continuation recognizes only sessions issued from successful initialize responses and later successful retries create fresh valid state.
- **Refactor**: Simplify session-lifecycle checks to the smallest maintainable boundary, keep invalid-session outcomes distinct from tool failures, and rerun `python3 -m pytest`.

### User Story 3 - Verify and Document Handshake Rules Consistently

- **Red**: Add failing verifier and documentation-backed checks proving hosted verification does not yet assert “no session on failed initialize” or that the published initialize guidance is incomplete.
- **Green**: Update the hosted verification flow, contract doc, and quickstart evidence so the corrected initialize/session lifecycle is documented and proven end to end.
- **Refactor**: Remove duplicated lifecycle wording across contracts, quickstart, verifier output, and tests, then rerun `python3 -m pytest`.

## Coverage Strategy

- Unit coverage should validate initialize-request parsing and any helper used to determine whether a response represents successful initialize completion.
- Contract coverage should lock the public rule that successful initialize issues `MCP-Session-Id`, while failing initialize paths do not issue headers or continuation state.
- Integration coverage should verify malformed initialize, invalid initialize, successful initialize, retry-after-failure, follow-up POST continuation, and invalid-session continuation behavior through the hosted `/mcp` route.
- Regression coverage should preserve authentication gating, origin handling, protocol-version validation, durable session continuation across instances, baseline tool flows, and verifier ordering outside the intentional initialize/session change.
- The full repository verification commands required before completion are `python3 -m pytest` and `ruff check .`.

## Rollback and Mitigation

- Keep FND-024 scoped to initialize/session gating, verification checks, and lifecycle documentation so operators can roll back by redeploying the prior revision if session-establishment behavior regresses for hosted consumers.
- Preserve stable invalid-session and security failure categories so rollout failures can be distinguished from broader protocol, transport, or authentication regressions.
- If implementation reveals multiple call sites deciding session issuance independently, consolidate that decision behind one helper so rollback or follow-up fixes remain localized.

## Observability, Security, and Simplicity

- Observability: hosted logs and verification evidence should make it obvious whether an initialize request was rejected before session issuance, succeeded and created a session, or failed later at continuation time.
- Security: preserve existing authentication and origin checks before session creation, keep rejected initialize paths free of reusable session identifiers, and avoid leaking session-store internals in failure payloads or verifier artifacts.
- Simplicity: prefer one session-creation gate in the existing hosted request executor rather than adding secondary handshake states, compensating cleanup, or post-failure session invalidation logic.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design artifacts update the external initialize/session contract, keep the lifecycle correction inside the current hosted request and verifier seams, and preserve the existing security and transport model. The required full-suite completion commands remain `python3 -m pytest` and `ruff check .`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
