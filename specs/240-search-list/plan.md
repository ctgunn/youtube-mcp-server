# Implementation Plan: Layer 2 Tool `search_list`

**Branch**: `240-search-list` | **Date**: 2026-07-12 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `search_list` for the YouTube endpoint operation `search.list`. The implementation will add the concrete search Layer 2 resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`, reuse the existing Layer 1 `build_search_list_wrapper()` from YT-140, and follow YT-201/YT-202 shared contract conventions for naming, quota, conditional auth disclosure, request validation, near-raw list result shaping, safe errors, examples, public exports, catalog replacement, and default registry integration.

The tool remains endpoint-backed and narrow: it requires the supported Layer 1 search inputs `part` and `q` for baseline searches, costs 100 official quota units per call, supports documented search type, pagination, date, language, region, channel, and video-specific refinements, treats `forContentOwner`, `forDeveloper`, and `forMine` as restricted OAuth-backed modes, returns search result references with query and paging context, and does not add resource hydration, transcript retrieval, analytics, ranking, summarization, recommendation, research synthesis, or cross-endpoint enrichment.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; new concrete Layer 2 search module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`; existing Layer 1 `search.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/search.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, search result mappings, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including search list contract builders, descriptor builders, handler builders, argument validators, conditional-auth helpers, result mappers, upstream-error mappers, local default transport/executor helpers, public export helpers, default registry helpers, representative catalog helpers, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single search request performs one Layer 1 wrapper call and local validation proportional only to submitted fields and returned result count; no resource hydration, transcript retrieval, analytics lookup, ranking, summarization, recommendation, research synthesis, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint list semantics, expose quota cost 100 in metadata/description/examples, declare conditional API-key or OAuth-backed access, require supported baseline search inputs, reject unsupported or incompatible filter combinations before execution, avoid leaking credential material or raw diagnostics in results or errors, add concrete code under the existing `youtube_common` search family placement, and avoid Layer 1 behavior changes unless tests reveal a metadata/export gap  
**Scale/Scope**: One public MCP tool (`search_list`), a new concrete search Layer 2 resource-family module, narrow public exports and default registry integration, replacement or superseding of the current representative `search_list` catalog placeholder, focused contract/unit/integration coverage, and documentation artifacts for YT-240 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-140 wrapper and YT-240 seed agree on quota cost `100`, conditional auth, baseline `part` plus `q`, restricted OAuth-backed filters, video-specific refinement boundaries, pagination support, empty-result behavior, and distinct validation/access/upstream-failure behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `search_list` contract builder, descriptor builder, handler builder, argument validator, conditional-auth helper, result mapper, upstream-error mapper, local default transport/executor helpers, default registration helper if touched, public export helper if touched, representative catalog helper if touched, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, plus regression checks for missing `part`, missing `q`, blank or non-string search inputs, restricted filters without OAuth, multiple restricted filters, video-only refinements without `type=video`, invalid pagination, quota failures, upstream invalid requests, endpoint unavailable, deprecated endpoint behavior, empty successful results, safe error detail sanitization, and no fabricated resource hydration.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── search_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── search.py             # Existing Layer 1 search.list wrapper dependency from YT-140
├── tools/
│   ├── dispatcher.py         # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py       # Public exports for search_list symbols
│       ├── contracts.py      # Existing shared contract primitives
│       ├── examples.py       # Replace/supersede current representative search_list catalog entry if required
│       ├── families.py       # Existing search family placement metadata
│       └── search.py         # New Layer 2 search family; add contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_search_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_search_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_search.py
```

**Structure Decision**: Add the concrete `search.py` Layer 2 family module because `families.py` already reserves the `search` family and the current shared examples only contain a representative `search_list` placeholder. This keeps `search_list` cohesive with the Layer 1 `search` wrapper, avoids mixing search behavior into playlists/videos/channels/higher-level modules, and creates the expected contract/unit/integration test locations for the search family.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `search.list` quota, conditional auth mode, baseline required inputs, restricted filter behavior, video-only refinement boundary, pagination inputs, empty-result handling, and documented error categories.
- Confirm existing YT-140 Layer 1 wrapper availability and whether the public YT-240 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, list result, error, availability, and example conventions in the local codebase.
- Confirm how to replace or supersede the current representative `search_list` entry in shared examples/catalog once a concrete endpoint-backed search family exists.
- Compare existing list-style tools, especially `playlists_list`, `playlistItems_list`, `commentThreads_list`, `comments_list`, `channels_list`, and `activities_list`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported input shape, conditional auth handling, search family placement, registration surface, list result shape, safe error categories, examples, empty-result behavior, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into video/channel/playlist hydration, transcript retrieval, analytics, ranking, summarization, recommendation, research synthesis, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/data-model.md)
- [contracts/search_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/contracts/search_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/240-search-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, list result shape, conditional auth and quota caveats, required search input validation, incompatible filter rejection, empty-result success, safe error categories, and no-hydration response boundaries before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `search_list`.

**Refactor**: Remove duplicated wording across artifacts, keep endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, conditional access disclosure, quota accuracy, required search input validation, list result behavior, empty-result behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Search YouTube Resources Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `search_list` is absent as a concrete endpoint-backed tool until implemented, requires supported baseline search inputs, invokes the Layer 1 search wrapper once with the correct auth path, and maps success to a near-raw search list result with endpoint, quota cost 100, query/filter context, auth path, paging context, and returned items.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, conditional-auth default local executor, public exports, and dispatcher registration needed for successful public and restricted search requests.

**Refactor**: Align naming, docstrings, helper reuse, filter caveats, empty-result handling, and error mapping with existing list tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Search Cost, Filters, Access, and Pagination Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 100 in metadata/description/usage notes/examples, conditional auth disclosure, required `part` and `q`, supported filter categories, pagination, availability state, quota caveat, empty-result behavior, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for keyword search, type-filtered search, channel-scoped search, date-filtered search, language or region refinement, restricted OAuth-backed search, paginated traversal, empty successful result, validation failures, restricted-access failure, quota or upstream service failure, and out-of-scope enrichment request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific required inputs, quota, conditional auth, filter compatibility, pagination, empty-result, no-hydration, and unsupported-input guidance reviewable in `search.py`.

### User Story 3 - Reject Invalid or Restricted Search Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, missing `q`, blank `q`, non-string `q`, unsupported fields, multiple restricted filters, restricted filters without OAuth, video-only refinements without `type=video`, invalid page token, out-of-range `maxResults`, malformed date/language/region/location inputs where locally validated, quota failure, upstream invalid request, endpoint unavailable, deprecated endpoint behavior, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, API keys, stack traces, raw upstream bodies, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_search_contract.py`, `tests/integration/test_youtube_search_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `SEARCH_LIST_*` symbols, add `build_search_list_tool_descriptor()` to the default registry, add concrete representative contract/example coverage, and replace or supersede the current placeholder `search_list` catalog entry so the catalog represents the endpoint-backed tool.

**Refactor**: Keep `search.py` cohesive, keep Layer 1 changes narrow, and avoid changes to playlists, playlist items, playlist images, thumbnails, captions/transcripts, analytics, recommendations, or higher-level workflow modules.

## Risk and Mitigation

- **Quota risk**: Each invocation costs 100 quota units. Discovery metadata, descriptions, examples, result context, and review evidence must consistently show cost `100`.
- **Auth path risk**: Baseline public searches use API-key auth while restricted filters require OAuth-backed authorization. Validation and examples must distinguish missing auth from invalid input and public empty results.
- **Filter compatibility risk**: Search filters have compatibility rules, especially restricted filters and video-only refinements. Local validation must reject known incompatible combinations before execution.
- **Pagination risk**: Page tokens must be tied to compatible search context. The contract must document pagination without promising cross-query token reuse.
- **Empty-result risk**: A valid search can return no items. Result mapping must keep empty successful results distinct from validation, access, quota, and upstream failures.
- **Response-boundary risk**: Search returns references, not hydrated video/channel/playlist/transcript/analytics records. The result mapper must not fabricate full resource details.
- **Security risk**: Do not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, raw request context, or secret-bearing details in failures, logs, metadata, or examples.
- **Cohesion risk**: `search_list` should live in the new concrete `search` Layer 2 module, not in videos, channels, playlists, retrieval, transcripts, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_search_contract.py tests/unit/test_youtube_search.py tests/integration/test_youtube_search_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
