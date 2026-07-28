# Tasks: Layer 2 Tool `watermarks_unset`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/data-model.md), [contracts/watermarks_unset.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/contracts/watermarks_unset.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and does not depend on incomplete tasks.
- **[Story]**: Maps to `US1`, `US2`, or `US3` from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/spec.md).
- Every task includes an exact file path or repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the local implementation surface and keep this slice aligned with the completed design artifacts.

- [X] T001 Verify the current branch and feature artifact paths from `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/plan.md`
- [X] T002 Inspect the existing Layer 1 `watermarks.unset` wrapper dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/watermarks.py`
- [X] T003 [P] Inspect existing Layer 1 watermark unset validators and no-upload boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/watermarks.py`
- [X] T004 [P] Inspect existing Layer 2 `watermarks_set` patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T005 [P] Inspect existing public export and default registry patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 [P] Inspect shared family and catalog placement for `watermarks_unset` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared Red checks, export expectations, catalog expectations, and registration expectations that all stories depend on.

**Critical**: No user story implementation should begin until this phase is complete and Red checks have been observed failing for the missing concrete `watermarks_unset` surface.

- [X] T007 [P] Add Red public export checks for `WATERMARKS_UNSET_TOOL_NAME`, `WATERMARKS_UNSET_QUOTA_COST`, `WATERMARKS_UNSET_INPUT_SCHEMA`, `WatermarksUnsetToolError`, `build_watermarks_unset_contract`, `build_watermarks_unset_handler`, `build_watermarks_unset_tool_descriptor`, `map_watermarks_unset_result`, and `validate_watermarks_unset_arguments` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add Red scaffold checks that the `watermarks` family exposes a concrete `watermarks_unset` descriptor and module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T009 [P] Add Red default catalog checks that `watermarks_unset` appears once with resource family `watermarks`, quota cost `50`, OAuth-required auth, no-upload caveats, and mutation acknowledgment metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T010 [P] Add Red default registration checks that `watermarks_unset` is discoverable through the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T011 [P] Add Red watermarks-family registration checks for `watermarks_unset` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T012 Add shared fake watermark-unset wrapper, fake sparse acknowledgment payloads, OAuth helper, channel helper, and upstream failure helpers with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T013 Run foundational Red checks and record the failing command evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/quickstart.md`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Remove a Channel Watermark Through a Public Endpoint Tool (Priority: P1) MVP

**Goal**: A caller with eligible OAuth can invoke `watermarks_unset` with a valid `channelId` and receive a structured sparse watermark-removal acknowledgment that preserves endpoint, quota, access, target channel, availability, and mutation context.

**Independent Test**: Invoke the tool handler with `{"channelId": "UC123"}` using a fake Layer 1 wrapper and OAuth context; verify one wrapper call and a result containing `endpoint: watermarks.unset`, `quotaCost: 50`, target channel identity, auth context, availability state, removal status, and acknowledgment details.

### Tests for User Story 1 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T014 [P] [US1] Add contract tests for `watermarks_unset` tool identity, input schema, upstream identity, quota cost `50`, OAuth-required auth mode, mutation acknowledgment response convention, near-raw response boundary, no-upload caveat, and executable descriptor shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`
- [X] T015 [P] [US1] Add unit tests for successful `validate_watermarks_unset_arguments`, channel context extraction, `map_watermarks_unset_result`, `build_watermarks_unset_handler`, required request submission, and sparse acknowledgment behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T016 [P] [US1] Add integration tests proving `watermarks_unset` is registered and callable through the watermarks family registry with a valid authorized watermark-removal request in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T017 [US1] Run US1 Red tests and confirm they fail for missing or incomplete `watermarks_unset` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Extend the concrete watermarks Layer 2 module with imports for `build_watermarks_unset_wrapper`, auth, executor, retry, shared contracts, and safe error helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T019 [US1] Define `WATERMARKS_UNSET_TOOL_NAME`, `WATERMARKS_UNSET_QUOTA_COST`, unsafe-detail keys, and `WATERMARKS_UNSET_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T020 [US1] Implement `WatermarksUnsetToolError` and safe error detail sanitization for watermark-unset failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T021 [US1] Implement `validate_watermarks_unset_arguments` requiring an object request, one non-empty string `channelId`, and no unsupported top-level fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T022 [US1] Implement channel context and no-upload context helpers for `watermarks_unset` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T023 [US1] Implement OAuth auth context selection for `watermarks_unset` and reject API-key-only execution before Layer 1 wrapper calls in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T024 [US1] Implement `map_watermarks_unset_result` to return endpoint, source operation, quota cost `50`, target context, auth context, availability state, removal status, sparse acknowledgment status, and sanitized upstream payload in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T025 [US1] Implement `build_watermarks_unset_handler` using the Layer 1 watermark-unset wrapper once per valid call with OAuth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T026 [US1] Implement `build_watermarks_unset_contract` and `build_watermarks_unset_tool_descriptor` with watermark-removal mutation metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T027 [US1] Export `watermarks_unset` constants, error class, validators, mappers, builders, and descriptor symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T028 [US1] Register `build_watermarks_unset_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor and Validation for User Story 1

- [X] T029 [US1] Add or update reStructuredText docstrings for every new or modified US1 function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T030 [US1] Add or update reStructuredText docstrings for every new or modified US1 fake wrapper, fake response, OAuth helper, channel helper, or upstream failure helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T031 [US1] Run US1 focused tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T032 [US1] Refactor US1 watermark-unset execution code for consistency with existing Layer 2 mutation helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Quota, OAuth, and Removal Semantics Before Calling (Priority: P2)

**Goal**: A client developer can inspect `watermarks_unset` metadata, descriptions, usage notes, caveats, and examples before invocation and understand endpoint identity, quota cost `50`, OAuth-only access, required `channelId`, no-upload boundary, sparse acknowledgment result shape, no-removal-possible behavior, rejected partner delegation, result safety, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `watermarks.unset`, quota cost `50`, OAuth-required access, required channel identity, no media upload, rejected watermark metadata, rejected `onBehalfOfContentOwner`, sparse acknowledgment result shape, no-removal-possible caveat, and no upload/lookup/update/banner/thumbnail/video/analytics/enrichment behavior.

### Tests for User Story 2 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T033 [P] [US2] Add contract tests for `WATERMARKS_UNSET_DESCRIPTION`, `WATERMARKS_UNSET_USAGE_NOTES`, `WATERMARKS_UNSET_CAVEATS`, `WATERMARKS_UNSET_CALLER_EXAMPLES`, quota visibility, OAuth visibility, channel-boundary visibility, no-upload visibility, rejected-delegation visibility, sparse acknowledgment visibility, no-removal-possible visibility, response boundary, and caller examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`
- [X] T034 [P] [US2] Add catalog contract tests confirming `watermarks_unset` metadata exposes quota cost `50`, OAuth-required auth, required `channelId`, no-upload boundaries, rejected partner delegation, owner-only availability, sparse acknowledgment, no-removal-possible caveat, and out-of-scope behavior before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `watermarks_unset` without replacing other resource-family entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T036 [P] [US2] Add integration tests proving default registry metadata preserves `watermarks_unset` caller-facing contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T037 [US2] Run US2 Red metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T038 [US2] Add `WATERMARKS_UNSET_DESCRIPTION`, `WATERMARKS_UNSET_USAGE_NOTES`, and `WATERMARKS_UNSET_CAVEATS` with quota cost `50`, OAuth-only access, required `channelId`, no-upload boundary, sparse acknowledgment behavior, no-removal-possible behavior, rejected partner delegation, safe result boundary, and out-of-scope guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T039 [US2] Add `WATERMARKS_UNSET_CALLER_EXAMPLES` covering successful authorized watermark removal, sparse success, missing channel validation failure, malformed channel failure, unsupported `body` or `media` failure, rejected partner delegation, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, no-removal-possible outcome, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T040 [US2] Update `build_watermarks_unset_contract` and `build_watermarks_unset_tool_descriptor` to include metadata, examples, caveats, response boundary, availability state, quota details, OAuth details, channel details, no-upload details, sparse acknowledgment details, rejected-delegation details, no-removal-possible details, and safe failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T041 [US2] Replace the representative `watermarks_unset` placeholder with the concrete endpoint-backed contract builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T042 [US2] Update `watermarks_unset` export coverage for caller-facing metadata and example constants from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

### Refactor and Validation for User Story 2

- [X] T043 [US2] Add or update reStructuredText docstrings for all modified US2 metadata, contract, descriptor, or example helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T044 [US2] Run US2 focused metadata, catalog, common contract, and registry tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T045 [US2] Refactor US2 metadata and example wording for consistency with existing mutation tools while preserving quota, OAuth, required `channelId`, no-upload boundary, sparse acknowledgment, no-removal-possible, rejected-delegation, and unsupported-input caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Removal Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation or failure feedback for missing channel identity, malformed channel identity, unsupported `body`, unsupported `media`, rejected partner delegation, unsupported modifiers, missing OAuth, insufficient authorization, not-found, quota, policy, unavailable, deprecated, no-removal-possible, unexpected-upstream, conflict, upstream-refusal, and out-of-scope workflow cases.

**Independent Test**: Submit missing `channelId`, non-string `channelId`, blank `channelId`, ambiguous multi-target `channelId` where locally detectable, supplied `body`, supplied `media`, unsupported top-level fields, `onBehalfOfContentOwner`, upload/lookup/update/banner/thumbnail/video/caption/playlist/comment/transcript/analytics/recommendation/ranking/summarization/enrichment fields, missing OAuth, insufficient OAuth, not-found, quota, policy, unavailable, deprecated, no-removal-possible, conflict, upstream refusal, and unexpected upstream cases; verify each returns the expected safe category and sanitized details while valid sparse acknowledgments remain successes.

### Tests for User Story 3 (Red)

> Write these tests first and confirm they fail before implementation.

- [X] T046 [US3] Add unit validation tests for non-object arguments, missing `channelId`, empty `channelId`, non-string `channelId`, comma-separated or ambiguous multi-target `channelId` where locally detectable, and valid channel normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T047 [US3] Add unit no-upload validation tests for supplied `body`, supplied `media`, watermark metadata fields, upload content fields, metadata-only requests, media-only requests, mixed set/unset request shapes, and raw media sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T048 [US3] Add unit validation tests for supplied `onBehalfOfContentOwner`, unsupported top-level fields, target aliases, bulk watermark fields, upload fields, lookup fields, channel update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, and automated branding fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T049 [US3] Add unit handler tests for missing OAuth, invalid auth mode, wrapper call prevention on access failure, API-key-only access rejection, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T050 [US3] Add unit result and upstream error mapping tests for sparse success, quota failure, upstream invalid request, authorization failure, forbidden or policy failure, target channel not found, no-removal-possible behavior, endpoint unavailable, deprecated endpoint, upstream refusal, conflict behavior, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T051 [P] [US3] Add contract tests proving failure examples cover invalid request, missing OAuth, missing channel, malformed channel, unsupported `body` or `media`, rejected partner delegation, quota/upstream failure, not-found failure, forbidden or policy failure, deprecated behavior, endpoint unavailable, no-removal-possible, upstream refusal, conflict, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`
- [X] T052 [P] [US3] Add integration tests for dispatcher rejection of missing channel, malformed channel, `body`, `media`, partner delegation, unsupported fields, missing OAuth, out-of-scope workflow field, no-removal-possible failure, and unsafe error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T053 [US3] Run US3 Red validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T054 [US3] Extend `validate_watermarks_unset_arguments` to return field-specific `invalid_request` errors for non-object arguments, missing channel identity, invalid channel identity, and ambiguous multi-target values where locally detectable in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T055 [US3] Extend `validate_watermarks_unset_arguments` to reject supplied `body`, supplied `media`, metadata-only requests, media-only requests, mixed set/unset request shapes, and raw upload or metadata payloads without echoing unsafe content in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T056 [US3] Extend `validate_watermarks_unset_arguments` to reject supplied `onBehalfOfContentOwner`, unsupported top-level fields, aliases, bulk watermark fields, upload fields, lookup fields, channel update fields, banner fields, thumbnail fields, video fields, caption fields, playlist fields, comment fields, transcript fields, analytics fields, recommendation fields, ranking fields, summarization fields, enrichment fields, and automated branding fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T057 [US3] Implement missing or invalid OAuth access rejection for `watermarks_unset` before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T058 [US3] Implement insufficient OAuth, forbidden, policy, refused watermark removal, conflict, unavailable channel, no-removal-possible, or target-channel failure mapping for `watermarks_unset` with sanitized shared safe details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T059 [US3] Implement upstream error mapping for quota, invalid request, authorization, forbidden, policy, resource not found, unavailable endpoint, deprecated endpoint, availability constraint, no-removal-possible, upstream refusal, conflict behavior, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T060 [US3] Ensure watermark-unset acknowledgment mapping does not fabricate refreshed channel metadata, watermark lookup results, media hosting URLs, banner results, thumbnail results, video results, analytics, recommendations, rankings, summaries, mutations outside watermark removal, or enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T061 [US3] Ensure watermark-unset error detail sanitization removes API keys, OAuth tokens, authorization headers, raw media content, raw upstream bodies, stack traces, unsafe request context, private authorization details, and secret-bearing details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

### Refactor and Validation for User Story 3

- [X] T062 [US3] Add or update reStructuredText docstrings for all new or modified US3 validation, auth, result, and error-mapping functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T063 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper, fake response, auth helper, channel helper, or upstream failure helper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T064 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`
- [X] T065 [US3] Refactor US3 validation and error mapping for consistency with existing mutation helpers while preserving watermarks-unset-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, not-found, quota, no-removal, availability, deprecation, conflict, upstream refusal, and unexpected failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T066 [P] Review `watermarks_unset` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/contracts/watermarks_unset.md`
- [X] T067 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/quickstart.md`
- [X] T068 [P] Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py`
- [X] T069 [P] Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`
- [X] T070 [P] Add any remaining cross-story regression coverage for `watermarks_unset` discovery, metadata, validation, safe errors, default registration, and catalog presence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T071 Run the complete focused YT-255 verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/255-watermarks-unset/quickstart.md`
- [X] T072 Run Layer 1 guard verification if Layer 1 files changed and fix failures using `pytest tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T073 Run code-quality verification and fix failures using `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T074 Run the full repository test suite and fix any failures using `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T075 Confirm `git status --short` contains only intended YT-255 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup and blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational and provides the MVP executable watermark-unset tool.
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
- T051 and T052 can be written in parallel with the serialized US3 unit-test work because they target contract and integration files.
- T066, T067, T068, T069, and T070 can run in parallel during polish because they inspect or update documentation, source docstrings, tests, and regression coverage in different scopes.

## Parallel Example: User Story 1

```text
Task: "T014 [P] [US1] Add contract tests for watermarks_unset in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py"
Task: "T015 [P] [US1] Add unit tests for watermarks_unset in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_watermarks.py"
Task: "T016 [P] [US1] Add integration tests for watermarks_unset in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py"
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
Task: "T051 [P] [US3] Add failure example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py"
Task: "T052 [P] [US3] Add dispatcher rejection tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_watermarks_registration.py"
Task: "T070 [P] Add remaining cross-story regression coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_watermarks_contract.py and related test files"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational Red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `watermarks_unset` can execute successful authorized watermark-removal requests through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. Deliver US1 to make the public endpoint-backed tool callable.
2. Deliver US2 to make discovery metadata, caveats, examples, quota, OAuth, channel, no-upload, rejected-delegation, no-removal, sparse acknowledgment, and unsupported-workflow guidance complete.
3. Deliver US3 to harden invalid requests, unsupported payloads, access failures, not-found cases, quota failures, no-removal outcomes, endpoint failures, deprecated behavior, upstream refusals, conflicts, and safe error details.
4. Complete polish with focused verification, full `pytest`, `ruff check .`, docstring review, and git status review.

### Parallel Team Strategy

1. Complete setup and foundational Red checks together.
2. After foundational checks are in place, split test-writing across contract, unit, and integration files where tasks are marked `[P]`.
3. Serialize source edits in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/watermarks.py` or coordinate carefully because most Green work touches the same file.
4. Run focused checks after each story, then full-suite and lint checks in polish.

## Task Counts

- **Total tasks**: 75
- **Setup**: 6 tasks
- **Foundational**: 7 tasks
- **US1**: 19 tasks
- **US2**: 13 tasks
- **US3**: 20 tasks
- **Polish**: 10 tasks

## Notes

- `[P]` tasks touch different files or are inspection/review tasks that can run without waiting on incomplete implementation.
- Story labels appear only on user story phase tasks.
- Every user story starts with Red tests, then Green implementation, then docstring/refactor/validation tasks.
- The suggested MVP scope is Phase 3, User Story 1 only.
