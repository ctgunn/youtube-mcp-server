# Tasks: YT-207 Layer 2 Tool `captions_download`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/contracts), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python code changes require reStructuredText docstrings for all new or modified functions.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with tasks that touch different files and do not depend on incomplete tasks
- **[Story]**: Which user story the task belongs to, such as `[US1]`
- All implementation tasks include exact repository paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature artifacts and existing implementation surface before adding tests or code.

- [X] T001 Review the YT-207 implementation scope in /Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/plan.md
- [X] T002 [P] Review the public tool contract requirements in /Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/contracts/captions-download-tool-contract.md
- [X] T003 [P] Review the existing concrete captions Layer 2 patterns in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T004 [P] Review the existing Layer 1 captions.download wrapper contract in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared test, export, and registration touchpoints that all user stories will use.

**CRITICAL**: No user story implementation should begin until this phase is complete.

- [X] T005 Add failing catalog coverage that `captions_download` is expected in the supported YouTube tool inventory in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T006 [P] Add failing public export coverage for `captions_download` constants and descriptor builders in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T007 [P] Add failing registration coverage that the default YouTube tool registration surface includes `captions_download` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T008 Run foundational Red checks and confirm failures from /Users/ctgunn/Projects/youtube-mcp-server
- [X] T009 Add the minimal `captions_download` public constants and export placeholders needed by later story tests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T010 Export the minimal `captions_download` public names through /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T011 Register the placeholder `captions_download` descriptor in the default tool catalog or dispatcher registration path in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T012 Add or update reStructuredText docstrings for foundational `captions_download` Python placeholders in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T013 Run foundational Red-Green checks for tool inventory and registration from /Users/ctgunn/Projects/youtube-mcp-server

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Download Caption Track Content Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `captions_download` for valid default, format-specific, and target-language caption downloads and receive a near-raw downloaded-content result.

**Independent Test**: Invoke `captions_download` with eligible authorization and a valid caption track `id`, with and without supported `tfmt` or `tlang`, then confirm the result includes `captions.download`, quota cost `200`, requested conversion context, content-form indicators, safe operation context, and downloaded caption content or a safe content representation.

### Tests for User Story 1 (REQUIRED)

Write these tests first and verify they fail before implementation.

- [X] T014 [P] [US1] Add failing contract tests for `captions_download` descriptor identity, schema, handler presence, and downloaded-content result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T015 [P] [US1] Add failing unit tests for valid default, `tfmt`, `tlang`, and combined `tfmt` plus `tlang` `captions_download` handler calls in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T016 [P] [US1] Add failing integration tests for `captions_download` discovery and executable registration in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py
- [X] T017 [P] [US1] Add failing MCP routing tests for successful `captions_download` `tools/call` results in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py
- [X] T018 [US1] Run User Story 1 Red checks and confirm failures from /Users/ctgunn/Projects/youtube-mcp-server

### Implementation for User Story 1

- [X] T019 [US1] Import and wire the Layer 1 `build_captions_download_wrapper` dependency in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T020 [US1] Implement `CAPTIONS_DOWNLOAD_INPUT_SCHEMA` for required `id`, optional `tfmt`, optional `tlang`, and optional `onBehalfOfContentOwner` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T021 [US1] Implement the default safe `captions_download` executor transport for representative downloaded-content results in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T022 [US1] Implement `validate_captions_download_arguments` for valid authorized default, format-specific, target-language, and combined conversion requests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T023 [US1] Implement `map_captions_download_result` preserving content, contentType, contentForm, sizeBytes when available, requestedFormat, requestedLanguage, endpoint, quotaCost, download summary, and delegation summary in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T024 [US1] Implement `build_captions_download_handler` and `build_captions_download_tool_descriptor` using the existing Layer 1 wrapper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T025 [US1] Export `build_captions_download_handler`, `build_captions_download_tool_descriptor`, `map_captions_download_result`, and `validate_captions_download_arguments` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T026 [US1] Add or update reStructuredText docstrings for all User Story 1 Python functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T027 [US1] Run focused User Story 1 tests and keep them green from /Users/ctgunn/Projects/youtube-mcp-server
- [X] T028 [US1] Refactor the User Story 1 result and handler implementation while preserving near-raw caption download behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

**Checkpoint**: User Story 1 should be fully functional and independently testable.

---

## Phase 4: User Story 2 - Understand Cost, Permissions, and Conversion Options Before Calling (Priority: P2)

**Goal**: A client developer can inspect `captions_download` before calling and see upstream identity, quota cost `200`, OAuth-required auth, permission-to-edit caveat, required `id`, supported `tfmt` values, `tlang` guidance, delegation guidance, and binary downloaded-content response context.

**Independent Test**: Review the tool discovery entry, contract metadata, descriptions, and examples, then confirm all required cost/auth/permission/identifier/conversion/delegation details are visible without implementation-only artifacts.

### Tests for User Story 2 (REQUIRED)

Write these tests first and verify they fail before implementation.

- [X] T029 [P] [US2] Add failing contract tests for `captions_download` quota, auth, availability, response boundary, usage notes, caveats, supported `tfmt` values, and `tlang` guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T030 [P] [US2] Add failing common contract tests that representative `captions_download` metadata stays safe and includes official quota/auth/permission/conversion fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py
- [X] T031 [P] [US2] Add failing discovery tests that `tools/list` preserves safe `captions_download` metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py
- [X] T032 [P] [US2] Add failing example-alignment tests for authorized default download, format-specific download, target-language conversion, delegated download, missing-identifier failure, unsupported-format failure, and malformed-language failure in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py
- [X] T033 [US2] Run User Story 2 Red checks and confirm failures from /Users/ctgunn/Projects/youtube-mcp-server

### Implementation for User Story 2

- [X] T034 [US2] Implement `build_captions_download_contract` with quota cost `200`, OAuth-required auth, permission-sensitive availability, usage notes, caveats, and response boundary metadata in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T035 [US2] Add `captions_download` representative examples and safe usage notes to /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T036 [US2] Add `captions_download` resource-family metadata where needed for catalog alignment in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py
- [X] T037 [US2] Ensure dispatcher discovery preserves `captions_download` safe metadata, input schema, quota, auth, availability, conversion notes, and usage notes in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T038 [US2] Export `build_captions_download_contract` and `CAPTIONS_DOWNLOAD_QUOTA_COST` through /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T039 [US2] Add or update reStructuredText docstrings for all User Story 2 Python functions changed in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T040 [US2] Run focused User Story 2 discovery, contract, and example tests from /Users/ctgunn/Projects/youtube-mcp-server
- [X] T041 [US2] Refactor User Story 2 metadata wording to remove duplication while preserving caller-facing quota, auth, permission, identifier, format, language, delegation, and response-form visibility in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Reject Unsupported Caption Download Requests Clearly (Priority: P3)

**Goal**: Invalid `captions_download` requests receive stable caller-facing validation and safe error categories for missing `id`, unsupported `tfmt`, malformed `tlang`, missing OAuth, invalid delegation, insufficient permission, conversion failure, missing caption tracks, quota failure, unavailable upstream service, and unexpected upstream failures.

**Independent Test**: Submit representative invalid requests and upstream failure simulations, then confirm each response clearly identifies the violated caption-download rule without exposing secrets, raw private caption content, binary payloads, stack traces, or signed URLs.

### Tests for User Story 3 (REQUIRED)

Write these tests first and verify they fail before implementation.

- [X] T042 [P] [US3] Add failing unit tests for missing `id`, blank `id`, unsupported `tfmt`, malformed `tlang`, unsupported fields, missing OAuth, and delegated download without OAuth in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T043 [P] [US3] Add failing contract tests for safe `captions_download` error categories and endpoint-specific upstream mappings for `couldNotConvert`, `forbidden`, and `captionNotFound` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T044 [P] [US3] Add failing MCP routing tests for invalid `captions_download` `tools/call` requests returning safe structured errors in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py
- [X] T045 [P] [US3] Add failing regression coverage that existing `captions_list`, `captions_insert`, and `captions_update` validation behavior is unchanged in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T046 [US3] Run User Story 3 Red checks and confirm failures from /Users/ctgunn/Projects/youtube-mcp-server

### Implementation for User Story 3

- [X] T047 [US3] Implement `CaptionsDownloadToolError` with safe category and details fields in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T048 [US3] Harden `validate_captions_download_arguments` for missing `id`, blank `id`, unsupported `tfmt`, malformed `tlang`, unsupported fields, missing OAuth, and delegated download without OAuth in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T049 [US3] Implement upstream error mapping for `couldNotConvert`, `forbidden`, `captionNotFound`, quota exhaustion, unavailable endpoint, and unexpected upstream failures in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T050 [US3] Ensure MCP `tools/call` error handling exposes safe `captions_download` error category, tool name, and remediation details in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T051 [US3] Add or update reStructuredText docstrings for all User Story 3 Python functions changed in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T052 [US3] Run focused User Story 3 validation and routing tests from /Users/ctgunn/Projects/youtube-mcp-server
- [X] T053 [US3] Refactor User Story 3 validation and error mapping to reuse shared Layer 2 conventions without changing caller-facing behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

**Checkpoint**: All user stories should be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full feature, clean up cross-story rough edges, and capture final evidence.

- [X] T054 [P] Review `captions_download` quickstart coverage and update implementation evidence placeholders in /Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/quickstart.md
- [X] T055 [P] Review public examples and tests for absence of API keys, OAuth tokens, stack traces, signed URLs, raw private caption content, binary payloads, and secret values in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T056 [P] Review reStructuredText docstrings for all new or changed `captions_download` Python functions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T057 Run the full focused YT-207 validation command from /Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/quickstart.md
- [X] T058 Run `python3 -m pytest` from /Users/ctgunn/Projects/youtube-mcp-server and fix any failures before completion
- [X] T059 Run `python3 -m ruff check .` from /Users/ctgunn/Projects/youtube-mcp-server and fix any failures before completion
- [X] T060 Record final validation evidence in /Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion - MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and may run alongside US1 after placeholder exports exist, but final discovery metadata should be checked after US1 descriptor work.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and can run alongside US1 after shared validation helper names are agreed, but final error behavior should be checked after US1 handler work.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on US2 or US3; delivers the executable MVP.
- **User Story 2 (P2)**: Independent metadata/discovery increment; benefits from US1 descriptor shape but must remain testable through discovery and contract tests.
- **User Story 3 (P3)**: Independent validation/error increment; benefits from US1 handler shape but must remain testable through invalid request and error mapping tests.

### Within Each User Story

- Red tests must be written and verified failing before implementation.
- Implement only enough Green behavior to pass the story tests.
- Update reStructuredText docstrings before story completion.
- Refactor only after story tests pass.
- Run focused tests after refactor.
- The feature is not complete until `python3 -m pytest` and `python3 -m ruff check .` pass after final code changes.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel during setup.
- T006 and T007 can run in parallel with T005 during foundational Red work.
- T014, T015, T016, and T017 can run in parallel for User Story 1 Red tests.
- T029, T030, T031, and T032 can run in parallel for User Story 2 Red tests.
- T042, T043, T044, and T045 can run in parallel for User Story 3 Red tests.
- T054, T055, and T056 can run in parallel during polish.

---

## Parallel Example: User Story 1

```bash
Task: "T014 [P] [US1] Add failing contract tests for `captions_download` descriptor identity, schema, handler presence, and downloaded-content result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T015 [P] [US1] Add failing unit tests for valid default, `tfmt`, `tlang`, and combined `tfmt` plus `tlang` `captions_download` handler calls in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T016 [P] [US1] Add failing integration tests for `captions_download` discovery and executable registration in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py"
Task: "T017 [P] [US1] Add failing MCP routing tests for successful `captions_download` `tools/call` results in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Parallel Example: User Story 2

```bash
Task: "T029 [P] [US2] Add failing contract tests for `captions_download` quota, auth, availability, response boundary, usage notes, caveats, supported `tfmt` values, and `tlang` guidance in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T030 [P] [US2] Add failing common contract tests that representative `captions_download` metadata stays safe and includes official quota/auth/permission/conversion fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T031 [P] [US2] Add failing discovery tests that `tools/list` preserves safe `captions_download` metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py"
Task: "T032 [P] [US2] Add failing example-alignment tests for authorized default download, format-specific download, target-language conversion, delegated download, missing-identifier failure, unsupported-format failure, and malformed-language failure in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py"
```

## Parallel Example: User Story 3

```bash
Task: "T042 [P] [US3] Add failing unit tests for missing `id`, blank `id`, unsupported `tfmt`, malformed `tlang`, unsupported fields, missing OAuth, and delegated download without OAuth in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T043 [P] [US3] Add failing contract tests for safe `captions_download` error categories and endpoint-specific upstream mappings for `couldNotConvert`, `forbidden`, and `captionNotFound` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T044 [P] [US3] Add failing MCP routing tests for invalid `captions_download` `tools/call` requests returning safe structured errors in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
Task: "T045 [P] [US3] Add failing regression coverage that existing `captions_list`, `captions_insert`, and `captions_update` validation behavior is unchanged in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational exports and registration expectations.
3. Complete Phase 3 User Story 1.
4. Validate User Story 1 independently with focused captions contract, unit, integration, and routing tests.
5. Stop for review or demo if only the executable download MVP is needed.

### Incremental Delivery

1. Setup plus Foundational gives a visible placeholder and failing tests for the new public tool.
2. User Story 1 adds executable default, format-specific, and target-language download behavior.
3. User Story 2 enriches discovery, metadata, examples, quota, auth, permission, and conversion visibility.
4. User Story 3 hardens invalid request handling and upstream error mapping.
5. Polish verifies the full repository and lint after final changes.

### Parallel Team Strategy

1. Complete Setup and Foundational together.
2. After Foundational:
   - Developer A: User Story 1 handler/result behavior.
   - Developer B: User Story 2 metadata/discovery/examples.
   - Developer C: User Story 3 validation/error handling.
3. Integrate by running the focused YT-207 command, then `python3 -m pytest`, then `python3 -m ruff check .`.

## Notes

- [P] tasks touch separate files or are Red-test tasks that can be authored independently.
- `[US1]`, `[US2]`, and `[US3]` map directly to the prioritized user stories in /Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/spec.md.
- Every changed Python function must have a reStructuredText docstring before its story is marked complete.
- Tests must fail before the corresponding implementation task begins.
