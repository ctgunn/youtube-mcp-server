# Tasks: YT-211 Layer 2 Tool `channels_update`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/`  
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/contracts/channels-update-tool-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/quickstart.md`

**Tests**: Tests are mandatory. Each user story begins with Red test tasks, then Green implementation, then Refactor/verification. Completion requires `python3 -m pytest` and `python3 -m ruff check .` after final code changes. Every new or modified Python function must have a reStructuredText docstring before its story is complete.

**Organization**: Tasks are grouped by independently testable user story in priority order.

## Phase 1: Setup (Shared Orientation)

**Purpose**: Confirm the feature scope and existing seams before creating Red tests.

- [X] T001 Review YT-211 scope, writable-part rules, OAuth requirement, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/plan.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/contracts/channels-update-tool-contract.md`
- [X] T002 [P] Review existing concrete channels Layer 2 patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`
- [X] T003 [P] Review existing registration, discovery, and catalog seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T004 [P] Review Layer 1 `channels.update` wrapper and validators in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/channels.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared `channels_update` scaffolding and exports that all user stories depend on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T005 [P] Add failing concrete `channels_update` resource-family placement and export expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T006 Add preliminary `channels_update` constants, schema placeholder, error type placeholder, and `__all__` entries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T007 Export preliminary `channels_update` symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T008 Add or update reStructuredText docstrings for foundational `channels_update` placeholders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T009 Run foundational scaffolding tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Update Supported Channel Settings Through a Public Tool (Priority: P1) MVP

**Goal**: `channels_update` is discoverable, callable, and returns near-raw updated channel resource results with endpoint identity, quota cost, selected writable part, requested parts, and safe operation context.

**Independent Test**: Invoke `channels_update` with eligible authorization, a supported writable part, and an aligned channel resource body, then confirm the result preserves the updated channel resource, selected writable part, quota context, and mapped endpoint identity.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add failing contract tests for `channels_update` descriptor identity, input schema, updated-resource result shape, and banner URL activation result context in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T011 [P] [US1] Add failing unit tests for `map_channels_update_result()`, requested part normalization, selected writable part context, and default updated-resource handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`
- [X] T012 [P] [US1] Add failing integration tests proving default dispatcher registration exposes executable `channels_update` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py`
- [X] T013 [US1] Run the US1 Red tests and confirm they fail for missing implementation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py`

### Implementation for User Story 1 (Green)

- [X] T014 [US1] Implement `CHANNELS_UPDATE_TOOL_NAME`, `CHANNELS_UPDATE_QUOTA_COST`, supported writable parts, input schema, description, usage-note placeholders, and caveat placeholders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T015 [US1] Implement `build_channels_update_contract()` with `YouTubeToolContract`, mutation response convention, near-raw response boundary, OAuth-required auth mode, and quota cost in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T016 [US1] Implement `_channels_update_requested_parts()` and `map_channels_update_result()` for returned resource fields, selected writable part, requested parts, endpoint identity, and quota cost in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T017 [US1] Implement `build_channels_update_handler()` that calls the existing `build_channels_update_wrapper()` through the injected executor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T018 [US1] Implement `build_channels_update_tool_descriptor()` for dispatcher-compatible discovery and invocation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T019 [US1] Export `channels_update` constants, error type, contract builder, handler builder, descriptor builder, result mapper, and validator symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T020 [US1] Register `build_channels_update_tool_descriptor()` in the default registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T021 [US1] Add or update reStructuredText docstrings for every new or modified `channels_update` function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T022 [US1] Run focused US1 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

### Refactor for User Story 1

- [X] T023 [US1] Refactor duplicate mutation-result mapping or requested-part helper logic while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

**Checkpoint**: User Story 1 is independently functional and can serve as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Access, and Writable Boundaries Before Calling (Priority: P2)

**Goal**: Tool discovery, descriptions, usage notes, caveats, and examples clearly show endpoint identity, quota cost `50`, OAuth-required auth, supported writable parts, part-to-body alignment, overwrite warning, content-owner delegation caveat, banner boundary, and out-of-scope workflows.

**Independent Test**: Inspect the `channels_update` descriptor and representative examples, then confirm a caller can identify quota, auth mode, supported writable parts, body alignment, read-only exclusions, overwrite behavior, banner activation boundary, and excluded higher-level channel workflows without invoking implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T024 [P] [US2] Add failing metadata contract tests for quota, OAuth-required auth, supported writable parts, part-to-body guidance, overwrite warning, content-owner delegation caveat, and banner boundary in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T025 [P] [US2] Add failing representative catalog alignment tests for `channels_update` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T026 [P] [US2] Add failing default registry metadata tests for `channels_update` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T027 [US2] Run the US2 Red tests and confirm they fail for incomplete metadata and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 2 (Green)

- [X] T028 [US2] Fill `CHANNELS_UPDATE_USAGE_NOTES`, `CHANNELS_UPDATE_CAVEATS`, and `CHANNELS_UPDATE_CALLER_EXAMPLES` for `brandingSettings`, `localizations`, banner URL activation, missing OAuth, missing body, part-to-body mismatch, read-only field rejection, and unsupported writable part rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T029 [US2] Extend `build_channels_update_contract()` metadata with writable-part guidance, overwrite warning, content-owner delegation caveat, banner boundary, response convention, response boundary, and availability state in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T030 [US2] Add a representative `channels_update` contract and alignment import in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T031 [US2] Export `CHANNELS_UPDATE_CALLER_EXAMPLES` and any new metadata symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T032 [US2] Add or update reStructuredText docstrings for all metadata and example helpers changed for US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T033 [US2] Run focused US2 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor for User Story 2

- [X] T034 [US2] Refactor duplicated quota, auth, writable-part, and caveat wording while keeping US2 metadata tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

**Checkpoint**: User Story 2 is independently verifiable through discovery and contract metadata.

---

## Phase 5: User Story 3 - Reject Unsupported or Ineligible Channel Updates Clearly (Priority: P3)

**Goal**: Invalid `channels_update` requests are rejected with stable, safe, caller-facing feedback for missing `part`, empty `part`, multiple parts, missing `body`, missing `body.id`, unsupported parts, part-to-body mismatch, read-only fields, unsupported delegation fields, missing OAuth, ineligible access, and upstream failures.

**Independent Test**: Submit invalid requests to `channels_update` and confirm each failure uses a safe shared Layer 2 category, identifies the correct field when safe, distinguishes auth and authorization failures from malformed update bodies, and excludes credentials, tokens, stack traces, private channel data, and sensitive request bodies.

### Tests for User Story 3 (Red)

- [X] T035 [P] [US3] Add failing unit tests for missing `part`, empty `part`, multiple parts, missing `body`, empty `body`, missing `body.id`, unsupported parts, part-to-body mismatch, read-only fields, and unsupported top-level fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`
- [X] T036 [P] [US3] Add failing unit tests for missing OAuth, OAuth auth-context selection, unsupported delegation fields, and ineligible channel-management access translation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`
- [X] T037 [P] [US3] Add failing contract tests for safe error categories and no credential, token, stack trace, private channel data, or sensitive body leakage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T038 [P] [US3] Add failing method-routing tests for invalid `channels_update` calls through the dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T039 [US3] Run the US3 Red tests and confirm they fail for incomplete validation and error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Implementation for User Story 3 (Green)

- [X] T040 [US3] Implement `validate_channels_update_arguments()` with required `part`, one supported writable part, required `body`, required `body.id`, part-to-body alignment, read-only field rejection, unsupported top-level field rejection, and unsupported delegation field rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T041 [US3] Implement `_auth_context_for_update()` for OAuth-required `channels_update` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T042 [US3] Implement `_map_channels_update_upstream_error()` and handler exception mapping for validation, authentication, authorization, missing channel, quota, unavailable service, and unexpected upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T043 [US3] Update `build_channels_update_handler()` to use `validate_channels_update_arguments()`, `_auth_context_for_update()`, and safe upstream error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T044 [US3] Add or update reStructuredText docstrings for all validation, auth-context, error-mapping, and handler functions changed for US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`
- [X] T045 [US3] Run focused US3 Green tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

### Refactor for User Story 3

- [X] T046 [US3] Refactor validation and error details to reuse shared safe categories while keeping US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, safety review, and regression coverage across the whole feature.

- [X] T047 [P] Run quickstart-focused validation commands documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/quickstart.md` and record any implementation evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/quickstart.md`
- [X] T048 [P] Run broader YouTube regression tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T049 [P] Run dispatcher and MCP routing guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`
- [X] T050 [P] Run Layer 1 guard tests for `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T051 Review public metadata, caller examples, mapped errors, and tests for credential, OAuth token, stack trace, private channel data, sensitive body, or secret leakage in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py`
- [X] T052 Review reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
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
- **US2 (P2)**: Independently testable through metadata and examples; depends on the `channels_update` descriptor seam created for US1 if implemented sequentially.
- **US3 (P3)**: Independently testable through invalid request behavior; depends on the `channels_update` handler seam created for US1 if implemented sequentially.

### Parallel Opportunities

- T002, T003, and T004 can run in parallel during Setup.
- T010, T011, and T012 can run in parallel for US1 Red tests.
- T024, T025, and T026 can run in parallel for US2 Red tests.
- T035, T036, T037, and T038 can run in parallel for US3 Red tests.
- T047, T048, T049, and T050 can run in parallel during Polish after implementation stabilizes.

## Parallel Execution Examples

### User Story 1

```bash
Task T010: "Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py"
Task T011: "Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py"
Task T012: "Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py"
```

### User Story 2

```bash
Task T024: "Add failing metadata contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py"
Task T025: "Add failing representative catalog alignment tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task T026: "Add failing registry metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 3

```bash
Task T035: "Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py"
Task T037: "Add failing safe error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py"
Task T038: "Add failing routing tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 Setup.
2. Complete Phase 2 Foundational.
3. Complete Phase 3 US1.
4. Validate US1 independently with `python3 -m pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_channels_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_channels.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_channels_registration.py`.
5. Stop for MVP review before adding US2 and US3 if desired.

### Incremental Delivery

1. Deliver US1 for callable near-raw channel updates.
2. Add US2 for complete metadata, usage notes, examples, and discovery readiness.
3. Add US3 for strict invalid request handling and safe error behavior.
4. Run Phase 6 full regression, full repository tests, and Ruff before feature completion.

### Final Validation

The feature is not complete until T053 and T054 pass after the final code change.
