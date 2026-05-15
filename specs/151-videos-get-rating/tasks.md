# Tasks: YT-151 Layer 1 Endpoint `videos.getRating`

**Input**: Design documents from `/specs/151-videos-get-rating/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks MUST include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Refresh feature-local execution context and confirm the intended implementation seams before code changes begin

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/quickstart.md` to confirm scope, Red-Green-Refactor order, and verification commands
- [X] T002 Review adjacent implementation seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T003 [P] Review current video-related test coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared seams and placeholder expectations that all `videos.getRating` user stories depend on before endpoint-specific work proceeds

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add failing baseline export and metadata assertions for `videos.getRating` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T005 [P] Add failing placeholder contract expectations for `videos.getRating` artifacts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`
- [X] T006 [P] Add failing placeholder consumer-summary expectations for `videos.getRating` review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T007 Extend shared integration exports for the planned `videos.getRating` wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in priority order

---

## Phase 3: User Story 1 - Retrieve Viewer Rating State Through a Reusable Layer 1 Contract (Priority: P1) 🎯 MVP

**Goal**: Add the internal OAuth-only `videos.getRating` wrapper so higher-layer workflows can retrieve current viewer rating state for one or more videos through one deterministic request contract

**Independent Test**: Submit a valid authorized request with `id` naming one or more videos and confirm the wrapper returns normalized per-video rating-state results, including at least one unrated success case

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add failing unit tests for `videos.getRating` metadata, required `id` validation, bounded one-or-more identifier handling, and OAuth-only enforcement in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T009 [P] [US1] Add failing transport tests for `GET /videos/getRating` request construction and normalized per-video rating lookup payload shaping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T010 [P] [US1] Add failing integration tests for successful authorized rated and unrated lookup flows through the shared executor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [ ] T011 [US1] Implement the `VideosGetRatingWrapper` class and `build_videos_get_rating_wrapper()` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T012 [US1] Implement `_require_videos_get_rating_arguments()` with deterministic `id` validation and bounded one-or-more identifier rules in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T013 [US1] Add `videos.getRating` transport request handling and normalized per-video result shaping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [ ] T014 [US1] Add or update reStructuredText docstrings for `videos.getRating` wrapper and transport functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [ ] T015 [US1] Refactor `videos.getRating` wrapper and transport handling for naming clarity and minimal shared-seam reuse in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` while keeping User Story 1 tests green

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Review Quota, OAuth, and Rating-State Semantics Before Reuse (Priority: P2)

**Goal**: Make maintainer-facing review surfaces fully describe the `videos.getRating` contract, including quota, OAuth requirement, supported identifier boundary, and returned rating-state semantics

**Independent Test**: Review the wrapper metadata, higher-layer summary output, and feature-local contracts to confirm maintainers can identify quota cost `1`, OAuth-only access, supported identifier guidance, and returned rating states without reading transport code

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T016 [P] [US2] Add failing contract tests for `videos.getRating` wrapper and auth-rating artifacts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`
- [X] T017 [P] [US2] Add failing metadata review-surface assertions for `videos.getRating` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T018 [P] [US2] Add failing consumer-summary tests for rating-lookup reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T019 [US2] Update maintainer-facing `videos.getRating` metadata notes and review-surface details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T020 [US2] Implement a higher-layer `get_video_rating_summary()` consumer path exposing identifier, returned state, quota, and auth details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T021 [US2] Finalize the wrapper identity contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-wrapper-contract.md`
- [X] T022 [US2] Finalize the auth and rating-state contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-auth-rating-contract.md`
- [X] T023 [US2] Add or update reStructuredText docstrings for changed review-surface and consumer functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T024 [US2] Refactor rating-lookup review wording for consistency across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-wrapper-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-auth-rating-contract.md` while keeping User Story 2 tests green

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Reject Invalid or Under-Authorized Rating-Lookup Requests Clearly (Priority: P3)

**Goal**: Preserve explicit failure boundaries so callers can distinguish malformed requests, unsupported identifier shapes or modifiers, missing OAuth access, and upstream lookup failures from successful rated or unrated results

**Independent Test**: Submit requests missing `id`, using unsupported modifiers or unsupported identifier forms, or lacking OAuth-backed access and confirm each path fails with a normalized outcome distinct from successful rated, successful unrated, and upstream-failure outcomes

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T025 [P] [US3] Add failing unit tests for unsupported identifier forms, unexpected fields, and missing required input in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T026 [P] [US3] Add failing transport tests for normalized upstream `invalid_request`, `auth`, and lookup-failure outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T027 [P] [US3] Add failing integration tests for unauthorized and upstream-failed `videos.getRating` execution paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing contract and consumer assertions for failure-boundary guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 3

- [X] T029 [US3] Tighten `videos.getRating` validation and OAuth failure handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T030 [US3] Implement normalized upstream lookup-failure shaping and rated-versus-unrated result separation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T031 [US3] Update higher-layer rating-lookup summaries to preserve failure-boundary context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T032 [US3] Update the failure-focused entities and transitions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/data-model.md`
- [X] T033 [US3] Add or update reStructuredText docstrings for changed validation, transport, and consumer functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T034 [US3] Refactor failure-category wording and duplicate validation guidance across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/quickstart.md` while keeping User Story 3 tests green

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T035 [P] Refresh feature-local implementation guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/quickstart.md` to match the final code and verification flow
- [X] T036 [P] Add any final cross-story regression assertions for `videos.getRating` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`
- [X] T037 Review reStructuredText docstrings for all changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T038 Run quickstart validation using `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/quickstart.md`
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
- **User Story 2 (P2)**: Starts after User Story 1 establishes the wrapper and transport seams because review surfaces depend on the implemented `videos.getRating` metadata and lookup result
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
- T005 and T006 can run in parallel during the foundational phase because they touch separate contract test files
- T008-T010 can run in parallel for User Story 1 because they target separate test files
- T016-T018 can run in parallel for User Story 2 because they target separate contract test files
- T021 and T022 can run in parallel once User Story 2 behavior is defined because they touch separate contract files
- T025-T028 can run in parallel for User Story 3 because they target separate test files
- T035 and T036 can run in parallel during polish because they touch different artifact types

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 Red tests together:
Task: "Add failing unit tests for `videos.getRating` metadata, required `id` validation, bounded one-or-more identifier handling, and OAuth-only enforcement in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing transport tests for `GET /videos/getRating` request construction and normalized per-video rating lookup payload shaping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration tests for successful authorized rated and unrated lookup flows through the shared executor in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
# Launch all User Story 2 Red tests together:
Task: "Add failing contract tests for `videos.getRating` wrapper and auth-rating artifacts in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py"
Task: "Add failing metadata review-surface assertions for `videos.getRating` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "Add failing consumer-summary tests for rating-lookup reviewability in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all User Story 3 Red tests together:
Task: "Add failing unit tests for unsupported identifier forms, unexpected fields, and missing required input in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "Add failing transport tests for normalized upstream `invalid_request`, `auth`, and lookup-failure outcomes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add failing integration tests for unauthorized and upstream-failed `videos.getRating` execution paths in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "Add failing contract and consumer assertions for failure-boundary guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Run the User Story 1 test set independently
5. Demo the internal `videos.getRating` wrapper before expanding review surfaces or failure nuance

### Incremental Delivery

1. Complete Setup + Foundational → base export and test seams ready
2. Add User Story 1 → validate the core wrapper lookup path
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
- Never treat targeted test runs as final completion evidence; the full repository suite must pass
- Keep the feature internal to Layer 1 and do not add a public MCP tool in this slice
