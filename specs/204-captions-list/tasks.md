# Tasks: YT-204 Layer 2 Tool `captions_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/data-model.md), [contracts/captions-list-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/contracts/captions-list-tool-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/quickstart.md)

**Tests**: Required for every story. Write failing tests first, implement the minimum Green changes, refactor, run focused checks, then run full repository validation and Ruff after the final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after foundational safeguards are complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase because it touches different files or only reads files
- **[Story]**: User story label for story phases only
- Every task includes an exact repository path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature branch, planning artifacts, and current Layer 1/Layer 2 surfaces before writing Red tests.

- [X] T001 Verify the working branch is `204-captions-list` and confirm `/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/plan.md` matches the current implementation scope
- [X] T002 [P] Review the public tool contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/contracts/captions-list-tool-contract.md` before editing tests
- [X] T003 [P] Review the existing Layer 1 captions wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py` before adding Layer 2 handler calls
- [X] T004 [P] Review the existing concrete Layer 2 activities pattern in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` before creating the captions module
- [X] T005 [P] Review shared Layer 2 contracts, conventions, examples, and family placement in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- [X] T006 [P] Review dispatcher and MCP routing behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T007 [P] Review existing YouTube and MCP tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the concrete captions module boundary and import/export safeguards that all user stories depend on.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T008 Add a failing import/export contract test for a concrete captions Layer 2 module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`
- [X] T009 Add a failing resource-family placement test requiring the captions family to point at `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T010 Create the concrete captions Layer 2 module skeleton in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T011 Export the concrete captions module symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T012 Update reStructuredText docstrings for foundational module and export helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T013 Run foundational focused checks `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/unit/test_youtube_common_scaffolding.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve Caption Tracks Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `captions_list` with a valid authorized video-based request and receive near-raw caption-track items, requested parts, empty collections, and pagination details.

**Independent Test**: Invoke `captions_list` with supported authorized video-based requests and confirm results preserve caption-track items, requested parts, empty collections, and page tokens.

### Tests for User Story 1 (REQUIRED)

- [X] T014 [P] [US1] Add failing unit tests for authorized video-based request mapping, result item preservation, empty collection success, requested parts, and pagination tokens in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py`
- [X] T015 [P] [US1] Add failing contract tests for the successful `captions_list` result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`
- [X] T016 [P] [US1] Add failing integration tests proving `captions_list` registers as an executable tool and calls through a fake Layer 1 captions wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`
- [X] T017 [P] [US1] Add a failing MCP routing test for `tools/call` returning a successful `captions_list` structured result in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 1

- [X] T018 [US1] Implement `CAPTIONS_LIST_INPUT_SCHEMA` and authorized video request shaping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T019 [US1] Implement the `captions_list` handler factory that invokes the existing Layer 1 `captions.list` wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T020 [US1] Implement the near-raw caption-track collection result mapper for `items`, `requestedParts`, `nextPageToken`, `prevPageToken`, `pageInfo`, `endpoint`, `quotaCost`, lookup summary, and delegation summary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T021 [US1] Register `captions_list` in the default public tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US1] Export the `captions_list` descriptor builder and schema from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T023 [US1] Update reStructuredText docstrings for all new or modified `captions_list` schema, handler, result mapper, and registration functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T024 [US1] Refactor the `captions_list` happy-path implementation while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T025 [US1] Run focused User Story 1 checks `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_method_routing.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently testable and delivers the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Lookup Rules Before Calling (Priority: P2)

**Goal**: A client developer can inspect `captions_list` before invocation and see upstream identity, quota cost `50`, OAuth-required auth, required `videoId`, optional `id`, and delegated content-owner guidance.

**Independent Test**: Review tool discovery, descriptor metadata, description, and usage examples to confirm cost, OAuth, lookup, and delegation requirements are visible before invocation.

### Tests for User Story 2 (REQUIRED)

- [X] T026 [P] [US2] Add failing contract tests for `captions_list` metadata fields, quota cost `50`, OAuth-required auth, availability state, usage notes, required `videoId`, optional `id`, and delegation caveat in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`
- [X] T027 [P] [US2] Add failing integration tests proving `captions_list` registration exposes caller-facing metadata, description quota text, OAuth requirement, and usage notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`
- [X] T028 [P] [US2] Add failing `tools/list` discovery tests for optional metadata preservation without breaking baseline tool descriptors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`
- [X] T029 [P] [US2] Add failing catalog regression tests proving any representative `captions_list` example remains aligned with the concrete `captions_list` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 2

- [X] T030 [US2] Add `captions_list` `YouTubeToolContract` metadata, usage notes, caveats, and response boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T031 [US2] Extend or reuse dispatcher registration to accept and preserve safe optional tool metadata for `captions_list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T032 [US2] Ensure MCP `tools/list` responses preserve optional `captions_list` metadata while existing descriptors remain compatible in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T033 [US2] Update concrete `captions_list` usage examples for authorized video lookup, caption track identifier filter, paginated continuation, empty result handling, and delegated content-owner context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T034 [US2] Update reStructuredText docstrings for metadata, usage-note, dispatcher metadata, and MCP discovery changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T035 [US2] Refactor duplicated quota, auth, caveat, and usage-note wording while keeping metadata tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T036 [US2] Run focused User Story 2 checks `python3 -m pytest tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_list_tools_method.py tests/contract/test_youtube_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently testable and pre-invocation metadata is visible.

---

## Phase 5: User Story 3 - Reject Unsupported Caption Lookup Requests Clearly (Priority: P3)

**Goal**: A caller receives stable validation feedback when `captions_list` requests omit `part`, omit `videoId`, misuse `id`, use unsupported fields, exceed bounds, omit OAuth authorization, or provide invalid delegation context.

**Independent Test**: Submit representative invalid requests and confirm the tool rejects them with safe, stable caller-facing categories and remediation details.

### Tests for User Story 3 (REQUIRED)

- [X] T037 [P] [US3] Add failing unit tests for missing `part`, missing `videoId`, `id` without `videoId`, unsupported fields, invalid `maxResults`, and invalid delegation context in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py`
- [X] T038 [P] [US3] Add failing contract tests for OAuth-required access requirements, delegated-owner guidance, and safe error categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py`
- [X] T039 [P] [US3] Add failing integration tests for invalid `captions_list` calls through the dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py`
- [X] T040 [P] [US3] Add failing MCP routing tests for invalid `tools/call` `captions_list` requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 3

- [X] T041 [US3] Implement required `part` and `videoId` validation plus optional `id` narrowing rules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T042 [US3] Implement OAuth preflight and delegated content-owner validation for `captions_list` requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T043 [US3] Implement safe `captions_list` error mapping for invalid requests, authentication failures, authorization failures, quota exhaustion, missing resources, endpoint unavailability, and upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T044 [US3] Update MCP error mapping only if custom `captions_list` errors are not safely represented by existing routing behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T045 [US3] Tighten `captions_list` input schema bounds and unsupported-field behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T046 [US3] Update reStructuredText docstrings for lookup validation, OAuth preflight, delegation validation, schema bounds, and error mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T047 [US3] Refactor validation and error helpers while preserving endpoint-specific scope in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
- [X] T048 [US3] Run focused User Story 3 checks `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_method_routing.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 3 is independently testable and unsupported requests fail safely.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the combined endpoint slice, refresh review-facing artifacts if implementation details shift, and complete repository-wide verification.

- [X] T049 [P] Update the quickstart validation notes if final implementation commands or touched files differ in `/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/quickstart.md`
- [X] T050 [P] Update the captions contract if implementation uncovers a documented caveat or error category adjustment in `/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/contracts/captions-list-tool-contract.md`
- [X] T051 [P] Review public exports and remove unused symbols in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T052 Run combined focused checks `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T053 Run Layer 1 guard checks `python3 -m pytest tests/contract/test_layer1_captions_contract.py tests/unit/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T054 Run the full repository test suite `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T055 Run lint validation `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T056 Confirm every new or modified Python function has a reStructuredText docstring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T057 Confirm `git diff --check` reports no whitespace errors from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user story work
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can run after or alongside US1 if edits to `captions.py`, `dispatcher.py`, and discovery tests are coordinated
- **User Story 3 (Phase 5)**: Depends on Foundational completion; can run after or alongside US1/US2 if edits to `captions.py` and routing tests are coordinated
- **Polish (Phase 6)**: Depends on all selected user stories being complete

### User Story Dependencies

- **US1 Retrieve Caption Tracks Through a Public Tool**: No dependency on US2 or US3 after Foundational; recommended MVP because it makes `captions_list` executable
- **US2 Understand Cost, Authorization, and Lookup Rules Before Calling**: No dependency on US3; may build on US1 registration but remains independently testable through metadata and discovery checks
- **US3 Reject Unsupported Caption Lookup Requests Clearly**: No dependency on US2; may build on US1 handler scaffolding but remains independently testable through validation and error checks

### Within Each User Story

- Red tests must be written and observed failing before Green implementation
- Schema and contract metadata before handler wiring
- Handler wiring before registration
- Registration before MCP routing checks
- reStructuredText docstrings before the story checkpoint
- Refactor only after focused tests pass
- Full repository validation occurs in Phase 6 after final code changes

### Parallel Opportunities

- Setup review tasks T002, T003, T004, T005, T006, and T007 can run in parallel
- US1 Red tests T014, T015, T016, and T017 can run in parallel
- US2 Red tests T026, T027, T028, and T029 can run in parallel
- US3 Red tests T037, T038, T039, and T040 can run in parallel
- Polish documentation/export review tasks T049, T050, and T051 can run in parallel
- Different user stories can be implemented by separate contributors after Phase 2 if shared-file edits are coordinated

---

## Parallel Example: User Story 1

```bash
# Add Red tests for US1 in parallel:
Task: "T014 [US1] Add authorized video request and result mapping unit tests in tests/unit/test_youtube_captions.py"
Task: "T015 [US1] Add successful result contract tests in tests/contract/test_youtube_captions_contract.py"
Task: "T016 [US1] Add executable registration integration tests in tests/integration/test_youtube_captions_registration.py"
Task: "T017 [US1] Add MCP tools/call success routing test in tests/unit/test_method_routing.py"
```

## Parallel Example: User Story 2

```bash
# Add Red tests for US2 in parallel:
Task: "T026 [US2] Add metadata contract tests in tests/contract/test_youtube_captions_contract.py"
Task: "T027 [US2] Add registration metadata integration tests in tests/integration/test_youtube_captions_registration.py"
Task: "T028 [US2] Add tools/list metadata tests in tests/unit/test_list_tools_method.py"
Task: "T029 [US2] Add representative catalog alignment tests in tests/contract/test_youtube_tool_catalog_contract.py"
```

## Parallel Example: User Story 3

```bash
# Add Red tests for US3 in parallel:
Task: "T037 [US3] Add lookup and bounds unit tests in tests/unit/test_youtube_captions.py"
Task: "T038 [US3] Add OAuth, delegation, and error contract tests in tests/contract/test_youtube_captions_contract.py"
Task: "T039 [US3] Add invalid call integration tests in tests/integration/test_youtube_captions_registration.py"
Task: "T040 [US3] Add MCP tools/call invalid request tests in tests/unit/test_method_routing.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 for US1
3. Run `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_method_routing.py`
4. Stop and validate that `captions_list` can be discovered, invoked for a valid authorized video request, and returns near-raw caption-track collection data with pagination and empty-result behavior

### Incremental Delivery

1. Complete Setup and Foundational module safeguards
2. Deliver US1 executable caption-track retrieval as the MVP
3. Deliver US2 quota/auth/upstream metadata visibility
4. Deliver US3 validation and safe rejection behavior
5. Complete Phase 6 full-suite and lint validation

### Parallel Team Strategy

With multiple contributors:

1. Complete Phase 1 and Phase 2 together
2. Assign US1 to the contributor owning handler and registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
3. Assign US2 to the contributor owning discovery metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
4. Assign US3 to the contributor owning lookup validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`
5. Coordinate edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` before final integration

## Notes

- [P] tasks are safe to start in parallel when they touch different files or only review files
- Story labels map directly to priorities in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/204-captions-list/spec.md)
- This task list intentionally limits implementation to one concrete endpoint-backed public tool, `captions_list`
- Final completion requires `python3 -m pytest`, `python3 -m ruff check .`, and `git diff --check`
