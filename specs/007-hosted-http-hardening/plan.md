# Implementation Plan: FND-007 Hosted Probe Semantics + HTTP Hardening

**Branch**: `007-hosted-http-hardening` | **Date**: 2026-03-15 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/007-hosted-http-hardening/spec.md)
**Input**: Feature specification from `/specs/007-hosted-http-hardening/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-007 by hardening the hosted HTTP boundary so `/healthz`,
`/readyz`, `/mcp`, and unsupported paths use deterministic transport-level
status codes, consistent JSON response handling, and stable error semantics for
operators and MCP clients. Execution will follow Red-Green-Refactor: start with
failing contract and integration coverage for readiness status behavior,
malformed or unsupported hosted requests, and route classification; add the
minimum shared hosted response-mapping behavior needed to pass; then refactor
route/status selection into reusable transport helpers with full regression
coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard-library HTTP server for hosted entrypoint plus in-repo MCP transport, protocol, health, config, and observability modules  
**Storage**: In-memory runtime state only; no persistent storage for this feature  
**Testing**: Python unittest suites across `tests/unit`, `tests/integration`, and `tests/contract`, plus deployed verification evidence for hosted endpoint behavior  
**Target Platform**: Linux container deployed to Google Cloud Run  
**Project Type**: MCP web-service with hosted HTTP endpoints and contract-driven verification artifacts  
**Performance Goals**: Hosted `/healthz` and `/readyz` remain lightweight for probe use; `/readyz` status semantics are accurate in 100% of ready and not-ready verification runs; supported MCP smoke requests preserve existing successful behavior under hosted transport  
**Constraints**: Preserve existing MCP payload contracts; do not expose stack traces or secrets in hosted errors; keep local and deployed route behavior aligned; use explicit Red-Green-Refactor sequencing for all work; avoid widening scope beyond `/healthz`, `/readyz`, `/mcp`, and unsupported-path handling  
**Scale/Scope**: One hosted service surface with three supported routes and one shared set of transport rules for success, readiness failure, malformed requests, unsupported methods, unsupported media types, and unknown paths

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
- External hosted behavior changes are defined in
  `/specs/007-hosted-http-hardening/contracts/hosted-http-contract.md` and kept
  limited to route semantics rather than protocol redesign.
- Red-Green-Refactor sequencing is captured in `research.md` and execution
  steps are documented in `quickstart.md`.
- Security and simplicity constraints are addressed by preserving sanitized
  error payloads, keeping readiness/liveness payloads lightweight, and
  centralizing status selection instead of adding per-route branching.

Post-design re-check: PASS (research, data model, contracts, and quickstart
resolve planning questions without violating constitution gates).

## Project Structure

### Documentation (this feature)

```text
specs/007-hosted-http-hardening/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hosted-http-contract.md
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
│   ├── test_mcp_request_flow.py
│   ├── test_readiness_flow.py
│   └── test_request_observability.py
└── unit/
    ├── test_cloud_run_config.py
    ├── test_envelope_contract.py
    ├── test_health_readiness_transport.py
    ├── test_invoke_error_mapping.py
    ├── test_method_routing.py
    ├── test_readiness_state.py
    └── test_request_context.py
```

**Structure Decision**: Keep the existing single-service Python layout and
implement hosted HTTP hardening in the current entrypoint and transport modules,
with contract and verification updates in the existing `tests/` and `specs/`
directories rather than introducing a separate HTTP adapter layer.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
