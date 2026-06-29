# Implementation Plan: Layer 2 Tool `guideCategories_list`

**Branch**: `223-guidecategories-list` | **Date**: 2026-06-29 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `guideCategories_list` for the legacy YouTube Data API `guideCategories.list` endpoint. The implementation will add a concrete Layer 2 guide-categories resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`, reuse and, where needed, narrowly extend the existing Layer 1 `build_guide_categories_list_wrapper()` from YT-123, and follow YT-201/YT-202 shared contract conventions for naming, quota, API-key auth disclosure, deprecated availability state, safe validation, safe errors, examples, and default registry integration.

The tool remains endpoint-backed and read-only: it requires `part`, supports a region-code lookup and an ID lookup only as backed by the Layer 1 wrapper, costs 1 official quota unit per call, declares the endpoint as deprecated, accepts optional localization only where Layer 1 and historical endpoint behavior support it, preserves empty results and legacy-unavailable outcomes distinctly, and does not add channel listing, channel categorization, video-category lookup, recommendations, search, ranking, summarization, enrichment, taxonomy migration, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; Layer 1 `guideCategories.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/guide_categories.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, guide-category results, legacy availability outcomes, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including guide-categories contract builders, descriptor builders, handler builders, argument validators, selector helpers, localization helpers, result mappers, legacy-availability mappers, upstream-error mappers, default executor/transport helpers, Layer 1 metadata helpers if changed, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single guide-category lookup performs one Layer 1 wrapper call and constant-time local validation; no additional channel lookup, video-category lookup, search, recommendation, ranking, summarization, enrichment, taxonomy migration, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 1 in metadata/description/examples, declare deprecated availability, require `part`, support only dependency-backed selectors, reject unsupported request fields before execution, avoid leaking API keys/tokens/raw diagnostics in results or errors, keep implementation in a new guide-categories Layer 2 resource-family module with only minimal Layer 1 wrapper metadata changes needed for spec alignment  
**Scale/Scope**: One public MCP tool (`guideCategories_list`), one new Layer 2 resource-family module, a narrow Layer 1 wrapper metadata/validation update if needed for ID lookup, focused contract/unit/integration coverage, and documentation artifacts for YT-223 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `guideCategories_list` contract builder, descriptor builder, handler builder, argument validator, selector helper, localization helper, result mapper, legacy-availability helper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, missing selector, conflicting selectors, invalid `regionCode`, invalid `id`, unsupported `hl`, unsupported optional fields, deprecated availability disclosure, legacy unavailable responses, empty successful results, guide-category not found, quota failures, endpoint unavailable, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── guideCategories_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── guide_categories.py         # Existing Layer 1 list wrapper dependency from YT-123; adjust metadata/validation only if needed for ID lookup alignment
├── tools/
│   ├── dispatcher.py               # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py             # Public exports for guideCategories_list symbols
│       ├── guide_categories.py     # New Layer 2 guideCategories family; add list contract, schema, examples, handler, validation, result mapping
│       ├── contracts.py            # Existing shared contract primitives
│       └── examples.py             # Representative shared contract set

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_guide_categories_contract.py
│   ├── test_youtube_common_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_guide_categories_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_guide_categories.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Add a new concrete `guide_categories` Layer 2 resource-family module. This matches the existing Layer 1 resource-family name, keeps legacy category handling separate from active `videoCategories` and channel tools, and follows the resource-family pattern used by captions, channels, channel sections, comments, and comment threads.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official and project-local `guideCategories.list` request shape, quota, auth mode, deprecated lifecycle state, supported selectors, localization behavior, response shape, and documented error categories.
- Confirm existing YT-123 Layer 1 wrapper availability and the gap between current local region-only metadata and the YT-223 spec's ID-lookup requirement.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, and example conventions in the local codebase.
- Compare existing read/list tools, especially `commentThreads_list`, `comments_list`, `channels_list`, `channelSections_list`, and active category-family Layer 1 wrappers, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/data-model.md)
- [contracts/guideCategories_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/contracts/guideCategories_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, deprecated availability disclosure, API-key-safe behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Guide Categories Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `guideCategories_list` is absent until implemented, requires `part`, requires exactly one selector, supports region-code lookup, supports ID lookup only after Layer 1 dependency metadata accepts it, invokes the Layer 1 list wrapper once, and maps success to a guide-category list result with endpoint, quota cost, requested parts, selector mode, localization context, deprecated availability state, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, optional Layer 1 wrapper metadata update, default local list transport, default executor, public exports, and dispatcher registration needed for successful guide-category lookup.

**Refactor**: Align naming, docstrings, helper reuse, deprecated availability handling, and error mapping with existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Auth, and Legacy Availability Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, API-key auth disclosure, deprecated availability state, required part selection, region selector, ID selector, optional localization caveat, current API reference omission caveat, response boundary, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for region lookup, ID lookup, localized lookup, empty success, missing part, missing selector, conflicting selectors, invalid identifier, invalid region, unsupported option, and legacy-unavailable platform behavior.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific deprecated and unavailable-platform caveats reviewable in `guide_categories.py`.

### User Story 3 - Reject Unsupported Guide Category Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, missing selector, both `regionCode` and `id`, blank selector values, unsupported `hl`, unsupported optional parameters, channel-listing filters, video-category lookup requests, search/recommendation/ranking/enrichment fields, guide category not found, quota failure, endpoint unavailable, deprecated endpoint, removed-resource behavior, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure API keys, OAuth values, stack traces, raw details, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_guide_categories_contract.py`, `tests/integration/test_youtube_guide_categories_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `GUIDE_CATEGORIES_LIST_*` symbols, add `build_guide_categories_list_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `guide_categories.py` cohesive, keep Layer 1 changes narrow, and avoid changes to active `videoCategories`, channel, search, or higher-level category workflow modules.

## Risk and Mitigation

- **Legacy availability risk**: The endpoint is deprecated and removed from current API reference navigation; metadata, examples, results, and errors must make this visible before callers build new workflows around it.
- **Dependency gap risk**: The local Layer 1 wrapper currently describes region-code lookup only; if `id` lookup remains in the public contract, implementation must first add failing Layer 1/Layer 2 tests and make a narrow wrapper metadata/validation update.
- **Scope risk**: Do not add active video category lookup or channel categorization; those belong to separate tools.
- **Validation risk**: Missing `part`, missing selector, conflicting selectors, invalid region, invalid ID, invalid localization, guide-category not found, quota failure, and endpoint unavailable outcomes must map to safe caller-facing categories.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request context, or unsafe authorization context in public metadata, results, logs, or errors.

## Verification Commands

```bash
pytest tests/contract/test_youtube_guide_categories_contract.py tests/unit/test_youtube_guide_categories.py tests/integration/test_youtube_guide_categories_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
