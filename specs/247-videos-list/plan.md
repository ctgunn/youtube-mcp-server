# Implementation Plan: Layer 2 Tool `videos_list`

**Branch**: `247-videos-list` | **Date**: 2026-07-21 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videos_list` for the YouTube endpoint operation `videos.list`. The implementation will add a concrete Layer 2 videos resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, reuse the existing Layer 1 `build_videos_list_wrapper()` from YT-147, and follow YT-201/YT-202 shared contract conventions for naming, quota, conditional access disclosure, selector validation, pagination guidance, near-raw list result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and read-only: it requires `part` plus exactly one selector from `id`, `chart`, or `myRating`, costs 1 official quota unit per call, uses API-key access for `id` and `chart`, uses OAuth-required access for `myRating`, allows `pageToken` and `maxResults` only for collection selectors, treats `regionCode` and `videoCategoryId` as chart-only refinements, preserves empty successful results distinctly, and does not add video search, upload, update, delete, rating mutation, transcript retrieval, recommendation, ranking, analytics, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 family registry at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`; existing Layer 1 `videos.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, video results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including videos contract builders, descriptor builders, handler builders, argument validators, part-selection helpers, selector helpers, pagination helpers, auth-context helpers, result mappers, empty-result helpers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single video-list lookup performs one Layer 1 wrapper call and local validation proportional only to supplied fields and returned items; no search, transcript lookup, analytics lookup, recommendation, ranking, summarization, enrichment, bulk processing, media transfer, mutation, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint lookup semantics, expose quota cost 1 in metadata/description/examples, declare conditional access expectations, require non-empty `part` plus exactly one selector from `id`, `chart`, or `myRating`, allow `pageToken` and `maxResults` only for `chart` or `myRating`, allow `regionCode` and `videoCategoryId` only with `chart`, reject unsupported fields and out-of-scope modifiers before execution, preserve empty item collections as successful lookups, avoid leaking API keys, OAuth tokens, authorization details, raw upstream diagnostics, stack traces, or unsafe request context in results or errors, add code under the videos Layer 2 resource-family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videos_list`), one new videos Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-247 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-147 wrapper, YT-247 seed, requirements inventory, shared Layer 2 contracts, and existing list-style tools agree on quota cost `1`, conditional access, required `part`, exactly one selector from `id`, `chart`, or `myRating`, collection-only pagination, chart-only `regionCode` and `videoCategoryId` refinements, empty successful result handling, unsupported modifier rejection, and distinct validation/access/quota/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videos_list` contract builder, descriptor builder, handler builder, argument validator, part-selection helper, selector helper, pagination helper, chart-refinement helper, auth-context helper, result mapper, empty-result helper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, empty `part`, non-string `part`, missing selector, blank selector, multiple selectors, malformed `id`, malformed `chart`, malformed `myRating`, `myRating` without OAuth, invalid `pageToken`, invalid `maxResults`, pagination on direct ID lookup, `regionCode` or `videoCategoryId` without chart, unsupported optional fields, search text, upload or mutation instructions, rating mutation instructions, transcript instructions, analytics instructions, recommendation/ranking/summarization/enrichment fields, missing API-key access for public selectors, missing OAuth for `myRating`, upstream empty item collections, quota failures, upstream invalid requests, authorization failures, endpoint unavailable, deprecated endpoint behavior, sparse result shaping, pagination context preservation, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── videos.py                  # Existing Layer 1 list wrapper dependency from YT-147
├── tools/
│   ├── dispatcher.py              # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py            # Public exports for videos_list symbols
│       ├── contracts.py           # Existing shared contract primitives
│       ├── examples.py            # Representative shared contract set; add concrete videos_list contract if needed
│       ├── families.py            # Existing videos family placement metadata
│       └── videos.py              # New Layer 2 family; add list contract, schema, examples, handler, validation, result mapping

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

**Structure Decision**: Add the concrete `videos.py` Layer 2 resource-family module because `families.py` already reserves the `videos` family, YT-147 provides the matching Layer 1 resource module, and this slice should remain separate from search, captions, video categories, thumbnails, video mutations, rating mutations, analytics, recommendations, and higher-level video workflow modules. This keeps the public tool cohesive with the upstream `videos` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `videos.list` quota, conditional auth mode, required `part`, supported selectors, supported refinements, pagination behavior, response shape, empty-result behavior, and documented error categories.
- Confirm existing YT-147 Layer 1 wrapper availability and whether the public YT-247 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, selector, pagination, and example conventions in the local codebase.
- Confirm current videos Layer 2 family placement and whether a new `youtube_common/videos.py` module should be created rather than reusing search, captions, video categories, rating, mutation, analytics, recommendation, or higher-level modules.
- Confirm how to add any representative `videos_list` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing read/list tools, especially `search_list`, `videoCategories_list`, `guideCategories_list`, `playlistItems_list`, and `playlists_list`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, selector behavior, conditional access handling, videos family placement, registration surface, video-list result shape, safe error categories, examples, empty-result behavior, unsupported modifier rejection, pagination compatibility, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into video search, upload, update, delete, rating mutation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/data-model.md)
- [contracts/videos_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/contracts/videos_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, selector request contract, video-list result shape, conditional auth and quota caveats, `part` validation, selector validation, pagination validation, chart-refinement validation, unsupported modifier rejection, empty successful result handling, safe error categories, and no-enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videos_list`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, conditional access disclosure, quota accuracy, selector exclusivity, pagination boundaries, empty-response behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Video Resources Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `videos_list` is absent until implemented, requires non-empty `part`, requires exactly one selector from `id`, `chart`, or `myRating`, invokes the Layer 1 list wrapper once with selector-appropriate auth, and maps success to a video-list result with endpoint, quota cost 1, requested parts, selector context, pagination context when present, access context, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, part helper, selector helper, pagination helper, auth-context helper, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful video lookup.

**Refactor**: Align naming, docstrings, helper reuse, selector handling, pagination handling, empty-result handling, and error mapping with existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Parts, Selectors, Access, and Pagination Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, conditional access disclosure, required `part`, exactly-one-selector behavior, direct ID lookup guidance, chart lookup guidance, rating-view guidance, collection-only pagination guidance, list result shape, empty-result caveat, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for direct ID lookup, chart lookup, rating-based lookup with OAuth, paginated traversal, populated success, empty success, missing part, missing selector, conflicting selectors, invalid pagination, missing API-key access, missing OAuth access, quota or upstream failure, and out-of-scope video workflow rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, conditional access, required part, selector rules, pagination rules, empty-result caveat, and unsupported-input guidance reviewable in `videos.py`.

### User Story 3 - Reject Invalid or Unsupported Video List Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, empty `part`, non-string `part`, missing selector, multiple selectors, empty `id`, empty `chart`, empty `myRating`, unsupported `myRating` value, invalid `pageToken`, invalid `maxResults`, pagination with `id`, `regionCode` without `chart`, `videoCategoryId` without `chart`, unsupported top-level fields, search text, upload/update/delete instructions, rating mutation instructions, transcript instructions, analytics instructions, recommendation fields, ranking fields, summarization fields, enrichment fields, missing API-key access for public selectors, missing OAuth access for `myRating`, quota failure, endpoint unavailable, upstream invalid request, deprecated behavior, empty upstream success, and unexpected upstream failure.

**Green**: Implement validator, selector-specific auth context selection, selector context extraction, pagination context extraction, chart-refinement context extraction, video-list context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_videos_contract.py`, `tests/integration/test_youtube_videos_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEOS_LIST_*` symbols, add `build_videos_list_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `videos.py` cohesive, keep Layer 1 changes narrow, and avoid changes to search, captions, video categories, thumbnails, video mutations, rating mutations, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Selector risk**: The tool supports exactly one selector from `id`, `chart`, or `myRating`. Validation must reject missing and conflicting selectors before execution so callers do not get ambiguous video collections.
- **Access risk**: `id` and `chart` use API-key-compatible access while `myRating` requires OAuth. The handler must not expose API keys, OAuth tokens, or authorization details and must distinguish missing or invalid access from malformed input and upstream failure.
- **Pagination risk**: `pageToken` and `maxResults` are valid only for collection-style selectors. Validation must reject pagination on direct ID lookup and preserve page context for supported collection traversal.
- **Chart refinement risk**: `regionCode` and `videoCategoryId` refine chart retrieval only. Validation must reject those fields outside chart mode and preserve refinement context when chart lookup succeeds.
- **Quota risk**: Each invocation costs 1 quota unit. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `1`.
- **Empty-result risk**: Valid requests may return zero video items. Result mapping must keep empty success distinct from validation, access, quota, and upstream failures.
- **Scope risk**: Do not add video search, media upload, metadata update, deletion, rating mutation, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, or examples.
- **Cohesion risk**: `videos_list` should live in the new `videos` Layer 2 module, not in search, captions, video categories, thumbnails, analytics, recommendation, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
