# Tasks: YT-150 Layer 1 Endpoint `videos.rate`

**Input**: Design documents from `/specs/150-videos-rate/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Refresh feature-local execution context before code changes begin

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/quickstart.md` to confirm scope, Red-Green-Refactor order, and verification commands
- [X] T002 Review existing adjacent implementation seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Review current video-related test coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared seams that all user stories depend on before endpoint-specific work proceeds

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing export and metadata baseline assertions for `videos.rate` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T005 [P] Add failing placeholder contract expectations for `videos.rate` artifacts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`
- [X] T006 Extend shared integration exports for the planned `videos.rate` wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T007 Refactor foundational naming and feature-local references for `videos.rate` across `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/data-model.md` while keeping prerequisite tests failing only for missing implementation

**Checkpoint**: Foundation ready - user story implementation can now begin in priority order

---

## Phase 3: User Story 1 - Apply a Video Rating Through a Reusable Internal Contract (Priority: P1) 🎯 MVP

**Goal**: Add the internal OAuth-only `videos.rate` wrapper so higher-layer workflows can like, dislike, or clear a video rating through one deterministic request contract

**Independent Test**: Submit a valid authorized request with `id` plus `rating=like`, `rating=dislike`, or `rating=none` and confirm the wrapper returns a normalized successful acknowledgement that preserves the video identity and requested action

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add failing unit tests for `videos.rate` metadata, supported `id` plus `rating` validation, and OAuth-only enforcement in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T009 [P] [US1] Add failing transport tests for `POST /videos/rate` request construction and acknowledgement payload shaping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T010 [P] [US1] Add failing integration tests for successful authorized like/dislike/clear flows through the shared executor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement the `VideosRateWrapper` class and `build_videos_rate_wrapper()` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T012 [US1] Implement `_require_videos_rate_arguments()` with deterministic `id` plus supported `rating` validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T013 [US1] Add `videos.rate` transport request and normalized acknowledgement shaping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T014 [US1] Add or update reStructuredText docstrings for `videos.rate` wrapper and transport functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T015 [US1] Refactor `videos.rate` wrapper and transport handling for naming clarity and minimal shared-seam reuse in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` while keeping User Story 1 tests green

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Review Rating Semantics, Quota, and Access Rules Before Reuse (Priority: P2)

**Goal**: Make maintainer-facing review surfaces fully describe the `videos.rate` contract, including quota, OAuth requirement, supported actions, and unsupported-input boundaries

**Independent Test**: Review the wrapper metadata, higher-layer summary output, and feature-local contracts to confirm maintainers can identify quota cost `50`, OAuth-only access, and the supported `like` / `dislike` / `none` action set without reading transport code

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add failing contract tests for `videos.rate` wrapper and auth-rating artifacts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`
- [X] T017 [P] [US2] Add failing metadata review-surface assertions for `videos.rate` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T018 [P] [US2] Add failing consumer-summary tests for rating reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T019 [US2] Update maintainer-facing `videos.rate` metadata notes and review-surface details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T020 [US2] Implement a higher-layer `rate_video_summary()` consumer path exposing identifier, requested action, quota, and auth details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T021 [US2] Finalize the wrapper identity contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-wrapper-contract.md`
- [X] T022 [US2] Finalize the auth and rating-boundary contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-auth-rating-contract.md`
- [X] T023 [US2] Add or update reStructuredText docstrings for changed review-surface and consumer functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T024 [US2] Refactor rating review wording for consistency across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-wrapper-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-auth-rating-contract.md` while keeping User Story 2 tests green

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Reject Unsupported or Unauthorized Rating Requests Clearly (Priority: P3)

**Goal**: Preserve explicit failure boundaries so callers can distinguish malformed requests, unsupported rating values, missing OAuth access, and upstream refusals

**Independent Test**: Submit requests missing `id`, missing `rating`, using unsupported rating values, or lacking OAuth-backed access and confirm each path fails with a normalized outcome distinct from successful acknowledgements and upstream refusal outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T025 [P] [US3] Add failing unit tests for unsupported rating values, unexpected fields, and missing required inputs in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T026 [P] [US3] Add failing transport tests for normalized upstream `invalid_request`, `auth`, and rating-rejection outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T027 [P] [US3] Add failing integration tests for unauthorized and upstream-refused `videos.rate` execution paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing contract and consumer assertions for failure-boundary guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 3

- [X] T029 [US3] Tighten `videos.rate` validation and OAuth failure handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T030 [US3] Implement normalized upstream rating-failure shaping and acknowledgement/failure separation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T031 [US3] Update higher-layer rating summaries to preserve failure-boundary context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T032 [US3] Update the failure-focused entities and transitions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/data-model.md`
- [X] T033 [US3] Add or update reStructuredText docstrings for changed validation, transport, and consumer functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T034 [US3] Refactor failure-category wording and duplicate validation guidance across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/quickstart.md` while keeping User Story 3 tests green

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T035 [P] Refresh feature-local implementation guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/quickstart.md` to match the final code and verification flow
- [X] T036 [P] Add any final cross-story regression assertions for `videos.rate` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`
- [X] T037 Review reStructuredText docstrings for all changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T038 Run quickstart validation using `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/quickstart.md`
- [X] T039 Run `python3 -m pytest` and resolve any failing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T040 Run `python3 -m ruff check .` and resolve any remaining lint issues in `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phases 3-5)**: Depend on Foundational phase completion
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational and defines the MVP wrapper behavior
- **User Story 2 (P2)**: Starts after User Story 1 establishes the wrapper and transport seams because review surfaces depend on the implemented `videos.rate` metadata and acknowledgement result
- **User Story 3 (P3)**: Starts after User Story 1 and can overlap with the later half of User Story 2 once the base wrapper exists, but it should finish after review-surface wording stabilizes

### Within Each User Story

- Tests MUST be written and FAIL before implementation (Red)
- Wrapper and validation code before transport/consumer expansion
- Core implementation before docstring completion and refactor (Green)
- Update reStructuredText docstrings for every new or changed Python function before story completion
- Refactor only after tests pass; re-run full affected test suites (Refactor)
- Before marking the feature complete, run the full repository test suite and fix any failures

### Parallel Opportunities

- T003 and other tasks marked `[P]` can run in parallel during setup and polish
- T008-T010 can run in parallel for User Story 1 because they target separate test files
- T016-T018 can run in parallel for User Story 2 because they target separate contract test files
- T025-T028 can run in parallel for User Story 3 because they target separate test files
- T021 and T022 can run in parallel once User Story 2 behavior is defined because they touch separate contract files
- T035 and T036 can run in parallel during polish because they touch different artifact types

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "Add failing unit tests for `videos.rate` metadata, supported `id` plus `rating` validation, and OAuth-only enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing transport tests for `POST /videos/rate` request construction and acknowledgement payload shaping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration tests for successful authorized like/dislike/clear flows through the shared executor in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "Add failing contract tests for `videos.rate` wrapper and auth-rating artifacts in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py"
Task: "Add failing metadata review-surface assertions for `videos.rate` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing consumer-summary tests for rating reviewability in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing unit tests for unsupported rating values, unexpected fields, and missing required inputs in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing transport tests for normalized upstream `invalid_request`, `auth`, and rating-rejection outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration tests for unauthorized and upstream-refused `videos.rate` execution paths in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "Add failing contract and consumer assertions for failure-boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the User Story 1 test set independently
5. Demo the internal `videos.rate` wrapper before expanding review surfaces or failure nuance

### Incremental Delivery

1. Complete Setup + Foundational → base export and test seams ready
2. Add User Story 1 → validate the core wrapper mutation path
3. Add User Story 2 → validate maintainer-facing reviewability
4. Add User Story 3 → validate failure-boundary clarity
5. Finish with Polish → run quickstart checks, full test suite, and lint

### Parallel Team Strategy

With multiple developers:

1. One developer completes Setup + Foundational
2. After Foundation:
   - Developer A: User Story 1 wrapper and transport flow
   - Developer B: User Story 2 contract and consumer review surfaces once User Story 1 seams land
   - Developer C: User Story 3 failure-path tests and validation updates once User Story 1 seams land

---

## Notes

- `[P]` tasks = different files, no dependencies
- `[US1]`, `[US2]`, and `[US3]` labels map tasks directly to spec user stories
- Each user story remains independently testable
- Red tasks should fail before Green implementation begins
- Refactor tasks must preserve behavior and keep tests passing
