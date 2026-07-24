# Tasks: Layer 2 Tool `watermarks_set`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/data-model.md), [contracts/watermarks_set.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/contracts/watermarks_set.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/plan.md`
- [X] T002 Inspect the existing Layer 1 `watermarks.set` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`
- [X] T003 [P] Inspect existing Layer 1 watermark validators and upload boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/watermarks.py`
- [X] T004 [P] Inspect existing media-upload Layer 2 patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/thumbnails.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect shared family and catalog placement for watermarks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, catalog expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until this phase is complete and Red checks have been observed failing for the missing concrete `watermarks_set` surface.

- [X] T007 [P] Add Red public export checks for `WATERMARKS_SET_TOOL_NAME`, `WATERMARKS_SET_QUOTA_COST`, `WATERMARKS_SET_INPUT_SCHEMA`, `WatermarksSetToolError`, `build_watermarks_set_contract`, `build_watermarks_set_handler`, `build_watermarks_set_tool_descriptor`, `map_watermarks_set_result`, and `validate_watermarks_set_arguments` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `watermarks` family exposes a concrete `watermarks_set` descriptor and module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `watermarks_set` appears once with resource family `watermarks`, quota cost `50`, OAuth-required auth, media-upload caveats, and upload or mutation acknowledgment metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `watermarks_set` is discoverable through the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red watermarks-family registration checks for `watermarks_set` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T012 Add shared fake watermark-set wrapper, fake sparse acknowledgment payloads, OAuth helper, media helper, and upstream failure helpers with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T013 Run foundational Red checks and record the failing command evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/quickstart.md`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Set a Channel Watermark Through a Public Endpoint Tool (Priority: P1) MVP

**Goal**: A caller with eligible OAuth can invoke `watermarks_set` with a valid `channelId`, supported watermark `body`, and supported `media` upload content, then receive a structured sparse watermark-update acknowledgment that preserves endpoint, quota, access, target channel, metadata, upload, and mutation context.

**Independent Test**: Invoke the tool handler with `{"channelId": "UC123", "body": {"timing": {"type": "offsetFromStart", "offsetMs": 0}, "position": {"type": "corner", "cornerPosition": "topRight"}}, "media": {"mimeType": "image/png", "content": "<watermark content omitted>"}}` using a fake Layer 1 wrapper and OAuth context; verify one wrapper call and a result containing `endpoint: watermarks.set`, `quotaCost: 50`, target channel identity, metadata context, safe upload context, auth context, availability state, update status, and acknowledgment details.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `watermarks_set` tool identity, input schema, upstream identity, quota cost `50`, OAuth-required auth mode, upload or mutation acknowledgment response convention, near-raw response boundary, media-upload caveat, and executable descriptor shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_watermarks_set_arguments`, channel context extraction, body metadata context extraction, safe upload context extraction, `map_watermarks_set_result`, `build_watermarks_set_handler`, required request submission, and sparse acknowledgment behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T016 [P] [US1] Add integration tests proving `watermarks_set` is registered and callable through the watermarks family registry with a valid authorized watermark-set request in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing `watermarks_set` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Create the concrete watermarks Layer 2 module with imports for `build_watermarks_set_wrapper`, auth, executor, retry, shared contracts, and safe error helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T019 [US1] Define `WATERMARKS_SET_TOOL_NAME`, `WATERMARKS_SET_QUOTA_COST`, allowed MIME types, unsafe-detail keys, maximum upload size constant, and `WATERMARKS_SET_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T020 [US1] Implement `WatermarksSetToolError` and safe error detail sanitization for watermark-set failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T021 [US1] Implement `validate_watermarks_set_arguments` requiring an object request, one non-empty string `channelId`, required `body`, required `media`, and no unsupported top-level fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T022 [US1] Implement channel context, body metadata context, and safe media upload context helpers for `watermarks_set` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T023 [US1] Implement OAuth auth context selection for `watermarks_set` and reject API-key-only execution before Layer 1 wrapper calls in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T024 [US1] Implement `map_watermarks_set_result` to return endpoint, quota cost `50`, target context, metadata context, upload context, auth context, availability state, update status, sparse acknowledgment status, and source operation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T025 [US1] Implement `build_watermarks_set_handler` using the Layer 1 watermark-set wrapper once per valid call with OAuth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T026 [US1] Implement `build_watermarks_set_contract` and `build_watermarks_set_tool_descriptor` with watermark-set upload mutation metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T027 [US1] Export `watermarks_set` constants, error class, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T028 [US1] Register `build_watermarks_set_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T030 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper, fake response, OAuth helper, media helper, or upstream failure helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T031 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T032 [US1] Refactor US1 watermark-set execution code for consistency with existing Layer 2 upload mutation helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Quota, OAuth, and Upload Requirements Before Calling (Priority: P2)

**Goal**: A client developer can inspect `watermarks_set` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `50`, OAuth-only access, required `channelId`, required `body`, required `media`, accepted MIME types, 10 MB upload boundary, sparse acknowledgment result shape, rejected partner delegation, media safety, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `watermarks.set`, quota cost `50`, OAuth-required access, required channel identity, required watermark metadata, required upload media, accepted media types, 10 MB limit, rejected `onBehalfOfContentOwner`, sparse acknowledgment result shape, and no removal/lookup/update/banner/thumbnail/video/analytics/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T033 [P] [US2] Add contract tests for `WATERMARKS_SET_DESCRIPTION`, `WATERMARKS_SET_USAGE_NOTES`, `WATERMARKS_SET_CAVEATS`, `WATERMARKS_SET_CALLER_EXAMPLES`, quota visibility, OAuth visibility, channel-boundary visibility, metadata-boundary visibility, upload-boundary visibility, rejected-delegation visibility, sparse acknowledgment visibility, response boundary, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`
- [X] T034 [P] [US2] Add catalog contract tests confirming `watermarks_set` metadata exposes quota cost `50`, OAuth-required auth, required `channelId`, required `body`, required `media`, upload boundaries, rejected partner delegation, owner-only availability, sparse acknowledgment, and out-of-scope behavior before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `watermarks_set` without replacing other resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T036 [P] [US2] Add integration tests proving default registry metadata preserves `watermarks_set` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T037 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T038 [US2] Add `WATERMARKS_SET_DESCRIPTION`, `WATERMARKS_SET_USAGE_NOTES`, and `WATERMARKS_SET_CAVEATS` with quota cost `50`, OAuth-only access, required `channelId`, required `body`, required `media`, accepted media types, 10 MB upload boundary, sparse acknowledgment behavior, rejected partner delegation, safe result boundary, and out-of-scope guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T039 [US2] Add `WATERMARKS_SET_CALLER_EXAMPLES` covering successful authorized watermark update, sparse success, missing channel validation failure, malformed channel failure, missing metadata failure, unsupported metadata failure, missing upload failure, unsupported upload failure, rejected partner delegation, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T040 [US2] Update `build_watermarks_set_contract` and `build_watermarks_set_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, OAuth details, channel details, metadata details, upload details, sparse acknowledgment details, rejected-delegation details, and safe failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T041 [US2] Update shared examples or catalog entries so `watermarks_set` appears as a concrete endpoint-backed contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T042 [US2] Update `watermarks_set` export coverage for caller-facing metadata and example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T043 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T044 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T045 [US2] Refactor US2 metadata and example wording for consistency with existing upload mutation tools while preserving quota, OAuth, required `channelId`, required `body`, required `media`, upload boundary, sparse acknowledgment, rejected-delegation, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Watermark Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation or failure feedback for missing channel identity, malformed channel identity, missing metadata, unsupported metadata, missing upload, unsupported upload, rejected partner delegation, unsupported modifiers, missing OAuth, insufficient authorization, not-found, quota, policy, unavailable, deprecated, unexpected-upstream, conflict, upstream-refusal, and out-of-scope workflow cases.

**Independent Test**: Submit missing `channelId`, non-string `channelId`, blank `channelId`, ambiguous multi-target `channelId` where locally detectable, missing `body`, invalid `body`, missing `body.timing`, missing `body.position`, invalid `body.targetChannelId`, missing `media`, invalid `media`, unsupported `media.mimeType`, missing or empty `media.content`, oversized upload content, unsupported top-level fields, `onBehalfOfContentOwner`, removal/lookup/update/banner/thumbnail/video/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields, missing OAuth, insufficient OAuth, not-found, quota, policy, unavailable, deprecated, conflict, upstream refusal, and unexpected upstream cases; verify each returns the expected safe category and sanitized details while valid sparse acknowledgments remain successes.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T046 [US3] Add unit validation tests for non-object arguments, missing `channelId`, empty `channelId`, non-string `channelId`, comma-separated or ambiguous multi-target `channelId` where locally detectable, and valid channel normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T047 [US3] Add unit body validation tests for missing `body`, non-object `body`, missing `body.timing`, empty `body.timing`, missing `body.position`, empty `body.position`, invalid `body.targetChannelId`, metadata-only requests, and unsupported metadata shapes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T048 [US3] Add unit media validation tests for missing `media`, non-object `media`, missing `media.mimeType`, unsupported `media.mimeType`, missing `media.content`, empty `media.content`, oversized `media.content`, extra media fields, media-only requests, ambiguous upload shapes, and raw media sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T049 [US3] Add unit validation tests for supplied `onBehalfOfContentOwner`, unsupported top-level fields, target aliases, bulk watermark fields, removal fields, lookup fields, channel update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, and automated branding fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T050 [US3] Add unit handler tests for missing OAuth, invalid auth mode, wrapper call prevention on access failure, API-key-only access rejection, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T051 [US3] Add unit result and upstream error mapping tests for sparse success, quota failure, upstream invalid request, authorization failure, forbidden or policy failure, target channel not found, unsupported upload, upload failure, endpoint unavailable, deprecated endpoint, upstream refusal, conflict behavior, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T052 [P] [US3] Add contract tests proving failure examples cover invalid request, missing OAuth, missing channel, malformed channel, missing metadata, unsupported metadata, missing upload, unsupported upload, rejected partner delegation, quota/upstream failure, not-found failure, forbidden or policy failure, deprecated behavior, endpoint unavailable, upstream refusal, conflict, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`
- [X] T053 [P] [US3] Add integration tests for dispatcher rejection of missing channel, malformed channel, missing body, missing media, partner delegation, unsupported fields, missing OAuth, out-of-scope workflow field, and unsafe error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T054 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T055 [US3] Extend `validate_watermarks_set_arguments` to return field-specific `invalid_request` errors for non-object arguments, missing channel identity, invalid channel identity, and ambiguous multi-target values where locally detectable in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T056 [US3] Extend `validate_watermarks_set_arguments` to return field-specific errors for missing `body`, malformed `body`, missing `body.timing`, empty `body.timing`, missing `body.position`, empty `body.position`, invalid `body.targetChannelId`, and unsupported metadata shapes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T057 [US3] Extend `validate_watermarks_set_arguments` to return field-specific errors for missing `media`, malformed `media`, missing `media.mimeType`, unsupported `media.mimeType`, missing `media.content`, empty `media.content`, oversized media content, extra media fields, and ambiguous upload shapes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T058 [US3] Extend `validate_watermarks_set_arguments` to reject supplied `onBehalfOfContentOwner`, unsupported top-level fields, aliases, bulk watermark fields, removal fields, lookup fields, channel update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, and automated branding fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T059 [US3] Implement missing or invalid OAuth access rejection for `watermarks_set` before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T060 [US3] Implement insufficient OAuth, forbidden, policy, refused watermark update, conflict, unsupported upload, upload failure, or unavailable channel mapping for `watermarks_set` with sanitized shared safe details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T061 [US3] Implement upstream error mapping for quota, invalid request, authorization, forbidden, policy, resource not found, unavailable endpoint, deprecated endpoint, availability constraint, upstream refusal, conflict behavior, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T062 [US3] Ensure watermark-set acknowledgment mapping does not fabricate refreshed channel metadata, watermark lookup results, media hosting URLs, banner results, thumbnail results, video results, analytics, recommendations, rankings, summaries, mutations outside watermark setting, or enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T063 [US3] Ensure watermark-set error detail sanitization removes API keys, OAuth tokens, authorization headers, raw media content, raw upstream bodies, stack traces, unsafe request context, private authorization details, and secret-bearing details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

### Refactor and Validation for User Story 3

- [X] T064 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T065 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper, fake response, auth helper, media helper, or upstream failure helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T066 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T067 [US3] Refactor US3 validation and error mapping for consistency with existing upload mutation helpers while preserving watermarks-set-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, not-found, quota, upload, availability, deprecation, conflict, upstream refusal, and unexpected failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T068 [P] Review `watermarks_set` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/contracts/watermarks_set.md`
- [X] T069 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/quickstart.md`
- [X] T070 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T071 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T072 [P] Add any remaining cross-story regression coverage for `watermarks_set` discovery, metadata, validation, safe errors, default registration, and catalog presence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T073 Run the complete focused YT-254 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/254-watermarks-set/quickstart.md`
- [X] T074 Run Layer 1 guard verification if Layer 1 files changed and fix failures using `pytest tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T075 Run code-quality verification and fix failures using `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T076 Run the full repository test suite and fix any failures using `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T077 Confirm `git status --short` contains only intended YT-254 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable watermark-set tool.
- **Phase 4 US2**: Depends on Foundational and is easiest after US1 descriptor scaffolding exists.
- **Phase 5 US3**: Depends on Foundational and is easiest after US1 handler/error scaffolding exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories after Foundational; recommended MVP.
- **US2 (P2)**: Can start after Foundational if descriptor scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `watermarks.py`.
- **US3 (P3)**: Can start after Foundational if validation/error scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `watermarks.py`.

### Within Each User Story

- Red tests must be added and observed failing before implementation tasks.
- Green implementation should be the minimum needed to pass that story's tests.
- Implementation tasks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py` should be serialized to avoid conflicting edits.
- Export and dispatcher tasks should happen after the descriptor builder exists.
- reStructuredText docstrings must be added or updated before story checkpoint validation.
- Refactor only after focused tests pass.
- Final completion requires focused tests, full `pytest`, and `ruff check .`.

## Parallel Opportunities

- T003, T004, T005, and T006 can run in parallel during setup because they inspect different files.
- T007, T008, T009, T010, and T011 can be written in parallel because they target different contract, unit, and integration test files.
- T014, T015, and T016 can be written in parallel because they target contract, unit, and integration test files.
- T033, T034, T035, and T036 can be written in parallel because they target separate metadata-oriented test files.
- T052 and T053 can be written in parallel with the serialized US3 unit-test work because they target contract and integration files.
- T068, T069, T070, T071, and T072 can run in parallel during polish because they inspect or update documentation, source docstrings, tests, and regression coverage in different scopes.

## Parallel Example: User Story 1

```text
Task: "T014 [P] [US1] Add contract tests for watermarks_set in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py"
Task: "T015 [P] [US1] Add unit tests for watermarks_set in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py"
Task: "T016 [P] [US1] Add integration tests for watermarks_set in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py"
```

## Parallel Example: User Story 2

```text
Task: "T033 [P] [US2] Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py"
Task: "T034 [P] [US2] Add catalog metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T035 [P] [US2] Add common export metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T036 [P] [US2] Add registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Parallel Example: User Story 3

```text
Task: "T052 [P] [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py"
Task: "T053 [P] [US3] Add dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py"
Task: "T072 [P] Add remaining cross-story regression coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py and related test files"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `watermarks_set` can execute successful authorized watermark-set requests through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. Deliver US1 to make the public endpoint-backed tool callable.
2. Deliver US2 to make discovery metadata, caveats, examples, quota, OAuth, channel, metadata, upload, rejected-delegation, sparse acknowledgment, and unsupported-workflow guidance complete.
3. Deliver US3 to harden invalid requests, unsupported uploads, access failures, not-found cases, quota failures, endpoint failures, deprecated behavior, upstream refusals, conflicts, and safe error details.
4. Complete polish with focused verification, full `pytest`, `ruff check .`, docstring review, and git status review.

### Parallel Team Strategy

1. Complete setup and foundational Red checks together.
2. Split contract, unit, and integration Red tests across different files where marked `[P]`.
3. Keep edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py` serialized unless developers coordinate non-overlapping functions.
4. Keep export, dispatcher, and shared catalog edits serialized after the descriptor builder exists.
