# Tasks: YT-212 Layer 2 Tool `channelSections_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/`  
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/contracts/channel-sections-list-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/quickstart.md`

**Tests**: Tests are mandatory. Each user story begins with Red test tasks, then Green implementation, then Refactor/verification. Completion requires `python3 -m pytest` and `python3 -m ruff check .` after final code changes. Every new or modified Python function must have a reStructuredText docstring before its story is complete.

**Organization**: Tasks are grouped by independently testable user story in priority order.

## Phase 1: Setup (Shared Orientation)

**Purpose**: Confirm the feature scope and existing seams before creating Red tests.

- [X] T001 Review YT-212 scope, selector rules, caveat boundaries, and out-of-scope workflows in `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/plan.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/contracts/channel-sections-list-tool-contract.md`
- [X] T002 [P] Review existing concrete Layer 2 tool patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T003 [P] Review registration, discovery, exports, and representative catalog seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T004 [P] Review Layer 1 `channelSections.list` wrapper behavior and tests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared `channelSections_list` scaffolding and exports that all user stories depend on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T005 [P] Add failing concrete channel-sections resource-family placement and export expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T006 Create the concrete channel-sections Layer 2 module skeleton with module docstring, constants placeholders, error type placeholder, and `__all__` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T007 Export preliminary `channelSections_list` symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T008 Add or update reStructuredText docstrings for foundational `channelSections_list` placeholders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T009 Run foundational scaffolding tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Retrieve Channel Sections Through a Public Tool (Priority: P1) MVP

**Goal**: `channelSections_list` is discoverable, callable, and returns near-raw channel-section collection results with endpoint identity, quota cost, requested parts, selected lookup mode, optional continuation fields when present, and successful empty collections.

**Independent Test**: Invoke `channelSections_list` with supported `id`, `channelId`, and authorized `mine` lookup requests, then confirm the result preserves channel-section items or an empty collection, requested parts, selected selector, optional continuation details, and `channelSections.list` metadata.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add failing contract tests for `channelSections_list` descriptor identity, input schema, result shape, empty collection behavior, optional continuation preservation, and near-raw boundary in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T011 [P] [US1] Add failing unit tests for `map_channel_sections_list_result()`, selected selector context, requested part normalization, caveat context, optional continuation fields, and default empty-result handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T012 [P] [US1] Add failing integration tests proving default dispatcher registration exposes executable `channelSections_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`
- [X] T013 [US1] Run the US1 Red tests and confirm they fail for missing implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`

### Implementation for User Story 1 (Green)

- [X] T014 [US1] Implement `CHANNEL_SECTIONS_LIST_TOOL_NAME`, `CHANNEL_SECTIONS_LIST_QUOTA_COST`, selector constants, input schema, description, usage-note placeholders, caveat placeholders, and `ChannelSectionsListToolError` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T015 [US1] Implement `_default_channel_sections_transport()` and `_default_executor()` with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T016 [US1] Implement `build_channel_sections_list_contract()` and `build_channel_sections_list_tool_descriptor()` using `YouTubeToolContract`, `AvailabilityState`, and `ResponseBoundary` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T017 [US1] Implement `_active_selectors()`, `_requested_parts()`, `_safe_caveat_context()`, and `map_channel_sections_list_result()` for returned items, selected selector, requested parts, caveats, and optional `nextPageToken`, `prevPageToken`, and `pageInfo` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T018 [US1] Implement `build_channel_sections_list_handler()` that calls `build_channel_sections_list_wrapper()` through the injected executor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T019 [US1] Export `channelSections_list` constants, error type, contract builder, handler builder, descriptor builder, result mapper, and validator symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T020 [US1] Register `build_channel_sections_list_tool_descriptor()` in the default registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T021 [US1] Add or update reStructuredText docstrings for every new or modified `channelSections_list` function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T022 [US1] Run focused US1 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

### Refactor for User Story 1

- [X] T023 [US1] Refactor duplicate list-result mapping, caveat-context, or selector helper logic while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

**Checkpoint**: User Story 1 is independently functional and can serve as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Access, Filters, and Caveats Before Calling (Priority: P2)

**Goal**: Tool discovery, descriptions, usage notes, caveats, and examples clearly show endpoint identity, quota cost `1`, mixed auth, selectors `channelId`, `id`, and `mine`, OAuth requirement for `mine`, deprecated `hl`, content-owner partner caveat, optional continuation handling, empty-result behavior, and out-of-scope boundaries.

**Independent Test**: Inspect the `channelSections_list` descriptor and representative examples, then confirm a caller can identify quota, auth mode, supported selectors, `mine` authorization, `hl` deprecation, content-owner partner requirements, optional continuation caveat, empty-result behavior, and excluded higher-level channel-section workflows without invoking implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T024 [P] [US2] Add failing metadata contract tests for quota, mixed auth, supported selectors, `mine` OAuth guidance, deprecated `hl`, content-owner partner caveat, optional continuation notes, empty-result notes, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T025 [P] [US2] Add failing representative catalog alignment tests for `channelSections_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T026 [P] [US2] Add failing default registry metadata tests for `channelSections_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T027 [US2] Run the US2 Red tests and confirm they fail for incomplete metadata and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 2 (Green)

- [X] T028 [US2] Fill `CHANNEL_SECTIONS_LIST_USAGE_NOTES`, `CHANNEL_SECTIONS_LIST_CAVEATS`, and `CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES` for `channelId`, `id`, `mine`, empty result, deprecated `hl`, content-owner partner caveat, conflicting selectors, auth failure, and unsupported higher-level workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T029 [US2] Extend `build_channel_sections_list_contract()` metadata with selector guidance, response convention, response boundary, availability state, deprecated `hl` caveat, content-owner partner caveat, and optional continuation caveat in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T030 [US2] Add a representative `channelSections_list` contract and alignment import in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T031 [US2] Export `CHANNEL_SECTIONS_LIST_CALLER_EXAMPLES` and any new metadata symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T032 [US2] Add or update reStructuredText docstrings for all metadata and example helpers changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T033 [US2] Run focused US2 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor for User Story 2

- [X] T034 [US2] Refactor duplicated quota, auth, selector, caveat, and out-of-scope wording while keeping US2 metadata tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

**Checkpoint**: User Story 2 is independently verifiable through discovery and contract metadata.

---

## Phase 5: User Story 3 - Reject Unsupported Channel-Section Requests Clearly (Priority: P3)

**Goal**: Invalid `channelSections_list` requests are rejected with stable, safe, caller-facing feedback for missing `part`, missing selector, empty selector values, conflicting selectors, invalid `mine`, unsupported fields, unsupported pagination fields when not enabled, missing OAuth for `mine`, invalid IDs, inaccessible targets, and upstream failures.

**Independent Test**: Submit invalid requests to `channelSections_list` and confirm each failure uses a safe shared Layer 2 category, identifies the correct field or selector when safe, distinguishes auth failures from no-match lookups, and excludes credentials, tokens, stack traces, CMS account details, and private channel data.

### Tests for User Story 3 (Red)

- [X] T035 [P] [US3] Add failing unit tests for missing `part`, missing selector, empty `channelId`, empty `id`, conflicting selectors, invalid `mine`, unsupported selector aliases, unsupported fields, and unsupported pagination fields when not enabled in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T036 [P] [US3] Add failing unit tests for `mine` without OAuth, API-key attempts for owner-scoped lookup, safe auth details, content-owner partner caveat handling, and selected auth context behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T037 [P] [US3] Add failing contract tests for safe error categories and no credential, token, stack trace, CMS account detail, secret, or private channel data leakage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T038 [P] [US3] Add failing method-routing tests for invalid `channelSections_list` calls through the dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T039 [US3] Run the US3 Red tests and confirm they fail for incomplete validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 3 (Green)

- [X] T040 [US3] Implement `validate_channel_sections_list_arguments()` with required `part`, exact-one selector, non-empty selector, `mine` boolean, unsupported selector alias rejection, deprecated `hl` caveat validation, content-owner caveat handling, and unsupported-field validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T041 [US3] Implement `_auth_context_for_selector()` for public selectors and owner-scoped `mine` OAuth behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T042 [US3] Implement `_map_upstream_error()` and handler exception mapping for validation, authentication, authorization, invalid ID, missing channel, missing channel section, quota, unavailable service, and unexpected upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T043 [US3] Update `build_channel_sections_list_handler()` to use `validate_channel_sections_list_arguments()`, `_auth_context_for_selector()`, and safe upstream error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T044 [US3] Add or update reStructuredText docstrings for all validation, auth-context, error-mapping, and handler functions changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T045 [US3] Run focused US3 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

### Refactor for User Story 3

- [X] T046 [US3] Refactor validation and error details to reuse shared safe categories while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, safety review, and regression coverage across the whole feature.

- [X] T047 [P] Run quickstart-focused validation commands documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/quickstart.md` and record any implementation evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/quickstart.md`
- [X] T048 [P] Run broader YouTube regression tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T049 [P] Run dispatcher and MCP routing guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`
- [X] T050 [P] Run Layer 1 guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T051 Review public metadata, caller examples, mapped errors, and tests for credential, OAuth token, stack trace, private channel data, CMS account detail, or secret leakage in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T052 Review reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T053 Run the full repository test suite with `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures in the touched files under `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T054 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any lint failures in the touched files under `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

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
- **US2 (P2)**: Independently testable through metadata and examples; depends on the `channelSections_list` descriptor seam created for US1 if implemented sequentially.
- **US3 (P3)**: Independently testable through invalid request behavior; depends on the `channelSections_list` handler seam created for US1 if implemented sequentially.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel during Setup.
- T010, T011, and T012 can run in parallel for US1 Red tests.
- T024, T025, and T026 can run in parallel for US2 Red tests.
- T035, T036, T037, and T038 can run in parallel for US3 Red tests.
- T047, T048, T049, and T050 can run in parallel during Polish after implementation stabilizes.

## Parallel Execution Examples

### User Story 1

```bash
Task T010: "Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task T011: "Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py"
Task T012: "Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py"
```

### User Story 2

```bash
Task T024: "Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task T025: "Add failing representative catalog alignment tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task T026: "Add failing registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 3

```bash
Task T035: "Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py"
Task T037: "Add failing safe error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task T038: "Add failing routing tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Validate US1 independently with `python3 -m pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`.
5. Stop for MVP review before adding US2 and US3 if desired.

### Incremental Delivery

1. Deliver US1 for callable near-raw channel-section retrieval.
2. Add US2 for complete metadata, usage notes, examples, and discovery readiness.
3. Add US3 for strict invalid request handling and safe error behavior.
4. Run Phase 6 full regression, full repository tests, and Ruff before feature completion.

### Final Validation

The feature is not complete until T053 and T054 pass after the final code change.
