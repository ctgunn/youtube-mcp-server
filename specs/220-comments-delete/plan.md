# Implementation Plan: Layer 2 Tool `comments_delete`

**Branch**: `220-comments-delete` | **Date**: 2026-06-19 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `comments_delete` for the upstream YouTube Data API `comments.delete` endpoint. The implementation will extend the existing comments Layer 2 resource-family module, reuse the existing Layer 1 `build_comments_delete_wrapper()` from YT-120, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, destructive mutation response shaping, safe validation, safe errors, examples, and default registry integration.

The tool remains endpoint-backed and destructive: it accepts one target comment `id`, requires eligible OAuth authorization, costs 50 official quota units per call, accepts optional delegated owner context only when supported by Layer 1 and eligible OAuth authorization, rejects request bodies and unsupported request shapes before execution, and maps successful no-content upstream responses to a safe deletion acknowledgment without adding listing, reply creation, comment editing, moderation status changes, recovery, automated moderation advice, ranking, summarization, sentiment, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; Layer 1 `comments.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, deletion acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including deletion contract builders, descriptor builders, handler builders, argument validators, target-id helpers, deletion-result mappers, auth-context helpers, upstream-error mappers, default executor/transport helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single deletion request performs one Layer 1 wrapper call and constant-time local validation; no additional lookup, listing, reply creation, comment editing, moderation, recovery, ranking, summarization, sentiment, enrichment, automated moderation advice, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 50 in metadata/description/examples, require OAuth access, require query-only `id`, reject request bodies and unsupported fields before execution, map successful HTTP 204/no-content responses to a safe acknowledgment, avoid leaking tokens/secrets/raw diagnostics in results or errors, keep implementation in the existing comments Layer 2 resource-family module  
**Scale/Scope**: One public MCP tool (`comments_delete`), one existing Layer 2 resource-family module, focused contract/unit/integration coverage, and documentation artifacts for YT-220 only

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

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `comments_delete` contract builder, descriptor builder, handler builder, argument validator, target-id helper, deletion-result mapper, OAuth-context helper, upstream-error mapper, local default transport/executor helpers, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `id`, empty `id`, duplicate or conflicting target shapes, request body rejection, unsupported fields, missing OAuth, authorization failures, missing target comments, already deleted target comments, quota failures, endpoint unavailable, 204/no-content success handling, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── comments-delete-tool-contract.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── comments.py                 # Existing Layer 1 deletion wrapper dependency from YT-120
├── tools/
│   ├── dispatcher.py               # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py             # Public exports for comments_delete symbols
│       ├── comments.py             # Existing Layer 2 comments family; add delete contract, schema, examples, handler, validation, result mapping
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

**Structure Decision**: Extend the existing concrete comments Layer 2 resource-family module used by `comments_list`, `comments_insert`, `comments_update`, and `comments_setModerationStatus`. This keeps all `comments_*` endpoint-backed tool contracts together, reuses existing comments registration and test files, and matches the resource-family pattern used by captions, channels, and channel sections.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official `comments.delete` request, quota, required OAuth behavior, query parameters, no-body rule, 204 response shape, and documented error categories.
- Confirm existing YT-120 Layer 1 wrapper availability and request-shape assumptions.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example conventions in the local codebase.
- Compare existing mutation tools, especially `comments_insert`, `comments_update`, `comments_setModerationStatus`, `channelSections_delete`, `captions_delete`, and `playlistImages_delete`, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/data-model.md)
- [contracts/comments-delete-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/contracts/comments-delete-tool-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/220-comments-delete/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-safe behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Delete Existing Comments Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `comments_delete` is absent until implemented, requires one valid `id`, requires OAuth context, invokes the Layer 1 deletion wrapper once, handles no-content upstream success, and maps success to a deletion acknowledgment with endpoint, quota cost, target ID, safe auth context, delegated owner context when supplied, and mutation status.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local deletion transport, default executor, public exports, and dispatcher registration needed for successful authorized comment deletion.

**Refactor**: Align naming, docstrings, helper reuse, and error mapping with existing comments and mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost and OAuth Before Deleting

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required auth disclosure, target comment identifier requirement, no request body rule, destructive deletion caveat, response boundary, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized deletion, delegated owner context, missing OAuth, missing target ID, empty or malformed target ID, duplicate or conflicting target shape, unsupported body, unsupported option, inaccessible target comment, already deleted target comment, and access-sensitive upstream failure.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific OAuth, destructive deletion, target-comment, and acknowledgment caveats reviewable in `comments.py`.

### User Story 3 - Reject Unsupported Comment Delete Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, empty ID, malformed ID, duplicate or conflicting target shapes, request body presence, unsupported parameters, missing OAuth, authorization failure, invalid request, target comment not found, already deleted target, quota failure, endpoint unavailable, deprecated endpoint, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure API keys, OAuth values, stack traces, raw diagnostics, unsafe request context, and secret-bearing request details are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_comments_contract.py`, `tests/integration/test_youtube_comments_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `COMMENTS_DELETE_*` symbols, add `build_comments_delete_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `comments.py` cohesive and avoid changes to unrelated resource families.

## Risk and Mitigation

- **Destructive operation risk**: This tool removes comments, so the public contract must clearly require OAuth, identify destructive behavior, and reject ambiguous or unsupported request shapes before execution.
- **Response-shape risk**: The upstream success response is HTTP 204/no-content; the Layer 2 result must expose a safe acknowledgment without fabricating deleted comment resource data.
- **Scope risk**: Do not add listing, reply creation, comment editing, moderation status changes, recovery, search, moderation recommendations, summarization, sentiment, ranking, enrichment, or cross-endpoint composition.
- **Auth risk**: Metadata must disclose OAuth-required access and errors must distinguish missing credentials from insufficient permissions without leaking tokens.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request body secrets, or unsafe authorization context in public metadata, results, logs, or errors.

## Verification Commands

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
