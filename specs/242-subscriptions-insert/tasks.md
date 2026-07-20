# Tasks: Layer 2 Tool `subscriptions_insert`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/data-model.md), [contracts/subscriptions_insert.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/contracts/subscriptions_insert.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after final code changes. Python code tasks include explicit reStructuredText docstring work before story completion.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature scope and current implementation surfaces before adding tests or code.

- [X] T001 [P] Review the final YT-242 implementation scope, dependencies, and verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/plan.md`
- [X] T002 [P] Review the public `subscriptions_insert` contract, input schema, result contract, and error categories in `/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/contracts/subscriptions_insert.md`
- [X] T003 [P] Review the existing Layer 1 `subscriptions.insert` wrapper, validators, and normalizers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared public symbol, family, catalog, and registry expectations that all user stories build on.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T004 [P] Add failing shared package export tests for `SUBSCRIPTIONS_INSERT_TOOL_NAME`, `SUBSCRIPTIONS_INSERT_QUOTA_COST`, and `build_subscriptions_insert_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T005 [P] Add failing subscriptions family contract tests proving `mcp_server.tools.youtube_common.subscriptions` exposes `subscriptions_insert` alongside `subscriptions_list` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T006 [P] Add failing default catalog tests proving `subscriptions_insert` is expected as a concrete endpoint-backed tool in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T007 Implement minimal `subscriptions_insert` public constants and placeholder export wiring required by foundational import tests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T008 Export minimal `subscriptions_insert` placeholders from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T009 Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm only intended missing `subscriptions_insert` behavior remains red in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: Foundation ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - Create a Channel Subscription Through a Public Tool (Priority: P1) MVP

**Goal**: An MCP client can call `subscriptions_insert` with valid OAuth-backed creation input and receive a near-raw created subscription result with endpoint, quota, request, access, and target-channel context.

**Independent Test**: Invoke `subscriptions_insert` through its descriptor or dispatcher with `part=snippet` and `body.snippet.resourceId.channelId`, then confirm the Layer 1 wrapper is called once with OAuth access and the result preserves created subscription fields without adding out-of-scope enrichment.

### Tests for User Story 1 (Red)

- [X] T010 [P] [US1] Add failing contract tests for `SUBSCRIPTIONS_INSERT_TOOL_NAME`, quota cost `50`, OAuth-required auth mode, input schema, `build_subscriptions_insert_contract()`, and mutation response convention in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T011 [P] [US1] Add failing unit tests for `validate_subscriptions_insert_arguments()` accepting valid target-channel requests with and without explicit `youtube#channel` resource kind in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T012 [US1] Add failing unit tests for `map_subscriptions_insert_result()` preserving endpoint, quota, requested parts, created marker, auth context, target channel context, target resource kind, and returned subscription fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T013 [US1] Add failing unit tests proving `build_subscriptions_insert_handler()` requires OAuth access, calls `build_subscriptions_insert_wrapper()` once, and never leaks credentials in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T014 [P] [US1] Add failing integration tests proving `build_subscriptions_insert_tool_descriptor()` registers and executes through `InMemoryToolDispatcher` for valid subscription creation requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T015 [P] [US1] Add failing default registry tests proving `subscriptions_insert` appears in `InMemoryToolDispatcher().list_tools()` and can be called for a representative creation request in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 1 (Green)

- [X] T016 [US1] Define `SUBSCRIPTIONS_INSERT_*` constants, supported parts, unsafe detail keys, and input schema in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T017 [US1] Implement `SubscriptionsInsertToolError`, subscription insert error sanitization, and shared safe details for creation failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T018 [US1] Implement `validate_subscriptions_insert_arguments()` for required `part=snippet`, required `body.snippet.resourceId.channelId`, optional `resourceId.kind=youtube#channel`, and normalized create arguments in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T019 [US1] Implement OAuth-required access-context selection for `subscriptions_insert` using safe credential handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T020 [US1] Implement `map_subscriptions_insert_result()` to preserve endpoint, quota, requested parts, created marker, auth context, target channel context, target resource kind, and returned subscription resource without fabricated enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T021 [US1] Implement `_default_subscriptions_insert_executor()` returning deterministic representative created subscription data in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T022 [US1] Implement `build_subscriptions_insert_handler()` using `build_subscriptions_insert_wrapper()` and one Layer 1 wrapper call per valid request in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T023 [US1] Implement `build_subscriptions_insert_contract()` and `build_subscriptions_insert_tool_descriptor()` with callable handler, input schema, quota, OAuth, mutation result, and metadata wiring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T024 [US1] Export `SUBSCRIPTIONS_INSERT_*`, `SubscriptionsInsertToolError`, `build_subscriptions_insert_contract()`, `build_subscriptions_insert_handler()`, `build_subscriptions_insert_tool_descriptor()`, `map_subscriptions_insert_result()`, and `validate_subscriptions_insert_arguments()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T025 [US1] Register `build_subscriptions_insert_tool_descriptor()` in the default dispatcher tool list near `subscriptions_list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T026 [US1] Add reStructuredText docstrings for every new or modified production and fake test helper function touched by US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`

### Refactor and Validation for User Story 1

- [X] T027 [US1] Refactor US1 implementation for naming, helper reuse, narrow endpoint scope, target-channel clarity, OAuth safety, and no-enrichment result boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T028 [US1] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US1 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Create Semantics, Cost, and OAuth Before Calling (Priority: P2)

**Goal**: A client developer can inspect `subscriptions_insert` discovery metadata, descriptions, usage notes, caveats, and examples and understand quota, OAuth, required create inputs, mutation behavior, duplicate/ineligible target caveats, safe failures, and out-of-scope workflows before invocation.

**Independent Test**: Review `subscriptions_insert` metadata and examples from its descriptor and catalog entries, then confirm mapped endpoint, quota cost, OAuth requirement, required `part=snippet`, required target channel path, explicit resource-kind boundary, created-resource result shape, safe failures, and out-of-scope workflows are visible without reading implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T029 [P] [US2] Add failing metadata tests for description, usage notes, caveats, examples, quota cost `50`, OAuth-required access, required `part=snippet`, required target channel path, mutation warning, duplicate/ineligible target caveats, and out-of-scope workflows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T030 [US2] Add failing example coverage tests for successful subscription creation, explicit `youtube#channel` kind, missing part, invalid part, missing target channel, invalid resource kind, unsupported write field, missing authorization, duplicate or ineligible target, quota or upstream failure, and out-of-scope request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T031 [P] [US2] Add failing shared catalog tests proving `subscriptions_insert` uses concrete contract metadata and no duplicate representative placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T032 [P] [US2] Add failing common contract tests for `subscriptions_insert` public exports, examples, and catalog participation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`

### Implementation for User Story 2 (Green)

- [X] T033 [US2] Add `SUBSCRIPTIONS_INSERT_DESCRIPTION`, `SUBSCRIPTIONS_INSERT_USAGE_NOTES`, `SUBSCRIPTIONS_INSERT_CAVEATS`, and `SUBSCRIPTIONS_INSERT_CALLER_EXAMPLES` covering all quickstart examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T034 [US2] Wire subscriptions insert examples, usage notes, caveats, auth mode, availability state, response convention, response boundary, duplicate/ineligible target caveats, and mutation warning into `build_subscriptions_insert_contract()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T035 [US2] Replace or supersede any representative catalog contract for `subscriptions.insert` with `build_subscriptions_insert_contract()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T036 [US2] Ensure `subscriptions_insert` metadata and examples are exposed consistently through public package exports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T037 [US2] Add reStructuredText docstrings for every new or modified metadata, descriptor, catalog, and fake test helper function touched by US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`

### Refactor and Validation for User Story 2

- [X] T038 [US2] Refactor metadata text to remove duplicated shared wording while preserving quota, OAuth, required create inputs, target channel path, resource-kind boundary, mutation warning, duplicate/ineligible caveats, safe failures, and unsupported-input guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T039 [US2] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US2 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reject Invalid, Duplicate, or Under-Authorized Create Requests Clearly (Priority: P3)

**Goal**: Callers receive clear validation, access, and upstream failure feedback for malformed create inputs, missing OAuth, duplicate or ineligible targets, quota failures, authorization failures, unavailable service, deprecated endpoint behavior, unexpected upstream failures, and out-of-scope workflow requests.

**Independent Test**: Submit representative invalid and ineligible `subscriptions_insert` requests through validator, handler, descriptor, and dispatcher paths, then confirm each failure uses safe categories and sanitized details while successful created subscription results remain distinct.

### Tests for User Story 3 (Red)

- [X] T040 [P] [US3] Add failing unit validation tests for missing `part`, unsupported `part`, missing `body`, non-object `body`, missing `body.snippet`, missing `body.snippet.resourceId`, missing or blank `body.snippet.resourceId.channelId`, invalid `body.snippet.resourceId.kind`, unsupported body fields, unsupported snippet fields, and unsupported resource-id fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T041 [US3] Add failing unit tests for unsupported modifiers, subscription listing fields, subscription deletion fields, channel search fields, notification fields, analytics fields, and higher-level workflow inputs in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T042 [US3] Add failing unit tests for missing OAuth, invalid OAuth, quota failure, duplicate target, self-subscription or ineligible target, authorization failure, target not found, endpoint unavailable, deprecated behavior, unexpected upstream failure, and sanitized unsafe upstream details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T043 [P] [US3] Add failing integration tests for invalid dispatcher requests, missing authorization failures, duplicate or ineligible target failures, safe upstream failures, and created subscription results staying distinct from failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T044 [P] [US3] Add failing contract tests proving failure examples cover missing part, invalid part, missing target channel, invalid resource kind, unsupported write field, missing authorization, duplicate or ineligible target, quota or upstream failure, and out-of-scope request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`

### Implementation for User Story 3 (Green)

- [X] T045 [US3] Expand `validate_subscriptions_insert_arguments()` to reject all US3 malformed inputs with safe field and writable body details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T046 [US3] Implement unsupported modifier and out-of-scope workflow rejection for subscription listing, deletion, channel search, notification, analytics, ranking, summarization, enrichment, idempotency, and duplicate-prevention request fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T047 [US3] Implement safe OAuth-required authentication and authorization failure handling for subscription insert requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T048 [US3] Implement upstream error mapping for quota, invalid request, duplicate target, self-subscription or ineligible target, authorization failure, not found, endpoint unavailable, deprecated behavior, unexpected upstream failure, and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T049 [US3] Ensure descriptor and dispatcher handlers surface `SubscriptionsInsertToolError` without leaking API keys, OAuth tokens, authorization headers, stack traces, raw upstream bodies, unsafe request context, or secret-bearing diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T050 [US3] Preserve successful created subscription results as `created: true` outcomes distinct from validation, access, duplicate target, ineligible target, quota, not-found, and upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T051 [US3] Add or update failure examples and contract metadata for all safe subscription insert error categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T052 [US3] Add reStructuredText docstrings for every new or modified validation, access, result, error-mapping, descriptor, and fake test helper function touched by US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`

### Refactor and Validation for User Story 3

- [X] T053 [US3] Refactor safe error helpers and invalid-request branches while preserving clear field-level feedback in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T054 [US3] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US3 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, verification, documentation, and full-suite confidence.

- [X] T055 [P] Review the implemented contract against `/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/contracts/subscriptions_insert.md` and update mismatches in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T056 [P] Review quickstart examples against `/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/quickstart.md` and update mismatches in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T057 [P] Review every new or modified Python function for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T058 Run focused quickstart verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/quickstart.md` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T059 Run `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any repository test failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T060 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any code-quality failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T061 Record final focused, full-suite, lint, and docstring evidence for YT-242 in `/Users/ctgunn/Projects/youtube-mcp-server/specs/242-subscriptions-insert/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; T001-T003 can start immediately.
- **Phase 2 Foundational**: Depends on setup review; blocks user story work.
- **Phase 3 US1**: Depends on Phase 2; delivers the MVP executable subscriptions insert tool.
- **Phase 4 US2**: Depends on Phase 2 and can run after or alongside US1 if descriptor/contract ownership is coordinated, but final metadata validation expects US1 contract builders to exist.
- **Phase 5 US3**: Depends on Phase 2 and can run after or alongside US1 if validator/error-helper ownership is coordinated, but final invalid-request validation expects US1 handler scaffolding to exist.
- **Phase 6 Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Start after Phase 2; no dependency on US2 or US3; recommended MVP scope.
- **US2 (P2)**: Start after Phase 2; depends on the same public contract surface as US1 but remains independently testable through metadata and catalog assertions.
- **US3 (P3)**: Start after Phase 2; depends on the same validator/handler surface as US1 but remains independently testable through invalid input and safe error assertions.

### Within Each User Story

- Red tests must be written and observed failing before Green implementation tasks begin.
- Contract, unit, and integration tests marked `[P]` can be written in parallel because they target different files or independent sections.
- Implementation tasks that touch `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py` should be sequenced to avoid conflicting edits.
- Docstring tasks must complete before the story checkpoint is considered done.
- Refactor tasks must preserve focused test success before moving to the next story or final polish.

---

## Parallel Execution Examples

### User Story 1

```text
Task: "T010 [P] [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
Task: "T011 [P] [US1] Add failing unit validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py"
Task: "T014 [P] [US1] Add failing integration descriptor tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py"
Task: "T015 [P] [US1] Add failing default registry tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 2

```text
Task: "T029 [P] [US2] Add failing metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
Task: "T031 [P] [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T032 [P] [US2] Add failing common contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

### User Story 3

```text
Task: "T040 [P] [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py"
Task: "T043 [P] [US3] Add failing dispatcher invalid-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py"
Task: "T044 [P] [US3] Add failing failure-example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup tasks T001-T003.
2. Complete Phase 2 foundational tasks T004-T009.
3. Complete Phase 3 US1 tasks T010-T028.
4. Validate `subscriptions_insert` independently with descriptor and dispatcher calls for valid OAuth-backed create paths.
5. Stop for MVP review before metadata enrichment and invalid-request hardening if incremental delivery is desired.

### Incremental Delivery

1. Setup and foundation establish the subscriptions insert public surface.
2. US1 adds executable subscription creation and default registration.
3. US2 makes the tool self-explanatory through discovery, examples, catalog metadata, OAuth guidance, target-channel body guidance, mutation warning, duplicate/ineligible caveats, and out-of-scope boundaries.
4. US3 hardens invalid input, access failures, upstream failures, created-result distinction, and safe sanitization.
5. Polish runs focused quickstart checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One person can review setup documents while another adds scaffold/export/catalog tests.
2. After Phase 2, separate contributors can write US1, US2, and US3 Red tests in parallel.
3. Coordinate implementation edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py` because most Green tasks converge there.
4. Keep final validation serialized so full-suite and lint evidence reflect the final combined state.

---

## Task Summary

- **Total tasks**: 61
- **Setup tasks**: 3
- **Foundational tasks**: 6
- **US1 tasks**: 19
- **US2 tasks**: 11
- **US3 tasks**: 15
- **Polish tasks**: 7
- **Parallel opportunities identified**: 19 tasks marked `[P]`, plus cross-story Red tests can be drafted in parallel after Phase 2
- **Suggested MVP scope**: Complete through US1, tasks T001-T028

## Final Verification Evidence

- Matched seed slice: `YT-242`
- Required focused verification: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`
- Required full repository verification: `PYTHONPATH=src python3 -m pytest`
- Required lint verification: `python3 -m ruff check .`
- Required Python docstring audit: confirm every new or modified Python function uses reStructuredText docstrings before completion
- Focused verification result: `303 passed in 0.95s`
- Full repository verification result: `3270 passed in 14.44s`
- Lint verification result: `All checks passed!`
- Python docstring audit result: `All audited Python functions have docstrings.`
- Whitespace verification result: `git diff --check` completed with no findings
