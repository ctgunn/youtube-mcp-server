# Implementation Plan: Deep Research Tool Foundation

**Branch**: `014-deep-research-tools` | **Date**: 2026-03-17 | **Spec**: [~/Projects/youtube-mcp-server/specs/014-deep-research-tools/spec.md](~/Projects/youtube-mcp-server/specs/014-deep-research-tools/spec.md)
**Input**: Feature specification from `/specs/014-deep-research-tools/spec.md`

## Summary

Add MCP-native `search` and `fetch` tools as the retrieval foundation for deep research consumers before any YouTube-specific tool slices ship. The plan keeps the existing FastAPI-hosted MCP runtime, adds two new registry-backed tools with stateless retrieval references, documents the external MCP contract for discovery and invocation, and proves the behavior through unit, contract, integration, and hosted verification steps using explicit Red-Green-Refactor sequencing.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, Python standard library JSON/HTTP/config/logging modules  
**Storage**: In-memory runtime state only; no persistent storage for retrieval references or fetched content  
**Testing**: `pytest` driving existing unit, integration, and contract suites  
**Target Platform**: Local development and Google Cloud Run hosted Linux runtime  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve the PRD baseline of sub-3-second p95 behavior for simple discovery calls and keep representative fetch operations within the project’s existing hosted latency expectations for remote MCP consumers  
**Constraints**: Preserve MCP protocol alignment from FND-010, preserve tool metadata/result alignment from FND-011, preserve hosted security controls from FND-013, avoid persistent storage, return security-safe structured errors, and keep the design simple enough to extend later with YouTube-specific tools  
**Scale/Scope**: One hosted MCP service exposing two new foundational retrieval tools for deep research consumers, with local and hosted verification coverage and no expansion yet into the 16 YouTube domain tools

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
specs/014-deep-research-tools/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── deep-research-tools-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── observability.py
    ├── protocol/
    │   ├── envelope.py
    │   └── methods.py
    ├── security.py
    ├── tools/
    │   └── dispatcher.py
    └── transport/
        ├── http.py
        └── streaming.py

tests/
├── contract/
├── integration/
└── unit/

scripts/
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Use the existing single-package Python service under `src/mcp_server` and extend the current protocol, tool registry, and hosted verification paths rather than introducing a new service boundary. Tests remain split across `tests/unit`, `tests/integration`, and `tests/contract`, and all planning artifacts stay isolated under `specs/014-deep-research-tools`.

## Phase 0: Research and Decision Closure

### Research Focus

- Define the retrieval contract shape for `search` and `fetch` so it works for deep research consumers without introducing YouTube-specific assumptions.
- Decide how `search` results should provide stable follow-up identifiers for `fetch` in a system that has no persistent storage.
- Define result-content expectations, failure categories, and hosted verification coverage for the new tools.
- Define the smallest source-code surface and test surface needed to add the tools without disturbing established MCP transport and security behavior.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the feature spec against the current dispatcher, protocol routing, hosted verification flow, and tests to identify every missing retrieval contract, result reference rule, and verification expectation.
- **Green**: Resolve each open design choice in `research.md`, including stateless retrieval references, request/result shapes, failure handling, and hosted verification boundaries, so no `NEEDS CLARIFICATION` markers remain.
- **Refactor**: Collapse overlapping decisions into one minimal retrieval model that later YouTube slices can extend without reopening the FND-014 contract.

### Research Outputs

- `research.md` with final decisions for tool scope, stateless result references, result-content structure, failure taxonomy, observability needs, and regression boundaries.

## Phase 1: Design and Contracts

### Design Focus

- Model the request, result, fetched-content, and verification entities required for `search` and `fetch`.
- Define the external MCP contract for discovery and invocation of both tools, including representative request and success/error bodies.
- Provide a concrete quickstart that exercises Red-Green-Refactor checks, local hosted validation, and manual `search` plus `fetch` verification.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing contract and test expectations for tool discovery, stateless result references, empty-result handling, unavailable-source handling, and hosted verification examples.
- **Green**: Produce `data-model.md`, `contracts/deep-research-tools-contract.md`, and `quickstart.md` with the minimum design detail needed to implement those failing tests.
- **Refactor**: Remove duplicated design language, confirm the contract stays aligned with the constitution and prior MCP slices, and re-check that the design does not introduce unnecessary persistence or transport changes.

### Design Outputs

- `data-model.md`
- `contracts/deep-research-tools-contract.md`
- `quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Discover Relevant Sources

- **Red**: Add failing unit tests for registration and input validation, contract tests for `tools/list` discovery metadata and `tools/call` result shape, and integration tests for successful and no-result `search` flows.
- **Green**: Implement the minimum `search` tool registration, argument validation, result shaping, and discovery exposure needed to satisfy those tests.
- **Refactor**: Consolidate search-result shaping and validation helpers, eliminate duplicated descriptor logic, and rerun the relevant unit, contract, and integration suites.

### User Story 2 - Retrieve Selected Content

- **Red**: Add failing unit and integration tests for stateless fetch-reference validation, successful `fetch` responses, unavailable-source failures, and MCP-compatible result content.
- **Green**: Implement the minimum `fetch` tool behavior required to accept a search-derived reference or equivalent source identifier and return structured fetched content or stable failures.
- **Refactor**: Collapse shared retrieval-response helpers between `search` and `fetch`, keep failure mapping centralized, and rerun targeted plus regression suites.

### User Story 3 - Verify Hosted Research Readiness

- **Red**: Add failing hosted integration and contract checks that expect `search` and `fetch` to be discoverable, callable through the protected `/mcp` route, and documented in verification guidance.
- **Green**: Update hosted verification docs and examples with one successful discovery path, one successful retrieval path, and representative failure-path expectations for both tools.
- **Refactor**: Remove duplicated verification steps between docs and contracts, keep observability and security expectations consistent with FND-013, and rerun the hosted regression suite.

### Regression Strategy

- Preserve existing initialize, `tools/list`, baseline server tool, `/health`, `/ready`, and protected `/mcp` behaviors outside the intentional addition of `search` and `fetch`.
- Re-run the full unit, contract, and integration suites after the new tool behavior passes targeted tests to prove no regressions in protocol alignment, transport semantics, readiness, or security handling.
- Verify that retrieval-tool failures remain MCP-safe and do not weaken the denial boundaries added in FND-013.

### Rollback and Mitigation

- Keep FND-014 scoped to registry definitions, retrieval-tool execution paths, and hosted verification artifacts so operators can roll back by redeploying the prior revision if the new tools cause integration issues.
- Use stable structured error categories and hosted verification evidence so failures during rollout can be diagnosed without ambiguous tool behavior.

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
