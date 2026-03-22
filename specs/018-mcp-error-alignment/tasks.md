# Tasks: JSON-RPC / MCP Error Code Alignment

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/data-model.md), [contracts/mcp-error-code-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/contracts/mcp-error-code-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes explicit Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because the task touches a different file and has no dependency on unfinished tasks in the same phase
- **[Story]**: User story label for story-specific work (`[US1]`, `[US2]`, `[US3]`)
- Every task includes an absolute file path

## Path Conventions

- Runtime code lives under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Contract, integration, and unit tests live under `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/`
- Feature docs live under `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align the FND-018 execution surface and documentation targets before runtime changes begin.

- [X] T001 Review and align FND-018 implementation inputs in `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/contracts/mcp-error-code-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/quickstart.md`
- [X] T002 [P] Align manual verification targets and expected numeric-code evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/quickstart.md`
- [X] T003 [P] Align feature-level contract references and migration notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/contracts/mcp-error-code-contract.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared numeric-code mapper and payload primitives that block all user stories.

**⚠️ CRITICAL**: No user story work should start until this phase is complete

- [X] T004 [P] Add failing unit coverage for numeric `error.code`, sanitized messages, and stable category detail in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_envelope_contract.py`
- [X] T005 [P] Add failing unit coverage for numeric malformed-request and unsupported-method routing in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T006 [P] Add failing contract coverage for the published numeric MCP error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py`
- [X] T007 Implement shared numeric error-code definitions and payload helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`
- [X] T008 Implement shared failure-category and precedence helpers for local and hosted flows in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T009 Refactor numeric error helper usage across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, then rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_envelope_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py`

**Checkpoint**: Shared numeric error primitives are ready; user stories can proceed in priority order.

---

## Phase 3: User Story 1 - Receive Protocol-Aligned Error Codes (Priority: P1) 🎯 MVP

**Goal**: Replace string-style local MCP error codes with the documented numeric mapping for malformed request, unsupported method, invalid argument, unknown-tool, and unexpected tool-failure paths.

**Independent Test**: Send representative malformed request, unsupported method, invalid tool argument, unknown-tool, and unexpected tool-failure cases through local MCP routing and confirm each response returns the documented numeric code, sanitized message, and stable category detail.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add failing unit tests for numeric invalid-argument and unknown-tool mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py`
- [X] T011 [P] [US1] Add failing unit tests for numeric retrieval-tool failure mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py`
- [X] T012 [P] [US1] Add failing contract tests for numeric malformed-request, unsupported-method, and invalid-argument MCP bodies in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py`
- [X] T013 [P] [US1] Add failing integration tests for local MCP failure journeys in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

### Implementation for User Story 1

- [X] T014 [US1] Implement numeric malformed-request, unsupported-method, and invalid-argument mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T015 [US1] Implement numeric unknown-tool and unexpected tool-failure mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T016 [US1] Align retrieval-tool error passthrough with the numeric error-code contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py`
- [X] T017 [US1] Refactor local error-category construction and rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

**Checkpoint**: User Story 1 is complete when local MCP failures no longer expose retired string-style top-level codes.

---

## Phase 4: User Story 2 - Trust Error Consistency Across Hosted and Local Flows (Priority: P2)

**Goal**: Reuse the numeric error-code mapping across hosted `/mcp` failures so equivalent local and hosted failure classes return the same code and category while preserving existing HTTP statuses.

**Independent Test**: Run malformed request, invalid argument, unauthenticated, origin-denied, missing-session, and tool-failure scenarios through local and hosted paths and confirm equivalent client-visible failures use the same numeric code and category detail.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing contract coverage for numeric hosted security and denial payloads in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py`
- [X] T019 [P] [US2] Add failing contract coverage for numeric hosted operational error payloads in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py`
- [X] T020 [P] [US2] Add failing integration coverage for numeric hosted HTTP failure flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`
- [X] T021 [P] [US2] Add failing integration coverage for local-versus-hosted numeric parity across auth, session, and tool failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py`

### Implementation for User Story 2

- [X] T022 [US2] Implement numeric hosted denial and invalid-request mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T023 [US2] Align hosted security decision categories with the numeric error-code contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/security.py`
- [X] T024 [US2] Align hosted resource-missing and replay/session failure mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T025 [US2] Refactor shared hosted-versus-local error mapping usage and rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py`

**Checkpoint**: User Stories 1 and 2 are complete when hosted `/mcp` failures preserve their HTTP semantics but match local numeric MCP error behavior.

---

## Phase 5: User Story 3 - Diagnose Failures Through One Documented Mapping (Priority: P3)

**Goal**: Publish and verify one documented numeric error mapping that downstream clients, operators, and future features can reuse without relying on retired string codes.

**Independent Test**: Review the published contract and verification artifacts, run one representative failure from each covered category, and confirm the observed code, category, and status behavior match the documented mapping.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T026 [P] [US3] Add failing contract coverage for numeric retrieval-tool failure examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py`
- [X] T027 [P] [US3] Add failing integration coverage for numeric deploy-verification and docs examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`
- [X] T028 [P] [US3] Add failing integration coverage for numeric hosted verification evidence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`

### Implementation for User Story 3

- [X] T029 [US3] Update downstream retrieval failure contract examples to numeric codes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/017-retrieval-tool-contract/contracts/retrieval-tool-contract.md`
- [X] T030 [US3] Update hosted verification checks and named failure assertions in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T031 [US3] Update deploy-time verification serialization and expected error assertions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T032 [US3] Update repository-level operator guidance for numeric MCP error verification in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [X] T033 [US3] Refactor final contract wording and rerun `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`

**Checkpoint**: User Story 3 is complete when the published mapping, docs, and verification evidence all describe and assert the same numeric contract.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish cross-story regression coverage and final release-readiness validation.

- [X] T034 [P] Add cross-story hosted parity regression coverage for numeric error categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_mcp_security_flows.py`
- [X] T035 [P] Update final FND-018 quick validation steps and regression commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/018-mcp-error-alignment/quickstart.md`
- [X] T036 Run the full FND-018 regression suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_envelope_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_mcp_security_flows.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can begin immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user-story implementation.
- **User Story 1 (Phase 3)**: Depends on Foundational; establishes the MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 because hosted parity should reuse the final local numeric mapping.
- **User Story 3 (Phase 5)**: Depends on User Stories 1 and 2 because published verification must reflect the implemented local and hosted contract.
- **Polish (Phase 6)**: Depends on all targeted user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2 and is independently testable.
- **User Story 2 (P2)**: Starts after US1 establishes the shared numeric mapping for local flows.
- **User Story 3 (P3)**: Starts after US1 and US2 establish the final runtime behavior and verification targets.

### Within Each User Story

- Write the listed tests first and confirm they fail.
- Implement only the minimum code or documentation changes needed to make those tests pass.
- Refactor only after the story-specific tests are green.
- Re-run the listed story-specific suites before marking the story complete.

### Dependency Graph

- `Phase 1 -> Phase 2 -> US1 -> US2 -> US3 -> Phase 6`

### Parallel Opportunities

- `T002` and `T003` can run in parallel during Setup.
- `T004`, `T005`, and `T006` can run in parallel during Foundational Red work.
- `T010`, `T011`, `T012`, and `T013` can run in parallel for US1 Red work.
- `T018`, `T019`, `T020`, and `T021` can run in parallel for US2 Red work.
- `T026`, `T027`, and `T028` can run in parallel for US3 Red work.
- `T034` and `T035` can run in parallel during Polish.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "T010 Add failing unit tests for numeric invalid-argument and unknown-tool mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_invoke_error_mapping.py"
Task: "T011 Add failing unit tests for numeric retrieval-tool failure mapping in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_retrieval_tools.py"
Task: "T012 Add failing contract tests for numeric malformed-request, unsupported-method, and invalid-argument MCP bodies in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py"
Task: "T013 Add failing integration tests for local MCP failure journeys in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "T018 Add failing contract coverage for numeric hosted security and denial payloads in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py"
Task: "T019 Add failing contract coverage for numeric hosted operational error payloads in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py"
Task: "T020 Add failing integration coverage for numeric hosted HTTP failure flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
Task: "T021 Add failing integration coverage for local-versus-hosted numeric parity across auth, session, and tool failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "T026 Add failing contract coverage for numeric retrieval-tool failure examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_deep_research_tools_contract.py"
Task: "T027 Add failing integration coverage for numeric deploy-verification and docs examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
Task: "T028 Add failing integration coverage for numeric hosted verification evidence in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational numeric error primitives.
3. Complete Phase 3: User Story 1.
4. Stop and validate local numeric MCP failure behavior before moving on.

### Incremental Delivery

1. Deliver the shared numeric error helpers and precedence rules.
2. Deliver US1 so local MCP failures stop exposing retired string codes.
3. Deliver US2 so hosted and local failure behavior stays aligned.
4. Deliver US3 so contracts, deploy verification, and docs all reuse the same numeric mapping.
5. Finish with cross-story regression and final release validation.

### Parallel Team Strategy

1. One engineer can own foundational error helpers while another prepares the foundational failing tests.
2. After Phase 2, one engineer can implement US1 while another prepares US2 Red tests on separate hosted test files.
3. Once US2 stabilizes, another engineer can take US3 verification and documentation updates without blocking the shared runtime mapper.

---

## Notes

- Every task follows the required checklist format `- [ ] T### [P] [US#] Description with file path`.
- Setup, Foundational, and Polish tasks intentionally omit story labels.
- User-story tasks always include the correct `[US#]` label for traceability.
- The MVP scope is User Story 1 only.
