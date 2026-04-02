# Tasks: Hosted MCP Session Durability

**Input**: Design documents from `/specs/015-hosted-session-durability/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the repository for durable hosted session work and capture the new runtime dependency.

- [X] T001 Add the durable session store dependency and any optional extra needed for hosted runtime installation in ~/Projects/youtube-mcp-server/pyproject.toml
- [X] T002 [P] Document the new durable-session runtime environment variables in ~/Projects/youtube-mcp-server/README.md
- [X] T003 [P] Add durable-session configuration examples and deployment notes in ~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the shared session durability primitives that block all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create the hosted durable-session configuration model and validation rules in ~/Projects/youtube-mcp-server/src/mcp_server/config.py
- [X] T005 [P] Create the durable session store abstraction and shared-state record helpers in ~/Projects/youtube-mcp-server/src/mcp_server/transport/session_store.py
- [X] T006 [P] Refactor stream/session state management behind a store-aware session manager in ~/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py
- [X] T007 Wire the durable session manager into transport creation and hosted request handling in ~/Projects/youtube-mcp-server/src/mcp_server/app.py
- [X] T008 Wire the durable session manager into hosted request execution and initialization flows in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T009 Add foundational unit coverage for durable-session config parsing and store abstraction behavior in ~/Projects/youtube-mcp-server/tests/unit/test_durable_session_config.py
- [X] T010 [P] Add foundational unit coverage for store-aware session lifecycle primitives in ~/Projects/youtube-mcp-server/tests/unit/test_durable_session_store.py

**Checkpoint**: Foundation ready; user story work can begin in priority order or in parallel where dependencies allow.

---

## Phase 3: User Story 1 - Continue an Active Hosted Session (Priority: P1) 🎯 MVP

**Goal**: Let an MCP consumer initialize once and continue valid hosted sessions across Cloud Run instance routing without process-local `session not found` failures.

**Independent Test**: Initialize a session on one app instance, continue it with follow-up `POST /mcp` and `GET /mcp` requests on a second app instance sharing the durable backend, and confirm protocol-correct success plus stable invalid-session failures.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T011 [P] [US1] Add contract coverage for durable initialize and follow-up continuation in ~/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py
- [X] T012 [P] [US1] Add integration coverage for cross-instance hosted session continuation in ~/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py
- [X] T013 [P] [US1] Add invalid-session regression coverage for hosted follow-up requests in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py

### Implementation for User Story 1

- [X] T014 [US1] Implement durable session create, lookup, touch, and invalid-session mapping in ~/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py
- [X] T015 [US1] Update hosted session initialization and follow-up `POST` behavior to use durable state in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T016 [US1] Update hosted `GET /mcp` continuation behavior to load session state from the shared backend in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T017 [US1] Add session-state observability fields for successful continuation and invalid-session rejection in ~/Projects/youtube-mcp-server/src/mcp_server/observability.py
- [X] T018 [US1] Refactor US1 session continuation code paths and rerun the affected unit, contract, and integration suites in ~/Projects/youtube-mcp-server/tests

**Checkpoint**: User Story 1 should now be independently functional and usable as the MVP increment.

---

## Phase 4: User Story 2 - Operate Within a Documented Deployment Topology (Priority: P2)

**Goal**: Let operators identify whether a deployment can safely advertise durable hosted sessions and block readiness when required shared state is unavailable.

**Independent Test**: Start the service with and without durable-session backend settings, verify `/ready` and deployment verification reflect the supported topology correctly, and confirm operators receive a clear not-ready signal when durability guarantees cannot be met.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T019 [P] [US2] Add contract coverage for durable-session readiness and unsupported-topology signaling in ~/Projects/youtube-mcp-server/tests/contract/test_readiness_contract.py
- [X] T020 [P] [US2] Add integration coverage for runtime readiness under durable-session configuration failures in ~/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py
- [X] T021 [P] [US2] Add deployment verification coverage for durable-session topology evidence in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py

### Implementation for User Story 2

- [X] T022 [US2] Implement durable-session topology validation and readiness inputs in ~/Projects/youtube-mcp-server/src/mcp_server/config.py
- [X] T023 [US2] Update readiness payload generation to surface durable-session availability and operator-safe failure reasons in ~/Projects/youtube-mcp-server/src/mcp_server/health.py
- [X] T024 [US2] Update deployment verification checks and evidence output for durable-session topology validation in ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T025 [US2] Update the hosted verifier to exercise durable-session readiness and topology checks in ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py
- [X] T026 [US2] Refactor US2 readiness and deployment-signal paths and rerun the affected readiness, deployment, and security suites in ~/Projects/youtube-mcp-server/tests

**Checkpoint**: User Stories 1 and 2 should both work independently, with operators able to verify supported deployment topology.

---

## Phase 5: User Story 3 - Reconnect and Verify Session Durability (Priority: P3)

**Goal**: Let integrators reconnect durable hosted sessions, replay recent events within the retained window, and detect replay-unavailable or expired sessions through stable session-state outcomes.

**Independent Test**: Initialize a hosted session, produce replayable events, reconnect with a valid `Last-Event-ID` on another instance, verify replay succeeds within the retained window, and confirm replay-unavailable or expired-session behavior is reported distinctly.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T027 [P] [US3] Add contract coverage for reconnect replay and replay-unavailable failures in ~/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py
- [X] T028 [P] [US3] Add integration coverage for recent-event replay across app instances in ~/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py
- [X] T029 [P] [US3] Add hosted verification coverage for reconnect and replay-window failures in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py

### Implementation for User Story 3

- [X] T030 [US3] Implement replay-window persistence, cursor lookup, and replay-unavailable failure mapping in ~/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py
- [X] T031 [US3] Update hosted `GET /mcp` replay handling and reconnect error behavior in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T032 [US3] Extend hosted verification and evidence recording for reconnect and replay-window outcomes in ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T033 [US3] Update the durable-session contract and operator quickstart with reconnect and replay-window rules in ~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/contracts/hosted-session-durability-contract.md
- [X] T034 [US3] Refactor US3 reconnect and replay logic and rerun the affected unit, contract, integration, and hosted verification suites in ~/Projects/youtube-mcp-server/tests

**Checkpoint**: All user stories should now be independently functional, including reconnect and replay behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, docs, and regression work across all stories

- [X] T035 [P] Add cross-story unit regression coverage for durable session observability and expiry edge cases in ~/Projects/youtube-mcp-server/tests/unit/test_streamable_http_transport.py
- [X] T036 [P] Update repository-level deployment and runtime guidance for durable hosted sessions in ~/Projects/youtube-mcp-server/README.md
- [X] T037 Run the full regression suite and capture final durable-session verification evidence in ~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; MVP slice.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can proceed after US1 if the same files are in flight.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and benefits from US1 session persistence being in place.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; no dependency on later stories.
- **User Story 2 (P2)**: Starts after Phase 2; independently testable, but shares config and verification files with US1.
- **User Story 3 (P3)**: Starts after US1 durable-session persistence exists; independently testable once replay support is implemented.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Shared primitives from earlier phases land before story-specific request-path changes.
- Implementation tasks deliver the minimum behavior needed for passing tests.
- Refactor tasks run only after story tests pass and must keep the affected suites green.

### Parallel Opportunities

- **Setup**: `T002` and `T003` can run in parallel after `T001`.
- **Foundational**: `T005` and `T006` can run in parallel after `T004`; `T009` and `T010` can run in parallel once the core design settles.
- **US1**: `T011`, `T012`, and `T013` can run in parallel.
- **US2**: `T019`, `T020`, and `T021` can run in parallel.
- **US3**: `T027`, `T028`, and `T029` can run in parallel.
- **Polish**: `T035` and `T036` can run in parallel before `T037`.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "Add contract coverage for durable initialize and follow-up continuation in ~/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
Task: "Add integration coverage for cross-instance hosted session continuation in ~/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
Task: "Add invalid-session regression coverage for hosted follow-up requests in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "Add contract coverage for durable-session readiness and unsupported-topology signaling in ~/Projects/youtube-mcp-server/tests/contract/test_readiness_contract.py"
Task: "Add integration coverage for runtime readiness under durable-session configuration failures in ~/Projects/youtube-mcp-server/tests/integration/test_readiness_flow.py"
Task: "Add deployment verification coverage for durable-session topology evidence in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "Add contract coverage for reconnect replay and replay-unavailable failures in ~/Projects/youtube-mcp-server/tests/contract/test_streamable_http_contract.py"
Task: "Add integration coverage for recent-event replay across app instances in ~/Projects/youtube-mcp-server/tests/integration/test_streamable_http_transport.py"
Task: "Add hosted verification coverage for reconnect and replay-window failures in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate the independent US1 continuation test across two app instances.

### Incremental Delivery

1. Finish Setup and Foundational work to establish the durable session layer.
2. Deliver US1 for cross-instance session continuation.
3. Deliver US2 for operator-visible readiness and supported topology enforcement.
4. Deliver US3 for reconnect and replay-window handling.
5. Finish Polish for full regression coverage and final documentation.

### Parallel Team Strategy

1. One developer handles shared session persistence primitives while another prepares config and docs during Setup and Foundational phases.
2. After Phase 2, one developer can own US1 request-path changes while another prepares US2 readiness and verification work.
3. US3 reconnect work starts once US1 persistence primitives are merged, with hosted verification updates progressing in parallel.

---

## Notes

- All tasks use the required checklist format with task ID, optional `[P]`, optional `[US#]`, and an exact file path.
- The MVP scope is Phase 3 only: durable cross-instance session continuation for User Story 1.
- User stories remain independently testable through the criteria defined at each phase header.
