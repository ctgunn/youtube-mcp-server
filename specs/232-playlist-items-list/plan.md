# Implementation Plan: Layer 2 Tool `playlistItems_list`

**Branch**: `232-playlist-items-list` | **Date**: 2026-07-09 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlistItems_list` for the YouTube Data API `playlistItems.list` endpoint. The implementation will add a new playlist-items Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`, reuse the existing Layer 1 `build_playlist_items_list_wrapper()` from YT-132, and follow YT-201/YT-202 shared contract conventions for naming, quota, API-key access disclosure, selector validation, pagination, near-raw list result shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires `part` plus exactly one supported selector (`playlistId` or `id`), costs 1 official quota unit per call, preserves playlist-scoped pagination where supported, returns playlist-item collection results with request context, and does not add playlist-item insertion, update, deletion, playlist mutation, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; new Layer 2 playlist-items module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`; existing Layer 1 `playlistItems.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, playlist-item list results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlist-items list contract builders, descriptor builders, handler builders, argument validators, access-context helpers, list result mappers, upstream-error mappers, local default transport/executor helpers, any touched Layer 1 wrapper helper, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist-item list request performs one Layer 1 wrapper call and local validation proportional to supplied selector and part strings; no playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 1 in metadata/description/examples, declare API-key access expectations for the supported selector set, require `part` and exactly one selector, reject unsupported request fields before execution, avoid leaking credential material or raw diagnostics in results or errors, add the new code under the existing `youtube_common` Layer 2 family structure, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`playlistItems_list`), additive new playlist-items Layer 2 resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-232 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-132 wrapper and YT-232 seed agree on quota cost `1`, API-key access expectations for the supported selector set, required `part`, supported selectors `playlistId` and `id`, playlist-scoped pagination, unsupported modifier rejection, empty list success behavior, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlistItems_list` contract builder, descriptor builder, handler builder, argument validator, access-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, missing selector, conflicting selectors, malformed identifiers, unsupported paging, out-of-range `maxResults`, access failures, quota failures, upstream invalid requests, missing-resource or no-match outcomes, endpoint unavailable, empty successful collections, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlistItems_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlist_items.py      # Existing Layer 1 list wrapper dependency from YT-132
├── tools/
│   ├── dispatcher.py          # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py        # Public exports for playlistItems_list symbols
│       ├── contracts.py       # Existing shared contract primitives
│       ├── examples.py        # Representative shared contract set, if catalog export requires update
│       ├── families.py        # Existing playlist_items family placement metadata
│       └── playlist_items.py  # New Layer 2 playlist-items family; add list contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_playlist_items_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_playlist_items_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_playlist_items.py
```

**Structure Decision**: Add `playlist_items.py` under the existing Layer 2 `youtube_common` package because `playlist_items` is already a required resource family in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`, the Layer 1 dependency already lives under the same resource-family name, and this slice should remain separate from playlist images, playlists, thumbnails, search, transcripts, and higher-level workflow modules. This keeps the public endpoint tool cohesive while avoiding a broad refactor of existing Layer 2 families.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlistItems.list` quota, access mode, required `part`, supported `playlistId` and `id` selectors, pagination boundaries, response shape, and documented error categories.
- Confirm existing YT-132 Layer 1 wrapper availability and whether the public YT-232 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, access, list result, pagination, error, availability, and example conventions in the local codebase.
- Compare existing list tools, especially `playlistImages_list`, `comments_list`, `commentThreads_list`, `members_list`, and the shared resource-family registry, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported selector shape, registration surface, list result shape, pagination handling, safe error categories, examples, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist-item mutation, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/data-model.md)
- [contracts/playlistItems_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/contracts/playlistItems_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, list result shape, access and quota caveats, part validation, selector validation, pagination validation, unsupported modifier rejection, empty successful collections, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlistItems_list`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, API-key access disclosure, quota accuracy, part and selector validation, list result and pagination behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Playlist Items Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlistItems_list` is absent until implemented, requires `part` plus exactly one supported selector, invokes the Layer 1 list wrapper once with API-key access context for the supported selector set, and maps success to a playlist-item list result with endpoint, quota cost 1, selected part context, selector context, paging context when applicable, access context, and returned items.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful playlist-scoped and identifier-based playlist-item retrieval.

**Refactor**: Align naming, docstrings, helper reuse, selector/paging caveats, and error mapping with `playlistImages_list`, `comments_list`, `commentThreads_list`, and shared list-result conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Selectors, Access, and Pagination Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, API-key access disclosure, required part selection, `playlistId` and `id` lookup modes, selector-specific pagination behavior, empty-result behavior, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for playlist-scoped retrieval, identifier-based retrieval, paginated playlist traversal, empty successful results, missing part, invalid part, missing selector, conflicting selector, unsupported paging or modifier, access failure, and out-of-scope playlist-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific selector, quota, access, paging, empty-result, and unsupported-input guidance reviewable in `playlist_items.py`.

### User Story 3 - Reject Invalid Playlist Item List Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, blank or unsupported `part`, missing selector, conflicting selectors, blank or non-string `playlistId`, blank or non-string `id`, duplicate or excessive identifier input, unsupported optional fields, invalid page tokens, out-of-range `maxResults`, selector-incompatible paging, access failure, quota failure, missing resource, endpoint unavailable, upstream invalid request, empty successful results, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlist_items_contract.py`, `tests/integration/test_youtube_playlist_items_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLIST_ITEMS_LIST_*` symbols, add `build_playlist_items_list_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlist_items.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist images, playlists, thumbnails, search, captions/transcripts, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Selector ambiguity risk**: The tool supports `playlistId` and `id` lookup modes. Validation must require exactly one selector and identify missing or conflicting selector input before execution.
- **Pagination ambiguity risk**: Playlist-scoped traversal is pageable, while identifier-based pagination must only be allowed if the shared contract explicitly permits it. Selector-incompatible paging must fail clearly rather than being silently ignored.
- **Access risk**: The supported selector set follows the documented API-key access path from YT-132. Metadata, examples, errors, and quickstart validation must not imply OAuth-only access for this low-level list tool.
- **Quota risk**: Each invocation costs 1 quota unit. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `1`.
- **Empty-result ambiguity risk**: A valid list request can return no playlist items. The result mapper must keep empty successful collections distinct from validation failures, access failures, no-match errors, quota failures, and upstream service failures.
- **Scope risk**: Do not add playlist-item insertion, update, deletion, playlist mutation, playlist search, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlistItems_list` should live in the new `playlist_items` Layer 2 module, not in playlist images, playlists, search, captions, transcripts, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
