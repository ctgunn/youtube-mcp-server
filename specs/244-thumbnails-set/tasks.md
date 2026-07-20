# Tasks: Layer 2 Thumbnails Set Tool

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/data-model.md), [contracts/thumbnails_set.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/contracts/thumbnails_set.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/plan.md`
- [X] T002 Inspect the existing Layer 1 `thumbnails.set` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/thumbnails.py`
- [X] T003 [P] Inspect existing media-upload Layer 2 patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T004 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T005 [P] Inspect shared family placement for thumbnails in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared test scaffolding, export expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until these tasks are complete and Red checks have been observed failing for the missing `thumbnails_set` surface.

- [X] T006 [P] Add Red public export checks for `THUMBNAILS_SET_TOOL_NAME`, `THUMBNAILS_SET_QUOTA_COST`, and `build_thumbnails_set_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T007 [P] Add Red scaffold checks that the thumbnails family has a concrete Layer 2 module and set descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T008 [P] Add Red default catalog checks that `thumbnails_set` appears once with resource family `thumbnails` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T009 [P] Add Red default registration checks that `thumbnails_set` is discoverable through the tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T010 [P] Add Red thumbnails-family registration checks for `thumbnails_set` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_thumbnails_registration.py`
- [X] T011 Add shared fake wrapper and executor helpers for thumbnails tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T012 Run foundational Red checks and confirm they fail for missing thumbnails symbols from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Set a Video Thumbnail Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `thumbnails_set` with a valid `videoId`, supported `media` upload content, and OAuth-backed access, then receive a safe thumbnail-set result with endpoint, quota, target, upload, auth, and upstream context.

**Independent Test**: Invoke the tool handler with `{"videoId": "video-123", "media": {"mimeType": "image/png", "content": "<thumbnail content omitted>"}}` and OAuth access using a fake Layer 1 wrapper; verify one wrapper call and a result containing `endpoint: thumbnails.set`, `quotaCost: 50`, `updated: true`, `target.videoId`, safe `upload` context, and `auth.mode: oauth_required`.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T013 [P] [US1] Add contract tests for `thumbnails_set` tool identity, input schema, upstream identity, quota cost 50, OAuth mode, media-upload response convention, and executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py`
- [X] T014 [P] [US1] Add unit tests for successful `validate_thumbnails_set_arguments`, safe upload summary handling, `map_thumbnails_set_result`, and `build_thumbnails_set_handler` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T015 [P] [US1] Add integration tests proving `thumbnails_set` is registered and callable through the thumbnails family registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_thumbnails_registration.py`
- [X] T016 [US1] Run US1 Red tests and confirm they fail for missing `thumbnails_set` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T017 [US1] Create the concrete thumbnails Layer 2 module with imports for `build_thumbnails_set_wrapper`, auth, executor, retry, shared contracts, and safe error helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T018 [US1] Define `THUMBNAILS_SET_TOOL_NAME`, `THUMBNAILS_SET_QUOTA_COST`, allowed upload descriptors, unsafe-detail keys, and `THUMBNAILS_SET_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T019 [US1] Implement `ThumbnailsSetToolError` and safe error detail sanitization support for thumbnail-setting failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T020 [US1] Implement `validate_thumbnails_set_arguments` requiring one non-empty `videoId`, required `media`, and no unsupported additional fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T021 [US1] Implement safe upload context helpers that preserve `mimeType` and `contentProvided` without echoing raw upload content in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T022 [US1] Implement `map_thumbnails_set_result` to return endpoint, quota cost 50, `updated: true`, safe target context, safe upload context, OAuth auth context, and safe upstream fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T023 [US1] Implement OAuth-required auth context and `build_thumbnails_set_handler` using the Layer 1 set wrapper once per valid call in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T024 [US1] Implement `build_thumbnails_set_contract` and `build_thumbnails_set_tool_descriptor` with media-upload mutation response metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T025 [US1] Export `thumbnails_set` constants, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T026 [US1] Register `build_thumbnails_set_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T027 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T028 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper or executor helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T029 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py`
- [X] T030 [US1] Refactor US1 thumbnail execution code for consistency with media-upload mutation helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Upload Requirements Before Calling (Priority: P2)

**Goal**: A client developer can inspect `thumbnails_set` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `50`, required OAuth, required `videoId`, required `media`, upload boundaries, sparse-result behavior, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `thumbnails.set`, quota cost `50`, OAuth-required access, required `videoId`, required `media`, media-upload boundary, sparse-success caveat, target-video caveats, and no generation/editing/video-management/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T031 [P] [US2] Add contract tests for metadata text, usage notes, caveats, quota visibility, OAuth visibility, media-upload visibility, availability state, response boundary, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py`
- [X] T032 [P] [US2] Add catalog contract tests confirming `thumbnails_set` metadata exposes quota cost 50, OAuth-required auth, and media-upload requirements before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T033 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `thumbnails_set` without replacing other resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T034 [P] [US2] Add integration tests proving default registry metadata preserves `thumbnails_set` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T035 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T036 [US2] Add `THUMBNAILS_SET_DESCRIPTION`, `THUMBNAILS_SET_USAGE_NOTES`, and `THUMBNAILS_SET_CAVEATS` with quota cost 50, OAuth-required access, required `videoId`, required `media`, upload boundary, sparse-response caveat, target-video caveats, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T037 [US2] Add `THUMBNAILS_SET_CALLER_EXAMPLES` covering successful thumbnail setting, sparse success, missing `videoId`, missing `media`, invalid `videoId`, unsupported upload, missing OAuth, target-video or quota upstream failure, and out-of-scope request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T038 [US2] Update `build_thumbnails_set_contract` and `build_thumbnails_set_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, OAuth details, and upload details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T039 [US2] Update shared examples or catalog entries if required so `thumbnails_set` replaces any representative placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor and Validation for User Story 2

- [X] T040 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, or descriptor helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T041 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py`
- [X] T042 [US2] Refactor US2 metadata and example wording for consistency with media-upload tools while preserving thumbnail-specific quota, OAuth, upload, target-video, sparse-response, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid or Under-Authorized Thumbnail Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation, access, target-video, upload, quota, availability, deprecation, and unexpected-upstream failures that remain distinct from successful thumbnail-set results.

**Independent Test**: Submit missing `videoId`, empty `videoId`, non-string `videoId`, missing `media`, malformed `media`, unsupported media, raw-media echo checks, unsupported fields, generation/editing/listing requests, missing OAuth, insufficient OAuth, target-video failure, upload rejection, quota, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category and sanitized details.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T043 [P] [US3] Add unit validation tests for missing `videoId`, empty `videoId`, non-string `videoId`, unsupported top-level fields, video URL attempts, search selector attempts, channel selector attempts, playlist selector attempts, metadata-update attempts, image-transformation attempts, thumbnail-generation prompts, paging controls, analytics modifiers, ranking modifiers, summarization modifiers, and enrichment modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T044 [US3] Add unit upload validation tests for missing `media`, non-object `media`, missing `media.mimeType`, missing `media.content`, empty media content, unsupported media type, additional media fields, ambiguous upload shapes, and raw media sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T045 [US3] Add unit handler tests for missing OAuth, invalid OAuth mode, wrapper call prevention on access failure, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T046 [US3] Add unit upstream error mapping tests for target video missing, target video unavailable, target video not writable, custom-thumbnail-ineligible target, upload rejected, quota failure, invalid request, authorization failure, endpoint unavailable, deprecated endpoint, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T047 [P] [US3] Add contract tests proving failure examples cover invalid request, access failure, unsupported upload, upload rejection, target-video failure, quota/upstream failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py`
- [X] T048 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T049 [US3] Extend `validate_thumbnails_set_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, malformed, and unsupported `videoId` inputs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T050 [US3] Extend `validate_thumbnails_set_arguments` to return field-specific errors for missing `media`, malformed `media`, missing `mimeType`, missing `content`, empty content, unsupported media type, additional media fields, and ambiguous upload shapes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T051 [US3] Extend `validate_thumbnails_set_arguments` to reject out-of-scope fields such as `videoUrl`, `q`, `channelId`, `playlistId`, `body`, `generateThumbnail`, `transformImage`, `pageToken`, `includeAnalytics`, `rankResults`, and `summarize` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T052 [US3] Implement missing-OAuth rejection before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T053 [US3] Implement upstream error mapping for authentication, authorization, target-video failures, unsupported upload, upload rejection, quota, invalid request, unavailable endpoint, deprecated endpoint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T054 [US3] Ensure thumbnail-set error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upload content, raw upstream bodies, stack traces, and unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`

### Refactor and Validation for User Story 3

- [X] T055 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T056 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper or executor helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T057 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T058 [US3] Refactor US3 validation and error mapping for consistency with media-upload mutation helpers while preserving thumbnail-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, target-video, upload, and upstream failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T059 [P] Review `thumbnails_set` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/contracts/thumbnails_set.md`
- [X] T060 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/quickstart.md`
- [X] T061 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`
- [X] T062 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`
- [X] T063 Run the complete focused YT-244 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/244-thumbnails-set/quickstart.md`
- [X] T064 Run `ruff check .` and fix lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T065 Run full repository test suite `pytest` and fix all failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T066 Confirm `git status --short` contains only intended YT-244 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable thumbnail-setting tool.
- **Phase 4 US2**: Depends on Foundational and is easiest after US1 descriptor scaffolding exists.
- **Phase 5 US3**: Depends on Foundational and is easiest after US1 handler/error scaffolding exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational; recommended MVP.
- **US2 (P2)**: Can start after Foundational if descriptor scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `thumbnails.py`.
- **US3 (P3)**: Can start after Foundational if validation/error scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `thumbnails.py`.

### Within Each User Story

- Red tests must be added and observed failing before implementation tasks.
- Green implementation should be the minimum needed to pass that story's tests.
- Implementation tasks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py` should be serialized to avoid conflicting edits.
- Export and dispatcher tasks should happen after the descriptor builder exists.
- reStructuredText docstrings must be added or updated before story checkpoint validation.
- Refactor only after focused tests pass.
- Final completion requires focused tests, full `pytest`, and `ruff check .`.

## Parallel Opportunities

- T003, T004, and T005 can run in parallel during setup because they inspect different files.
- T006, T007, T008, T009, and T010 can be written in parallel because they target different contract, unit, and integration test files.
- T013, T014, and T015 can be written in parallel because they target contract, unit, and integration test files.
- T031, T032, T033, and T034 can be written in parallel because they target separate metadata-oriented test files.
- T043 and T047 can run in parallel because they touch unit validation tests and contract failure examples in different files; T044, T045, and T046 should be serialized because they touch the same unit-test file.
- T059, T060, T061, and T062 can run in parallel during polish because they inspect or update documentation and docstrings in different scopes.

## Parallel Example: User Story 1

```bash
Task: "T013 [US1] Add contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py"
Task: "T014 [US1] Add unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py"
Task: "T015 [US1] Add integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_thumbnails_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T031 [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py"
Task: "T032 [US2] Add catalog metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T033 [US2] Add common export metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T034 [US2] Add registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```bash
Task: "T043 [US3] Add invalid request unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py"
Task: "T047 [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_thumbnails_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `thumbnails_set` can execute a successful authorized thumbnail-setting path through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. US1 delivers executable endpoint-backed thumbnail setting with safe success context.
2. US2 makes quota, OAuth, upload requirements, examples, sparse-result behavior, and out-of-scope boundaries discoverable before invocation.
3. US3 completes invalid request, access, target-video, upload, and upstream failure boundaries.
4. Polish runs focused tests, full `pytest`, `ruff check .`, docstring review, and final status review.

### Parallel Team Strategy

1. Complete Setup and Foundational together.
2. Assign one person to US1 implementation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py`.
3. Assign another person to US2 metadata tests and catalog assertions.
4. Assign another person to US3 validation tests, coordinating edits to `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_thumbnails.py`.

## Task Summary

- **Total tasks**: 66
- **Setup tasks**: 5
- **Foundational tasks**: 7
- **User Story 1 tasks**: 18
- **User Story 2 tasks**: 12
- **User Story 3 tasks**: 16
- **Polish tasks**: 8
- **Suggested MVP scope**: Phase 1, Phase 2, and Phase 3 only

## Notes

- `[P]` tasks are limited to work that can proceed without depending on incomplete tasks and usually touches different files.
- Story labels map to `US1`, `US2`, and `US3` from the feature specification.
- All implementation tasks touching Python code include explicit docstring follow-up tasks.
- Do not mark the feature complete until full `pytest` and `ruff check .` pass after final changes.
- Keep the implementation endpoint-backed and avoid thumbnail generation, image editing, video upload, video metadata updates, channel branding, analytics, ranking, summarization, enrichment, preflight lookup, bulk processing, or cross-endpoint behavior.
