# Implementation Plan: FND-006 Cloud Run Foundation Deployment

**Branch**: `006-cloud-run-foundation` | **Date**: 2026-03-13 | **Spec**: [~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/spec.md](~/Projects/youtube-mcp-server/specs/006-cloud-run-foundation/spec.md)
**Input**: Feature specification from `/specs/006-cloud-run-foundation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-006 by defining a reproducible hosted deployment path for the
existing MCP foundation service, capturing the runtime inputs and revision
settings required for a successful launch, and adding a post-deploy verification
flow that proves liveness, readiness, initialize, list-tools, and baseline tool
invocation against the hosted endpoint. Execution follows mandatory
Red-Green-Refactor sequencing: start with failing contract/integration coverage
for deployment artifacts and hosted verification helpers, add the minimum
deployment packaging and verification behavior needed to pass, then refactor the
deployment instructions and verification utilities into a single maintainable
workflow with full regression coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn  
**Storage**: In-memory runtime state only; deployment artifacts are file-based documentation and packaging assets  
**Testing**: Python unittest discovery suites across `tests/unit`, `tests/integration`, and `tests/contract` plus hosted/manual verification evidence for deployment acceptance  
**Target Platform**: Linux container deployed to Google Cloud Run  
**Project Type**: MCP web-service with deployment packaging and operational verification artifacts  
**Performance Goals**: Hosted revision can be deployed by an operator in 15 minutes or less excluding platform queue time; deployed `/healthz` and `/readyz` remain fast and accurate; hosted MCP baseline verification succeeds on first attempt in at least 95% of valid runs  
**Constraints**: Preserve existing MCP contracts and baseline tool behavior; keep secrets out of source control and operator-visible logs; require explicit revision settings and post-deploy evidence; mandatory Red-Green-Refactor sequencing for deployment and verification work  
**Scale/Scope**: One reproducible foundation deployment path for a single hosted revision with verification coverage for health/readiness and minimum MCP round-trip

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
  `/specs/006-cloud-run-foundation/contracts/cloud-run-foundation-contract.md`
  and limited to deployment-time and hosted verification expectations.
- Red-Green-Refactor sequencing is documented in `research.md` and operational
  execution steps are documented in `quickstart.md`.
- Security and simplicity are preserved by keeping runtime state unchanged,
  constraining new work to deployment packaging, configuration surfaces, and
  hosted verification evidence.

Post-design re-check: PASS (research, data model, contracts, and quickstart
resolve the planning unknowns without violating constitution gates).

## Project Structure

### Documentation (this feature)

```text
specs/006-cloud-run-foundation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cloud-run-foundation-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
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
│   ├── test_mcp_request_flow.py
│   ├── test_profile_startup_matrix.py
│   ├── test_readiness_flow.py
│   ├── test_request_observability.py
│   └── test_startup_config_validation_flow.py
└── unit/
    ├── test_baseline_server_tools.py
    ├── test_envelope_contract.py
    ├── test_initialize_method.py
    ├── test_invoke_error_mapping.py
    ├── test_list_tools_method.py
    ├── test_method_routing.py
    ├── test_metrics_state.py
    ├── test_readiness_state.py
    ├── test_request_context.py
    ├── test_runtime_config_validation.py
    ├── test_runtime_profiles.py
    ├── test_tool_registry.py
    └── test_tool_registry_duplicates.py

.env.example
README.md
```

**Structure Decision**: Keep the existing single-service Python layout and add
deployment packaging, deployment documentation, and hosted verification support
around the current service entrypoint rather than introducing a separate deploy
application or additional runtime layer.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
