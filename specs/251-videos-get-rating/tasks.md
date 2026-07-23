# Tasks: Layer 2 Tool `videos_getRating`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/data-model.md), [contracts/videos_getRating.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/contracts/videos_getRating.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/plan.md`
- [X] T002 Inspect the existing Layer 1 `videos.getRating` wrapper, validator, and normalizer dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/response_normalizers/videos.py`
- [X] T003 [P] Inspect existing `videos_list`, `videos_insert`, `videos_update`, and `videos_rate` Layer 2 implementation patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T004 [P] Inspect existing read-result patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect existing videos-focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, catalog expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until this phase is complete and Red checks have been observed failing for the missing `videos_getRating` surface.

- [X] T007 [P] Add Red public export checks for `VIDEOS_GET_RATING_TOOL_NAME`, `VIDEOS_GET_RATING_QUOTA_COST`, `VIDEOS_GET_RATING_INPUT_SCHEMA`, `VideosGetRatingToolError`, `build_videos_get_rating_contract`, `build_videos_get_rating_handler`, `build_videos_get_rating_tool_descriptor`, `map_videos_get_rating_result`, and `validate_videos_get_rating_arguments` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `videos` family exposes a concrete `videos_getRating` descriptor beside `videos_list`, `videos_insert`, `videos_update`, and `videos_rate` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `videos_getRating` appears once with resource family `videos`, quota cost `1`, OAuth-required auth, and `rating_lookup` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `videos_getRating` is discoverable through the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red videos-family registration checks for `videos_getRating` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T012 Add shared fake get-rating wrapper, fake rating response payloads, OAuth helper, and upstream failure helpers for videos get-rating tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T013 Run foundational Red checks and record the failing command evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/quickstart.md`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Look Up Viewer Rating State Through a Public Endpoint Tool (Priority: P1) MVP

**Goal**: A caller with eligible OAuth can invoke `videos_getRating` with valid one-video or multi-video `id` input, then receive structured per-video rating lookup outcomes.

**Independent Test**: Invoke the tool handler with `{"id": "abc123"}` and `{"id": "abc123,def456"}` using a fake Layer 1 wrapper and OAuth context; verify one wrapper call per request and a result containing `endpoint: videos.getRating`, `quotaCost: 1`, requested IDs, returned ratings, auth context, availability state, and per-video lookup details.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `videos_getRating` tool identity, input schema, upstream identity, quota cost `1`, OAuth-required auth mode, `rating_lookup` response convention, near-raw response boundary, and executable descriptor shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_videos_get_rating_arguments`, identifier context extraction, `map_videos_get_rating_result`, `build_videos_get_rating_handler`, single-video lookup, multi-video lookup, and unrated `none` result behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T016 [P] [US1] Add integration tests proving `videos_getRating` is registered and callable through the videos family registry with valid authorized single-video and multi-video rating lookup requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing `videos_getRating` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Add `build_videos_get_rating_wrapper` imports and get-rating-specific support imports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T019 [US1] Define `VIDEOS_GET_RATING_TOOL_NAME`, `VIDEOS_GET_RATING_QUOTA_COST`, returned rating constants, unsafe-detail keys, allowed fields, and `VIDEOS_GET_RATING_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T020 [US1] Implement `VideosGetRatingToolError` and safe error detail sanitization for video-rating lookup failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T021 [US1] Implement `validate_videos_get_rating_arguments` requiring non-empty `id`, one to fifty unique comma-separated video identifiers, optional valid `onBehalfOfContentOwner`, and no unsupported top-level fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T022 [US1] Implement requested ID splitting, identifier-set context, optional delegation context, and no-request-body helpers for `videos_getRating` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T023 [US1] Implement OAuth auth context selection for `videos_getRating` and reject API-key-only execution before Layer 1 wrapper calls in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T024 [US1] Implement `map_videos_get_rating_result` to return endpoint, quota cost `1`, lookup context, auth context, availability state, response kind/etag when safe, and per-video `items` ratings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T025 [US1] Implement `build_videos_get_rating_handler` using the Layer 1 get-rating wrapper once per valid call with OAuth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T026 [US1] Implement `build_videos_get_rating_contract` and `build_videos_get_rating_tool_descriptor` with rating lookup metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T027 [US1] Export `videos_getRating` constants, error class, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T028 [US1] Register `build_videos_get_rating_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T030 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper, fake response, OAuth helper, or upstream failure helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T031 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T032 [US1] Refactor US1 video-get-rating execution code for consistency with existing Layer 2 read-result helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Quota, OAuth, and Lookup Semantics Before Calling (Priority: P2)

**Goal**: A client developer can inspect `videos_getRating` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `1`, OAuth-only access, required `id`, identifier boundaries, optional delegation, returned rating states, no-request-body behavior, per-video result shape, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `videos.getRating`, quota cost `1`, OAuth-required access, required `id`, one-to-fifty unique ID boundary, optional `onBehalfOfContentOwner` caveat, returned ratings `like`, `dislike`, `none`, and `unspecified`, no request body, active read availability, per-video result shape, and no mutation/history/count/update/upload/delete/analytics/ranking/summarization/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T033 [P] [US2] Add contract tests for `VIDEOS_GET_RATING_DESCRIPTION`, `VIDEOS_GET_RATING_USAGE_NOTES`, `VIDEOS_GET_RATING_CAVEATS`, `VIDEOS_GET_RATING_CALLER_EXAMPLES`, quota visibility, OAuth visibility, identifier-boundary visibility, delegation visibility, no-body visibility, per-video result visibility, response boundary, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T034 [P] [US2] Add catalog contract tests confirming `videos_getRating` metadata exposes quota cost `1`, OAuth-required auth, required identity input, identifier boundaries, returned rating states, optional delegation caveat, no-body rules, active availability, and out-of-scope behavior before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `videos_getRating` without replacing `videos_list`, `videos_insert`, `videos_update`, or `videos_rate` resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T036 [P] [US2] Add integration tests proving default registry metadata preserves `videos_getRating` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T037 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T038 [US2] Add `VIDEOS_GET_RATING_DESCRIPTION`, `VIDEOS_GET_RATING_USAGE_NOTES`, and `VIDEOS_GET_RATING_CAVEATS` with quota cost `1`, OAuth-only access, required identity input, supported identifier boundary, optional partner delegation caveat, returned rating states, no-body guidance, safe per-video result boundary, and out-of-scope guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T039 [US2] Add `VIDEOS_GET_RATING_CALLER_EXAMPLES` covering authorized single-video lookup, authorized multi-video lookup, delegated partner lookup, unrated `none` lookup, `unspecified` lookup, missing identity failure, duplicate identifier failure, over-limit identifier failure, missing OAuth failure, quota or upstream failure, unavailable target failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T040 [US2] Update `build_videos_get_rating_contract` and `build_videos_get_rating_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, OAuth details, identifier details, returned rating-state details, no-body details, per-video result details, and safe failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T041 [US2] Update shared examples or catalog entries so `videos_getRating` appears as a concrete endpoint-backed contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T042 [US2] Update `videos_getRating` export coverage for caller-facing metadata and example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T043 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T044 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T045 [US2] Refactor US2 metadata and example wording for consistency with existing read tools while preserving quota, OAuth, identifier, delegation, returned rating-state, no-request-body, per-video result, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid or Unsupported Rating-Lookup Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation or failure feedback for missing identity, malformed or duplicate identifiers, over-limit identifiers, request body, invalid delegation, missing OAuth, insufficient authorization, not-found, quota, policy, unavailable, deprecated, unexpected-upstream, successful unrated or unspecified outcomes, and out-of-scope workflow cases.

**Independent Test**: Submit missing `id`, empty `id`, non-string `id`, duplicate IDs, over-limit IDs, malformed comma-delimited IDs, supplied `body`, unsupported fields, invalid `onBehalfOfContentOwner`, mutation/history/count/metadata/update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields, missing OAuth, insufficient OAuth, not-found, quota, policy, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category and sanitized details while successful `none` and `unspecified` results remain successes.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T046 [US3] Add unit validation tests for missing `id`, empty or non-string `id`, empty IDs inside comma-separated lists, duplicate IDs, more than fifty IDs, unsupported identifier aliases, and valid one-to-fifty ID normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T047 [US3] Add unit validation tests for supplied `body`, unsupported top-level fields, invalid `onBehalfOfContentOwner`, rating mutation fields, rating history fields, aggregate count fields, and out-of-scope metadata/update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T048 [US3] Add unit handler tests for missing OAuth, invalid auth mode, wrapper call prevention on access failure, API-key-only access rejection, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T049 [US3] Add unit result and upstream error mapping tests for `like`, `dislike`, `none`, and `unspecified` successes, empty returned items, partial returned items, quota failure, upstream invalid request, authorization failure, forbidden or policy failure, target video not found, endpoint unavailable, deprecated endpoint, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T050 [P] [US3] Add contract tests proving failure examples cover invalid request, missing OAuth, duplicate ID failure, over-limit ID failure, quota/upstream failure, not-found failure, forbidden or policy failure, deprecated behavior, endpoint unavailable, successful unrated lookup, successful unspecified lookup, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T051 [P] [US3] Add integration tests for dispatcher rejection of missing identity, duplicate IDs, over-limit IDs, request body, invalid delegation, missing OAuth, out-of-scope mutation field, and unsafe error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T052 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T053 [US3] Extend `validate_videos_get_rating_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, duplicated, ambiguous, malformed, or over-limit `id` values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T054 [US3] Extend `validate_videos_get_rating_arguments` to reject request bodies, unsupported top-level fields, unsupported aliases, invalid `onBehalfOfContentOwner`, and out-of-scope mutation/history/count/metadata/update/upload/delete/abuse/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T055 [US3] Implement missing or invalid OAuth access rejection for `videos_getRating` before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T056 [US3] Implement insufficient OAuth, partner delegation refusal, forbidden, policy, or unavailable target mapping for `videos_getRating` with sanitized `authorization_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T057 [US3] Implement upstream error mapping for quota, invalid request, authorization, forbidden, policy, resource not found, unavailable endpoint, deprecated endpoint, availability constraint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T058 [US3] Ensure video-get-rating result mapping preserves `like`, `dislike`, `none`, and `unspecified` successful lookup states without fabricating refreshed video metadata, rating history, aggregate counts, analytics, recommendations, rankings, summaries, mutations, or enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T059 [US3] Ensure video-get-rating error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, unsafe request context, and secret-bearing details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

### Refactor and Validation for User Story 3

- [X] T060 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T061 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper, fake response, auth helper, or upstream failure helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T062 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T063 [US3] Refactor US3 validation and error mapping for consistency with existing read helpers while preserving videos-get-rating-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, not-found, quota, availability, deprecation, upstream failure, and successful unrated-state scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T064 [P] Review `videos_getRating` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/contracts/videos_getRating.md`
- [X] T065 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/quickstart.md`
- [X] T066 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T067 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T068 [P] Add any remaining cross-story regression coverage for `videos_getRating` discovery, metadata, validation, safe errors, default registration, and catalog presence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T069 Run the complete focused YT-251 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/quickstart.md`
- [X] T070 Run Layer 1 guard verification if Layer 1 files changed and fix failures using `pytest tests/contract/test_layer1_videos_contract.py tests/contract/test_layer1_metadata_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T071 Run code-quality verification and fix failures using `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T072 Run the full repository test suite and fix any failures using `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T073 Confirm `git status --short` contains only intended YT-251 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable video-rating lookup tool.
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
- T050 and T051 can be written in parallel with the serialized US3 unit-test work because they target contract and integration files.
- T064, T065, T066, T067, and T068 can run in parallel during polish because they inspect or update documentation, source docstrings, tests, and regression coverage in different scopes.

## Parallel Example: User Story 1

```text
Task: "T014 [P] [US1] Add contract tests for videos_getRating in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T015 [P] [US1] Add unit tests for videos_getRating in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T016 [P] [US1] Add integration tests for videos_getRating in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
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
Task: "T050 [P] [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T051 [P] [US3] Add dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
Task: "T068 [P] Add remaining cross-story regression coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py and related test files"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `videos_getRating` can execute successful authorized single-video and multi-video lookup requests through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. Deliver US1 to make the public endpoint-backed tool callable.
2. Deliver US2 to make discovery metadata, caveats, examples, quota, OAuth, identifier, delegation, returned rating-state, no-request-body, and per-video result guidance complete.
3. Deliver US3 to harden invalid requests, access failures, not-found cases, quota failures, endpoint failures, deprecated behavior, successful unrated states, and safe error details.
4. Complete polish with focused verification, full `pytest`, `ruff check .`, docstring review, and git status review.

### Parallel Team Strategy

1. Complete setup and foundational Red checks together.
2. Split contract, unit, and integration Red tests across different files where marked `[P]`.
3. Keep edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` serialized unless developers coordinate non-overlapping functions.
4. Keep export, dispatcher, and shared catalog edits serialized after the descriptor builder exists.

## Notes

- `[P]` tasks touch different files or are inspection/review tasks with no dependency on incomplete edits.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to the user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/251-videos-get-rating/spec.md).
- Tests must be written and observed failing before implementation.
- Python code changes require reStructuredText docstrings before each story is marked complete.
- Final completion requires the focused YT-251 verification, full `pytest`, and `ruff check .`.
