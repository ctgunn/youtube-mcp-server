# Tasks: YT-160 Layer 1 Live Calls for Discovery, Video, and Branding Resources

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/data-model.md), and [live-call contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/contracts/layer1-discovery-video-branding-live-call-contract.md)

**Tests**: Test tasks are mandatory. Every changed Python function requires a reStructuredText docstring with purpose, parameters, return value, relevant raised errors, and side effects. Completion requires `python3 -m pytest` and `python3 -m ruff check .` to pass from `/Users/ctgunn/Projects/youtube-mcp-server` after the final code change.

**Organization**: Tasks are grouped by independently testable user story. Existing shared runtime, transport, normalizers, retries, and observability are reused. YT-160 completion work adds shared OAuth refresh and Google upload protocol behavior without a new public tool, resource-family client, or persistent credential store.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the contract baseline and record current behavior before code changes.

- [X] T001 Review the configured-runtime dependency, operation/authentication matrix, media scope, and no-fallback rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/contracts/layer1-discovery-video-branding-live-call-contract.md`.
- [X] T002 Run the existing live-runtime baseline checks from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_live_runtime.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`, then record that pre-retrofit YT-160 descriptors still select local representative defaults.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Confirm the reusable YT-157 runtime/transport test seam before wiring any affected descriptor.

- [X] T003 Run the controlled-opener, credential-redaction, retry, malformed-response, and missing-credential checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` to preserve the shared foundation used by every story.

**Checkpoint**: The existing configured runtime, common transport, and controlled-opener test seam are verified. User-story work may begin; every dispatcher edit remains serialized because it changes `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

---

## Phase 3: User Story 1 - Receive Live Discovery and Video Results (Priority: P1) 🎯 MVP

**Goal**: Configured search, video lookup, video-category, and video-abuse-reason requests return live normalized outcomes instead of representative defaults while preserving their public contracts.

**Independent Test**: Build an app with a configured API key and controlled opener, invoke `search_list`, `videoAbuseReportReasons_list`, `videoCategories_list`, and `videos_list`, and verify each makes one expected live request with a distinctive normalized result; invalid or missing-credential paths must not call the opener or return representative data.

### Tests for User Story 1 (Red)

- [X] T004 [US1] Add failing parameterized configured-runtime request tests for `search_list`, `videoAbuseReportReasons_list`, `videoCategories_list`, and API-key `videos_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`; assert executor capture, path, method, API-key placement, distinctive live result, and no representative fallback.
- [X] T005 [P] [US1] Add failing public-contract preservation assertions for configured discovery/video descriptor metadata, schemas, validation, normalized errors, and safe details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_abuse_report_reasons_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_video_categories_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`.

### Implementation for User Story 1 (Green)

- [X] T006 [US1] Pass `conditional_dependencies` to `build_search_list_tool_descriptor` and `build_videos_list_tool_descriptor`, and `api_key_dependencies` to the video-abuse-reason and video-category descriptor builders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T007 [US1] Add or update reStructuredText docstrings for every modified dispatcher and test function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.

### Refactor and Story Validation

- [X] T008 [US1] Refactor duplicated controlled-request assertions while retaining the existing shared runtime/transport boundary, then run the P1 unit, contract, and integration checks named in `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/quickstart.md` for search, video abuse reasons, video categories, videos, and live runtime.

**Checkpoint**: The P1 discovery and video-read MVP is independently usable through configured public tools with preserved contracts and safe failures.

---

## Phase 4: User Story 2 - Perform Authorized Video and Subscription Changes (Priority: P2)

**Goal**: Authorized subscription, thumbnail, video-mutation/rating, and watermark operations reach the shared live executor, apply the declared credential mode, and preserve safe outcomes.

**Independent Test**: Build an app with configured API-key and OAuth access plus a controlled opener; invoke `subscriptions_list`, subscription mutations, `thumbnails_set`, six OAuth video operations, and watermark operations; verify target/method, credential location, JSON/raw-media/multipart form where applicable, normalized result, and secret-free normalized failures.

### Tests for User Story 2 (Red)

- [X] T009 [US2] Add failing table-driven configured-runtime request, missing-credential, and normalized-upstream-failure tests for `subscriptions_list`, `subscriptions_insert`, `subscriptions_delete`, `thumbnails_set`, `videos_insert`, `videos_update`, `videos_rate`, `videos_getRating`, `videos_reportAbuse`, `videos_delete`, `watermarks_set`, and `watermarks_unset` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.
- [X] T010 [P] [US2] Add failing contract-preservation assertions for conditional subscription access, OAuth-only mutations, media safety, safe error categories, and unchanged metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`.

### Implementation for User Story 2 (Green)

- [X] T011 [US2] Pass `conditional_dependencies` to `build_subscriptions_list_tool_descriptor` and `oauth_dependencies` to subscription mutation, thumbnail, six OAuth video-operation, and watermark descriptor builders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`; preserve existing raw-media/multipart serialization in the shared transport.
- [X] T012 [US2] Add or update reStructuredText docstrings for every modified dispatcher and test function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.

### Refactor and Story Validation

- [X] T013 [US2] Consolidate operation-table fixtures and remove temporary branches without adding a resource-specific transport, then run the P2 unit, contract, and integration checks named in `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/quickstart.md` for subscriptions, thumbnails, videos, watermarks, and live runtime.

**Checkpoint**: Authorized management operations are independently testable against controlled live execution, retain existing contracts, and never substitute representative data for a safe failure.

---

## Phase 5: User Story 3 - Reach Live Wrappers Through Existing Public Tools (Priority: P3)

**Goal**: The existing low-level search and video tools plus the higher-level video-detail tool all reach the configured live wrapper path.

**Independent Test**: With a configured API key and controlled opener, invoke `search_list`, `videos_list`, and `videos_getVideo`; verify all capture a common live executor request, and verify a controlled upstream failure is normalized without a direct bypass, local default, credential leak, or representative response.

### Tests for User Story 3 (Red)

- [X] T014 [US3] Add a failing configured `videos_getVideo` flow that proves its lower-level lookup captures the configured executor and produces the expected live `/youtube/v3/videos` request and safe normalized upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.
- [X] T015 [P] [US3] Add failing regression assertions for the existing `videos_getVideo` lower-layer `videos.list` dependency, normalized result shape, error translation, and no-representative marker in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Implementation for User Story 3 (Green)

- [X] T016 [US3] Build a `videos.list` lookup with the configured conditional dependencies and pass it as `lookup` to `build_videos_get_video_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`; do not add direct YouTube requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.
- [X] T017 [US3] Add or update reStructuredText docstrings for every modified dispatcher and composed-video test function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Refactor and Story Validation

- [X] T018 [US3] Refactor the injected lookup and shared controlled-opener assertions for readability while retaining public-tool schemas and error mapping, then run `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.

**Checkpoint**: All three named public flows are independently demonstrable through the configured live path; `videos_getVideo` composes the configured `videos.list` handler and does not bypass Layer 1.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete safety, documentation, verification, and final regression work across all stories.

- [X] T019 [P] Audit configured request/error/log fixtures for API keys, OAuth tokens, bearer headers, credential-bearing URLs, raw body/media, stack traces, and representative fallbacks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.
- [X] T020 [P] Validate the controlled-opener and manual-verification instructions against the completed test commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/quickstart.md`.
- [X] T021 Audit all changed Python functions for complete reStructuredText docstrings with `:param:`, `:return:`, `:raises:` where applicable, and side-effect documentation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.
- [X] T022 Run the complete focused verification matrix from `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/quickstart.md` in `/Users/ctgunn/Projects/youtube-mcp-server` and resolve every focused-test failure.
- [X] T023 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` after the final code changes and fix every failure before declaring the feature complete.
- [X] T024 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` after T023 and fix every lint failure before declaring the feature complete.

---

## Phase 7: Live Execution Completion Gate

**Purpose**: Close the cross-cutting runtime gaps identified after the original 16-operation wiring retrofit, while retaining deterministic verification and safe credential handling.

- [X] T025 Add safe API-key/OAuth capability readiness reporting in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/health.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py` with unit and integration coverage.
- [X] T026 Add static-or-refreshable OAuth credential support, in-memory access-token caching, and safe refresh failure behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/oauth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_oauth.py`.
- [X] T027 Route direct media requests through Google's `/upload/youtube/v3/...` endpoint with `uploadType=media` or `uploadType=multipart` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` and prove all supported media forms in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`.
- [X] T028 Implement and test `videos.insert` resumable-session initialization, bounded 256 KiB-aligned chunk transfer, `308` progression, and committed-range recovery in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`.
- [X] T029 Add bounded exponential backoff for idempotent methods and prohibit automatic POST mutation replay in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/retry.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`.
- [X] T030 Add the opt-in read-only real API smoke command and pytest guard in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py`, and document static/renewable OAuth setup in `/Users/ctgunn/Projects/youtube-mcp-server/.env.example` and `/Users/ctgunn/Projects/youtube-mcp-server/README.md`.
- [X] T031 Update all YT-160 Markdown artifacts for the final shared live-execution scope and run `python3 -m pytest`, `python3 -m ruff check .`, and `git diff --check` from `/Users/ctgunn/Projects/youtube-mcp-server`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; establishes the contract and behavior baseline.
- **Foundational (Phase 2)**: Depends on Setup; verifies the existing configured-runtime test seam before any descriptor wiring.
- **User Story 1 (Phase 3)**: Depends on Phase 2; delivers the MVP live read/discovery path.
- **User Story 2 (Phase 4)**: Depends on Phase 2 and T006 because it extends the same dispatcher method; it remains independently testable after its own descriptor calls are added.
- **User Story 3 (Phase 5)**: Depends on T006 because it composes the configured `videos.list` path; it may proceed after P1 and independently validates the composed public flow.
- **Polish (Phase 6)**: Depends on all desired stories being complete.

### User Story Completion Order

```text
Phase 1 Setup → Phase 2 Runtime seam
                    └─→ US1 (P1: discovery/video reads) ─→ US3 (P3: public-tool composition)
                    └─→ US2 (P2: authorized mutations; serialized after US1 only for dispatcher.py edits)
US1 + US2 + US3 → Polish and full-suite verification
```

### Parallel Opportunities

- T004 and T005 can run in parallel because their integration and contract test files differ.
- T009 and T010 can run in parallel because their integration and contract test files differ.
- T014 and T015 can run in parallel because their live-runtime and composed-tool test files differ.
- T019 and T020 can run in parallel because they audit different files.
- Source edits T006, T011, and T016 are deliberately sequential because each edits `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

## Parallel Execution Examples

### User Story 1

```text
Task: "T004 Add configured discovery/video live-runtime tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py"
Task: "T005 Add contract preservation assertions in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py and related discovery/video contract files"
```

### User Story 2

```text
Task: "T009 Add authorized mutation live-runtime tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py"
Task: "T010 Add subscription, media, and video contract assertions in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py and related contract files"
```

### User Story 3

```text
Task: "T014 Add configured videos_getVideo flow coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py"
Task: "T015 Add composed-video contract and registration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete T004 through T008.
3. Verify configured `search_list`, `videoAbuseReportReasons_list`, `videoCategories_list`, and `videos_list` with controlled openers.
4. Stop and validate P1 independently before moving to authorized mutation or composed-detail work.

### Incremental Delivery

1. Complete Setup and foundational verification.
2. Add User Story 1 and validate live read/discovery behavior (MVP).
3. Add User Story 2 and validate authorized mutation/media behavior without altering P1 contracts.
4. Add User Story 3 and validate composed public-tool routing through the live lower-level video path.
5. Complete polish and full-suite verification only after all desired stories remain independently valid.

### Task Format Validation

- All 31 tasks use the required `- [ ] T### [P?] [US#?] Description with absolute path` checklist format.
- Every user-story task carries exactly one story label; Setup, Foundational, and Polish tasks carry no story label.
- `[P]` appears only on tasks that modify different files from their concurrently runnable companion task.
