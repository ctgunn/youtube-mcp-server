# Implementation Plan: Layer 2 Tool `videos_getRating`

**Branch**: `251-videos-get-rating` | **Date**: 2026-07-22 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videos_getRating` for the YouTube endpoint operation `videos.getRating`. The implementation will extend the existing videos Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, reuse the existing Layer 1 `build_videos_get_rating_wrapper()` from YT-151, and follow YT-201/YT-202 shared contract conventions for naming, 1-unit quota disclosure, OAuth-only access disclosure, comma-separated video identifier validation, optional eligible content-owner delegation, no-request-body behavior, per-video rating lookup result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and read-oriented: it requires `id`, supports one to fifty comma-delimited video IDs, may accept `onBehalfOfContentOwner` only for eligible partner OAuth contexts, requires OAuth for every request, rejects request bodies and unsupported modifiers before execution, preserves returned ratings `like`, `dislike`, `none`, and `unspecified`, treats unrated or unspecified states as successful lookup outcomes, and does not add rating mutation, rating history, aggregate like/dislike counts, video metadata lookup or update, upload, deletion, abuse reporting, thumbnail management, captions, playlists, comments, transcripts, analytics, recommendations, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing videos Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`; existing Layer 1 `videos.getRating` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`; existing Layer 1 videos validators and response normalizers under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/videos.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, rating lookup results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including videos get-rating contract builders, descriptor builders, handler builders, argument validators, identifier helpers, OAuth/delegation-context helpers, result mappers, upstream-error mappers, local default executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single video-rating lookup invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 1-unit quota cost, OAuth requirement, supported identifier boundary, optional partner delegation caveat, returned rating values, no-request-body boundary, and per-video lookup result shape in under 1 minute; no mutation, transcript retrieval, analytics lookup, recommendation, ranking, summarization, enrichment, bulk workflow, media transfer, or multi-endpoint workflow is introduced  
**Constraints**: Preserve endpoint lookup semantics, expose quota cost 1 in metadata/description/examples, require OAuth-only access, require non-empty `id`, support one to fifty comma-separated video identifiers, accept `onBehalfOfContentOwner` only as the documented partner OAuth delegation field if supported by Layer 1, reject request bodies and unsupported fields before execution, map success to per-video rating lookup outcomes rather than a refreshed video resource, distinguish `none` and `unspecified` from failures, avoid leaking API keys, OAuth tokens, authorization details, raw upstream diagnostics, stack traces, or unsafe request context in results or errors, keep changes under the videos Layer 2 family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videos_getRating`), endpoint-specific additions to the existing videos Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-251 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-151 wrapper dependency, YT-251 seed requirements, official endpoint behavior, shared Layer 2 contracts, and existing videos module pattern into one endpoint-specific `videos_getRating` plan with quota cost `1`, OAuth-only access, required `id`, optional partner-only `onBehalfOfContentOwner` where supported, one-to-fifty comma-delimited identifier support, no request body, safe per-video result shaping, and distinct validation/access/quota/not-found/policy/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videos_getRating` contract builder, descriptor builder, handler builder, argument validator, identifier helper, auth-context helper, delegation-context helper if added, result mapper, upstream-error mapper, local default executor, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `id`, empty or non-string `id`, duplicate identifiers, more than fifty identifiers, unsupported identifier forms, request body rejection, unsupported top-level fields, invalid partner delegation values, missing OAuth, API-key-only access, successful `like`, `dislike`, `none`, and `unspecified` lookup outcomes, partial or empty returned item handling, quota failure, access failure, not-found failure, endpoint unavailable, deprecated endpoint behavior, upstream invalid request, out-of-scope mutation/history/count/update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment requests, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos_getRating.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   ├── videos.py                         # Existing Layer 1 getRating wrapper dependency from YT-151
│   ├── validators/videos.py              # Existing Layer 1 videos.getRating validation dependency
│   └── response_normalizers/videos.py    # Existing Layer 1 videos.getRating result normalization dependency
├── tools/
│   ├── dispatcher.py                     # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                   # Public exports for videos_getRating symbols
│       ├── contracts.py                  # Existing shared contract primitives
│       ├── conventions.py                # Existing response/error boundary helpers
│       ├── examples.py                   # Representative shared contract set; add concrete videos_getRating contract if needed
│       ├── families.py                   # Existing videos family placement metadata
│       └── videos.py                     # Existing Layer 2 family; add getRating contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `videos.py` Layer 2 resource-family module because YT-247 through YT-250 established videos family placement, YT-151 provides the matching Layer 1 resource wrapper, and YT-251 should remain separate from rating mutation, search, captions, thumbnails, playlists, comments, analytics, recommendations, and higher-level workflows. This keeps the public tool cohesive with the upstream `videos` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current official `videos.getRating` quota, OAuth mode, required inputs, optional partner delegation, no-request-body behavior, response body structure, returned rating values, and documented error categories.
- Confirm existing YT-151 Layer 1 wrapper availability and whether the public YT-251 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, read-result, and example conventions in the local codebase.
- Confirm current videos Layer 2 family placement and how to add `videos_getRating` beside `videos_list`, `videos_insert`, `videos_update`, and `videos_rate` in the existing `youtube_common/videos.py` module.
- Confirm how to add any representative `videos_getRating` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing read tools, especially `videos_list`, `channels_list`, `comments_list`, and the YT-151 response normalizer, to choose the smallest consistent per-video lookup result shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, OAuth handling, optional partner delegation handling, videos family placement, registration surface, lookup result shape, safe error categories, examples, no-body rules, returned rating-state semantics, unsupported field rejection, official endpoint caveats, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into rating mutation, rating history, aggregate rating counts, metadata lookup or update, media upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/data-model.md)
- [contracts/videos_getRating.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/contracts/videos_getRating.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, video rating lookup request contract, per-video rating result shape, OAuth and quota caveats, `id` validation, optional partner delegation validation, request-body rejection, unsupported modifier rejection, safe error categories, and no mutation/history/count/update/upload/delete/analytics/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videos_getRating`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, identifier boundaries, optional partner delegation caveats, no-request-body behavior, per-video lookup result behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Look Up Viewer Rating State Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `videos_getRating` is absent until implemented, requires non-empty `id`, accepts only one to fifty unique comma-separated video IDs, invokes the Layer 1 get-rating wrapper once with OAuth context, and maps successful responses to per-video lookup results with endpoint, quota cost 1, requested video identities, returned ratings, access context, availability state, and lookup details.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, identifier-context helper, auth-context helper, result mapper, default local executor, public exports, and dispatcher registration needed for successful rating lookup.

**Refactor**: Align naming, docstrings, helper reuse, per-video result mapping, and error mapping with existing Layer 2 read tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Quota, OAuth, and Lookup Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `id`, one-to-fifty identifier boundary, optional partner delegation caveat, returned rating values `like`, `dislike`, `none`, and `unspecified`, no request body, per-video result shape, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized single-video lookup, authorized multi-video lookup, optional delegated partner lookup if supported, unrated or unspecified successful lookup, missing identity failure, duplicate or over-limit identifier failure, missing OAuth failure, quota or upstream failure, unavailable target failure, and out-of-scope workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required inputs, identifier rules, returned rating-state rules, delegation caveats, no-body rules, and unsupported-input guidance reviewable in `videos.py`.

### User Story 3 - Reject Invalid or Unsupported Rating-Lookup Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, blank or non-string `id`, duplicate IDs, over-limit ID count, malformed comma-delimited IDs, supplied `body`, unsupported top-level fields, invalid `onBehalfOfContentOwner`, rating mutation fields, rating history fields, aggregate count fields, metadata fields, update fields, upload fields, delete fields, abuse-report fields, thumbnail/caption/playlist/comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, forbidden or policy failure, not-found failure, deprecated behavior, successful unrated or unspecified result, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, optional partner delegation pass-through if supported by Layer 1, rating lookup context extraction, per-video result extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the official endpoint request shape.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_videos_contract.py`, `tests/integration/test_youtube_videos_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEOS_GET_RATING_*` or project-consistent `VIDEOS_GETRATING_*` symbols, import and use `build_videos_get_rating_wrapper()`, add `build_videos_get_rating_tool_descriptor()` to the default registry, and add representative contract/example coverage while preserving the public tool name `videos_getRating`.

**Refactor**: Keep `videos.py` cohesive, keep Layer 1 changes narrow, and avoid changes to search, captions, video categories, thumbnails, playlists, comments, rating mutation, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Viewer-specific data risk**: Rating lookup returns authorized viewer state. Validation and metadata must require OAuth and avoid presenting the result as public video data.
- **Unrated-state risk**: `none` and `unspecified` are successful returned states. Result mapping must distinguish them from missing items, not-found errors, validation failures, and access failures.
- **Quota risk**: Each invocation costs 1 quota unit. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `1`.
- **Access risk**: Video rating lookup is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, or credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **Identifier-boundary risk**: The official endpoint accepts a comma-separated `id` list. The public tool must document and enforce the one-to-fifty unique identifier boundary rather than silently accepting ambiguous or unbounded input.
- **Delegation risk**: `onBehalfOfContentOwner` is partner-only. If exposed, it must be documented as eligible OAuth delegation context and rejected when malformed or unsupported.
- **Scope risk**: Do not add rating mutation, rating history, aggregate rating counts, metadata lookup or update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `videos_getRating` should live in the existing videos Layer 2 module, not in search, captions, thumbnails, playlists, comments, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
