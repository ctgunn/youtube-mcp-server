# Tasks: YT-205 Layer 2 Tool `captions_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/data-model.md), [contracts/captions-insert-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/contracts/captions-insert-tool-contract.md)

**Tests**: Mandatory. Each user story starts with failing tests, proceeds to minimum implementation, then refactors with focused validation. Final completion requires `python3 -m pytest` and `python3 -m ruff check .`.

**Organization**: Tasks are grouped by user story so each story can be independently implemented and tested.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature context and implementation surface before writing Red tests.

- [X] T001 Review YT-205 plan, spec, research, data model, and contract scope in /Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/plan.md
- [X] T002 [P] Review existing `captions_list` implementation pattern in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T003 [P] Review existing Layer 1 `captions.insert` wrapper behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py
- [X] T004 [P] Review existing captions test layout in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add cross-story failing checks for public catalog/export/registration expectations that every story depends on.

**CRITICAL**: No user story implementation should begin until these Red checks exist and fail for the missing `captions_insert` tool.

- [X] T005 [P] Add failing public export expectations for `CAPTIONS_INSERT_TOOL_NAME`, `CaptionsInsertToolError`, and `build_captions_insert_tool_descriptor` in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T006 [P] Add failing catalog contract expectations that `captions_insert` exists as a concrete tool aligned to representative metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T007 [P] Add failing default registration expectations for `captions_insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
- [X] T008 Run the foundational Red checks and confirm they fail for missing `captions_insert` using /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py

**Checkpoint**: Foundation Red checks identify the missing public tool, export, catalog, and registration surface.

---

## Phase 3: User Story 1 - Create Caption Tracks Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can invoke `captions_insert` with eligible authorization, caption metadata, and caption media input and receive a near-raw created caption resource.

**Independent Test**: Invoke the dispatcher descriptor or registered tool with `part`, `body.snippet.videoId`, `body.snippet.language`, `body.snippet.name`, and `media`, then confirm the result includes endpoint `captions.insert`, quota cost `400`, requested parts, safe metadata/media summaries, and the created caption resource.

### Tests for User Story 1 (Red)

- [X] T009 [P] [US1] Add failing unit tests for `CAPTIONS_INSERT_INPUT_SCHEMA` required fields and successful argument validation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T010 [P] [US1] Add failing unit tests for `map_captions_insert_result` preserving created caption resource fields and safe media summary in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T011 [P] [US1] Add failing handler test proving `build_captions_insert_tool_descriptor` invokes the injected Layer 1 wrapper for an authorized metadata-plus-media request in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T012 [P] [US1] Add failing integration test registering and executing `captions_insert` through `InMemoryToolDispatcher` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py

### Implementation for User Story 1 (Green)

- [X] T013 [US1] Add `captions_insert` constants, strict input schema, description, usage notes, and caveats in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T014 [US1] Implement `CaptionsInsertToolError`, default insert executor transport, `build_captions_insert_contract`, and safe metadata conversion in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T015 [US1] Implement `validate_captions_insert_arguments`, requested-parts parsing, safe metadata summary, and safe media summary helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T016 [US1] Implement `map_captions_insert_result`, upstream error mapping, `build_captions_insert_handler`, and `build_captions_insert_tool_descriptor` in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T017 [US1] Export `captions_insert` public symbols from /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T018 [US1] Register `build_captions_insert_tool_descriptor` in default dispatcher tool definitions in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T019 [US1] Add or update reStructuredText docstrings for every new or modified `captions_insert` function and helper in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

### Refactor and Validate User Story 1

- [X] T020 [US1] Refactor `captions_insert` implementation for near-raw mutation result consistency with `captions_list` while keeping tests green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T021 [US1] Run focused US1 tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py

**Checkpoint**: User Story 1 is independently callable through the descriptor and dispatcher registration path.

---

## Phase 4: User Story 2 - Understand Cost, Authorization, and Upload Rules Before Calling (Priority: P2)

**Goal**: A client developer can inspect `captions_insert` before invocation and understand upstream identity, quota cost `400`, OAuth-required auth, media-upload requirements, required metadata, delegation caveats, and deprecated `sync`.

**Independent Test**: Review tool discovery/contract metadata and examples, then confirm they expose `captions.insert`, quota cost `400`, `oauth_required`, required `body` and `media`, optional `onBehalfOfContentOwner`, and a deprecated `sync` caveat.

### Tests for User Story 2 (Red)

- [X] T022 [P] [US2] Add failing contract tests for `captions_insert` identity, quota, auth, input contract, usage notes, caveats, and response boundary in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T023 [P] [US2] Add failing tool catalog tests comparing concrete `captions_insert` metadata with representative `captions_insert` expectations in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py
- [X] T024 [P] [US2] Add failing `tools/list` discovery tests proving `captions_insert` exposes safe metadata, quota, auth, and upload requirements in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py
- [X] T025 [P] [US2] Add failing shared scaffolding tests for safe public metadata and representative usage notes for `captions_insert` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py

### Implementation for User Story 2 (Green)

- [X] T026 [US2] Update `captions_insert` metadata, usage notes, caveats, response boundary, and input contract details to satisfy discovery requirements in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T027 [US2] Add `captions_insert` exports to shared YouTube common public API in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py
- [X] T028 [US2] Add or update representative `captions_insert` metadata expectations if needed in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py
- [X] T029 [US2] Ensure dispatcher list metadata preserves `captions_insert` metadata without leaking unsafe fields in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T030 [US2] Add or update reStructuredText docstrings for metadata, descriptor, and export helpers changed for US2 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

### Refactor and Validate User Story 2

- [X] T031 [US2] Refactor duplicate quota/auth/upload wording while preserving public discovery behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T032 [US2] Run focused US2 discovery and contract tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py

**Checkpoint**: User Story 2 is independently verifiable through contracts and discovery without invoking the tool.

---

## Phase 5: User Story 3 - Reject Unsupported Caption Creation Requests Clearly (Priority: P3)

**Goal**: A caller gets safe, specific validation feedback for missing metadata, missing media, missing OAuth, unsupported media descriptors, invalid delegation, deprecated `sync` handling, and upstream failure categories.

**Independent Test**: Submit representative invalid requests to `validate_captions_insert_arguments` and the dispatcher handler, then confirm failures use safe categories/details and never expose credentials or raw caption content.

### Tests for User Story 3 (Red)

- [X] T033 [P] [US3] Add failing unit tests for missing `part`, missing `body`, missing `body.snippet.videoId`, missing `body.snippet.language`, and missing `body.snippet.name` in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T034 [P] [US3] Add failing unit tests for missing `media`, unsupported media descriptors, and safe media-content handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T035 [P] [US3] Add failing unit tests for missing OAuth, delegated owner without OAuth, deprecated `sync` caveat handling, and safe error details in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py
- [X] T036 [P] [US3] Add failing contract tests for safe `CaptionsInsertToolError` categories and sanitized details in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T037 [P] [US3] Add failing method-routing tests for valid and invalid `captions_insert` `tools/call` behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py

### Implementation for User Story 3 (Green)

- [X] T038 [US3] Harden `validate_captions_insert_arguments` for required metadata, media, OAuth, delegation, unsupported fields, and deprecated `sync` validation in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T039 [US3] Harden `CaptionsInsertToolError` details and upstream error mapping for invalid request, auth, authorization, quota, conflict, not found, unavailable, and upstream failure categories in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T040 [US3] Update dispatcher or protocol error propagation for safe `captions_insert` `tools/call` failures if required in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T041 [US3] Add or update reStructuredText docstrings for validation and error-mapping functions changed for US3 in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

### Refactor and Validate User Story 3

- [X] T042 [US3] Refactor validation/error helpers to stay local to `captions_insert` unless a shared helper is clearly reused in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py
- [X] T043 [US3] Run focused US3 validation and routing tests and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py

**Checkpoint**: User Story 3 is independently verifiable through validation, dispatcher, and method-routing failures.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the complete feature stays additive, safe, documented, and regression-free.

- [X] T044 [P] Review and update YT-205 quickstart evidence notes after implementation in /Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/quickstart.md
- [X] T045 [P] Review security safety for examples, metadata, errors, and tests to ensure no credentials, raw caption content, signed URLs, or stack traces leak in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py
- [X] T046 [P] Run Layer 1 guard tests if wrapper code was touched and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py
- [X] T047 Run complete focused YouTube captions and registration test set and fix failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py
- [X] T048 Run full repository test suite with `python3 -m pytest` and fix any failures before completion in /Users/ctgunn/Projects/youtube-mcp-server/tests
- [X] T049 Run lint validation with `python3 -m ruff check .` and fix any failures before completion in /Users/ctgunn/Projects/youtube-mcp-server/src
- [X] T050 Review every new or modified Python function for reStructuredText docstrings before completion in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks implementation tasks.
- **User Story 1 (Phase 3)**: Depends on Foundational Red checks and provides the MVP executable tool.
- **User Story 2 (Phase 4)**: Depends on Foundational Red checks; can be developed in parallel with US1 after shared descriptor naming is agreed, but final discovery checks depend on the descriptor from US1.
- **User Story 3 (Phase 5)**: Depends on Foundational Red checks; can be developed in parallel with US1 after validation helper names are agreed, but final routing checks depend on descriptor registration from US1.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: MVP. No dependency on US2 or US3 after Foundational.
- **US2 (P2)**: Independent discovery/metadata value, but shares descriptor constants and exports from US1.
- **US3 (P3)**: Independent validation/error value, but shares handler and validator surfaces from US1.

### Within Each User Story

- Write Red tests first and confirm they fail before implementation.
- Implement minimum Green code only after Red checks exist.
- Add or update reStructuredText docstrings for every changed Python function before story completion.
- Refactor only after focused tests pass.
- Re-run focused tests for the story after refactor.

## Parallel Opportunities

- T002, T003, and T004 can run in parallel during setup.
- T005, T006, and T007 can run in parallel because they touch separate test files.
- US1 Red tests T009, T010, T011, and T012 can run in parallel once shared names are agreed.
- US2 Red tests T022, T023, T024, and T025 can run in parallel because they touch separate contract/discovery files.
- US3 Red tests T033, T034, T035, T036, and T037 can be split across unit, contract, and routing files.
- Polish checks T044, T045, and T046 can run in parallel before the final full-suite and lint gates.

## Parallel Example: User Story 1

```bash
Task: "T009 [US1] Add failing unit tests for CAPTIONS_INSERT_INPUT_SCHEMA in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T012 [US1] Add failing integration test registering and executing captions_insert in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_captions_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T022 [US2] Add failing contract tests for captions_insert metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_captions_contract.py"
Task: "T024 [US2] Add failing tools/list discovery tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py"
```

## Parallel Example: User Story 3

```bash
Task: "T033 [US3] Add failing unit tests for missing caption metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_captions.py"
Task: "T037 [US3] Add failing method-routing tests for captions_insert tools/call behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 only.
3. Validate that `captions_insert` can be built, registered, and called with valid metadata plus media input.
4. Stop and demo the MVP before broadening metadata/discovery and invalid-request coverage.

### Incremental Delivery

1. Add US1 executable tool behavior.
2. Add US2 discovery metadata and caller-facing guidance.
3. Add US3 invalid-request and safe error behavior.
4. Complete polish, full test suite, and lint validation.

### Validation Commands

```bash
python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py
python3 -m pytest
python3 -m ruff check .
```

## Notes

- `[P]` tasks touch different files or can be prepared independently before implementation merges them.
- `[US1]`, `[US2]`, and `[US3]` labels map to prioritized user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/spec.md).
- All Python implementation tasks require reStructuredText docstring coverage before the story is complete.
- Final feature completion requires the full repository test suite and Ruff lint command to pass after the last code change.
