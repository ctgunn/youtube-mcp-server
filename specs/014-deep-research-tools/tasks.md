# Tasks: Deep Research Tool Foundation

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/data-model.md), [contracts/deep-research-tools-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/contracts/deep-research-tools-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes explicit Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because the task touches a different file and has no dependency on unfinished tasks in the same phase
- **[Story]**: User story label for story-specific work (`[US1]`, `[US2]`, `[US3]`)
- Every task includes an absolute file path

## Path Conventions

- Runtime code lives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Contract, integration, and unit tests live under `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/`
- Feature docs live under `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the FND-014 work area and isolate the new retrieval-tool coverage before runtime changes begin

- [X] T001 Review and align FND-014 design inputs in `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/contracts/deep-research-tools-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/quickstart.md`
- [X] T002 [P] Create the dedicated deep-research contract test module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T003 [P] Create the dedicated retrieval-tool unit test module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared retrieval abstractions, schemas, and error mapping required by all user stories

**⚠️ CRITICAL**: No user story work should start until this phase is complete

- [X] T004 [P] Add failing unit tests for shared retrieval request validation, stateless reference normalization, and failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`
- [X] T005 [P] Add failing contract tests for deep-research tool discovery metadata and shared MCP error categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T006 Implement shared retrieval request/result models, reference parsing, and retrieval exceptions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`
- [X] T007 Extend MCP tool-call error mapping for retrieval-specific failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T008 Extend dispatcher bootstrap support for non-baseline retrieval tools in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T009 Refactor shared retrieval helper usage across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, then rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`

**Checkpoint**: Shared retrieval contract and error primitives are ready; user stories can now proceed in order

---

## Phase 3: User Story 1 - Discover Relevant Sources (Priority: P1) 🎯 MVP

**Goal**: Add a discoverable `search` MCP tool that validates inputs and returns structured candidate sources with stable follow-up identifiers

**Independent Test**: Invoke `search` through `tools/list` and `tools/call` on the protected MCP route and confirm valid queries return structured results, empty queries are rejected, and no-result searches return an empty result set without becoming errors

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add failing contract tests for `search` discovery metadata and success-result shape in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T011 [P] [US1] Add failing integration tests for successful and no-result `search` flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`
- [X] T012 [P] [US1] Add failing unit tests for `search` schema validation, result ordering, and pagination fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement `search` request validation and search-result builders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`
- [X] T014 [US1] Register the `search` tool and expose its schema through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T015 [US1] Ensure `search` results serialize into MCP-aligned structured content in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T016 [US1] Refactor `search` helper flow across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, then rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

**Checkpoint**: User Story 1 is complete when `search` is discoverable and independently callable with valid, invalid, and no-result coverage

---

## Phase 4: User Story 2 - Retrieve Selected Content (Priority: P2)

**Goal**: Add a `fetch` MCP tool that accepts a search-derived reference or canonical URI and returns one selected source in structured content form

**Independent Test**: Call `fetch` with a result reference returned by `search` and confirm the service returns source identity plus content; then call it with malformed or unavailable targets and confirm it returns stable MCP-safe failures

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T017 [P] [US2] Extend contract tests for `fetch` request validation, success-result shape, and retrieval-safe errors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T018 [P] [US2] Extend integration tests for `search` to `fetch` handoff and unavailable-source fetch flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`
- [X] T019 [P] [US2] Extend unit tests for `fetch` identifier parsing, resource-to-URI matching, and failure mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`

### Implementation for User Story 2

- [X] T020 [US2] Implement `fetch` request parsing, source retrieval payload shaping, and unavailable-source handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`
- [X] T021 [US2] Register the `fetch` tool and expose its schema through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US2] Map retrieval failures from `fetch` into MCP-safe error responses in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T023 [US2] Refactor shared retrieval-reference handling across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, then rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

**Checkpoint**: User Stories 1 and 2 are complete when a consumer can discover results with `search` and retrieve one selected source with `fetch` without relying on additional setup

---

## Phase 5: User Story 3 - Verify Hosted Research Readiness (Priority: P3)

**Goal**: Publish and verify hosted MCP examples showing `search` and `fetch` discovery, invocation, and expected failure behavior on the protected remote endpoint

**Independent Test**: Follow the documented hosted verification flow against the protected `/mcp` route and confirm both tools are discoverable, one `search` and one `fetch` call succeed, and representative invalid or unavailable calls fail with the documented behavior

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Add failing documentation example tests for hosted `search` and `fetch` usage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`
- [X] T025 [P] [US3] Add failing hosted verification coverage for `search` and `fetch` smoke checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T026 [P] [US3] Extend hosted contract assertions for deep-research tool discovery and invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`

### Implementation for User Story 3

- [X] T027 [US3] Update hosted `search` and `fetch` usage examples in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [X] T028 [US3] Align operator quickstart steps and expected evidence for deep-research verification in `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/quickstart.md`
- [X] T029 [US3] Extend Cloud Run verification smoke coverage for `search` and `fetch` in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T030 [US3] Refactor duplicated hosted verification language across `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/quickstart.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/contracts/deep-research-tools-contract.md`, then rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`

**Checkpoint**: All three user stories are complete when hosted docs and verification tooling prove the new tools work end to end on the protected MCP surface

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish regression coverage and contract/document cleanup that spans multiple stories

- [X] T031 [P] Add cross-story hosted regression coverage for deep-research tool routing and protected MCP behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`
- [X] T032 [P] Update final contract examples, edge-case notes, and hosted evidence expectations in `/Users/ctgunn/Projects/youtube-mcp-server/specs/014-deep-research-tools/contracts/deep-research-tools-contract.md`
- [X] T033 Run the full FND-014 regression suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_tool_registry.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can begin immediately
- **Foundational (Phase 2)**: Depends on Setup; blocks all user-story implementation
- **User Story 1 (Phase 3)**: Depends on Foundational; establishes the MVP
- **User Story 2 (Phase 4)**: Depends on User Story 1 because `fetch` must consume the discovery contract established by `search`
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 because hosted verification must cover both tools
- **Polish (Phase 6)**: Depends on all targeted user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; no dependency on other user stories
- **User Story 2 (P2)**: Starts after US1 because it relies on the search-result reference contract
- **User Story 3 (P3)**: Starts after US1 and US2 because it validates and documents both tool flows together

### Within Each User Story

- Write the listed tests first and confirm they fail
- Implement only the minimum code or documentation changes needed to make those tests pass
- Refactor only after the story-specific tests are green
- Re-run the listed story-specific suites before marking the story complete

### Dependency Graph

- `Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6`

### Parallel Opportunities

- `T002` and `T003` can run in parallel during Setup
- `T004` and `T005` can run in parallel during Foundational Red work
- `T010`, `T011`, and `T012` can run in parallel for US1 Red work
- `T017`, `T018`, and `T019` can run in parallel for US2 Red work
- `T024`, `T025`, and `T026` can run in parallel for US3 Red work
- `T031` and `T032` can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "T010 Add failing contract tests for search discovery metadata and success-result shape in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py"
Task: "T011 Add failing integration tests for successful and no-result search flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
Task: "T012 Add failing unit tests for search schema validation, result ordering, and pagination fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "T017 Extend contract tests for fetch request validation, success-result shape, and retrieval-safe errors in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py"
Task: "T018 Extend integration tests for search to fetch handoff and unavailable-source fetch flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
Task: "T019 Extend unit tests for fetch identifier parsing, resource-to-URI matching, and failure mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "T024 Add failing documentation example tests for hosted search and fetch usage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
Task: "T025 Add failing hosted verification coverage for search and fetch smoke checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
Task: "T026 Extend hosted contract assertions for deep-research tool discovery and invocation in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate `search` independently before moving on

### Incremental Delivery

1. Deliver the shared retrieval foundation
2. Deliver US1 so deep-research consumers can discover candidate sources
3. Deliver US2 so consumers can retrieve one selected source
4. Deliver US3 so operators can verify and document the hosted flow
5. Finish with cross-story regression and contract cleanup

### Parallel Team Strategy

1. One engineer can own Phase 2 shared retrieval primitives
2. After Phase 2, one engineer can take US1 while another prepares US3 Red tests on separate files
3. Once US1 stabilizes, another engineer can implement US2 without blocking the hosted-doc work in US3

---

## Notes

- Every task uses the required checklist format: checkbox, task ID, optional `[P]`, optional `[US#]`, and an absolute file path
- Setup, Foundational, and Polish tasks intentionally omit story labels
- User-story tasks always include the correct `[US#]` label for traceability
- The MVP scope is User Story 1 only
