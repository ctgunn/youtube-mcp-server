# Implementation Plan: Layer 2 Tool `videoCategories_list`

**Branch**: `246-video-categories-list` | **Date**: 2026-07-21 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `videoCategories_list` for the YouTube endpoint operation `videoCategories.list`. The implementation will add a concrete Layer 2 video-categories resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`, reuse the existing Layer 1 `build_video_categories_list_wrapper()` from YT-146, and follow YT-201/YT-202 shared contract conventions for naming, quota, API-key access disclosure, selector validation, localization guidance, near-raw list result shaping, safe errors, examples, public exports, catalog alignment, and default registry integration.

The tool remains endpoint-backed and read-only: it requires `part` plus exactly one selector from `id` or `regionCode`, accepts optional `hl` display-language guidance, costs 1 official quota unit per call, uses API-key access expectations, preserves empty successful results distinctly, and does not add video search, automatic category selection, category recommendation, popularity analysis, ranking, summarization, analytics, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 family registry at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`; existing Layer 1 `videoCategories.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_categories.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, category results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including video categories contract builders, descriptor builders, handler builders, argument validators, part-selection helpers, selector helpers, localization helpers, result mappers, empty-result helpers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, catalog/example helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single video-category lookup performs one Layer 1 wrapper call and local validation proportional only to supplied fields and returned items; no search, video lookup, analytics lookup, category recommendation, ranking, summarization, enrichment, bulk processing, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint lookup semantics, expose quota cost 1 in metadata/description/examples, declare API-key access expectation, require non-empty `part` plus exactly one selector from `id` or `regionCode`, treat `hl` as optional display-language guidance, reject unsupported fields and out-of-scope modifiers before execution, preserve empty item collections as successful lookups, avoid leaking API keys, authorization details, raw upstream diagnostics, stack traces, or unsafe request context in results or errors, add code under the video-categories Layer 2 resource-family placement, and avoid Layer 1 behavior changes unless tests reveal a narrow metadata/export gap  
**Scale/Scope**: One public MCP tool (`videoCategories_list`), one new video-categories Layer 2 resource-family module, narrow public exports and default registry integration, addition of a concrete catalog/example entry if absent, focused contract/unit/integration coverage, and documentation artifacts for YT-246 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-146 wrapper, YT-246 seed, requirements inventory, shared Layer 2 contracts, and existing list-style tools agree on quota cost `1`, API-key access, required `part`, exactly one selector from `id` or `regionCode`, optional `hl` display-language behavior, empty successful result handling, unsupported modifier rejection, and distinct validation/access/quota/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `videoCategories_list` contract builder, descriptor builder, handler builder, argument validator, part-selection helper, selector helper, localization helper, result mapper, empty-result helper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, empty `part`, non-string `part`, missing selector, blank selector, both selectors supplied, malformed `regionCode`, empty or malformed `id`, invalid `hl`, unsupported optional fields, paging controls, ordering controls, search text, video identifiers, channel identifiers, analytics instructions, classification instructions, ranking/summarization/enrichment fields, missing API-key access, upstream empty item collections, quota failures, upstream invalid requests, authorization failures, endpoint unavailable, deprecated endpoint behavior, sparse result shaping, localization context preservation, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videoCategories_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── video_categories.py         # Existing Layer 1 list wrapper dependency from YT-146
├── tools/
│   ├── dispatcher.py               # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py             # Public exports for videoCategories_list symbols
│       ├── contracts.py            # Existing shared contract primitives
│       ├── examples.py             # Representative shared contract set; add concrete videoCategories_list contract if needed
│       ├── families.py             # Existing video_categories family placement metadata
│       └── video_categories.py     # New Layer 2 family; add list contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_tool_catalog_contract.py
│   └── test_youtube_video_categories_contract.py
├── integration/
│   ├── test_youtube_tool_registration.py
│   └── test_youtube_video_categories_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_video_categories.py
```

**Structure Decision**: Add the concrete `video_categories.py` Layer 2 resource-family module because `families.py` already reserves the `video_categories` family, YT-146 provides the matching Layer 1 resource module, and this slice should remain separate from deprecated guide categories, videos, search, analytics, recommendations, and higher-level category workflow modules. This keeps the public tool cohesive with the upstream `videoCategories` resource while avoiding broad refactors.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `videoCategories.list` quota, API-key auth mode, required `part`, supported selectors, optional `hl`, response shape, empty-result behavior, and documented error categories.
- Confirm existing YT-146 Layer 1 wrapper availability and whether the public YT-246 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, selector, localization, and example conventions in the local codebase.
- Confirm current video-categories Layer 2 family placement and whether a new `youtube_common/video_categories.py` module should be created rather than reusing guide categories, videos, search, localization, or higher-level modules.
- Confirm how to add any representative `videoCategories_list` entry in shared examples/catalog once the concrete endpoint-backed tool exists.
- Compare existing read/list tools, especially `guideCategories_list`, `i18nLanguages_list`, `i18nRegions_list`, `search_list`, and `videoAbuseReportReasons_list`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, selector behavior, API-key handling, video-categories family placement, registration surface, category-list result shape, safe error categories, examples, empty-result behavior, unsupported modifier rejection, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into video search, automatic category selection, category recommendation, popularity analysis, ranking, summarization, analytics, enrichment, bulk processing, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/data-model.md)
- [contracts/videoCategories_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/contracts/videoCategories_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, selector request contract, category-list result shape, API-key and quota caveats, `part` validation, selector validation, `hl` validation, unsupported modifier rejection, empty successful result handling, safe error categories, and no-enrichment response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `videoCategories_list`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, API-key access disclosure, quota accuracy, selector exclusivity, optional localization boundary, empty-response behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Video Categories Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `videoCategories_list` is absent until implemented, requires non-empty `part`, requires exactly one selector from `id` or `regionCode`, invokes the Layer 1 list wrapper once with API-key auth, and maps success to a category-list result with endpoint, quota cost 1, requested parts, selector context, localization context when supplied, access context, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, part helper, selector helper, localization helper, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful category lookup.

**Refactor**: Align naming, docstrings, helper reuse, selector handling, localization handling, empty-result handling, and error mapping with existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Access, Selectors, and Localization Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, API-key access disclosure, required `part`, exactly-one-selector behavior, region lookup guidance, category ID lookup guidance, optional `hl`, list result shape, empty-result caveat, availability state, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for region-scoped lookup, category-ID lookup, localized lookup, populated success, empty success, missing part, missing selector, conflicting selectors, invalid selector, invalid localization, missing access, quota or upstream failure, and out-of-scope category-analysis request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific quota, API-key access, required part, selector rules, optional `hl`, empty-result caveat, and unsupported-input guidance reviewable in `video_categories.py`.

### User Story 3 - Reject Invalid or Unsupported Category Lookup Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, empty `part`, non-string `part`, missing selector, both selectors supplied, empty `id`, malformed `regionCode`, invalid `hl`, unsupported top-level fields, paging controls, ordering controls, search text, video identifiers, channel identifiers, analytics instructions, classification instructions, ranking fields, summarization fields, enrichment fields, missing API-key access, quota failure, endpoint unavailable, upstream invalid request, deprecated behavior, empty upstream success, and unexpected upstream failure.

**Green**: Implement validator, API-key auth context selection, selector context extraction, localization context extraction, category-list context extraction, and upstream-error mapper using shared safe categories; ensure API keys, OAuth tokens, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_video_categories_contract.py`, `tests/integration/test_youtube_video_categories_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `VIDEO_CATEGORIES_LIST_*` symbols, add `build_video_categories_list_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `video_categories.py` cohesive, keep Layer 1 changes narrow, and avoid changes to deprecated guide categories, videos, search, localization infrastructure, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Selector risk**: The tool supports exactly one selector from `id` or `regionCode`. Validation must reject missing and conflicting selectors before execution so callers do not get ambiguous category catalogs.
- **Region interpretation risk**: Category availability may vary by region. Results must preserve requested region context and returned fields without claiming categories apply globally when a regional selector was used.
- **Localization risk**: Callers may expect translated labels to always exist. Results must preserve requested `hl` context and returned fields without fabricating translations or treating upstream fallback text as a failure.
- **Quota risk**: Each invocation costs 1 quota unit. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `1`.
- **Access risk**: The endpoint uses API-key access expectations. The handler must not expose API keys or authorization details and must distinguish missing or invalid access from malformed input and upstream failure.
- **Empty-result risk**: Valid requests may return zero category items. Result mapping must keep empty success distinct from validation, access, quota, and upstream failures.
- **Scope risk**: Do not add video search, automatic category selection, category recommendation, popularity analysis, ranking, summarization, analytics, enrichment, bulk processing, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or secret-bearing details in failures, logs, metadata, or examples.
- **Cohesion risk**: `videoCategories_list` should live in the new `video_categories` Layer 2 module, not in guide categories, videos, search, localization infrastructure, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_video_categories_contract.py tests/unit/test_youtube_video_categories.py tests/integration/test_youtube_video_categories_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
