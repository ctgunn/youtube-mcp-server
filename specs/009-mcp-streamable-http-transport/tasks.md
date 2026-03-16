# Tasks: FND-009 MCP Streamable HTTP Transport

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/contracts/mcp-streamable-http-contract.md`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the dedicated test surfaces and task scaffolding for FND-009 work.

- [X] T001 Create streamable transport unit test module in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py
- [X] T002 [P] Create streamable transport integration test module in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py
- [X] T003 [P] Create streamable transport contract test module in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared session-state, SSE, and hosted transport helpers that every story depends on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement shared `HostedMCPSession`, `StreamChannel`, and `StreamEvent` state helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py
- [X] T005 [P] Implement shared SSE event encoding and replay cursor helpers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/conftest.py
- [X] T006 [P] Add reusable hosted stream assertion fixtures in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/conftest.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/conftest.py
- [X] T007 Implement shared streamable request parsing and header normalization hooks in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Establish a Compliant Hosted MCP Session (Priority: P1) 🎯 MVP

**Goal**: Accept standards-aligned streamable `GET` and `POST` MCP session establishment requests, issue session identifiers when appropriate, and reject invalid transport requests deterministically.

**Independent Test**: Exercise valid and invalid hosted session-establishment requests against `/mcp` and confirm the server negotiates the expected method, headers, and session outcome without relying on custom request conventions.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add red contract tests for `GET` and `POST` negotiation, session header issuance, and invalid-session failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py
- [X] T009 [P] [US1] Add red integration tests for hosted session establishment and invalid transport requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py
- [X] T010 [P] [US1] Add red unit tests for session registry transitions and transport header validation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py

### Implementation for User Story 1

- [X] T011 [US1] Implement session lifecycle and protocol-version validation in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py
- [X] T012 [US1] Update hosted MCP request classification for streamable `GET` and `POST` semantics in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py
- [X] T013 [US1] Implement session-aware hosted `GET` and `POST` handling plus `MCP-Session-Id` response headers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T014 [US1] Refactor session-establishment flow and re-run US1 suites in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py

**Checkpoint**: User Story 1 is independently functional when a client can establish or be denied a hosted MCP session solely through the documented streamable transport rules.

---

## Phase 4: User Story 2 - Receive Streamed MCP Responses and Server-Driven Events (Priority: P1)

**Goal**: Deliver ordered streamed responses and server-driven events over SSE, including reconnect-safe event IDs and isolation across concurrent sessions and streams.

**Independent Test**: Open a valid session, trigger streamed MCP activity, and confirm clients receive ordered SSE output, reconnect with `Last-Event-ID` when supported, and never receive events from another session or stream.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T015 [P] [US2] Add red contract tests for SSE response rules, event ordering, and replay boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py
- [X] T016 [P] [US2] Add red integration tests for streamed `POST` responses, `GET` event streams, and reconnect with `Last-Event-ID` in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py
- [X] T017 [P] [US2] Add red unit tests for stream event buffering, replay cursors, and multi-stream isolation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py

### Implementation for User Story 2

- [X] T018 [US2] Implement stream channel state, event queueing, and replay cursors in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py
- [X] T019 [US2] Implement SSE response generation and stream termination behavior in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T020 [US2] Wire streamed MCP responses and server-driven event dispatch through /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py
- [X] T021 [US2] Refactor stream delivery helpers and re-run US2 suites in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py

**Checkpoint**: User Story 2 is independently functional when streamed responses and server-driven events flow over SSE with deterministic ordering and per-session isolation.

---

## Phase 5: User Story 3 - Verify Hosted Transport Compatibility Before Client Rollout (Priority: P2)

**Goal**: Provide local and hosted verification paths, scripts, and documentation that prove the streamable transport behaves the same way before rollout to external MCP consumers.

**Independent Test**: Run the documented local and hosted verification flow and confirm it exercises session establishment, JSON-vs-SSE negotiation, invalid header failures, and reconnect behavior using the same visible contract in both environments.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T022 [P] [US3] Add red integration tests for local and hosted streamable verification flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py
- [X] T023 [P] [US3] Add red contract tests for documented verification expectations in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py

### Implementation for User Story 3

- [X] T024 [US3] Update streamable hosted verification commands and assertions in /Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py and /Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh
- [X] T025 [US3] Document local and hosted streamable transport validation in /Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/quickstart.md and /Users/ctgunn/Projects/youtube-mcp-server/README.md
- [X] T026 [US3] Refactor verification guidance and re-run US3 suites in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py, /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py

**Checkpoint**: User Story 3 is independently functional when operators and integrators can verify streamable transport parity locally and on Cloud Run without reverse-engineering the implementation.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize cross-story regression, observability checks, and artifact updates.

- [X] T027 [P] Update hosted transport observability coverage for session and stream metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_request_observability.py and /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/observability.py
- [X] T028 Run full regression coverage across /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/, /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/, and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/
- [X] T029 [P] Record final streamable transport verification evidence in /Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/quickstart.md and /Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/checklists/requirements.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1; blocks all user story work.
- **User Story 1 (Phase 3)**: Depends on Phase 2; recommended MVP slice.
- **User Story 2 (Phase 4)**: Depends on Phase 3 because streamed delivery builds on established session and transport negotiation behavior.
- **User Story 3 (Phase 5)**: Depends on Phases 3 and 4 because verification guidance must reflect working session establishment and streaming behavior.
- **Polish (Phase 6)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1**: No dependency on other user stories after foundational work is done.
- **US2**: Depends on US1 because stream delivery and reconnect behavior require working session establishment and session-aware hosted routing.
- **US3**: Depends on US1 and US2 because verification guidance must cover the final transport surface, including streaming and reconnect behavior.

### Within Each User Story

- Red tests MUST be written and fail before implementation starts.
- Shared state/helpers come before hosted routing changes.
- Hosted routing changes come before documentation or verification automation updates.
- Refactor happens only after story tests are green, followed by rerunning affected suites.

### Suggested Execution Order

1. Complete Phase 1.
2. Complete Phase 2.
3. Complete Phase 3 (US1) as the MVP.
4. Complete Phase 4 (US2).
5. Complete Phase 5 (US3).
6. Finish Phase 6.

---

## Parallel Opportunities

- T002 and T003 can run in parallel after T001.
- T005 and T006 can run in parallel after T004.
- T008, T009, and T010 can run in parallel inside US1.
- T015, T016, and T017 can run in parallel inside US2.
- T022 and T023 can run in parallel inside US3.
- T027 and T029 can run in parallel during polish.

---

## Parallel Example: User Story 1

```bash
Task: "Add red contract tests for GET and POST negotiation, session header issuance, and invalid-session failures in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
Task: "Add red integration tests for hosted session establishment and invalid transport requests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
Task: "Add red unit tests for session registry transitions and transport header validation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add red contract tests for SSE response rules, event ordering, and replay boundaries in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
Task: "Add red integration tests for streamed POST responses, GET event streams, and reconnect with Last-Event-ID in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
Task: "Add red unit tests for stream event buffering, replay cursors, and multi-stream isolation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add red integration tests for local and hosted streamable verification flows in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
Task: "Add red contract tests for documented verification expectations in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_mcp_transport_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Finish Setup and Foundational phases.
2. Deliver User Story 1 so modern MCP clients can establish a hosted streamable session through the documented endpoint.
3. Validate US1 independently before expanding scope.

### Incremental Delivery

1. Add US1 to establish compliant hosted session negotiation.
2. Add US2 to deliver ordered streamed responses and reconnect-safe event handling.
3. Add US3 to prove local and hosted parity for rollout.
4. Finish with cross-story regression and verification evidence updates.

### Parallel Team Strategy

1. One engineer completes Setup and Foundational phases.
2. After Phase 2:
   - Engineer A can take US1.
   - Engineer B can prepare US1 red tests in parallel and then pivot to US2 once US1 transport negotiation is in place.
3. US3 begins after the transport surface stabilizes under US1 and US2.

---

## Notes

- Every task follows the required checklist format: checkbox, task ID, optional `[P]`, required `[US#]` in story phases, and exact file path.
- Tests are intentionally front-loaded in each story to enforce Red-Green-Refactor.
- User Story 1 is the suggested MVP scope.
