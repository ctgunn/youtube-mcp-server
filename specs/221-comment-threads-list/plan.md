# Implementation Plan: Layer 2 Tool `commentThreads_list`

**Branch**: `221-comment-threads-list` | **Date**: 2026-06-19 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `commentThreads_list` for the upstream YouTube Data API `commentThreads.list` endpoint. The implementation will add a concrete Layer 2 `comment_threads` resource-family module, reuse the existing Layer 1 `build_comment_threads_list_wrapper()` from YT-121, and follow YT-201/YT-202 shared contract conventions for naming, quota, API-key auth disclosure, selector validation, pagination, ordering, search-term handling, moderation-status access caveats, text-format handling, safe errors, examples, and default registry integration.

The tool remains endpoint-backed and read-oriented: it requires `part`, requires exactly one retrieval selector (`videoId`, `allThreadsRelatedToChannelId`, or `id`), costs 1 official quota unit per call, supports upstream list modifiers where valid for the selected selector, rejects unsupported workflow options and request bodies before execution, and maps successful responses to a near-raw comment-thread list result without adding reply listing, thread insertion, comment mutation, moderation actions, ranking, summarization, sentiment, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; Layer 1 `commentThreads.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, comment-thread list results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including comment-thread contract builders, descriptor builders, handler builders, argument validators, selector helpers, result mappers, API-key auth-context helpers, upstream-error mappers, default executor/transport helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single retrieval request performs one Layer 1 wrapper call and constant-time local validation; pagination is explicit per request and no additional reply lookup, thread insertion, comment mutation, moderation action, ranking, summarization, sentiment, enrichment, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 1 in metadata/description/examples, require `part`, require exactly one selector, use API-key auth for public selector retrieval, document access-sensitive moderation-status behavior, reject request bodies and unsupported fields before execution, reject `maxResults`, `moderationStatus`, `order`, `pageToken`, and `searchTerms` with `id`, avoid leaking tokens/secrets/raw diagnostics in results or errors, keep implementation in a `comment_threads` Layer 2 resource-family module  
**Scale/Scope**: One public MCP tool (`commentThreads_list`), one Layer 2 resource-family module, focused contract/unit/integration coverage, and documentation artifacts for YT-221 only

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

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `commentThreads_list` contract builder, descriptor builder, handler builder, argument validator, selector helper, result mapper, API-key auth-context helper, upstream-error mapper, local default transport/executor helpers, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, missing selector, conflicting selectors, unsupported `maxResults`, `moderationStatus`, `order`, `pageToken`, or `searchTerms` with `id`, invalid `textFormat`, invalid `moderationStatus`, unsupported options, access failures, disabled comments, not-found mapping, and empty successful result distinction.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── commentThreads_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── comment_threads.py          # Existing Layer 1 list wrapper dependency from YT-121
├── tools/
│   ├── dispatcher.py               # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py             # Public exports for commentThreads_list symbols
│       ├── comment_threads.py      # New Layer 2 contract, schema, examples, handler, validation, result mapping
│       ├── contracts.py            # Existing shared contract primitives
│       └── examples.py             # Representative shared contract set

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_comment_threads_contract.py
│   ├── test_youtube_common_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_comment_threads_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_comment_threads.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Add a concrete `comment_threads` Layer 2 resource-family module because the public `commentThreads_*` tools map to the YouTube `commentThreads` resource family, and the existing Layer 1 dependency already lives in `integrations/resources/comment_threads.py`. This keeps `commentThreads_list` separate from `comments_*` endpoint tools while preserving the resource-family pattern used by captions, channels, channel sections, and comments.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official `commentThreads.list` request, quota, supported filters, optional parameters, selector-specific restrictions, no-body request policy, response shape, auth/access caveats, and documented error categories.
- Confirm existing YT-121 Layer 1 wrapper availability and request-shape assumptions.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example conventions in the local codebase.
- Compare existing list tools, especially `comments_list`, `channelSections_list`, `channels_list`, `activities_list`, and `captions_list`, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/data-model.md)
- [contracts/commentThreads_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/contracts/commentThreads_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, API-key-only public selector execution, documented access-sensitive caveats, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Comment Threads Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `commentThreads_list` is absent until implemented, requires `part`, accepts exactly one selector, invokes the Layer 1 list wrapper once with API-key auth, and maps success to a comment-thread list result with endpoint, quota cost, requested parts, selector, items, pagination fields, order/search/text-format context, and moderation-status context when supplied.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful video-based, channel-related, and ID-based retrieval.

**Refactor**: Align naming, docstrings, helper reuse, and error mapping with existing list tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Auth, and Filter Modes Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, API-key auth disclosure, required part selection, `videoId`, `allThreadsRelatedToChannelId`, and `id` selector rules, pagination restrictions, `moderationStatus`, `order`, `searchTerms`, `textFormat` values, no request body, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for video-based retrieval, channel-related retrieval, ID-based retrieval, paginated retrieval, ordered retrieval, searched retrieval, plain-text retrieval, moderation-status access-sensitive retrieval, empty successful results, selector validation failures, unsupported option failures, disabled-comments failure, and access-sensitive failure.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific selector and access caveats reviewable in `comment_threads.py`.

### User Story 3 - Reject Unsupported Comment Thread List Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, missing selector, multiple selectors, empty IDs, malformed IDs, unsupported `maxResults`, `moderationStatus`, `order`, `pageToken`, and `searchTerms` with `id`, invalid page size, invalid `textFormat`, invalid `moderationStatus`, request body, reply-listing fields, mutation fields, moderation-action fields, ranking instructions, access failure, disabled comments, channel/video/thread not found, quota failure, endpoint unavailable, deprecated endpoint, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth/API key values, stack traces, raw details, and unsafe diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_comment_threads_contract.py`, `tests/integration/test_youtube_comment_threads_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `COMMENT_THREADS_LIST_*` symbols, add `build_comment_threads_list_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `comment_threads.py` cohesive and avoid changes to unrelated resource families.

## Risk and Mitigation

- **Selector compatibility risk**: Official docs require exactly one filter and state `maxResults`, `moderationStatus`, `order`, `pageToken`, and `searchTerms` are not supported with `id`; local validation must reject unsupported combinations before Layer 1 execution.
- **Access caveat risk**: Layer 1 currently executes public selectors with API-key auth while official docs make `moderationStatus` access-sensitive. Metadata and validation must disclose moderation-status authorization caveats without claiming ordinary public retrieval requires OAuth.
- **No-match versus failure risk**: Empty successful responses must remain distinguishable from `commentThreadNotFound`, `channelNotFound`, `videoNotFound`, `commentsDisabled`, authorization failures, quota exhaustion, and upstream failures.
- **Scope risk**: Do not add reply listing, thread creation, comment insertion, comment editing, comment deletion, moderation status changes, sentiment, ranking, summarization, analytics, or enrichment.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, or unsafe request context in public metadata, results, logs, or errors.

## Verification Commands

```bash
pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
