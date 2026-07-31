# Tasks: YT-302 Video Details

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/`  
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/data-model.md), [videos-get-video-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/contracts/videos-get-video-contract.md)

**Tests**: Tests are mandatory. Write each Red task first and verify it fails before its corresponding Green task. Final completion requires `python3 -m pytest` and `python3 -m ruff check .` after the final code change. Every new or modified Python function, including test fakes and helpers, needs a reStructuredText docstring.

**Organization**: Tasks are grouped by independently testable user story in priority order.

## Phase 1: Setup

**Purpose**: Confirm the established source seams and test targets before adding behavior. No dependency installation, persistence, or project scaffolding is required.

- [X] T001 Confirm the one-lookup boundary, permitted input groups, public result mapping, and targeted verification command against `/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/contracts/videos-get-video-contract.md`
- [X] T002 [P] Create the focused unit-test module with documented reusable fake lookup fixtures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`
- [X] T003 [P] Create the focused discovery-contract test module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`

---

## Phase 2: Foundational

**Purpose**: Establish the shared concrete-tool boundary that every story needs.

**⚠️ CRITICAL**: Complete this phase before user-story implementation.

- [X] T004 Add a failing concrete-descriptor boundary test that distinguishes executable video tools from representative-only descriptors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`
- [X] T005 Define the shared public schema, supported-part constants, safe error type, and concrete metadata factory for `videos_getVideo` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T006 Add reStructuredText docstrings to every new or modified Python function and class in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T007 Run the foundational contract check and confirm T004 passes after T005 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`

**Checkpoint**: A concrete public-tool contract boundary exists; P1, P2, and P3 work may proceed in priority order.

---

## Phase 3: User Story 1 - Retrieve a Video's Core Details (Priority: P1) 🎯 MVP

**Goal**: Let a client retrieve one available video through `videoId` and receive the normalized default detail shape.

**Independent Test**: Register only `videos_getVideo` with a fake lower-level lookup, invoke it with an available `videoId` and no `parts`, and verify one lookup requests the core source groups and returns the documented default fields rather than a collection envelope.

### Red — Tests for User Story 1

- [X] T008 [P] [US1] Add failing validation and core-normalization tests for required nonblank `videoId`, one lower-level call, and the default field mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`
- [X] T009 [P] [US1] Add failing contract tests for the `videos_getVideo` input schema, normalized-retrieval metadata, default-field provenance, and absence of a representative-only marker in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`
- [X] T010 [P] [US1] Add failing concrete registration and invocation tests using a fake successful lookup in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`
- [X] T011 [P] [US1] Add a failing default-dispatcher discovery and invocation test for `videos_getVideo` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Green — Implementation for User Story 1

- [X] T012 [US1] Implement `videoId` validation and construction of one lower-level request that always selects `snippet` and `contentDetails` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T013 [US1] Implement the single-item default normalizer for `videoId`, descriptive, channel, duration, category, tag, and thumbnail fields while preserving sparse source values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T014 [US1] Implement the executable `videos_getVideo` descriptor and handler that adapts the existing `videos_list` lookup without exposing its collection envelope in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T015 [US1] Export the concrete descriptor and add it to the default public-tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for every Python function, class, and test fake changed for core retrieval in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Refactor — User Story 1

- [X] T017 [US1] Refactor duplicated core extraction and descriptor setup without changing the default result contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T018 [US1] Run the focused core-retrieval test set and fix any failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

**Checkpoint**: `videos_getVideo` is independently usable for an available video without optional groups.

---

## Phase 4: User Story 2 - Request Additional Detail Groups (Priority: P2)

**Goal**: Let a client request supported optional groups while preserving the complete default result.

**Independent Test**: Invoke the registered tool with each supported `parts` value, then with multiple groups and an empty array; verify the lower-level part union and exact additive field mapping. Verify duplicate, unsupported, non-array, and non-text values fail before lookup.

### Red — Tests for User Story 2

- [X] T019 [P] [US2] Add failing tests for optional-part validation, empty-list behavior, duplicate and unsupported rejection, and core-plus-requested lower-part union in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`
- [X] T020 [P] [US2] Add failing contract tests for all five part values, their exact field mappings, and additive default-field behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`
- [X] T021 [P] [US2] Add failing invocation tests for one and multiple requested optional groups in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green — Implementation for User Story 2

- [X] T022 [US2] Implement validation of the optional unique `parts` array and deterministic union of requested groups with required core groups in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T023 [US2] Implement conditional mapping for `snippet`, `contentDetails`, `statistics`, `status`, and `topicDetails`, returning only requested available fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T024 [US2] Update the descriptor metadata, field provenance declarations, usage notes, and safe examples for every optional group in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T025 [US2] Add or update reStructuredText docstrings for every Python function, class, and test fake changed for optional detail groups in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Refactor — User Story 2

- [X] T026 [US2] Refactor the optional-part map into one authoritative mapping while retaining requested-only output behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T027 [US2] Run the focused optional-part test set and fix any failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

**Checkpoint**: The default shape remains stable, and each optional group is independently requestable and testable.

---

## Phase 5: User Story 3 - Understand Unavailable and Failed Lookups (Priority: P3)

**Goal**: Let clients receive safe, actionable failure categories without disclosure of sensitive availability or diagnostic details.

**Independent Test**: Use fake lower-level outcomes for empty items, unavailable/not-found, access denial, quota exhaustion, and source failure. Verify the correct safe category and sanitized details for each and confirm no private availability reason or secret-bearing value appears.

### Red — Tests for User Story 3

- [X] T028 [P] [US3] Add failing unit tests for translating empty items and unavailable source outcomes to `unavailable_resource`, and access, quota, and source failures to their distinct safe categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`
- [X] T029 [P] [US3] Add failing contract tests for documented error categories, safe remediation metadata, and prohibited diagnostic-detail exclusion in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`
- [X] T030 [P] [US3] Add failing registration-level invocation tests using fake unavailable, access, quota, and source failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green — Implementation for User Story 3

- [X] T031 [US3] Implement empty-result, unavailable, authorization-sensitive, quota, and source-failure translation while preserving the existing sanitizer boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T032 [US3] Ensure descriptor metadata and handler errors expose only documented category, safe field names, and retry or authorization guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T033 [US3] Add or update reStructuredText docstrings for every Python function, class, and test fake changed for failure handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Refactor — User Story 3

- [X] T034 [US3] Refactor duplicated error mapping and sanitization branches without changing the caller-visible categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T035 [US3] Run the focused failure-path test set and fix any failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

**Checkpoint**: All documented failure outcomes are independently testable and safe for callers.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Verify the complete contract, quality gates, and rollback boundary after all stories are complete.

- [X] T036 [P] Reconcile examples, field mappings, error categories, and rollback notes with the implemented public descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/contracts/videos-get-video-contract.md`
- [X] T037 [P] Execute the independent scenarios in the planning guide and update any stale verification instructions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/quickstart.md`
- [X] T038 Review every changed Python file for required reStructuredText docstrings and correct any omissions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T039 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T040 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every reported issue in `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can begin immediately.
- **Foundational (Phase 2)**: Depends on Setup; it establishes the concrete public-tool boundary used by every story.
- **US1 (Phase 3)**: Depends on Foundational; it is the MVP.
- **US2 (Phase 4)**: Depends on US1 because it extends the core descriptor and normalizer, while retaining an independently verifiable optional-group increment.
- **US3 (Phase 5)**: Depends on US1 because it extends the core handler's lookup outcome; it can begin after US1 in parallel with US2 if changes to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py` are coordinated.
- **Polish (Phase 6)**: Depends on all selected story phases.

### User Story Completion Order

```text
Setup → Foundational → US1 (MVP) → ┬→ US2
                                  └→ US3
                                        ↓
                                      Polish
```

### Parallel Opportunities

- T002 and T003 can proceed in parallel because they create different test files.
- In US1, T008 through T011 can proceed in parallel because each changes a different test file.
- In US2, T019 through T021 can proceed in parallel because each changes a different test file.
- In US3, T028 through T030 can proceed in parallel because each changes a different test file.
- T036 and T037 can proceed in parallel because they update different planning artifacts.
- US2 and US3 can be assigned to different developers after US1, but their shared source module requires serialized merge and test execution.

## Parallel Execution Examples

### User Story 1

```text
Task: "T008 Add core behavior tests in tests/unit/test_youtube_composed_videos.py"
Task: "T009 Add discovery contract tests in tests/contract/test_youtube_composed_videos_contract.py"
Task: "T010 Add direct registration tests in tests/integration/test_youtube_composed_tool_registration.py"
Task: "T011 Add default dispatcher tests in tests/integration/test_youtube_tool_registration.py"
```

### User Story 2

```text
Task: "T019 Add optional-part validation tests in tests/unit/test_youtube_composed_videos.py"
Task: "T020 Add optional-part contract tests in tests/contract/test_youtube_composed_videos_contract.py"
Task: "T021 Add optional-part invocation tests in tests/integration/test_youtube_composed_tool_registration.py"
```

### User Story 3

```text
Task: "T028 Add error-mapping unit tests in tests/unit/test_youtube_composed_videos.py"
Task: "T029 Add safe-error contract tests in tests/contract/test_youtube_composed_videos_contract.py"
Task: "T030 Add failure invocation tests in tests/integration/test_youtube_composed_tool_registration.py"
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational work.
2. Complete US1 through T018.
3. Verify the independent US1 test criterion and its focused test set.
4. Demo or release the core one-video detail workflow before optional groups and expanded failure behavior.

### Incremental Delivery

1. Deliver US1: default normalized retrieval for one available video.
2. Deliver US2: requested optional groups with strict part validation.
3. Deliver US3: safe unavailable, access, quota, and source-service outcomes.
4. Finish with contract reconciliation, quickstart validation, docstring review, full tests, and lint.

## Format Validation

- All 40 tasks use the required `- [ ] T### [P?] [US?] Description with absolute file path` checklist format.
- All user-story tasks carry exactly one story label; Setup, Foundational, and Polish tasks carry no story label.
- Every story contains Red tests before Green implementation, explicit docstring work, refactoring, and focused validation.
- The final phase requires the full repository test suite and lint to pass before feature completion.
