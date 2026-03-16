# Implementation Plan: FND-009 MCP Streamable HTTP Transport

**Branch**: `009-mcp-streamable-http-transport` | **Date**: 2026-03-15 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md)
**Input**: Feature specification from `/specs/009-mcp-streamable-http-transport/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-009 by replacing the current hosted request/response-only `/mcp`
route with MCP streamable HTTP behavior on the same endpoint, adding
standards-aligned `GET` and `POST` transport handling, SSE-based streamed
delivery, and session-aware hosted verification while preserving the current
Cloud Run deployment path. Execution follows mandatory Red-Green-Refactor:
start with failing tests for streamable transport negotiation, streamed
delivery, session handling, and local/hosted parity; add the minimum hosted
transport and stream-state changes needed to pass; then refactor stream state,
event formatting, and hosted/session routing behind shared helpers with full
regression coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard-library HTTP server, Python standard-library threading and queue primitives, in-repo MCP transport/protocol/config/observability modules, MCP Streamable HTTP specification (protocol version `2025-11-25`) for transport behavior  
**Storage**: In-memory runtime state only for transport sessions, stream cursors, and event queues; planning and verification artifacts are file-based  
**Testing**: Python unittest suites across `tests/unit`, `tests/integration`, and `tests/contract`, plus local/manual and hosted/manual verification for streamable transport flows  
**Target Platform**: Linux container deployed to Google Cloud Run  
**Project Type**: MCP web-service with hosted HTTP/SSE transport behavior  
**Performance Goals**: Successful hosted transport verification establishes a session in 100% of valid runs; streamed responses preserve ordering in 100% of transport regression checks; local and hosted verification remain behaviorally aligned in at least 95% of compared scenarios  
**Constraints**: Keep one hosted MCP endpoint; preserve Cloud Run deployability; keep liveness/readiness semantics intact; avoid exposing secrets in stream or session metadata; follow Red-Green-Refactor before implementation; do not widen scope into full protocol-envelope replacement, which remains in FND-010  
**Scale/Scope**: One hosted MCP endpoint supporting streamable `GET` and `POST`, optional SSE stream resumability, session-aware request handling, and concurrent client isolation for the foundation server tools and MCP lifecycle surface

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with full regression test re-run
- [x] Integration and regression coverage strategy is documented
- [x] Observability, security, and simplicity constraints are addressed

Gate assessment notes:
- External MCP-facing behavior is defined in
  `/specs/009-mcp-streamable-http-transport/contracts/mcp-streamable-http-contract.md`
  and scoped to transport/session semantics rather than full protocol payload
  redesign.
- Red-Green-Refactor sequencing is documented in `research.md` and execution
  steps are documented in `quickstart.md`.
- Observability, security, and simplicity constraints are addressed by keeping
  one hosted endpoint, using in-memory session state only, preserving current
  health/readiness routes, and explicitly carrying forward origin/session
  validation requirements from the MCP transport specification.

Post-design re-check: PASS (research, data model, contract, and quickstart
resolve planning questions without violating constitution gates).

## Project Structure

### Documentation (this feature)

```text
specs/009-mcp-streamable-http-transport/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-streamable-http-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── health.py
    ├── observability.py
    ├── protocol/
    │   ├── envelope.py
    │   └── methods.py
    ├── tools/
    │   ├── __init__.py
    │   └── dispatcher.py
    └── transport/
        ├── __init__.py
        └── http.py

tests/
├── contract/
│   ├── test_mcp_transport_contract.py
│   ├── test_operational_observability_contract.py
│   └── test_readiness_contract.py
├── integration/
│   ├── test_cloud_run_verification_flow.py
│   ├── test_hosted_http_routes.py
│   ├── test_mcp_request_flow.py
│   └── test_request_observability.py
└── unit/
    ├── test_hosted_http_semantics.py
    ├── test_invoke_error_mapping.py
    ├── test_method_routing.py
    ├── test_request_context.py
    └── test_tool_registry.py
```

**Structure Decision**: Keep the existing single-service Python layout and add
streamable transport behavior inside the current hosted entrypoint and transport
modules, with new session/stream helpers in `src/mcp_server/transport/` and
new contract/integration coverage in the existing `tests/` tree rather than
introducing a separate gateway service before FND-012.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
