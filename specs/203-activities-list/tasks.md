# Tasks: YT-203 Layer 2 Tool `activities_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/data-model.md), [contracts/activities-list-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/contracts/activities-list-tool-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/quickstart.md)

**Tests**: Required for every story. Write failing tests first, implement the minimum Green changes, refactor, run focused checks, then run full repository validation and Ruff after the final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after foundational safeguards are complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase because it touches different files or only reads files
- **[Story]**: User story label for story phases only
- Every task includes an exact repository path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature branch, planning artifacts, and current Layer 1/Layer 2 surfaces before writing Red tests.

- [X] T001 Verify the working branch is `203-activities-list` and confirm `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/plan.md` matches the current implementation scope
- [X] T002 [P] Review the public tool contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/contracts/activities-list-tool-contract.md` before editing tests
- [X] T003 [P] Review the existing Layer 1 activities wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py` before adding Layer 2 handler calls
- [X] T004 [P] Review shared Layer 2 contracts, conventions, examples, and family placement in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- [X] T005 [P] Review dispatcher and MCP routing behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T006 [P] Review existing YouTube and MCP tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the concrete activities module boundary and import/export safeguards that all user stories depend on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T007 Add a failing import/export contract test for a concrete activities Layer 2 module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_activities_contract.py`
- [X] T008 Add a failing resource-family placement test requiring the activities family to point at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 Create the concrete activities Layer 2 module skeleton in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T010 Export the concrete activities module symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T011 Update reStructuredText docstrings for foundational module and export helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T012 Run foundational focused checks `python3 -m pytest tests/contract/test_youtube_activities_contract.py tests/unit/test_youtube_common_scaffolding.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve Channel Activity Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `activities_list` with a valid channel-based request and receive near-raw activity items, requested parts, empty collections, and pagination details.

**Independent Test**: Invoke `activities_list` with supported channel-based requests and confirm results preserve activity items, requested parts, empty collections, and page tokens.

### Tests for User Story 1 (REQUIRED)

- [X] T013 [P] [US1] Add failing unit tests for channel-based request mapping, result item preservation, empty collection success, requested parts, and pagination tokens in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_activities.py`
- [X] T014 [P] [US1] Add failing contract tests for the successful `activities_list` result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_activities_contract.py`
- [X] T015 [P] [US1] Add failing integration tests proving `activities_list` registers as an executable tool and calls through a fake Layer 1 activities wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_activities_registration.py`
- [X] T016 [P] [US1] Add a failing MCP routing test for `tools/call` returning a successful `activities_list` structured result in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 1

- [X] T017 [US1] Implement `ACTIVITIES_LIST_INPUT_SCHEMA` and public channel request shaping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T018 [US1] Implement the `activities_list` handler factory that invokes the existing Layer 1 `activities.list` wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T019 [US1] Implement the near-raw activity collection result mapper for `items`, `requestedParts`, `nextPageToken`, `prevPageToken`, `pageInfo`, `endpoint`, `quotaCost`, and selector summary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T020 [US1] Register `activities_list` in the default public tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T021 [US1] Export the `activities_list` descriptor builder and schema from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T022 [US1] Update reStructuredText docstrings for all new or modified `activities_list` schema, handler, result mapper, and registration functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T023 [US1] Refactor the `activities_list` happy-path implementation while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T024 [US1] Run focused User Story 1 checks `python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_method_routing.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently testable and delivers the MVP.

---

## Phase 4: User Story 2 - Understand Cost and Access Before Calling (Priority: P2)

**Goal**: A client developer can inspect `activities_list` before invocation and see upstream identity, quota cost `1`, mixed/conditional auth, selector-specific access notes, and deprecated `home` caveat.

**Independent Test**: Review tool discovery, descriptor metadata, description, and usage examples to confirm cost and access requirements are visible before invocation.

### Tests for User Story 2 (REQUIRED)

- [X] T025 [P] [US2] Add failing contract tests for `activities_list` metadata fields, quota cost `1`, mixed/conditional auth, availability state, usage notes, and deprecated `home` caveat in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_activities_contract.py`
- [X] T026 [P] [US2] Add failing integration tests proving `activities_list` registration exposes caller-facing metadata, description quota text, and usage notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_activities_registration.py`
- [X] T027 [P] [US2] Add failing `tools/list` discovery tests for optional metadata preservation without breaking baseline tool descriptors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`
- [X] T028 [P] [US2] Add failing catalog regression tests proving the representative `activities_list` example remains aligned with the concrete `activities_list` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 2

- [X] T029 [US2] Add `activities_list` `YouTubeToolContract` metadata, usage notes, caveats, and response boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T030 [US2] Extend dispatcher registration to accept and preserve safe optional tool metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T031 [US2] Ensure MCP `tools/list` responses preserve optional `activities_list` metadata while existing descriptors remain compatible in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T032 [US2] Update concrete `activities_list` usage examples for public channel, pagination, authorized `mine`, and deprecated `home` selector scenarios in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T033 [US2] Update reStructuredText docstrings for metadata, usage-note, dispatcher metadata, and MCP discovery changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T034 [US2] Refactor duplicated quota, auth, caveat, and usage-note wording while keeping metadata tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T035 [US2] Run focused User Story 2 checks `python3 -m pytest tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_list_tools_method.py tests/contract/test_youtube_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently testable and pre-invocation metadata is visible.

---

## Phase 5: User Story 3 - Reject Unsupported Activity Requests Clearly (Priority: P3)

**Goal**: A caller receives stable validation feedback when `activities_list` requests omit selectors, provide conflicting selectors, use unsupported fields, exceed bounds, or require unavailable authorization.

**Independent Test**: Submit representative invalid requests and confirm the tool rejects them with safe, stable caller-facing categories and remediation details.

### Tests for User Story 3 (REQUIRED)

- [X] T036 [P] [US3] Add failing unit tests for missing selector, multiple selectors, missing `part`, unsupported fields, invalid `maxResults`, and deprecated `home` caveat handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_activities.py`
- [X] T037 [P] [US3] Add failing contract tests for selector-specific public versus authorized-user access requirements and safe error categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_activities_contract.py`
- [X] T038 [P] [US3] Add failing integration tests for invalid `activities_list` calls through the dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_activities_registration.py`
- [X] T039 [P] [US3] Add failing MCP routing tests for invalid `tools/call` `activities_list` requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 3

- [X] T040 [US3] Implement exact-one selector validation for `channelId`, `mine`, and `home` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T041 [US3] Implement selector-specific auth preflight for public `channelId` and authorized `mine` or `home` requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T042 [US3] Implement safe `activities_list` error mapping for invalid requests, auth failures, quota exhaustion, missing resources, deprecated endpoint behavior, endpoint unavailability, and upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T043 [US3] Update MCP error mapping only if custom `activities_list` errors are not safely represented by existing routing behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T044 [US3] Tighten `activities_list` input schema bounds and unsupported-field behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T045 [US3] Update reStructuredText docstrings for selector validation, auth preflight, schema bounds, and error mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T046 [US3] Refactor validation and error helpers while preserving endpoint-specific scope in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
- [X] T047 [US3] Run focused User Story 3 checks `python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_method_routing.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 3 is independently testable and unsupported requests fail safely.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the combined endpoint slice, refresh review-facing artifacts if implementation details shift, and complete repository-wide verification.

- [X] T048 [P] Update the quickstart validation notes if final implementation commands or touched files differ in `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/quickstart.md`
- [X] T049 [P] Update the activities contract if implementation uncovers a documented caveat or error category adjustment in `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/contracts/activities-list-tool-contract.md`
- [X] T050 [P] Review public exports and remove unused symbols in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T051 Run combined focused checks `python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T052 Run Layer 1 guard checks `python3 -m pytest tests/contract/test_layer1_activities_contract.py tests/unit/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T053 Run the full repository test suite `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T054 Run lint validation `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T055 Confirm every new or modified Python function has a reStructuredText docstring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T056 Confirm `git diff --check` reports no whitespace errors from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user story work
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can run after or alongside US1 if edits to `activities.py`, `dispatcher.py`, and discovery tests are coordinated
- **User Story 3 (Phase 5)**: Depends on Foundational completion; can run after or alongside US1/US2 if edits to `activities.py` and routing tests are coordinated
- **Polish (Phase 6)**: Depends on all selected user stories being complete

### User Story Dependencies

- **US1 Retrieve Channel Activity Through a Public Tool**: No dependency on US2 or US3 after Foundational; recommended MVP because it makes `activities_list` executable
- **US2 Understand Cost and Access Before Calling**: No dependency on US3; may build on US1 registration but remains independently testable through metadata and discovery checks
- **US3 Reject Unsupported Activity Requests Clearly**: No dependency on US2; may build on US1 handler scaffolding but remains independently testable through validation and error checks

### Within Each User Story

- Red tests must be written and observed failing before Green implementation
- Schema and contract metadata before handler wiring
- Handler wiring before registration
- Registration before MCP routing checks
- reStructuredText docstrings before the story checkpoint
- Refactor only after focused tests pass
- Full repository validation occurs in Phase 6 after final code changes

### Parallel Opportunities

- Setup review tasks T002, T003, T004, T005, and T006 can run in parallel
- US1 Red tests T013, T014, T015, and T016 can run in parallel
- US2 Red tests T025, T026, T027, and T028 can run in parallel
- US3 Red tests T036, T037, T038, and T039 can run in parallel
- Polish documentation/export review tasks T048, T049, and T050 can run in parallel
- Different user stories can be implemented by separate contributors after Phase 2 if shared-file edits are coordinated

---

## Parallel Example: User Story 1

```bash
# Add Red tests for US1 in parallel:
Task: "T013 [US1] Add channel request and result mapping unit tests in tests/unit/test_youtube_activities.py"
Task: "T014 [US1] Add successful result contract tests in tests/contract/test_youtube_activities_contract.py"
Task: "T015 [US1] Add executable registration integration tests in tests/integration/test_youtube_activities_registration.py"
Task: "T016 [US1] Add MCP tools/call success routing test in tests/unit/test_method_routing.py"
```

## Parallel Example: User Story 2

```bash
# Add Red tests for US2 in parallel:
Task: "T025 [US2] Add metadata contract tests in tests/contract/test_youtube_activities_contract.py"
Task: "T026 [US2] Add registration metadata integration tests in tests/integration/test_youtube_activities_registration.py"
Task: "T027 [US2] Add tools/list metadata tests in tests/unit/test_list_tools_method.py"
Task: "T028 [US2] Add representative catalog alignment tests in tests/contract/test_youtube_tool_catalog_contract.py"
```

## Parallel Example: User Story 3

```bash
# Add Red tests for US3 in parallel:
Task: "T036 [US3] Add selector and bounds unit tests in tests/unit/test_youtube_activities.py"
Task: "T037 [US3] Add auth and error contract tests in tests/contract/test_youtube_activities_contract.py"
Task: "T038 [US3] Add invalid call integration tests in tests/integration/test_youtube_activities_registration.py"
Task: "T039 [US3] Add MCP tools/call invalid request tests in tests/unit/test_method_routing.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 for US1
3. Run `python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_method_routing.py`
4. Stop and validate that `activities_list` can be discovered, invoked for a valid channel request, and returns near-raw activity collection data with pagination and empty-result behavior

### Incremental Delivery

1. Complete Setup and Foundational module safeguards
2. Deliver US1 executable channel activity retrieval as the MVP
3. Deliver US2 quota/auth/upstream metadata visibility
4. Deliver US3 validation and safe rejection behavior
5. Complete Phase 6 full-suite and lint validation

### Parallel Team Strategy

With multiple contributors:

1. Complete Phase 1 and Phase 2 together
2. Assign US1 to the contributor owning handler and registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
3. Assign US2 to the contributor owning discovery metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
4. Assign US3 to the contributor owning selector validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`
5. Coordinate edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` before final integration

## Notes

- [P] tasks are safe to start in parallel when they touch different files or only review files
- Story labels map directly to priorities in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/spec.md)
- This task list intentionally limits implementation to one concrete endpoint-backed public tool, `activities_list`
- Final completion requires `python3 -m pytest`, `python3 -m ruff check .`, and `git diff --check`
