# Implementation Plan: Tool Registry + Dispatcher (FND-002)

**Branch**: `002-tool-registry-dispatcher` | **Date**: 2026-03-01 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/002-tool-registry-dispatcher/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/002-tool-registry-dispatcher/spec.md)
**Input**: Feature specification from `/specs/002-tool-registry-dispatcher/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-002 by introducing a formal tool registration lifecycle and a
schema-aware dispatcher that routes `tools/call` requests to registered handlers.
Execution will follow Red-Green-Refactor: first add failing tests for
registration validation, duplicate protection, and unknown-tool behavior; then
implement the minimum registry/dispatch code to pass; then refactor validation
and error-path reuse with full regression reruns.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn  
**Storage**: In-memory registry state (no persistent storage in this slice)  
**Testing**: pytest, Python unittest suites, contract and integration tests  
**Target Platform**: Linux container on Google Cloud Run
**Project Type**: MCP web-service (HTTP transport + internal registry/dispatcher)  
**Performance Goals**: p95 under 500ms for `tools/list` and `tools/call` against baseline in-memory handlers under local test conditions  
**Constraints**: Structured MCP-safe errors only; no stack traces in client payloads; tool registration must be transport-independent; mandatory Red-Green-Refactor workflow  
**Scale/Scope**: FND-002 only (tool registration and dispatch lifecycle for foundation/baseline tools), without YouTube external API integrations

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
- External behavior contracts are captured in
  `/contracts/mcp-tool-registry-dispatch-contract.md`.
- Red-Green-Refactor sequencing is explicit in `research.md` and `quickstart.md`.
- Error handling, deterministic behavior, and simplicity constraints are
  addressed without introducing new storage or deployment complexity.

Post-design re-check: PASS (all constitution gates remain satisfied after
research, data model, contracts, and quickstart generation).

## Project Structure

### Documentation (this feature)

```text
specs/002-tool-registry-dispatcher/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-tool-registry-dispatch-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
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
│   └── test_mcp_transport_contract.py
├── integration/
│   └── test_mcp_request_flow.py
└── unit/
    ├── test_envelope_contract.py
    ├── test_initialize_method.py
    ├── test_invoke_error_mapping.py
    ├── test_list_tools_method.py
    └── test_method_routing.py
```

**Structure Decision**: Continue with the existing single-service Python layout.
FND-002 scopes changes to protocol routing and `tools/dispatcher.py` while
keeping transport boundaries stable and external contract behavior explicit.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
