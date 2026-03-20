# Tasks: Retrieval Tool Contract Completeness

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/data-model.md), [contracts/retrieval-tool-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/contracts/retrieval-tool-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes explicit Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because the task touches a different file and has no dependency on unfinished tasks in the same phase
- **[Story]**: User story label for story-specific work (`[US1]`, `[US2]`, `[US3]`)
- Every task includes an absolute file path

## Path Conventions

- Runtime code lives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Contract, integration, and unit tests live under `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/`
- Feature docs live under `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the FND-017 work area and lock the implementation scope to the discovery-contract seams before runtime changes begin.

- [X] T001 Review and align FND-017 design inputs in `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/contracts/retrieval-tool-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/quickstart.md`
- [X] T002 [P] Add FND-017 implementation notes and expected verification targets to `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/quickstart.md`
- [X] T003 [P] Align repository-level retrieval contract goals and discovery-driven verification notes in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared schema-composition and validation-alignment primitives that all user stories depend on.

**⚠️ CRITICAL**: No user story work should start until this phase is complete

- [X] T004 [P] Add failing unit coverage for schema-composition support and unsupported-field handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`
- [X] T005 [P] Add failing contract coverage for composed retrieval discovery schemas in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T006 Implement shared retrieval schema constants and request-shape helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`
- [X] T007 Implement composed object-schema validation support for retrieval input schemas in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T008 Refactor shared retrieval schema usage across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, then rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`

**Checkpoint**: Shared schema and validation primitives are ready; user stories can proceed in priority order.

---

## Phase 3: User Story 1 - Discover a Valid Fetch Shape (Priority: P1) 🎯 MVP

**Goal**: Publish a fully machine-readable `fetch` contract so clients can construct every supported identifier pattern without trial-and-error.

**Independent Test**: List tools, inspect the `fetch` descriptor, then call `fetch` successfully by `resourceId`, by `uri`, and by matching `resourceId` plus `uri`; confirm missing identifiers and conflicting identifiers fail with the documented structured error.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T009 [P] [US1] Add failing unit tests for valid and invalid `fetch` identifier combinations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`
- [X] T010 [P] [US1] Add failing contract tests for machine-readable `fetch` discovery metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T011 [P] [US1] Add failing integration tests for `fetch` by `resourceId`, by `uri`, by matching identifiers, and by invalid combinations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`
- [X] T012 [P] [US1] Add failing hosted-route integration coverage for discovery-driven `fetch` request patterns in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`

### Implementation for User Story 1

- [X] T013 [US1] Update `FETCH_TOOL_SCHEMA` and `fetch` request-shape validation to reflect the supported identifier patterns in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`
- [X] T014 [US1] Expose the completed `fetch` discovery descriptor through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T015 [US1] Align `fetch` invocation error mapping and structured result handling with the completed request contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T016 [US1] Refactor `fetch` contract helpers and rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`

**Checkpoint**: User Story 1 is complete when `fetch` can be constructed and validated entirely from discovery output.

---

## Phase 4: User Story 2 - Trust Discovery for Search Inputs (Priority: P2)

**Goal**: Ensure the published `search` contract is complete and stays aligned with the real runtime acceptance and rejection rules.

**Independent Test**: List tools, inspect the `search` descriptor, then call `search` with a valid query and optional controls; confirm invalid empty or malformed requests fail as the descriptor implies and a no-results search remains a non-error outcome.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T017 [P] [US2] Add failing unit tests for `search` schema completeness, optional controls, and invalid field handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`
- [X] T018 [P] [US2] Add failing contract tests for `search` discovery metadata and invalid-request alignment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T019 [P] [US2] Add failing integration tests for discovery-driven `search` success, no-results, and invalid-input flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

### Implementation for User Story 2

- [X] T020 [US2] Tighten `SEARCH_TOOL_SCHEMA` and `search` request validation so discovery and runtime rules match in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`
- [X] T021 [US2] Expose the completed `search` discovery descriptor through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T022 [US2] Align `search` validation failures and no-results handling with the published contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T023 [US2] Refactor `search` contract helpers and rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

**Checkpoint**: User Story 2 is complete when `search` inputs are fully self-describing and behave exactly as discovery advertises.

---

## Phase 5: User Story 3 - Verify Contract and Runtime Stay Aligned (Priority: P3)

**Goal**: Prove through documentation and hosted verification that retrieval requests can be built from discovery output alone and that the live service matches the published contract.

**Independent Test**: Follow the documented hosted flow, verify `tools/list` exposes the completed retrieval schemas, run one valid `search` request and every supported valid `fetch` pattern, then confirm invalid `fetch` shapes fail with the documented outcomes.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Add failing documentation-example coverage for completed retrieval discovery and call patterns in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`
- [X] T025 [P] [US3] Add failing hosted verification coverage for discovery-driven retrieval requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T026 [P] [US3] Extend contract coverage for hosted retrieval discovery and invocation alignment in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`

### Implementation for User Story 3

- [X] T027 [US3] Update hosted retrieval discovery and invocation examples in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [X] T028 [US3] Update local and hosted discovery-driven validation steps in `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/quickstart.md`
- [X] T029 [US3] Extend retrieval smoke checks and evidence capture for discovery-driven request patterns in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T030 [US3] Align hosted verification serialization and named checks for retrieval contract completeness in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T031 [US3] Refactor retrieval verification wording and rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`

**Checkpoint**: User Story 3 is complete when hosted docs and verification prove discovery-driven retrieval requests end to end.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish regression coverage and cross-story contract cleanup.

- [X] T032 [P] Add cross-story hosted regression coverage for retrieval-tool discovery metadata on `/mcp` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`
- [X] T033 [P] Update final contract examples and edge-case notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/contracts/retrieval-tool-contract.md`
- [X] T034 Run the full FND-017 regression suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can begin immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user-story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational; establishes the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and can proceed after US1 if shared files are coordinated.
- **User Story 3 (Phase 5)**: Depends on US1 and US2 because verification must cover the completed retrieval contract.
- **Polish (Phase 6)**: Depends on all targeted user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; no dependency on later stories.
- **User Story 2 (P2)**: Starts after Phase 2; independently testable, but shares retrieval contract files with US1.
- **User Story 3 (P3)**: Starts after US1 and US2 because hosted verification must cover the final retrieval contract.

### Within Each User Story

- Write the listed tests first and confirm they fail.
- Implement only the minimum code or documentation changes needed to make those tests pass.
- Refactor only after the story-specific tests are green.
- Re-run the listed story-specific suites before marking the story complete.

### Dependency Graph

- `Phase 1 -> Phase 2 -> {US1, US2} -> US3 -> Phase 6`

### Parallel Opportunities

- `T002` and `T003` can run in parallel during Setup.
- `T004` and `T005` can run in parallel during Foundational Red work.
- `T009`, `T010`, `T011`, and `T012` can run in parallel for US1 Red work.
- `T017`, `T018`, and `T019` can run in parallel for US2 Red work.
- `T024`, `T025`, and `T026` can run in parallel for US3 Red work.
- `T032` and `T033` can run in parallel during Polish.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "T009 Add failing unit tests for valid and invalid fetch identifier combinations in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py"
Task: "T010 Add failing contract tests for machine-readable fetch discovery metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py"
Task: "T011 Add failing integration tests for fetch by resourceId, by uri, by matching identifiers, and by invalid combinations in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
Task: "T012 Add failing hosted-route integration coverage for discovery-driven fetch request patterns in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "T017 Add failing unit tests for search schema completeness, optional controls, and invalid field handling in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py"
Task: "T018 Add failing contract tests for search discovery metadata and invalid-request alignment in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py"
Task: "T019 Add failing integration tests for discovery-driven search success, no-results, and invalid-input flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "T024 Add failing documentation-example coverage for completed retrieval discovery and call patterns in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
Task: "T025 Add failing hosted verification coverage for discovery-driven retrieval requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
Task: "T026 Extend contract coverage for hosted retrieval discovery and invocation alignment in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate `fetch` discovery and invocation independently before moving on.

### Incremental Delivery

1. Deliver the shared schema and validation foundation.
2. Deliver US1 so clients can infer valid `fetch` requests from discovery.
3. Deliver US2 so `search` inputs are equally discovery-driven and aligned.
4. Deliver US3 so hosted docs and verification prove the completed retrieval contract.
5. Finish with cross-story regression and contract cleanup.

### Parallel Team Strategy

1. One engineer can own Phase 2 shared schema validation while another prepares Setup documentation updates.
2. After Phase 2, one engineer can implement US1 while another prepares US2 Red tests on separate files.
3. Once US1 and US2 stabilize, another engineer can take US3 verification and documentation work without blocking retrieval runtime changes.

---

## Notes

- Every task uses the required checklist format: checkbox, task ID, optional `[P]`, optional `[US#]`, and an absolute file path.
- Setup, Foundational, and Polish tasks intentionally omit story labels.
- User-story tasks always include the correct `[US#]` label for traceability.
- The MVP scope is User Story 1 only.
