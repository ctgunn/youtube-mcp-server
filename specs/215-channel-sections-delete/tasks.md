# Tasks: Layer 2 Tool `channelSections_delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/contracts/channelSections_delete.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/quickstart.md`

**Tests**: Test tasks are mandatory and appear before implementation in each story. Completion requires focused checks, a full `pytest` run, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently after shared foundation work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches a different file or only reads context
- **[Story]**: User story label for story phases only
- Every task includes an absolute file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing implementation surface and feature artifacts before writing tests.

- [X] T001 Review the YT-215 plan and contract decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/plan.md`
- [X] T002 [P] Review the public interface contract for `channelSections_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/contracts/channelSections_delete.md`
- [X] T003 [P] Review the existing Layer 2 channel-section implementation patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T004 [P] Review existing `channelSections` tests to preserve local style in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T005 [P] Review existing `channelSections` unit test patterns in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared Red checks for export, representative-contract, and registry availability that all stories rely on.

**Critical**: No user story implementation should begin until these failing shared tests are in place.

- [X] T006 Add failing scaffolding checks for `CHANNEL_SECTIONS_DELETE_TOOL_NAME`, `CHANNEL_SECTIONS_DELETE_QUOTA_COST`, and `build_channel_sections_delete_tool_descriptor` exports in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T007 Add failing representative metadata coverage for `build_channel_sections_delete_contract()` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 Add failing default registry discovery check for `channelSections_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`
- [X] T009 Run the shared Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py -k 'channel_sections_delete or channelSections_delete or captions_delete_public_metadata_is_safe_and_complete'` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Shared Red tests exist and fail for missing `channelSections_delete` support.

---

## Phase 3: User Story 1 - Delete Channel Sections Through a Public Tool (Priority: P1) MVP

**Goal**: A power user can call `channelSections_delete` with OAuth and a valid channel-section ID and receive a deletion acknowledgment while the tool performs exactly one endpoint-backed delete operation.

**Independent Test**: Invoke the descriptor handler with `{"id": "section-123"}` and eligible OAuth, confirm the result includes `endpoint: channelSections.delete`, `quotaCost: 50`, `deleted: true`, safe target context, and no fabricated deleted channel-section fields.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add failing contract tests for `channelSections_delete` identity, required `id`, result boundary, and no fabricated resource fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T011 [P] [US1] Add failing unit tests for successful result mapping and one-wrapper-call handler execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T012 [P] [US1] Add failing dispatcher invocation test for an authorized default `channelSections_delete` acknowledgment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`
- [X] T013 [US1] Run the US1 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py -k delete` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1 (Green)

- [X] T014 [US1] Add `CHANNEL_SECTIONS_DELETE_*` constants, input schema, error class, and default delete transport scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T015 [US1] Implement `build_channel_sections_delete_contract()`, `map_channel_sections_delete_result()`, and deletion response-boundary metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T016 [US1] Implement `build_channel_sections_delete_handler()` and `build_channel_sections_delete_tool_descriptor()` using the existing Layer 1 `build_channel_sections_delete_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T017 [US1] Export `channelSections_delete` constants, error type, validator, mapper, contract builder, handler builder, and descriptor builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T018 [US1] Register `build_channel_sections_delete_tool_descriptor()` in the default tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T019 [US1] Add reStructuredText docstrings for every new or modified `channelSections_delete` function, helper, and test fake method touched for US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

### Refactor and Validation for User Story 1

- [X] T020 [US1] Refactor the US1 implementation for naming consistency with existing `channelSections_insert` and `channelSections_update` helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T021 [US1] Run focused US1 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py -k delete` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Deletion Risk Before Calling (Priority: P2)

**Goal**: A client developer can inspect discovery metadata, usage notes, caveats, and examples and understand endpoint identity, quota cost 50, OAuth requirement, required `id`, partner context, and destructive deletion semantics before invocation.

**Independent Test**: Review `channelSections_delete` metadata and examples from the tool descriptor and confirm all required quota, OAuth, deletion, partner-context, no-body, and out-of-scope workflow disclosures are visible.

### Tests for User Story 2 (Red)

- [X] T022 [P] [US2] Add failing contract tests for quota, OAuth, destructive deletion caveats, no-body policy, partner context, and out-of-scope workflow disclosures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T023 [P] [US2] Add failing shared representative contract test for safe `channelSections_delete` public metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T024 [US2] Add failing caller example coverage for authorized delete, partner delete, missing ID, invalid ID, unsupported option, missing target, and missing OAuth in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T025 [US2] Run the US2 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k 'delete and metadata'` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2 (Green)

- [X] T026 [US2] Add `CHANNEL_SECTIONS_DELETE_DESCRIPTION`, `CHANNEL_SECTIONS_DELETE_USAGE_NOTES`, `CHANNEL_SECTIONS_DELETE_CAVEATS`, and `CHANNEL_SECTIONS_DELETE_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T027 [US2] Populate `channelSections_delete` response convention and metadata fields for quota, OAuth, availability, destructive delete, no-body handling, partner context, and disallowed workflows in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T028 [US2] Add `channelSections_delete` to `REPRESENTATIVE_YOUTUBE_TOOL_CONTRACTS` imports and tuple in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T029 [US2] Export `CHANNEL_SECTIONS_DELETE_DESCRIPTION`, `CHANNEL_SECTIONS_DELETE_USAGE_NOTES`, `CHANNEL_SECTIONS_DELETE_CAVEATS`, and `CHANNEL_SECTIONS_DELETE_CALLER_EXAMPLES` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T030 [US2] Add or update reStructuredText docstrings for metadata and example helper functions changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

### Refactor and Validation for User Story 2

- [X] T031 [US2] Refactor repeated quota, OAuth, and caveat wording while preserving required caller-facing text in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T032 [US2] Run focused US2 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py -k delete` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently verifiable through public discovery metadata and examples.

---

## Phase 5: User Story 3 - Reject Unsupported Delete Requests Clearly (Priority: P3)

**Goal**: A caller receives clear validation or mapped upstream failure feedback for missing OAuth, missing or invalid `id`, unsupported options, partner-context problems, missing target sections, authorization failures, quota failures, unavailable endpoints, deprecation, and unexpected upstream failures.

**Independent Test**: Submit representative invalid requests and fake upstream failures to the handler and confirm each response uses the shared Layer 2 category with safe details and no leaked tokens, owner IDs, stack traces, or raw unsafe diagnostics.

### Tests for User Story 3 (Red)

- [X] T033 [P] [US3] Add failing unit validation tests for missing OAuth, missing `id`, empty `id`, non-string `id`, empty `onBehalfOfContentOwner`, request body, bulk delete, recovery, layout repair, and playlist cleanup fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T034 [US3] Add failing unit tests for upstream error mapping to `invalid_request`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T035 [P] [US3] Add failing contract test proving public errors and results do not leak OAuth tokens, CMS owner IDs, stack traces, API keys, or raw unsafe diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T036 [US3] Run the US3 Red checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py -k delete` from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3 (Green)

- [X] T037 [US3] Implement `validate_channel_sections_delete_arguments()` and invalid-request helpers for required OAuth, required `id`, partner context, and unsupported fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T038 [US3] Implement `_delete_auth_context()` and safe partner-context flag handling for delete requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T039 [US3] Implement `_map_delete_upstream_error()` for shared Layer 2 categories and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T040 [US3] Wire delete validation, OAuth context, and upstream error mapping into `build_channel_sections_delete_handler()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T041 [US3] Add or update reStructuredText docstrings for every validator, auth helper, error mapper, and fake wrapper method changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

### Refactor and Validation for User Story 3

- [X] T042 [US3] Refactor delete validation and error mapping to avoid duplicating unrelated insert/update logic in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T043 [US3] Run focused US3 checks with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py -k delete` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: All user stories are independently functional and failure behavior is caller-safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation alignment, and repository-wide quality checks.

- [X] T044 [P] Verify the implementation matches quickstart examples in `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/quickstart.md`
- [X] T045 [P] Review all changed Python functions for reStructuredText docstrings covering purpose, inputs, outputs, quota cost, OAuth behavior, destructive deletion, deletion acknowledgment, and partner-context notes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T046 [P] Review public exports for stale or missing `channelSections_delete` symbols in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T047 Run focused feature verification with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T048 Run `ruff check .` and fix any lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T049 Run the full repository test suite with `pytest` and fix any failing tests before completion from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T050 Record final focused test, full-suite, and lint evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/215-channel-sections-delete/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; starts immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational; MVP scope.
- **User Story 2 (Phase 4)**: Depends on Foundational and can proceed after US1 contract builder exists; metadata work is independently testable.
- **User Story 3 (Phase 5)**: Depends on Foundational and can proceed after US1 handler skeleton exists; validation work is independently testable.
- **Polish (Phase 6)**: Depends on selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Core tool execution and deletion acknowledgment; no dependency on US2 or US3.
- **US2 (P2)**: Metadata and examples; relies on the contract/descriptor shape created by US1 but can be reviewed independently through discovery metadata.
- **US3 (P3)**: Validation and error handling; relies on the handler and error type created by US1 but can be tested independently through invalid requests and fake upstream failures.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation.
- Green implementation must be the smallest endpoint-backed code needed to satisfy that story.
- reStructuredText docstrings must be complete before story completion.
- Refactor tasks must preserve behavior and rerun focused tests.
- The feature is not complete until full `pytest` and `ruff check .` pass.

## Parallel Opportunities

- Setup tasks T002, T003, T004, and T005 can run in parallel because they only read different files.
- Foundational tests T006, T007, and T008 touch different test files and can be drafted in parallel.
- US1 Red tests T010, T011, and T012 touch different files and can be drafted in parallel.
- US2 Red tests T022 and T023 touch different files and can be drafted in parallel; T024 shares a file with T022 and should be coordinated.
- US3 Red tests T033 and T034 share one file and should be sequenced; T035 can run in parallel in the contract test file if coordinated with US2 edits.
- Polish review tasks T044, T045, and T046 can run in parallel before final command tasks.

## Parallel Example: User Story 1

```bash
Task: "T010 Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task: "T011 Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py"
Task: "T012 Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "T022 Add metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task: "T023 Add representative metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T033 Add invalid-request validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py"
Task: "T035 Add no-leak contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for `channelSections_delete` execution and deletion acknowledgment.
3. Stop and validate US1 independently with the focused delete tests.
4. Use US1 as the demoable MVP because it exposes the public tool and successful delete path.

### Incremental Delivery

1. Add US1 to expose and execute the tool.
2. Add US2 to harden public metadata, caveats, and examples.
3. Add US3 to complete validation and safe upstream error behavior.
4. Finish with focused checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One contributor drafts shared export/registry tests while another drafts story-level contract tests.
2. After Foundational Red checks are in place, implementation can split by file ownership: channel-section module, exports/dispatcher, and tests.
3. Coordinate edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` because all stories eventually modify that file.

## Independent Test Criteria Summary

- **US1**: Valid OAuth delete with `id` returns one deletion acknowledgment for `channelSections.delete` with quota cost 50 and no fabricated deleted resource fields.
- **US2**: Tool discovery metadata, usage notes, caveats, and examples visibly disclose upstream identity, quota cost 50, OAuth requirement, required `id`, partner context, destructive deletion, and out-of-scope behaviors.
- **US3**: Invalid inputs and fake upstream failures return shared safe Layer 2 categories with actionable details and no leaked credentials, owner identifiers, stack traces, or unsafe diagnostics.

## Notes

- `[P]` tasks are intentionally conservative; tasks sharing the same Python file should be coordinated even when logically independent.
- Every Python code task must preserve or add reStructuredText docstrings before the story checkpoint.
- Do not implement lookup-before-delete, bulk deletion, recovery, layout repair, playlist cleanup, analytics, enrichment, or channel branding behavior.
