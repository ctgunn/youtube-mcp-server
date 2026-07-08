# Implementation Plan: Layer 2 Tool `playlistImages_list`

**Branch**: `228-playlist-images-list` | **Date**: 2026-07-08 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlistImages_list` for the YouTube Data API `playlistImages.list` endpoint. The implementation will add a concrete playlist-images resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, reuse the existing Layer 1 `build_playlist_images_list_wrapper()` from YT-128, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, selector validation, selector-specific paging, list result shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires `part`, requires exactly one selector from `playlistId` or `id`, allows `pageToken` and `maxResults` only with `playlistId`, costs 1 official quota unit per call, preserves successful empty results distinctly, and does not add playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, analytics, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `playlistImages.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, playlist-image list results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlist-images contract builders, descriptor builders, handler builders, argument validators, part and selector helpers, result mappers, upstream-error mappers, default executor/transport helpers, Layer 1 metadata helpers if changed, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist-image list request performs one Layer 1 wrapper call and constant-time local validation; no additional playlist traversal, image upload, media transformation, analytics, ranking, summarization, enrichment, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 1 in metadata/description/examples, declare OAuth-required access, require `part`, require exactly one selector from `playlistId` or `id`, allow paging only for `playlistId`, reject unsupported request fields before execution, avoid leaking OAuth tokens/raw diagnostics in results or errors, and keep implementation in a focused playlist-images Layer 2 resource-family module with no Layer 1 behavior changes unless tests reveal a metadata export gap  
**Scale/Scope**: One public MCP tool (`playlistImages_list`), one new Layer 2 playlist-images resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-228 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-128 wrapper and YT-228 seed agree on quota cost `1`, OAuth-required access, required `part`, exclusive `playlistId` or `id` selectors, paging only for `playlistId`, unsupported modifier rejection, and empty-result success behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlistImages_list` contract builder, descriptor builder, handler builder, argument validator, part helper, selector helper, paging helper, auth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, missing selectors, conflicting selectors, paging on `id`, empty page tokens, out-of-range page sizes, unsupported optional fields, missing OAuth access, authorization failures, empty successful results, quota failures, upstream invalid requests, endpoint unavailable, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlistImages_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlist_images.py      # Existing Layer 1 list wrapper dependency from YT-128
├── tools/
│   ├── dispatcher.py           # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py         # Public exports for playlistImages_list symbols
│       ├── contracts.py        # Existing shared contract primitives
│       ├── examples.py         # Representative shared contract set, if catalog export requires update
│       ├── families.py         # Existing playlist_images family placement metadata
│       └── playlist_images.py  # New Layer 2 playlist-images family; add contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_playlist_images_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_playlist_images_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_playlist_images.py
```

**Structure Decision**: Add a concrete `playlist_images` Layer 2 resource-family module because `playlist_images` already exists in shared family metadata and Layer 1 resource modules, but no public Layer 2 module exists yet. This keeps playlist-image listing separate from playlist-image mutation, playlist items, playlists, thumbnails, media upload, and higher-level workflow modules while matching existing one-family module patterns.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlistImages.list` quota, auth mode, required `part`, supported selectors, selector-specific paging, unsupported modifier boundary, response shape, and documented error categories.
- Confirm existing YT-128 Layer 1 wrapper availability and whether the public YT-228 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, and example conventions in the local codebase.
- Compare existing read/list tools, especially `membershipsLevels_list`, `members_list`, `commentThreads_list`, `comments_list`, and `channelSections_list`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported part values, selector behavior, paging bounds, registration surface, safe error categories, examples, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist-image mutation, media upload, playlist management, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/data-model.md)
- [contracts/playlistImages_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/contracts/playlistImages_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, near-raw result shape, OAuth and quota caveats, exclusive selector validation, selector-specific paging, unsupported modifier rejection, empty-result interpretation, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlistImages_list`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required access disclosure, quota accuracy, selector boundaries, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Playlist Images Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlistImages_list` is absent until implemented, requires `part`, requires exactly one selector from `playlistId` or `id`, invokes the Layer 1 list wrapper once with OAuth-required auth, and maps success to a playlist-image list result with endpoint, quota cost 1, requested parts, selector context, paging context when present, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, selector helper, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful OAuth-backed playlist-image retrieval.

**Refactor**: Align naming, docstrings, helper reuse, selector caveats, and error mapping with `membershipsLevels_list`, `members_list`, and existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Authorization, Selectors, and Parts Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, OAuth-required auth disclosure, required part selection, `playlistId` and `id` selector guidance, selector-specific paging, response boundary, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for playlist-scoped retrieval, direct image lookup, empty success, missing part, invalid part, missing selector, conflicting selector, unsupported paging/modifier, authorization failure, and out-of-scope image-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific selector, paging, quota, and OAuth guidance reviewable in `playlist_images.py`.

### User Story 3 - Reject Invalid Playlist Image List Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, blank or unsupported `part`, missing selector, both selectors, paging with `id`, blank `pageToken`, non-integer or out-of-range `maxResults`, unsupported optional parameters, missing OAuth access, authorization failure, quota failure, endpoint unavailable, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, stack traces, raw details, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlist_images_contract.py`, `tests/integration/test_youtube_playlist_images_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLIST_IMAGES_LIST_*` symbols, add `build_playlist_images_list_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlist_images.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist image insertion/update/delete, playlist items, playlists, thumbnails, media transfer, analytics, recommendations, search, or higher-level workflow modules.

## Risk and Mitigation

- **Selector ambiguity risk**: The tool must require exactly one selector from `playlistId` or `id`. Tests and examples must prove missing and conflicting selectors fail before execution.
- **Paging-boundary risk**: Paging belongs only to playlist-scoped `playlistId` retrieval. Unit and contract tests must reject `pageToken` or `maxResults` for `id` lookup and invalid paging values.
- **Access risk**: Playlist image retrieval is OAuth-required in the local Layer 1 contract. Metadata, examples, errors, and quickstart validation must make OAuth-required access visible and must not imply API-key-only lookup support.
- **Empty-result ambiguity risk**: A valid OAuth-backed request may return no playlist images. Result mapping and examples must preserve empty collections as successful outcomes distinct from invalid, inaccessible, or missing-resource requests.
- **Scope risk**: Do not add playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist-image details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlistImages_list` should live in a dedicated `playlist_images` Layer 2 module, not in playlist items, playlists, thumbnails, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlist_images_contract.py tests/unit/test_youtube_playlist_images.py tests/integration/test_youtube_playlist_images_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
