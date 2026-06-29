# Implementation Plan: Layer 2 Tool `commentThreads_insert`

**Branch**: `222-comment-threads-insert` | **Date**: 2026-06-29 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `commentThreads_insert` for the upstream YouTube Data API `commentThreads.insert` endpoint. The implementation will extend the existing concrete comment threads Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`, reuse the existing Layer 1 `build_comment_threads_insert_wrapper()` from YT-122, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, mutation response shaping, safe validation, safe errors, examples, and default registry integration.

The tool remains endpoint-backed and write-oriented: it requires `part`, requires an OAuth-authorized request, requires a `body` with `body.snippet.channelId`, `body.snippet.videoId`, and `body.snippet.topLevelComment.snippet.textOriginal`, costs 50 official quota units per call, accepts optional delegated owner context when supported by Layer 1, rejects reply creation and other unsupported write shapes, and maps successful responses to a near-raw created comment-thread result without adding listing, reply insertion, moderation, editing, deletion, automated response generation, ranking, summarization, sentiment, enrichment, analytics, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; Layer 1 `commentThreads.insert` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, created-thread results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including comment-thread insert contract builders, descriptor builders, handler builders, argument validators, top-level body helpers, result mappers, OAuth-context helpers, upstream-error mappers, default executor/transport helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single top-level thread creation request performs one Layer 1 wrapper call and constant-time local validation; no additional lookup, listing, reply creation, moderation, ranking, summarization, sentiment, enrichment, analytics, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 50 in metadata/description/examples, require `part`, require OAuth access, require `body.snippet.channelId`, require `body.snippet.videoId`, require non-empty `body.snippet.topLevelComment.snippet.textOriginal`, reject unsupported request fields before execution, avoid leaking tokens/secrets/raw diagnostics in results or errors, keep implementation in the existing `comment_threads` Layer 2 resource-family module  
**Scale/Scope**: One public MCP tool (`commentThreads_insert`), one existing Layer 2 resource-family module, focused contract/unit/integration coverage, and documentation artifacts for YT-222 only

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

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `commentThreads_insert` contract builder, descriptor builder, handler builder, argument validator, top-level body helper, result mapper, OAuth-context helper, upstream-error mapper, local default transport/executor helpers, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, missing `body`, missing `body.snippet`, missing `body.snippet.channelId`, missing `body.snippet.videoId`, missing or empty `body.snippet.topLevelComment.snippet.textOriginal`, unsupported reply-style shapes, unsupported request fields, missing OAuth, authorization failures, channel not found, video not found, disabled comments, text-too-long failures, quota failures, endpoint unavailable, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── commentThreads_insert.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── comment_threads.py          # Existing Layer 1 insert wrapper dependency from YT-122
├── tools/
│   ├── dispatcher.py               # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py             # Public exports for commentThreads_insert symbols
│       ├── comment_threads.py      # Existing Layer 2 commentThreads family; add insert contract, schema, examples, handler, validation, result mapping
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

**Structure Decision**: Extend the existing concrete `comment_threads` Layer 2 resource-family module created for `commentThreads_list`. This keeps public `commentThreads_*` endpoint-backed tools together, reuses the existing Layer 1 `integrations/resources/comment_threads.py` dependency, and matches the resource-family pattern used by captions, channels, channel sections, comments, and the YT-221 neighboring list tool.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official `commentThreads.insert` request, quota, required OAuth scope, required `part`, required request body fields, response shape, top-level-comment boundary, reply delegation to `comments.insert`, and documented error categories.
- Confirm existing YT-122 Layer 1 wrapper availability and request-shape assumptions.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example conventions in the local codebase.
- Compare existing mutation tools, especially `comments_insert`, `channelSections_insert`, `captions_insert`, `channels_update`, and the neighboring `commentThreads_list`, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/data-model.md)
- [contracts/commentThreads_insert.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/contracts/commentThreads_insert.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-safe behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Create Top-Level Comment Threads Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `commentThreads_insert` is absent until implemented, requires `part`, requires a valid top-level comment-thread body with `body.snippet.channelId`, `body.snippet.videoId`, and `body.snippet.topLevelComment.snippet.textOriginal`, requires OAuth context, invokes the Layer 1 insert wrapper once, and maps success to a created comment-thread result with endpoint, quota cost, requested parts, mutation status, safe auth context, target context, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local insert transport, default executor, public exports, and dispatcher registration needed for successful authorized top-level thread creation.

**Refactor**: Align naming, docstrings, helper reuse, and error mapping with existing comment thread and mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Top-Level Comment Rules Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required auth disclosure, required part selection, `body.snippet.channelId`, `body.snippet.videoId`, `body.snippet.topLevelComment.snippet.textOriginal`, optional delegation context, response boundary, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized top-level thread creation, delegated owner context, missing OAuth, missing part, missing target channel, missing target video, missing top-level comment text, invalid target context, unsupported reply creation shape, unsupported option validation failure, disabled-comment target failure, and access-sensitive upstream failure.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific OAuth and top-level creation caveats reviewable in `comment_threads.py`.

### User Story 3 - Reject Unsupported Thread Creation Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, missing `body`, missing `snippet`, missing channel ID, missing video ID, missing `topLevelComment`, missing nested top-level comment snippet, missing or blank text, reply creation fields such as `parentId`, list filters, update/moderation/delete fields, unsupported optional parameters, missing OAuth, authorization failure, invalid request, channel not found, video not found, comments disabled, text too long, quota failure, endpoint unavailable, deprecated endpoint, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure API keys, OAuth values, stack traces, raw details, unsafe request context, and publishable secret data are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_comment_threads_contract.py`, `tests/integration/test_youtube_comment_threads_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `COMMENT_THREADS_INSERT_*` symbols, add `build_comment_threads_insert_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `comment_threads.py` cohesive and avoid changes to unrelated resource families.

## Risk and Mitigation

- **Publication risk**: This tool creates a visible YouTube top-level comment, so the public contract must clearly require OAuth and reject ambiguous or unsupported request shapes before execution.
- **Scope risk**: Do not add reply creation; official docs direct that behavior to `comments.insert`.
- **Validation risk**: Missing `snippet.channelId`, missing `snippet.videoId`, missing `snippet.topLevelComment.snippet.textOriginal`, too-long text, invalid custom emoji, disabled comments, channel-not-found, video-not-found, and invalid metadata errors must map to safe caller-facing categories.
- **Auth risk**: Metadata must disclose OAuth-required access and errors must distinguish missing credentials from insufficient permissions without leaking tokens.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request body secrets, or unsafe authorization context in public metadata, results, logs, or errors.

## Verification Commands

```bash
pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
