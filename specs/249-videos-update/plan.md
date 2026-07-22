# Implementation Plan: Layer 2 Tool `videos_update`

**Branch**: `249-videos-update` | **Date**: 2026-07-22 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videos_update` for the YouTube endpoint operation `videos.update`. The implementation will extend the existing videos Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, reuse the existing Layer 1 `build_videos_update_wrapper()` from YT-149, and follow YT-201/YT-202 shared contract conventions for naming, 50-unit quota disclosure, OAuth-only access disclosure, writable-part validation, near-raw updated-resource result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and mutation-oriented: it requires `part`, `body.id`, and a compatible update body, initially supports the locally available `part=snippet` update path with `body.snippet.title`, requires OAuth for every request, rejects read-only or unsupported update fields before execution, preserves replacement-oriented update semantics for included writable parts, and does not add media upload, media replacement, transcoding, automatic publishing workflows, creation, deletion, rating mutation, thumbnail management, captions, playlists, comments, transcripts, analytics, recommendations, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing videos Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`; existing Layer 1 `videos.update` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`; existing Layer 1 videos validators under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, update body context, updated-video results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including videos update contract builders, descriptor builders, handler builders, argument validators, part-selection helpers, update-body validators, writable-field helpers, OAuth-context helpers, delegation helpers, result mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single video-update invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 50-unit quota cost, OAuth requirement, writable-part boundary, and replacement-oriented update semantics in under 1 minute; no search, transcript lookup, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, media transfer, or multi-endpoint publishing workflow is introduced  
**Constraints**: Preserve endpoint update semantics, expose quota cost 50 in metadata/description/examples, require OAuth-only access, require non-empty `part` plus update `body`, initially support the local Layer 1 path `part=snippet` with `body.id` and `body.snippet.title`, reject unsupported writable parts and read-only fields before execution, reject unsupported fields and out-of-scope modifiers before execution, avoid leaking API keys, OAuth tokens, authorization details, raw upstream diagnostics, stack traces, or unsafe request context in results or errors, keep changes under the videos Layer 2 family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videos_update`), endpoint-specific additions to the existing videos Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-249 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-149 wrapper dependency, YT-249 seed requirements, shared Layer 2 contracts, and existing videos module pattern into one endpoint-specific `videos_update` plan with quota cost `50`, OAuth-only access, required `part` plus `body`, initial writable path `part=snippet` with `body.id` and `body.snippet.title`, safe updated-resource result shaping, and distinct validation/access/quota/not-found/policy/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videos_update` contract builder, descriptor builder, handler builder, argument validator, part helper, body helper, writable-field helper, delegation helper, auth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, empty or non-string `part`, unsupported `part`, missing `body`, missing `body.id`, missing `body.snippet`, missing `body.snippet.title`, unsupported `body` fields, unsupported `snippet` fields, missing OAuth, invalid delegation context, quota failures, upstream invalid requests, authorization failures, forbidden or policy failures, not-found failures, endpoint unavailable, deprecated endpoint behavior, sparse updated-resource shaping, replacement-semantics caveat visibility, out-of-scope upload/create/delete/rating/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment requests, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos_update.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   ├── videos.py                       # Existing Layer 1 update wrapper dependency from YT-149
│   └── validators/videos.py            # Existing Layer 1 videos.update validation dependency
├── tools/
│   ├── dispatcher.py                   # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                 # Public exports for videos_update symbols
│       ├── contracts.py                # Existing shared contract primitives
│       ├── conventions.py              # Existing response/error boundary helpers
│       ├── examples.py                 # Representative shared contract set; add concrete videos_update contract if needed
│       ├── families.py                 # Existing videos family placement metadata
│       └── videos.py                   # Existing Layer 2 family; add update contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_youtube_videos_contract.py
├── integration/
│   ├── test_youtube_tool_registration.py
│   └── test_youtube_videos_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_videos.py
```

**Structure Decision**: Extend the existing `videos.py` Layer 2 resource-family module because YT-247 and YT-248 established videos family placement, YT-149 provides the matching Layer 1 resource wrapper, and YT-249 should remain separate from search, captions, thumbnails, playlists, comments, ratings, analytics, recommendations, and higher-level publishing workflow modules. This keeps the public tool cohesive with the upstream `videos` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `videos.update` quota, OAuth mode, required `part`, required `body`, supported writable parts, supported update body fields, optional request fields, response shape, caveat notes, and documented error categories.
- Confirm existing YT-149 Layer 1 wrapper availability and whether the public YT-249 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, mutation result, writable-field, and example conventions in the local codebase.
- Confirm current videos Layer 2 family placement and how to add `videos_update` beside `videos_list` and `videos_insert` in the existing `youtube_common/videos.py` module.
- Confirm how to add any representative `videos_update` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing mutation tools, especially `videos_insert`, `channels_update`, `comments_update`, `playlistImages_update`, `playlistItems_update`, and `playlists_update`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, OAuth handling, videos family placement, registration surface, updated-resource result shape, safe error categories, examples, writable-part constraints, unsupported field rejection, replacement-semantics caveats, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into media upload, media replacement, automatic publishing workflow, video creation, deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/data-model.md)
- [contracts/videos_update.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/contracts/videos_update.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, video update request contract, updated-video result shape, OAuth and quota caveats, `part` validation, `body` validation, writable-field validation, delegation validation, unsupported modifier rejection, safe error categories, and no upload/publishing/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videos_update`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, writable-part/update-body boundaries, replacement-semantics caveats, updated-resource response behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Update Video Resources Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `videos_update` is absent until implemented, requires non-empty `part`, requires `body.id`, requires a compatible writable update body, invokes the Layer 1 update wrapper once with OAuth context, and maps success to an updated-video result with endpoint, quota cost 50, requested parts, update body context, access context, optional delegation context, mutation outcome details, and returned video fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, part helper, body helper, writable-field helper, delegation helper, auth-context helper, result mapper, default local update transport, default executor, public exports, and dispatcher registration needed for successful video update.

**Refactor**: Align naming, docstrings, helper reuse, update-body handling, updated-resource mapping, and error mapping with existing Layer 2 mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, Writable Parts, and Update Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `part`, required `body`, supported writable parts, replacement-oriented update semantics, optional delegation guidance, updated-resource result shape, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized metadata/status update, optional delegated content-owner context, missing identity failure, missing part failure, read-only or unsupported part failure, incompatible update body failure, missing OAuth failure, quota or upstream failure, and out-of-scope workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required inputs, writable-part rules, replacement semantics, and unsupported-input guidance reviewable in `videos.py`.

### User Story 3 - Reject Invalid or Unsupported Video Update Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, empty or non-string `part`, unsupported `part`, missing `body`, missing `body.id`, blank `body.id`, missing `body.snippet`, missing `body.snippet.title`, unsupported body fields, unsupported snippet fields, invalid `onBehalfOfContentOwner`, unsupported top-level fields, media upload fields, media replacement fields, automatic publishing instructions, create/delete instructions, rating mutation instructions, thumbnail/caption/playlist/comment instructions, transcript instructions, analytics instructions, recommendation fields, ranking fields, summarization fields, enrichment fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, forbidden or policy failure, not-found failure, deprecated behavior, sparse upstream success, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, update context extraction, writable-part context extraction, safe delegation context extraction, updated-video context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_videos_contract.py`, `tests/integration/test_youtube_videos_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEOS_UPDATE_*` symbols, add `build_videos_update_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `videos.py` cohesive, keep Layer 1 changes narrow, and avoid changes to search, captions, video categories, thumbnails, playlists, comments, rating mutations, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Mutation risk**: Video updates can alter existing resources. Validation must require explicit video identity, writable part selection, and compatible update body before execution.
- **Replacement-semantics risk**: Included writable parts may replace existing data in that section. Metadata, examples, and validation failures must make the update-body expectations visible before callers mutate a video.
- **Writable-field risk**: The local Layer 1 wrapper initially supports a narrow `snippet.title` update path. Layer 2 must reject unsupported parts and fields unless the Layer 1 contract is deliberately expanded.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Access risk**: Video update is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, or delegated-owner credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **Result-shaping risk**: Successful update returns a single updated video resource, not a collection. Result mapping must preserve returned fields and avoid fabricated media state, publication workflow state, analytics, recommendations, rankings, summaries, or enrichment.
- **Scope risk**: Do not add media upload, media replacement, transcoding, automatic publishing workflow, video creation, deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `videos_update` should live in the existing videos Layer 2 module, not in search, captions, thumbnails, playlists, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
