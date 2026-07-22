# Tasks: Layer 2 Tool `videos_rate`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/data-model.md), [contracts/videos_rate.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/contracts/videos_rate.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/plan.md`
- [X] T002 Inspect the existing Layer 1 `videos.rate` wrapper and validator dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py`
- [X] T003 [P] Inspect existing `videos_list`, `videos_insert`, and `videos_update` Layer 2 implementation patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T004 [P] Inspect existing mutation acknowledgment patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect existing videos-focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, catalog expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until this phase is complete and Red checks have been observed failing for the missing `videos_rate` surface.

- [X] T007 [P] Add Red public export checks for `VIDEOS_RATE_TOOL_NAME`, `VIDEOS_RATE_QUOTA_COST`, `VIDEOS_RATE_INPUT_SCHEMA`, `VideosRateToolError`, `build_videos_rate_contract`, `build_videos_rate_handler`, `build_videos_rate_tool_descriptor`, `map_videos_rate_result`, and `validate_videos_rate_arguments` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `videos` family exposes a concrete `videos_rate` descriptor beside `videos_list`, `videos_insert`, and `videos_update` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `videos_rate` appears once with resource family `videos`, quota cost `50`, OAuth-required auth, and `mutation_acknowledgment` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `videos_rate` is discoverable through the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red videos-family registration checks for `videos_rate` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T012 Add shared fake rate wrapper, fake no-content executor, OAuth helper, and upstream failure helpers for videos rate tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T013 Run foundational Red checks and record the failing command evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/quickstart.md`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Rate Videos Through a Public Endpoint Tool (Priority: P1) MVP

**Goal**: A caller with eligible OAuth can invoke `videos_rate` with valid `id` and supported `rating`, then receive a structured mutation acknowledgment.

**Independent Test**: Invoke the tool handler with `{"id": "abc123", "rating": "like"}`, `{"id": "abc123", "rating": "dislike"}`, and `{"id": "abc123", "rating": "none"}` using a fake Layer 1 wrapper and OAuth context; verify one wrapper call per request and a result containing `endpoint: videos.rate`, `quotaCost: 50`, rating context, auth context, availability state, status/no-content context, and mutation acknowledgment details.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `videos_rate` tool identity, input schema, upstream identity, quota cost `50`, OAuth-required auth mode, mutation acknowledgment response convention, near-raw response boundary, and executable descriptor shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_videos_rate_arguments`, rating context extraction, `map_videos_rate_result`, `build_videos_rate_handler`, and `rating=none` clear-rating behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T016 [P] [US1] Add integration tests proving `videos_rate` is registered and callable through the videos family registry with valid authorized `like`, `dislike`, and `none` rating requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing `videos_rate` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Add `build_videos_rate_wrapper` imports and rate-specific support imports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T019 [US1] Define `VIDEOS_RATE_TOOL_NAME`, `VIDEOS_RATE_QUOTA_COST`, supported rating constants, unsafe-detail keys, and `VIDEOS_RATE_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T020 [US1] Implement `VideosRateToolError` and safe error detail sanitization for video-rating failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T021 [US1] Implement `validate_videos_rate_arguments` requiring non-empty `id`, supported `rating` values `like`, `dislike`, or `none`, and no unsupported top-level fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T022 [US1] Implement target identity, rating-state context, clear-rating context, and no-request-body helpers for `videos_rate` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T023 [US1] Implement OAuth auth context selection for `videos_rate` and reject API-key-only execution before Layer 1 wrapper calls in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T024 [US1] Implement `map_videos_rate_result` to return endpoint, quota cost `50`, rating context, auth context, availability state, no-content status context, and mutation type `rated` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T025 [US1] Implement `build_videos_rate_handler` using the Layer 1 rate wrapper once per valid call with OAuth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T026 [US1] Implement `build_videos_rate_contract` and `build_videos_rate_tool_descriptor` with mutation acknowledgment metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T027 [US1] Export `videos_rate` constants, error class, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T028 [US1] Register `build_videos_rate_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T030 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper, fake executor, OAuth helper, or upstream failure helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T031 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T032 [US1] Refactor US1 video-rate execution code for consistency with existing Layer 2 mutation acknowledgment helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Quota, OAuth, and Rating Semantics Before Calling (Priority: P2)

**Goal**: A client developer can inspect `videos_rate` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `50`, OAuth-only access, required `id`, required `rating`, supported actions, clear-rating semantics, no-request-body behavior, acknowledgment result shape, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `videos.rate`, quota cost `50`, OAuth-required access, required `id`, required `rating`, supported `like`, `dislike`, and `none`, `none` clear-rating semantics, no request body, active mutation availability, acknowledgment result shape, and no lookup/history/count/update/upload/delete/analytics/ranking/summarization/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T033 [P] [US2] Add contract tests for `VIDEOS_RATE_DESCRIPTION`, `VIDEOS_RATE_USAGE_NOTES`, `VIDEOS_RATE_CAVEATS`, `VIDEOS_RATE_CALLER_EXAMPLES`, quota visibility, OAuth visibility, rating-action visibility, no-body visibility, acknowledgment visibility, response boundary, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T034 [P] [US2] Add catalog contract tests confirming `videos_rate` metadata exposes quota cost `50`, OAuth-required auth, required identity/rating inputs, rating-state boundaries, clear-rating behavior, no-body rules, active availability, and out-of-scope behavior before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `videos_rate` without replacing `videos_list`, `videos_insert`, or `videos_update` resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T036 [P] [US2] Add integration tests proving default registry metadata preserves `videos_rate` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T037 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T038 [US2] Add `VIDEOS_RATE_DESCRIPTION`, `VIDEOS_RATE_USAGE_NOTES`, and `VIDEOS_RATE_CAVEATS` with quota cost `50`, OAuth-only access, required identity/rating inputs, supported rating actions, clear-rating semantics, no-body guidance, safe acknowledgment boundary, and out-of-scope guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T039 [US2] Add `VIDEOS_RATE_CALLER_EXAMPLES` covering authorized `like`, authorized `dislike`, authorized `none`, missing identity failure, missing rating failure, unsupported rating failure, request body failure, missing OAuth failure, quota or upstream failure, non-ratable target failure, not-found failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T040 [US2] Update `build_videos_rate_contract` and `build_videos_rate_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, OAuth details, rating-state details, no-body details, acknowledgment details, and safe failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T041 [US2] Update shared examples or catalog entries so `videos_rate` appears as a concrete endpoint-backed contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T042 [US2] Update `videos_rate` export coverage for caller-facing metadata and example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T043 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T044 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T045 [US2] Refactor US2 metadata and example wording for consistency with existing mutation tools while preserving quota, OAuth, rating-state, clear-rating, no-request-body, acknowledgment, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid or Unsupported Rating Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation or failure feedback for missing identity, missing rating, unsupported rating, request body, missing OAuth, insufficient authorization, not-found, quota, disabled rating, policy, unavailable, deprecated, unexpected-upstream, and out-of-scope workflow cases.

**Independent Test**: Submit missing `id`, empty `id`, non-string `id`, missing `rating`, empty `rating`, non-string `rating`, unsupported `rating`, differently cased `rating`, supplied `body`, unsupported fields, lookup/history/count/update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields, missing OAuth, insufficient OAuth, not-found, quota, disabled rating, purchase-required, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category and sanitized details.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T046 [P] [US3] Add unit validation tests for missing `id`, empty or non-string `id`, missing `rating`, empty or non-string `rating`, unsupported `rating`, differently cased `rating`, and `rating=none` distinct from omitted `rating` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T047 [P] [US3] Add unit validation tests for supplied `body`, unsupported top-level fields, aliases, delegated modifiers, current-rating lookup fields, rating history fields, aggregate count fields, and out-of-scope update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T048 [P] [US3] Add unit handler tests for missing OAuth, invalid auth mode, wrapper call prevention on access failure, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T049 [P] [US3] Add unit result and upstream error mapping tests for quota failure, upstream invalid rating, unverified email, purchase-required refusal, authorization failure, forbidden or policy failure, disabled rating, target video not found, endpoint unavailable, deprecated endpoint, no-content success, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T050 [P] [US3] Add contract tests proving failure examples cover invalid request, missing OAuth, quota/upstream failure, not-found failure, forbidden or policy failure, disabled rating, deprecated behavior, endpoint unavailable, no-content success, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T051 [P] [US3] Add integration tests for dispatcher rejection of missing identity, missing rating, unsupported rating, request body, missing OAuth, out-of-scope lookup field, and unsafe error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T052 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T053 [US3] Extend `validate_videos_rate_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, duplicated, ambiguous, or malformed `id` values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T054 [US3] Extend `validate_videos_rate_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, unsupported, differently cased, duplicated, or conflicting `rating` values while preserving explicit `none` semantics in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T055 [US3] Extend `validate_videos_rate_arguments` to reject request bodies, unsupported top-level fields, aliases, delegated modifiers, and out-of-scope lookup/history/count/update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T056 [US3] Implement missing or invalid OAuth access rejection for `videos_rate` before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T057 [US3] Implement insufficient OAuth, unverified email, purchase-required, forbidden, policy, disabled rating, or non-ratable target mapping for `videos_rate` with sanitized `authorization_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T058 [US3] Implement upstream error mapping for quota, invalid request, invalid rating, authorization, forbidden, policy, disabled rating, resource not found, unavailable endpoint, deprecated endpoint, availability constraint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T059 [US3] Ensure video-rate result mapping preserves no-content success acknowledgment without fabricating refreshed video metadata, current-rating lookup results, rating history, aggregate counts, analytics, recommendations, rankings, summaries, or enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T060 [US3] Ensure video-rate error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, unsafe request context, and secret-bearing details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

### Refactor and Validation for User Story 3

- [X] T061 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T062 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper, fake executor, auth helper, or upstream failure helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T063 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T064 [US3] Refactor US3 validation and error mapping for consistency with existing mutation helpers while preserving videos-rate-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, not-found, quota, disabled-rating, availability, deprecation, and upstream failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T065 [P] Review `videos_rate` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/contracts/videos_rate.md`
- [X] T066 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/quickstart.md`
- [X] T067 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T068 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T069 [P] Add any remaining cross-story regression coverage for `videos_rate` discovery, metadata, validation, safe errors, default registration, and catalog presence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T070 Run the complete focused YT-250 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/250-videos-rate/quickstart.md`
- [X] T071 Run Layer 1 guard verification if Layer 1 files changed and fix failures using `pytest tests/contract/test_layer1_videos_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T072 Run code-quality verification and fix failures using `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T073 Run the full repository test suite and fix any failures using `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T074 Confirm `git status --short` contains only intended YT-250 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable video-rating tool.
- **Phase 4 US2**: Depends on Foundational and is easiest after US1 descriptor scaffolding exists.
- **Phase 5 US3**: Depends on Foundational and is easiest after US1 handler/error scaffolding exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational; recommended MVP.
- **US2 (P2)**: Can start after Foundational if descriptor scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `videos.py`.
- **US3 (P3)**: Can start after Foundational if validation/error scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `videos.py`.

### Within Each User Story

- Red tests must be added and observed failing before implementation tasks.
- Green implementation should be the minimum needed to pass that story's tests.
- Implementation tasks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` should be serialized to avoid conflicting edits.
- Export and dispatcher tasks should happen after the descriptor builder exists.
- reStructuredText docstrings must be added or updated before story checkpoint validation.
- Refactor only after focused tests pass.
- Final completion requires focused tests, full `pytest`, and `ruff check .`.

## Parallel Opportunities

- T003, T004, T005, and T006 can run in parallel during setup because they inspect different files.
- T007, T008, T009, T010, and T011 can be written in parallel because they target different contract, unit, and integration test files.
- T014, T015, and T016 can be written in parallel because they target contract, unit, and integration test files.
- T033, T034, T035, and T036 can be written in parallel because they target separate metadata-oriented test files.
- T046, T047, T048, T049, T050, and T051 can be planned in parallel, but edits to `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py` should be coordinated because several US3 tasks share that file.
- T065, T066, T067, T068, and T069 can run in parallel during polish because they inspect or update documentation, source docstrings, tests, and regression coverage in different scopes.

## Parallel Example: User Story 1

```text
Task: "T014 [P] [US1] Add contract tests for videos_rate in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T015 [P] [US1] Add unit tests for videos_rate in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T016 [P] [US1] Add integration tests for videos_rate in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
```

## Parallel Example: User Story 2

```text
Task: "T033 [P] [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T034 [P] [US2] Add catalog metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T035 [P] [US2] Add common export metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T036 [P] [US2] Add registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```text
Task: "T046 [P] [US3] Add invalid rating-shape unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T050 [P] [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T051 [P] [US3] Add dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `videos_rate` can execute successful authorized `like`, `dislike`, and `none` requests through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. Deliver US1 to make the public endpoint-backed tool callable.
2. Deliver US2 to make discovery metadata, caveats, examples, quota, OAuth, rating-state, clear-rating, no-request-body, and acknowledgment guidance complete.
3. Deliver US3 to harden invalid requests, access failures, disabled-rating cases, not-found cases, quota failures, endpoint failures, and safe error details.
4. Complete polish with focused verification, full `pytest`, `ruff check .`, docstring review, and git status review.

### Parallel Team Strategy

1. Complete setup and foundational Red checks together.
2. Split contract, unit, and integration Red tests across different files where marked `[P]`.
3. Keep edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` serialized unless developers coordinate non-overlapping functions.
4. Keep export, dispatcher, and shared catalog edits serialized after the descriptor builder exists.
