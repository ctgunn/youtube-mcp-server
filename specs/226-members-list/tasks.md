# Tasks: Layer 2 Tool `members_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/data-model.md), [contracts/members_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/contracts/members_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/quickstart.md)

**Tests**: Test tasks are required for every phase. Each story starts with Red tests, then Green implementation, then Refactor/docstring verification. Completion requires a final `pytest` run and `ruff check .`.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after shared foundation is in place.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature workspace and implementation targets are ready before writing Red tests.

- [X] T001 Verify the YT-226 design artifacts and current quota decision in /Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/research.md
- [X] T002 [P] Inspect existing Layer 2 list-tool patterns for `comments_list`, `i18nRegions_list`, and `guideCategories_list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/
- [X] T003 [P] Inspect existing Layer 1 `members.list` metadata and request boundary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/members.py
- [X] T004 [P] Inspect current default registry wiring patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared failing checks and public wiring expectations that block all user stories.

**Critical**: No user story implementation should begin until these shared Red checks exist and fail for the missing `members_list` public tool.

- [X] T005 [P] Add failing shared export checks for `MEMBERS_LIST_*` symbols in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T006 [P] Add failing shared public metadata checks for `members_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T007 [P] Add failing catalog coverage for `members_list` discovery and representative examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T008 [P] Add failing default registry discovery coverage for `members_list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T009 Add failing quota-alignment coverage for Layer 1 `members.list` review metadata showing quota cost `2` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_members_contract.py

**Checkpoint**: Foundation ready when shared Red checks fail because `members_list` symbols, metadata, and default registration are missing.

---

## Phase 3: User Story 1 - Retrieve Channel Members Through a Public Tool (Priority: P1) MVP

**Goal**: Power users with eligible owner authorization can call `members_list` and receive a near-raw member collection with selected mode, requested parts, paging context, and quota context preserved.

**Independent Test**: Invoke `members_list` with `part=snippet`, `mode=all_current` or `mode=updates`, eligible OAuth-backed owner context, and optional paging input, then verify the result preserves `members.list` endpoint context, quota cost `2`, returned `items`, selected mode, requested parts, and pagination fields.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add contract tests for `members_list` identity, input schema, and successful list result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py
- [X] T011 [P] [US1] Add unit tests for valid `all_current`, valid `updates`, paged requests, and successful empty result mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_members.py
- [X] T012 [P] [US1] Add integration tests for registering and executing `members_list` successful owner-scoped calls in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_members_registration.py

### Implementation for User Story 1 (Green)

- [X] T013 [US1] Create the Layer 2 members module with `MEMBERS_LIST_TOOL_NAME`, quota, supported parts, supported modes, input schema, and safe error class in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T014 [US1] Implement `validate_members_list_arguments` for `part=snippet`, `mode=all_current|updates`, optional `pageToken`, and optional `maxResults` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T015 [US1] Implement `map_members_list_result` to preserve endpoint, quota cost `2`, requested parts, mode, OAuth context, `items`, `kind`, `etag`, `nextPageToken`, and `pageInfo` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T016 [US1] Implement `build_members_list_handler` using `build_members_list_wrapper`, OAuth-required auth context, the validator, and result mapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T017 [US1] Implement `build_members_list_contract` and `build_members_list_tool_descriptor` for executable MCP registration in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T018 [US1] Export `members_list` constants, builders, validator, mapper, and error class from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T019 [US1] Register `build_members_list_tool_descriptor()` in the default tool registry in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T020 [US1] Align Layer 1 `members.list` quota metadata and docstrings to official quota cost `2` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/members.py

### Refactor and Validation for User Story 1

- [X] T021 [US1] Add or update reStructuredText docstrings for every new or changed Python function touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T022 [US1] Add or update reStructuredText docstrings for every changed Layer 1 helper touched by US1 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/members.py
- [X] T023 [US1] Run focused US1 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_members.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_members_registration.py

**Checkpoint**: US1 is independently functional when `members_list` can be discovered, invoked for owner-scoped successful and empty member-list retrieval, and returns near-raw list results with quota cost `2`.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Membership Access Before Calling (Priority: P2)

**Goal**: Client developers can inspect `members_list` before invocation and understand endpoint identity, quota cost `2`, OAuth-required owner access, channel-membership constraints, supported inputs, and out-of-scope workflows.

**Independent Test**: Review discovery metadata, descriptions, usage notes, caveats, and examples for `members_list` and verify all required quota, auth, access, request, and boundary information is visible without invoking implementation internals.

### Tests for User Story 2 (Red)

- [X] T024 [P] [US2] Add contract tests for metadata, description, usage notes, caveats, and safe public fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py
- [X] T025 [P] [US2] Add catalog tests for representative `members_list` examples covering success, paging, empty result, validation failures, access failure, and out-of-scope rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T026 [P] [US2] Add shared metadata regression checks for quota cost `2`, OAuth-required auth, and owner-only caveats in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

### Implementation for User Story 2 (Green)

- [X] T027 [US2] Add `MEMBERS_LIST_DESCRIPTION`, `MEMBERS_LIST_USAGE_NOTES`, and `MEMBERS_LIST_CAVEATS` with quota cost `2`, OAuth-required auth, owner-only visibility, and channel-membership constraints in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T028 [US2] Add `MEMBERS_LIST_CALLER_EXAMPLES` for current-member retrieval, update-stream retrieval, paged retrieval, empty success, missing part, missing mode, unsupported mode, invalid maxResults, unsupported option, access failure, and out-of-scope request rejection in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T029 [US2] Add `members_list` to the shared representative contract set in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T030 [US2] Ensure `build_members_list_contract` exposes active availability plus owner-only and channel-membership caveats in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py

### Refactor and Validation for User Story 2

- [X] T031 [US2] Add or update reStructuredText docstrings for metadata, example, and contract helper functions touched by US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T032 [US2] Run focused US2 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py

**Checkpoint**: US2 is independently functional when callers can understand quota, auth, access constraints, examples, and unsupported boundaries from public discovery surfaces alone.

---

## Phase 5: User Story 3 - Reject Unsupported or Ineligible Member List Requests Clearly (Priority: P3)

**Goal**: Callers receive deterministic safe validation and access feedback for malformed, unsupported, ineligible, quota, unavailable, and unexpected member-list outcomes.

**Independent Test**: Submit invalid or ineligible `members_list` requests and verify each failure maps to a safe caller-facing category without leaking OAuth tokens, raw upstream bodies, stack traces, raw request context, or sensitive member details.

### Tests for User Story 3 (Red)

- [X] T033 [P] [US3] Add unit tests for missing `part`, invalid `part`, missing `mode`, unsupported `mode`, invalid `maxResults`, empty `pageToken`, unsupported fields, unsupported filters, and unsupported delegation inputs in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_members.py
- [X] T034 [P] [US3] Add contract tests for safe error categories and sanitized diagnostics in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py
- [X] T035 [P] [US3] Add integration tests for dispatcher-level invalid request rejection and safe failure propagation in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_members_registration.py

### Implementation for User Story 3 (Green)

- [X] T036 [US3] Extend `validate_members_list_arguments` to reject unsupported optional parameters, `hasAccessToLevel`, `filterByMemberChannelId`, delegation fields, subscriber lookup fields, management actions, analytics, ranking, summarization, and enrichment fields in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T037 [US3] Implement `_members_list_auth_context` to reject API-key-only execution and require OAuth-compatible owner-scoped access in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T038 [US3] Implement `_map_members_list_upstream_error` for invalid request, authentication, authorization, quota, not-found, endpoint unavailable, and upstream failure categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T039 [US3] Ensure `MembersListToolError` sanitizes details with shared safe error conventions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py

### Refactor and Validation for User Story 3

- [X] T040 [US3] Add or update reStructuredText docstrings for validation, auth-context, error-mapping, and error classes touched by US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T041 [US3] Run focused US3 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_members.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_members_registration.py

**Checkpoint**: US3 is independently functional when invalid and ineligible requests fail with safe, specific, caller-facing outcomes and successful empty results remain distinct.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the full feature is coherent, documented, safe, and regression-free.

- [X] T042 [P] Update YT-226 implementation notes and quota discrepancy evidence in /Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/quickstart.md
- [X] T043 [P] Review generated contract documentation against implemented public metadata in /Users/ctgunn/Projects/youtube-mcp-server/specs/226-members-list/contracts/members_list.md
- [X] T044 Review all changed Python functions for reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py
- [X] T045 Review all changed exports and registry wiring for minimal scope in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T046 Run the focused YT-226 verification command and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/
- [X] T047 Run `pytest` for the full repository test suite and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/
- [X] T048 Run `ruff check .` and fix lint failures in /Users/ctgunn/Projects/youtube-mcp-server/

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
- **US1 Red tests**: T010, T011, and T012 can run in parallel.
- **US2 Red tests**: T024, T025, and T026 can run in parallel.
- **US3 Red tests**: T033, T034, and T035 can run in parallel.
- **Polish docs**: T042 and T043 can run in parallel.

## Parallel Example: User Story 1

```bash
# Launch US1 Red test authoring in parallel:
Task: "T010 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py"
Task: "T011 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_members.py"
Task: "T012 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_members_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 metadata/example tests in parallel:
Task: "T024 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py"
Task: "T025 [US2] Add catalog example tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T026 [US2] Add shared metadata checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 invalid-request and safe-error tests in parallel:
Task: "T033 [US3] Add validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_members.py"
Task: "T034 [US3] Add safe error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py"
Task: "T035 [US3] Add dispatcher failure integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_members_registration.py"
```

---

## Implementation Strategy

### MVP First

Complete Phase 1, Phase 2, and Phase 3 only. This delivers a discoverable and callable `members_list` tool for successful owner-scoped retrieval while preserving quota cost `2`, selected mode, requested parts, returned items, and pagination context.

### Incremental Delivery

1. **MVP**: US1 provides the callable member-list tool and default registry wiring.
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
