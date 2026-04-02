# Implementation Plan: Baseline Server Tools (FND-003)

**Branch**: `003-baseline-server-tools` | **Date**: 2026-03-02 | **Spec**: [~/Projects/youtube-mcp-server/specs/003-baseline-server-tools/spec.md](~/Projects/youtube-mcp-server/specs/003-baseline-server-tools/spec.md)
**Input**: Feature specification from `/specs/003-baseline-server-tools/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-003 by adding three baseline non-YouTube tools (`server_ping`,
`server_info`, `server_list_tools`) to the existing registry/dispatcher flow,
with no transport changes. Execution follows Red-Green-Refactor: add failing
unit/integration/contract tests for listing and invocation behavior, implement
only the minimum handler and registration changes required to pass, then
refactor shared metadata and response helpers with full regression reruns.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn  
**Storage**: In-memory runtime state only (tool registry and runtime metadata)  
**Testing**: Python unittest discovery suites across `tests/unit`, `tests/integration`, and `tests/contract`  
**Target Platform**: Linux container on Google Cloud Run
**Project Type**: MCP web-service (HTTP transport + protocol router + tool dispatcher)  
**Performance Goals**: Baseline smoke tool invocation responses return in under 1 second p95 in local and foundation deployment smoke checks  
**Constraints**: No external API dependencies; preserve standardized MCP response/error envelope; no stack traces in client-visible errors; strict Red-Green-Refactor execution  
**Scale/Scope**: FND-003 only; add baseline tools and contracts for operator smoke verification without changing handshake or transport surface

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
- External behavior changes are captured in
  `/contracts/mcp-baseline-server-tools-contract.md`.
- Red-Green-Refactor workflow is explicitly captured in `research.md` and
  operationalized in `quickstart.md`.
- Scope remains simple and bounded to in-process baseline handlers, with no new
  external integrations or storage complexity.

Post-design re-check: PASS (all constitution gates remain satisfied after
research, data model, contracts, and quickstart generation).

## Project Structure

### Documentation (this feature)

```text
specs/003-baseline-server-tools/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-baseline-server-tools-contract.md
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
    ├── test_method_routing.py
    └── test_tool_registry.py
```

**Structure Decision**: Keep the existing single-service Python structure.
FND-003 changes are confined to tool registration/handlers and related tests,
while preserving transport and routing boundaries established in FND-001/FND-002.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
