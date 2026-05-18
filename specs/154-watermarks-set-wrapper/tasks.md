# Tasks: YT-154 Layer 1 Endpoint `watermarks.set`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python implementation tasks include explicit reStructuredText docstring tasks for every new or modified function.

**Organization**: Tasks are grouped by user story so `watermarks.set` can be implemented as an internal Layer 1 wrapper MVP first, then expanded with reviewability and failure-boundary hardening.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files or depends only on completed setup/foundation tasks
- **[Story]**: Maps to the user story from `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/spec.md`
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing Layer 1 upload wrapper seams and prepare implementation without changing behavior.

- [X] T001 Review adjacent upload wrapper implementation patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T002 [P] Review YouTube media-upload request and no-content acknowledgement patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T003 [P] Review higher-layer upload consumer summary patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T004 [P] Review existing Layer 1 upload and mutation test organization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_thumbnails_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T005 [P] Review YT-154 contract and quickstart expectations in `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/layer1-watermarks-set-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/layer1-watermarks-set-auth-upload-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared test fixtures and import scaffolding needed by all user-story tasks.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [X] T006 Add shared representative `watermarks.set` argument fixtures for valid, missing-channel, missing-body, missing-media, unsupported-media, oversized-media, and optional delegation cases in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T007 [P] Add shared YouTube transport response helpers for 204 no-content, unsupported image format, missing media body, forbidden channel, and upstream unavailable cases in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T008 [P] Add planned import placeholders for `build_watermarks_set_wrapper` expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T009 [P] Create the initial watermarks contract test module scaffold in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py`

**Checkpoint**: Shared test setup exists, and user story work can proceed in priority order or in parallel where marked.

---

## Phase 3: User Story 1 - Set a Channel Watermark Through a Reusable Layer 1 Contract (Priority: P1) MVP

**Goal**: A platform developer can submit an authorized `watermarks.set` request through a typed internal Layer 1 wrapper and receive a normalized successful watermark-update acknowledgement.

**Independent Test**: Submit a valid authorized request with `channelId`, watermark metadata, and `media`; verify the wrapper executes through the shared executor, sends `POST /upload/youtube/v3/watermarks/set`, and returns a normalized acknowledgement tied to the target channel.

### Tests for User Story 1 (REQUIRED)

> Write these tests FIRST and verify they fail before implementation.

- [X] T010 [P] [US1] Add failing unit tests for `watermarks.set` wrapper metadata, export visibility, OAuth-only call behavior, required `channelId`, required `body`, required `media`, and successful executor call shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T011 [P] [US1] Add failing transport tests for authorized `POST /upload/youtube/v3/watermarks/set` request construction, `channelId` query parameter encoding, bearer authorization header use, body/media upload handling, and 204 no-content acknowledgement normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T012 [P] [US1] Add failing integration test for successful `watermarks.set` execution through the shared executor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement `WatermarksSetWrapper` with OAuth-required call validation and upload-aware request validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T014 [US1] Implement `build_watermarks_set_wrapper` metadata with operation key `watermarks.set`, path `/upload/youtube/v3/watermarks/set`, method `POST`, quota cost `50`, and required `channelId`, `body`, and `media` request shape in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T015 [US1] Export `build_watermarks_set_wrapper` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T016 [US1] Add `watermarks.set` request handling and no-content acknowledgement normalization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T017 [US1] Add upload-path request shaping for `watermarks.set` so query, body metadata, media content, and OAuth headers remain distinct in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T018 [US1] Add or update reStructuredText docstrings for every new or modified `watermarks.set` wrapper, export, and transport function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T019 [US1] Run targeted US1 validation with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T020 [US1] Refactor US1 wrapper and transport code for naming clarity while keeping targeted tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: User Story 1 is independently functional as the MVP internal wrapper path.

---

## Phase 4: User Story 2 - Review Quota, OAuth, and Upload Expectations Before Reuse (Priority: P2)

**Goal**: A maintainer can review wrapper metadata, contracts, and higher-layer summaries to understand quota cost, OAuth requirement, required target channel, watermark metadata, media-upload expectations, supported upload boundary, and successful acknowledgement behavior.

**Independent Test**: Review the wrapper surface and generated summary for `watermarks.set`; verify quota `50`, OAuth-required access, required `channelId`, required `body`, required `media`, upload limits, acknowledgement semantics, and `onBehalfOfContentOwner` boundary guidance are visible in under 1 minute.

### Tests for User Story 2 (REQUIRED)

> Write these tests FIRST and verify they fail before implementation.

- [X] T021 [P] [US2] Add failing contract tests for `watermarks.set` wrapper review surface identity, quota cost, OAuth mode, required `channelId`, required `body`, required `media`, upload-boundary wording, acknowledgement wording, and partner delegation boundary notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py`
- [X] T022 [P] [US2] Add failing metadata contract tests for `watermarks.set` maintainer-facing notes and quota/auth/upload visibility in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T023 [P] [US2] Add failing consumer contract tests for a higher-layer `watermarks.set` summary that preserves target channel context, source operation, auth mode, quota cost, required fields, upload guidance, and credential-safe acknowledgement details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2

- [X] T024 [US2] Enrich `watermarks.set` metadata notes and request-shape review text for quota, OAuth, required `channelId`, watermark metadata, media upload constraints, acknowledgement semantics, and partner-only delegation boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T025 [US2] Implement `set_watermark_summary` higher-layer summary method for `watermarks.set` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Ensure the higher-layer watermark summary omits OAuth tokens, credentials, channel-owner identity, delegated-owner credentials, and raw uploaded media bytes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T027 [US2] Add or update reStructuredText docstrings for every new or modified metadata and consumer-summary function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T028 [US2] Run targeted US2 validation with `python3 -m pytest tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T029 [US2] Refactor US2 metadata and consumer-summary wording to remove duplicated upload-boundary guidance while keeping targeted tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Checkpoint**: User Story 2 is independently reviewable through metadata, contracts, and consumer summaries.

---

## Phase 5: User Story 3 - Reject Invalid or Under-Authorized Watermark Requests Clearly (Priority: P3)

**Goal**: A downstream tool author can distinguish missing or malformed channel identifiers, missing watermark metadata, missing upload content, unsupported media, missing OAuth access, forbidden channel failures, upstream image validation failures, upstream outages, and successful acknowledgements.

**Independent Test**: Submit malformed, unsupported, unauthorized, upstream-refused, upstream-unavailable, and valid `watermarks.set` requests; verify each outcome remains distinct and actionable.

### Tests for User Story 3 (REQUIRED)

> Write these tests FIRST and verify they fail before implementation.

- [X] T030 [P] [US3] Add failing unit tests for missing `channelId`, blank `channelId`, non-string `channelId`, missing `body`, unsupported watermark metadata, missing `media`, unsupported MIME type, oversized media, unsupported top-level fields, unsupported partner-only delegation when not supported, and missing OAuth access in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T031 [P] [US3] Add failing transport tests for upstream unsupported image format, excessive image height, excessive image width, missing media body, forbidden channel, and upstream unavailable normalization for `watermarks.set` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T032 [P] [US3] Add failing integration tests that separate local validation failures, access failures, unsupported media failures, upstream image validation failures, channel refusals, upstream outages, and successful acknowledgements for `watermarks.set` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T033 [P] [US3] Add failing contract tests for auth-upload boundary wording and failure-boundary reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py`

### Implementation for User Story 3

- [X] T034 [US3] Implement deterministic `watermarks.set` request validation for required `channelId`, required `body`, required `media`, unsupported metadata, unsupported top-level fields, and unsupported partner-only delegation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T035 [US3] Implement media payload validation for supported MIME types, non-empty content, and documented maximum upload size in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T036 [US3] Implement OAuth-only error behavior for `watermarks.set` before execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T037 [US3] Extend `watermarks.set` upstream error-category normalization for unsupported image format, excessive image dimensions, missing media body, forbidden channel, and upstream unavailable cases in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T038 [US3] Verify unsupported `onBehalfOfContentOwner` behavior is rejected or clearly flagged by the wrapper contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T039 [US3] Add or update reStructuredText docstrings for every new or modified validation and failure-normalization function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T040 [US3] Run targeted US3 validation with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_watermarks_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T041 [US3] Refactor US3 validation and error-boundary code while keeping targeted tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

**Checkpoint**: All user stories are independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation consistency, and regression cleanup across all stories.

- [X] T042 [P] Reconcile implementation behavior with `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/layer1-watermarks-set-wrapper-contract.md`
- [X] T043 [P] Reconcile implementation behavior with `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/contracts/layer1-watermarks-set-auth-upload-contract.md`
- [X] T044 [P] Update quickstart review readiness notes if implementation discovers naming changes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/quickstart.md`
- [X] T045 [P] Review all changed Python functions for complete reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T046 Run targeted Layer 1 regression suite with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_watermarks_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T047 Run full repository test suite with `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T048 Run lint validation with `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion

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
Task: "T010 [US1] Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T011 [US1] Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T012 [US1] Add failing integration test in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

### User Story 2

```bash
# Parallel Red tasks after Phase 2:
Task: "T021 [US2] Add failing wrapper contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py"
Task: "T022 [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T023 [US2] Add failing consumer contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

### User Story 3

```bash
# Parallel Red tasks after Phase 2:
Task: "T030 [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T031 [US3] Add failing upstream error normalization tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T032 [US3] Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T033 [US3] Add failing boundary contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate US1 independently with targeted unit, transport, and integration tests
5. Continue to US2 and US3 only after the internal wrapper can submit and acknowledge a valid watermark-set request

### Incremental Delivery

1. Setup + Foundational: shared fixtures and planned imports are ready
2. US1: add the internal wrapper and successful acknowledgement path
3. US2: add review surfaces and higher-layer summary details
4. US3: harden invalid, unauthorized, unsupported-media, forbidden-channel, and upstream failure boundaries
5. Polish: reconcile contracts, run targeted regression, full pytest, and Ruff

### Parallel Team Strategy

1. One developer prepares shared test fixtures in Phase 2
2. Multiple developers write Red tests for US1, US2, and US3 in parallel
3. Implementation proceeds in priority order to reduce merge conflicts in shared integration modules
4. Final validation is serialized through targeted regression, full pytest, and Ruff

---

## Notes

- [P] tasks touch different files or can run before shared implementation exists
- [US1], [US2], and [US3] labels map directly to prioritized user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/154-watermarks-set-wrapper/spec.md`
- YT-154 remains internal to Layer 1 and must not add a public `watermarks_set` MCP tool
- Every Python implementation task must preserve or add reStructuredText docstrings before the story is marked complete
- The feature is not complete until `python3 -m pytest` and `python3 -m ruff check .` pass from `/Users/ctgunn/Projects/youtube-mcp-server`
