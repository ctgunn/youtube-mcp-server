# Implementation Plan: FND-008 Deployment Execution + Cloud Run Observability

**Branch**: `008-deployment-cloud-observability` | **Date**: 2026-03-15 | **Spec**: [~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/spec.md](~/Projects/youtube-mcp-server/specs/008-deployment-cloud-observability/spec.md)
**Input**: Feature specification from `/specs/008-deployment-cloud-observability/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement FND-008 by turning the existing Cloud Run deployment helper from a
command renderer into an executable operator workflow, capturing the deployed
revision metadata needed for verification, and emitting hosted request logs in
structured runtime output that platform logging can ingest directly. Execution
follows mandatory Red-Green-Refactor sequencing: start with failing tests for
deployment execution, deployment-result capture, and hosted stdout/stderr log
emission; add the minimum workflow and observability changes needed to pass;
then refactor deployment-result shaping and hosted log emission behind shared
helpers with full regression coverage.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard-library HTTP server, Python standard-library subprocess and JSON tooling, in-repo MCP transport/protocol/config/observability modules  
**Storage**: In-memory runtime state only; deployment evidence and planning artifacts are file-based  
**Testing**: Python unittest suites across `tests/unit`, `tests/integration`, and `tests/contract`, plus hosted/manual verification evidence for deployment and logging behavior  
**Target Platform**: Linux container deployed to Google Cloud Run  
**Project Type**: MCP web-service with deployment automation and operational observability artifacts  
**Performance Goals**: Operators can execute deployment and capture initial evidence in 15 minutes or less excluding platform queue time; 100% of successful deploys capture revision name and hosted URL; 100% of hosted verification requests emit structured request logs  
**Constraints**: Preserve current MCP, health, and readiness response contracts; do not expose secrets in deployment output or logs; keep deployment execution limited to one hosted revision workflow; maintain deterministic machine-readable outputs; follow Red-Green-Refactor before any implementation work  
**Scale/Scope**: One deployment workflow, one deployment-result record, and one hosted request logging path for the existing foundation service surface (`/healthz`, `/readyz`, `/mcp`, and unsupported paths)

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
  `/specs/008-deployment-cloud-observability/contracts/deployment-observability-contract.md`
  and limited to deployment workflow outcome reporting and hosted runtime log
  emission rather than protocol redesign.
- Red-Green-Refactor sequencing is documented in `research.md` and operational
  execution steps are documented in `quickstart.md`.
- Security and simplicity constraints are addressed by preserving the existing
  hosted service surface, keeping deployment evidence machine-readable, and
  prohibiting secrets in workflow output or structured logs.

Post-design re-check: PASS (research, data model, contracts, and quickstart
resolve planning questions without violating constitution gates).

## Project Structure

### Documentation (this feature)

```text
specs/008-deployment-cloud-observability/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── deployment-observability-contract.md
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
        ├── __init__.py
        └── http.py

scripts/
├── deploy_cloud_run.sh
└── verify_cloud_run_foundation.py

tests/
├── contract/
│   ├── test_cloud_run_foundation_contract.py
│   ├── test_mcp_transport_contract.py
│   ├── test_operational_observability_contract.py
│   └── test_readiness_contract.py
├── integration/
│   ├── test_cloud_run_deployment_assets.py
│   ├── test_cloud_run_docs_examples.py
│   ├── test_cloud_run_verification_flow.py
│   ├── test_hosted_http_routes.py
│   ├── test_mcp_request_flow.py
│   └── test_request_observability.py
└── unit/
    ├── test_cloud_run_config.py
    ├── test_hosted_http_semantics.py
    ├── test_metrics_state.py
    ├── test_request_context.py
    └── test_runtime_config_validation.py
```

**Structure Decision**: Keep the existing single-service Python layout and add
deployment execution and hosted log-emission behavior within the current
deployment helper, hosted entrypoint, and observability modules rather than
introducing a separate deployment service or external logging adapter.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
