# Tasks: YT-209 Layer 2 Tool `channelBanners_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/contracts/channel-banners-insert-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/quickstart.md`

**Tests**: Test tasks are REQUIRED. Every user story includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python code tasks include explicit reStructuredText docstring work for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase because it touches different files or only reads context.
- **[Story]**: User story label for story phases only.
- Every task includes an exact repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature context and implementation surface before writing failing tests.

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/spec.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/contracts/channel-banners-insert-tool-contract.md` to extract the required `channelBanners_insert` contract, test commands, and docstring obligations.
- [X] T002 [P] Review existing Layer 2 endpoint patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`.
- [X] T003 [P] Review shared Layer 2 contract, response-boundary, and representative example helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`.
- [X] T004 [P] Review public YouTube exports and default registration surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T005 [P] Review the existing Layer 1 `channelBanners.insert` wrapper, validator, and consumer context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channel_banners.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/consumers/channel_banners.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared test scaffolding and guardrails that all stories depend on.

**Critical**: No user story work can begin until this phase is complete.

- [X] T006 Confirm the YT-109 Layer 1 `build_channel_banners_insert_wrapper` dependency is available and OAuth/media constrained in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py`.
- [X] T007 Confirm shared Layer 2 helpers support upload-result response boundaries, media-constrained availability, and safe public metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`.
- [X] T008 [P] Create the initial channel-banner contract test module with a module docstring and failing import or missing-contract check for `build_channel_banners_insert_contract` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`.
- [X] T009 [P] Create the initial channel-banner unit test module with a module docstring and failing import or missing-validator check for `validate_channel_banners_insert_arguments` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_banners.py`.
- [X] T010 [P] Create the initial channel-banner registration test module with a module docstring and failing discovery check for `channelBanners_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_banners_registration.py`.
- [X] T011 Run the foundational red check `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/unit/test_youtube_channel_banners.py tests/integration/test_youtube_channel_banners_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new missing-symbol or missing-discovery checks fail before implementation.

**Checkpoint**: Foundation ready - user story implementation can now begin in priority order or in parallel if separate workers coordinate file ownership.

---

## Phase 3: User Story 1 - Upload Channel Banner Assets Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `channelBanners_insert` with eligible authorization and supported banner media input and receive a near-raw banner upload result mapped to `channelBanners.insert`.

**Independent Test**: Invoke the concrete `channelBanners_insert` descriptor handler with supported media input and confirm the result identifies `channelBanners.insert`, quota cost `50`, safe media context, returned banner URL, and no fabricated active channel branding state.

### Tests for User Story 1 (REQUIRED)

- [X] T012 [P] [US1] Add failing contract tests for `channelBanners_insert` module exports, descriptor existence, contract builder existence, input schema required `media`, and successful upload result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`.
- [X] T013 [P] [US1] Add failing unit tests for `CHANNEL_BANNERS_INSERT_INPUT_SCHEMA`, `validate_channel_banners_insert_arguments`, and `map_channel_banners_insert_result` upload-result behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_banners.py`.
- [X] T014 [P] [US1] Add failing integration tests for registering and executing `channelBanners_insert` through `InMemoryToolDispatcher` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_banners_registration.py`.
- [X] T015 [US1] Run `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/unit/test_youtube_channel_banners.py tests/integration/test_youtube_channel_banners_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new US1 tests fail before implementation.

### Implementation for User Story 1

- [X] T016 [US1] Create the concrete Layer 2 channel banner module with module-level constants, safe local default transport, and executor helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T017 [US1] Implement `ChannelBannersInsertToolError`, `build_channel_banners_insert_contract`, and the upload-result `ResponseBoundary` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T018 [US1] Implement `validate_channel_banners_insert_arguments`, `map_channel_banners_insert_result`, `build_channel_banners_insert_handler`, and `build_channel_banners_insert_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T019 [US1] Export `channelBanners_insert` constants, error class, contract builder, handler builder, descriptor builder, mapper, and validator from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
- [X] T020 [US1] Register `build_channel_banners_insert_tool_descriptor()` in the default dispatcher tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T021 [US1] Add or update reStructuredText docstrings for every new or modified `channelBanners_insert` Python function and test helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_banners.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_banners_registration.py`.
- [X] T022 [US1] Run `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/unit/test_youtube_channel_banners.py tests/integration/test_youtube_channel_banners_registration.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and make the US1 tests pass.
- [X] T023 [US1] Refactor the `channelBanners_insert` implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py` to remove duplication with existing Layer 2 upload helpers while preserving the passing US1 tests.

**Checkpoint**: User Story 1 is independently functional and provides the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Upload Rules Before Calling (Priority: P2)

**Goal**: A client developer can inspect `channelBanners_insert` before calling and see upstream identity, quota cost `50`, OAuth-required auth, media constraints, optional delegation, no-body request behavior, returned URL behavior, and the separate `channels.update` activation boundary.

**Independent Test**: Review tool metadata, discovery output, and examples and confirm a caller can prepare a valid request without consulting implementation-only artifacts.

### Tests for User Story 2 (REQUIRED)

- [X] T024 [P] [US2] Add failing contract tests for `channelBanners_insert` metadata, usage notes, caveats, response convention, response boundary, returned URL behavior, and activation-boundary wording in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`.
- [X] T025 [P] [US2] Add failing shared metadata safety checks for `channelBanners_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`.
- [X] T026 [P] [US2] Add failing representative example alignment checks for `channelBanners_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`.
- [X] T027 [P] [US2] Add failing default-discovery metadata assertions for `channelBanners_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T028 [US2] Run `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new US2 tests fail before implementation.

### Implementation for User Story 2

- [X] T029 [US2] Add `channelBanners_insert` representative metadata to `REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`.
- [X] T030 [US2] Update `channelBanners_insert` metadata text, usage notes, and caveats so discovery exposes `channelBanners.insert`, `Quota cost: 50`, OAuth-required auth, required media, accepted MIME types, 6 MB maximum, 16:9 and resolution guidance, `onBehalfOfContentOwner`, no JSON request body, returned URL behavior, and separate `channels.update` activation boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T031 [US2] Ensure public metadata safety validation for `channelBanners_insert` passes without exposing API keys, OAuth tokens, stack traces, signed URLs, raw image payloads, binary payloads, private channel data, or secret values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T032 [US2] Add safe caller-facing examples for authorized upload, delegated upload, missing media, invalid media, unsupported channel update option, authorization-sensitive failure, and returned URL boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T033 [US2] Add or update reStructuredText docstrings for every new or modified metadata/example Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`.
- [X] T034 [US2] Run `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and make the US2 tests pass.
- [X] T035 [US2] Refactor metadata, usage-note, and example wording in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` to remove duplicate prose while preserving the passing US2 tests.

**Checkpoint**: User Story 2 is independently inspectable and metadata-complete.

---

## Phase 5: User Story 3 - Reject Unsupported Banner Upload Requests Clearly (Priority: P3)

**Goal**: Invalid, unauthorized, unsupported, or upstream-failed `channelBanners_insert` requests produce clear safe error categories and remediation guidance.

**Independent Test**: Submit representative invalid requests and fake upstream failures and confirm each failure maps to the expected safe category without leaking sensitive details.

### Tests for User Story 3 (REQUIRED)

- [X] T036 [P] [US3] Add failing parameterized validation tests for missing `media`, missing `media.mimeType`, missing media content or reference, unsupported MIME type, oversized media, unsupported fields, unsupported JSON body, and unsupported image-editing fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`.
- [X] T037 [P] [US3] Add failing unit tests for `validate_channel_banners_insert_arguments` safe details, optional `onBehalfOfContentOwner`, media-size handling, and unsupported request-shape handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_banners.py`.
- [X] T038 [P] [US3] Add failing upstream error mapping tests for `mediaBodyRequired`, `bannerAlbumFull`, forbidden authorization failures, quota exhaustion, transient unavailability, invalid request, and unexpected upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`.
- [X] T039 [P] [US3] Add failing dispatcher rejection tests for invalid `channelBanners_insert` requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_banners_registration.py`.
- [X] T040 [US3] Run `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/unit/test_youtube_channel_banners.py tests/integration/test_youtube_channel_banners_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm the new US3 tests fail before implementation.

### Implementation for User Story 3

- [X] T041 [US3] Implement missing-media, missing-mime-type, missing-content, unsupported-MIME, oversized-media, unsupported-field, no-body, delegation, and OAuth validation branches for `channelBanners_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T042 [US3] Implement safe upstream error mapping for `channelBanners_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, including `mediaBodyRequired` and `bannerAlbumFull` to `invalid_request`, forbidden errors to `authorization_failed`, quota errors to `quota_exhausted`, unavailable service to `endpoint_unavailable`, and unexpected errors to `upstream_failure`.
- [X] T043 [US3] Ensure `ChannelBannersInsertToolError` details never expose API keys, OAuth tokens, stack traces, signed URLs, raw image payloads, binary payloads, private channel data, or secret values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
- [X] T044 [US3] Add or update reStructuredText docstrings for every new or modified validation, error-mapping, and fake-wrapper test helper function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_banners.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_banners_registration.py`.
- [X] T045 [US3] Run `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/unit/test_youtube_channel_banners.py tests/integration/test_youtube_channel_banners_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and make the US3 tests pass.
- [X] T046 [US3] Refactor validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py` to reuse shared error categories and existing Layer 2 helper patterns without changing public behavior.

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, cleanup, and feature-wide evidence.

- [X] T047 [P] Run the complete focused YT-209 validation command `python3 -m pytest tests/unit/test_youtube_channel_banners.py tests/contract/test_youtube_channel_banners_contract.py tests/integration/test_youtube_channel_banners_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix failures in the touched files.
- [X] T048 [P] Run MCP discovery and routing guard tests `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py` from `/Users/ctgunn/Projects/youtube-mcp-server` if `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` or `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` changed.
- [X] T049 [P] Run Layer 1 guard tests `python3 -m pytest tests/contract/test_layer1_channel_banners_contract.py tests/unit/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server` if `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py` or `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channel_banners.py` changed.
- [X] T050 Review all changed public metadata, examples, errors, and logs for secret and raw-media safety in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`.
- [X] T051 Review every new or modified Python function for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and touched files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`.
- [X] T052 Run the quickstart validation checklist from `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/quickstart.md`.
- [X] T053 Run the full repository test suite `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failure before considering YT-209 complete.
- [X] T054 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every lint finding before considering YT-209 complete.
- [X] T055 Update implementation evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/quickstart.md` with focused test, full-suite, lint, safety-review, and docstring-review outcomes.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational; delivers the MVP executable tool.
- **User Story 2 (Phase 4)**: Depends on Foundational and can be developed after or alongside US1 if file edits are coordinated, but it is easiest after US1 creates the concrete tool contract.
- **User Story 3 (Phase 5)**: Depends on Foundational and can be developed after or alongside US1 if file edits are coordinated, but it is easiest after US1 creates the concrete validator and handler.
- **Polish (Phase 6)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on US2 or US3 after Foundational; establishes the executable `channelBanners_insert` MVP.
- **US2 (P2)**: Depends on the `channelBanners_insert` contract surface created by US1 for simplest execution; remains independently testable through discovery and metadata.
- **US3 (P3)**: Depends on the `channelBanners_insert` validator and handler created by US1 for simplest execution; remains independently testable through invalid request and error-mapping checks.

### Within Each User Story

- Red tests must be written and run before implementation.
- Green implementation must be the minimum code required to pass that story's tests.
- reStructuredText docstrings must be added or updated before a story is marked complete.
- Refactor only after tests pass; rerun the affected focused test command afterward.
- Final completion requires `python3 -m pytest` and `python3 -m ruff check .` after the last code change.

### Parallel Opportunities

- Setup review tasks T002, T003, T004, and T005 can run in parallel.
- Foundational test module tasks T008, T009, and T010 can be created in parallel because they touch different test files.
- US1 red tests T012, T013, and T014 can be written in parallel because they touch different test files.
- US2 red tests T024, T025, T026, and T027 can be written in parallel because they touch different test files.
- US3 red tests T036, T037, T038, and T039 can be split by test file, with coordination for shared edits to `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py`.
- Polish guard runs T047, T048, and T049 can run in parallel when their file-change conditions apply.

---

## Parallel Example: User Story 1

```bash
# Launch Red test-writing work in parallel:
Task: "T012 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py"
Task: "T013 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_banners.py"
Task: "T014 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_banners_registration.py"
```

## Parallel Example: User Story 2

```bash
# Launch metadata Red test-writing work in parallel:
Task: "T024 [US2] Add channel-banner contract metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py"
Task: "T025 [US2] Add shared metadata safety checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T026 [US2] Add representative catalog checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T027 [US2] Add default discovery checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
# Launch validation/error Red test-writing work in parallel:
Task: "T036 [US3] Add validation parameter cases in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_banners_contract.py"
Task: "T037 [US3] Add unit validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_banners.py"
Task: "T039 [US3] Add dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_banners_registration.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup review.
2. Complete Phase 2 foundational red checks.
3. Complete Phase 3 US1 to add executable `channelBanners_insert` with upload result mapping.
4. Stop and validate US1 independently with `python3 -m pytest tests/contract/test_youtube_channel_banners_contract.py tests/unit/test_youtube_channel_banners.py tests/integration/test_youtube_channel_banners_registration.py`.

### Incremental Delivery

1. Add US1 for the executable banner upload tool and basic upload result.
2. Add US2 for complete quota/auth/media/delegation/returned-URL metadata visibility.
3. Add US3 for invalid request and upstream error mapping.
4. Finish Phase 6 with focused validation, full-suite validation, lint, quickstart evidence, safety review, and docstring review.

### Parallel Team Strategy

With multiple workers:

1. Complete Setup and Foundational together.
2. Assign US1 implementation ownership to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the US1 tests.
3. Assign US2 metadata ownership to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` and metadata assertions after US1 creates the concrete contract.
4. Assign US3 validation/error ownership to `channelBanners_insert` validation and error mapping after US1 creates the concrete validator and handler.

---

## Notes

- `[P]` tasks touch different files or are read-only and can run in parallel within the phase.
- `[US1]`, `[US2]`, and `[US3]` labels map tasks to prioritized user stories from `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/spec.md`.
- Tests must fail before implementation for each story.
- Avoid adding persistence, hosted transport changes, image resizing, preview generation, active banner publication, channel metadata update, bulk channel operations, enrichment, or heuristic behavior.
- Do not expose API keys, OAuth tokens, stack traces, signed URLs, raw image payloads, binary payloads, private channel data, or secret values in public metadata, examples, errors, docs, tests, or logs.
