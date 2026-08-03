# Tasks: YT-158 Layer 1 Live Calls for Channel and Community Resources

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [live-call contract](contracts/layer1-channel-community-live-call-contract.md), and [quickstart.md](quickstart.md)

**Tests**: Tests are mandatory. Every implementation phase follows Red-Green-Refactor. Completion requires passing `python3 -m pytest` and `python3 -m ruff check .` after the final code change. Every new or modified Python function requires a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each story has a discrete acceptance proof. The shared dispatcher wiring is foundational because every story depends on the configured runtime selecting live execution.

## Phase 1: Setup (Shared Planning and Test Baseline)

**Purpose**: Confirm the scope and record the pre-change behavior before implementation.

- [X] T001 Reconcile the 20-operation inventory and seven-resource-family acceptance matrix against `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/contracts/layer1-channel-community-live-call-contract.md`
- [X] T002 Run and record the existing targeted baseline for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_live_runtime.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` before adding YT-158 coverage

---

## Phase 2: Foundational (Configured Runtime Injection)

**Purpose**: Build the one shared configured-descriptor seam that blocks every user story. Complete this phase before story implementation.

### Red — Foundational Tests

- [X] T003 [P] Add a failing configured-runtime registration test in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` proving that all 20 in-scope descriptors receive the runtime executor and configured credential availability rather than a representative default
- [X] T004 [P] Add a failing public-contract regression test in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` proving configured descriptors retain the existing tool name, input schema, metadata, result shape, and safe error category

### Green — Minimal Shared Implementation

- [X] T005 Extend configured descriptor construction in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` so captions, channel banners, channels, channel sections, comments, and comment threads receive the same configured executor/API-key/OAuth dependencies already supplied to activities
- [X] T006 Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, documenting runtime dependency inputs, returned descriptors, errors where applicable, and secret-free side effects

### Refactor — Foundational Cleanup

- [X] T007 Refactor the shared runtime-dependency mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` to avoid repeated argument construction while preserving explicit test/local overrides in all affected descriptor builders
- [X] T008 Run the foundational Red/Green regression checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, fixing failures before beginning user-story work

**Checkpoint**: A normal configured dispatcher supplies the shared live runtime to all 20 in-scope public descriptors; no user story may proceed with representative configured defaults.

---

## Phase 3: User Story 1 — Receive Live Channel and Community Results (Priority: P1) 🎯 MVP

**Goal**: A configured default invocation of each in-scope operation reaches the live request path and preserves its normalized result contract.

**Independent Test**: Configure the runtime with a controlled opener, invoke every in-scope operation without a test-only executor override, and assert a distinctive controlled live response is mapped through the existing wrapper and public result path rather than a representative response.

### Red — User Story 1 Tests

- [X] T009 [P] [US1] Add parameterized failing configured-live success tests for `activities.list`, all five caption operations, `channelBanners.insert`, both channel operations, all four channel-section operations, all five comment operations, and both comment-thread operations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_configured_runtime_flows.py`
- [X] T010 [P] [US1] Add failing result-compatibility assertions for the seven affected families in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, covering unchanged descriptor metadata and family-specific normalized result shapes after runtime injection

### Green — User Story 1 Implementation

- [X] T011 [US1] Correct any descriptor builder that does not forward the supplied configured executor or credential to its existing wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T012 [US1] Preserve the existing Layer 1 metadata, selector/body validation, quota documentation, response-normalizer selection, and wrapper call path for all 20 operations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`
- [X] T013 [US1] Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`

### Refactor — User Story 1 Cleanup

- [X] T014 [US1] Refactor the controlled live-response recorder and operation matrix in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_configured_runtime_flows.py` to remove duplicated family fixtures while retaining a distinct assertion for each of the 20 operations
- [X] T015 [US1] Run the User Story 1 proof in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_configured_runtime_flows.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, fixing failures before accepting the MVP

**Checkpoint**: All 20 configured default operations select the shared live path and keep their public result contract. This is the MVP scope.

---

## Phase 4: User Story 2 — Apply the Correct Authorization and Request Form (Priority: P2)

**Goal**: Each configured operation applies its existing API-key, OAuth, or conditional authorization rule and emits the correct existing request form without leaking secrets.

**Independent Test**: Use a controlled opener to capture each operation's request and assert its method, path, parameters, selected credential location, body or media form, success mapping, and normalized failure behavior; run cases without the selected credential and with controlled upstream failures.

### Red — User Story 2 Tests

- [X] T016 [P] [US2] Add failing parameterized request-construction tests for all 20 operations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, asserting the declared method, path, query parameters, API-key query credential or OAuth bearer credential, JSON body, raw-media body, or multipart body as applicable
- [X] T017 [P] [US2] Add failing safe-failure and redaction tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` for missing selected credentials, HTTP authorization rejection, malformed responses, timeout/retryable failures, and absence of API keys/OAuth tokens in result, error, and observability details

### Green — User Story 2 Implementation

- [X] T018 [US2] Correct only authorization selection, request shaping, or normalized-error defects exposed by T016–T017 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` without adding a resource-specific transport
- [X] T019 [US2] Preserve shared credential redaction, retry selection, safe observability, and failure normalization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/errors.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T020 [US2] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/errors.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`

### Refactor — User Story 2 Cleanup

- [X] T021 [US2] Refactor request-capture and secret-redaction fixtures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` so request-form assertions stay table-driven and no fixture embeds a real credential
- [X] T022 [US2] Run the User Story 2 verification in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`, fixing failures before accepting authorization and request-form behavior

**Checkpoint**: The configured runtime applies the existing authorization and request-form contract to all 20 operations, with normalized secret-free failures.

---

## Phase 5: User Story 3 — Use Live Wrappers Through Public Tools (Priority: P3)

**Goal**: At least one configured public-tool flow per affected resource family reaches the live wrapper path, with no tool bypassing Layer 1 or substituting representative data.

**Independent Test**: Construct the normal application/transport/dispatcher path with configured runtime settings and a controlled opener; invoke one tool for activities, captions, channel banners, channels, channel sections, comments, and comment threads, and verify the opener observes the expected request and the client receives the existing normalized result or safe failure.

### Red — User Story 3 Tests

- [X] T023 [US3] Add seven failing configured public-tool live-path tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_configured_runtime_flows.py` for `activities_list`, a captions tool, `channelBanners_insert`, a channels tool, a channel-sections tool, a comments tool, and a comment-threads tool through application/transport/dispatcher composition
- [X] T024 [US3] Add failing public-tool normalized-upstream-failure and no-representative-fallback tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_configured_runtime_flows.py`, using controlled authorization and upstream failures without exposing credentials

### Green — User Story 3 Implementation

- [X] T025 [US3] Correct any configured public-tool registration or handler wiring defect identified by T023–T024 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/app.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`
- [X] T026 [US3] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/app.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`

### Refactor — User Story 3 Cleanup

- [X] T027 [US3] Refactor the seven public-tool flow fixtures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_configured_runtime_flows.py` to share configured-runtime setup while keeping each resource-family assertion independently readable
- [X] T028 [US3] Run the User Story 3 proof in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_configured_runtime_flows.py` and the affected registration suites under `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, fixing failures before accepting public-tool reachability

**Checkpoint**: All seven affected resource families have a configured public-tool flow that demonstrably reaches the shared live wrapper path.

---

## Phase 6: Polish and Cross-Cutting Completion

**Purpose**: Complete repository-wide compatibility, security, documentation, and final validation.

- [X] T029 [P] Reconcile the final test commands and expected secret-handling guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/quickstart.md` with the implemented focused test paths
- [X] T030 [P] Review the final runtime-injection change against `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/contracts/layer1-channel-community-live-call-contract.md` and add missing contract regression assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`
- [X] T031 Run every focused unit, integration, and contract command listed in `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/quickstart.md`, fixing all failures and documenting any changed verification path in that file
- [X] T032 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server/` and fix every full-suite failure before declaring YT-158 complete
- [X] T033 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server/`, fix all reported issues, and re-run the relevant tests for every changed file
- [X] T034 Verify every changed Python function has a complete reStructuredText docstring and every YT-158 acceptance criterion is evidenced in `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/contracts/layer1-channel-community-live-call-contract.md`, and the final test output

---

## Dependencies and Execution Order

1. Complete Phase 1, then Phase 2. T003 and T004 can run in parallel; T005 depends on both Red tests; T006 and T007 follow the implementation; T008 gates every user story.
2. User Story 1 is the MVP and begins after T008. T009 and T010 can run in parallel, then T011–T013, then T014–T015.
3. User Story 2 begins after the configured-default behavior is stable in T015. T016 and T017 can run in parallel, then T018–T020, then T021–T022.
4. User Story 3 begins after T015 and may be developed in parallel with User Story 2 once the common configured-runtime seam is stable. T023 precedes T024 because both extend the same flow-test module; they are followed by T025–T026 and then T027–T028.
5. Phase 6 starts after all desired user stories pass their checkpoints. T029 and T030 can run in parallel; T031 precedes the final mandatory T032–T034 sequence.

## Parallel Execution Examples

### User Story 1

```text
T009: Parameterized configured-live success matrix in tests/integration/test_youtube_configured_runtime_flows.py
T010: Result-contract compatibility coverage in tests/contract/test_youtube_tool_catalog_contract.py
```

### User Story 2

```text
T016: Request method/path/auth/body/upload coverage in tests/unit/test_youtube_transport.py
T017: Missing-credential, upstream-failure, and redaction coverage in tests/integration/test_layer1_live_runtime.py
```

### User Story 3

```text
T023: Seven configured public-tool success flows in tests/integration/test_youtube_configured_runtime_flows.py
T024: Configured public-tool failure/no-fallback flows in the same file after T023
```

## Implementation Strategy

### MVP First

1. Complete T001–T008 to remove representative defaults from configured descriptor construction.
2. Complete User Story 1 (T009–T015).
3. Stop and independently verify all 20 configured default operations return controlled live-path results with stable public contracts.

### Incremental Delivery

1. The foundation establishes runtime injection for all seven families.
2. User Story 1 proves live result selection across all 20 operations.
3. User Story 2 proves authorization, request forms, retry/error mapping, and redaction.
4. User Story 3 proves the public tool surface reaches the same live wrapper path for every family.
5. Phase 6 completes documentation, full-suite regression verification, linting, and docstring auditing.

### Format Validation

All 34 tasks use the required `- [ ] T### [P?] [US#?] description with absolute file path` format. Story labels appear only on story tasks; parallel markers identify only work that can proceed in separate files without waiting on an incomplete task.
