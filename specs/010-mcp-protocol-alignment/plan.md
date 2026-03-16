# Implementation Plan: FND-010 MCP Protocol Contract Alignment

**Branch**: `010-mcp-protocol-alignment` | **Date**: 2026-03-15 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/spec.md)
**Input**: Feature specification from `/specs/010-mcp-protocol-alignment/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-010 by replacing the current custom `success/data/meta/error`
MCP-like envelope with MCP-native protocol request, result, and error behavior
across initialize, tool discovery, tool invocation, and unsupported-method
flows while preserving the FND-009 streamable HTTP transport surface, baseline
tool availability, and local-versus-hosted parity. Execution follows mandatory
Red-Green-Refactor: first add failing contract, integration, and unit tests for
MCP-native payloads and lifecycle rules; then introduce the smallest protocol
adapter, error-mapping, and result-shaping changes needed to pass; then remove
legacy wrapper assumptions and rerun full regression coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard-library HTTP server and JSON tooling, in-repo MCP transport/protocol/config/observability modules, MCP Streamable HTTP transport behavior from FND-009, MCP protocol-native request/result/error semantics for hosted and local flows  
**Storage**: In-memory runtime state only for tool registry, request context, and hosted transport sessions; planning artifacts are file-based  
**Testing**: Python `unittest` suites across `tests/unit`, `tests/integration`, and `tests/contract`, plus local/manual and hosted/manual MCP verification flows  
**Target Platform**: Linux container deployed to Google Cloud Run  
**Project Type**: Python MCP web-service with hosted streamable HTTP transport  
**Performance Goals**: 100% of protocol contract tests pass in local and hosted environments; 0 covered MCP success responses retain legacy wrapper fields; local and hosted initialize/list/call behavior remains aligned in at least 95% of compared verification scenarios  
**Constraints**: Preserve the single `/mcp` endpoint and FND-009 transport semantics; do not regress baseline tools or health/readiness behavior; do not expose internal stack traces or secrets; follow Red-Green-Refactor before implementation; avoid widening scope into tool-metadata expansion reserved for FND-011  
**Scale/Scope**: One hosted MCP endpoint, initialize plus tool discovery and invocation lifecycle, protocol-native success and failure payloads, and migration of existing contract/unit/integration coverage away from the legacy wrapper

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
  `/specs/010-mcp-protocol-alignment/contracts/mcp-protocol-contract.md` and
  explicitly replaces the legacy wrapper contract from FND-001 while remaining
  compatible with the hosted transport behavior introduced in FND-009.
- Red-Green-Refactor sequencing is documented in `research.md` and turned into
  execution steps in `quickstart.md`.
- Observability, security, and simplicity constraints are addressed by keeping
  the existing hosted entrypoint, preserving health/readiness routes, requiring
  sanitized protocol errors, and limiting this slice to contract alignment
  rather than tool metadata redesign.

Post-design re-check: PASS (research, data model, contract, and quickstart
resolve planning questions without violating constitution gates).

## Project Structure

### Documentation (this feature)

```text
specs/010-mcp-protocol-alignment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-protocol-contract.md
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
        ├── http.py
        └── streaming.py

tests/
├── contract/
│   ├── test_mcp_transport_contract.py
│   ├── test_streamable_http_contract.py
│   ├── test_cloud_run_foundation_contract.py
│   └── test_operational_observability_contract.py
├── integration/
│   ├── test_mcp_request_flow.py
│   ├── test_streamable_http_transport.py
│   ├── test_hosted_http_routes.py
│   ├── test_cloud_run_verification_flow.py
│   └── test_request_observability.py
└── unit/
    ├── test_envelope_contract.py
    ├── test_initialize_method.py
    ├── test_list_tools_method.py
    ├── test_invoke_error_mapping.py
    ├── test_method_routing.py
    └── test_streamable_http_transport.py
```

**Structure Decision**: Keep the existing single-service Python layout and
update the current protocol and hosted transport modules in place. FND-010 is a
contract migration inside the existing server rather than a new service or a
new endpoint, so the correct structure is to evolve `src/mcp_server/protocol/`
and the current `tests/` layers rather than introduce parallel adapters.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
