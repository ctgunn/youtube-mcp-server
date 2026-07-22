# Tasks: Layer 2 Tool `videos_update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/data-model.md), [contracts/videos_update.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/contracts/videos_update.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/plan.md`
- [X] T002 Inspect the existing Layer 1 `videos.update` wrapper and validator dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/videos.py`
- [X] T003 [P] Inspect existing `videos_list` and `videos_insert` Layer 2 implementation patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T004 [P] Inspect existing mutation tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect existing videos-focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, catalog expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until this phase is complete and Red checks have been observed failing for the missing `videos_update` surface.

- [X] T007 [P] Add Red public export checks for `VIDEOS_UPDATE_TOOL_NAME`, `VIDEOS_UPDATE_QUOTA_COST`, `VIDEOS_UPDATE_INPUT_SCHEMA`, `VideosUpdateToolError`, `build_videos_update_contract`, `build_videos_update_handler`, `build_videos_update_tool_descriptor`, `map_videos_update_result`, and `validate_videos_update_arguments` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `videos` family exposes a concrete `videos_update` descriptor beside `videos_list` and `videos_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `videos_update` appears once with resource family `videos`, quota cost `50`, OAuth-required auth, and mutation-result metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `videos_update` is discoverable through the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red videos-family registration checks for `videos_update` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T012 Add shared fake update wrapper, fake executor, OAuth helper, and upstream failure helpers for videos update tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T013 Run foundational Red checks and record the failing command evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/quickstart.md`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Update Video Resources Through a Public Endpoint Tool (Priority: P1) MVP

**Goal**: A caller with eligible OAuth can invoke `videos_update` with valid `part`, `body.id`, and compatible update body, then receive a near-raw updated video result.

**Independent Test**: Invoke the tool handler with `{"part": "snippet", "body": {"id": "abc123", "snippet": {"title": "Updated title"}}}` using a fake Layer 1 wrapper and OAuth context; verify one wrapper call and a result containing `endpoint: videos.update`, `quotaCost: 50`, `requestedParts`, `update`, `auth`, optional `delegation`, `item`, `mutation`, and returned video fields.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `videos_update` tool identity, input schema, upstream identity, quota cost `50`, OAuth-required auth mode, mutation response convention, updated-resource response boundary, and executable descriptor shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_videos_update_arguments`, part normalization, update body context extraction, `map_videos_update_result`, and `build_videos_update_handler` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T016 [P] [US1] Add integration tests proving `videos_update` is registered and callable through the videos family registry with a valid authorized update request in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing `videos_update` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Add `build_videos_update_wrapper` imports and update-specific support imports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T019 [US1] Define `VIDEOS_UPDATE_TOOL_NAME`, `VIDEOS_UPDATE_QUOTA_COST`, writable-part constants, supported field constants, unsafe-detail keys, and `VIDEOS_UPDATE_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T020 [US1] Implement `VideosUpdateToolError` and safe error detail sanitization for video-update failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T021 [US1] Implement `validate_videos_update_arguments` requiring non-empty `part=snippet`, `body.id`, `body.snippet.title`, optional safe `kind`, optional `onBehalfOfContentOwner`, and no unsupported fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T022 [US1] Implement part-selection, target identity, update-body context, writable-field context, and safe delegation helpers for `videos_update` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T023 [US1] Implement OAuth auth context selection for `videos_update` and reject API-key-only execution before Layer 1 wrapper calls in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T024 [US1] Implement `map_videos_update_result` to return endpoint, quota cost `50`, requested parts, update context, auth context, optional delegation, item, mutation type `updated`, and safe returned upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T025 [US1] Implement `build_videos_update_handler` using the Layer 1 update wrapper once per valid call with OAuth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T026 [US1] Implement `build_videos_update_contract` and `build_videos_update_tool_descriptor` with near-raw mutation-result metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T027 [US1] Export `videos_update` constants, error class, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T028 [US1] Register `build_videos_update_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T030 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper, fake executor, OAuth helper, or upstream failure helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T031 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T032 [US1] Refactor US1 video-update execution code for consistency with existing Layer 2 mutation helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, Writable Parts, and Update Semantics Before Calling (Priority: P2)

**Goal**: A client developer can inspect `videos_update` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `50`, OAuth-only access, required identity/body/part input, writable-part boundaries, replacement-oriented update semantics, delegation, updated-resource result shape, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `videos.update`, quota cost `50`, OAuth-required access, required `part`, required `body.id`, required `body.snippet.title`, writable part `snippet`, replacement-semantics guidance, active mutation availability, updated-resource result shape, and no upload/create/delete/rating/thumbnail/caption/playlist/comment/transcript/analytics/ranking/summarization/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T033 [P] [US2] Add contract tests for `VIDEOS_UPDATE_DESCRIPTION`, `VIDEOS_UPDATE_USAGE_NOTES`, `VIDEOS_UPDATE_CAVEATS`, `VIDEOS_UPDATE_CALLER_EXAMPLES`, quota visibility, OAuth visibility, writable-part visibility, replacement-semantics visibility, response boundary, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T034 [P] [US2] Add catalog contract tests confirming `videos_update` metadata exposes quota cost `50`, OAuth-required auth, required identity/body/part inputs, writable-part boundaries, replacement semantics, active availability, and out-of-scope behavior before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `videos_update` without replacing `videos_list` or `videos_insert` resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T036 [P] [US2] Add integration tests proving default registry metadata preserves `videos_update` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T037 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T038 [US2] Add `VIDEOS_UPDATE_DESCRIPTION`, `VIDEOS_UPDATE_USAGE_NOTES`, and `VIDEOS_UPDATE_CAVEATS` with quota cost `50`, OAuth-only access, required identity/body/part inputs, writable-part boundaries, replacement semantics, safe result boundary, and out-of-scope guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T039 [US2] Add `VIDEOS_UPDATE_CALLER_EXAMPLES` covering authorized metadata update, delegated content-owner update, missing identity failure, missing part failure, read-only or unsupported part failure, incompatible update body failure, missing OAuth failure, quota or upstream failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T040 [US2] Update `build_videos_update_contract` and `build_videos_update_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, OAuth details, writable-part details, update-body details, replacement-semantics guidance, and safe failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T041 [US2] Update shared examples or catalog entries so `videos_update` appears as a concrete endpoint-backed contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T042 [US2] Update `videos_update` export coverage for caller-facing metadata and example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T043 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T044 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T045 [US2] Refactor US2 metadata and example wording for consistency with existing mutation tools while preserving quota, OAuth, writable-part, update-body, replacement-semantics, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid or Unsupported Video Update Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation or failure feedback for missing identity, missing part selection, read-only or unsupported fields, missing OAuth, insufficient authorization, not-found, quota, policy, unavailable, deprecated, unexpected-upstream, and out-of-scope workflow cases.

**Independent Test**: Submit missing `part`, empty `part`, non-string `part`, unsupported `part`, missing `body`, missing `body.id`, blank `body.id`, missing `body.snippet`, missing `body.snippet.title`, unsupported body fields, unsupported snippet fields, invalid delegation, media upload fields, creation/deletion/rating/thumbnail/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields, missing OAuth, insufficient OAuth, not-found, quota, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category and sanitized details.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T046 [P] [US3] Add unit validation tests for missing `part`, empty or non-string `part`, unsupported or read-only `part`, missing `body`, missing or blank `body.id`, missing `body.snippet`, missing or blank `body.snippet.title`, unsupported body fields, unsupported snippet fields, and invalid delegation context in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T047 [P] [US3] Add unit validation tests for unsupported media upload, media replacement, automatic publishing, create, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, enrichment, and cross-endpoint workflow fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T048 [P] [US3] Add unit handler tests for missing OAuth, invalid auth mode, insufficient delegated authorization, wrapper call prevention on access failure, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T049 [P] [US3] Add unit result and upstream error mapping tests for quota failure, upstream invalid request, authorization failure, forbidden or policy failure, target video not found, endpoint unavailable, deprecated endpoint, sparse upstream success, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T050 [P] [US3] Add contract tests proving failure examples cover invalid request, missing OAuth, quota/upstream failure, not-found failure, forbidden or policy failure, deprecated behavior, endpoint unavailable, sparse success, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`
- [X] T051 [P] [US3] Add integration tests for dispatcher rejection of missing identity, missing part, unsupported body field, missing OAuth, out-of-scope upload field, and unsafe error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T052 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T053 [US3] Extend `validate_videos_update_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, unsupported, read-only, duplicate, and conflicting `part` values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T054 [US3] Extend `validate_videos_update_arguments` to return field-specific errors for missing, empty, malformed, read-only, unsupported, or part-incompatible `body`, `body.id`, `body.snippet`, and `body.snippet.title` values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T055 [US3] Extend `validate_videos_update_arguments` to reject unsupported top-level fields and out-of-scope fields such as `media`, `uploadMode`, `videoCreation`, `delete`, `rating`, `thumbnail`, `caption`, `playlist`, `comment`, `includeTranscript`, `analytics`, `recommend`, `rankResults`, `summarize`, and `enrich` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T056 [US3] Implement missing or invalid OAuth access rejection for `videos_update` before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T057 [US3] Implement insufficient OAuth or delegated-owner access mapping for `videos_update` with sanitized `authorization_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T058 [US3] Implement upstream error mapping for quota, invalid request, authorization, forbidden, policy, resource not found, unavailable endpoint, deprecated endpoint, availability constraint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T059 [US3] Ensure video-update result mapping preserves sparse upstream updated resources without fabricating omitted metadata, media state, publication workflow state, thumbnails, captions, playlists, analytics, recommendations, rankings, summaries, or enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T060 [US3] Ensure video-update error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, unsafe request context, and secret-bearing details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

### Refactor and Validation for User Story 3

- [X] T061 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T062 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper, fake executor, auth helper, or upstream failure helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T063 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`
- [X] T064 [US3] Refactor US3 validation and error mapping for consistency with existing mutation helpers while preserving videos-update-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, not-found, quota, availability, deprecation, and upstream failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T065 [P] Review `videos_update` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/contracts/videos_update.md`
- [X] T066 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/quickstart.md`
- [X] T067 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T068 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`
- [X] T069 [P] Add any remaining cross-story regression coverage for `videos_update` discovery, metadata, validation, safe errors, default registration, and catalog presence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T070 Run the complete focused YT-249 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/quickstart.md`
- [X] T071 Run Layer 1 guard verification if Layer 1 files changed and fix failures using `pytest tests/contract/test_layer1_videos_contract.py tests/unit/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T072 Run code-quality verification and fix failures using `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T073 Run the full repository test suite and fix any failures using `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T074 Confirm `git status --short` contains only intended YT-249 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable video-update tool.
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
Task: "T014 [P] [US1] Add contract tests for videos_update in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T015 [P] [US1] Add unit tests for videos_update in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T016 [P] [US1] Add integration tests for videos_update in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
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
Task: "T046 [P] [US3] Add invalid update-shape unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_videos.py"
Task: "T050 [P] [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_videos_contract.py"
Task: "T051 [P] [US3] Add dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_videos_registration.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `videos_update` can execute a successful authorized `snippet` update through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. Deliver US1 to make the public endpoint-backed tool callable.
2. Deliver US2 to make discovery metadata, caveats, examples, quota, OAuth, writable-part, update-body, and replacement-semantics guidance complete.
3. Deliver US3 to harden invalid requests, access failures, not-found cases, quota failures, endpoint failures, and safe error details.
4. Complete polish with focused verification, full `pytest`, `ruff check .`, docstring review, and git status review.

### Parallel Team Strategy

1. Complete setup and foundational Red checks together.
2. Split contract, unit, and integration Red tests across different files where marked `[P]`.
3. Keep edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py` serialized unless developers coordinate non-overlapping functions.
4. Keep export, dispatcher, and shared catalog edits serialized after the descriptor builder exists.

## Independent Test Criteria Summary

- **US1**: A valid authorized `part=snippet` update invokes the Layer 1 wrapper once and returns a near-raw updated-video result with endpoint, quota, requested parts, update context, access context, optional delegation, mutation, and item context.
- **US2**: Tool discovery metadata and examples disclose `videos.update`, quota cost `50`, OAuth-only access, required identity/body/part input, supported writable fields, replacement-oriented update semantics, active availability, updated-resource result shape, and out-of-scope behavior before invocation.
- **US3**: Invalid, unsupported, access-failed, not-found, quota-failed, unavailable, deprecated, unexpected-upstream, and sparse-success cases return distinct safe outcomes with sanitized details.

## Task Summary

- Total tasks: 74
- Setup tasks: 6
- Foundational tasks: 7
- User Story 1 tasks: 19
- User Story 2 tasks: 13
- User Story 3 tasks: 19
- Polish tasks: 10
- Suggested MVP scope: Phase 1, Phase 2, and Phase 3 User Story 1

## Notes

- `[P]` tasks touch different files or are inspection-only and can run in parallel.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to prioritized user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/249-videos-update/spec.md).
- Every Python implementation or test-helper function added or modified by these tasks must include a reStructuredText docstring before the related story checkpoint is complete.
- Final feature completion requires the focused YT-249 command, full `pytest`, and `ruff check .` to pass after final code changes.
