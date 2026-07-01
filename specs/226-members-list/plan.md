# Implementation Plan: Layer 2 Tool `members_list`

**Branch**: `226-members-list` | **Date**: 2026-07-01 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the low-level public Layer 2 MCP tool `members_list` for the YouTube Data API `members.list` endpoint. The implementation will add a concrete members resource-family module under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`, reuse the existing Layer 1 `build_members_list_wrapper()` from YT-126, and follow YT-201/YT-202 shared contract conventions for naming, quota, OAuth-required auth disclosure, owner-only/channel-membership access caveats, list result shaping, safe validation, safe errors, examples, public exports, and default registry integration.

The tool remains endpoint-backed and owner-scoped: it requires `part=snippet` and a supported `mode` value, supports optional `pageToken` and `maxResults` within the documented member-list boundary, costs 2 official quota units per call per current Google documentation, preserves successful empty results distinctly, and does not add public subscriber lookup, membership-level listing, member administration, delegated owner management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP tool registry and dispatcher under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/`; shared Layer 2 contracts under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`; existing Layer 1 `members.list` wrapper under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/members.py`; Python standard library dataclasses, enums, and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; tool metadata, request validation state, member-list results, representative examples, and test fixtures remain in memory or file-based only  
**Testing**: `pytest` focused contract/unit/integration checks; final full-suite command `pytest`; lint command `ruff check .`  
**Documentation Style**: Python reStructuredText docstrings are required for every new or changed Python function, including members contract builders, descriptor builders, handler builders, argument validators, membership-mode helpers, paging helpers, result mappers, upstream-error mappers, default executor/transport helpers, Layer 1 metadata helpers if changed, and tests' fake wrapper methods where applicable  
**Target Platform**: MCP server running locally and in hosted Python 3.11 runtime; no new platform dependency  
**Project Type**: Python MCP service with Layer 2 endpoint-backed public tool modules  
**Performance Goals**: Single member-list request performs one Layer 1 wrapper call and constant-time local validation; no additional subscriber lookup, membership-level listing, member administration, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint expansion is introduced  
**Constraints**: Preserve endpoint semantics, expose current official quota cost 2 in metadata/description/examples, declare OAuth-required owner-only/channel-membership access, require `part=snippet`, require `mode` as `all_current` or `updates`, allow `pageToken` and `maxResults` only within the documented boundary, reject unsupported request fields before execution, avoid leaking OAuth tokens/raw diagnostics in results or errors, and keep implementation in a focused members Layer 2 resource-family module with only minimal Layer 1 wrapper metadata changes needed for quota alignment  
**Scale/Scope**: One public MCP tool (`members_list`), one new Layer 2 members resource-family module, narrow public exports and default registry integration, a targeted Layer 1 quota metadata update from 1 to 2 if required by implementation tests, focused contract/unit/integration coverage, and documentation artifacts for YT-226 only

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

**Gate Status**: PASS. No constitution violations or unresolved clarifications. Phase 0 research resolved the seed/local quota discrepancy by aligning public YT-226 artifacts with the current official Google documentation for `members.list`.

**Docstring Requirement**: Implementation tasks must add or preserve reStructuredText docstrings for all new or changed Python functions, including `members_list` contract builder, descriptor builder, handler builder, argument validator, mode helper, paging helper, auth-context helper, result mapper, upstream-error mapper, local default transport/executor helpers, any touched Layer 1 wrapper helper, and fake wrapper methods in tests.

**Integration and Regression Coverage**: Add contract tests for public metadata and examples, unit tests for validation/result/error mapping, integration tests for default registry discovery and dispatcher execution, plus regression checks for missing `part`, invalid `part`, missing `mode`, invalid `mode`, invalid `maxResults`, unsupported optional fields, unsupported delegation/filter fields, API-key-only access, owner-authorization failures, channel-membership eligibility failures, empty successful results, quota failures, upstream invalid requests, endpoint unavailable, and safe error detail sanitization.

**Full-Suite Command**: `pytest`

**Lint Command**: `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── members_list.md
└── tasks.md              # Phase 2 output from /speckit.tasks; not created by this command
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── integrations/resources/
│   └── members.py                 # Existing Layer 1 list wrapper dependency from YT-126; align quota metadata to current docs if needed
├── tools/
│   ├── dispatcher.py              # Default tool registration integration
│   └── youtube_common/
│       ├── __init__.py            # Public exports for members_list symbols
│       ├── contracts.py           # Existing shared contract primitives
│       ├── examples.py            # Representative shared contract set
│       ├── families.py            # Existing members family placement metadata
│       └── members.py             # New Layer 2 members family; add members_list contract, schema, examples, handler, validation, result mapping

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── contract/
│   ├── test_youtube_members_contract.py
│   ├── test_youtube_common_contract.py
│   └── test_youtube_tool_catalog_contract.py
├── integration/
│   ├── test_youtube_members_registration.py
│   └── test_youtube_tool_registration.py
└── unit/
    ├── test_youtube_members.py
    └── test_youtube_common_scaffolding.py
```

**Structure Decision**: Add a concrete `members` Layer 2 resource-family module because `members` is already a required resource family in shared scaffolding, but no public Layer 2 module exists yet. This keeps channel-membership member listing separate from `memberships_levels`, comments, channels, analytics, and higher-level workflow modules while matching existing one-family module patterns.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Outline & Research

**Research Tasks**

- Resolve current official and project-local `members.list` quota, auth mode, owner-only access, channel-membership eligibility, request shape, mode values, paging rules, response shape, and documented error categories.
- Confirm existing YT-126 Layer 1 wrapper availability and the gap between current local quota metadata/request boundary and the public YT-226 contract.
- Confirm YT-201/YT-202 Layer 2 naming, metadata, quota, auth, response, error, availability, and example conventions in the local codebase.
- Compare existing read/list tools, especially `comments_list`, `i18nRegions_list`, `i18nLanguages_list`, and `guideCategories_list`, to choose the smallest consistent implementation shape.

**Output**: [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/research.md)

## Phase 1: Design & Contracts

**Design Outputs**

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/data-model.md)
- [contracts/members_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/contracts/members_list.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/quickstart.md)
- Agent context updated by `.specify/scripts/bash/update-agent-context.sh codex`

**Post-Design Constitution Check**: PASS. The design preserves contract-first documentation, TDD sequencing, full-suite validation, reStructuredText docstring requirements, safe error/result surfaces, OAuth-required owner-only access disclosure, current quota accuracy, and simple endpoint-backed implementation scope.

## Phase 2: Planning Approach

### User Story 1 - Retrieve Channel Members Through a Public Tool

**Red**: Add failing contract/unit/integration checks proving `members_list` is absent until implemented, requires `part=snippet`, requires `mode` as `all_current` or `updates`, invokes the Layer 1 list wrapper once with OAuth-required auth, and maps success to a member-list result with endpoint, quota cost 2, requested parts, selected mode, paging context, availability/access caveats, and returned item fields.

**Green**: Add the smallest constants, schema, contract builder, descriptor builder, handler, validator, result mapper, optional Layer 1 quota metadata update, default local list transport, default executor, public exports, and dispatcher registration needed for successful owner-scoped member retrieval.

**Refactor**: Align naming, docstrings, helper reuse, availability/access caveats, and error mapping with `comments_list` and existing read/list Layer 2 tools; run focused tests and final `pytest` plus `ruff check .`.

### User Story 2 - Understand Cost, OAuth, and Membership Access Before Calling

**Red**: Add failing metadata and example checks for public name, upstream identity, quota cost 2 in metadata/description/usage notes/examples, OAuth-required auth disclosure, owner-only and channel-membership access constraints, required part selection, required mode, optional paging, response boundary, and out-of-scope workflow boundaries.

**Green**: Populate caller-facing description, usage notes, caveats, response convention, response boundary, and examples for owner-authorized retrieval, paged retrieval, empty success, missing part, missing mode, unsupported mode, invalid maxResults, unsupported option, access or membership eligibility failure, and out-of-scope subscriber or analytics request rejection.

**Refactor**: Remove duplicated text that belongs in shared YT-201/YT-202 helpers while keeping endpoint-specific owner-visibility and membership-mode guidance reviewable in `members.py`.

### User Story 3 - Reject Unsupported or Ineligible Member List Requests Clearly

**Red**: Add failing validation and error-mapping checks for missing `part`, blank or unsupported `part`, missing `mode`, unsupported `mode`, invalid `maxResults`, empty `pageToken`, unsupported optional parameters, unsupported delegation/filter fields, API-key-only access, non-owner OAuth access, membership-not-enabled failure, quota failure, endpoint unavailable, upstream invalid request, and unexpected upstream failure.

**Green**: Implement validator and upstream-error mapper using shared safe categories; ensure OAuth tokens, stack traces, raw details, unsafe request context, and secret-bearing diagnostics are not exposed.

**Refactor**: Consolidate safe invalid-request helpers and keep the validation surface close to the supported endpoint subset.

### Shared Foundation Work

**Red**: Add failing scaffold/export/registration tests in `tests/unit/test_youtube_common_scaffolding.py`, `tests/contract/test_youtube_common_contract.py`, `tests/contract/test_youtube_members_contract.py`, `tests/integration/test_youtube_members_registration.py`, `tests/contract/test_youtube_tool_catalog_contract.py`, and `tests/integration/test_youtube_tool_registration.py`.

**Green**: Export `MEMBERS_LIST_*` symbols, add `build_members_list_tool_descriptor()` to the default registry, and add representative contract/example coverage.

**Refactor**: Keep `members.py` cohesive, keep Layer 1 changes narrow, and avoid changes to membership levels, subscriber lookup, delegated owner management, analytics, recommendations, search, or higher-level membership workflow modules.

## Risk and Mitigation

- **Quota discrepancy risk**: The YT-226 seed and existing YT-126 local metadata list quota cost 1, while the current official Google `members.list` documentation lists quota cost 2 as of 2026-06-01. Implementation must start with failing metadata tests and update public and any touched Layer 1 metadata to 2, recording the official-doc caveat in review materials.
- **Supported-parameter scope risk**: Current official docs list optional `hasAccessToLevel` and `filterByMemberChannelId`, but YT-126 exposes only `part`, `mode`, `pageToken`, and `maxResults`. YT-226 keeps those extra filters out of scope and rejects them clearly unless a later Layer 1 contract revision adds support.
- **Mode semantics risk**: `all_current` and `updates` have different paging expectations. The validator and examples must document both modes, preserve mode-specific page context, and reject page tokens used with an incompatible mode as safe invalid-request/upstream failures.
- **Scope risk**: Do not add subscriber lookup, membership-level listing, member administration, delegated owner management, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint behavior; those belong to separate tools or layers.
- **Security risk**: Do not expose OAuth tokens, raw upstream diagnostics, stack traces, raw request context, unsafe authorization context, or member details in failures, logs, metadata, or examples.
- **Cohesion risk**: `members_list` should live in a dedicated `members` Layer 2 module, not in `memberships_levels`, comments, channels, or higher-level workflow modules.

## Verification Commands

```bash
pytest tests/contract/test_youtube_members_contract.py tests/unit/test_youtube_members.py tests/integration/test_youtube_members_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```
