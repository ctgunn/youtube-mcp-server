# Tasks: Layer 4 Remote MCP Read-Only Live Smoke

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/data-model.md), [remote MCP live-smoke contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/contracts/remote-mcp-live-smoke-contract.md), and [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/quickstart.md)

**Tests**: Tests are mandatory. Write each Red task first and verify it fails before its Green task. Completion requires focused remote, catalog, and configured-runtime verification; a passing `make test`; and a final passing `make quality`. The authorized remote smoke command is manual evidence only and must never run in ordinary automation.

**Organization**: Tasks are grouped by user story. The dedicated remote client is the only allowed runtime boundary: it must make real HTTP requests to a controlled loopback responder in tests and an operator-supplied running endpoint manually. It must not call `create_app`, an in-process transport, or a dispatcher.

## Phase 1: Setup (Shared Verification Workspace)

**Purpose**: Establish isolated test locations and review the only allowed reusable local-smoke facts before changing behavior.

- [X] T001 [P] Create the deterministic loopback remote-MCP responder and request-capture scaffold in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py` without using an in-process application or dispatcher.
- [X] T002 [P] Create public transport contract-test scaffolding for initialize, discovery, invocation, session, and streamed responses in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_remote_mcp_live_smoke_contract.py`.
- [X] T003 Document the canonical reviewed 12-entry allowlist, public fixture dependency, fixed limits, and no-duplication rule as imports/expectations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`, referencing `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py` as the source of truth.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish fail-closed preflight, safe evidence primitives, and the test-only remote boundary required by every user story.

**⚠️ CRITICAL**: Complete this phase before implementation of any user story.

- [X] T004 Add failing preflight and redaction tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py` for absent `RUN_REMOTE_MCP_LIVE_SMOKE`, absent `REMOTE_MCP_URL`, endpoint-required missing authentication, and reports/CLI output that must omit tokens, headers, session IDs, arguments, raw URLs, raw bodies, and exception text.
- [X] T005 Implement fixed safe error/report primitives, environment preflight, request-count constants, and injected requester boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py` so T004 fails closed before any network request.
- [X] T006 Add or update complete reStructuredText docstrings for every new or modified Python function and test helper in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`.
- [X] T007 Refactor the shared preflight, sanitization, and controlled-responder helpers in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py` while keeping T004 green.

**Checkpoint**: A missing prerequisite makes zero remote requests and every shared report surface is safe to use in story-level tests.

---

## Phase 3: User Story 1 - Run a Remote Read-Only Smoke (Priority: P1) 🎯 MVP

**Goal**: An approved operator can initialize an actual remote MCP session, discover its catalog, and receive an individually classified live result for each approved discovered read-only tool.

**Independent Test**: Run `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py` against its controlled loopback HTTP responder and verify `initialize` → session-bearing `tools/list` → selected `tools/call` ordering, bearer forwarding when supplied, protocol/session retention, JSON and streamed result handling, and one outcome per selected tool.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T008 [P] [US1] Add failing public-MCP contract tests for JSON-RPC initialize/client information, `MCP-Session-Id` and protocol-version continuation, `tools/list`, `tools/call`, and direct-JSON versus streamed call envelopes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_remote_mcp_live_smoke_contract.py`.
- [X] T009 [P] [US1] Add failing loopback integration tests for ordered remote HTTP requests, conditional bearer authorization on every request, selected allowlist calls only, bounded comment-parent derivation, and per-tool success/safe-availability/failure outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`.

### Implementation for User Story 1

- [X] T010 [US1] Implement remote JSON-RPC request creation, initialize/session/protocol retention, discovery parsing, and direct JSON plus event-stream response normalization in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py` so T008 and T009 can use only the public remote transport.
- [X] T011 [US1] Implement discovery-derived selection from the canonical local allowlist, reviewed object arguments, bounded in-memory comment-parent fixture derivation, per-tool result classification, and discovered `metadata.upstream.operationKey` endpoint agreement in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py`.
- [X] T012 [US1] Add or update complete reStructuredText docstrings for every Python function changed by the remote request, session, streamed-response, selection, fixture, and outcome work in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_remote_mcp_live_smoke_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`.
- [X] T013 [US1] Refactor duplicate request IDs, session/header handling, streamed-event parsing, and endpoint/outcome assertions in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`, then run the User Story 1 independent test.

**Checkpoint**: The remote smoke flow is independently demonstrable against a true loopback HTTP endpoint; it does not instantiate local application code.

---

## Phase 4: User Story 2 - Prevent Unsafe Live Calls (Priority: P1)

**Goal**: Security reviewers can prove that the remote workflow cannot select unreviewed/sensitive operations and cannot leak credentials or raw transport data while handling failures.

**Independent Test**: Supply an allowlisted catalog plus mutation-capable, OAuth/owner-sensitive, unknown, malformed, timeout, and secret-bearing responder cases to `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`; assert only approved entries are called and all evidence remains redacted.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T014 [P] [US2] Add failing contract tests for explicit allowlist authority, intentional exclusions, finite 12-tool/14-POST bounds, 30-second request timeout, conditional endpoint-identity mismatch, and fixed safe outcome categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_remote_mcp_live_smoke_contract.py`.
- [X] T015 [P] [US2] Add failing loopback integration tests for rejected initialization, missing/expired session, empty or drifting catalogs, unavailable fixture source, unapproved mutation/sensitive tools, HTTP/timeout failures, malformed stream data, bound-reached results, and deliberate secret-bearing error/header/body values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`.

### Implementation for User Story 2

- [X] T016 [US2] Implement strict active-allowlist validation, selected-versus-excluded reporting, fixture-source safety, endpoint mismatch handling, and 12-tool/14-POST/30-second bound enforcement in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py`.
- [X] T017 [US2] Implement fixed safe classification for authorization, session, HTTP, timeout, malformed protocol, availability, and bound-reached outcomes plus final CLI serialization that discards exception text, headers, session IDs, inputs, URLs, and raw bodies in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py`.
- [X] T018 [US2] Add or update complete reStructuredText docstrings for every Python function changed by safety validation, limits, redaction, error classification, and CLI reporting in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_remote_mcp_live_smoke_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`.
- [X] T019 [US2] Refactor the safety/error paths in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py` so one sanitizer/classifier governs all report surfaces, then run the User Story 2 independent test.

**Checkpoint**: The remote client calls no unapproved tool, terminates within documented bounds, and exposes no secret-bearing transport fact in any result or console line.

---

## Phase 5: User Story 3 - Interpret and Reproduce Verification Evidence (Priority: P2)

**Goal**: Maintainers can run the remote smoke deliberately, interpret its bounded safe report, and distinguish it from deterministic catalog, configured-runtime, and local live verification.

**Independent Test**: Run the documentation/gate regression tests and inspect the manual target to confirm it requires opt-in endpoint settings, stays absent from ordinary quality/CI/deployment paths, and README accurately explains all four workflows.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T020 [US3] Add failing documentation and automation-boundary regression assertions for the remote manual command, opt-in/environment prerequisites, redaction guidance, four-workflow distinction, and absence from normal quality/CI/deployment execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`.

### Implementation for User Story 3

- [X] T021 [P] [US3] Add a `test-remote-live-smoke` manual target that sources ignored local environment files and invokes only `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_remote_mcp_live_smoke.py` in `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, without adding it to `test`, `quality`, CI, or deployment targets.
- [X] T022 [P] [US3] Document remote endpoint/authentication prerequisites, approved deployment/quota boundary, safe evidence, failure recovery, and the distinction among all four verification workflows in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`.
- [X] T023 [US3] Add or update complete reStructuredText docstrings for every Python test function changed by the documentation and automation assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`.
- [X] T024 [US3] Refactor command/documentation assertions and operator wording in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`, `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, and `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, then run the User Story 3 independent test.

**Checkpoint**: The operator-facing command is reproducible but never automatic, and all published workflow boundaries remain clear and credential-safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile design/implementation evidence, run required regression gates, and correct every failure before completion.

- [X] T025 [P] Reconcile the implemented environment names, bounds, outcome vocabulary, and redaction rules with `/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/contracts/remote-mcp-live-smoke-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/405-remote-live-smoke/quickstart.md`.
- [X] T026 [P] Run the deterministic remote smoke suite at `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py`, catalog suite at `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, and configured-runtime suite at `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`; fix failures in their owning files.
- [X] T027 Run the full repository test suite through `/Users/ctgunn/Projects/youtube-mcp-server/Makefile` with `make test` and resolve every failing test in its owning file before completion.
- [X] T028 Run the constitutional completion gate through `/Users/ctgunn/Projects/youtube-mcp-server/Makefile` with `make quality` and resolve every lint, type-check, and test failure in its owning file before completion.

---

## Dependencies & Execution Order

### Dependency Graph

```text
Phase 1 Setup (T001-T003)
        │
        ▼
Phase 2 Foundation (T004-T007)
        │
        ├──► US1: Remote read-only flow (T008-T013) ──► US2: Safety controls (T014-T019)
        │                                                    │
        └────────────────────────────────────────────────────┘
                                                             ▼
                                      US3: Command and evidence (T020-T024)
                                                             │
                                                             ▼
                                    Polish and completion gates (T025-T028)
```

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; T001 and T002 can run in parallel because they create different test modules.
- **Foundation (Phase 2)**: Depends on Setup and blocks all story Green work. It establishes fail-closed preflight and a safe test boundary.
- **US1 (Phase 3)**: Depends on Foundation. It is the MVP and supplies the remote client flow that US2 hardens.
- **US2 (Phase 4)**: Its Red tasks can be prepared after Foundation, but its Green tasks depend on the US1 remote client so safety is added to the real transport path rather than a duplicate implementation.
- **US3 (Phase 5)**: Depends on the finalized US1/US2 command behavior; its Makefile and README updates can proceed in parallel after T020 establishes their failing regression checks.
- **Polish (Phase 6)**: Depends on all three stories being complete.

### User Story Completion Order

1. **US1 (P1)** — deliver the true remote public-transport smoke flow and validate it against a loopback endpoint. This is the MVP.
2. **US2 (P1)** — enforce the allowlist, bounds, redaction, and failure safety on that live flow.
3. **US3 (P2)** — expose the safe manual command and documentation once its semantics are fixed.

### Parallel Opportunities

- T001 and T002 are parallel test-module setup work.
- T008 and T009 are parallel Red tests for the contract and loopback integration boundary.
- T014 and T015 are parallel Red tests for safety contract and integration behavior.
- T021 and T022 are parallel after T020 because `Makefile` and `README.md` are independent files.
- T025 and T026 can run in parallel after all story code is merged; T027 and T028 must run sequentially after fixes from earlier checks.

## Parallel Execution Examples

### User Story 1

```text
Task: "T008 [US1] Add public-MCP contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_remote_mcp_live_smoke_contract.py"
Task: "T009 [US1] Add loopback transport integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py"
```

### User Story 2

```text
Task: "T014 [US2] Add allowlist/bounds/redaction contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_remote_mcp_live_smoke_contract.py"
Task: "T015 [US2] Add timeout/session/secret-leak integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_remote_mcp_live_smoke.py"
```

### User Story 3

```text
Task: "T021 [US3] Add manual remote-smoke target in /Users/ctgunn/Projects/youtube-mcp-server/Makefile"
Task: "T022 [US3] Add four-workflow operator guidance in /Users/ctgunn/Projects/youtube-mcp-server/README.md"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundation so preflight and report safety are testable.
2. Complete US1 through T013 to prove a remote-only, session-aware loopback smoke flow.
3. Run the US1 independent test before adding policy hardening or operator docs.
4. Demonstrate only controlled loopback evidence at this stage; do not run a real endpoint yet.

### Incremental Delivery

1. Setup + Foundation establishes safe remote verification primitives.
2. US1 adds remote discovery/invocation evidence.
3. US2 adds strict safety, redaction, and bounded-operation enforcement.
4. US3 makes the final behavior usable and understandable by operators without changing normal automation.
5. Polish runs required regressions and completion gates; real remote smoke remains an approved manual post-deployment activity.

## Notes

- All 28 tasks use the required `- [ ] T### [P?] [US?] Description with absolute file path` checklist format.
- Story tasks include their required `[US1]`, `[US2]`, or `[US3]` labels; Setup, Foundation, and Polish tasks intentionally have no story label.
- Every Python-changing phase contains an explicit reStructuredText docstring task before its Refactor task.
- No task authorizes real remote smoke execution as ordinary test evidence, CI, or a deployment gate.
