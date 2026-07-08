# Implementation Plan: Layer 2 Tool `playlistImages_insert`

**Branch**: `229-playlist-images-insert` | **Date**: 2026-07-08 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `playlistImages_insert` for the YouTube Data API `playlistImages.insert` media-upload endpoint. The implementation will extend the existing playlist-images Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, reuse the existing Layer 1 `build_playlist_images_insert_wrapper()` from YT-129, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, upload-sensitive request validation, mutation result shaping, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and narrow: it requires `part`, requires a `body` metadata payload, requires a `media` upload payload, costs 50 official quota units per call, requires OAuth-backed access, preserves returned playlist-image fields without enrichment, and does not add playlist image listing, update, deletion, thumbnail replacement, playlist management, analytics, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing playlist-images Layer 2 module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`; existing Layer 1 `playlistImages.insert` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, upload descriptors, mutation results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including playlist-images insert contract builders, descriptor builders, handler builders, argument validators, part/body/media helpers, auth-context helpers, mutation result mappers, upstream-error mappers, local default transport/executor helpers, any touched Layer 1 wrapper helper, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single playlist-image insert request performs one Layer 1 wrapper call and constant-time local validation; no playlist traversal, image transformation, thumbnail activation, analytics, ranking, summarization, enrichment, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 50 in metadata/description/examples, declare OAuth-required access, require `part`, require `body` metadata, require `media` upload content, reject unsupported request fields before execution, avoid leaking OAuth tokens/raw upload bytes/raw diagnostics in results or errors, keep implementation in the existing playlist-images Layer 2 module, and avoid Layer 1 behavior changes unless tests reveal a metadata export gap  
**Scale/Scope**: One public MCP tool (`playlistImages_insert`), additive extension to the existing playlist-images Layer 2 resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-229 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-129 wrapper and YT-229 seed agree on quota cost `50`, OAuth-required access, required `part`, required `body` metadata, required `media` upload content, unsupported modifier rejection, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `playlistImages_insert` contract builder, descriptor builder, handler builder, argument validator, part helper, body helper, media helper, auth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, missing `body`, invalid `body`, missing `media`, invalid or unsupported `media`, unsupported optional fields, missing OAuth access, authorization failures, quota failures, upstream invalid requests, media eligibility failures, endpoint unavailable, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlistImages_insert.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── playlist_images.py      # Existing Layer 1 insert wrapper dependency from YT-129
├── tools/
│   ├── dispatcher.py           # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py         # Public exports for playlistImages_insert symbols
│       ├── contracts.py        # Existing shared contract primitives
│       ├── examples.py         # Representative shared contract set, if catalog export requires update
│       ├── families.py         # Existing playlist_images family placement metadata
│       └── playlist_images.py  # Existing Layer 2 playlist-images family; add insert contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `playlist_images` Layer 2 resource-family module because YT-228 already created the family module for `playlistImages_list`, Layer 1 resource modules use the same family name, and this slice belongs to the same upstream `playlistImages` resource. This keeps playlist-image insertion separate from playlist items, playlists, thumbnails, and higher-level workflow modules while avoiding a second resource-family module for one endpoint.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `playlistImages.insert` quota, auth mode, required `part`, required metadata body, required media upload, unsupported modifier boundary, response shape, and documented error categories.
- Confirm existing YT-129 Layer 1 wrapper availability and whether the public YT-229 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, mutation response, upload, error, availability, and example conventions in the local codebase.
- Compare existing media-upload and mutation tools, especially `channelBanners_insert`, `captions_insert`, `comments_insert`, and `channelSections_insert`, plus the existing `playlistImages_list` module, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported part values, body shape, media shape, registration surface, safe error categories, examples, upload-sensitive result shape, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into playlist-image listing, update, deletion, thumbnail activation, playlist management, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/data-model.md)
- [contracts/playlistImages_insert.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/contracts/playlistImages_insert.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, near-raw mutation result shape, OAuth and quota caveats, required body and media validation, unsupported modifier rejection, safe upload descriptors, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `playlistImages_insert`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required access disclosure, quota accuracy, upload boundaries, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Insert Playlist Images Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `playlistImages_insert` is absent until implemented, requires `part`, requires `body`, requires `media`, invokes the Layer 1 insert wrapper once with OAuth-required auth, and maps success to a created playlist-image result with endpoint, quota cost 50, requested parts, body context, upload context, auth context, and returned resource fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, body helper, media helper, result mapper, default local insert transport, default executor, public exports, and dispatcher registration needed for successful OAuth-backed playlist-image insertion.

**Refactor**: Align naming, docstrings, helper reuse, media caveats, and error mapping with `channelBanners_insert`, `captions_insert`, and existing playlist-image list conventions; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Authorization, and Upload Requirements Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required auth disclosure, required part selection, required metadata body, required media upload, response boundary, mutation semantics, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for successful OAuth-backed insertion, missing part, invalid part, missing body, invalid body, missing media, unsupported media, authorization failure, quota or upstream insertion failure, and out-of-scope image-management request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific body, media, quota, and OAuth guidance reviewable in `playlist_images.py`.

### User Story 3 - Reject Invalid Playlist Image Insert Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, blank or unsupported `part`, missing `body`, body without required playlist-image metadata, unsupported body fields, missing `media`, media without `mimeType` or `content`, unsupported media MIME types, unsafe raw media exposure, unsupported optional parameters, missing OAuth access, authorization failure, quota failure, media eligibility failure, endpoint unavailable, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, stack traces, raw media content, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_playlist_images_contract.py`, `tests/integration/test_youtube_playlist_images_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `PLAYLIST_IMAGES_INSERT_*` symbols, add `build_playlist_images_insert_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `playlist_images.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlist image list/update/delete, playlist items, playlists, thumbnails, media transfer infrastructure, analytics, recommendations, search, or higher-level workflow modules.

## Risk and Mitigation

- **Upload-boundary risk**: The tool must require a metadata body and media upload content. Tests and examples must prove metadata-only, upload-only, missing-media, malformed-media, and unsupported-media requests fail before execution.
- **Access risk**: Playlist image insertion is OAuth-required. Metadata, examples, errors, and quickstart validation must make OAuth-required access visible and must not imply API-key-only support.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Mutation ambiguity risk**: Successful insertion should preserve created playlist-image fields and operation context, while upstream rejections remain distinct from local validation failures and access failures.
- **Scope risk**: Do not add playlist image listing, update, deletion, thumbnail activation, playlist management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose OAuth tokens, raw upload bytes, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive playlist-image details in failures, logs, metadata, or examples.
- **Cohesion risk**: `playlistImages_insert` should live in the existing `playlist_images` Layer 2 module, not in playlist items, playlists, thumbnails, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_playlist_images_contract.py tests/unit/test_youtube_playlist_images.py tests/integration/test_youtube_playlist_images_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
