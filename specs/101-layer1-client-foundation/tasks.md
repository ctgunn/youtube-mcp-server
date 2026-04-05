# Tasks: YT-101 Layer 1 Shared Client Foundation

**Input**: Design documents from `/specs/101-layer1-client-foundation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are required in every phase. Completion requires a passing full repository test-suite run after the final code changes. All new or changed Python functions must include reStructuredText docstrings.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel if dependencies are already complete
- **[Story]**: Which user story this task belongs to
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the internal integration module and test file skeletons used by later phases.

- [X] T001 Create the Layer 1 integration package in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T002 [P] Create the shared unit test file scaffold in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T003 [P] Create the shared integration test file scaffold in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
- [X] T004 [P] Create the higher-layer consumer contract test file scaffold in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared internal contract and execution surfaces that block all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 Implement wrapper metadata types and validation rules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py
- [X] T006 [P] Implement auth mode policy types and credential-selection helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py
- [X] T007 [P] Implement normalized upstream failure types and error-normalization helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/errors.py
- [X] T008 [P] Implement retry and backoff policy helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/retry.py
- [X] T009 Implement the shared request executor and logging hook integration in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py
- [X] T010 Wire package exports for the shared Layer 1 foundation in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T011 Add or update reStructuredText docstrings for foundational integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py
- [X] T012 [P] Add or update reStructuredText docstrings for foundational integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py
- [X] T013 [P] Add or update reStructuredText docstrings for foundational integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/errors.py
- [X] T014 [P] Add or update reStructuredText docstrings for foundational integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/retry.py
- [X] T015 Add or update reStructuredText docstrings for foundational integration modules in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py

**Checkpoint**: Shared Layer 1 foundation types and executor exist for user story work.

---

## Phase 3: User Story 1 - Add Endpoint Wrappers Consistently (Priority: P1) 🎯 MVP

**Goal**: Let maintainers define a representative Layer 1 endpoint wrapper through one shared contract with consistent metadata, auth handling, retry behavior, logging hooks, and normalized failures.

**Independent Test**: Define a representative wrapper using the new contract and verify through unit and integration coverage that required metadata, auth mode selection, shared execution, and normalized failure behavior all work without custom per-wrapper infrastructure.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests first and confirm they fail before implementation**

- [X] T016 [P] [US1] Add Red metadata and validation tests for representative wrappers in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T017 [P] [US1] Add Red auth-mode and normalized-failure tests for representative wrappers in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T018 [P] [US1] Add Red shared-executor integration tests for representative wrappers in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 1

- [X] T019 [P] [US1] Implement the representative endpoint wrapper definition and typed result shape in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T020 [US1] Implement wrapper registration and binding to the shared request executor in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T021 [US1] Integrate shared execution observability with existing request logging patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/observability.py
- [X] T022 [US1] Add or update reStructuredText docstrings for wrapper implementation functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T023 [US1] Refactor wrapper metadata, executor, and observability integration while keeping US1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T024 [US1] Run the User Story 1 verification commands and fix any failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py

**Checkpoint**: User Story 1 should now support a representative wrapper that is independently testable.

---

## Phase 4: User Story 2 - Consume Typed Integration Methods in Higher Layers (Priority: P2)

**Goal**: Let a representative higher-layer workflow consume typed Layer 1 methods instead of building raw upstream request logic itself.

**Independent Test**: Wire one representative higher-layer consumer to a typed Layer 1 wrapper and verify through contract and integration coverage that the consumer avoids raw request-building and handles normalized failures consistently.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T025 [P] [US2] Add Red higher-layer consumer contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T026 [P] [US2] Add Red higher-layer consumer integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 2

- [X] T027 [P] [US2] Implement the representative higher-layer consumer seam in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T028 [US2] Connect the representative higher-layer consumer to typed wrapper methods and normalized failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T029 [US2] Add or update reStructuredText docstrings for consumer seam functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T030 [US2] Refactor higher-layer consumer composition while keeping US2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T031 [US2] Run the User Story 2 verification commands and fix any failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

**Checkpoint**: User Stories 1 and 2 should both work independently, with higher-layer code consuming typed Layer 1 methods.

---

## Phase 5: User Story 3 - Review Foundation Readiness Before Expanding Coverage (Priority: P3)

**Goal**: Give maintainers and reviewers enough contract and artifact clarity to confirm the Layer 1 foundation is ready for broader endpoint expansion.

**Independent Test**: Review the implementation and planning artifacts together and verify that metadata requirements, auth modes, retry behavior, logging hooks, lifecycle notes, and normalized failures are all documented and exercised by representative proof points.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T032 [P] [US3] Add Red documentation and artifact regression tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T033 [P] [US3] Add Red readiness integration assertions for representative foundation artifacts in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T034 [P] [US3] Update the wrapper contract documentation with final implementation-aligned details in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md
- [X] T035 [P] [US3] Update the consumer contract documentation with final implementation-aligned details in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-consumer-contract.md
- [X] T036 [P] [US3] Update the entity and lifecycle details for review readiness in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/data-model.md
- [X] T037 [US3] Update the implementation and verification guidance for reviewers in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/quickstart.md
- [X] T038 [US3] Refactor artifact wording and traceability so US3 readiness tests stay green in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/plan.md
- [X] T039 [US3] Run the User Story 3 verification commands and fix any failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

**Checkpoint**: All three user stories should now be independently functional and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, regression protection, and full-suite validation across the feature.

- [X] T040 [P] Add cross-story regression coverage for shared Layer 1 foundation behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T041 [P] Review and tighten package exports for the integration foundation in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T042 [P] Reconcile AGENTS guidance if implementation changes introduce new planning-relevant details in /Users/ctgunn/Projects/youtube-mcp-server/AGENTS.md
- [X] T043 Run the quickstart verification flow and update any stale commands in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/quickstart.md
- [X] T044 Run the full repository test suite and resolve any failing tests before completion in /Users/ctgunn/Projects/youtube-mcp-server/src
- [X] T045 Run lint validation and resolve any issues before completion in /Users/ctgunn/Projects/youtube-mcp-server

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup** has no dependencies and starts immediately.
- **Phase 2: Foundational** depends on Phase 1 and blocks all user story work.
- **Phase 3: US1** depends on Phase 2.
- **Phase 4: US2** depends on Phase 2 and on the representative wrapper from US1 being available for reuse.
- **Phase 5: US3** depends on the implementation outcomes of US1 and US2 so the artifacts reflect real behavior.
- **Phase 6: Polish** depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)** is the MVP and has no dependency on other user stories after foundational work is complete.
- **US2 (P2)** depends on the shared foundation and representative wrapper created in US1.
- **US3 (P3)** depends on the implemented foundation behavior from US1 and US2 so readiness artifacts describe actual behavior.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation begins.
- Implementation follows the smallest change set needed to satisfy the story.
- ReStructuredText docstrings must be updated before the story is complete.
- Refactor happens only after tests pass and must preserve behavior.
- Story-specific verification runs before moving on.
- Full repository validation is still required before the feature is complete.

### Parallel Opportunities

- Phase 1 scaffolding tasks `T002` through `T004` can run in parallel after `T001`.
- Foundational policy tasks `T006` through `T008` can run in parallel after `T005` starts the contract shape.
- Foundational docstring tasks `T012` through `T014` can run in parallel once their modules exist.
- US1 Red tasks `T016` through `T018` can run in parallel.
- US2 Red tasks `T025` and `T026` can run in parallel.
- US3 artifact update tasks `T034` through `T036` can run in parallel.
- Polish tasks `T040` through `T042` can run in parallel before the final validation tasks.

---

## Parallel Example: User Story 1

```bash
# Launch the Red tests for User Story 1 together:
Task: "Add Red metadata and validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add Red auth-mode and normalized-failure tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add Red shared-executor integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch the Red tests for User Story 2 together:
Task: "Add Red higher-layer consumer contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
Task: "Add Red higher-layer consumer integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 3

```bash
# Update the review artifacts for User Story 3 together:
Task: "Update the wrapper contract documentation in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-wrapper-contract.md"
Task: "Update the consumer contract documentation in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/contracts/layer1-consumer-contract.md"
Task: "Update the entity and lifecycle details in /Users/ctgunn/Projects/youtube-mcp-server/specs/101-layer1-client-foundation/data-model.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the representative wrapper flow independently.
5. Stop for review before expanding to US2 and US3 if desired.

### Incremental Delivery

1. Build the shared foundation once in Phase 2.
2. Deliver US1 as the maintainer-facing MVP.
3. Add US2 to prove higher-layer typed consumption.
4. Add US3 to lock in review readiness and artifact quality.
5. Finish with cross-cutting regression and full-suite validation.

### Parallel Team Strategy

1. One developer completes Phase 1 and coordinates Phase 2 contracts.
2. Another developer can prepare Red tests in parallel where marked `[P]`.
3. After US1 lands, a second developer can take US2 while a third prepares US3 artifact updates.
4. Rejoin for final regression and full-suite validation.

---

## Notes

- All tasks use the required checklist format with checkbox, task ID, optional `[P]`, required story label for user-story phases, and exact file paths.
- User stories remain independently testable, but US2 and US3 intentionally build on the representative proof points created earlier in the feature.
- The final completion gate is a passing `cd src && pytest` and `ruff check .`.
