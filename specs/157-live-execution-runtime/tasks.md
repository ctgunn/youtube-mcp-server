# Tasks: YT-157 Layer 1 Live YouTube Data API Execution Runtime

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/data-model.md), and [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/contracts/)

**Tests**: Tests are mandatory. Write and run the Red tests before their corresponding Green tasks. All changed Python functions require reStructuredText docstrings. The feature is not complete until `python3 -m pytest` and `python3 -m ruff check .` pass.

**Scope boundary**: Establish one shared configured live-runtime path and prove one public-tool flow. Do not perform the family-wide default-executor replacements reserved for YT-158 through YT-160.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the implementation baseline and document the new optional OAuth runtime setting without adding a new dependency or project skeleton.

- [X] T001 Record the pre-change focused test baseline for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_runtime_config_validation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`.
- [X] T002 [P] Add a blank, secret-free `YOUTUBE_OAUTH_TOKEN` configuration placeholder and explanatory comment to `/Users/ctgunn/Projects/youtube-mcp-server/.env.example`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the shared runtime configuration and live-executor factory that all stories need. No user-story implementation starts until this phase is complete.

- [X] T003 Add failing runtime-settings tests for API-key presence, OAuth-token presence, blank-value rejection, secret-free validation details, and live-mode defaults in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_runtime_config_validation.py`.
- [X] T004 [P] Add failing factory tests that distinguish the concrete YouTube executor from a representative executor and verify the existing three-attempt/10-second defaults in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_live_runtime.py`.
- [X] T005 Implement a validated Layer 1 live-runtime settings value that loads `YOUTUBE_API_KEY` and optional `YOUTUBE_OAUTH_TOKEN` without echoing values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py`.
- [X] T006 Implement the shared configured runtime/dependency factory, reusing `build_youtube_data_api_executor`, `RetryPolicy`, and existing observability hooks in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`.
- [X] T007 Add or update reStructuredText docstrings for every new or changed configuration and runtime-factory function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`.
- [X] T008 Refactor the foundational configuration/factory code to keep credential lookup, mode selection, and safe validation centralized, then run `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_runtime_config_validation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_live_runtime.py`.

**Checkpoint**: The shared runtime can be built from safe configuration and cannot silently select a representative default.

---

## Phase 3: User Story 1 - Invoke Live YouTube Data (Priority: P1) 🎯 MVP

**Goal**: An operator-configured public tool uses the shared live runtime and a real configured credential instead of a placeholder credential or representative executor.

**Independent Test**: Build the normal configured app/transport/dispatcher path with a controlled opener, invoke one public API-key tool flow, and assert that its request reaches the concrete YouTube transport with the configured credential while preserving its normalized result shape.

- [X] T009 [P] [US1] Add a failing configured public-tool integration test with a controlled opener that fails if the normal construction path selects a representative executor or placeholder API key in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.
- [X] T010 [P] [US1] Add a failing contract regression test that the verified public tool retains its existing name, input schema, metadata, result shape, and safe categories after live-runtime injection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`.
- [X] T011 [US1] Thread the configured live-runtime dependency from application construction through the MCP HTTP transport and dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/app.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T012 [US1] Update the verified `activities_list` descriptor path to accept the injected configured executor and configured API-key availability rather than construct its local representative default in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`.
- [X] T013 [US1] Add or update reStructuredText docstrings for every changed application, transport, dispatcher, and activities construction function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/app.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`.
- [X] T014 [US1] Refactor the configured composition path to remove duplicate dependency wiring, run the US1 contract/integration tests, and confirm the controlled public-tool flow returns a normalized live-path result in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.

**Checkpoint**: User Story 1 is independently demonstrable through one configured public tool without an external network call or a production credential.

---

## Phase 4: User Story 2 - Receive Safe Failure Instead of Sample Data (Priority: P2)

**Goal**: Missing, unusable, or rejected live credentials and upstream failures yield safe normalized failures and never plausible sample data.

**Independent Test**: For API-key and OAuth-required selections, invoke the controlled configured path with an absent/invalid credential and with controlled upstream failures; assert no representative result or credential value appears in returned details or integration events.

- [X] T015 [P] [US2] Add failing tests for missing API-key, missing OAuth-token, blank credential, and conditional-mode credential selection failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_live_runtime.py`.
- [X] T016 [P] [US2] Add failing controlled-upstream tests for authorization rejection, timeout, retryable failure, malformed payload, and credential redaction in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.
- [X] T017 [US2] Map runtime configuration and selected-credential failures to the existing safe Layer 1/tool error flow without constructing a representative result in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`.
- [X] T018 [US2] Ensure runtime-created integration events and caller-safe error details redact credential-bearing request information while preserving existing event/error fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/observability.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`.
- [X] T019 [US2] Add or update reStructuredText docstrings for every modified safe-failure and observability function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/observability.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`.
- [X] T020 [US2] Refactor failure and redaction handling to retain one safe conversion path, then run the US2 unit/integration tests and verify no test fixture credential appears in results, errors, or captured events in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_live_runtime.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.

**Checkpoint**: User Story 2 is independently testable: every unavailable live-access condition fails safely and never produces a representative success.

---

## Phase 5: User Story 3 - Reuse Shared Execution Behavior (Priority: P3)

**Goal**: Maintainers connect wrappers to the reusable configured runtime while preserving request validation, request forms, retry/observability behavior, normalizers, and public contracts.

**Independent Test**: Use controlled openers with API-key and OAuth contexts to execute representative query, JSON-body, raw-media, and multipart requests through the shared runtime; assert wrapper validation, response normalization, retries, and event behavior remain intact with no endpoint-specific live transport.

- [X] T021 [P] [US3] Add failing characterization tests for wrapper validation-before-execution, API-key/OAuth request attachment, JSON/media/multipart construction, normalizer selection, and retry behavior through the runtime factory in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`.
- [X] T022 [P] [US3] Add failing integration tests that verify shared request/response/error hooks still emit safe endpoint/auth/outcome records when the configured executor is used in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`.
- [X] T023 [US3] Expose the configured runtime factory through the existing integration compatibility surface without duplicating request construction, retry, normalization, or error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`.
- [X] T024 [US3] Keep concrete request construction, response normalizers, retry selection, and wrapper delegation as the shared implementation path; make only the minimal compatibility updates in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/base.py` if characterization tests require them.
- [X] T025 [US3] Add or update reStructuredText docstrings for every changed Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/executor.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/base.py`.
- [X] T026 [US3] Refactor to remove any endpoint-specific credential, live-transport, retry, logging, or error-normalization code introduced during YT-157, then run the focused transport, foundation, and contract suites in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_resource_modules_contract.py`.

**Checkpoint**: All three user stories are independently functional, and the shared runtime remains the only configured live-execution implementation.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete operator documentation, hosted configuration alignment, verification, and final regression proof.

- [X] T027 [P] Document `YOUTUBE_OAUTH_TOKEN`, its secret-handling rules, and no-fallback behavior in `/Users/ctgunn/Projects/youtube-mcp-server/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/.env.local`.
- [X] T028 [P] Update hosted secret-reference documentation and configuration defaults for the optional OAuth token in `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/infrastructure/gcp/variables.tf`, and `/Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`.
- [X] T029 Validate every procedure and expected safe-failure result in `/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/quickstart.md` using controlled credentials and openers.
- [X] T030 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve every failing test before feature completion.
- [X] T031 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve every reported violation before feature completion.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Begins immediately. T002 can run in parallel with T001.
- **Phase 2 (Foundational)**: Depends on Phase 1. T003 and T004 are Red tests that can run in parallel; T005 through T008 are sequential because configuration must exist before the runtime factory can use it.
- **Phase 3 (US1, P1)**: Depends on Phase 2. Delivers the MVP configured public-tool proof path.
- **Phase 4 (US2, P2)**: Depends on Phase 2, not on US1. It can be developed in parallel with US1 when separate contributors avoid the shared runtime file; the recommended order is after US1 for lower integration risk.
- **Phase 5 (US3, P3)**: Depends on Phase 2, not on US1 or US2. It can begin in parallel with the other stories, but is recommended after US1 and US2 because it validates their shared runtime behavior.
- **Phase 6 (Polish)**: Depends on all selected user-story phases. T027 and T028 can run in parallel; T029 through T031 are sequential final verification.

### User Story Dependency Graph

```text
Setup
  └─> Foundational runtime configuration and factory
       ├─> US1: configured live public-tool flow (MVP)
       ├─> US2: safe no-fallback failures
       └─> US3: shared execution reuse
            
US1 + US2 + US3
  └─> Polish and full-suite verification
```

### Parallel Opportunities

- **Foundational**: T003 and T004 touch different test files and can be written in parallel.
- **US2**: T015 and T016 are independent Red test files and can be written in parallel.
- **US3**: T021 and T022 are independent Red test files and can be written in parallel.
- **Polish**: T027 and T028 update different operator documentation/deployment surfaces and can be completed in parallel.
- **Stories**: After T008, US1, US2, and US3 are independently testable. Coordinate changes to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py` if teams work concurrently.

## Parallel Execution Examples

### User Story 1

```text
Task: "Add the configured public-tool Red integration test in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py"
Task: "Add the public-contract Red regression test in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

### User Story 2

```text
Task: "Add credential-availability Red tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_live_runtime.py"
Task: "Add controlled upstream-failure and redaction Red tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py"
```

### User Story 3

```text
Task: "Add shared transport-form Red tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "Add safe observability-hook Red tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 through T008 to establish tested runtime configuration and the shared live-executor factory.
2. Complete T009 through T014 to prove one configured public tool reaches the concrete live transport with a controlled opener.
3. Run the US1 independent test. If it selects a representative executor, placeholder credential, or external network call, stop and correct the composition path before advancing.

### Incremental Delivery

1. **Foundation**: Safe runtime configuration, credential selection, and a live executor factory.
2. **US1**: One configured public-tool live path—the MVP.
3. **US2**: Safe configuration/upstream failure behavior and redaction proof.
4. **US3**: Regression proof that the shared request/normalization/observability paths remain reusable.
5. **Polish**: Operator and hosted documentation, quickstart validation, full test suite, and lint.

### Format Validation

- Every task begins with `- [ ]`, has a sequential T001–T031 identifier, includes `[P]` only when it is independently parallelizable, and has a `[US#]` label only in a user-story phase.
- Every task description contains one or more absolute repository paths.
- User-story phases each contain explicit Red tests, Green implementation, Python docstring work, and Refactor/verification work.
