# Tasks: YT-119 Layer 1 Endpoint `comments.setModerationStatus`

**Input**: Design documents from `/specs/119-comments-set-moderation-status/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths below follow the single-project structure from `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/plan.md`

## Phase 1: Setup (Shared Context)

**Purpose**: Confirm scope, source touchpoints, and feature-local references before test-first implementation starts

- [X] T001 Review the planned implementation and validation flow in /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/plan.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/quickstart.md
- [X] T002 Review the existing comment wrapper patterns and neighboring write endpoints in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T003 [P] Review the current Layer 1 comments coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared endpoint registration and transport seams that all moderation stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing foundational wrapper registration coverage for `comments.setModerationStatus` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T005 [P] Add failing foundational transport coverage for the `POST /comments/setModerationStatus` query-only request path in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T006 Implement `CommentsSetModerationStatusWrapper`, the builder, validation helpers, and the package export in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T007 Implement foundational transport recognition and normalized moderation acknowledgment handling for `comments.setModerationStatus` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T008 Refactor foundational moderation helper naming and add or update reStructuredText docstrings in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Moderate Comments Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Deliver the authorized success path for moderating one or more comments through the internal Layer 1 wrapper

**Independent Test**: Invoke `comments.setModerationStatus` with valid `id`, `moderationStatus`, optional `banAuthor` when allowed, and OAuth-backed access, then confirm the wrapper returns a normalized successful moderation acknowledgment without requiring a request body

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add failing successful wrapper-call integration coverage for authorized moderation requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py
- [X] T010 [P] [US1] Add failing successful higher-layer moderation summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py
- [X] T011 [P] [US1] Add failing successful request-construction and acknowledgment coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py

### Implementation for User Story 1

- [X] T012 [US1] Implement the valid moderation request path, supported state acceptance, and OAuth enforcement for successful calls in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T013 [US1] Implement normalized successful moderation acknowledgment payload handling, including empty upstream success bodies, in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T014 [US1] Implement a higher-layer moderation summary method for successful outcomes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T015 [US1] Add or update reStructuredText docstrings for the successful moderation path in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T016 [US1] Refactor the successful moderation path while keeping the User Story 1 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py

**Checkpoint**: User Story 1 should now support independently testable successful moderation requests

---

## Phase 4: User Story 2 - Understand Moderation-State and OAuth Boundaries Before Reuse (Priority: P2)

**Goal**: Make the moderation wrapper reviewable enough that maintainers can see quota, OAuth, supported states, and optional flag boundaries without reading implementation internals

**Independent Test**: Review the wrapper metadata, feature-local contracts, and higher-layer summary output to confirm quota cost `50`, OAuth-required access, supported states `published`/`heldForReview`/`rejected`, and `banAuthor` compatibility rules are visible and consistent

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T017 [P] [US2] Add failing contract-artifact coverage for moderation reviewability in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py
- [X] T018 [P] [US2] Add failing review-surface metadata coverage for moderation notes and optional fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py
- [X] T019 [P] [US2] Add failing higher-layer review-summary coverage for moderation source metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py

### Implementation for User Story 2

- [X] T020 [US2] Update maintainer-facing moderation notes, optional field declarations, and review-surface metadata for `comments.setModerationStatus` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T021 [US2] Update the feature-local moderation contracts and quickstart references in /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-wrapper-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-auth-write-contract.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-auth-moderation-contract.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/quickstart.md
- [X] T022 [US2] Update higher-layer moderation summary fields so review consumers can see source operation, auth mode, quota, supported status, and optional flag guidance in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T023 [US2] Add or update reStructuredText docstrings for reviewability-oriented moderation surfaces in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T024 [US2] Refactor moderation review-surface wording and keep the User Story 2 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/layer1-comments-set-moderation-status-auth-write-contract.md

**Checkpoint**: User Story 2 should now be independently testable through review surfaces and contract artifacts

---

## Phase 5: User Story 3 - Fail Clearly for Invalid or Ineligible Moderation Requests (Priority: P3)

**Goal**: Deliver deterministic validation and distinct normalized failures for malformed, unsupported, or unauthorized moderation attempts

**Independent Test**: Submit requests with missing `id`, missing `moderationStatus`, duplicate targets, unsupported moderation states, incompatible `banAuthor` combinations, API-key auth, and upstream moderation denials, then confirm the wrapper returns distinct normalized failures for each invalid category

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T025 [P] [US3] Add failing invalid-request and auth-mismatch unit coverage for moderation validation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py
- [X] T026 [P] [US3] Add failing unsupported-transition and upstream-failure transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
- [X] T027 [P] [US3] Add failing invalid and upstream-rejected moderation integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py

### Implementation for User Story 3

- [X] T028 [US3] Implement deterministic validation for missing identifiers, missing moderation status, duplicate targets, supported states, and `banAuthor` compatibility in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py
- [X] T029 [US3] Implement normalized upstream error categorization for moderation denials, invalid moderation requests, and unsupported moderation combinations in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py
- [X] T030 [US3] Update higher-layer moderation summary compatibility for failure-path expectations in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T031 [US3] Add or update reStructuredText docstrings for the failure-path moderation logic in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py
- [X] T032 [US3] Refactor invalid and unauthorized moderation handling while keeping the User Story 3 tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py

**Checkpoint**: All three user stories should now be independently functional and testable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, documentation consistency, and whole-repository validation

- [X] T033 [P] Reconcile feature-level documentation and task references across /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/plan.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/research.md, /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/data-model.md, and /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/quickstart.md
- [X] T034 [P] Review all touched Python modules for reStructuredText docstring completeness in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py, /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py, and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py
- [X] T035 Validate the implementation workflow and commands against /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/quickstart.md
- [X] T036 Run the full repository test suite and resolve any failing tests using /Users/ctgunn/Projects/youtube-mcp-server/tests/ and /Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/quickstart.md as the completion gate

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP story
- **User Story 2 (Phase 4)**: Depends on Foundational completion and reuses the User Story 1 wrapper surface
- **User Story 3 (Phase 5)**: Depends on Foundational completion and builds on the moderation surface introduced by User Story 1
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational completion - no dependency on other user stories
- **User Story 2 (P2)**: Depends on the moderation wrapper surface from User Story 1 but remains independently testable through review artifacts and summaries
- **User Story 3 (P3)**: Depends on the moderation wrapper surface from User Story 1 but remains independently testable through invalid and failure-path scenarios

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Wrapper metadata and validation before consumer summary updates
- Transport normalization before success or failure summaries that depend on it
- Core implementation before integration validation (Green)
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run full affected test suites (Refactor)
- Before marking the feature complete, run the full repository test suite and fix any failures

### Parallel Opportunities

- `T003` can run in parallel with `T001` and `T002`
- `T005` can run in parallel with `T004`
- Within **US1**, `T009`, `T010`, and `T011` can run in parallel
- Within **US2**, `T017`, `T018`, and `T019` can run in parallel
- Within **US3**, `T025`, `T026`, and `T027` can run in parallel
- In the polish phase, `T033` and `T034` can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "Add failing successful wrapper-call integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "Add failing successful higher-layer moderation summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
Task: "Add failing successful request-construction and acknowledgment coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "Add failing contract-artifact coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_comments_contract.py"
Task: "Add failing review-surface metadata coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing higher-layer review-summary coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing invalid-request and auth-mismatch unit coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing unsupported-transition and upstream-failure transport coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing invalid and upstream-rejected moderation integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate the authorized moderation success path independently
5. Demo or hand off the MVP internal wrapper before expanding reviewability and failure handling

### Incremental Delivery

1. Complete Setup + Foundational to establish the wrapper, export, and transport seam
2. Add User Story 1 to deliver the usable moderation path
3. Add User Story 2 to make the moderation contract reviewable for maintainers and higher layers
4. Add User Story 3 to harden invalid and unauthorized request handling
5. Finish with polish and full-suite validation

### Parallel Team Strategy

1. One developer completes Setup + Foundational
2. After Foundational is complete:
   - Developer A can implement User Story 1
   - Developer B can prepare User Story 2 Red tests and contract assertions
   - Developer C can prepare User Story 3 Red tests for invalid and failure paths
3. Merge stories in priority order, keeping each independently testable

---

## Notes

- [P] tasks touch different files or can be completed without waiting on another incomplete task in the same phase
- [US1], [US2], and [US3] map directly to the user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/spec.md`
- User Story 1 is the suggested MVP scope
- All tasks above follow the required checklist format with checkbox, task ID, optional labels, and exact file paths
