# Tasks: YT-213 Layer 2 Tool `channelSections_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/`  
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/contracts/channel-sections-insert-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/quickstart.md`

**Tests**: Tests are mandatory. Each user story begins with Red test tasks, then Green implementation, then Refactor/verification. Completion requires `python3 -m pytest` and `python3 -m ruff check .` after final code changes. Every new or modified Python function must have a reStructuredText docstring before its story is complete.

**Organization**: Tasks are grouped by independently testable user story in priority order.

## Phase 1: Setup (Shared Orientation)

**Purpose**: Confirm the YT-213 scope, endpoint facts, and existing resource-family seams before creating Red tests.

- [X] T001 Review YT-213 scope, OAuth/write requirements, content-structure boundaries, and out-of-scope workflows in `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/plan.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/contracts/channel-sections-insert-tool-contract.md`
- [X] T002 [P] Review existing channel-section Layer 2 list patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T003 [P] Review comparable write and metadata patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T004 [P] Review registration, discovery, exports, and representative catalog seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T005 [P] Review Layer 1 `channelSections.insert` wrapper behavior and tests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared `channelSections_insert` placeholders and exports that all user stories depend on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T006 [P] Add failing concrete `channelSections_insert` resource-family placement and export expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T007 Add `channelSections_insert` constants placeholders, error type placeholder, builder placeholders, handler placeholders, validator placeholders, and `__all__` entries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T008 Export preliminary `channelSections_insert` symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T009 Add or update reStructuredText docstrings for foundational `channelSections_insert` placeholders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T010 Run foundational scaffolding tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Create Channel Sections Through a Public Tool (Priority: P1) MVP

**Goal**: `channelSections_insert` is discoverable, callable, and returns near-raw created channel-section results with endpoint identity, quota cost, requested parts, OAuth context, safe partner context when present, and returned resource fields preserved.

**Independent Test**: Invoke `channelSections_insert` with eligible OAuth authorization, supported part selection, and valid playlist-backed or channel-backed section bodies, then confirm the result preserves the created channel-section resource, requested parts, endpoint identity, quota cost, and safe operation context.

### Tests for User Story 1 (Red)

- [X] T011 [P] [US1] Add failing contract tests for `channelSections_insert` descriptor identity, OAuth-required auth mode, input schema, created-resource result shape, and near-raw boundary in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T012 [P] [US1] Add failing unit tests for `map_channel_sections_insert_result()`, requested part normalization, safe partner-context flags, returned resource preservation, and default created-resource handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T013 [P] [US1] Add failing integration tests proving default dispatcher registration exposes executable `channelSections_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`
- [X] T014 [US1] Run the US1 Red tests and confirm they fail for missing implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`

### Implementation for User Story 1 (Green)

- [X] T015 [US1] Implement `CHANNEL_SECTIONS_INSERT_TOOL_NAME`, `CHANNEL_SECTIONS_INSERT_QUOTA_COST`, supported part constants, input schema skeleton, description, usage-note placeholders, caveat placeholders, caller example placeholders, and `ChannelSectionsInsertToolError` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T016 [US1] Implement insert-safe default executor or transport helpers for local execution and tests with reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T017 [US1] Implement `build_channel_sections_insert_contract()` and `build_channel_sections_insert_tool_descriptor()` using `YouTubeToolContract`, `AvailabilityState`, and `ResponseBoundary` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T018 [US1] Implement insert part normalization, safe partner-context extraction, and `map_channel_sections_insert_result()` for returned `item`, requested parts, endpoint identity, quota cost, `created`, and partner context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T019 [US1] Implement `build_channel_sections_insert_handler()` that calls `build_channel_sections_insert_wrapper()` through the injected executor and OAuth context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T020 [US1] Export `channelSections_insert` constants, error type, contract builder, handler builder, descriptor builder, result mapper, and validator symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T021 [US1] Register `build_channel_sections_insert_tool_descriptor()` in the default registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US1] Add or update reStructuredText docstrings for every new or modified `channelSections_insert` function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T023 [US1] Run focused US1 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

### Refactor for User Story 1

- [X] T024 [US1] Refactor duplicate created-resource mapping, part-normalization, partner-context, or handler wiring logic while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

**Checkpoint**: User Story 1 is independently functional and can serve as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, OAuth, and Content Rules Before Calling (Priority: P2)

**Goal**: Tool discovery, descriptions, usage notes, caveats, and examples clearly show endpoint identity, quota cost `50`, OAuth requirement, supported part names, required `body`, required `body.snippet.type`, writable body fields, content-owner/channel delegation, maximum section limit, content-structure rules, and out-of-scope boundaries.

**Independent Test**: Inspect the `channelSections_insert` descriptor and representative examples, then confirm a caller can identify quota, OAuth mode, supported parts, body shape, partner context, section type/content rules, maximum-section caveat, and excluded higher-level workflows without invoking implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T025 [P] [US2] Add failing metadata contract tests for quota `50`, OAuth-required auth, supported parts, body requirement, `snippet.type`, writable fields, partner-context caveats, section-limit caveat, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T026 [P] [US2] Add failing representative catalog alignment tests for `channelSections_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T027 [P] [US2] Add failing default registry metadata tests for `channelSections_insert` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T028 [US2] Run the US2 Red tests and confirm they fail for incomplete metadata and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 2 (Green)

- [X] T029 [US2] Fill `CHANNEL_SECTIONS_INSERT_USAGE_NOTES`, `CHANNEL_SECTIONS_INSERT_CAVEATS`, and `CHANNEL_SECTIONS_INSERT_CALLER_EXAMPLES` for playlist-backed creation, channel-backed creation, delegated context, missing OAuth, missing part, missing section type, invalid content structure, duplicate references, capacity failure, and unsupported workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T030 [US2] Extend `build_channel_sections_insert_contract()` metadata with OAuth guidance, supported part names, body-shape guidance, writable-field guidance, content-rule caveats, partner-context caveats, section-limit caveat, created-resource response convention, and near-raw response boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T031 [US2] Add a representative `channelSections_insert` contract and alignment import in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T032 [US2] Export `CHANNEL_SECTIONS_INSERT_CALLER_EXAMPLES`, `CHANNEL_SECTIONS_INSERT_CAVEATS`, `CHANNEL_SECTIONS_INSERT_DESCRIPTION`, `CHANNEL_SECTIONS_INSERT_INPUT_SCHEMA`, `CHANNEL_SECTIONS_INSERT_QUOTA_COST`, and `CHANNEL_SECTIONS_INSERT_USAGE_NOTES` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T033 [US2] Add or update reStructuredText docstrings for all metadata and example helpers changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T034 [US2] Run focused US2 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor for User Story 2

- [X] T035 [US2] Refactor duplicated quota, OAuth, part, body, partner-context, content-rule, section-limit, and out-of-scope wording while keeping US2 metadata tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

**Checkpoint**: User Story 2 is independently verifiable through discovery and contract metadata.

---

## Phase 5: User Story 3 - Reject Unsupported Create Requests Clearly (Priority: P3)

**Goal**: Invalid `channelSections_insert` requests are rejected with stable, safe, caller-facing feedback for missing OAuth, missing `part`, unsupported parts, missing or malformed `body`, missing `body.snippet.type`, invalid content structure, duplicate references, invalid partner context, capacity failures, unsupported fields, and upstream failures.

**Independent Test**: Submit invalid requests to `channelSections_insert` and confirm each failure uses a safe shared Layer 2 category, identifies the correct field or content rule when safe, distinguishes auth failures from body/content failures, and excludes credentials, tokens, stack traces, CMS account details, owner identifiers, and private channel data.

### Tests for User Story 3 (Red)

- [X] T036 [P] [US3] Add failing unit tests for missing `part`, unsupported part names, missing `body`, non-object body, missing `body.snippet`, missing `body.snippet.type`, unsupported body fields, and unsupported optional fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T037 [US3] Add failing unit tests for playlist-backed and channel-backed content rules, missing required `contentDetails`, invalid playlist/channel mismatches, duplicate references, missing required titles, invalid positions, and too many references in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T038 [US3] Add failing unit tests for missing OAuth, invalid partner-context pairing, partner-scoped safe details, and selected OAuth auth context behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`
- [X] T039 [P] [US3] Add failing contract tests for safe error categories and no credential, token, stack trace, CMS account detail, owner identifier, secret, or private channel data leakage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T040 [P] [US3] Add failing method-routing tests for invalid `channelSections_insert` calls through the dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T041 [US3] Run the US3 Red tests and confirm they fail for incomplete validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 3 (Green)

- [X] T042 [US3] Implement `validate_channel_sections_insert_arguments()` with required `part`, supported part names, required `body`, object body shape, required `body.snippet.type`, unsupported body field rejection, unsupported optional field rejection, and unsupported higher-level workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T043 [US3] Implement section content-rule helpers for `singlePlaylist`, `multiplePlaylists`, `multipleChannels`, content mismatch rejection, missing content rejection, duplicate reference rejection, required title checks, position checks, and too-many-reference guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T044 [US3] Implement OAuth preflight and partner-context validation for `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T045 [US3] Implement insert upstream error mapping for validation, authentication, authorization, missing referenced playlist/channel, duplicate references, capacity limits, quota exhaustion, unavailable service, and unexpected upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T046 [US3] Update `build_channel_sections_insert_handler()` to use `validate_channel_sections_insert_arguments()`, OAuth/partner preflight, content-rule helpers, and safe upstream error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T047 [US3] Add or update reStructuredText docstrings for all validation, content-rule, auth-context, error-mapping, and handler functions changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`
- [X] T048 [US3] Run focused US3 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

### Refactor for User Story 3

- [X] T049 [US3] Refactor validation and error details to reuse shared safe categories while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, safety review, and regression coverage across the whole feature.

- [X] T050 [P] Run quickstart-focused validation commands documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/quickstart.md` and record any implementation evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/quickstart.md`
- [X] T051 [P] Run broader YouTube regression tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T052 [P] Run dispatcher and MCP routing guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`
- [X] T053 [P] Run Layer 1 guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T054 Review public metadata, caller examples, mapped errors, and tests for credential, OAuth token, stack trace, private channel data, CMS account detail, owner identifier, or secret leakage in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py`
- [X] T055 Review reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T056 Run the full repository test suite with `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures in the touched files under `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T057 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any lint failures in the touched files under `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; can start immediately.
- **Phase 2 Foundational**: Depends on Setup; blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational; delivers MVP.
- **Phase 4 US2**: Depends on Foundational and can be implemented after or alongside US1 once the descriptor seam exists; metadata tasks integrate best after US1 contract builder exists.
- **Phase 5 US3**: Depends on Foundational and can be implemented after or alongside US1 once the handler seam exists; validation tasks integrate best after US1 handler exists.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: MVP; no dependency on US2 or US3 after Foundational.
- **US2 (P2)**: Independently testable through metadata and examples; depends on the `channelSections_insert` descriptor seam created for US1 if implemented sequentially.
- **US3 (P3)**: Independently testable through invalid request behavior; depends on the `channelSections_insert` handler seam created for US1 if implemented sequentially.

### Parallel Opportunities

- T002, T003, T004, and T005 can run in parallel during Setup.
- T011, T012, and T013 can run in parallel for US1 Red tests.
- T025, T026, and T027 can run in parallel for US2 Red tests.
- T036, T039, and T040 can run in parallel for US3 Red tests because they touch different test files; T037 and T038 should run sequentially with T036 because they edit the same unit-test file.
- T050, T051, T052, and T053 can run in parallel during Polish after implementation stabilizes.

## Parallel Execution Examples

### User Story 1

```bash
Task T011: "Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task T012: "Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py"
Task T013: "Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py"
```

### User Story 2

```bash
Task T025: "Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task T026: "Add failing representative catalog alignment tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task T027: "Add failing registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 3

```bash
Task T036: "Add failing body validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py"
Task T039: "Add failing safe error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py"
Task T040: "Add failing routing tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Validate US1 independently with `python3 -m pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channel_sections_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channel_sections.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channel_sections_registration.py`.
5. Stop for MVP review before adding US2 and US3 if desired.

### Incremental Delivery

1. Deliver US1 for callable near-raw channel-section creation.
2. Add US2 for complete metadata, usage notes, examples, and discovery readiness.
3. Add US3 for strict invalid request handling and safe error behavior.
4. Run Phase 6 full regression, full repository tests, and Ruff before feature completion.

### Final Validation

The feature is not complete until T056 and T057 pass after the final code change.
