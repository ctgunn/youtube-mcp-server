# Implementation Plan: Retrieval Tool Contract Completeness

**Branch**: `017-retrieval-tool-contract` | **Date**: 2026-03-19 | **Spec**: [~/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/spec.md](~/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/spec.md)
**Input**: Feature specification from `/specs/017-retrieval-tool-contract/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Complete the machine-readable MCP contract for the foundational retrieval tools so `search` and `fetch` can be called from discovery output alone, with special focus on expressing the valid `fetch` identifier combinations in discovery metadata instead of leaving them to runtime-only validation. The plan keeps the current Python MCP service and hosted transport intact, tightens the retrieval schemas and documentation, and proves discovery/runtime alignment through Red-Green-Refactor coverage across unit, contract, integration, and hosted verification flows.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Uvicorn, Pydantic v2, Redis client, Python standard library JSON/HTTP/config/logging modules  
**Storage**: In-memory runtime state only for tool registry, request handling, and retrieval sample data; no new persistent storage required for this slice  
**Testing**: `pytest` across existing unit, contract, and integration suites plus hosted verification/documentation checks  
**Target Platform**: Local development and Google Cloud Run hosted Linux runtime serving MCP clients  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve existing foundation latency expectations while adding only schema, validation, and documentation work that does not materially change retrieval-tool execution cost  
**Constraints**: Preserve MCP-native discovery and invocation behavior from FND-010 and FND-011, preserve the existing protected hosted access model, avoid breaking current `search` and `fetch` success paths, and keep discovery metadata and runtime validation as one aligned contract  
**Scale/Scope**: One hosted MCP service, two retrieval tools, one contract-completeness slice focused on `tools/list`, `tools/call`, hosted examples, and regression-safe validation behavior

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
specs/017-retrieval-tool-contract/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── retrieval-tool-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    ├── app.py
    ├── cloud_run_entrypoint.py
    ├── deploy.py
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
│   └── test_deep_research_tools_contract.py
├── integration/
│   ├── test_hosted_http_routes.py
│   ├── test_mcp_request_flow.py
│   └── test_cloud_run_docs_examples.py
└── unit/
    └── test_retrieval_tools.py

scripts/
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Extend the existing single-package Python service under `src/mcp_server` by tightening retrieval-tool schemas, validation alignment, and MCP-facing documentation in the current dispatcher, retrieval, hosted route, and verification seams. Preserve the existing `tests/unit`, `tests/contract`, and `tests/integration` layout so Red-Green-Refactor coverage remains explicit at the schema, MCP contract, and hosted-flow boundaries.

## Phase 0: Research and Decision Closure

### Research Focus

- Decide how the `fetch` discovery contract should express valid identifier combinations in machine-readable form.
- Decide how to keep discovery metadata and runtime validation aligned so retrieval rules do not drift.
- Decide what examples and hosted verification evidence are needed to prove that clients can build valid retrieval calls from discovery output alone.
- Decide the minimum validation and documentation scope that closes FND-017 without broadening retrieval behavior beyond the existing tool surface.

### Planned Red-Green-Refactor Flow

- **Red**: Compare the current retrieval schemas, runtime validation rules, tests, and hosted examples against the FND-017 spec to identify where valid `fetch` shapes and failure rules are still implicit.
- **Green**: Resolve the contract-shape, alignment, and verification decisions in `research.md`, leaving no unresolved clarification points in the technical approach.
- **Refactor**: Collapse overlapping contract decisions into one minimal retrieval-contract strategy that keeps `search` and `fetch` machine-readable without adding separate parallel rule systems.

### Research Outputs

- `research.md` with final decisions for retrieval schema expression, validation alignment, example coverage, and hosted verification scope.

## Phase 1: Design and Contracts

### Design Focus

- Model the retrieval discovery contract, valid and invalid request shapes, validation outcomes, and verification evidence needed by FND-017.
- Define the external MCP contract for `tools/list`, `search`, and `fetch`, including the supported `fetch` identifier combinations and disallowed request shapes.
- Provide a concrete quickstart that demonstrates Red-Green-Refactor checks, local validation, and hosted verification driven by discovery output instead of undocumented assumptions.

### Planned Red-Green-Refactor Flow

- **Red**: Capture the failing contract and design expectations for `search` schema completeness, `fetch` combination completeness, runtime/discovery alignment, and hosted example sufficiency before implementation tasks begin.
- **Green**: Produce `data-model.md`, `contracts/retrieval-tool-contract.md`, and `quickstart.md` with the minimum design detail needed to implement those failing checks.
- **Refactor**: Remove duplicated wording across the plan, contract, and quickstart; confirm the design preserves existing MCP and hosted security boundaries; and re-check that the solution remains the smallest change that satisfies the spec.

### Design Outputs

- `data-model.md`
- `contracts/retrieval-tool-contract.md`
- `quickstart.md`

## Phase 2: Implementation Strategy

### User Story 1 - Discover a Valid Fetch Shape

- **Red**: Add failing unit, contract, and integration tests proving `tools/list` makes the supported `fetch` identifier patterns machine-readable and that clients can build valid requests for each supported pattern without guesswork.
- **Green**: Implement the minimum retrieval-schema and descriptor changes needed to publish the valid `fetch` input combinations and accept those requests consistently.
- **Refactor**: Consolidate `fetch` contract definitions so structural validation, runtime validation, and documentation derive from one coherent rule set, then rerun the targeted plus regression suites.

### User Story 2 - Trust Discovery for Search Inputs

- **Red**: Add failing tests proving `search` discovery metadata fully describes required and optional inputs, and that invalid requests fail exactly where the published contract says they should.
- **Green**: Implement the minimum schema and validation-alignment updates needed for discovery-driven `search` requests to succeed or fail predictably.
- **Refactor**: Remove duplicated search-rule wording across schema, runtime checks, and examples, then rerun the retrieval and MCP contract regression suites.

### User Story 3 - Verify Contract and Runtime Stay Aligned

- **Red**: Add failing contract, integration, and hosted verification checks proving discovery metadata, runtime validation, and hosted examples stay aligned for representative retrieval success and failure scenarios.
- **Green**: Implement the minimum documentation, verification, and evidence updates needed to prove discovery-driven retrieval calls work locally and on the hosted route.
- **Refactor**: Consolidate retrieval verification helpers and examples, tighten release-evidence wording, and rerun the full unit, contract, and integration suites.

### Regression Strategy

- Preserve current `initialize`, `tools/list`, `tools/call`, `/health`, `/ready`, hosted auth, browser-access behavior, and durable-session behavior outside the intentional retrieval-contract changes.
- Re-run the full unit, contract, and integration suites after targeted retrieval-contract tests pass to prove no regressions in protocol alignment, hosted access, or deep-research retrieval behavior.
- Verify that supported existing `fetch` success paths continue to work for `resourceId`, `uri`, and matching combined identifiers while invalid combinations remain rejected predictably.

### Rollback and Mitigation

- Keep the feature scoped to retrieval schemas, runtime validation alignment, MCP discovery output, examples, and verification so operators can roll back by redeploying the prior revision if a contract-tightening change causes client issues.
- Preserve stable structured errors and hosted verification evidence so any rollout issue can be distinguished quickly from broader protocol, authentication, or session failures.

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
