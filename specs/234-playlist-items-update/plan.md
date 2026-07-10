# Implementation Plan: Layer 2 Tool `playlistItems_update`

**Branch**: `234-playlist-items-update` | **Date**: 2026-07-09 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlistItems_update` for the YouTube Data API `playlistItems.update` endpoint. The implementation will extend the existing playlist-items Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`, reuse the existing Layer 1 `build_playlist_items_update_wrapper()` from YT-134, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-backed authorization disclosure, mutation validation, near-raw updated-resource result shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires `part`, `body.id`, a writable `body.snippet` payload preserving playlist and referenced-video context, and OAuth-backed access; it costs 50 official quota units per call; it returns updated playlist-item resources with request context; and it does not add playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, automated curation, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 playlist-items module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`; existing Layer 1 `playlistItems.update` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, playlist-item update results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlist-items update contract builders, descriptor builders, handler builders, argument validators, OAuth access-context helpers, mutation result mappers, upstream-error mappers, local default transport/executor helpers, any touched Layer 1 wrapper helper, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist-item update request performs one Layer 1 wrapper call and local validation proportional to supplied part and body fields; no playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint mutation semantics, expose quota cost 50 in metadata/description/examples, declare OAuth-backed access expectations, require `part`, `body.id`, and writable `body.snippet` playlist/video context, reject unsupported request fields before execution, avoid leaking credential material or raw diagnostics in results or errors, extend the existing `youtube_common.playlist_items` Layer 2 family structure, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`playlistItems_update`), additive extension to the existing playlist-items Layer 2 resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-234 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-134 wrapper and YT-234 seed agree on quota cost `50`, OAuth-backed access expectations, required `part`, required `body.id`, required writable `body.snippet.playlistId`, required `body.snippet.resourceId.videoId`, unsupported optional placement/content-detail rejection unless explicitly added, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlistItems_update` contract builder, descriptor builder, handler builder, argument validator, OAuth access-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, missing `body`, non-object `body`, missing `body.id`, missing `body.snippet`, missing playlist identifier, missing video reference, unsupported placement or content-detail fields, read-only fields, unsupported optional fields, missing OAuth access, authorization failures, quota failures, upstream invalid requests, invalid writable-field outcomes, missing-resource outcomes, endpoint unavailable, deprecated endpoint behavior, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlistItems_update.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlist_items.py      # Existing Layer 1 update wrapper dependency from YT-134
├── tools/
│   ├── dispatcher.py          # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py        # Public exports for playlistItems_update symbols
│       ├── contracts.py       # Existing shared contract primitives
│       ├── examples.py        # Representative shared contract set, if catalog export requires update
│       ├── families.py        # Existing playlist_items family placement metadata
│       └── playlist_items.py  # Existing Layer 2 playlist-items family; add update contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `playlist_items.py` Layer 2 module because YT-232 and YT-233 already established the resource-family file for public playlist-item endpoint tools, the Layer 1 dependency already lives under the same resource-family name, and this slice should remain separate from playlist images, playlists, thumbnails, search, transcripts, and higher-level workflow modules. This keeps list, insert, and update endpoint tools cohesive while avoiding a broad refactor of existing Layer 2 families.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlistItems.update` quota, access mode, required `part`, required target `body.id`, required writable playlist/video context body, optional-field boundaries, response shape, and documented error categories.
- Confirm existing YT-134 Layer 1 wrapper availability and whether the public YT-234 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, OAuth, mutation result, error, availability, and example conventions in the local codebase.
- Compare existing mutation tools, especially `comments_update`, `channelSections_update`, `playlistImages_update`, `playlistItems_insert`, and the existing `playlistItems_list` module, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported update body shape, registration surface, mutation result shape, OAuth boundary, safe error categories, examples, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, automated curation, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/data-model.md)
- [contracts/playlistItems_update.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/contracts/playlistItems_update.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, mutation result shape, OAuth and quota caveats, part validation, body validation, target identity validation, writable-field validation, unsupported modifier rejection, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlistItems_update`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-backed access disclosure, quota accuracy, part/body/target/writable-field validation, mutation result behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Update Playlist Items Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlistItems_update` is absent until implemented, requires `part`, `body.id`, and a valid writable `body.snippet` playlist/video context, requires OAuth-backed access, invokes the Layer 1 update wrapper once, and maps success to an updated playlist-item result with endpoint, quota cost 50, selected part context, target identity context, writable update context, authorization context, and returned resource fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, OAuth-backed default local executor, public exports, and dispatcher registration needed for successful playlist-item update.

**Refactor**: Align naming, docstrings, helper reuse, mutation caveats, and error mapping with `comments_update`, `channelSections_update`, `playlistImages_update`, `playlistItems_insert`, and shared mutation-result conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Authorization, and Update Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-backed access disclosure, required part selection, required target playlist-item identity, writable update data, mutation result shape, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for OAuth-backed update, missing part, invalid part, missing target identity, missing writable update body, invalid update body, unsupported field, authorization failure, quota or upstream update failure, and out-of-scope playlist-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific target identity, quota, auth, writable update data, and unsupported-input guidance reviewable in `playlist_items.py`.

### User Story 3 - Reject Invalid Playlist Item Update Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, blank or unsupported `part`, missing `body`, non-object `body`, missing `body.id`, missing `body.snippet`, missing `body.snippet.playlistId`, missing `body.snippet.resourceId.videoId`, malformed resource identity, read-only fields, unsupported optional fields, unsupported placement or content-detail fields, missing OAuth access, authorization failure, quota failure, missing resource, endpoint unavailable, upstream invalid request, invalid writable-field failure, deprecated endpoint behavior, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlist_items_contract.py`, `tests/integration/test_youtube_playlist_items_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLIST_ITEMS_UPDATE_*` symbols, add `build_playlist_items_update_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlist_items.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist images, playlists, thumbnails, search, captions/transcripts, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Mutation safety risk**: Playlist item update changes an existing playlist entry. Validation, examples, and quickstart must make OAuth-backed access and target playlist-item identity explicit before invocation.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Body-shape ambiguity risk**: The supported update shape centers on `body.id` plus writable `body.snippet` playlist/video context. Requests missing target identity, playlist identity, video reference, or supported snippet shape must fail clearly before execution.
- **Writable-field ambiguity risk**: Placement and content-detail behavior are outside the guaranteed contract unless explicitly added. Unsupported or conflicting writable fields must fail clearly rather than being silently ignored.
- **Access risk**: The tool requires OAuth-backed access. Metadata, examples, errors, and quickstart validation must not imply API-key-only access for this mutation tool.
- **Upstream rejection risk**: A valid local request can still fail due to playlist ownership, missing playlist item, unwritable target state, invalid writable fields, quota, missing resources, or service availability. Error mapping must keep these distinct from local validation failures.
- **Scope risk**: Do not add playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlistItems_update` should extend the existing `playlist_items` Layer 2 module, not playlist images, playlists, search, captions, transcripts, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
