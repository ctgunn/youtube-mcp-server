# Tasks: YT-145 Layer 1 Endpoint `videoAbuseReportReasons.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python changes must include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (e.g. `US1`, `US2`, `US3`)
- Every task includes an exact file path

## Path Conventions

- Single project layout rooted at `/Users/ctgunn/Projects/youtube-mcp-server`
- Source code under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm scope, source touchpoints, and feature-local references before test-first implementation starts

- [X] T001 Review the planned implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/plan.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/quickstart.md
- [X] T002 Review the YT-145 contract, research, and data-model artifacts in /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-wrapper-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-localization-contract.md
- [X] T003 [P] Review the existing Layer 1 wrapper, transport, and consumer patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T004 [P] Review the current Layer 1 metadata, transport, integration, and consumer coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_localization_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared endpoint registration, contract-test seam, and transport recognition that all YT-145 user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Add failing foundational wrapper registration and review-surface coverage for `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T006 [P] Add failing foundational transport coverage for the `GET /videoAbuseReportReasons` request path in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T007 [P] Create failing foundational contract-artifact coverage for localized video utility wrappers in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_localization_contract.py
- [X] T008 [P] Add failing foundational higher-layer summary coverage for `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T009 Implement `VideoAbuseReportReasonsListWrapper`, the builder, request-shape metadata, and the package export in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T010 Implement foundational transport recognition and normalized payload parsing for `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T011 Implement foundational higher-layer summary scaffolding for `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T012 Refactor foundational helper naming and add or update reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Retrieve Localized Abuse Report Reasons Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `videoAbuseReportReasons.list` wrapper that can retrieve localized abuse-report reason data for one display-language view through the shared executor flow and return stable normalized retrieval results

**Independent Test**: Submit a valid `videoAbuseReportReasons.list` request with `part` and `hl` and confirm the wrapper executes through the shared executor and returns a normalized successful result that preserves the requested display-language context

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Add failing happy-path wrapper tests for `videoAbuseReportReasons.list` metadata, required `part`, required `hl`, and successful execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T014 [P] [US1] Add failing transport tests for `GET /videoAbuseReportReasons` request construction and successful payload normalization in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T015 [P] [US1] Add failing integration tests for valid display-language retrieval through `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T016 [US1] Implement the valid retrieval path and deterministic `part` plus `hl` execution for successful `videoAbuseReportReasons.list` calls in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T017 [US1] Implement normalized successful retrieval payload handling, including successful empty upstream responses, in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T018 [US1] Implement a higher-layer `videoAbuseReportReasons.list` summary method for successful outcomes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T019 [US1] Add or update reStructuredText docstrings for the successful retrieval path in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T020 [US1] Refactor the successful retrieval path while keeping the User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: User Story 1 should now support independently testable successful localized abuse-reason retrieval

---

## Phase 4: User Story 2 - Review Quota, Access, and Localization Expectations Before Reuse (Priority: P2)

**Goal**: Make the `videoAbuseReportReasons.list` wrapper reviewable enough that maintainers can see quota, API-key access, localized lookup rules, and empty-result guidance without reading implementation internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, and higher-layer summary output to confirm quota cost `1`, API-key access, `part` plus `hl` rules, and localization guidance are visible and consistent

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T021 [P] [US2] Add failing contract-artifact coverage for `videoAbuseReportReasons.list` wrapper requirements in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_localization_contract.py
- [X] T022 [P] [US2] Add failing review-surface metadata coverage for quota visibility, auth mode, and request-boundary notes in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T023 [P] [US2] Add failing higher-layer review-summary coverage for `videoAbuseReportReasons.list` source metadata and localization visibility in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T024 [US2] Finalize maintainer-facing wrapper contract guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-wrapper-contract.md
- [X] T025 [US2] Finalize localization lookup and empty-result guidance in /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-localization-contract.md
- [X] T026 [US2] Implement quota, auth, and localized lookup review notes for `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T027 [US2] Update the YT-145 feature narrative to reflect final review-surface decisions in /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/quickstart.md
- [X] T028 [US2] Add or update reStructuredText docstrings for quota and localization review surfaces in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T029 [US2] Refactor metadata wording and review-surface naming while keeping the User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-wrapper-contract.md

**Checkpoint**: User Story 2 should now be independently testable through feature artifacts, metadata, and higher-layer review surfaces

---

## Phase 5: User Story 3 - Reject Invalid or Unsupported Abuse-Reason Requests Clearly (Priority: P3)

**Goal**: Ensure missing required inputs, unsupported modifiers, and valid empty-result outcomes are clearly distinguished so downstream callers can remediate requests correctly

**Independent Test**: Submit requests with missing `part`, missing `hl`, unsupported modifiers, and valid zero-item results, then confirm the wrapper returns distinct normalized invalid-request or successful empty-result outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T030 [P] [US3] Add failing invalid-request unit coverage for missing `part`, missing `hl`, and unsupported fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T031 [P] [US3] Add failing invalid-request and empty-result transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T032 [P] [US3] Add failing invalid and empty-result integration coverage for `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T033 [US3] Implement deterministic validation for missing required inputs and unsupported modifiers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T034 [US3] Implement normalized invalid-request and successful empty-result handling for `videoAbuseReportReasons.list` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T035 [US3] Update higher-layer `videoAbuseReportReasons.list` summary compatibility for invalid-request and empty-result expectations in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T036 [US3] Document invalid-request and empty-result retrieval behavior in /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/research.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/quickstart.md
- [X] T037 [US3] Add or update reStructuredText docstrings for the failure-path retrieval logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T038 [US3] Refactor invalid and empty-result retrieval handling while keeping the User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/quickstart.md

**Checkpoint**: All three user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation consistency, and whole-repository validation

- [X] T039 [P] Reconcile feature-level documentation and task references across /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/data-model.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-localization-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/quickstart.md
- [X] T040 [P] Review all touched Python modules for reStructuredText docstring completeness in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T041 Run the YT-145 targeted validation flow from /Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/quickstart.md against /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_localization_contract.py
- [X] T042 Run the full repository test suite and lint validation from /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/src/ and resolve any failing tests before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP story
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses the wrapper surface introduced by User Story 1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on the retrieval surface introduced by User Story 1
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational completion and has no dependency on other user stories
- **User Story 2 (P2)**: Depends on the `videoAbuseReportReasons.list` wrapper and summary surface from User Story 1 but remains independently testable through review artifacts and summaries
- **User Story 3 (P3)**: Depends on the `videoAbuseReportReasons.list` wrapper and transport surface from User Story 1 but remains independently testable through invalid-request and empty-result scenarios

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Wrapper metadata and validation before consumer summary updates
- Transport normalization before success or failure summaries that depend on it
- Core implementation before integration validation (Green)
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run full affected test suites (Refactor)
- Before marking the feature complete, run the targeted validation flow and then the full repository suite

### Parallel Opportunities

- `T003` and `T004` can run in parallel after `T001`
- `T006`, `T007`, and `T008` can run in parallel after `T005`
- Within **US1**, `T013`, `T014`, and `T015` can run in parallel
- Within **US2**, `T021`, `T022`, and `T023` can run in parallel
- Within **US3**, `T030`, `T031`, and `T032` can run in parallel
- In the polish phase, `T039` and `T040` can run in parallel

### Story Completion Order

- **MVP order**: US1
- **Recommended incremental order**: US1 → US2 → US3
- **Parallelizable after Foundation**: US2 contract and review-surface Red tests can begin while US1 implementation is underway; US3 Red tests can begin once the shared retrieval seam exists

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "Add failing happy-path wrapper tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "Add failing contract-artifact coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_localization_contract.py"
Task: "Add failing review-surface metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing higher-layer review-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing invalid-request unit coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing invalid-request and empty-result transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing invalid and empty-result integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported retrieval success path independently
5. Demo or hand off the MVP internal wrapper before expanding reviewability and invalid-request handling

### Incremental Delivery

1. Complete Setup + Foundational to establish the wrapper, export, transport, summary, and contract-test seam
2. Add User Story 1 to deliver the usable retrieval path
3. Add User Story 2 to make the retrieval contract reviewable for maintainers and higher layers
4. Add User Story 3 to harden invalid and unsupported request handling
5. Finish with polish and full-suite validation

### Parallel Team Strategy

1. One developer completes Setup + Foundational
2. After Foundational is complete:
   - Developer A can implement User Story 1
   - Developer B can prepare User Story 2 Red tests and contract assertions
   - Developer C can prepare User Story 3 Red tests for invalid and empty-result paths
3. Merge stories in priority order, keeping each independently testable

---

## Notes

- `[P]` tasks touch different files or can be completed without waiting on another incomplete task in the same phase
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/spec.md`
- User Story 1 is the suggested MVP scope
- All tasks above follow the required checklist format with checkbox, task ID, optional labels, and exact file paths
