# Tasks: FND-011 Tool Metadata + Invocation Result Alignment

**Input**: Design documents from `/specs/011-tool-metadata-result-alignment/`
**Prerequisites**: [plan.md](~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/plan.md), [spec.md](~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/spec.md), [research.md](~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/research.md), [data-model.md](~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/data-model.md), [contracts/tool-metadata-contract.md](~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/contracts/tool-metadata-contract.md), [quickstart.md](~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Lock in the execution baseline and feature-specific contract examples before code changes begin.

- [X] T001 Align FND-011 Red-Green-Refactor validation commands in ~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/quickstart.md
- [X] T002 Align discovery and tool-result examples with final task scope in ~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/contracts/tool-metadata-contract.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared registry and protocol helpers that block all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 [P] Add shared registry descriptor coverage for complete tool definitions in ~/Projects/youtube-mcp-server/tests/unit/test_tool_registry.py
- [X] T004 [P] Add shared protocol success-content coverage for aligned MCP content items in ~/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py
- [X] T005 Implement reusable tool descriptor projection helpers in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T006 Implement reusable successful tool-result content shaping helpers in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T007 Preserve hosted JSON serialization for richer discovery and result payloads in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py

**Checkpoint**: Foundation ready. User story implementation can now proceed.

---

## Phase 3: User Story 1 - Discover Complete Tool Definitions (Priority: P1) 🎯 MVP

**Goal**: Deliver complete MCP-facing discovery metadata so clients can prepare valid calls from `tools/list` alone.

**Independent Test**: Request `tools/list` through local and hosted MCP flows and confirm every returned tool includes `name`, `description`, and `inputSchema`, with deterministic ordering across repeated requests.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add unit coverage for complete and deterministic tool descriptors in ~/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py
- [X] T009 [P] [US1] Add contract coverage for `tools/list` input schema exposure in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py
- [X] T010 [P] [US1] Add end-to-end discovery completeness coverage in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T011 [P] [US1] Add hosted `tools/list` metadata verification in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py

### Implementation for User Story 1

- [X] T012 [US1] Expose `inputSchema` from registry-backed `list_tools()` responses in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T013 [US1] Return complete registry descriptors from the `tools/list` protocol path in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T014 [US1] Refactor shared descriptor-building paths and rerun affected discovery tests in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

**Checkpoint**: User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Receive MCP-Compatible Tool Results (Priority: P2)

**Goal**: Deliver aligned MCP content for successful baseline tool invocations without falling back to the simplified JSON-string-only wrapper.

**Independent Test**: Invoke `server_ping`, `server_info`, and `server_list_tools` through local and hosted MCP flows and confirm each success result returns stable MCP content that preserves structured output.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T015 [P] [US2] Add baseline tool payload expectations for aligned success-content inputs in ~/Projects/youtube-mcp-server/tests/unit/test_baseline_server_tools.py
- [X] T016 [P] [US2] Add contract coverage for aligned successful `tools/call` content in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py
- [X] T017 [P] [US2] Add end-to-end aligned tool-result coverage for baseline tools in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T018 [P] [US2] Add hosted baseline tool result-shape verification in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py

### Implementation for User Story 2

- [X] T019 [US2] Return richer registry descriptors from `server_list_tools` payloads in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T020 [US2] Replace the text-only success serializer with aligned MCP content shaping in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T021 [US2] Refactor baseline tool success-result helpers and rerun affected invocation tests in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py

**Checkpoint**: User Stories 1 and 2 both work independently with complete discovery and aligned successful tool results.

---

## Phase 5: User Story 3 - Extend the Catalog Without Breaking the Contract (Priority: P3)

**Goal**: Keep the registry extensible so newly registered tools inherit the same discovery and result contract as the baseline tools.

**Independent Test**: Register a new tool in the existing dispatcher, verify it appears in `tools/list` with complete metadata, and verify a successful invocation returns the same aligned MCP content structure as baseline tools.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T022 [P] [US3] Add unit coverage for new-tool registration and complete metadata reuse in ~/Projects/youtube-mcp-server/tests/unit/test_tool_registry.py
- [X] T023 [P] [US3] Add duplicate and invalid-registration regression coverage for non-discoverable broken tools in ~/Projects/youtube-mcp-server/tests/unit/test_tool_registry_duplicates.py
- [X] T024 [P] [US3] Add register-list-call integration coverage for custom tools using the aligned contract in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py

### Implementation for User Story 3

- [X] T025 [US3] Tighten invalid registration rejection so incomplete tools never surface in discovery in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T026 [US3] Generalize aligned success-content shaping for dynamically registered tools in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T027 [US3] Refactor registry and protocol extension points and rerun affected extensibility tests in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py

**Checkpoint**: All user stories are independently functional and new tools can adopt the same contract without transport changes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final regression protection, documentation, and release evidence.

- [X] T028 [P] Add cross-cutting discovery and tool-result regression coverage in ~/Projects/youtube-mcp-server/tests/contract/test_cloud_run_foundation_contract.py
- [X] T029 [P] Add hosted streamable HTTP regression coverage for richer discovery and result payloads in ~/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py
- [X] T030 Update external feature documentation for complete tool metadata and aligned result content in ~/Projects/youtube-mcp-server/README.md
- [X] T031 Run and record final quickstart validation evidence for FND-011 in ~/Projects/youtube-mcp-server/specs/011-tool-metadata-result-alignment/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion. Blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion. Delivers the MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 completion for the recommended delivery path because invocation results build on the finalized discovery contract, though Red tests can be prepared earlier.
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 completion because extensibility must inherit the final metadata and result contract.
- **Polish (Phase 6)**: Depends on all user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2. No dependency on later stories.
- **User Story 2 (P2)**: Starts after Phase 2, but should be merged after US1 because both stories touch `~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`.
- **User Story 3 (P3)**: Starts after Phase 2, but should be merged after US1 and US2 because it extends both registry and result-shaping behavior.

### Within Each User Story

- Red tests must be written and failing before implementation starts.
- Green implementation is limited to the smallest code change needed to pass the story tests.
- Refactor tasks happen only after the story is green and must preserve passing tests.
- Each story must remain independently testable at its checkpoint.

## Parallel Opportunities

- Foundational Red tasks `T003` and `T004` can run in parallel because they touch different test files.
- US1 Red tasks `T008` through `T011` can run in parallel because they touch separate unit, contract, and integration files.
- US2 Red tasks `T015` through `T018` can run in parallel because they touch separate unit, contract, and integration files.
- US3 Red tasks `T022` through `T024` can run in parallel because they touch separate registry and integration files.
- Polish regression tasks `T028` and `T029` can run in parallel before the final documentation and evidence updates.

## Parallel Example: User Story 1

```bash
# Launch US1 Red tests in parallel:
Task: "T008 Add unit coverage for complete and deterministic tool descriptors in ~/Projects/youtube-mcp-server/tests/unit/test_list_tools_method.py"
Task: "T009 Add contract coverage for tools/list input schema exposure in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py"
Task: "T010 Add end-to-end discovery completeness coverage in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
Task: "T011 Add hosted tools/list metadata verification in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 Red tests in parallel:
Task: "T015 Add baseline tool payload expectations for aligned success-content inputs in ~/Projects/youtube-mcp-server/tests/unit/test_baseline_server_tools.py"
Task: "T016 Add contract coverage for aligned successful tools/call content in ~/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py"
Task: "T017 Add end-to-end aligned tool-result coverage for baseline tools in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
Task: "T018 Add hosted baseline tool result-shape verification in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 Red tests in parallel:
Task: "T022 Add unit coverage for new-tool registration and complete metadata reuse in ~/Projects/youtube-mcp-server/tests/unit/test_tool_registry.py"
Task: "T023 Add duplicate and invalid-registration regression coverage for non-discoverable broken tools in ~/Projects/youtube-mcp-server/tests/unit/test_tool_registry_duplicates.py"
Task: "T024 Add register-list-call integration coverage for custom tools using the aligned contract in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational shared helpers.
3. Complete Phase 3: User Story 1.
4. Stop and validate `tools/list` locally and through hosted flow before moving on.

### Incremental Delivery

1. Deliver the shared descriptor and result-shaping foundation.
2. Deliver US1 and validate complete discovery metadata.
3. Deliver US2 and validate aligned successful tool results.
4. Deliver US3 and validate extensibility for newly registered tools.
5. Finish with polish, regression, and release evidence.

### Parallel Team Strategy

1. One developer prepares foundational registry tests while another prepares foundational protocol-result tests.
2. After Phase 2, one developer can own US1 implementation while others prepare US2 and US3 Red tests.
3. Merge US1 before US2 and US3 implementation because both later stories share `~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` and `~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

## Notes

- Every task follows the required checklist format `- [ ] T### [P] [US#] Description with file path`.
- Story labels are present only on user story tasks.
- The suggested MVP scope is User Story 1 after Setup and Foundational phases.
- Refactor tasks require rerunning affected suites before completion.
