# Implementation Plan: OpenAI Retrieval Compatibility

**Branch**: `023-openai-retrieval-compatibility` | **Date**: 2026-03-25 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/spec.md)
**Input**: Feature specification from `/specs/023-openai-retrieval-compatibility/spec.md`

## Summary

Align the foundational `search` and `fetch` MCP tools with the current OpenAI retrieval compatibility guidance for ChatGPT Apps, deep research, and company-knowledge-style integrations. The plan keeps the existing hosted FastAPI MCP service, protected `/mcp` access model, and tool names intact while changing the published retrieval contract to the OpenAI-facing shape, updating runtime validation and result shaping to match, and proving the behavior through unit, contract, integration, and hosted verification coverage with explicit Red-Green-Refactor sequencing.

Canonical terms for this feature are `OpenAI retrieval contract`, `compatibility boundary`, `discovery metadata`, `structuredContent`, `protected /mcp`, and `hosted verification evidence`.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis client, Python standard-library JSON/HTTP/config/logging tooling, existing MCP transport/protocol/tooling modules under `src/mcp_server/`  
**Storage**: In-memory runtime state only for tool registry, request handling, and retrieval sample data; no persistent storage introduced for this slice  
**Testing**: `pytest` for unit, contract, and integration suites; `ruff check .` for linting; hosted verification via `scripts/verify_cloud_run_foundation.py` and documentation-backed example checks  
**Target Platform**: Local development plus hosted Linux runtime on Google Cloud Run serving protected remote MCP traffic  
**Project Type**: Hosted MCP web service  
**Performance Goals**: Preserve existing retrieval latency expectations and hosted MCP behavior while changing only request/result contract shape, validation, and verification evidence  
**Constraints**: Keep tool names `search` and `fetch`; preserve MCP-native `tools/list` and `tools/call` behavior; preserve protected `/mcp` authentication and hosted transport expectations; keep empty `search` as a non-error outcome; avoid parallel retrieval pipelines or new endpoints; document any compatibility adapter explicitly if direct contract alignment is not used  
**Scale/Scope**: One hosted MCP service, two retrieval tools, one OpenAI-facing compatibility slice spanning discovery metadata, runtime validation, result shaping, contract tests, hosted verification, and operator documentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Pre-design gate result: PASS. FND-023 changes external MCP-facing retrieval behavior, so updated contracts are mandatory. The plan keeps the change inside the existing retrieval tools, MCP methods, and hosted verification seams rather than adding a second retrieval surface. Full-suite proof commands before completion: `pytest` and `ruff check .`.

## Project Structure

### Documentation (this feature)

```text
specs/023-openai-retrieval-compatibility/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openai-retrieval-compatibility-contract.md
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
│   ├── test_cloud_run_docs_examples.py
│   ├── test_hosted_http_routes.py
│   └── test_mcp_request_flow.py
└── unit/
    └── test_retrieval_tools.py

scripts/
└── verify_cloud_run_foundation.py
```

**Structure Decision**: Extend the existing single-package Python service under `src/mcp_server` by changing only the retrieval-tool schema, validation, result-shaping, and hosted verification surfaces already used by FND-014 and FND-017. Preserve the current `tests/unit`, `tests/contract`, and `tests/integration` layout so Red-Green-Refactor coverage stays explicit at the schema, MCP contract, and protected hosted-flow boundaries.

## Implementation Phases

### Phase 0 - Research and Contract Closure

- **Red**: Capture the current mismatch between the repository’s retrieval contract and the current OpenAI guidance by comparing `query`/`resourceId`/`uri`-based discovery and result shapes against the OpenAI-required `search` and `fetch` compatibility schema.
- **Green**: Resolve the planning decisions for OpenAI-compatible request arguments, result fields, compatibility-boundary wording, hosted verification expectations, and the decision between direct contract alignment and an explicit compatibility adapter in `research.md`.
- **Refactor**: Collapse overlapping terminology from FND-014, FND-017, and the OpenAI guidance into one consistent design vocabulary so later implementation work does not maintain separate definitions of the retrieval contract.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for OpenAI-compatible `tools/list` metadata, `tools/call` request shapes, result bodies, and hosted verification examples before implementation tasks begin.
- **Green**: Produce `data-model.md`, `contracts/openai-retrieval-compatibility-contract.md`, and `quickstart.md` that define the OpenAI-facing retrieval contract, compatibility boundary, verification evidence, and implementation touchpoints precisely enough to drive failing tests first.
- **Refactor**: Normalize contract terms, example payloads, and verification check names across all design artifacts, then re-run the constitution check against the completed design.

### Phase 2 - Implementation Strategy Preview

- **Red**: Identify the failing tests that implementation must add first for schema publication, runtime validation, result-shape alignment, hosted verification evidence, and backward-compatibility failure behavior.
- **Green**: Organize implementation around the minimum change set that makes those tests pass: update retrieval schema and handlers, update descriptor publication and any MCP result shaping required by the new contract, update tests, and update hosted verification/docs examples.
- **Refactor**: Remove duplicated contract definitions across code, tests, and docs, preserve existing transport/security behavior, and rerun `pytest` plus `ruff check .` after the implementation changes are complete.

## User Story Delivery Strategy

### User Story 1 - Use OpenAI-Compatible Retrieval Calls

- **Red**: Add failing unit, contract, and integration tests proving `search` and `fetch` discovery and invocation still expose the repo-specific retrieval contract instead of the current OpenAI-compatible shape.
- **Green**: Implement the minimum schema, validation, and result-shaping changes required for `search` and `fetch` to accept the supported OpenAI-compatible inputs and return the documented OpenAI-compatible outputs.
- **Refactor**: Consolidate retrieval-contract constants and error mapping so the OpenAI-facing behavior is described once and reused consistently, then rerun `pytest`.

### User Story 2 - Follow OpenAI-Specific Examples Reliably

- **Red**: Add failing documentation, docs-example, and hosted verification checks proving current examples do not show the supported OpenAI-specific retrieval flow.
- **Green**: Update quickstart, contract examples, and hosted verification behavior so discovery plus one valid `search` and one valid `fetch` flow can be executed exactly as documented.
- **Refactor**: Remove duplicate example payloads and check naming drift across contracts, quickstart, verifier output, and docs-example tests, then rerun `pytest`.

### User Story 3 - Preserve Clarity Around Compatibility Boundaries

- **Red**: Add failing contract and regression checks proving the service either silently preserves the old retrieval shape or leaves the compatibility boundary undocumented.
- **Green**: Implement the minimum compatibility-boundary behavior and documentation needed so non-OpenAI or legacy retrieval shapes either adapt through a documented path or fail predictably with stable structured errors.
- **Refactor**: Simplify compatibility logic to the smallest maintainable boundary, remove unnecessary dual-shape handling if direct alignment is sufficient, and rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate OpenAI-compatible request validation, legacy-shape rejection or adaptation behavior, empty-search success handling, and fetch lookup/result-shaping helpers.
- Contract coverage should lock the OpenAI-facing `tools/list`, `search`, and `fetch` behavior documented in `contracts/openai-retrieval-compatibility-contract.md`.
- Integration coverage should verify the protected `/mcp` flow for initialize, discovery, OpenAI-compatible `search`, OpenAI-compatible `fetch`, and representative unsupported legacy-shape requests.
- Regression coverage should preserve initialize, baseline tools, hosted authentication, streamable MCP transport, empty-search non-error behavior, and resource-unavailable failure behavior outside the intentional retrieval-contract changes.
- The full repository verification commands required before completion are `pytest` and `ruff check .`.

## Rollback and Mitigation

- Keep FND-023 scoped to retrieval schemas, handlers, result shaping, tests, and hosted verification artifacts so operators can roll back by redeploying the prior revision if compatibility changes break an integration.
- Preserve stable structured error categories and hosted verification evidence so rollout failures can be distinguished quickly from broader protocol, transport, or authentication regressions.
- If implementation requires a temporary compatibility adapter, isolate it to the retrieval-tool seam so it can be removed later without affecting unrelated MCP behavior.

## Observability, Security, and Simplicity

- Observability: hosted verification and request logs should make it obvious whether a failure came from invalid OpenAI-compatible arguments, unsupported legacy shapes, or missing retrieval sources.
- Security: preserve the protected `/mcp` authentication model, keep failures MCP-safe, and avoid exposing secrets or internal implementation details in compatibility errors or verification artifacts.
- Simplicity: prefer direct alignment of the existing `search` and `fetch` contract to the OpenAI shape. Only keep an explicit adapter layer if it is the smallest safe path to preserve a documented compatibility boundary.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design artifacts update the external retrieval contract, define the required hosted verification evidence, keep the change inside the current MCP service seams, and preserve the existing security and transport model. The required full-suite completion commands remain `pytest` and `ruff check .`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
