# Tasks: Remote MCP Security and Transport Hardening

**Input**: Design documents from `/specs/013-remote-mcp-security/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout with runtime code in `src/` and tests in `tests/`
- Hosted MCP runtime code lives under `src/mcp_server/`
- Contract, integration, and unit coverage live under `tests/contract/`, `tests/integration/`, and `tests/unit/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the repo for the FND-013 security slice without changing runtime behavior yet

- [X] T001 Review and align feature docs in `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md`
- [X] T002 [P] Add hosted security environment examples to `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [X] T003 [P] Create a dedicated security task target list in `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 [P] Add unit tests for hosted security configuration parsing and validation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_security_config.py`
- [X] T005 [P] Add unit tests for origin trust and bearer credential evaluation helpers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_hosted_security_policy.py`
- [X] T006 [P] Add contract coverage for protected `/mcp` authentication and origin requirements in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py`
- [X] T007 Implement shared hosted security models and policy evaluators in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/security.py`
- [X] T008 Extend runtime security settings and startup validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py`
- [X] T009 Wire shared security configuration into app creation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/app.py`
- [X] T010 Refactor shared security helpers across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/security.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/app.py`, then rerun `pytest tests/unit/test_hosted_security_config.py tests/unit/test_hosted_security_policy.py tests/contract/test_hosted_mcp_security_contract.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Protect the Hosted MCP Entry Point (Priority: P1) 🎯 MVP

**Goal**: Reject unsafe browser origins and unauthenticated remote MCP requests before session creation, stream access, or tool execution

**Independent Test**: Send hosted `/mcp` requests with approved and denied origin/auth combinations and confirm only approved requests proceed into normal MCP handling

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Add unit tests for hosted request security gating in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_cloud_run_security_gate.py`
- [X] T012 [P] [US1] Add integration tests for denied and accepted hosted `/mcp` flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_mcp_security_flows.py`
- [X] T013 [P] [US1] Extend protected route contract assertions for session creation and stream denial in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py`

### Implementation for User Story 1

- [X] T014 [US1] Integrate origin and bearer-token enforcement into hosted request execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T015 [US1] Update hosted route classification and status mapping for security denials in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`
- [X] T016 [US1] Ensure protected session creation and stream reuse honor security decisions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py`
- [X] T017 [US1] Refactor hosted security gating paths in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py`, then rerun `pytest tests/unit/test_cloud_run_security_gate.py tests/integration/test_hosted_mcp_security_flows.py tests/contract/test_hosted_mcp_security_contract.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Give Integrators a Clear Consumption Contract (Priority: P2)

**Goal**: Publish clear, accurate documentation and verification guidance for authenticated hosted MCP use and expected denial behavior

**Independent Test**: Follow the published docs to complete one authenticated hosted MCP flow, then intentionally violate the documented auth/origin rules and confirm the docs describe the observed failures

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add documentation example tests for authenticated hosted usage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`
- [X] T019 [P] [US2] Add verification coverage for quickstart success and denial scenarios in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T020 [P] [US2] Add contract assertions for documented hosted security expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py`

### Implementation for User Story 2

- [X] T021 [US2] Update hosted usage, configuration, and curl examples in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [X] T022 [US2] Align operator verification steps and expected outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/quickstart.md`
- [X] T023 [US2] Refine the external hosted security contract language in `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md`
- [X] T024 [US2] Refactor duplicated documentation language in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/quickstart.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md`, then rerun `pytest tests/integration/test_cloud_run_docs_examples.py tests/integration/test_cloud_run_verification_flow.py tests/contract/test_hosted_mcp_security_contract.py`

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently, and integrators should have a usable hosted contract

---

## Phase 5: User Story 3 - Diagnose Security Failures Predictably (Priority: P3)

**Goal**: Emit stable client-visible denial categories and operator-visible security decision records without leaking secrets

**Independent Test**: Trigger representative denied hosted requests and confirm both the caller-facing failure type and the structured runtime log/event fields are sufficient for diagnosis

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T025 [P] [US3] Add unit tests for security decision record emission in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_security_observability.py`
- [X] T026 [P] [US3] Add integration tests for denied-request logging and request correlation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_security_request_observability.py`
- [X] T027 [P] [US3] Extend observability contract assertions for security denials in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_operational_observability_contract.py`

### Implementation for User Story 3

- [X] T028 [US3] Add structured security decision logging helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/observability.py`
- [X] T029 [US3] Thread security decision context through hosted request handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T030 [US3] Refine protected request metrics and denial outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`
- [X] T031 [US3] Refactor security observability paths in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/observability.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, then rerun `pytest tests/unit/test_security_observability.py tests/integration/test_security_request_observability.py tests/contract/test_operational_observability_contract.py`

**Checkpoint**: All user stories should now be independently functional and diagnosable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T032 [P] Update deployment and startup validation guidance for hosted security settings in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`
- [X] T033 [P] Extend hosted verification tooling for authenticated and denied flows in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T034 Add cross-story regression coverage for secured readiness and protected MCP flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py`
- [X] T035 Run the full feature regression suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `pytest tests/unit/test_hosted_security_config.py tests/unit/test_hosted_security_policy.py tests/unit/test_cloud_run_security_gate.py tests/unit/test_security_observability.py tests/integration/test_hosted_mcp_security_flows.py tests/integration/test_cloud_run_docs_examples.py tests/integration/test_cloud_run_verification_flow.py tests/integration/test_security_request_observability.py tests/integration/test_readiness_flow.py tests/contract/test_hosted_mcp_security_contract.py tests/contract/test_operational_observability_contract.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion; establishes the MVP
- **User Story 2 (Phase 4)**: Depends on User Story 1 behavior being defined so docs and verification match the implemented hosted contract
- **User Story 3 (Phase 5)**: Depends on User Story 1 enforcement paths existing so denial observability can be instrumented accurately
- **Polish (Phase 6)**: Depends on all targeted user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; no dependency on other user stories
- **User Story 2 (P2)**: Starts after US1 because it documents and verifies the secured behavior introduced there
- **User Story 3 (P3)**: Starts after US1 and can proceed in parallel with late US2 cleanup if staffing allows

### Within Each User Story

- Write the listed tests first and confirm they fail
- Implement only the minimum runtime, docs, or observability changes needed to make those tests pass
- Refactor after tests are green and rerun the story-specific suites before marking the story complete

### Dependency Graph

- `Phase 1 -> Phase 2 -> US1 -> {US2, US3} -> Phase 6`
- `US2` and `US3` both depend on the protected-route behavior introduced by `US1`

### Parallel Opportunities

- `T002` and `T003` can run in parallel during Setup
- `T004`, `T005`, and `T006` can run in parallel during Foundational work
- `T011`, `T012`, and `T013` can run in parallel for US1 Red work
- `T018`, `T019`, and `T020` can run in parallel for US2 Red work
- `T025`, `T026`, and `T027` can run in parallel for US3 Red work
- `T032` and `T033` can run in parallel during Polish

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "T011 Add unit tests for hosted request security gating in tests/unit/test_cloud_run_security_gate.py"
Task: "T012 Add integration tests for denied and accepted hosted /mcp flows in tests/integration/test_hosted_mcp_security_flows.py"
Task: "T013 Extend protected route contract assertions for session creation and stream denial in tests/contract/test_hosted_mcp_security_contract.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "T018 Add documentation example tests for authenticated hosted usage in tests/integration/test_cloud_run_docs_examples.py"
Task: "T019 Add verification coverage for quickstart success and denial scenarios in tests/integration/test_cloud_run_verification_flow.py"
Task: "T020 Add contract assertions for documented hosted security expectations in tests/contract/test_hosted_mcp_security_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "T025 Add unit tests for security decision record emission in tests/unit/test_security_observability.py"
Task: "T026 Add integration tests for denied-request logging and request correlation in tests/integration/test_security_request_observability.py"
Task: "T027 Extend observability contract assertions for security denials in tests/contract/test_operational_observability_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate secured `/mcp` behavior independently before moving on

### Incremental Delivery

1. Deliver the shared security foundation
2. Deliver US1 to secure hosted MCP access
3. Deliver US2 to document and verify the new contract
4. Deliver US3 to make denials observable and diagnosable
5. Finish with cross-cutting deployment and regression work

### Parallel Team Strategy

1. One engineer handles Phase 2 shared security infrastructure
2. After US1 begins, one engineer can own runtime enforcement while another prepares US2 docs/tests
3. Once US1 enforcement stabilizes, a third engineer can take US3 observability without blocking US2 documentation cleanup

---

## Notes

- Every task follows the required checklist format with a task ID and exact file path
- User story tasks include required `[US#]` labels; Setup, Foundational, and Polish tasks intentionally omit story labels
- `[P]` markers are used only where tasks can proceed on different files without waiting for incomplete dependent work
- Independent test criteria are taken directly from the feature spec and repeated at the top of each user story phase
