# Implementation Plan: Config + Secrets + Startup Validation (FND-004)

**Branch**: `004-config-secrets-startup-validation` | **Date**: 2026-03-03 | **Spec**: [~/Projects/youtube-mcp-server/specs/004-config-secrets-startup-validation/spec.md](~/Projects/youtube-mcp-server/specs/004-config-secrets-startup-validation/spec.md)
**Input**: Feature specification from `/specs/004-config-secrets-startup-validation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-004 by introducing centralized runtime configuration and secret
validation at startup, deterministic `dev/staging/prod` profile handling, and
readiness behavior that reports configuration validity without leaking
sensitive values. Execution follows Red-Green-Refactor: write failing tests for
startup validation and readiness gating, implement minimum validation/profile
logic to pass those tests, then refactor validation reuse and error hygiene
with full regression coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn  
**Storage**: In-memory runtime configuration state only (no persistent storage in this slice)  
**Testing**: Python unittest discovery suites across `tests/unit`, `tests/integration`, and `tests/contract`  
**Target Platform**: Linux container on Google Cloud Run
**Project Type**: MCP web-service (HTTP transport + protocol router + tool dispatcher)  
**Performance Goals**: Configuration validation completes during startup in under 2 seconds for normal boot paths; readiness checks return in under 200ms p95 under local baseline load  
**Constraints**: Fail-fast boot on invalid required config; deterministic `dev/staging/prod` profile behavior; no secret values in logs or client-visible errors; mandatory Red-Green-Refactor workflow  
**Scale/Scope**: FND-004 only; startup config and readiness semantics without introducing YouTube tool implementations

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
- External runtime behavior changes are captured in
  `/contracts/runtime-config-readiness-contract.md`.
- Explicit Red-Green-Refactor sequencing is defined in `research.md` and
  operationalized in `quickstart.md`.
- Observability/security constraints are satisfied by explicit secret redaction
  requirements and readiness diagnostics with non-sensitive error detail.

Post-design re-check: PASS (all constitution gates remain satisfied after
research, data model, contracts, and quickstart generation).

## Project Structure

### Documentation (this feature)

```text
specs/004-config-secrets-startup-validation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── runtime-config-readiness-contract.md
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
    ├── test_baseline_server_tools.py
    ├── test_envelope_contract.py
    ├── test_initialize_method.py
    ├── test_invoke_error_mapping.py
    ├── test_list_tools_method.py
    ├── test_method_routing.py
    ├── test_tool_registry.py
    └── test_tool_registry_duplicates.py

requirements/
├── PRD.md
└── spec-kit-seed.md

specs/004-config-secrets-startup-validation/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── runtime-config-readiness-contract.md
```

**Structure Decision**: Keep the existing single-service Python structure.
FND-004 changes are scoped to centralized config validation and readiness
reporting boundaries while preserving current transport/protocol layout.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Status

- 2026-03-03: FND-004 implementation completed for startup validation, profile enforcement, and readiness behavior.
- Added runtime config and health modules plus startup wiring in app/transport layers.
- Added unit/integration/contract coverage for config validation, profile matrix, readiness responses, and redaction guarantees.
- Regression evidence captured in `quickstart.md` with all suites passing.
