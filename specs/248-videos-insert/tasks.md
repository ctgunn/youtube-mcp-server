# Tasks: Layer 2 Tool `videos_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/contracts/videos_insert.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/quickstart.md`

**Tests**: Test tasks are required. Every user story and foundational change includes Red-Green-Refactor coverage. Completion requires a passing full repository test-suite run after the final code changes. Python changes must include reStructuredText docstrings for every new or modified function.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup

**Purpose**: Confirm feature scope, existing implementation seams, and task inputs before writing Red tests.

- [X] T001 Review the YT-248 design artifacts in `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/contracts/videos_insert.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/quickstart.md`
- [X] T002 Inspect the existing Layer 2 videos and dispatcher seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T003 [P] Inspect the existing Layer 1 videos insert dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/videos.py`
- [X] T004 [P] Inspect existing videos-focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`

---

## Phase 2: Foundational

**Purpose**: Add shared Red tests and shared registration expectations that block all user stories.

**Critical**: No user story implementation should begin until these shared failing expectations exist.

- [X] T005 [P] Add failing shared export expectations for `VIDEOS_INSERT_*`, `VideosInsertToolError`, `build_videos_insert_contract`, `build_videos_insert_handler`, `build_videos_insert_tool_descriptor`, `map_videos_insert_result`, and `validate_videos_insert_arguments` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T006 [P] Add failing shared contract and safe metadata expectations for the concrete `videos_insert` contract in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T007 [P] Add failing public catalog expectations proving `videos_insert` appears with quota `1600`, OAuth-required auth, media-constrained availability, and safe examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T008 Add failing default registry discovery expectations for `videos_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T009 Add a temporary Red evidence note for the failing shared tests in `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/quickstart.md`

**Checkpoint**: Foundational Red tests exist for exports, shared contract metadata, catalog presence, and default registry discovery.

---

## Phase 3: User Story 1 - Create Videos Through a Public Endpoint Tool (Priority: P1)

**Goal**: A caller with eligible OAuth can invoke `videos_insert` with valid `part`, `body`, and `media`, and receive a near-raw created video result.

**Independent Test**: Invoke `videos_insert` through the descriptor or dispatcher with a fake Layer 1 wrapper, valid OAuth context, metadata body, and test-safe media descriptor; verify one Layer 1 call and a created-resource result with endpoint, quota, requested parts, upload context, access context, availability context, mutation details, and returned video fields.

### Tests for User Story 1

- [X] T010 [P] [US1] Add failing contract tests for `videos_insert` required `part`, `body`, `media`, upload-result convention, created-resource response boundary, and callable descriptor shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T011 [P] [US1] Add failing unit tests for valid authorized `videos_insert` argument normalization, upload context extraction, result mapping, and fake wrapper invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T012 [P] [US1] Add failing integration tests for dispatcher invocation of a valid authorized `videos_insert` request and preservation of created video fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`

### Implementation for User Story 1

- [X] T013 [US1] Define `VIDEOS_INSERT_TOOL_NAME`, `VIDEOS_INSERT_QUOTA_COST`, `VIDEOS_INSERT_UPLOAD_MODES`, `VIDEOS_INSERT_ALLOWED_FIELDS`, `VIDEOS_INSERT_INPUT_SCHEMA`, and created-resource description constants in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T014 [US1] Implement `VideosInsertToolError`, safe error-detail sanitization, `part` normalization, metadata body validation, media descriptor validation, upload-mode validation, and upload-context helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T015 [US1] Implement `map_videos_insert_result` to preserve `endpoint`, `quotaCost`, `requestedParts`, safe `upload`, `auth`, `availability`, optional `delegation`, `item`, `mutation`, and returned upstream video fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T016 [US1] Implement `validate_videos_insert_arguments`, `build_videos_insert_contract`, `build_videos_insert_handler`, and `build_videos_insert_tool_descriptor` using the existing `build_videos_insert_wrapper()` dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T017 [US1] Export `videos_insert` constants, error class, builders, validator, and result mapper from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T018 [US1] Register `build_videos_insert_tool_descriptor()` in the default tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T019 [US1] Add or update reStructuredText docstrings for all new or changed `videos_insert` functions and fake wrapper methods in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T020 [US1] Run focused User Story 1 tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T021 [US1] Refactor the `videos_insert` success path for minimal duplication with existing upload/mutation helpers while keeping User Story 1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 1 is independently functional as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, Upload, and Availability Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, descriptions, usage notes, caveats, and examples to understand `videos.insert`, quota cost `1600`, OAuth-only access, media-upload requirements, upload modes, delegation, availability caveats, and out-of-scope behavior before invocation.

**Independent Test**: Review the public descriptor and contract for `videos_insert`; verify all caller-facing text and examples expose cost, auth, upload, availability, and response boundaries without implementation-only artifacts.

### Tests for User Story 2

- [X] T022 [P] [US2] Add failing contract tests for `VIDEOS_INSERT_DESCRIPTION`, `VIDEOS_INSERT_USAGE_NOTES`, `VIDEOS_INSERT_CAVEATS`, `VIDEOS_INSERT_CALLER_EXAMPLES`, quota `1600`, OAuth-required auth, media-constrained availability, and out-of-scope wording in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T023 [P] [US2] Add failing catalog tests proving shared examples include the concrete `videos_insert` contract with safe metadata and caller-facing examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T024 [P] [US2] Add failing integration tests proving dispatcher `list_tools()` exposes `videos_insert` metadata, usage notes, examples, quota, auth mode, and availability state in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`

### Implementation for User Story 2

- [X] T025 [US2] Populate `VIDEOS_INSERT_DESCRIPTION`, `VIDEOS_INSERT_USAGE_NOTES`, `VIDEOS_INSERT_CAVEATS`, and `VIDEOS_INSERT_CALLER_EXAMPLES` with authorized creation, resumable upload, delegated content owner, metadata-only failure, media-only failure, missing OAuth failure, unsupported upload mode failure, quota or upstream failure, availability-constrained behavior, and out-of-scope workflow examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T026 [US2] Extend `build_videos_insert_contract()` metadata with upstream identity, quota cost `1600`, OAuth-required auth, media-constrained availability, response convention, response boundary, error categories, usage notes, and caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T027 [US2] Add the concrete `build_videos_insert_contract()` entry to the shared YouTube tool catalog examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T028 [US2] Ensure `build_videos_insert_tool_descriptor()` includes safe metadata and examples for public discovery in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T029 [US2] Add or update reStructuredText docstrings for all metadata, contract, descriptor, and example functions changed for `videos_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T030 [US2] Run focused User Story 2 metadata and catalog tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T031 [US2] Refactor duplicated quota, OAuth, media-upload, delegation, availability, and out-of-scope wording while keeping User Story 2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata, tool contract, and examples.

---

## Phase 5: User Story 3 - Reject Unsupported Video Creation Requests Clearly (Priority: P3)

**Goal**: A caller receives safe, specific validation or failure feedback for missing inputs, malformed upload requests, missing OAuth, insufficient authorization, quota or availability failures, and out-of-scope workflows.

**Independent Test**: Submit representative invalid requests and fake upstream failures to `videos_insert`; verify each outcome is categorized with safe caller-facing guidance and no secret, raw media, signed URL, stack trace, or unsafe upstream detail leakage.

### Tests for User Story 3

- [X] T032 [P] [US3] Add failing unit tests for missing `part`, empty or non-string `part`, missing `body`, incomplete `body`, missing `media`, incomplete `media`, metadata-only request, media-only request, unsupported `uploadMode`, invalid `notifySubscribers`, invalid delegation, unsupported fields, and missing OAuth in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T033 [P] [US3] Add failing contract tests for safe error categories, validation failure examples, policy or availability caveats, and no raw media or secret-bearing public metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T034 [P] [US3] Add failing integration tests for dispatcher rejection of missing media, missing body, missing OAuth, unsupported upload mode, and unsafe error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T035 [P] [US3] Add failing shared regression tests for unsupported publishing, update, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 3

- [X] T036 [US3] Tighten `validate_videos_insert_arguments()` to reject missing, malformed, unsupported, metadata-only, media-only, unsupported upload-mode, invalid optional field, invalid delegation, and out-of-scope workflow requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T037 [US3] Implement OAuth preflight and access-context behavior for `videos_insert`, including `authentication_failed` for missing OAuth and `authorization_failed` for insufficient delegated or upload access in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T038 [US3] Implement upstream failure mapping for quota, authorization, policy, invalid request, upload, unavailable endpoint, deprecated endpoint, availability constraint, resource-not-found, and unexpected failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T039 [US3] Ensure safe error-detail sanitization removes API keys, OAuth tokens, authorization headers, raw media payloads, signed URLs, raw upstream diagnostics, stack traces, raw request context, and secret-bearing details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T040 [US3] Add or update reStructuredText docstrings for all validation, OAuth, failure-mapping, and sanitization functions changed for `videos_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T041 [US3] Run focused User Story 3 validation, error, and regression tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T042 [US3] Refactor invalid-request and safe-error helpers while keeping User Story 3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 3 is independently testable through invalid request, missing auth, upstream failure, and unsafe-detail regression cases.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete cross-story verification, documentation reconciliation, and quality checks.

- [X] T043 [P] Reconcile implemented behavior with `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/contracts/videos_insert.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/quickstart.md`
- [X] T044 [P] Add any remaining cross-story regression coverage for `videos_insert` discovery, metadata, validation, safe errors, default registration, and catalog presence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T045 Review every new or changed Python function for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T046 Run focused YT-248 verification and fix failures using `pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T047 Run Layer 1 guard verification if Layer 1 files changed and fix failures using `pytest tests/contract/test_layer1_videos_contract.py tests/unit/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T048 Run code-quality verification and fix failures using `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T049 Run the full repository test suite and fix any failures using `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T050 Record final Red-Green-Refactor, focused verification, full-suite verification, lint verification, and docstring evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/248-videos-insert/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 Setup has no dependencies.
- Phase 2 Foundational depends on Phase 1 and blocks all user stories.
- Phase 3 User Story 1 depends on Phase 2 and is the MVP.
- Phase 4 User Story 2 depends on Phase 2 and can proceed independently after shared descriptor seams exist, though it benefits from User Story 1 metadata builders.
- Phase 5 User Story 3 depends on Phase 2 and can proceed independently after shared error and validation seams exist, though it benefits from User Story 1 handler builders.
- Phase 6 Polish depends on all selected user stories.

### User Story Dependencies

- User Story 1 (P1): Can start after Foundational and delivers the executable creation path.
- User Story 2 (P2): Can start after Foundational; independently testable through discovery metadata and examples.
- User Story 3 (P3): Can start after Foundational; independently testable through validation and safe failure behavior.

### Within Each User Story

- Red tests must be written and observed failing before implementation tasks begin.
- Constants and schema precede validators, contract builders, handlers, descriptors, exports, and registration.
- Python implementation precedes docstring review and focused story verification.
- Refactor only after focused tests pass, then re-run affected tests.
- The full repository test suite must pass before the feature is complete.

## Parallel Opportunities

- T003 and T004 can run in parallel after T001.
- T005, T006, and T007 can run in parallel because they touch different test files.
- T010, T011, and T012 can run in parallel for User Story 1 Red coverage.
- T022, T023, and T024 can run in parallel for User Story 2 Red coverage.
- T032, T033, T034, and T035 can run in parallel for User Story 3 Red coverage.
- T043 and T044 can run in parallel during polish because one reconciles docs while the other fills test gaps.

## Parallel Example: User Story 1

```text
Task: "T010 [P] [US1] Add failing contract tests for videos_insert in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T011 [P] [US1] Add failing unit tests for videos_insert in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T012 [P] [US1] Add failing integration tests for videos_insert in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
```

## Parallel Example: User Story 2

```text
Task: "T022 [P] [US2] Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T023 [P] [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T024 [P] [US2] Add failing discovery integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
```

## Parallel Example: User Story 3

```text
Task: "T032 [P] [US3] Add failing validation unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T033 [P] [US3] Add failing safe-error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T034 [P] [US3] Add failing dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
Task: "T035 [P] [US3] Add failing out-of-scope catalog regression tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational Red tests.
3. Complete Phase 3 User Story 1.
4. Validate the MVP with focused videos contract, unit, and integration tests.
5. Stop for review if only executable video creation is needed.

### Incremental Delivery

1. Deliver User Story 1 for executable authorized video creation.
2. Deliver User Story 2 for public metadata, examples, quota, OAuth, upload, and availability clarity.
3. Deliver User Story 3 for robust invalid request, access, quota, upload, availability, and upstream failure handling.
4. Complete Phase 6 with focused verification, lint, full-suite validation, and review evidence.

### Parallel Team Strategy

1. Complete Phase 1 and Phase 2 together.
2. Split Red test work by file using the tasks marked `[P]`.
3. Assign one implementer to `src/mcp_server/tools/youtube_common/videos.py` at a time to avoid write conflicts.
4. Assign separate reviewers to exports/registration, catalog examples, and verification evidence once the core module stabilizes.

## Task Summary

- Total tasks: 50
- Setup tasks: 4
- Foundational tasks: 5
- User Story 1 tasks: 12
- User Story 2 tasks: 10
- User Story 3 tasks: 11
- Polish tasks: 8
- Suggested MVP scope: Phase 1, Phase 2, and Phase 3 User Story 1
