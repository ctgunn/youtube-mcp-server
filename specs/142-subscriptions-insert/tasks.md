# Tasks: YT-142 Layer 1 Endpoint `subscriptions.insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/data-model.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this belongs to (for example `US1`, `US2`, `US3`)
- Every task includes an exact file path

## Path Conventions

- Single project layout rooted at `/Users/ctgunn/Projects/youtube-mcp-server`
- Source code under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- Feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm scope, source touchpoints, and feature-local references before test-first implementation starts

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/plan.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md` to confirm the implementation and validation flow
- [X] T002 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-wrapper-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-auth-write-contract.md` to confirm contract boundaries
- [X] T003 [P] Review the existing Layer 1 mutation wrapper, transport, consumer, and export patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T004 [P] Review the current Layer 1 metadata, transport, integration, and consumer coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared endpoint registration, contract-test seam, transport recognition, and summary seam that all YT-142 user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Add failing foundational wrapper registration and review-surface coverage for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T006 [P] Add failing foundational transport coverage for the `POST /subscriptions` request path in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T007 [P] Add failing foundational contract-artifact coverage for subscription insert wrappers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`
- [X] T008 [P] Add failing foundational higher-layer summary coverage for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T009 Implement `subscriptions.insert` wrapper registration, builder metadata, request-shape metadata, and the package export in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T010 Implement foundational transport recognition and normalized payload parsing for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T011 Implement foundational higher-layer summary scaffolding for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T012 Refactor foundational helper naming and add or update reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create a Subscription Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver a typed Layer 1 `subscriptions.insert` wrapper that can create a subscription from a valid authorized writable request through the shared executor flow and return a stable normalized creation result

**Independent Test**: Submit a valid authorized `subscriptions.insert` request with `part` and `body.snippet.resourceId.channelId`, then confirm the wrapper executes through the shared executor and returns a normalized successful result containing the created subscription data and request context

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [P] [US1] Add failing happy-path wrapper tests for `subscriptions.insert` metadata, required `part` plus writable `body.snippet.resourceId.channelId` rules, and successful execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T014 [P] [US1] Add failing transport tests for `POST /subscriptions` request construction, request-body serialization, and successful payload normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T015 [P] [US1] Add failing integration tests for valid subscription creation through `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T016 [US1] Implement the valid creation path, required writable `snippet` enforcement, and successful authorized execution for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T017 [US1] Implement normalized successful creation payload handling for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T018 [US1] Implement a higher-layer `subscriptions.insert` summary method for successful outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T019 [US1] Add or update reStructuredText docstrings for the successful creation path in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T020 [US1] Refactor the successful creation path while keeping the User Story 1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Story 1 should now support independently testable successful subscription creation

---

## Phase 4: User Story 2 - Review Quota, OAuth, and Writable-Part Expectations Before Reuse (Priority: P2)

**Goal**: Make the `subscriptions.insert` wrapper reviewable enough that maintainers can see quota, OAuth-required access, required create inputs, and unsupported write-boundary guidance without reading implementation internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, research artifact, quickstart guidance, and higher-layer summary output to confirm quota cost `50`, OAuth-required access, required `part` plus target-channel input, and unsupported-request guidance are visible and consistent

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T021 [P] [US2] Add failing contract-artifact coverage for `subscriptions.insert` wrapper requirements in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`
- [X] T022 [P] [US2] Add failing review-surface metadata coverage for quota visibility, auth mode, required fields, and maintainer-facing writable notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T023 [P] [US2] Add failing higher-layer review-summary coverage for `subscriptions.insert` source metadata, required fields, writable part, and required nested target field in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T024 [US2] Implement maintainer-facing metadata notes, review-surface guidance, and required-field exposure for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T025 [US2] Implement higher-layer `subscriptions.insert` review-summary fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Align `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-auth-write-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md` with the implemented quota, auth, and writable-part review surfaces
- [X] T027 [US2] Add or update reStructuredText docstrings for quota, auth, and required-input reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T028 [US2] Refactor review-surface wording and summary-field naming while keeping the User Story 2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-wrapper-contract.md`

**Checkpoint**: User Story 2 should now make `subscriptions.insert` reviewable independently of implementation code

---

## Phase 5: User Story 3 - Reject Invalid, Duplicate, or Unauthorized Subscription Requests Clearly (Priority: P3)

**Goal**: Harden `subscriptions.insert` so invalid request shapes, unsupported writable parts, missing OAuth access, duplicate or ineligible targets, and upstream create failures remain clearly distinct for downstream callers

**Independent Test**: Submit requests with missing target-subscription details, unsupported writable parts, incompatible authorization, duplicate or ineligible targets, and upstream rejection profiles, then confirm the wrapper and normalized results keep those outcomes distinct from successful creation

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T029 [P] [US3] Add failing invalid-request unit coverage for missing target channel, unsupported writable parts, unsupported optional fields, and invalid `resourceId.kind` values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T030 [P] [US3] Add failing invalid-request, access-failure, duplicate-target, and upstream-create-failure transport coverage for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T031 [P] [US3] Add failing invalid, unauthorized, duplicate-target, and upstream-rejected integration coverage for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 3

- [X] T032 [US3] Implement deterministic validation for missing required input, unsupported writable parts, unsupported optional fields, and invalid target-kind values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T033 [US3] Implement normalized invalid-request, access-related failure, duplicate or ineligible target, and upstream create failure handling for `subscriptions.insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T034 [US3] Update higher-layer `subscriptions.insert` summary compatibility for invalid-request, access-failure, duplicate-target, and upstream-create-failure expectations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T035 [US3] Align `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md` with the final invalid-request and failure-boundary behavior
- [X] T036 [US3] Add or update reStructuredText docstrings for the failure-path creation logic in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T037 [US3] Refactor invalid, access-related, duplicate-target, and upstream-create-failure handling while keeping the User Story 3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md`

**Checkpoint**: All three user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation consistency, and whole-repository validation

- [X] T038 [P] Reconcile feature-level documentation and task references across `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/contracts/layer1-subscriptions-insert-auth-write-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md`
- [X] T039 [P] Review all touched Python modules for reStructuredText docstring completeness in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T040 Run the YT-142 targeted validation flow from `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py`
- [X] T041 Run the full repository test suite and resolve any failing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/`
- [X] T042 Run full lint validation for touched integration modules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP story
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses the wrapper surface introduced by User Story 1
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on the create surface introduced by User Story 1
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational completion and has no dependency on other stories
- **User Story 2 (P2)**: Depends on the `subscriptions.insert` wrapper and summary surface from User Story 1 but remains independently testable through review artifacts and summaries
- **User Story 3 (P3)**: Depends on the `subscriptions.insert` wrapper and transport surface from User Story 1 but remains independently testable through invalid-request and upstream-failure scenarios

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
- Within **US3**, `T029`, `T030`, and `T031` can run in parallel
- In the polish phase, `T038` and `T039` can run in parallel

### Story Completion Order

- **MVP order**: US1
- **Recommended incremental order**: US1 → US2 → US3
- **Parallelizable after Foundation**: US2 contract and review-surface Red tests can begin while US1 implementation is underway; US3 Red tests can begin once the shared creation seam exists

### Dependency Graph

- Phase 1 → Phase 2 → US1 → US2
- Phase 1 → Phase 2 → US1 → US3
- US2 and US3 → Phase 6

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "T013 Add failing happy-path wrapper tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T014 Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T015 Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "T021 Add failing contract-artifact coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_subscriptions_contract.py"
Task: "T022 Add failing review-surface metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T023 Add failing higher-layer review-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "T029 Add failing invalid-request unit coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T030 Add failing invalid-request, access-failure, duplicate-target, and upstream-create-failure transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T031 Add failing invalid, unauthorized, duplicate-target, and upstream-rejected integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the supported creation success path independently
5. Demo or hand off the MVP internal wrapper before expanding reviewability and failure hardening

### Incremental Delivery

1. Complete Setup + Foundational to establish the wrapper, export, transport, summary, and contract-test seam
2. Add User Story 1 to deliver the usable creation path
3. Add User Story 2 to make the creation contract reviewable for maintainers and higher layers
4. Add User Story 3 to harden invalid and unauthorized request handling
5. Finish with polish and full-suite validation

### Parallel Team Strategy

1. One developer completes Setup + Foundational
2. After Foundational is complete:
   - Developer A can implement User Story 1
   - Developer B can prepare User Story 2 Red tests
   - Developer C can prepare User Story 3 Red tests for invalid and upstream-failure paths
3. Merge stories in priority order, keeping each independently testable

---

## Notes

- `[P]` tasks touch different files or can be completed without waiting on another incomplete task in the same phase
- `[US1]`, `[US2]`, and `[US3]` map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/142-subscriptions-insert/spec.md`
- User Story 1 is the suggested MVP scope
- All tasks above follow the required checklist format with checkbox, task ID, optional labels, and exact file paths
