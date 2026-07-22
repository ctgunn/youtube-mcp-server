# Implementation Plan: Layer 2 Tool `videos_rate`

**Branch**: `250-videos-rate` | **Date**: 2026-07-22 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/spec.md)  
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videos_rate` for the YouTube endpoint operation `videos.rate`. The implementation will extend the existing videos Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, reuse the existing Layer 1 `build_videos_rate_wrapper()` from YT-150, and follow YT-201/YT-202 shared contract conventions for naming, 50-unit quota disclosure, OAuth-only access disclosure, supported rating-state validation, no-request-body behavior, mutation acknowledgment result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and mutation-oriented: it requires `id` and `rating`, supports `rating` values `like`, `dislike`, and `none`, treats `none` as an explicit clear-rating request, requires OAuth for every request, rejects request bodies and unsupported modifiers before execution, acknowledges successful no-content rating updates, and does not add current-rating lookup, rating history, aggregate rating counts, video metadata update, upload, deletion, abuse reporting, thumbnail management, captions, playlists, comments, transcripts, analytics, recommendations, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing videos Layer 2 family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`; existing Layer 1 `videos.rate` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`; existing Layer 1 videos validators under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, rating acknowledgment results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including videos rate contract builders, descriptor builders, handler builders, argument validators, rating-context helpers, OAuth-context helpers, result mappers, upstream-error mappers, local default executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single video-rating invocation performs local validation plus one Layer 1 wrapper call; a client developer can identify the 50-unit quota cost, OAuth requirement, supported rating values, clear-rating behavior, no-request-body boundary, and acknowledgment result shape in under 1 minute; no lookup, transcript retrieval, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, media transfer, or multi-endpoint workflow is introduced  
**Constraints**: Preserve endpoint rating semantics, expose quota cost 50 in metadata/description/examples, require OAuth-only access, require non-empty `id` plus supported `rating`, support only `like`, `dislike`, and `none`, reject request bodies and unsupported fields before execution, map success to an acknowledgment rather than a refreshed video resource, avoid leaking API keys, OAuth tokens, authorization details, raw upstream diagnostics, stack traces, or unsafe request context in results or errors, keep changes under the videos Layer 2 family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videos_rate`), endpoint-specific additions to the existing videos Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-250 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolves the local YT-150 wrapper dependency, YT-250 seed requirements, official endpoint behavior, shared Layer 2 contracts, and existing videos module pattern into one endpoint-specific `videos_rate` plan with quota cost `50`, OAuth-only access, required `id` plus `rating`, supported actions `like`, `dislike`, and `none`, explicit clear-rating semantics, no request body, safe acknowledgment result shaping, and distinct validation/access/quota/not-found/policy/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videos_rate` contract builder, descriptor builder, handler builder, argument validator, rating helper, auth-context helper, result mapper, upstream-error mapper, local default executor, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `id`, empty or non-string `id`, missing `rating`, empty or non-string `rating`, unsupported or differently cased `rating`, `rating=none` clear-rating behavior, request body rejection, unsupported top-level fields, missing OAuth, API-key-only access, invalid rating upstream failures, unverified email, rental/purchase-required refusal, disabled rating, forbidden or policy failure, not-found failure, quota failure, endpoint unavailable, deprecated endpoint behavior, no-content success shaping, out-of-scope lookup/update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment requests, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos_rate.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   ├── videos.py                       # Existing Layer 1 rate wrapper dependency from YT-150
│   └── validators/videos.py            # Existing Layer 1 videos.rate validation dependency
├── tools/
│   ├── dispatcher.py                   # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py                 # Public exports for videos_rate symbols
│       ├── contracts.py                # Existing shared contract primitives
│       ├── conventions.py              # Existing response/error boundary helpers
│       ├── examples.py                 # Representative shared contract set; add concrete videos_rate contract if needed
│       ├── families.py                 # Existing videos family placement metadata
│       └── videos.py                   # Existing Layer 2 family; add rate contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Extend the existing `videos.py` Layer 2 resource-family module because YT-247 through YT-249 established videos family placement, YT-150 provides the matching Layer 1 resource wrapper, and YT-250 should remain separate from current-rating lookup, search, captions, thumbnails, playlists, comments, analytics, recommendations, and higher-level workflows. This keeps the public tool cohesive with the upstream `videos` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current official `videos.rate` quota, OAuth mode, required inputs, supported rating values, no-request-body behavior, no-content success response, aggregate-count caveat, and documented error categories.
- Confirm existing YT-150 Layer 1 wrapper availability and whether the public YT-250 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, mutation result, and example conventions in the local codebase.
- Confirm current videos Layer 2 family placement and how to add `videos_rate` beside `videos_list`, `videos_insert`, and `videos_update` in the existing `youtube_common/videos.py` module.
- Confirm how to add any representative `videos_rate` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing mutation tools, especially `videos_update`, `comments_setModerationStatus`, `comments_delete`, `playlistImages_delete`, and `subscriptions_delete`, to choose the smallest consistent acknowledgment shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, OAuth handling, videos family placement, registration surface, acknowledgment result shape, safe error categories, examples, no-body rules, rating-state semantics, unsupported field rejection, official endpoint caveats, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into current-rating lookup, rating history, aggregate rating counts, metadata update, media upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/data-model.md)
- [contracts/videos_rate.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/contracts/videos_rate.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, video rating request contract, rating acknowledgment result shape, OAuth and quota caveats, `id` validation, `rating` validation, `none` clear-rating semantics, request-body rejection, unsupported modifier rejection, safe error categories, and no lookup/update/upload/delete/analytics/enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videos_rate`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-only access disclosure, quota accuracy, rating-state boundaries, no-request-body behavior, no-content acknowledgment behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Rate Videos Through a Public Endpoint Tool

**Red**: Add failing contract/unit/integration checks proving `videos_rate` is absent until implemented, requires non-empty `id`, requires supported `rating`, invokes the Layer 1 rate wrapper once with OAuth context, and maps no-content success to a rating acknowledgment with endpoint, quota cost 50, target video identity, requested rating action, access context, availability state, and mutation details.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, rating-context helper, auth-context helper, result mapper, default local no-content executor, public exports, and dispatcher registration needed for successful video rating.

**Refactor**: Align naming, docstrings, helper reuse, acknowledgment mapping, and error mapping with existing Layer 2 mutation tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Quota, OAuth, and Rating Semantics Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 50 in metadata/description/usage notes/examples, OAuth-required access disclosure, required `id`, required `rating`, supported `like`/`dislike`/`none`, clear-rating semantics, no request body, no-content acknowledgment result shape, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for authorized `like`, authorized `dislike`, authorized `none`, missing identity failure, missing rating failure, unsupported rating failure, request body failure, missing OAuth failure, quota or upstream failure, disabled/non-ratable target failure, not-found failure, and out-of-scope workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, OAuth, required inputs, rating-state rules, clear-rating behavior, no-body rules, and unsupported-input guidance reviewable in `videos.py`.

### User Story 3 - Reject Invalid or Unsupported Rating Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `id`, blank or non-string `id`, missing `rating`, blank or non-string `rating`, unsupported `rating`, case-mismatched `rating`, duplicated/conflicting rating fields where representable, supplied `body`, unsupported top-level fields, current-rating lookup fields, rating history fields, aggregate count fields, update fields, upload fields, delete fields, abuse-report fields, thumbnail/caption/playlist/comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, missing OAuth access, quota failure, endpoint unavailable, upstream invalid request, unverified email, purchase-required refusal, forbidden or policy failure, disabled rating, not-found failure, deprecated behavior, no-content success, and unexpected upstream failure.

**Green**: Implement validator, OAuth context selection, rating context extraction, acknowledgment context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the official endpoint request shape.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_videos_contract.py`, `tests/integration/test_youtube_videos_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEOS_RATE_*` symbols, import and use `build_videos_rate_wrapper()`, add `build_videos_rate_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `videos.py` cohesive, keep Layer 1 changes narrow, and avoid changes to search, captions, video categories, thumbnails, playlists, comments, current-rating lookup, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Mutation risk**: Video rating changes user state. Validation must require explicit video identity and rating action before execution.
- **Clear-rating risk**: `none` is a supported clear-rating action. Metadata, examples, and validation failures must distinguish it from a missing rating value.
- **Quota risk**: Each invocation costs 50 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `50`.
- **Access risk**: Video rating is OAuth-only. The handler must not expose API keys, OAuth tokens, authorization headers, or credentials and must distinguish missing or invalid access from malformed input and upstream failure.
- **No-content result risk**: Successful `videos.rate` returns no refreshed video resource. Result mapping must provide a useful acknowledgment without fabricating video metadata, current-rating lookup results, analytics, recommendations, rankings, summaries, or enrichment.
- **Scope risk**: Do not add current-rating lookup, rating history, aggregate rating counts, metadata update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, examples, or docs.
- **Cohesion risk**: `videos_rate` should live in the existing videos Layer 2 module, not in search, captions, thumbnails, playlists, comments, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
