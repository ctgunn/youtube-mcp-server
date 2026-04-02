# Tasks: Browser-Originated MCP Access + CORS Support

**Input**: Design documents from `/specs/016-browser-mcp-cors/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are REQUIRED. Every user story and foundational change must include Red-Green-Refactor coverage tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare repository documentation and execution guidance for browser-originated hosted MCP work.

- [X] T001 Add browser-originated configuration and validation guidance to ~/Projects/youtube-mcp-server/README.md
- [X] T002 [P] Align manual browser verification steps and expected outcomes in ~/Projects/youtube-mcp-server/specs/016-browser-mcp-cors/quickstart.md
- [X] T003 [P] Align browser access contract notes and supported route scope in ~/Projects/youtube-mcp-server/specs/016-browser-mcp-cors/contracts/hosted-browser-mcp-contract.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared browser-access policy primitives that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Add foundational Red coverage for browser origin policy evaluation in ~/Projects/youtube-mcp-server/tests/unit/test_hosted_security_policy.py
- [X] T005 [P] Add foundational Red coverage for browser preflight classification and header-policy rules in ~/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py
- [X] T006 Implement browser-aware hosted route classification and shared response metadata constants in ~/Projects/youtube-mcp-server/src/mcp_server/transport/http.py
- [X] T007 [P] Implement browser origin policy parsing, requested-header evaluation, and response-header helpers in ~/Projects/youtube-mcp-server/src/mcp_server/security.py
- [X] T008 Wire browser access configuration into hosted runtime settings in ~/Projects/youtube-mcp-server/src/mcp_server/config.py
- [X] T009 Refactor shared browser policy primitives and rerun the foundational unit suites in ~/Projects/youtube-mcp-server/tests

**Checkpoint**: Foundation ready; user story work can begin in priority order or in parallel where dependencies allow.

---

## Phase 3: User Story 1 - Complete Allowed Browser Requests (Priority: P1) 🎯 MVP

**Goal**: Let approved browser-originated MCP clients complete preflight and authenticated hosted requests with the documented cross-origin response headers.

**Independent Test**: Send browser-style preflight and follow-up hosted MCP requests from `http://localhost:3000`, confirm preflight succeeds, confirm the hosted response includes the documented browser headers, and confirm authentication/session behavior still works.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Add contract coverage for approved-origin preflight and approved-origin hosted responses in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py
- [X] T011 [P] [US1] Add integration coverage for approved browser initialize and follow-up hosted requests in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_mcp_security_flows.py
- [X] T012 [P] [US1] Add hosted-route integration coverage for successful browser preflight handling in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py

### Implementation for User Story 1

- [X] T013 [US1] Implement explicit approved-origin `OPTIONS` preflight handling in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T014 [US1] Apply approved browser response headers to hosted MCP success responses in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T015 [US1] Expose browser-readable session and stream response headers for approved hosted flows in ~/Projects/youtube-mcp-server/src/mcp_server/security.py
- [X] T016 [US1] Refactor approved browser response shaping and rerun the affected contract and integration suites in ~/Projects/youtube-mcp-server/tests

**Checkpoint**: User Story 1 should now be independently functional and usable as the MVP increment.

---

## Phase 4: User Story 2 - Deny Unsupported Browser Access Predictably (Priority: P2)

**Goal**: Let operators and clients distinguish denied origins and unsupported browser request patterns through stable hosted behavior.

**Independent Test**: Send browser-style preflight and actual requests from `https://evil.example`, plus unsupported route, method, and requested-header combinations, and confirm the service returns the documented denial behavior without appearing to grant browser access.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T017 [P] [US2] Add contract coverage for denied origins and unsupported browser request patterns in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py
- [X] T018 [P] [US2] Add integration coverage for denied-origin and unsupported browser flows in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_mcp_security_flows.py
- [X] T019 [P] [US2] Add unit regression coverage for malformed origin and unsupported browser decision mapping in ~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_security_gate.py

### Implementation for User Story 2

- [X] T020 [US2] Implement stable denial categories for disallowed origins and malformed browser security input in ~/Projects/youtube-mcp-server/src/mcp_server/security.py
- [X] T021 [US2] Implement unsupported browser route, method, and requested-header handling in ~/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py
- [X] T022 [US2] Add browser denial observability fields and logging for hosted requests in ~/Projects/youtube-mcp-server/src/mcp_server/observability.py
- [X] T023 [US2] Refactor denial-path handling and rerun the affected unit, contract, and integration suites in ~/Projects/youtube-mcp-server/tests

**Checkpoint**: User Stories 1 and 2 should both work independently, with stable allow and deny behavior for browser-originated hosted access.

---

## Phase 5: User Story 3 - Verify Browser Access Before Release (Priority: P3)

**Goal**: Let operators and maintainers verify approved and denied browser behavior through automated hosted verification and documented release evidence.

**Independent Test**: Run the hosted verification flow with approved-origin, denied-origin, and unsupported browser request inputs; confirm the verification output records the expected outcomes and the documented release workflow remains accurate.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T024 [P] [US3] Add contract coverage for browser verification evidence and response-header expectations in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py
- [X] T025 [P] [US3] Add integration coverage for browser verification outcomes in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py
- [X] T026 [P] [US3] Add documentation-example coverage for browser verification commands in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py

### Implementation for User Story 3

- [X] T027 [US3] Extend hosted verification checks and evidence serialization for approved and denied browser scenarios in ~/Projects/youtube-mcp-server/src/mcp_server/deploy.py
- [X] T028 [US3] Update the hosted verification runner to exercise browser preflight and denial scenarios in ~/Projects/youtube-mcp-server/scripts/verify_cloud_run_foundation.py
- [X] T029 [US3] Update browser release validation steps and expected evidence in ~/Projects/youtube-mcp-server/specs/016-browser-mcp-cors/quickstart.md
- [X] T030 [US3] Refactor browser verification helpers and rerun the affected contract and integration suites in ~/Projects/youtube-mcp-server/tests

**Checkpoint**: All user stories should now be independently functional, including release verification for browser-originated access.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final regression, documentation consistency, and cross-story cleanup

- [X] T031 [P] Add cross-story regression coverage for originless clients and browser-compatible session headers in ~/Projects/youtube-mcp-server/tests/unit/test_hosted_http_semantics.py
- [X] T032 [P] Update repository-level browser access, auth, and verification guidance in ~/Projects/youtube-mcp-server/README.md
- [X] T033 Run the full regression suite and record final browser-access validation notes in ~/Projects/youtube-mcp-server/specs/016-browser-mcp-cors/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion; MVP slice.
- **User Story 2 (Phase 4)**: Depends on Foundational completion and can proceed after US1 if the same files are not concurrently in flight.
- **User Story 3 (Phase 5)**: Depends on Foundational completion and benefits from US1 and US2 behavior being available for verification.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; no dependency on later stories.
- **User Story 2 (P2)**: Starts after Phase 2; independently testable, but shares hosted entrypoint and security files with US1.
- **User Story 3 (P3)**: Starts after US1 and US2 browser behavior exists; independently testable once verification coverage is implemented.

### Within Each User Story

- Tests MUST be written and fail before implementation.
- Shared primitives from earlier phases land before story-specific request-path changes.
- Implementation tasks deliver the minimum behavior needed for passing tests.
- Refactor tasks run only after story tests pass and must keep the affected suites green.

### Parallel Opportunities

- **Setup**: `T002` and `T003` can run in parallel after `T001`.
- **Foundational**: `T004` and `T005` can run in parallel; `T007` and `T008` can run in parallel after `T006` begins to define the shared contract.
- **US1**: `T010`, `T011`, and `T012` can run in parallel.
- **US2**: `T017`, `T018`, and `T019` can run in parallel.
- **US3**: `T024`, `T025`, and `T026` can run in parallel.
- **Polish**: `T031` and `T032` can run in parallel before `T033`.

---

## Parallel Example: User Story 1

```bash
# Launch all US1 Red tests together:
Task: "Add contract coverage for approved-origin preflight and approved-origin hosted responses in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py"
Task: "Add integration coverage for approved browser initialize and follow-up hosted requests in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_mcp_security_flows.py"
Task: "Add hosted-route integration coverage for successful browser preflight handling in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_http_routes.py"
```

## Parallel Example: User Story 2

```bash
# Launch all US2 Red tests together:
Task: "Add contract coverage for denied origins and unsupported browser request patterns in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py"
Task: "Add integration coverage for denied-origin and unsupported browser flows in ~/Projects/youtube-mcp-server/tests/integration/test_hosted_mcp_security_flows.py"
Task: "Add unit regression coverage for malformed origin and unsupported browser decision mapping in ~/Projects/youtube-mcp-server/tests/unit/test_cloud_run_security_gate.py"
```

## Parallel Example: User Story 3

```bash
# Launch all US3 Red tests together:
Task: "Add contract coverage for browser verification evidence and response-header expectations in ~/Projects/youtube-mcp-server/tests/contract/test_hosted_mcp_security_contract.py"
Task: "Add integration coverage for browser verification outcomes in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_verification_flow.py"
Task: "Add documentation-example coverage for browser verification commands in ~/Projects/youtube-mcp-server/tests/integration/test_cloud_run_docs_examples.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Stop and validate the independent approved-browser preflight and hosted-request flow.

### Incremental Delivery

1. Finish Setup and Foundational work to establish shared browser policy primitives.
2. Deliver US1 for approved browser preflight and hosted-response support.
3. Deliver US2 for stable browser denial behavior and observability.
4. Deliver US3 for release verification and operator evidence.
5. Finish Polish for full regression coverage and final documentation.

### Parallel Team Strategy

1. One developer handles shared transport and security helpers while another updates setup documentation in Phase 1.
2. After Phase 2, one developer can own approved-browser request behavior while another prepares denial-path tests for US2.
3. Verification and documentation work for US3 can start once approved and denied browser behaviors are merged.

---

## Notes

- All tasks use the required checklist format with task ID, optional `[P]`, optional `[US#]`, and an exact file path.
- The MVP scope is Phase 3 only: approved browser-originated preflight and hosted MCP request handling for User Story 1.
- User stories remain independently testable through the criteria defined at each phase header.
