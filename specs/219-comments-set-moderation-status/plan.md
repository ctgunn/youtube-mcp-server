# Implementation Plan: Layer 2 Tool `comments_setModerationStatus`

**Branch**: `219-comments-set-moderation-status` | **Date**: 2026-06-19 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `comments_setModerationStatus` for the upstream YouTube Data API `comments.setModerationStatus` endpoint. The implementation will extend the existing comments Layer 2 resource-family module, reuse the existing Layer 1 `build_comments_set_moderation_status_wrapper()` from YT-119, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, mutation acknowledgment response shaping, safe validation, safe errors, examples, and default registry integration.

The tool remains endpoint-backed and write-oriented: it accepts query-only moderation inputs, requires at least one target comment `id`, requires `moderationStatus`, supports only `heldForReview`, `published`, and `rejected`, accepts `banAuthor` only when `moderationStatus` is `rejected`, costs 50 official quota units per call, accepts optional delegated owner context only when supported by Layer 1 and eligible OAuth authorization, rejects unsupported request shapes before execution, and maps successful no-content upstream responses to a safe moderation acknowledgment without adding listing, reply creation, comment editing, deletion, automated moderation advice, ranking, summarization, sentiment, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; Layer 1 `comments.setModerationStatus` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, moderation acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including moderation status contract builders, descriptor builders, handler builders, argument validators, target-id helpers, moderation-status helpers, optional-flag helpers, result mappers, auth-context helpers, upstream-error mappers, default executor/transport helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single moderation request performs one Layer 1 wrapper call and constant-time local validation; no additional lookup, listing, reply creation, comment editing, deletion, ranking, summarization, sentiment, enrichment, automated moderation advice, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 50 in metadata/description/examples, require OAuth access, require query-only `id` and `moderationStatus`, support `banAuthor` only with `rejected`, reject request bodies and unsupported fields before execution, avoid leaking tokens/secrets/raw diagnostics in results or errors, keep implementation in the existing comments Layer 2 resource-family module  
**Scale/Scope**: One public MCP tool (`comments_setModerationStatus`), one existing Layer 2 resource-family module, focused contract/unit/integration coverage, and documentation artifacts for YT-219 only

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

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `comments_setModerationStatus` contract builder, descriptor builder, handler builder, argument validator, target-id helper, moderation-status helper, optional-flag helper, result mapper, OAuth-context helper, upstream-error mapper, local default transport/executor helpers, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `id`, empty or duplicate `id`, missing `moderationStatus`, unsupported status, invalid `banAuthor`, `banAuthor` with non-`rejected` status, request body rejection, unsupported fields, missing OAuth, authorization failures, missing target comments, limited moderation functionality, quota failures, endpoint unavailable, 204/no-content success handling, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── comments-set-moderation-status-tool-contract.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── comments.py                 # Existing Layer 1 moderation wrapper dependency from YT-119
├── tools/
│   ├── dispatcher.py               # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py             # Public exports for comments_setModerationStatus symbols
│       ├── comments.py             # Existing Layer 2 comments family; add moderation contract, schema, examples, handler, validation, result mapping
│       ├── contracts.py            # Existing shared contract primitives
│       └── examples.py             # Representative shared contract set

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_comments_contract.py
│   ├── test_youtube_common_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_comments_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_comments.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Extend the existing concrete comments Layer 2 resource-family module created for `comments_list`, `comments_insert`, and `comments_update`. This keeps all `comments_*` endpoint-backed tool contracts together, reuses existing comments registration and test files, and matches the resource-family pattern used by captions, channels, and channel sections.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official `comments.setModerationStatus` request, quota, required OAuth behavior, query parameters, accepted moderation statuses, `banAuthor` rule, no-body rule, 204 response shape, and documented error categories.
- Confirm existing YT-119 Layer 1 wrapper availability and request-shape assumptions.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example conventions in the local codebase.
- Compare existing mutation tools, especially `comments_insert`, `comments_update`, `channelSections_update`, `channels_update`, and `captions_update`, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/data-model.md)
- [contracts/comments-set-moderation-status-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/contracts/comments-set-moderation-status-tool-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/219-comments-set-moderation-status/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-safe behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Moderate Existing Comments Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `comments_setModerationStatus` is absent until implemented, requires at least one valid `id`, requires a supported `moderationStatus`, requires OAuth context, invokes the Layer 1 moderation wrapper once, handles no-content upstream success, and maps success to a moderation acknowledgment with endpoint, quota cost, target IDs, requested status, safe auth context, optional flag context, and mutation status.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local moderation transport, default executor, public exports, and dispatcher registration needed for successful authorized moderation status changes.

**Refactor**: Align naming, docstrings, helper reuse, and error mapping with existing comments and mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Moderation States Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required auth disclosure, target comment identifiers, supported moderation statuses, `banAuthor` compatibility, no request body rule, response boundary, caveats, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized publication, authorized hold-for-review, authorized rejection with compatible `banAuthor`, missing OAuth, missing target IDs, duplicate target IDs, missing moderation status, unsupported moderation status, incompatible `banAuthor`, unsupported body, unsupported option, inaccessible target comment, and access-sensitive upstream failure.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific OAuth, moderation-state, and optional-flag caveats reviewable in `comments.py`.

### User Story 3 - Reject Unsupported Moderation Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, empty ID, duplicate IDs, missing `moderationStatus`, unsupported status, non-boolean `banAuthor`, `banAuthor` with non-`rejected` status, request body presence, unsupported parameters, missing OAuth, authorization failure, invalid request, target comment not found, limited moderation functionality, quota failure, endpoint unavailable, deprecated endpoint, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure API keys, OAuth values, stack traces, raw diagnostics, unsafe request context, and secret-bearing request details are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_comments_contract.py`, `tests/integration/test_youtube_comments_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `COMMENTS_SET_MODERATION_STATUS_*` symbols, add `build_comments_set_moderation_status_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `comments.py` cohesive and avoid changes to unrelated resource families.

## Risk and Mitigation

- **Mutation risk**: This tool changes comment visibility and may hide replies for rejected comments, so the public contract must clearly require OAuth and reject ambiguous or unsupported request shapes before execution.
- **Moderation-state risk**: Only `heldForReview`, `published`, and `rejected` are supported; unsupported values and unsupported transition assumptions must fail clearly.
- **Optional flag risk**: `banAuthor` is only valid with `rejected`; incompatible combinations must fail locally before execution.
- **Scope risk**: Do not add listing, reply creation, comment editing, deletion, search, moderation recommendations, summarization, sentiment, ranking, enrichment, or cross-endpoint composition.
- **Auth risk**: Metadata must disclose OAuth-required access and errors must distinguish missing credentials from insufficient permissions without leaking tokens.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request body secrets, or unsafe authorization context in public metadata, results, logs, or errors.

## Verification Commands

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
