# Implementation Plan: Layer 2 Tool `playlistItems_delete`

**Branch**: `235-playlist-items-delete` | **Date**: 2026-07-10 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlistItems_delete` for the YouTube Data API `playlistItems.delete` endpoint. The implementation will extend the existing playlist-items Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`, reuse the existing Layer 1 `build_playlist_items_delete_wrapper()` from YT-135, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, destructive request validation, mutation acknowledgment shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires one `id`, costs 50 official quota units per call, requires OAuth-backed access, returns a deletion acknowledgment with target context, and does not add playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing playlist-items Layer 2 module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`; existing Layer 1 `playlistItems.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, deletion acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlist-items delete contract builders, descriptor builders, handler builders, argument validators, OAuth access-context helpers, deletion acknowledgment mappers, upstream-error mappers, local default transport/executor helpers, any touched Layer 1 wrapper helper, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist-item delete request performs one Layer 1 wrapper call and constant-time local validation; no playlist traversal, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint destructive semantics, expose quota cost 50 in metadata/description/examples, declare OAuth-required access, require `id`, reject unsupported request fields before execution, avoid leaking OAuth tokens/raw diagnostics in results or errors, keep implementation in the existing `youtube_common.playlist_items` Layer 2 family structure, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`playlistItems_delete`), additive extension to the existing playlist-items Layer 2 resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-235 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-135 wrapper and YT-235 seed agree on quota cost `50`, OAuth-required access, required `id`, unsupported modifier rejection, destructive no-body acknowledgment behavior, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlistItems_delete` contract builder, descriptor builder, handler builder, argument validator, OAuth access-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `id`, invalid `id`, unsupported optional fields, missing OAuth access, authorization failures, quota failures, upstream invalid requests, missing-resource failures, endpoint unavailable, deprecated endpoint behavior, destructive no-body success, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlistItems_delete.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlist_items.py      # Existing Layer 1 delete wrapper dependency from YT-135
├── tools/
│   ├── dispatcher.py          # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py        # Public exports for playlistItems_delete symbols
│       ├── contracts.py       # Existing shared contract primitives
│       ├── examples.py        # Representative shared contract set, if catalog export requires update
│       ├── families.py        # Existing playlist_items family placement metadata
│       └── playlist_items.py  # Existing Layer 2 playlist-items family; add delete contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `playlist_items.py` Layer 2 module because YT-232 through YT-234 already established the resource-family file for public playlist-item endpoint tools, the Layer 1 dependency already lives under the same resource-family name, and this slice belongs to the same upstream `playlistItems` resource. This keeps list, insert, update, and delete endpoint tools cohesive while avoiding a broad refactor of existing Layer 2 families.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlistItems.delete` quota, auth mode, required `id`, unsupported modifier boundary, response shape, and documented error categories.
- Confirm existing YT-135 Layer 1 wrapper availability and whether the public YT-235 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, mutation acknowledgment, error, availability, and example conventions in the local codebase.
- Compare existing delete and mutation tools, especially `comments_delete`, `channelSections_delete`, `captions_delete`, `playlistImages_delete`, `playlistItems_insert`, and `playlistItems_update`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported identifier shape, registration surface, destructive acknowledgment shape, safe error categories, examples, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/data-model.md)
- [contracts/playlistItems_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/contracts/playlistItems_delete.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, destructive acknowledgment result shape, OAuth and quota caveats, identifier validation, unsupported modifier rejection, no-body success behavior, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlistItems_delete`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required access disclosure, quota accuracy, identifier validation, destructive acknowledgment behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Delete Playlist Items Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlistItems_delete` is absent until implemented, requires `id`, invokes the Layer 1 delete wrapper once with OAuth-required auth, and maps success to a deletion acknowledgment result with endpoint, quota cost 50, target identifier context, auth context, and mutation outcome.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, OAuth-backed default local executor, public exports, and dispatcher registration needed for successful OAuth-backed playlist-item deletion.

**Refactor**: Align naming, docstrings, helper reuse, destructive caveats, and error mapping with `comments_delete`, `channelSections_delete`, `captions_delete`, `playlistImages_delete`, and existing playlist-item mutation conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Authorization, and Delete Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required auth disclosure, required identifier, destructive response boundary, no-body acknowledgment behavior, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful OAuth-backed deletion, successful no-body deletion acknowledgment, missing identifier, invalid identifier, unsupported input, authorization failure, missing-resource or quota upstream failure, and out-of-scope playlist-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific identifier, quota, OAuth, destructive, no-body acknowledgment, and unsupported-input guidance reviewable in `playlist_items.py`.

### User Story 3 - Reject Invalid Playlist Item Delete Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, blank `id`, non-string `id`, unsupported body/part/playlist metadata/paging/listing inputs, missing OAuth access, authorization failure, quota failure, missing resource, endpoint unavailable, deprecated endpoint behavior, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, API keys, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlist_items_contract.py`, `tests/integration/test_youtube_playlist_items_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLIST_ITEMS_DELETE_*` symbols, add `build_playlist_items_delete_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlist_items.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist images, playlists, thumbnails, search, captions/transcripts, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Destructive action risk**: The tool removes a playlist item from a playlist. Metadata, examples, quickstart, and validation must make the destructive nature visible before invocation.
- **Access risk**: Playlist item deletion is OAuth-required. Metadata, examples, errors, and quickstart validation must make OAuth-required access visible and must not imply API-key-only support.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Acknowledgment ambiguity risk**: Successful delete may not return a deleted resource body. The result mapper must provide explicit deletion acknowledgment with target identifier context without fabricating resource fields.
- **Target identity risk**: The request must clearly identify one playlist item to delete; missing or conflicting target identity must fail locally instead of becoming an ambiguous upstream mutation.
- **Upstream rejection risk**: A valid local request can still fail due to playlist ownership, missing playlist item, unwritable target state, quota, missing resources, or service availability. Error mapping must keep these distinct from local validation failures.
- **Scope risk**: Do not add playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose OAuth tokens, API keys, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlistItems_delete` should live in the existing `playlist_items` Layer 2 module, not in playlist images, playlists, thumbnails, search, captions, transcripts, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
