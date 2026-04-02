# Tasks: OpenAI Retrieval Compatibility

**Input**: Design documents from `/specs/023-openai-retrieval-compatibility/`
**Prerequisites**: [plan.md](~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/plan.md), [spec.md](~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/spec.md), [research.md](~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/research.md), [data-model.md](~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/data-model.md), [contracts/openai-retrieval-compatibility-contract.md](~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/contracts/openai-retrieval-compatibility-contract.md), [quickstart.md](~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing retrieval surfaces and planning artifacts that this slice will change.

- [X] T001 Review retrieval implementation seams in ~/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py, ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py, and ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T002 [P] Review retrieval test seams in ~/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py, ~/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py, and ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T003 [P] Review hosted verification and docs seams in ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py and ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared contract constants, verification targets, and regression baseline before story work begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create a shared OpenAI-compatible retrieval contract plan in ~/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py covering `search` query input, `fetch` id input, result field names, and legacy-shape policy
- [X] T005 [P] Add foundational regression expectations for retrieval contract changes in ~/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py for empty-search success and unavailable-fetch failure semantics
- [X] T006 [P] Add foundational hosted verification check placeholders for OpenAI retrieval flow in ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py
- [X] T007 Record the full targeted Red suite command for retrieval compatibility in ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/quickstart.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Use OpenAI-Compatible Retrieval Calls (Priority: P1) 🎯 MVP

**Goal**: Make `search` and `fetch` discoverable and callable using the OpenAI-compatible request and result contract.

**Independent Test**: Initialize against `/mcp`, run `tools/list`, call `search` with `query`, then call `fetch` with an `id` returned from search, and confirm the MCP result payloads match the OpenAI-compatible contract.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add unit tests for OpenAI-compatible retrieval schemas and validation in ~/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py
- [X] T009 [P] [US1] Add contract tests for OpenAI-compatible `tools/list`, `search`, and `fetch` payloads in ~/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py
- [X] T010 [P] [US1] Add integration tests for OpenAI-compatible `search` to `fetch` MCP flow in ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T011 [US1] Run the US1 Red test suite with `pytest tests/unit/test_retrieval_tools.py tests/contract/test_deep_research_tools_contract.py tests/integration/test_mcp_request_flow.py` from ~/Projects/youtube-mcp-server

### Implementation for User Story 1

- [X] T012 [P] [US1] Update OpenAI-compatible search and fetch schemas plus sample-source identifiers in ~/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py
- [X] T013 [P] [US1] Update retrieval tool discovery descriptors and descriptions in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T014 [US1] Implement OpenAI-compatible `search` result shaping and `fetch` request validation in ~/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py
- [X] T015 [US1] Update MCP tool result wrapping assumptions for the new retrieval payloads in ~/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T016 [US1] Verify the US1 Green suite passes with `pytest tests/unit/test_retrieval_tools.py tests/contract/test_deep_research_tools_contract.py tests/integration/test_mcp_request_flow.py` from ~/Projects/youtube-mcp-server
- [X] T017 [US1] Refactor shared retrieval contract constants and helper functions in ~/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py while keeping US1 tests green

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Follow OpenAI-Specific Examples Reliably (Priority: P2)

**Goal**: Make the documented and hosted verification examples reflect the OpenAI-specific retrieval flow exactly.

**Independent Test**: Follow the OpenAI-specific quickstart and hosted verification flow end to end without undocumented assumptions and observe the expected discovery, search, and fetch behavior.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add docs-example integration coverage for OpenAI retrieval examples in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py
- [X] T019 [P] [US2] Add hosted-route integration coverage for OpenAI retrieval checks in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py
- [X] T020 [US2] Run the US2 Red test suite with `pytest tests/integration/test_cloud_run_docs_examples.py tests/integration/test_hosted_http_routes.py` from ~/Projects/youtube-mcp-server

### Implementation for User Story 2

- [X] T021 [P] [US2] Update OpenAI-specific retrieval examples and execution steps in ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/quickstart.md
- [X] T022 [P] [US2] Update hosted verification check names and request payloads for OpenAI retrieval flow in ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py
- [X] T023 [US2] Align any documentation-backed retrieval assertions in ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py with the OpenAI verification evidence format
- [X] T024 [US2] Verify the US2 Green suite passes with `pytest tests/integration/test_cloud_run_docs_examples.py tests/integration/test_hosted_http_routes.py` from ~/Projects/youtube-mcp-server
- [X] T025 [US2] Refactor duplicated OpenAI example payloads and hosted check naming across ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py and ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/quickstart.md while keeping US2 tests green

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - Preserve Clarity Around Compatibility Boundaries (Priority: P3)

**Goal**: Make legacy-shape handling explicit so maintainers and operators can distinguish supported OpenAI behavior from prior repo-specific retrieval behavior.

**Independent Test**: Review the discovery contract, run the unsupported legacy-shape checks, and confirm the system either adapts legacy requests through a documented path or rejects them with stable structured errors and matching verification evidence.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add unit tests for unsupported legacy retrieval shapes and compatibility-boundary failures in ~/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py
- [X] T027 [P] [US3] Add contract tests for documented compatibility-boundary behavior in ~/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py
- [X] T028 [P] [US3] Add hosted verification and integration checks for legacy-shape failures in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py
- [X] T029 [US3] Run the US3 Red test suite with `pytest tests/unit/test_retrieval_tools.py tests/contract/test_deep_research_tools_contract.py tests/integration/test_hosted_http_routes.py` from ~/Projects/youtube-mcp-server

### Implementation for User Story 3

- [X] T030 [P] [US3] Implement explicit legacy-shape rejection or adaptation behavior in ~/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py
- [X] T031 [P] [US3] Update compatibility-boundary discovery and descriptor wording in ~/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py
- [X] T032 [P] [US3] Update the public compatibility-boundary contract in ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/contracts/openai-retrieval-compatibility-contract.md
- [X] T033 [US3] Update the compatibility-boundary operator and developer guidance in ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/quickstart.md
- [X] T034 [US3] Verify the US3 Green suite passes with `pytest tests/unit/test_retrieval_tools.py tests/contract/test_deep_research_tools_contract.py tests/integration/test_hosted_http_routes.py` from ~/Projects/youtube-mcp-server
- [X] T035 [US3] Refactor compatibility-boundary constants and error messages in ~/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py and ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/contracts/openai-retrieval-compatibility-contract.md while keeping US3 tests green

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final alignment, regression proof, and completion gating across all stories

- [X] T036 [P] Update feature-specific contract, research, and data-model wording for final implementation reality in ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/research.md, ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/data-model.md, and ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/spec.md
- [X] T037 [P] Add any final retrieval regression coverage needed across ~/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py, ~/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py, and ~/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py
- [X] T038 Run quickstart validation against ~/Projects/youtube-mcp-server/specs/023-openai-retrieval-compatibility/quickstart.md and record any required corrections in that file
- [X] T039 Run the full repository test suite with `pytest` from ~/Projects/youtube-mcp-server and resolve any failing tests before completion
- [X] T040 Run the full repository lint suite with `ruff check .` from ~/Projects/youtube-mcp-server and resolve any failing issues before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user story work.
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP slice.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because docs and hosted examples must reflect the implemented OpenAI-compatible runtime behavior.
- **User Story 3 (Phase 5)**: Depends on User Story 1 and can proceed after the core OpenAI-compatible contract exists.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational and has no dependency on other stories.
- **User Story 2 (P2)**: Depends on User Story 1 runtime behavior but remains independently testable through documentation-backed and hosted verification checks.
- **User Story 3 (P3)**: Depends on User Story 1 runtime behavior and remains independently testable through legacy-shape and contract-boundary checks.

### Within Each User Story

- Tests MUST be written and FAIL before implementation.
- Schema and contract publication changes precede handler and verifier changes.
- Runtime behavior changes precede documentation finalization.
- Refactor tasks happen only after the story’s Green suite passes.
- Before marking the feature complete, run the full repository test suite and lint suite and fix any failures.

### Story Completion Order

1. **US1**: OpenAI-compatible retrieval contract and runtime behavior
2. **US2**: OpenAI-specific docs and hosted verification flow
3. **US3**: Compatibility-boundary clarity and legacy-shape behavior

### Parallel Opportunities

- `T002` and `T003` can run in parallel during Setup.
- `T005`, `T006`, and `T007` can run in parallel during Foundational work.
- `T008`, `T009`, and `T010` can run in parallel for US1 Red tests.
- `T012` and `T013` can run in parallel for US1 Green implementation.
- `T018` and `T019` can run in parallel for US2 Red tests.
- `T021` and `T022` can run in parallel for US2 Green implementation.
- `T026`, `T027`, and `T028` can run in parallel for US3 Red tests.
- `T030`, `T031`, and `T032` can run in parallel for US3 Green implementation.
- `T036` and `T037` can run in parallel during Polish.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "Add unit tests for OpenAI-compatible retrieval schemas and validation in tests/unit/test_retrieval_tools.py"
Task: "Add contract tests for OpenAI-compatible tools/list, search, and fetch payloads in tests/contract/test_deep_research_tools_contract.py"
Task: "Add integration tests for OpenAI-compatible search to fetch MCP flow in tests/integration/test_mcp_request_flow.py"

# Launch independent US1 implementation tasks together:
Task: "Update OpenAI-compatible search and fetch schemas plus sample-source identifiers in src/mcp_server/tools/retrieval.py"
Task: "Update retrieval tool discovery descriptors and descriptions in src/mcp_server/tools/dispatcher.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "Add docs-example integration coverage for OpenAI retrieval examples in tests/integration/test_cloud_run_docs_examples.py"
Task: "Add hosted-route integration coverage for OpenAI retrieval checks in tests/integration/test_hosted_http_routes.py"

# Launch independent US2 implementation tasks together:
Task: "Update OpenAI-specific retrieval examples and execution steps in specs/023-openai-retrieval-compatibility/quickstart.md"
Task: "Update hosted verification check names and request payloads for OpenAI retrieval flow in scripts/verify_cloud_run_foundation.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "Add unit tests for unsupported legacy retrieval shapes and compatibility-boundary failures in tests/unit/test_retrieval_tools.py"
Task: "Add contract tests for documented compatibility-boundary behavior in tests/contract/test_deep_research_tools_contract.py"
Task: "Add hosted verification and integration checks for legacy-shape failures in tests/integration/test_hosted_http_routes.py"

# Launch independent US3 implementation tasks together:
Task: "Implement explicit legacy-shape rejection or adaptation behavior in src/mcp_server/tools/retrieval.py"
Task: "Update compatibility-boundary discovery and descriptor wording in src/mcp_server/tools/dispatcher.py"
Task: "Update the public compatibility-boundary contract in specs/023-openai-retrieval-compatibility/contracts/openai-retrieval-compatibility-contract.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate OpenAI-compatible discovery plus `search` to `fetch` flow independently.

### Incremental Delivery

1. Deliver US1 to establish the OpenAI-compatible runtime contract.
2. Deliver US2 to make the supported flow easy to follow and verify.
3. Deliver US3 to make legacy-shape behavior explicit and maintainable.
4. Finish with Polish and full-suite verification.

### Parallel Team Strategy

1. One developer handles Setup and Foundational work.
2. After Foundational completion:
   - Developer A: US1 runtime and schema work
   - Developer B: US2 docs and hosted verification work after US1 contract stabilizes
   - Developer C: US3 compatibility-boundary work after US1 contract stabilizes

---

## Notes

- All tasks use the required checklist format with task ID, optional `[P]`, optional story label, and exact file path.
- The suggested MVP scope is **User Story 1** only.
- Final completion evidence requires both `pytest` and `ruff check .` to pass from the repository root.
