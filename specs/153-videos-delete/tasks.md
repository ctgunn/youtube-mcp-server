# Tasks: YT-153 Layer 1 Endpoint `videos.delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python implementation tasks include explicit reStructuredText docstring tasks for every new or modified function.

**Organization**: Tasks are grouped by user story so `videos.delete` can be implemented as an internal Layer 1 wrapper MVP first, then expanded with reviewability and failure-boundary hardening.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files or depends only on completed setup/foundation tasks
- **[Story]**: Maps to the user story from `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/spec.md`
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing Layer 1 video delete wrapper seams and prepare implementation without changing behavior.

- [X] T001 Review adjacent video wrapper implementation patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T002 [P] Review YouTube transport delete request and no-content acknowledgement patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T003 [P] Review higher-layer delete consumer summary patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T004 [P] Review existing Layer 1 video and delete test organization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared test fixtures and import scaffolding needed by all user-story tasks.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [ ] T005 Add shared representative `videos.delete` argument fixtures for valid required-only, blank-id, body-present, unsupported-field, and optional delegation cases in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [ ] T006 [P] Add shared YouTube transport response helpers for 204 no-content, forbidden, video-not-found, and upstream unavailable cases in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [ ] T007 [P] Add planned import placeholders for `build_videos_delete_wrapper` expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`

**Checkpoint**: Shared test setup exists, and user story work can proceed in priority order or in parallel where marked.

---

## Phase 3: User Story 1 - Delete a Video Through a Reusable Layer 1 Contract (Priority: P1) MVP

**Goal**: A platform developer can submit an authorized `videos.delete` request through a typed internal Layer 1 wrapper and receive a normalized successful deletion acknowledgement.

**Independent Test**: Submit a valid authorized request with `id`; verify the wrapper executes through the shared executor, sends `DELETE /youtube/v3/videos` without a body, and returns a normalized acknowledgement tied to the target video.

### Tests for User Story 1 (REQUIRED)

> Write these tests FIRST and verify they fail before implementation.

- [ ] T008 [P] [US1] Add failing unit tests for `videos.delete` wrapper metadata, export visibility, OAuth-only call behavior, required `id`, and successful executor call shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [ ] T009 [P] [US1] Add failing transport tests for authorized `DELETE /youtube/v3/videos` request construction, `id` query parameter encoding, bearer authorization header use, no request-body transmission, and 204 no-content acknowledgement normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [ ] T010 [P] [US1] Add failing integration test for successful `videos.delete` execution through the shared executor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [ ] T011 [US1] Implement `VideosDeleteWrapper` with OAuth-required call validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T012 [US1] Implement `build_videos_delete_wrapper` metadata with operation key `videos.delete`, path `/youtube/v3/videos`, method `DELETE`, quota cost `50`, and required `id` request shape in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T013 [US1] Export `build_videos_delete_wrapper` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [ ] T014 [US1] Add `videos.delete` request handling and no-content acknowledgement normalization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [ ] T015 [US1] Add or update reStructuredText docstrings for every new or modified `videos.delete` wrapper and transport function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [ ] T016 [US1] Run targeted US1 validation with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [ ] T017 [US1] Refactor US1 wrapper and transport code for naming clarity while keeping targeted tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: User Story 1 is independently functional as the MVP internal wrapper path.

---

## Phase 4: User Story 2 - Review Quota, OAuth, and Destructive-Action Semantics Before Reuse (Priority: P2)

**Goal**: A maintainer can review wrapper metadata, contracts, and higher-layer summaries to understand quota cost, OAuth requirement, required target identifier, no-body behavior, destructive-action semantics, and successful acknowledgement behavior.

**Independent Test**: Review the wrapper surface and generated summary for `videos.delete`; verify quota `50`, OAuth-required access, required `id`, no-body delete behavior, acknowledgement semantics, and `onBehalfOfContentOwner` boundary guidance are visible in under 1 minute.

### Tests for User Story 2 (REQUIRED)

> Write these tests FIRST and verify they fail before implementation.

- [ ] T018 [P] [US2] Add failing contract tests for `videos.delete` wrapper review surface identity, quota cost, OAuth mode, required `id`, no-body guidance, acknowledgement wording, and partner delegation boundary notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`
- [ ] T019 [P] [US2] Add failing metadata contract tests for `videos.delete` maintainer-facing notes and quota/auth/destructive-action visibility in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [ ] T020 [P] [US2] Add failing consumer contract tests for a higher-layer `videos.delete` summary that preserves target video context, source operation, auth mode, quota cost, required fields, and credential-safe delete guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [ ] T021 [US2] Enrich `videos.delete` metadata notes and request-shape review text for quota, OAuth, required `id`, no-body behavior, acknowledgement semantics, and partner-only delegation boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T022 [US2] Implement `delete_video_summary` higher-layer summary method for `videos.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [ ] T023 [US2] Ensure the higher-layer delete summary omits OAuth tokens, credentials, target-owner identity, and delegated-owner credentials in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [ ] T024 [US2] Add or update reStructuredText docstrings for every new or modified metadata and consumer-summary function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [ ] T025 [US2] Run targeted US2 validation with `python3 -m pytest tests/contract/test_layer1_videos_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [ ] T026 [US2] Refactor US2 metadata and consumer-summary wording to remove duplicated delete-boundary guidance while keeping targeted tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Story 2 is independently reviewable through metadata, contracts, and consumer summaries.

---

## Phase 5: User Story 3 - Reject Invalid or Under-Authorized Delete Requests Clearly (Priority: P3)

**Goal**: A downstream tool author can distinguish missing or malformed identifiers, unsupported request bodies or modifiers, missing OAuth access, upstream forbidden failures, video-not-found failures, upstream outages, and successful acknowledgements.

**Independent Test**: Submit malformed, unsupported, unauthorized, upstream-refused, not-found, and valid `videos.delete` requests; verify each outcome remains distinct and actionable.

### Tests for User Story 3 (REQUIRED)

> Write these tests FIRST and verify they fail before implementation.

- [ ] T027 [P] [US3] Add failing unit tests for missing `id`, blank `id`, non-string `id`, body-present requests, unsupported top-level fields, unsupported partner-only delegation when not supported, and missing OAuth access in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [ ] T028 [P] [US3] Add failing transport tests for upstream forbidden, video-not-found, and upstream unavailable normalization for `videos.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [ ] T029 [P] [US3] Add failing integration tests that separate local validation failures, access failures, upstream refusals, not-found failures, and successful acknowledgements for `videos.delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [ ] T030 [P] [US3] Add failing contract tests for auth-delete boundary wording and failure-boundary reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

### Implementation for User Story 3

- [ ] T031 [US3] Implement deterministic `videos.delete` request validation for required `id`, blank or non-string `id`, unsupported request bodies, unsupported top-level fields, and unsupported partner-only delegation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T032 [US3] Implement OAuth-only error behavior for `videos.delete` before execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T033 [US3] Extend `videos.delete` upstream error-category normalization for forbidden, video-not-found, and upstream unavailable cases in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [ ] T034 [US3] Verify unsupported request-body and partner-only `onBehalfOfContentOwner` behavior is rejected or clearly flagged by the wrapper contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [ ] T035 [US3] Add or update reStructuredText docstrings for every new or modified validation and failure-normalization function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [ ] T036 [US3] Run targeted US3 validation with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_videos_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [ ] T037 [US3] Refactor US3 validation and error-boundary code while keeping targeted tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation consistency, and regression cleanup across all stories.

- [ ] T038 [P] Reconcile implementation behavior with `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/contracts/layer1-videos-delete-wrapper-contract.md`
- [ ] T039 [P] Reconcile implementation behavior with `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/contracts/layer1-videos-delete-auth-delete-contract.md`
- [ ] T040 [P] Update quickstart review readiness notes if implementation discovers naming changes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/quickstart.md`
- [ ] T041 [P] Review all changed Python functions for complete reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [ ] T042 Run targeted Layer 1 regression suite with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_videos_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [ ] T043 Run full repository test suite with `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [ ] T044 Run lint validation with `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks user story work
- **User Stories (Phase 3+)**: Depend on Foundational completion
- **Polish (Phase 6)**: Depends on all selected user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational; no dependency on US2 or US3; MVP scope
- **User Story 2 (P2)**: Starts after Foundational; can run in parallel with US1 for tests, but implementation benefits from US1 metadata and wrapper builder
- **User Story 3 (P3)**: Starts after Foundational; can run in parallel for tests, but implementation benefits from US1 wrapper and US2 documented boundaries

### Within Each User Story

- Red tests must be written and confirmed failing before Green implementation
- Wrapper metadata and validation must precede transport and consumer behavior that depends on it
- Core implementation must pass targeted tests before refactor tasks
- reStructuredText docstrings must be added or updated before story completion
- Refactor tasks must preserve behavior and keep targeted tests green
- Full repository tests and Ruff validation must pass in the final phase

### Dependency Graph

```text
Phase 1 Setup
  -> Phase 2 Foundational
    -> Phase 3 US1 MVP
      -> Phase 4 US2 Reviewability
      -> Phase 5 US3 Failure Boundaries
        -> Phase 6 Polish and Full Validation
```

US2 and US3 test-writing tasks may start after Phase 2 if a team wants parallel Red coverage, but their Green implementation should coordinate with the US1 wrapper builder and metadata shape.

---

## Parallel Execution Examples

### User Story 1

```bash
# Parallel Red tasks after Phase 2:
Task: "T008 [US1] Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T009 [US1] Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T010 [US1] Add failing integration test in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

### User Story 2

```bash
# Parallel Red tasks after Phase 2:
Task: "T018 [US2] Add failing wrapper contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py"
Task: "T019 [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T020 [US2] Add failing consumer contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

### User Story 3

```bash
# Parallel Red tasks after Phase 2:
Task: "T027 [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T028 [US3] Add failing upstream error normalization tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T029 [US3] Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T030 [US3] Add failing boundary contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate US1 independently with targeted unit, transport, and integration tests
5. Continue to US2 and US3 only after the internal wrapper can submit and acknowledge a valid delete request

### Incremental Delivery

1. Setup + Foundational: shared fixtures and planned imports are ready
2. US1: add the internal wrapper and successful acknowledgement path
3. US2: add review surfaces and higher-layer summary details
4. US3: harden invalid, unauthorized, forbidden, not-found, and upstream failure boundaries
5. Polish: reconcile contracts, run targeted regression, full pytest, and Ruff

### Parallel Team Strategy

1. One developer prepares shared test fixtures in Phase 2
2. Multiple developers write Red tests for US1, US2, and US3 in parallel
3. Implementation proceeds in priority order to reduce merge conflicts in shared integration modules
4. Final validation is serialized through targeted regression, full pytest, and Ruff

---

## Notes

- [P] tasks touch different files or can run before shared implementation exists
- [US1], [US2], and [US3] labels map directly to prioritized user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/spec.md`
- YT-153 remains internal to Layer 1 and must not add a public `videos_delete` MCP tool
- Every Python implementation task must preserve or add reStructuredText docstrings before the story is marked complete
- The feature is not complete until `python3 -m pytest` and `python3 -m ruff check .` pass from `/Users/ctgunn/Projects/youtube-mcp-server`
