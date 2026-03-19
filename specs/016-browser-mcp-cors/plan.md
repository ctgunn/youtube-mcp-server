# Implementation Plan: Browser-Originated MCP Access + CORS Support

**Branch**: `016-browser-mcp-cors` | **Date**: 2026-03-18 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/016-browser-mcp-cors/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/016-browser-mcp-cors/spec.md)
**Input**: Feature specification from `/specs/016-browser-mcp-cors/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add an explicit browser-originated hosted MCP contract on top of the existing remote security model so approved browser clients can complete preflight and actual requests, while denied origins and unsupported browser request patterns fail predictably. The plan keeps the current Python hosted MCP service and auth model intact, adds deliberate browser preflight and response-header behavior for documented routes, and proves the result through Red-Green-Refactor coverage across unit, contract, integration, and hosted verification flows.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, Python standard library JSON/HTTP/config/logging modules  
**Storage**: In-memory runtime state for request handling plus existing runtime configuration from environment variables; no new persistent storage required for browser access policy in this slice  
**Testing**: `pytest` across existing unit, contract, and integration suites plus hosted verification flows  
**Target Platform**: Local development and Google Cloud Run hosted Linux runtime serving remote MCP clients  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve PRD hosted latency expectations while keeping browser preflight handling lightweight enough that approved browser flows do not materially degrade existing non-browser MCP request latency  
**Constraints**: Preserve MCP transport and protocol behavior from FND-009 and FND-010, preserve auth and origin hardening from FND-013, keep originless non-browser clients working where already supported, avoid introducing implicit browser access, and keep denial behavior safe and observable  
**Scale/Scope**: One hosted MCP service with explicit browser support for documented hosted routes, stable denial behavior for unsupported origins and request patterns, and verification coverage for both approved and denied browser-originated access

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with full regression test re-run
- [x] Integration and regression coverage strategy is documented
- [x] Observability, security, and simplicity constraints are addressed

## Project Structure

### Documentation (this feature)

```text
specs/016-browser-mcp-cors/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── hosted-browser-mcp-contract.md
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
    ├── observability.py
    ├── security.py
    ├── protocol/
    │   ├── envelope.py
    │   └── methods.py
    ├── tools/
    │   ├── dispatcher.py
    │   └── retrieval.py
    └── transport/
        ├── http.py
        ├── session_store.py
        └── streaming.py

tests/
├── contract/
├── integration/
└── unit/

scripts/
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Extend the existing single-package Python service under `src/mcp_server` by adding browser-specific hosted transport behavior in the request entrypoint and shared transport/security helpers, while preserving the current `tests/unit`, `tests/contract`, and `tests/integration` layout for Red-Green-Refactor coverage and keeping hosted verification logic in the existing deployment and verification flow.

## Phase 0: Research and Decision Closure

### Research Focus

- Define the minimal browser-originated access model that layers explicit CORS behavior onto the existing origin and auth gate.
- Decide which hosted routes and methods should participate in browser preflight and response-header behavior.
- Decide the stable response behavior for approved origins, denied origins, unsupported browser request patterns, and originless non-browser clients.
- Decide which response headers must be present on preflight and actual responses for the documented browser access model.
- Define observability and verification expectations so browser support is explicit rather than inferred.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the existing hosted security and transport behavior against the FND-016 spec to identify missing preflight handling, missing browser-facing response headers, and ambiguous denial behavior.
- **Green**: Resolve each browser-access decision in `research.md`, including route scope, approval rules, header behavior, denial mapping, and verification expectations, leaving no unresolved clarifications.
- **Refactor**: Collapse overlapping browser-policy decisions into one minimal hosted browser-access contract that extends the existing security model without introducing duplicate rule paths.

### Research Outputs

- `research.md` with final decisions for browser route scope, preflight behavior, response headers, denied-origin handling, observability, and verification.

## Phase 1: Design and Contracts

### Design Focus

- Model the browser-origin policy, preflight evaluation, response-header policy, denial outcomes, and verification evidence entities needed by FND-016.
- Define the external hosted contract for browser preflight, approved-origin responses, denied-origin behavior, unsupported browser request patterns, and interaction with existing authentication/session rules.
- Provide a concrete quickstart that demonstrates Red-Green-Refactor checks, local browser-style verification, and hosted verification updates for approved and denied browser access.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing contract and design expectations for browser preflight, approved-origin response headers, denied-origin failures, and hosted verification evidence before implementation tasks begin.
- **Green**: Produce `data-model.md`, `contracts/hosted-browser-mcp-contract.md`, and `quickstart.md` with the minimum design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contract, and quickstart; confirm the design preserves the existing auth and protocol boundaries; and re-check that browser support remains the smallest change that satisfies the spec.

### Design Outputs

- `data-model.md`
- `contracts/hosted-browser-mcp-contract.md`
- `quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Complete Allowed Browser Requests

- **Red**: Add failing unit, contract, and integration tests proving approved browser origins can complete preflight and receive the documented response headers on supported hosted MCP requests without breaking the current auth flow.
- **Green**: Implement the minimum hosted browser-preflight and response-header behavior needed for documented routes and methods while preserving current MCP request handling and authentication requirements.
- **Refactor**: Consolidate browser-header generation and approval decisions, remove duplicate route-specific browser logic, and rerun the targeted plus regression suites.

### User Story 2 - Deny Unsupported Browser Access Predictably

- **Red**: Add failing tests proving disallowed origins, unsupported browser methods, and unsupported browser request patterns return the documented denial behavior instead of generic or implicit failures.
- **Green**: Implement the minimum denial-path handling and documented response shaping needed to make unsupported browser access explicit and stable.
- **Refactor**: Simplify denial mapping and observability around browser-origin failures, remove duplicated decision code, and rerun security and hosted-route regression suites.

### User Story 3 - Verify Browser Access Before Release

- **Red**: Add failing contract, integration, and hosted verification checks for approved-origin preflight, approved-origin request success, denied-origin rejection, and unsupported browser patterns.
- **Green**: Implement the minimum verification and documentation updates needed to prove browser support and denial behavior before release.
- **Refactor**: Consolidate verification helpers and browser test fixtures, tighten operator-facing evidence wording, and rerun the full unit, contract, and integration suites.

### Regression Strategy

- Preserve current `/health`, `/ready`, `initialize`, `tools/list`, `tools/call`, durable-session flows, and non-browser security behavior outside the intentional browser-access changes.
- Re-run the full unit, contract, and integration suites after targeted browser-access tests pass to prove no regressions in protocol alignment, hosted security, retrieval tools, readiness, or session continuation.
- Verify that explicit browser support does not accidentally grant access to disallowed origins or weaken originless non-browser client behavior where it is already allowed.

### Rollback and Mitigation

- Keep the feature scoped to hosted browser-access policy, response headers, configuration, verification, and documentation so operators can roll back by redeploying the prior revision if a browser-specific change causes integration issues.
- Use stable browser denial behavior and observability so rollout problems can be diagnosed quickly and distinguished from generic authentication, protocol, or session failures.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with full regression test re-run
- [x] Integration and regression coverage strategy is documented
- [x] Observability, security, and simplicity constraints are addressed

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
