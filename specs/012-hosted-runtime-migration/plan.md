# Implementation Plan: FND-012 Hosted Runtime Migration for Streaming MCP

**Branch**: `012-hosted-runtime-migration` | **Date**: 2026-03-16 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/012-hosted-runtime-migration/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/012-hosted-runtime-migration/spec.md)
**Input**: Feature specification from `/specs/012-hosted-runtime-migration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-012 by migrating the hosted Cloud Run entrypoint from the current
standard-library `http.server` runtime to an ASGI-based runtime that can handle
streaming MCP traffic more reliably while preserving the existing `/mcp`,
`/health`, and `/ready` contract. Execution follows mandatory
Red-Green-Refactor: start with failing unit, contract, and integration tests
that codify runtime, readiness, and verification expectations; introduce the
minimum runtime, startup, and deployment changes needed to satisfy those tests;
then consolidate runtime lifecycle and request-bridging logic and rerun full
regression coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, existing in-repo MCP transport/protocol/config/observability modules, current streamable transport session helpers  
**Storage**: In-memory runtime state only for tool registry, request context, readiness state, and MCP streaming sessions; planning artifacts are file-based  
**Testing**: Python `unittest` suites across `tests/unit`, `tests/integration`, and `tests/contract`, plus local/manual and hosted/manual verification flows  
**Target Platform**: Linux container deployed to Google Cloud Run  
**Project Type**: Python MCP web-service with hosted HTTP and SSE transport  
**Performance Goals**: 100% of covered hosted MCP smoke flows complete without runtime-related transport failures; 100% of readiness and liveness transition checks remain correct; concurrent-session verification demonstrates correct isolation across at least 20 simultaneous client runs  
**Constraints**: Preserve the `/mcp`, `/health`, and `/ready` routes; keep the FND-009/FND-010/FND-011 transport and protocol contract stable; avoid exposing secrets or stack traces; keep one hosted service entrypoint per environment; follow Red-Green-Refactor before implementation; maintain a documented rollback path to the prior runtime command until deployment verification passes  
**Scale/Scope**: One hosted service, one Cloud Run container image, one runtime migration slice covering the hosted entrypoint, lifecycle handling, deployment/startup assets, verification flow, and regression coverage for MCP and operational routes

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
- External behavior changes are defined in
  `/specs/012-hosted-runtime-migration/contracts/hosted-runtime-migration-contract.md`
  and focus on runtime continuity, operational route behavior, and local/hosted
  verification of the existing MCP surface.
- Red-Green-Refactor sequencing is documented in `research.md` and turned into
  execution steps in `quickstart.md`.
- Observability, security, and simplicity constraints are addressed by keeping
  the current hosted route contract intact, reusing the existing request
  handling boundary where possible, preserving structured logging/readiness
  behavior, and limiting scope to runtime migration rather than broader MCP
  feature expansion.

Post-design re-check: PASS (research, data model, contract, and quickstart
resolve the runtime migration decisions without constitution violations).

## Project Structure

### Documentation (this feature)

```text
specs/012-hosted-runtime-migration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hosted-runtime-migration-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── deploy.py
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
        ├── streaming.py
        └── __init__.py

scripts/
├── deploy_cloud_run.sh
└── verify_cloud_run_foundation.py

tests/
├── contract/
│   ├── test_mcp_transport_contract.py
│   ├── test_streamable_http_contract.py
│   ├── test_cloud_run_foundation_contract.py
│   ├── test_operational_observability_contract.py
│   └── test_readiness_contract.py
├── integration/
│   ├── test_streamable_http_transport.py
│   ├── test_hosted_http_routes.py
│   ├── test_cloud_run_verification_flow.py
│   ├── test_request_observability.py
│   └── test_readiness_flow.py
└── unit/
    ├── test_streamable_http_transport.py
    ├── test_hosted_http_semantics.py
    ├── test_readiness_state.py
    ├── test_runtime_profiles.py
    └── test_cloud_run_config.py

Dockerfile
README.md
```

**Structure Decision**: Keep the existing single-service Python layout and
migrate the hosted runtime in place. FND-012 changes the serving stack,
container start command, and runtime lifecycle around the current MCP endpoint,
so the correct structure is to evolve `src/mcp_server/cloud_run_entrypoint.py`,
the runtime/deployment files, and the existing test layers rather than add a
second gateway or separate deployment service.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
