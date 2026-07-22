# Implementation Plan: Layer 2 Tool `videos_insert`

**Branch**: `248-videos-insert` | **Date**: 2026-07-21 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videos_insert` for the YouTube endpoint operation `videos.insert`. The implementation will extend the existing videos Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, reuse the existing Layer 1 `build_videos_insert_wrapper()` from YT-148, and follow YT-201/YT-202 shared contract conventions for naming, 1600-unit quota disclosure, OAuth-only access disclosure, media-upload validation, near-raw created-resource result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and upload-oriented: it requires `part`, `body`, and `media`, supports only the upload modes and optional request fields exposed by the Layer 1 dependency, requires OAuth for every request, surfaces media-constrained or release-limited availability caveats, and does not add automatic publishing, post-upload editing, thumbnails, captions, playlists, comments, ratings, transcripts, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint workflows.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing videos Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`; existing Layer 1 `videos.insert` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, upload descriptors, created-video results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including videos insert contract builders, descriptor builders, handler builders, argument validators, part-selection helpers, body/media validators, upload-mode helpers, auth-context helpers, result mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single video-insert invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 1600-unit quota cost, OAuth requirement, media-upload requirement, and availability caveats in under 1 minute; no search, transcript lookup, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, or multi-endpoint publishing workflow is introduced  
**Constraints**: Preserve endpoint creation semantics, expose quota cost 1600 in metadata/description/examples, require OAuth-only access, require non-empty `part`, `body`, and `media`, preserve supported `uploadMode` values from the Layer 1 wrapper, treat `notifySubscribers` and `onBehalfOfContentOwner` as optional only where supported, reject unsupported fields and out-of-scope modifiers before execution, avoid leaking API keys, OAuth tokens, authorization details, raw media payloads, signed URLs, raw upstream diagnostics, stack traces, or unsafe request context in results or errors, keep changes under the videos Layer 2 family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videos_insert`), endpoint-specific additions to the existing videos Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-248 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-148 wrapper dependency, YT-248 seed requirements, shared Layer 2 contracts, and existing `videos_list` module pattern into one endpoint-specific `videos_insert` plan with quota cost `1600`, OAuth-only access, required `part` plus `body` plus `media`, supported `uploadMode` values `multipart` and `resumable`, optional `notifySubscribers` and `onBehalfOfContentOwner` when supported, media-constrained availability caveats, safe upload result shaping, and distinct validation/access/quota/upload/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videos_insert` contract builder, descriptor builder, handler builder, argument validator, part helper, body helper, media helper, upload-mode helper, delegation helper, auth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, empty or non-string `part`, missing `body`, incomplete `body`, missing `media`, incomplete `media`, unsupported `uploadMode`, unsupported top-level fields, missing OAuth, invalid delegation context, safe media summary behavior, raw media and secret sanitization, quota failures, upstream invalid requests, authorization failures, policy or availability refusals, endpoint unavailable, deprecated endpoint behavior, sparse created-resource shaping, and out-of-scope publishing/editing/enrichment requests.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos_insert.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   ├── videos.py                       # Existing Layer 1 insert wrapper dependency from YT-148
│   └── validators/videos.py            # Existing Layer 1 videos.insert validation dependency
├── tools/
│   ├── dispatcher.py                   # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                 # Public exports for videos_insert symbols
│       ├── contracts.py                # Existing shared contract primitives
│       ├── conventions.py              # Existing response/error boundary helpers
│       ├── examples.py                 # Representative shared contract set; add concrete videos_insert contract if needed
│       ├── families.py                 # Existing videos family placement metadata
│       └── videos.py                   # Existing Layer 2 family; add insert contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `videos.py` Layer 2 resource-family module because YT-247 already established videos family placement, YT-148 provides the matching Layer 1 resource wrapper, and YT-248 should remain separate from search, captions, thumbnails, playlists, comments, ratings, analytics, recommendations, and higher-level publishing workflow modules. This keeps the public tool cohesive with the upstream `videos` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `videos.insert` quota, OAuth mode, required `part`, required `body`, required `media`, supported upload modes, optional request fields, response shape, caveat notes, and documented error categories.
- Confirm existing YT-148 Layer 1 wrapper availability and whether the public YT-248 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, media-upload, mutation result, and example conventions in the local codebase.
- Confirm current videos Layer 2 family placement and how to add `videos_insert` beside `videos_list` in the existing `youtube_common/videos.py` module.
- Confirm how to add any representative `videos_insert` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing upload/mutation tools, especially `captions_insert`, `playlistImages_insert`, `channelBanners_insert`, `thumbnails_set`, `playlists_insert`, and `videos_list`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, OAuth handling, videos family placement, registration surface, created-video result shape, safe error categories, examples, media-upload constraints, unsupported modifier rejection, availability caveats, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into automatic publishing, video update, delete, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/data-model.md)
- [contracts/videos_insert.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/contracts/videos_insert.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, video creation request contract, created-video result shape, OAuth and quota caveats, `part` validation, `body` validation, `media` validation, upload-mode validation, delegation validation, unsupported modifier rejection, safe media summary behavior, safe error categories, and no publishing/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videos_insert`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, media-upload boundaries, created-resource response behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Create Videos Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `videos_insert` is absent until implemented, requires non-empty `part`, `body`, and `media`, invokes the Layer 1 insert wrapper once with OAuth context, and maps success to a created-video result with endpoint, quota cost 1600, requested parts, upload context, access context, availability context, mutation outcome details, and returned video fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, part helper, body helper, media helper, upload-mode helper, auth-context helper, result mapper, default local insert transport, default executor, public exports, and dispatcher registration needed for successful video creation.

**Refactor**: Align naming, docstrings, helper reuse, upload handling, created-resource mapping, and error mapping with existing Layer 2 upload/mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, Upload, and Availability Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1600 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `part`, required `body`, required `media`, supported upload modes, optional delegation guidance, media-constrained availability state, audit/private-default caveat visibility, created-resource result shape, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized video creation, supported media upload, optional delegated content-owner context, metadata-only failure, media-only failure, missing OAuth failure, unsupported upload option failure, quota or upstream failure, availability-constrained behavior, and out-of-scope workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required inputs, upload rules, availability caveats, and unsupported-input guidance reviewable in `videos.py`.

### User Story 3 - Reject Unsupported Video Creation Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, empty or non-string `part`, missing `body`, incomplete `body`, missing `media`, incomplete `media`, unsupported `uploadMode`, invalid `notifySubscribers`, invalid `onBehalfOfContentOwner`, unsupported top-level fields, automatic publishing instructions, update/delete instructions, rating mutation instructions, thumbnail/caption/playlist/comment instructions, transcript instructions, analytics instructions, recommendation fields, ranking fields, summarization fields, enrichment fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, policy or availability refusal, deprecated behavior, sparse upstream success, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, upload context extraction, body/media context extraction, created-video context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw media payloads, signed URLs, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_videos_contract.py`, `tests/integration/test_youtube_videos_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEOS_INSERT_*` symbols, add `build_videos_insert_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `videos.py` cohesive, keep Layer 1 changes narrow, and avoid changes to search, captions, video categories, thumbnails, playlists, comments, rating mutations, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Quota risk**: Each invocation costs 1600 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `1600` and high-cost guidance.
- **Access risk**: Video creation is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, or delegated-owner credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **Upload risk**: `body` and `media` are both required. Validation must reject metadata-only and media-only requests before execution and keep raw media payloads out of public metadata, examples, logs, and errors.
- **Availability risk**: Upload behavior may be media-constrained, release-gated, audit-constrained, private-by-default, or policy-limited. Metadata and errors must make those boundaries visible without inventing a separate workflow.
- **Result-shaping risk**: Successful creation returns a single created video resource, not a collection. Result mapping must preserve returned fields and avoid fabricated publication state, processing state, analytics, or enrichment.
- **Scope risk**: Do not add automatic publishing, video metadata update, deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw media payloads, signed URLs, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `videos_insert` should live in the existing videos Layer 2 module, not in search, captions, thumbnails, playlists, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
