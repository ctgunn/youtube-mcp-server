# Tasks: Initialize Session Correctness

**Input**: Design documents from `/specs/024-initialize-session-correctness/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/data-model.md), [contracts/initialize-session-correctness-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/contracts/initialize-session-correctness-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes explicit Red-Green-Refactor coverage. Completion requires a passing full repository test-suite run after the final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align shared test helpers and execution scaffolding before lifecycle work begins

- [X] T001 Normalize hosted initialize payload helpers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/conftest.py`
- [X] T002 [P] Normalize hosted stream header helpers for initialize and continuation flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/conftest.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared lifecycle primitives and verifier seams that block all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add a reusable initialize-success predicate for hosted lifecycle decisions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`
- [X] T004 [P] Add initialize failure/success verifier check scaffolding in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Receive a Session Only After Successful Initialize (Priority: P1) 🎯 MVP

**Goal**: Ensure only successful initialize responses issue `MCP-Session-Id` and create usable hosted session state

**Independent Test**: Send valid, invalid, and malformed initialize requests through the hosted `/mcp` route and confirm only the successful response includes `MCP-Session-Id` and usable continuation state.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] [US1] Add unit tests for initialize success detection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T006 [P] [US1] Add contract tests for invalid initialize responses returning no `MCP-Session-Id` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py`
- [X] T007 [P] [US1] Add hosted route integration tests for malformed and invalid initialize requests creating no session in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`

### Implementation for User Story 1

- [X] T008 [US1] Gate session creation and initialize header emission on successful initialize outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T009 [US1] Refactor initialize response handling to reuse the shared success predicate in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T010 [US1] Re-run targeted US1 lifecycle suites from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py`

**Checkpoint**: User Story 1 should now be independently functional and testable as the MVP slice

---

## Phase 4: User Story 2 - Trust Hosted Session Lifecycle State (Priority: P2)

**Goal**: Ensure retries after failed initialize create fresh valid state and continuation works only for sessions issued from successful initialize responses

**Independent Test**: Exercise failed initialize, successful retry, valid continuation, and non-issued-session continuation against the hosted `/mcp` route and confirm only successfully initialized sessions are recognized.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T011 [P] [US2] Add contract tests for unauthorized initialize returning no session header in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py`
- [X] T012 [P] [US2] Add stream transport integration tests for retry-after-failure and invalid continuation behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py`
- [X] T013 [P] [US2] Add request-flow regression coverage for continuation using only issued sessions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

### Implementation for User Story 2

- [X] T014 [US2] Enforce retry-after-failure and non-issued-session continuation behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- [X] T015 [US2] Distinguish rejected initialize decisions from continuation decisions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/observability.py`
- [X] T016 [US2] Re-run targeted US2 continuation suites from `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py`

**Checkpoint**: User Stories 1 and 2 should both work independently, with retry and continuation semantics locked down

---

## Phase 5: User Story 3 - Verify and Document Handshake Rules Consistently (Priority: P3)

**Goal**: Align hosted verification evidence and public documentation with the corrected initialize/session lifecycle

**Independent Test**: Run verification-flow and docs-example tests and confirm they prove both the failing no-session initialize path and the successful session-creation path exactly as documented.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T017 [P] [US3] Add verification-flow tests for initialize failure/success evidence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py`
- [X] T018 [P] [US3] Add documentation-backed assertions for failed initialize with no `MCP-Session-Id` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`

### Implementation for User Story 3

- [X] T019 [US3] Update initialize verification checks and evidence output in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [X] T020 [US3] Surface the corrected initialize verification evidence in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py`
- [X] T021 [US3] Document the corrected initialize/session lifecycle in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [X] T022 [US3] Re-run targeted US3 verification and docs suites from `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py`

**Checkpoint**: All user stories should now be independently functional, verified, and documented

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, manual validation, and full-suite proof

- [X] T023 [P] Validate the manual lifecycle checks in `/Users/ctgunn/Projects/youtube-mcp-server/specs/024-initialize-session-correctness/quickstart.md`
- [X] T024 Run the full repository test suite and lint checks covering `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - blocks all user stories
- **Phase 3 (US1)**: Depends on Phase 2 completion
- **Phase 4 (US2)**: Depends on Phase 2 completion and should build on the US1 lifecycle gate in `cloud_run_entrypoint.py`
- **Phase 5 (US3)**: Depends on the US1/US2 behavior being implemented so verification and docs can reflect final runtime behavior
- **Phase 6 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational phase completion - no story dependency
- **US2 (P2)**: Can start after Foundational phase completion but depends on the US1 session-creation gate landing first in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py`
- **US3 (P3)**: Depends on US1 and US2 because verification and docs must describe the final corrected behavior

### Within Each User Story

- Tests MUST be written and fail before implementation
- Shared helpers before runtime behavior changes
- Runtime behavior changes before documentation or verifier output changes
- Refactor only after targeted tests pass
- Before feature completion, run the full repository test suite and fix any failures

---

## Parallel Opportunities

- **Setup**: T001 and T002 can run in parallel because they update different helper files
- **Foundational**: T003 and T004 can run in parallel because protocol helper work and verifier scaffolding live in different files
- **US1**: T005, T006, and T007 can run in parallel because they touch different test files
- **US2**: T011, T012, and T013 can run in parallel because they touch different test files
- **US3**: T017 and T018 can run in parallel because they touch different integration test files
- **Polish**: T023 can run before T024 once implementation is complete

---

## Parallel Example: User Story 1

```bash
# Launch all Red tests for User Story 1 together:
Task: "Add unit tests for initialize success detection in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
Task: "Add contract tests for invalid initialize responses returning no MCP-Session-Id in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
Task: "Add hosted route integration tests for malformed and invalid initialize requests creating no session in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 2

```bash
# Launch all Red tests for User Story 2 together:
Task: "Add contract tests for unauthorized initialize returning no session header in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py"
Task: "Add stream transport integration tests for retry-after-failure and invalid continuation behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
Task: "Add request-flow regression coverage for continuation using only issued sessions in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_request_flow.py"
```

## Parallel Example: User Story 3

```bash
# Launch all Red tests for User Story 3 together:
Task: "Add verification-flow tests for initialize failure/success evidence in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
Task: "Add documentation-backed assertions for failed initialize with no MCP-Session-Id in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate US1 independently with the targeted tests in T010
5. Stop if only the MVP correction is needed

### Incremental Delivery

1. Finish Setup + Foundational so lifecycle primitives and verifier scaffolding are ready
2. Deliver US1 to stop invalid session issuance on failed initialize
3. Deliver US2 to harden retry and continuation semantics
4. Deliver US3 to align verifier evidence and public docs with the final behavior
5. Finish with quickstart validation and the full repository suite

### Parallel Team Strategy

1. One developer handles helper and protocol groundwork in Phases 1-2
2. After Phase 2, test-writing tasks inside each story can run in parallel
3. Runtime changes in `cloud_run_entrypoint.py` should stay serialized to avoid merge conflicts
4. Verification/docs work in US3 can proceed once US1 and US2 runtime behavior is stable

---

## Notes

- All tasks use the required checklist format: checkbox, task ID, optional `[P]`, required `[US#]` label for story tasks, and exact file paths
- User stories are intentionally scoped for independent testing, even though US2 and US3 build on the runtime correction introduced by US1
- The final completion gate is the full repository run in T024, not the targeted story runs
