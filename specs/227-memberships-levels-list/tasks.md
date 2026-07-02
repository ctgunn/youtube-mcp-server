# Tasks: Layer 2 Tool `membershipsLevels_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/data-model.md), [contracts/membershipsLevels_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/contracts/membershipsLevels_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/quickstart.md)

**Tests**: Test tasks are required for every phase. Each story starts with Red tests, then Green implementation, then Refactor/docstring verification. Completion requires a final `pytest` run and `ruff check .`.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after shared foundation is in place.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature workspace and implementation targets are ready before writing Red tests.

- [X] T001 Verify the YT-227 design artifacts and supported `part=snippet` decision in /Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/research.md
- [X] T002 [P] Inspect existing Layer 2 list-tool patterns for `members_list`, `i18nRegions_list`, and `guideCategories_list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/
- [X] T003 [P] Inspect existing Layer 1 `membershipsLevels.list` metadata and request boundary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/memberships_levels.py
- [X] T004 [P] Inspect current default registry wiring patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared failing checks and public wiring expectations that block all user stories.

**Critical**: No user story implementation should begin until these shared Red checks exist and fail for the missing `membershipsLevels_list` public tool.

- [X] T005 [P] Add failing shared export checks for `MEMBERSHIPS_LEVELS_LIST_*` symbols in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T006 [P] Add failing shared public metadata checks for `membershipsLevels_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T007 [P] Add failing catalog coverage for `membershipsLevels_list` discovery and representative examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T008 [P] Add failing default registry discovery coverage for `membershipsLevels_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py

**Checkpoint**: Foundation ready when shared Red checks fail because `membershipsLevels_list` symbols, metadata, and default registration are missing.

---

## Phase 3: User Story 1 - Retrieve Membership Levels Through a Public Tool (Priority: P1) MVP

**Goal**: Power users with eligible owner authorization can call `membershipsLevels_list` and receive a near-raw membership-level collection with requested parts, quota context, and returned fields preserved.

**Independent Test**: Invoke `membershipsLevels_list` with `part=snippet` and eligible OAuth-backed owner context, then verify the result preserves `membershipsLevels.list` endpoint context, quota cost `1`, returned `items`, requested parts, and optional upstream fields.

### Tests for User Story 1 (Red)

- [X] T009 [P] [US1] Add contract tests for `membershipsLevels_list` identity, input schema, and successful list result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py
- [X] T010 [P] [US1] Add unit tests for valid `part=snippet`, successful result mapping, upstream field preservation, and successful empty result mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_memberships_levels.py
- [X] T011 [P] [US1] Add integration tests for registering and executing `membershipsLevels_list` successful owner-scoped calls in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_memberships_levels_registration.py

### Implementation for User Story 1 (Green)

- [X] T012 [US1] Create the Layer 2 memberships-levels module with `MEMBERSHIPS_LEVELS_LIST_TOOL_NAME`, quota cost `1`, supported parts, input schema, and safe error class in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T013 [US1] Implement `validate_memberships_levels_list_arguments` for required `part=snippet` and rejection of malformed part values in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T014 [US1] Implement `map_memberships_levels_list_result` to preserve endpoint, quota cost `1`, requested parts, OAuth context, `items`, `kind`, and `etag` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T015 [US1] Implement `build_memberships_levels_list_handler` using `build_memberships_levels_list_wrapper`, OAuth-required auth context, the validator, and result mapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T016 [US1] Implement `build_memberships_levels_list_contract` and `build_memberships_levels_list_tool_descriptor` for executable MCP registration in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T017 [US1] Export `membershipsLevels_list` constants, builders, validator, mapper, and error class from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T018 [US1] Register `build_memberships_levels_list_tool_descriptor()` in the default tool registry in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

### Refactor and Validation for User Story 1

- [X] T019 [US1] Add or update reStructuredText docstrings for every new or changed Python function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T020 [US1] Run focused US1 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_memberships_levels.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_memberships_levels_registration.py

**Checkpoint**: US1 is independently functional when `membershipsLevels_list` can be discovered, invoked for owner-scoped successful and empty membership-level retrieval, and returns near-raw list results with quota cost `1`.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Membership Access Before Calling (Priority: P2)

**Goal**: Client developers can inspect `membershipsLevels_list` before invocation and understand endpoint identity, quota cost `1`, OAuth-required owner access, channel-membership constraints, supported inputs, and out-of-scope workflows.

**Independent Test**: Review discovery metadata, descriptions, usage notes, caveats, and examples for `membershipsLevels_list` and verify all required quota, auth, access, request, and boundary information is visible without invoking implementation internals.

### Tests for User Story 2 (Red)

- [X] T021 [P] [US2] Add contract tests for metadata, description, usage notes, caveats, and safe public fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py
- [X] T022 [P] [US2] Add catalog tests for representative `membershipsLevels_list` examples covering success, empty result, validation failures, access failure, and out-of-scope rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T023 [P] [US2] Add shared metadata regression checks for quota cost `1`, OAuth-required auth, and owner-only caveats in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

### Implementation for User Story 2 (Green)

- [X] T024 [US2] Add `MEMBERSHIPS_LEVELS_LIST_DESCRIPTION`, `MEMBERSHIPS_LEVELS_LIST_USAGE_NOTES`, and `MEMBERSHIPS_LEVELS_LIST_CAVEATS` with quota cost `1`, OAuth-required auth, owner-only visibility, and channel-membership constraints in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T025 [US2] Add `MEMBERSHIPS_LEVELS_LIST_CALLER_EXAMPLES` for owner-authorized retrieval, empty success, missing part, invalid part, unsupported option, access failure, and out-of-scope member-list or analytics request rejection in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T026 [US2] Add `membershipsLevels_list` to the shared representative contract set in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T027 [US2] Ensure `build_memberships_levels_list_contract` exposes active availability plus owner-only and channel-membership caveats in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py

### Refactor and Validation for User Story 2

- [X] T028 [US2] Add or update reStructuredText docstrings for metadata, example, and contract helper functions touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T029 [US2] Run focused US2 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

**Checkpoint**: US2 is independently functional when callers can understand quota, auth, access constraints, examples, and unsupported boundaries from public discovery surfaces alone.

---

## Phase 5: User Story 3 - Reject Unsupported or Ineligible Membership Level Requests Clearly (Priority: P3)

**Goal**: Callers receive deterministic safe validation and access feedback for malformed, unsupported, ineligible, quota, unavailable, and unexpected membership-level list outcomes.

**Independent Test**: Submit invalid or ineligible `membershipsLevels_list` requests and verify each failure maps to a safe caller-facing category without leaking OAuth tokens, raw upstream bodies, stack traces, raw request context, or sensitive membership-level details.

### Tests for User Story 3 (Red)

- [X] T030 [P] [US3] Add unit tests for missing `part`, invalid `part`, unsupported fields, unsupported filters, unsupported paging controls, and unsupported delegation inputs in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_memberships_levels.py
- [X] T031 [P] [US3] Add contract tests for safe error categories and sanitized diagnostics in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py
- [X] T032 [P] [US3] Add integration tests for dispatcher-level invalid request rejection and safe failure propagation in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_memberships_levels_registration.py

### Implementation for User Story 3 (Green)

- [X] T033 [US3] Extend `validate_memberships_levels_list_arguments` to reject unsupported optional parameters, filters, paging controls, page tokens, maximum result counts, delegation fields, member-list selectors, subscriber lookup fields, management actions, analytics, ranking, summarization, and enrichment fields in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T034 [US3] Implement `_memberships_levels_list_auth_context` to reject API-key-only execution and require OAuth-compatible owner-scoped access in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T035 [US3] Implement `_map_memberships_levels_list_upstream_error` for invalid request, authentication, authorization, quota, not-found, endpoint unavailable, and upstream failure categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T036 [US3] Ensure `MembershipsLevelsListToolError` sanitizes details with shared safe error conventions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py

### Refactor and Validation for User Story 3

- [X] T037 [US3] Add or update reStructuredText docstrings for validation, auth-context, error-mapping, and error classes touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T038 [US3] Run focused US3 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_memberships_levels.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_memberships_levels_registration.py

**Checkpoint**: US3 is independently functional when invalid and ineligible requests fail with safe, specific, caller-facing outcomes and successful empty results remain distinct.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the full feature is coherent, documented, safe, and regression-free.

- [X] T039 [P] Review generated contract documentation against implemented public metadata in /Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/contracts/membershipsLevels_list.md
- [X] T040 [P] Review generated quickstart scenarios against implemented behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/quickstart.md
- [X] T041 Review all changed Python functions for reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py
- [X] T042 Review all changed exports and registry wiring for minimal scope in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T043 Run the focused YT-227 verification command and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/
- [X] T044 Run `pytest` for the full repository test suite and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/
- [X] T045 Run `ruff check .` and fix lint failures in /Users/ctgunn/Projects/youtube-mcp-server/

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Phase 1; blocks all story implementation.
- **Phase 3 US1**: Depends on Phase 2; recommended MVP.
- **Phase 4 US2**: Depends on Phase 2 and can run after or alongside US1 once the module surface exists.
- **Phase 5 US3**: Depends on Phase 2 and can run after or alongside US1 once the validator/error surface exists.
- **Phase 6 Polish**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3 after Phase 2; delivers callable MVP.
- **US2 (P2)**: Can be implemented independently after Phase 2, but benefits from US1 contract/descriptors existing.
- **US3 (P3)**: Can be implemented independently after Phase 2, but benefits from US1 validator/handler skeleton existing.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Contract and unit tests can usually be written in parallel.
- Implementation tasks touching the same Python module should be sequenced to reduce conflicts.
- Docstring tasks must be completed before the story checkpoint is considered done.
- Focused tests must pass before moving to final polish.

---

## Parallel Opportunities

- **Setup**: T002, T003, and T004 can run in parallel.
- **Foundation**: T005, T006, T007, and T008 can run in parallel because they touch different test files.
- **US1 Red tests**: T009, T010, and T011 can run in parallel.
- **US2 Red tests**: T021, T022, and T023 can run in parallel.
- **US3 Red tests**: T030, T031, and T032 can run in parallel.
- **Polish docs**: T039 and T040 can run in parallel.

## Parallel Example: User Story 1

```bash
# Launch US1 Red test authoring in parallel:
Task: "T009 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py"
Task: "T010 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_memberships_levels.py"
Task: "T011 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_memberships_levels_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 metadata/example tests in parallel:
Task: "T021 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py"
Task: "T022 [US2] Add catalog example tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T023 [US2] Add shared metadata checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 invalid-request and safe-error tests in parallel:
Task: "T030 [US3] Add validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_memberships_levels.py"
Task: "T031 [US3] Add safe error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py"
Task: "T032 [US3] Add dispatcher failure integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_memberships_levels_registration.py"
```

---

## Implementation Strategy

### MVP First

Complete Phase 1, Phase 2, and Phase 3 only. This delivers a discoverable and callable `membershipsLevels_list` tool for successful owner-scoped retrieval while preserving quota cost `1`, requested parts, returned membership-level resources, and upstream fields.

### Incremental Delivery

1. **MVP**: US1 provides the callable membership-level list tool and default registry wiring.
2. **Metadata hardening**: US2 makes quota, OAuth, owner-only access, channel-membership constraints, examples, and unsupported boundaries visible before invocation.
3. **Failure hardening**: US3 completes deterministic validation, safe error mapping, and ineligible-access handling.
4. **Polish**: Run focused verification, full `pytest`, and `ruff check .` before completion.

### Validation Checklist

- Every task uses `- [ ] T###` checklist format.
- User story phase tasks include `[US1]`, `[US2]`, or `[US3]`.
- Parallelizable tasks include `[P]`.
- Every task description includes an absolute file path.
- Test tasks precede implementation tasks in each user story.
- Python implementation phases include explicit reStructuredText docstring tasks.
- Final phase includes full repository test-suite and lint commands.
