# Tasks: FND-010 MCP Protocol Contract Alignment

**Input**: Design documents from `/specs/010-mcp-protocol-alignment/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/data-model.md), [contracts/mcp-protocol-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/contracts/mcp-protocol-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align feature docs and execution scaffolding before code changes begin.

- [X] T001 Update execution notes and target test commands in /Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/quickstart.md
- [X] T002 Create the story-to-contract traceability task baseline in /Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/tasks.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared protocol primitives and transport hooks that block all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 [P] Add protocol-native response builder coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_envelope_contract.py
- [X] T004 [P] Add shared protocol routing regression coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py
- [X] T005 Replace legacy envelope helpers with protocol-native builders in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py
- [X] T006 Update shared protocol routing entrypoints for MCP-native request and response shape in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T007 Preserve hosted `/mcp` transport framing while accepting protocol-native bodies in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py
- [X] T008 Preserve hosted JSON and SSE protocol body handling in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py

**Checkpoint**: Foundation ready. User story implementation can now proceed.

---

## Phase 3: User Story 1 - Use Native MCP Flows (Priority: P1) 🎯 MVP

**Goal**: Deliver MCP-native initialize, tool discovery, and tool invocation flows without the legacy wrapper.

**Independent Test**: Run initialize, `tools/list`, and `tools/call` against local and hosted code paths and confirm every success payload uses the MCP-native `result` contract with no `success/data/meta/error` wrapper.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Replace initialize contract assertions with MCP-native success expectations in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_initialize_method.py
- [X] T010 [P] [US1] Replace tool discovery and tool call contract assertions with MCP-native result expectations in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py
- [X] T011 [P] [US1] Add end-to-end MCP-native initialize to list to call journey coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T012 [P] [US1] Add hosted streamable transport assertions for MCP-native success payloads in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py

### Implementation for User Story 1

- [X] T013 [US1] Implement MCP-native initialize result shaping in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T014 [US1] Implement MCP-native tool discovery result shaping in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T015 [US1] Implement MCP-native tool invocation result shaping in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T016 [US1] Update hosted response serialization for MCP-native initialize and tool success bodies in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T017 [US1] Refactor protocol success helpers and rerun affected story tests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Receive Predictable Protocol Errors (Priority: P2)

**Goal**: Deliver stable MCP-native failures for malformed requests, unsupported methods, invalid arguments, and tool execution errors.

**Independent Test**: Send malformed requests, unsupported methods, invalid tool arguments, and failing tool calls through local and hosted paths and confirm each returns the documented MCP-native `error` shape with sanitized details.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Replace wrapper-based error assertions with MCP-native error assertions in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_envelope_contract.py
- [X] T019 [P] [US2] Add MCP-native invalid-argument and unknown-tool error coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py
- [X] T020 [P] [US2] Add unsupported-method and malformed-request contract coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py
- [X] T021 [P] [US2] Add hosted MCP-native error-path verification in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py

### Implementation for User Story 2

- [X] T022 [US2] Implement MCP-native protocol error builders with sanitized data handling in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py
- [X] T023 [US2] Implement stable malformed-request, unsupported-method, and invalid-argument mapping in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T024 [US2] Preserve hosted HTTP status mapping while returning MCP-native protocol error bodies in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T025 [US2] Refactor shared error mapping paths and rerun affected story tests in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py

**Checkpoint**: User Stories 1 and 2 both work independently with stable success and failure contracts.

---

## Phase 5: User Story 3 - Validate One Contract Across Environments (Priority: P3)

**Goal**: Prove local and hosted environments expose the same MCP lifecycle and failure contract, and document how integrators validate it.

**Independent Test**: Run the same protocol-native initialize, `tools/list`, `tools/call`, malformed request, and unsupported-method scenarios against local and hosted environments and confirm the results match the documented contract.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add local-versus-hosted MCP-native parity coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py
- [X] T027 [P] [US3] Add contract regression coverage for hosted transport carrying MCP-native bodies in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py
- [X] T028 [P] [US3] Add release-evidence contract checks for MCP-native verification output in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py

### Implementation for User Story 3

- [X] T029 [US3] Update hosted verification flow to assert MCP-native contract parity in /Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py
- [X] T030 [US3] Update manual verification and migration guidance for MCP-native contract validation in /Users/ctgunn/Projects/youtube-mcp-server/README.md
- [X] T031 [US3] Align feature quickstart with final local and hosted parity workflow in /Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/quickstart.md
- [X] T032 [US3] Refactor duplicated parity assertions and rerun affected story tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py

**Checkpoint**: All user stories are independently functional and supported by matching local and hosted validation evidence.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, regression protection, and release-ready documentation.

- [X] T033 [P] Add final protocol lifecycle regression coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py
- [X] T034 [P] Add cross-cutting observability regression checks for MCP-native request handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py
- [X] T035 Remove obsolete wrapper-specific implementation paths after all stories are green in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T036 Run and record final full-suite validation evidence in /Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. Blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion. Delivers the MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because error handling must align with the new success-path protocol shape.
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 because parity validation requires the final success and failure contract.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2. No dependency on later stories.
- **User Story 2 (P2)**: Starts after US1 establishes the MCP-native response contract.
- **User Story 3 (P3)**: Starts after US1 and US2 establish the final protocol contract and hosted behavior.

### Within Each User Story

- Red tests must be written and failing before implementation starts.
- Green implementation is limited to the smallest code change needed to pass the story tests.
- Refactor tasks happen only after the story is green and must preserve passing tests.
- Each story must remain independently testable at its checkpoint.

## Parallel Opportunities

- Foundational test additions in `tests/unit/test_envelope_contract.py` and `tests/unit/test_method_routing.py` can run in parallel.
- US1 Red tasks `T009` through `T012` can run in parallel because they touch separate test files.
- US2 Red tasks `T018` through `T021` can run in parallel because they touch separate test files.
- US3 Red tasks `T026` through `T028` can run in parallel because they touch separate verification files.
- Polish test tasks `T033` and `T034` can run in parallel before the final full-suite run.

## Parallel Example: User Story 1

```bash
# Launch US1 Red tests in parallel:
Task: "T009 Replace initialize contract assertions with MCP-native success expectations in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_initialize_method.py"
Task: "T010 Replace tool discovery and tool call contract assertions with MCP-native result expectations in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py"
Task: "T011 Add end-to-end MCP-native initialize to list to call journey coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
Task: "T012 Add hosted streamable transport assertions for MCP-native success payloads in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 Red tests in parallel:
Task: "T018 Replace wrapper-based error assertions with MCP-native error assertions in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_envelope_contract.py"
Task: "T019 Add MCP-native invalid-argument and unknown-tool error coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py"
Task: "T020 Add unsupported-method and malformed-request contract coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py"
Task: "T021 Add hosted MCP-native error-path verification in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 parity and documentation checks in parallel:
Task: "T026 Add local-versus-hosted MCP-native parity coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
Task: "T027 Add contract regression coverage for hosted transport carrying MCP-native bodies in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
Task: "T028 Add release-evidence contract checks for MCP-native verification output in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational protocol primitives.
3. Complete Phase 3: User Story 1.
4. Stop and validate MCP-native initialize, list, and call behavior before moving on.

### Incremental Delivery

1. Deliver foundational protocol helpers and transport compatibility.
2. Deliver US1 and validate the MVP contract.
3. Deliver US2 and validate predictable error behavior.
4. Deliver US3 and validate local-versus-hosted parity plus release evidence.
5. Finish with polish and full regression coverage.

### Parallel Team Strategy

1. One developer handles foundational protocol helpers while another prepares foundational tests.
2. After Phase 2, one developer can own US1 implementation while others prepare US2 and US3 Red tests.
3. Once US1 is green, US2 and US3 can progress with minimal file overlap outside shared protocol routing.

## Notes

- Every task follows the required checklist format `- [ ] T### [P] [US#] Description with file path`.
- Story labels are present only on user story tasks.
- The MVP scope is User Story 1 after Setup and Foundational phases.
- Refactor tasks require rerunning affected suites before completion.
