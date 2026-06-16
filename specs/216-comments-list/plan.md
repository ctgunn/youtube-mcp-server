# Implementation Plan: Layer 2 Tool `comments_list`

**Branch**: `216-comments-list` | **Date**: 2026-06-15 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `comments_list` for the upstream YouTube Data API `comments.list` endpoint. The implementation will add a comments Layer 2 resource-family module, reuse the existing Layer 1 `build_comments_list_wrapper()` from YT-116, and follow YT-201/YT-202 shared contract conventions for naming, quota, auth-mode disclosure, selector validation, pagination, text-format handling, safe errors, examples, and registry integration.

The tool remains endpoint-backed and read-oriented: it requires `part`, requires exactly one retrieval selector (`id` or `parentId`), costs 1 official quota unit per call, supports `maxResults`, `pageToken`, and `textFormat` where upstream allows them, rejects unsupported workflow options, and maps successful responses to a near-raw comment list result without adding thread discovery, mutation, moderation, ranking, summarization, sentiment, or enrichment behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; Layer 1 `comments.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, comment list results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including comments contract builders, descriptor builders, handler builders, argument validators, result mappers, default executor/transport helpers, upstream-error mappers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single retrieval request performs one Layer 1 wrapper call and constant-time local validation; pagination is explicit per request and no additional lookup, thread traversal, moderation, ranking, summarization, sentiment, enrichment, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 1 in metadata/description/examples, require `part`, require exactly one selector, reject unsupported request fields before execution, do not allow `maxResults` or `pageToken` with `id`, avoid leaking tokens/secrets/raw diagnostics in results or errors, keep implementation in a comments Layer 2 resource-family module  
**Scale/Scope**: One public MCP tool (`comments_list`), one Layer 2 resource-family module, focused contract/unit/integration coverage, and documentation artifacts for YT-216 only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

**Gate Status**: PASS. No constitution violations or unresolved clarifications.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `comments_list` contract builder, descriptor builder, handler builder, argument validator, selector helper, result mapper, auth-context helper, upstream-error mapper, local default transport/executor helpers, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, missing selector, conflicting selectors, unsupported `maxResults` or `pageToken` with `id`, invalid `textFormat`, unsupported options, access failures, not-found mapping, and empty successful result distinction.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
specs/216-comments-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── comments_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
src/mcp_server/
├── integrations/resources/
│   └── comments.py                 # Existing Layer 1 list wrapper dependency from YT-116
├── tools/
│   ├── dispatcher.py               # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py             # Public exports for comments_list symbols
│       ├── comments.py             # New Layer 2 contract, schema, examples, handler, validation, result mapping
│       ├── contracts.py            # Existing shared contract primitives
│       └── examples.py             # Representative shared contract set

tests/
├── contract/
│   ├── test_youtube_comments_contract.py
│   └── test_youtube_common_contract.py
├── integration/
│   └── test_youtube_comments_registration.py
└── unit/
    ├── test_youtube_comments.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Add a concrete comments Layer 2 resource-family module because no public Layer 2 comments module exists yet. This keeps all `comments_*` endpoint-backed tool contracts together as the comments family grows and matches the existing resource-family pattern used by captions, channels, and channel sections.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official `comments.list` request, quota, supported filters, pagination limits, text-format values, no-body request policy, response shape, auth/access caveats, and documented error categories.
- Confirm existing YT-116 Layer 1 wrapper availability and request-shape assumptions.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example conventions in the local codebase.
- Compare existing list tools, especially `activities_list`, `channels_list`, `channelSections_list`, and `captions_list`, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/data-model.md)
- [contracts/comments_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/contracts/comments_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Comments Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `comments_list` is absent until implemented, requires `part`, accepts exactly one selector, invokes the Layer 1 list wrapper once with the selected auth context, and maps success to a comment list result with endpoint, quota cost, requested parts, selector, items, pagination fields, and text-format context.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful ID-based and parent-comment retrieval.

**Refactor**: Align naming, docstrings, helper reuse, and error mapping with existing list tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Auth, and Lookup Modes Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, mixed or conditional auth disclosure, required part selection, `id` and `parentId` selector rules, pagination restrictions, `textFormat` values, no request body, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for ID retrieval, parent-comment retrieval, paginated retrieval, plain-text retrieval, empty successful results, selector validation failures, unsupported option failures, and access-sensitive failure.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific caveats reviewable in `comments.py`.

### User Story 3 - Reject Unsupported Comment List Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, missing selector, multiple selectors, empty IDs, malformed IDs, unsupported `maxResults` and `pageToken` with `id`, invalid page size, invalid `textFormat`, request body, sorting/search/moderation/thread traversal options, access failure, not-found, quota failure, endpoint unavailable, deprecated endpoint, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth/API key values, stack traces, raw details, and unsafe diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_comments_contract.py`, and `tests/integration/test_youtube_comments_registration.py`.

**Green**: Export `COMMENTS_LIST_*` symbols, add `build_comments_list_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `comments.py` cohesive and avoid changes to unrelated resource families.

## Risk and Mitigation

- **Selector compatibility risk**: Official docs require exactly one filter and state `maxResults` and `pageToken` are not supported with `id`; local validation must reject unsupported combinations before Layer 1 execution.
- **Access caveat risk**: Official docs document insufficient-permission failures and existing project inventory treats comment list auth as API-key or mixed depending on filter mode. Metadata must disclose the selected auth mode and access-sensitive limitations without claiming every read requires OAuth.
- **No-match versus failure risk**: Empty successful responses must remain distinguishable from `commentNotFound`, authorization failures, quota exhaustion, and upstream failures.
- **Scope risk**: Do not add comment-thread discovery, reply creation, editing, moderation status changes, deletion, sentiment, ranking, summarization, analytics, or enrichment.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, or unsafe request context in public metadata, results, or errors.

## Verification Commands

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py
pytest
ruff check .
```
