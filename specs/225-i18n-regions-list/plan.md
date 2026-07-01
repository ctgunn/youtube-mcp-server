# Implementation Plan: Layer 2 Tool `i18nRegions_list`

**Branch**: `225-i18n-regions-list` | **Date**: 2026-06-30 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `i18nRegions_list` for the active YouTube Data API `i18nRegions.list` endpoint. The implementation will extend the existing Layer 2 localization resource-family module at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`, reuse and narrowly align the existing Layer 1 `build_i18n_regions_list_wrapper()` from YT-125, and follow YT-201/YT-202 shared contract conventions for naming, quota, API-key auth disclosure, active availability state, safe validation, safe errors, examples, and default registry integration.

The tool remains endpoint-backed and read-only: it requires `part=snippet`, supports optional `hl` display-language preference with upstream default behavior when omitted, costs 1 official quota unit per call, preserves empty results distinctly, and does not add language lookup, translation, country validation, geotargeting, search filtering, recommendation, ranking, summarization, enrichment, analytics, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 2 localization module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`; Layer 1 `i18nRegions.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, localization-region results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including localization region contract builders, descriptor builders, handler builders, argument validators, display-language helpers, result mappers, upstream-error mappers, default executor/transport helpers, Layer 1 metadata helpers if changed, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single localization-region lookup performs one Layer 1 wrapper call and constant-time local validation; no additional language lookup, translation, country validation, geotargeting, search filtering, recommendation, ranking, summarization, enrichment, analytics, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 1 in metadata/description/examples, declare active availability, require `part=snippet`, treat `hl` as optional in the Layer 2 public contract, reject unsupported request fields before execution, avoid leaking API keys/tokens/raw diagnostics in results or errors, keep implementation in the existing localization Layer 2 resource-family module with only minimal Layer 1 wrapper metadata changes needed for official endpoint alignment  
**Scale/Scope**: One public MCP tool (`i18nRegions_list`), one extension to the existing Layer 2 localization resource-family module, a narrow Layer 1 wrapper metadata/validation update if needed to make `hl` optional, focused contract/unit/integration coverage, and documentation artifacts for YT-225 only

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

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `i18nRegions_list` contract builder, descriptor builder, handler builder, argument validator, display-language helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, invalid `hl`, unsupported optional fields, empty successful results, quota failures, upstream invalid requests, endpoint unavailable, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── i18nRegions_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── localization.py              # Existing Layer 1 list wrapper dependency from YT-125; align `hl` optionality only if needed
├── tools/
│   ├── dispatcher.py                # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py              # Public exports for i18nRegions_list symbols
│       ├── localization.py          # Existing Layer 2 localization family; add i18nRegions list contract, schema, examples, handler, validation, result mapping
│       ├── contracts.py             # Existing shared contract primitives
│       └── examples.py              # Representative shared contract set

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_i18n_regions_contract.py
│   ├── test_youtube_common_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_i18n_regions_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_i18n_regions.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Extend the existing concrete `localization` Layer 2 resource-family module created for YT-224. This mirrors the Layer 1 localization resource-family module, keeps `i18nLanguages` and `i18nRegions` public tools cohesive, and avoids mixing localization reference tools into guide categories, search, video categories, or higher-level workflow modules.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Resolve official and project-local `i18nRegions.list` request shape, quota, auth mode, active lifecycle state, `part` rules, optional `hl` behavior, response shape, resource fields, and documented error categories.
- Confirm existing YT-125 Layer 1 wrapper availability and the gap between current local `part` plus required `hl` metadata and the official/YT-225 public contract where `hl` is optional.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, and example conventions in the local codebase.
- Compare existing read/list tools, especially `i18nLanguages_list`, `guideCategories_list`, `commentThreads_list`, `comments_list`, `channels_list`, and `channelSections_list`, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/data-model.md)
- [contracts/i18nRegions_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/contracts/i18nRegions_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/225-i18n-regions-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, active availability disclosure, API-key-safe behavior, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Localization Regions Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `i18nRegions_list` is absent until implemented, requires `part`, accepts optional `hl`, invokes the Layer 1 list wrapper once, and maps success to a localization-region list result with endpoint, quota cost, requested parts, display-language context when present, active availability state, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, optional Layer 1 wrapper metadata update, default local list transport, default executor, public exports, and dispatcher registration needed for successful localization-region lookup.

**Refactor**: Align naming, docstrings, helper reuse, active availability handling, and error mapping with `i18nLanguages_list` and existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, Auth, and Region Lookup Usage Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, API-key auth disclosure, active availability state, required part selection, optional `hl`, default display-language behavior, response boundary, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for default listing, display-language-specific listing, empty success, missing part, invalid part, invalid display language, unsupported option, and out-of-scope language lookup or geotargeting request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific localization-region guidance reviewable in `localization.py`.

### User Story 3 - Reject Unsupported Localization-Region Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, blank or unsupported `part`, unsupported `hl`, unsupported optional parameters, language filters, country validation requests, geotargeting instructions, search filtering, recommendation/ranking/enrichment fields, quota failure, endpoint unavailable, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure API keys, OAuth values, stack traces, raw details, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the upstream endpoint.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_i18n_regions_contract.py`, `tests/integration/test_youtube_i18n_regions_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `I18N_REGIONS_LIST_*` symbols, add `build_i18n_regions_list_tool_descriptor()` to the default registry, and add representative contract coverage.

**Refactor**: Keep `localization.py` cohesive, keep Layer 1 changes narrow, and avoid changes to language lookup, translation, caption, search, geotargeting, analytics, or higher-level localization workflow modules.

## Risk and Mitigation

- **Layer 1 optionality gap risk**: The current Layer 1 wrapper requires `hl`, while the official endpoint and YT-225 public contract make `hl` optional with a default display language. Implementation must start with failing tests and then make a narrow wrapper metadata/validation update if needed.
- **Scope risk**: Do not add language lookup, translation, country validation, geotargeting, search filtering, recommendation, ranking, summarization, enrichment, analytics, or region-code conversion behavior; those belong to separate tools or layers.
- **Validation risk**: Missing `part`, invalid `part`, invalid `hl`, unsupported fields, empty successful results, quota failure, upstream invalid request, and endpoint unavailable outcomes must map to safe caller-facing categories.
- **Security risk**: Do not expose API keys, OAuth tokens, raw upstream diagnostics, stack traces, raw request context, or unsafe authorization context in public metadata, results, logs, or errors.
- **Cohesion risk**: `i18nRegions_list` should live alongside `i18nLanguages_list` in the localization Layer 2 module so localization reference tools share patterns without mixing into unrelated categories or search modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_i18n_regions_contract.py tests/unit/test_youtube_i18n_regions.py tests/integration/test_youtube_i18n_regions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
