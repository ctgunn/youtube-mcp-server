# Tasks: YT-210 Layer 2 Tool `channels_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/`  
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/contracts/channels-list-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/quickstart.md`

**Tests**: Tests are mandatory. Each user story begins with Red test tasks, then Green implementation, then Refactor/verification. Completion requires `python3 -m pytest` and `python3 -m ruff check .` after final code changes. Every new or modified Python function must have a reStructuredText docstring before its story is complete.

**Organization**: Tasks are grouped by independently testable user story in priority order.

## Phase 1: Setup (Shared Orientation)

**Purpose**: Confirm the feature scope and existing seams before creating Red tests.

- [X] T001 Review YT-210 scope, selector rules, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/plan.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/contracts/channels-list-tool-contract.md`
- [X] T002 [P] Review existing concrete Layer 2 tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`
- [X] T003 [P] Review existing registration, discovery, and method-routing seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the channels Layer 2 module seam and shared exports that all user stories depend on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T004 [P] Add failing concrete channels resource-family placement expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T005 Create the concrete channels Layer 2 module skeleton with module docstring, constants placeholders, and `__all__` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T006 Export the preliminary channels module symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T007 Run foundational scaffolding tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve Channels Through a Public Tool (Priority: P1) MVP

**Goal**: `channels_list` is discoverable, callable, and returns near-raw channel collection results with endpoint identity, quota cost, requested parts, selected lookup mode, pagination fields, and successful empty collections.

**Independent Test**: Invoke `channels_list` with supported `id`, `forHandle`, `forUsername`, and authorized `mine` lookup requests, then confirm the result preserves channel items or an empty collection, requested parts, selected selector, pagination details, and `channels.list` metadata.

### Tests for User Story 1 (Red)

- [X] T008 [P] [US1] Add failing contract tests for `channels_list` descriptor identity, result shape, empty collection behavior, and pagination preservation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T009 [P] [US1] Add failing unit tests for `map_channels_list_result()`, selected selector context, requested part normalization, and default empty-result handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`
- [X] T010 [P] [US1] Add failing integration tests proving default dispatcher registration exposes executable `channels_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py`
- [X] T011 [US1] Run the US1 Red tests and confirm they fail for missing implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py`

### Implementation for User Story 1 (Green)

- [X] T012 [US1] Implement `CHANNELS_LIST_TOOL_NAME`, `CHANNELS_LIST_QUOTA_COST`, selector constants, input schema, description, usage-note placeholders, caveat placeholders, and `ChannelsListToolError` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T013 [US1] Implement `_default_channels_transport()` and `_default_executor()` with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T014 [US1] Implement `build_channels_list_contract()` and `build_channels_list_tool_descriptor()` using `YouTubeToolContract` and `ResponseBoundary` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T015 [US1] Implement `_active_selectors()`, `_requested_parts()`, and `map_channels_list_result()` for returned items, selected selector, requested parts, `nextPageToken`, `prevPageToken`, and `pageInfo` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T016 [US1] Implement `build_channels_list_handler()` that calls `build_channels_list_wrapper()` through the injected executor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T017 [US1] Export `channels_list` constants, error type, contract builder, handler builder, descriptor builder, result mapper, and validator symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T018 [US1] Register `build_channels_list_tool_descriptor()` in the default registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T019 [US1] Add or update reStructuredText docstrings for every new or modified `channels_list` function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T020 [US1] Run focused US1 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

### Refactor for User Story 1

- [X] T021 [US1] Refactor duplicate list-result mapping or selector helper logic while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

**Checkpoint**: User Story 1 is independently functional and can serve as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Access, and Filter Rules Before Calling (Priority: P2)

**Goal**: Tool discovery, descriptions, usage notes, caveats, and examples clearly show endpoint identity, quota cost `1`, mixed auth, selectors `id`, `mine`, `forHandle`, `forUsername`, OAuth requirement for `mine`, pagination behavior, empty-result behavior, and out-of-scope boundaries.

**Independent Test**: Inspect the `channels_list` descriptor and representative examples, then confirm a caller can identify quota, auth mode, supported selectors, `mine` authorization, pagination, empty-result behavior, and excluded higher-level channel workflows without invoking implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T022 [P] [US2] Add failing metadata contract tests for quota, mixed auth, supported selectors, `mine` OAuth guidance, pagination notes, empty-result notes, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T023 [P] [US2] Add failing representative catalog alignment tests for `channels_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T024 [P] [US2] Add failing default registry metadata tests for `channels_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T025 [US2] Run the US2 Red tests and confirm they fail for incomplete metadata and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 2 (Green)

- [X] T026 [US2] Fill `CHANNELS_LIST_USAGE_NOTES`, `CHANNELS_LIST_CAVEATS`, and `CHANNELS_LIST_CALLER_EXAMPLES` for `id`, `forHandle`, `forUsername`, `mine`, pagination, empty result, conflicting selectors, and auth failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T027 [US2] Extend `build_channels_list_contract()` metadata with selector guidance, response convention, response boundary, availability state, and safe caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T028 [US2] Add a representative `channels_list` contract and alignment import in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T029 [US2] Export `CHANNELS_LIST_CALLER_EXAMPLES` and any new metadata symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T030 [US2] Add or update reStructuredText docstrings for all metadata and example helpers changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T031 [US2] Run focused US2 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

### Refactor for User Story 2

- [X] T032 [US2] Refactor duplicated quota, auth, selector, and caveat wording while keeping US2 metadata tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

**Checkpoint**: User Story 2 is independently verifiable through discovery and contract metadata.

---

## Phase 5: User Story 3 - Reject Unsupported Channel Lookup Requests Clearly (Priority: P3)

**Goal**: Invalid `channels_list` requests are rejected with stable, safe, caller-facing feedback for missing `part`, missing selector, empty selector values, conflicting selectors, invalid pagination, unsupported fields, missing OAuth for `mine`, and upstream failures.

**Independent Test**: Submit invalid requests to `channels_list` and confirm each failure uses a safe shared Layer 2 category, identifies the correct field or selector when safe, distinguishes auth failures from no-match lookups, and excludes credentials, tokens, stack traces, and private channel data.

### Tests for User Story 3 (Red)

- [X] T033 [P] [US3] Add failing unit tests for missing `part`, missing selector, empty `id`, empty `forHandle`, empty `forUsername`, conflicting selectors, invalid `maxResults`, and unsupported fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`
- [X] T034 [P] [US3] Add failing unit tests for `mine` without OAuth, API-key attempts for owner-scoped lookup, safe auth details, and selected auth context behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`
- [X] T035 [P] [US3] Add failing contract tests for safe error categories and no credential, token, stack trace, or private channel data leakage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T036 [P] [US3] Add failing method-routing tests for invalid `channels_list` calls through the dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T037 [US3] Run the US3 Red tests and confirm they fail for incomplete validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 3 (Green)

- [X] T038 [US3] Implement `validate_channels_list_arguments()` with required `part`, exact-one selector, non-empty selector, `mine` boolean, `maxResults`, and unsupported-field validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T039 [US3] Implement `_auth_context_for_selector()` for public selectors and owner-scoped `mine` OAuth behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T040 [US3] Implement `_map_upstream_error()` and handler exception mapping for validation, auth, authorization, missing resource, quota, unavailable service, and unexpected upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T041 [US3] Update `build_channels_list_handler()` to use `validate_channels_list_arguments()`, `_auth_context_for_selector()`, and safe upstream error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T042 [US3] Add or update reStructuredText docstrings for all validation, auth-context, error-mapping, and handler functions changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T043 [US3] Run focused US3 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

### Refactor for User Story 3

- [X] T044 [US3] Refactor validation and error details to reuse shared safe categories while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, safety review, and regression coverage across the whole feature.

- [X] T045 [P] Run quickstart-focused validation commands documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/quickstart.md` and record any implementation evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/quickstart.md`
- [X] T046 [P] Run broader YouTube regression tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T047 [P] Run dispatcher and MCP routing guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`
- [X] T048 [P] Run Layer 1 guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T049 Review public metadata, caller examples, mapped errors, and tests for credential, OAuth token, stack trace, private channel data, or secret leakage in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T050 Review reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T051 Run the full repository test suite with `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures in the touched files under `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T052 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any lint failures in the touched files under `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Setup; blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational; delivers MVP.
- **Phase 4 US2**: Depends on Foundational and can be implemented after or alongside US1 once the module seam exists; metadata tasks integrate best after US1 contract builder exists.
- **Phase 5 US3**: Depends on Foundational and can be implemented after or alongside US1 once the handler seam exists; validation tasks integrate best after US1 handler exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: MVP; no dependency on US2 or US3 after Foundational.
- **US2 (P2)**: Independently testable through metadata and examples; depends on the `channels_list` descriptor seam created for US1 if implemented sequentially.
- **US3 (P3)**: Independently testable through invalid request behavior; depends on the `channels_list` handler seam created for US1 if implemented sequentially.

### Parallel Opportunities

- T002 and T003 can run in parallel during Setup.
- T008, T009, and T010 can run in parallel for US1 Red tests.
- T022, T023, and T024 can run in parallel for US2 Red tests.
- T033, T034, T035, and T036 can run in parallel for US3 Red tests.
- T045, T046, T047, and T048 can run in parallel during Polish after implementation stabilizes.

## Parallel Execution Examples

### User Story 1

```bash
Task T008: "Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py"
Task T009: "Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py"
Task T010: "Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py"
```

### User Story 2

```bash
Task T022: "Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py"
Task T023: "Add failing representative catalog alignment tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task T024: "Add failing registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 3

```bash
Task T033: "Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py"
Task T035: "Add failing safe error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py"
Task T036: "Add failing routing tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Validate US1 independently with `python3 -m pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py`.
5. Stop for MVP review before adding US2 and US3 if desired.

### Incremental Delivery

1. Deliver US1 for callable near-raw channel retrieval.
2. Add US2 for complete metadata, usage notes, examples, and discovery readiness.
3. Add US3 for strict invalid request handling and safe error behavior.
4. Run Phase 6 full regression, full repository tests, and Ruff before feature completion.

### Final Validation

The feature is not complete until T051 and T052 pass after the final code change.
