# Tasks: YT-155 Layer 1 Endpoint `watermarks.unset`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story includes Red-Green-Refactor coverage tasks, and completion requires a passing full repository test-suite run after final code changes. Python code changes require reStructuredText docstrings for all new or modified functions before a story is complete.

**Organization**: Tasks are grouped by user story so `watermarks.unset` can be implemented as an internal Layer 1 wrapper MVP first, then expanded with reviewability and failure-boundary hardening.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm scope, local patterns, and target files before writing failing tests.

- [X] T001 Review YT-155 scope and internal-only Layer 1 boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/plan.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/quickstart.md`
- [X] T002 [P] Review existing `watermarks.set` wrapper and no-content acknowledgement patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T003 [P] Review YT-155 contract expectations in `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/contracts/layer1-watermarks-unset-wrapper-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/contracts/layer1-watermarks-unset-auth-boundary-contract.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Prepare shared test seams and confirm no public MCP surface is introduced.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T004 Add shared representative `watermarks.unset` argument fixtures for valid, missing-channel, blank-channel, non-string-channel, body-present, media-present, unsupported-field, and optional delegation cases in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T005 [P] Add planned import placeholders for `build_watermarks_unset_wrapper` expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T006 [P] Extend the existing watermarks contract test scaffold to read YT-155 contract documents in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py`
- [X] T007 Verify that no `watermarks_unset` public MCP tool registration is planned or required in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

**Checkpoint**: Shared YT-155 test seams are ready, and user story work can begin.

---

## Phase 3: User Story 1 - Remove a Channel Watermark Through a Reusable Layer 1 Contract (Priority: P1) MVP

**Goal**: A platform developer can call an authorized internal `watermarks.unset` wrapper with channel context and receive a normalized watermark-removal acknowledgement.

**Independent Test**: Submit valid authorized arguments with `channelId`; verify the wrapper executes through the shared executor, sends a `POST /youtube/v3/watermarks/unset` request with OAuth access, and returns a normalized acknowledgement tied to the target channel.

### Tests for User Story 1 (Red)

- [X] T008 [P] [US1] Add failing unit tests for `watermarks.unset` wrapper metadata, export visibility, OAuth-only call behavior, required `channelId`, no-upload request shape, and successful executor call shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T009 [P] [US1] Add failing transport tests for authorized `POST /youtube/v3/watermarks/unset` request construction, `channelId` query parameter encoding, bearer authorization header use, absence of request body/media upload content, and 204 no-content acknowledgement normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T010 [P] [US1] Add failing integration test for successful `watermarks.unset` execution through the shared executor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 1 (Green)

- [X] T011 [US1] Implement `WatermarksUnsetWrapper` with OAuth-required call behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T012 [US1] Implement `_require_watermarks_unset_arguments` validation for required non-empty `channelId` and no `body` or `media` payloads in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T013 [US1] Implement `build_watermarks_unset_wrapper` metadata with operation key `watermarks.unset`, path `/youtube/v3/watermarks/unset`, method `POST`, quota cost `50`, auth mode `oauth_required`, and required `channelId` request shape in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T014 [US1] Export `build_watermarks_unset_wrapper` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T015 [US1] Add `watermarks.unset` request handling and no-content removal acknowledgement normalization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for every new or modified `watermarks.unset` wrapper, export, and transport function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`

### Refactor and Validation for User Story 1

- [X] T017 [US1] Refactor `watermarks.unset` naming and acknowledgement result fields to align with neighboring mutation wrappers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T018 [US1] Run targeted US1 validation with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Review Quota and OAuth Expectations Before Reuse (Priority: P2)

**Goal**: A maintainer or higher-layer author can review wrapper metadata, contracts, and summaries to understand quota cost, OAuth requirement, required target channel, no-upload boundary, unsupported request shapes, and acknowledgement behavior.

**Independent Test**: Review the wrapper surface and generated summary for `watermarks.unset`; verify quota `50`, OAuth-required access, required `channelId`, no-upload guidance, acknowledgement semantics, and partner delegation boundary guidance are visible in under 1 minute.

### Tests for User Story 2 (Red)

- [X] T019 [P] [US2] Add failing contract tests for `watermarks.unset` wrapper review surface identity, quota cost, OAuth mode, required `channelId`, no-upload boundary wording, no-removal wording, acknowledgement wording, and partner delegation boundary notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py`
- [X] T020 [P] [US2] Add failing metadata contract tests for `watermarks.unset` maintainer-facing notes and quota/auth/no-upload visibility in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [X] T021 [P] [US2] Add failing consumer contract tests for a higher-layer `watermarks.unset` summary that preserves target channel context, source operation, auth mode, quota cost, required fields, no-upload guidance, no-removal guidance, and credential-safe acknowledgement details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 2 (Green)

- [X] T022 [US2] Enrich `watermarks.unset` metadata notes and request-shape review text for quota, OAuth, required `channelId`, no-upload boundary, acknowledgement semantics, no-removal outcomes, and partner-only delegation boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T023 [US2] Implement `unset_watermark_summary` higher-layer summary method for `watermarks.unset` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T024 [US2] Add or update reStructuredText docstrings for every new or modified metadata and consumer-summary function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

### Refactor and Validation for User Story 2

- [X] T025 [US2] Refactor duplicated quota, auth, no-upload, and acknowledgement wording across wrapper notes and consumer-summary fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T026 [US2] Run targeted US2 validation with `python3 -m pytest tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reject Invalid or Under-Authorized Removal Requests Clearly (Priority: P3)

**Goal**: A downstream tool author can distinguish malformed requests, unsupported set-style payloads, missing OAuth access, forbidden channel failures, no-removal-possible outcomes, upstream unavailability, and successful removals.

**Independent Test**: Submit malformed, unsupported, unauthorized, upstream-refused, no-removal, upstream-unavailable, and valid `watermarks.unset` requests; verify each outcome remains distinct and actionable.

### Tests for User Story 3 (Red)

- [X] T027 [P] [US3] Add failing unit tests for blank `channelId`, non-string `channelId`, unsupported `body`, unsupported `media`, unsupported top-level fields, unsupported partner delegation, and missing OAuth access in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T028 [P] [US3] Add failing transport tests for forbidden channel, no-current-watermark or already-removed response, invalid request response, and upstream unavailable normalization for `watermarks.unset` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T029 [P] [US3] Add failing integration tests that separate local validation failures, access failures, unsupported payload failures, forbidden channel failures, no-removal outcomes, upstream outages, and successful acknowledgements for `watermarks.unset` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T030 [P] [US3] Add failing contract tests for auth-boundary wording, no-removal wording, unsupported-payload wording, and failure-boundary reviewability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py`

### Implementation for User Story 3 (Green)

- [X] T031 [US3] Harden deterministic `watermarks.unset` request validation for required `channelId`, unsupported `body`, unsupported `media`, unsupported set-only fields, unsupported top-level fields, and unsupported partner-only delegation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T032 [US3] Implement OAuth-only error behavior and unsupported-payload error messages for `watermarks.unset` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T033 [US3] Implement normalized upstream category mapping for invalid request, forbidden channel, no-removal/not-found, and upstream unavailable `watermarks.unset` failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T034 [US3] Update `unset_watermark_summary` to keep invalid, forbidden, no-removal, upstream-unavailable, and success outcomes credential-safe and reviewable in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T035 [US3] Add or update reStructuredText docstrings for every new or modified validation, error-mapping, transport, and consumer-summary function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

### Refactor and Validation for User Story 3

- [X] T036 [US3] Refactor failure-boundary wording and test names so `watermarks.unset` remains a single-endpoint Layer 1 slice in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py`
- [X] T037 [US3] Run targeted US3 validation with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_watermarks_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation consistency, and repository health.

- [X] T038 [P] Confirm YT-155 implementation remains internal-only and does not register a public `watermarks_unset` MCP tool in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T039 [P] Review feature-local contracts and quickstart for consistency with implemented `watermarks.unset` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/contracts/layer1-watermarks-unset-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/contracts/layer1-watermarks-unset-auth-boundary-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/quickstart.md`
- [X] T040 Review all reStructuredText docstrings for touched Python functions before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T041 Run complete targeted Layer 1 validation with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T042 Run full repository tests with `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T043 Run lint validation with `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can be developed after or alongside US1, but final summary validation is clearer once US1 wrapper behavior exists.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and benefits from US1 wrapper behavior plus US2 review surfaces.
- **Polish (Phase 6)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories; delivers the MVP wrapper and successful removal path.
- **US2 (P2)**: Can start after Foundational, but depends on wrapper metadata shape from US1 for final passing checks.
- **US3 (P3)**: Can start after Foundational, but depends on wrapper validation and transport seams from US1 for final passing checks.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Green implementation must be the smallest code change that satisfies the story tests.
- reStructuredText docstring tasks must be complete before each story checkpoint.
- Refactor tasks run only after story tests pass and must keep targeted tests green.
- Full repository validation happens in Phase 6 after final code changes.

## Parallel Opportunities

- T002 and T003 can run in parallel after T001 because they inspect different context surfaces.
- T005 and T006 can run in parallel after T004 because they touch different test files.
- US1 Red tasks T008, T009, and T010 can run in parallel because they target unit, transport, and integration coverage in different files.
- US2 Red tasks T019, T020, and T021 can run in parallel because they target separate contract files.
- US3 Red tasks T027, T028, T029, and T030 can run in parallel because they target separate test concerns.
- T038 and T039 can run in parallel during polish because they inspect different files and do not depend on test execution.

## Parallel Example: User Story 1

```bash
Task: "T008 [P] [US1] Add failing unit tests for watermarks.unset wrapper metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T009 [P] [US1] Add failing transport tests for watermarks.unset request construction in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T010 [P] [US1] Add failing integration test for successful watermarks.unset execution in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 2

```bash
Task: "T019 [P] [US2] Add failing watermarks contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py"
Task: "T020 [P] [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T021 [P] [US2] Add failing consumer contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T027 [P] [US3] Add failing validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T028 [P] [US3] Add failing transport normalization tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T029 [P] [US3] Add failing integration failure-boundary tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T030 [P] [US3] Add failing contract failure-boundary tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_watermarks_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational test seams.
3. Complete Phase 3 User Story 1.
4. Validate the MVP with T018.
5. Stop for review if only the typed internal removal wrapper is needed.

### Incremental Delivery

1. Complete Setup and Foundational phases.
2. Deliver US1 to make `watermarks.unset` callable internally.
3. Deliver US2 to make quota, OAuth, no-upload, and downstream reuse expectations reviewable.
4. Deliver US3 to harden invalid, unauthorized, unsupported, forbidden, no-removal, and upstream failure boundaries.
5. Complete Phase 6 full targeted, full repository, and lint validation.

### Parallel Team Strategy

1. One person completes setup and foundational fixture seams.
2. Separate contributors can write Red tests for US1, US2, and US3 in parallel once foundational seams exist.
3. Green implementation should be sequenced through US1 first because US2 and US3 final checks depend on the wrapper shape.
4. Final polish and full-suite validation should happen after all selected stories are integrated.

## Notes

- `[P]` tasks touch different files or inspect independent surfaces and can run in parallel after their prerequisites.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to the prioritized user stories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/155-watermarks-unset-wrapper/spec.md`.
- Every story includes Red tests, Green implementation, reStructuredText docstring work, Refactor, and targeted validation.
- Phase 6 includes the mandatory full repository test run and lint validation before completion.
