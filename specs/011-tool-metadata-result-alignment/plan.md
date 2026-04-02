# Implementation Plan: FND-011 Tool Metadata + Invocation Result Alignment

**Branch**: `011-tool-metadata-result-alignment` | **Date**: 2026-03-16 | **Spec**: [~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/spec.md](~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/spec.md)
**Input**: Feature specification from `/specs/011-tool-metadata-result-alignment/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-011 by expanding the tool registry and invocation boundary so
`tools/list` returns complete MCP-facing tool metadata, baseline tools expose
usable input schemas during discovery, and successful tool calls return
MCP-compatible content structures that preserve tool meaning without relying on
the current simplified text-only wrapper. Execution follows mandatory
Red-Green-Refactor: first add failing unit, contract, and integration tests for
tool metadata completeness and result alignment; then introduce the minimum
registry, protocol, and baseline-tool changes needed to satisfy that contract;
then remove duplicated shaping logic and rerun full regression coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard-library HTTP server and JSON tooling, in-repo MCP transport/protocol/config/observability modules, in-repo tool registry and dispatcher modules, MCP-native protocol contract from FND-010  
**Storage**: In-memory runtime state only for tool registry, request context, and hosted transport sessions; planning artifacts are file-based  
**Testing**: Python `unittest` suites across `tests/unit`, `tests/integration`, and `tests/contract`, plus local/manual MCP verification flows  
**Target Platform**: Linux container deployed to Google Cloud Run  
**Project Type**: Python MCP web-service with hosted streamable HTTP transport  
**Performance Goals**: 100% of registered baseline tools expose complete discovery metadata in covered tests; 100% of covered successful baseline tool invocations return aligned MCP content structures; no regressions in existing initialize, discovery, invocation, readiness, or hosted-route contract suites  
**Constraints**: Preserve the single `/mcp` endpoint and FND-010 protocol-native request/error behavior; keep baseline tools discoverable and callable; do not expose internal stack traces or secret values; follow Red-Green-Refactor before implementation; keep the registry extensible for later YouTube tools without adding new user-facing tools in this slice  
**Scale/Scope**: One hosted MCP endpoint, three baseline tools, registry discovery metadata, successful invocation result shaping, and regression coverage for local and hosted MCP flows

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
  `/specs/011-tool-metadata-result-alignment/contracts/tool-metadata-contract.md`
  and narrows scope to discovery metadata and successful tool result content on
  top of the FND-010 protocol contract.
- Red-Green-Refactor sequencing is documented in `research.md` and turned into
  execution steps in `quickstart.md`.
- Observability, security, and simplicity constraints are addressed by keeping
  the existing `/mcp` endpoint and hosted transport, rejecting incomplete tool
  definitions before they surface to clients, and limiting this slice to
  registry/result alignment instead of broader tool expansion.

Post-design re-check: PASS (research, data model, contract, and quickstart
resolve planning questions without violating constitution gates).

## Project Structure

### Documentation (this feature)

```text
specs/011-tool-metadata-result-alignment/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── tool-metadata-contract.md
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
│   └── test_cloud_run_foundation_contract.py
├── integration/
│   ├── test_mcp_request_flow.py
│   ├── test_hosted_http_routes.py
│   └── test_streamable_http_transport.py
└── unit/
    ├── test_baseline_server_tools.py
    ├── test_list_tools_method.py
    ├── test_tool_registry.py
    ├── test_tool_registry_duplicates.py
    └── test_invoke_error_mapping.py
```

**Structure Decision**: Keep the existing single-service Python layout and
update the current registry, protocol, and baseline-tool modules in place.
FND-011 changes the MCP-facing contract for discovery and successful tool
results inside the existing server, so the correct structure is to evolve
`src/mcp_server/tools/dispatcher.py`, `src/mcp_server/protocol/methods.py`,
and the current `tests/` layers rather than introduce new services or a second
tool registry path.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
