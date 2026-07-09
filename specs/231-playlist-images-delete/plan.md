# Implementation Plan: Layer 2 Tool `playlistImages_delete`

**Branch**: `231-playlist-images-delete` | **Date**: 2026-07-09 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlistImages_delete` for the YouTube Data API `playlistImages.delete` endpoint. The implementation will extend the existing playlist-images Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, reuse the existing Layer 1 `build_playlist_images_delete_wrapper()` from YT-131, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, destructive request validation, mutation acknowledgment shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires one `id`, costs 50 official quota units per call, requires OAuth-backed access, returns a deletion acknowledgment with target context, and does not add playlist image listing, insertion, update, media upload, thumbnail management, playlist management, analytics, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing playlist-images Layer 2 module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`; existing Layer 1 `playlistImages.delete` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, deletion acknowledgments, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlist-images delete contract builders, descriptor builders, handler builders, argument validators, auth-context helpers, deletion acknowledgment mappers, upstream-error mappers, local default transport/executor helpers, any touched Layer 1 wrapper helper, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist-image delete request performs one Layer 1 wrapper call and constant-time local validation; no playlist traversal, upload processing, thumbnail activation, analytics, ranking, summarization, enrichment, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 50 in metadata/description/examples, declare OAuth-required access, require `id`, reject unsupported request fields before execution, avoid leaking OAuth tokens/raw diagnostics in results or errors, keep implementation in the existing playlist-images Layer 2 module, and avoid Layer 1 behavior changes unless tests reveal a metadata export gap  
**Scale/Scope**: One public MCP tool (`playlistImages_delete`), additive extension to the existing playlist-images Layer 2 resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-231 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-131 wrapper and YT-231 seed agree on quota cost `50`, OAuth-required access, required `id`, unsupported modifier rejection, destructive no-body acknowledgment behavior, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlistImages_delete` contract builder, descriptor builder, handler builder, argument validator, auth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `id`, invalid `id`, unsupported optional fields, missing OAuth access, authorization failures, quota failures, upstream invalid requests, missing-resource failures, endpoint unavailable, destructive no-body success, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlistImages_delete.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlist_images.py      # Existing Layer 1 delete wrapper dependency from YT-131
├── tools/
│   ├── dispatcher.py           # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py         # Public exports for playlistImages_delete symbols
│       ├── contracts.py        # Existing shared contract primitives
│       ├── examples.py         # Representative shared contract set, if catalog export requires update
│       ├── families.py         # Existing playlist_images family placement metadata
│       └── playlist_images.py  # Existing Layer 2 playlist-images family; add delete contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `playlist_images` Layer 2 resource-family module because YT-228 through YT-230 already use it for `playlistImages_list`, `playlistImages_insert`, and `playlistImages_update`, Layer 1 resource modules use the same family name, and this slice belongs to the same upstream `playlistImages` resource. This keeps playlist-image delete separate from playlist items, playlists, thumbnails, and higher-level workflow modules while avoiding a second resource-family module for one endpoint.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlistImages.delete` quota, auth mode, required `id`, unsupported modifier boundary, response shape, and documented error categories.
- Confirm existing YT-131 Layer 1 wrapper availability and whether the public YT-231 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, mutation acknowledgment, error, availability, and example conventions in the local codebase.
- Compare existing delete and mutation tools, especially `comments_delete`, `channelSections_delete`, `captions_delete`, and the existing `playlistImages_update` module, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported identifier shape, registration surface, destructive acknowledgment shape, safe error categories, examples, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist-image listing, insertion, update, upload, thumbnail activation, playlist management, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/data-model.md)
- [contracts/playlistImages_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/contracts/playlistImages_delete.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/231-playlist-images-delete/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, destructive acknowledgment result shape, OAuth and quota caveats, identifier validation, unsupported modifier rejection, no-body success behavior, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlistImages_delete`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required access disclosure, quota accuracy, identifier validation, destructive acknowledgment behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Delete Playlist Images Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlistImages_delete` is absent until implemented, requires `id`, invokes the Layer 1 delete wrapper once with OAuth-required auth, and maps success to a deletion acknowledgment result with endpoint, quota cost 50, target identifier context, auth context, and mutation outcome.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local delete transport, default executor, public exports, and dispatcher registration needed for successful OAuth-backed playlist-image deletion.

**Refactor**: Align naming, docstrings, helper reuse, destructive caveats, and error mapping with `comments_delete`, `channelSections_delete`, `captions_delete`, and existing playlist-image mutation conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Authorization, and Delete Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required auth disclosure, required identifier, destructive response boundary, no-body acknowledgment behavior, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful OAuth-backed deletion, successful no-body deletion acknowledgment, missing identifier, invalid identifier, unsupported input, authorization failure, missing-resource or quota upstream failure, and out-of-scope image-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific identifier, quota, OAuth, destructive, no-body acknowledgment, and unsupported-input guidance reviewable in `playlist_images.py`.

### User Story 3 - Reject Invalid Playlist Image Delete Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, blank `id`, non-string `id`, unsupported body/part/media/paging/listing inputs, missing OAuth access, authorization failure, quota failure, missing resource, endpoint unavailable, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlist_images_contract.py`, `tests/integration/test_youtube_playlist_images_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLIST_IMAGES_DELETE_*` symbols, add `build_playlist_images_delete_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlist_images.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist image list/insert/update, playlist items, playlists, thumbnails, media transfer infrastructure, analytics, recommendations, search, or higher-level workflow modules.

## Risk and Mitigation

- **Destructive action risk**: The tool deletes playlist images. Metadata, examples, quickstart, and validation must make the destructive nature visible before invocation.
- **Access risk**: Playlist image deletion is OAuth-required. Metadata, examples, errors, and quickstart validation must make OAuth-required access visible and must not imply API-key-only support.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Acknowledgment ambiguity risk**: Successful delete may not return a deleted resource body. The result mapper must provide explicit deletion acknowledgment with target identifier context without fabricating resource fields.
- **Target identity risk**: The request must clearly identify one playlist image to delete; missing or conflicting target identity must fail locally instead of becoming an ambiguous upstream mutation.
- **Scope risk**: Do not add playlist image listing, insertion, update, media upload, thumbnail activation, playlist management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist-image details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlistImages_delete` should live in the existing `playlist_images` Layer 2 module, not in playlist items, playlists, thumbnails, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlist_images_contract.py tests/unit/test_youtube_playlist_images.py tests/integration/test_youtube_playlist_images_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
