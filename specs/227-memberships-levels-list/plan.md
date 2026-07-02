# Implementation Plan: Layer 2 Tool `membershipsLevels_list`

**Branch**: `227-memberships-levels-list` | **Date**: 2026-07-02 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `membershipsLevels_list` for the YouTube Data API `membershipsLevels.list` endpoint. The implementation will add a concrete memberships-levels resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py`, reuse the existing Layer 1 `build_memberships_levels_list_wrapper()` from YT-127, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, owner-only/channel-membership access caveats, list result shaping, safe validation, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and owner-scoped: it requires `part=snippet`, costs 1 official quota unit per call per the YT-227 seed and existing Layer 1 wrapper, preserves successful empty results distinctly, rejects unsupported filters, paging controls, delegation inputs, and broader membership workflows, and does not add channel member listing, subscriber lookup, membership administration, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `membershipsLevels.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, membership-level list results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including memberships-levels contract builders, descriptor builders, handler builders, argument validators, part helpers, result mappers, upstream-error mappers, default executor/transport helpers, Layer 1 metadata helpers if changed, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single membership-level list request performs one Layer 1 wrapper call and constant-time local validation; no additional member listing, subscriber lookup, membership administration, analytics, recommendation, ranking, summarization, enrichment, paging traversal, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose quota cost 1 in metadata/description/examples, declare OAuth-required owner-only/channel-membership access, require `part=snippet`, reject unsupported request fields before execution, avoid leaking OAuth tokens/raw diagnostics in results or errors, and keep implementation in a focused memberships-levels Layer 2 resource-family module with no Layer 1 behavior changes unless tests reveal a metadata export gap  
**Scale/Scope**: One public MCP tool (`membershipsLevels_list`), one new Layer 2 memberships-levels resource-family module, narrow public exports and default registry integration, focused contract/unit/integration coverage, and documentation artifacts for YT-227 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research confirms the local YT-127 wrapper and YT-227 seed agree on quota cost `1`, OAuth-required owner scope, required `part`, unsupported modifier rejection, and empty-result success behavior.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `membershipsLevels_list` contract builder, descriptor builder, handler builder, argument validator, part helper, auth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, unsupported optional fields, unsupported paging/filter/delegation fields, API-key-only access, owner-authorization failures, channel-membership eligibility failures, empty successful results, quota failures, upstream invalid requests, endpoint unavailable, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── membershipsLevels_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── memberships_levels.py      # Existing Layer 1 list wrapper dependency from YT-127
├── tools/
│   ├── dispatcher.py              # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py            # Public exports for membershipsLevels_list symbols
│       ├── contracts.py           # Existing shared contract primitives
│       ├── examples.py            # Representative shared contract set
│       ├── families.py            # Existing memberships_levels family placement metadata
│       └── memberships_levels.py  # New Layer 2 memberships-levels family; add contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_common_contract.py
│   ├── test_youtube_memberships_levels_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_memberships_levels_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_common_scaffolding.py
    └── test_youtube_memberships_levels.py
```

**Structure Decision**: Add a concrete `memberships_levels` Layer 2 resource-family module because `memberships_levels` already exists in shared family metadata and Layer 1 resource modules, but no public Layer 2 module exists yet. This keeps membership-level listing separate from channel member listing, subscriber lookup, comments, channels, analytics, and higher-level workflow modules while matching existing one-family module patterns.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Confirm current local `membershipsLevels.list` quota, auth mode, owner-only access, channel-membership eligibility, request shape, unsupported modifier boundary, response shape, and documented error categories.
- Confirm existing YT-127 Layer 1 wrapper availability and whether the public YT-227 contract can rely on it without Layer 1 changes.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, and example conventions in the local codebase.
- Compare existing read/list tools, especially `members_list`, `comments_list`, `i18nRegions_list`, `i18nLanguages_list`, and `guideCategories_list`, to choose the smallest consistent implementation shape.

**Red**: Identify missing planning facts that would block task generation, including supported part values, optional modifier handling, registration surface, safe error categories, examples, and docstring requirements.

**Green**: Resolve all planning facts in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/research.md) with concrete decisions and no unresolved clarification markers.

**Refactor**: Consolidate decisions into the smallest endpoint-backed Layer 2 approach and remove any planning paths that broaden into channel members, analytics, or higher-level workflows.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/data-model.md)
- [contracts/membershipsLevels_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/contracts/membershipsLevels_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Red**: Define failing design expectations for public discovery metadata, input schema, near-raw result shape, auth and quota caveats, unsupported modifier rejection, empty-result interpretation, and safe error categories before implementation tasks are created.

**Green**: Produce the data model, public tool contract, and quickstart with only required design detail for `membershipsLevels_list`.

**Refactor**: Remove duplicated wording across artifacts, keep owner-scoped endpoint scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification.

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required owner-only access disclosure, quota accuracy, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Membership Levels Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `membershipsLevels_list` is absent until implemented, requires `part=snippet`, invokes the Layer 1 list wrapper once with OAuth-required auth, and maps success to a membership-level list result with endpoint, quota cost 1, requested parts, availability/access caveats, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, default local list transport, default executor, public exports, and dispatcher registration needed for successful owner-scoped membership-level retrieval.

**Refactor**: Align naming, docstrings, helper reuse, availability/access caveats, and error mapping with `members_list` and existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Membership Access Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 1 in metadata/description/usage notes/examples, OAuth-required auth disclosure, owner-only and channel-membership access constraints, required part selection, response boundary, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for owner-authorized retrieval, empty success, missing part, invalid part, unsupported modifier, access or membership eligibility failure, and out-of-scope member-list or analytics request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific owner-visibility and membership-level guidance reviewable in `memberships_levels.py`.

### User Story 3 - Reject Unsupported or Ineligible Membership Level Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, blank or unsupported `part`, unsupported optional parameters, unsupported paging/filter/delegation fields, API-key-only access, non-owner OAuth access, membership-not-enabled failure, quota failure, endpoint unavailable, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, stack traces, raw details, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_memberships_levels_contract.py`, `tests/integration/test_youtube_memberships_levels_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `MEMBERSHIPS_LEVELS_LIST_*` symbols, add `build_memberships_levels_list_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `memberships_levels.py` cohesive, keep Layer 1 changes narrow, and avoid changes to channel member listing, subscriber lookup, delegated owner management, analytics, recommendations, search, or higher-level membership workflow modules.

## Risk and Mitigation

- **Supported-parameter scope risk**: The local Layer 1 YT-127 contract exposes only required `part`. YT-227 keeps filters, paging controls, and delegation inputs out of scope and rejects them clearly unless a later Layer 1 contract revision adds support.
- **Owner-access risk**: Membership-level data is owner-scoped and channel-membership constrained. Metadata, examples, errors, and quickstart validation must make OAuth-required owner access visible and must not imply API-key-only or public lookup support.
- **Empty-result ambiguity risk**: A valid owner-authorized request may return no configured membership levels. Result mapping and examples must preserve empty collections as successful outcomes distinct from invalid or ineligible requests.
- **Scope risk**: Do not add channel member listing, subscriber lookup, membership administration, delegated owner management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or sensitive membership configuration details in failures, logs, metadata, or examples.
- **Cohesion risk**: `membershipsLevels_list` should live in a dedicated `memberships_levels` Layer 2 module, not in `members`, comments, channels, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_memberships_levels_contract.py tests/unit/test_youtube_memberships_levels.py tests/integration/test_youtube_memberships_levels_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
