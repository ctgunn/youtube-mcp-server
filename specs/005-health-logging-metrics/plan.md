# Implementation Plan: FND-005 Health, Logging, Error Model, Metrics

**Branch**: `005-health-logging-metrics` | **Date**: 2026-03-05 | **Spec**: [~/Projects/youtube-mcp-server/specs/005-health-logging-metrics/spec.md](~/Projects/youtube-mcp-server/specs/005-health-logging-metrics/spec.md)
**Input**: Feature specification from `/specs/005-health-logging-metrics/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-005 by ensuring operational health/readiness behavior remains
explicit and probe-friendly while adding request-scoped structured logs,
normalized client error semantics, and core request metrics (counts and latency
percentile-capable observations). Execution follows constitution-mandated
Red-Green-Refactor: introduce failing tests for health/error/logging/metrics
contracts, add the minimum instrumentation and normalization needed to pass,
then refactor shared request context and observability helpers with full
regression verification.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn  
**Storage**: In-memory runtime state only (tool registry, request context, metric aggregates)  
**Testing**: Python unittest discovery suites across `tests/unit`, `tests/integration`, and `tests/contract`  
**Target Platform**: Linux container on Google Cloud Run
**Project Type**: MCP web-service (HTTP transport + MCP protocol routing)  
**Performance Goals**: `/healthz` responses under 500 ms under normal conditions; request observability coverage for >=99% handled requests; metrics emitted for all exercised endpoint classes in automated tests  
**Constraints**: No stack traces or secret leakage in client-visible errors/logs; preserve MCP success envelope compatibility; add observability with minimal architectural complexity; mandatory Red-Green-Refactor sequencing  
**Scale/Scope**: FND-005 only; foundational operational behavior for health, logging, error model normalization, and core request metrics

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
- Contract updates are defined in
  `/specs/005-health-logging-metrics/contracts/operational-observability-contract.md`.
- Red-Green-Refactor sequencing is explicitly documented in `research.md` and
  operationalized in `quickstart.md`.
- Observability and security constraints are captured by mandatory structured
  logging fields, normalized error contracts, request ID correlation, and
  explicit prohibition of stack trace/secret leakage.

Post-design re-check: PASS (research, data model, contracts, and quickstart
artifacts remain constitution-compliant with no unresolved clarification gates).

## Project Structure

### Documentation (this feature)

```text
specs/005-health-logging-metrics/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── operational-observability-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── config.py
    ├── health.py
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
│   └── test_readiness_contract.py
├── integration/
│   ├── test_mcp_request_flow.py
│   ├── test_profile_startup_matrix.py
│   ├── test_readiness_flow.py
│   └── test_startup_config_validation_flow.py
└── unit/
    ├── test_envelope_contract.py
    ├── test_invoke_error_mapping.py
    ├── test_method_routing.py
    ├── test_readiness_state.py
    ├── test_runtime_config_validation.py
    ├── test_tool_registry.py
    └── test_tool_registry_duplicates.py

specs/005-health-logging-metrics/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── operational-observability-contract.md
```

**Structure Decision**: Keep the existing single-service Python layout and add
observability behavior at transport/protocol boundaries to avoid unnecessary
new modules while meeting FND-005 requirements.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
