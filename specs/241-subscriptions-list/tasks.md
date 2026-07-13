# Tasks: Layer 2 Tool `subscriptions_list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/data-model.md), [contracts/subscriptions_list.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/contracts/subscriptions_list.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/quickstart.md)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after final code changes. Python code tasks include explicit reStructuredText docstring work before story completion.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the feature's empty implementation and test surfaces without adding user-facing behavior.

- [X] T001 [P] Create the new Layer 2 subscriptions module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T002 [P] Create the subscriptions contract test module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T003 [P] Create the subscriptions unit test module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T004 [P] Create the subscriptions registration test module with a module docstring in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Confirm shared resource-family placement, public exports, and default catalog expectations before story work begins.

**Critical**: No user story implementation should begin until this phase is complete.

- [X] T005 [P] Add a failing scaffold test for `get_resource_family("subscriptions")` placement paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T006 [P] Add a failing shared contract test proving `mcp_server.tools.youtube_common.subscriptions` is importable as the subscriptions family module in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T007 [P] Add a failing shared package export test for `SUBSCRIPTIONS_LIST_TOOL_NAME` and `build_subscriptions_list_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add a failing default catalog test proving `subscriptions_list` is expected as a concrete endpoint-backed tool in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T009 Implement the minimal subscriptions family import scaffold and public placeholders needed for T005 through T008 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T010 Export the minimal subscriptions placeholders from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T011 Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and confirm only intended subscriptions behavior remains red in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: Foundation ready; user story implementation can now begin.

---

## Phase 3: User Story 1 - List Channel Subscriptions (Priority: P1) MVP

**Goal**: An MCP client can call `subscriptions_list` with valid `part` plus a supported public or OAuth-backed selector and receive a near-raw subscription list result with endpoint, quota, selector, access, pagination, and item context.

**Independent Test**: Invoke `subscriptions_list` through its descriptor or dispatcher with channel-scoped, identifier-based, current-user, recent-subscriber, subscriber-list, paginated, and empty-result requests and confirm successful list results preserve context without adding out-of-scope enrichment.

### Tests for User Story 1 (Red)

- [X] T012 [P] [US1] Add failing contract tests for `SUBSCRIPTIONS_LIST_TOOL_NAME`, quota cost `1`, conditional auth mode, input schema, `build_subscriptions_list_contract()`, and list response convention in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T013 [P] [US1] Add failing unit tests for `validate_subscriptions_list_arguments()` accepting valid `channelId`, `id`, `mine`, `myRecentSubscribers`, `mySubscribers`, paginated, ordered, and empty-result-compatible requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T014 [US1] Add failing unit tests for `map_subscriptions_list_result()` preserving endpoint, quota, items, empty marker, selector context, access context, and pagination tokens in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T015 [US1] Add failing unit tests proving `build_subscriptions_list_handler()` selects public access for `channelId` and `id`, OAuth access for user-context selectors, calls `build_subscriptions_list_wrapper()` once, and never leaks credentials in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T016 [P] [US1] Add failing integration tests proving `build_subscriptions_list_tool_descriptor()` registers and executes through `InMemoryToolDispatcher` for valid public and OAuth-backed subscription list requests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T017 [P] [US1] Add failing default registry tests proving `subscriptions_list` appears in `InMemoryToolDispatcher().list_tools()` and can be called for a valid channel-scoped request in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 1 (Green)

- [X] T018 [US1] Define `SUBSCRIPTIONS_LIST_*` constants, supported parts, selectors, order values, maximum result limit, unsafe detail keys, and input schema in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T019 [US1] Implement `SubscriptionsListToolError`, subscription error sanitization, and shared safe details for subscription list failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T020 [US1] Implement `build_subscriptions_list_contract()` with `subscriptions.list` identity, conditional auth mode, quota cost `1`, list response convention, and near-raw response boundary in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T021 [US1] Implement `validate_subscriptions_list_arguments()` for required non-empty `part`, supported parts, exactly-one selector, boolean selector truthiness, selector shapes, page token shape, maxResults bounds, and order values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T022 [US1] Implement conditional access-context selection for `subscriptions_list` with public `channelId` and `id` paths plus OAuth-backed `mine`, `myRecentSubscribers`, and `mySubscribers` paths in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T023 [US1] Implement `map_subscriptions_list_result()` to preserve endpoint, quota, items, empty marker, selector context, access context, pageInfo, nextPageToken, and prevPageToken without fabricated channel or subscriber enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T024 [US1] Implement `_default_subscriptions_list_executor()` returning deterministic representative populated and empty subscription list data in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T025 [US1] Implement `build_subscriptions_list_handler()` using `build_subscriptions_list_wrapper()` and one Layer 1 wrapper call per valid request in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T026 [US1] Implement `build_subscriptions_list_tool_descriptor()` with callable handler, input schema, and metadata wiring in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T027 [US1] Export `SUBSCRIPTIONS_LIST_*`, `SubscriptionsListToolError`, `build_subscriptions_list_contract()`, `build_subscriptions_list_handler()`, `build_subscriptions_list_tool_descriptor()`, `map_subscriptions_list_result()`, and `validate_subscriptions_list_arguments()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T028 [US1] Register `build_subscriptions_list_tool_descriptor()` in the default dispatcher tool list in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T029 [US1] Add reStructuredText docstrings for every new or modified production and fake test helper function touched by US1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`

### Refactor and Validation for User Story 1

- [X] T030 [US1] Refactor US1 implementation for naming, helper reuse, narrow endpoint scope, selector clarity, and no-enrichment result boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T031 [US1] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US1 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Cost, Filters, and Auth Before Calling (Priority: P2)

**Goal**: A client developer can inspect `subscriptions_list` discovery metadata, descriptions, usage notes, caveats, and examples and understand quota, conditional auth, required inputs, selectors, pagination, ordering, private subscriber limitations, empty-result behavior, safe failures, and out-of-scope workflows before invocation.

**Independent Test**: Review `subscriptions_list` metadata and examples from its descriptor and catalog entries, then confirm mapped endpoint, quota cost, auth paths, required `part`, selector compatibility, paging and ordering rules, no-enrichment boundary, safe failures, and out-of-scope workflows are visible without reading implementation-only artifacts.

### Tests for User Story 2 (Red)

- [X] T032 [P] [US2] Add failing metadata tests for description, usage notes, caveats, examples, quota cost `1`, conditional auth disclosure, required `part`, supported selectors, pagination, ordering, empty-result behavior, private subscriber caveats, no-enrichment boundary, and out-of-scope workflows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T033 [US2] Add failing example coverage tests for channel subscription listing, direct subscription lookup, current-user subscriptions, recent subscribers, subscriber list, paginated listing, successful empty result, missing selector, conflicting selectors, access failure, quota or upstream failure, and unsupported enrichment request in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T034 [P] [US2] Add failing shared catalog tests proving `subscriptions_list` uses concrete contract metadata and no duplicate representative placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [P] [US2] Add failing common contract tests for `subscriptions_list` public exports, examples, and catalog participation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`

### Implementation for User Story 2 (Green)

- [X] T036 [US2] Add `SUBSCRIPTIONS_LIST_DESCRIPTION`, `SUBSCRIPTIONS_LIST_USAGE_NOTES`, `SUBSCRIPTIONS_LIST_CAVEATS`, and `SUBSCRIPTIONS_LIST_CALLER_EXAMPLES` covering all quickstart examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T037 [US2] Wire subscriptions examples, usage notes, caveats, auth mode, availability state, response convention, response boundary, and private subscriber caveats into `build_subscriptions_list_contract()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T038 [US2] Replace or supersede any representative `_contract` for `subscriptions.list` with `build_subscriptions_list_contract()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T039 [US2] Ensure `subscriptions_list` metadata and examples are exposed consistently through public package exports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T040 [US2] Add reStructuredText docstrings for every new or modified metadata/catalog helper function touched by US2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`

### Refactor and Validation for User Story 2

- [X] T041 [US2] Refactor metadata text to remove duplicated shared wording while preserving quota, conditional auth, required inputs, selector compatibility, pagination, ordering, empty-result, no-enrichment, private subscriber, and unsupported-input guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T042 [US2] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US2 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: User Stories 1 and 2 both work independently.

---

## Phase 5: User Story 3 - Reject Ambiguous or Invalid Selector Combinations (Priority: P3)

**Goal**: Callers receive clear validation, access, and upstream failure feedback for missing or invalid `part`, missing selectors, selector conflicts, false-only boolean selectors, invalid pagination, unsupported order, missing user-context authorization, quota failures, not-found outcomes, unavailable service, and out-of-scope requests.

**Independent Test**: Submit representative invalid and ineligible `subscriptions_list` requests through validator, handler, descriptor, and dispatcher paths, then confirm each failure uses safe categories and sanitized details while successful populated and empty subscription results remain distinct.

### Tests for User Story 3 (Red)

- [X] T043 [P] [US3] Add failing unit validation tests for missing `part`, invalid `part`, missing selector, conflicting selectors, blank `channelId`, blank `id`, false-only boolean selectors, unsupported fields, invalid `pageToken`, out-of-range `maxResults`, unsupported `order`, and partner-only delegation fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T044 [US3] Add failing unit tests for paging and order compatibility with direct `id` lookup, user-context selectors without OAuth, public selectors with OAuth-only auth path, unsupported enrichment fields, mutation fields, and successful empty result classification in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T045 [US3] Add failing unit tests for missing credentials, invalid credentials, quota failure, account closed, account suspended, subscription forbidden, subscriber not found, endpoint unavailable, deprecated behavior, unexpected upstream failure, and sanitized unsafe upstream details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T046 [P] [US3] Add failing integration tests for invalid dispatcher requests, user-context access failures, safe upstream failures, empty successful results, and populated subscription results staying distinct from failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T047 [P] [US3] Add failing contract tests proving failure examples cover missing part, invalid part, missing selector, conflicting selector, false-only selector, invalid pagination, unsupported order, access failure, quota or upstream failure, not-found failure, and out-of-scope enrichment request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`

### Implementation for User Story 3 (Green)

- [X] T048 [US3] Expand `validate_subscriptions_list_arguments()` to reject all US3 malformed inputs with safe field and selector details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T049 [US3] Implement selector-aware pagination and ordering validation for collection selectors and direct identifier lookup boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T050 [US3] Implement safe public and OAuth-backed authentication and authorization failure handling for subscription list requests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T051 [US3] Implement upstream error mapping for quota, invalid request, account closed, account suspended, subscription forbidden, subscriber not found, endpoint unavailable, deprecated behavior, unexpected upstream failure, and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T052 [US3] Ensure descriptor and dispatcher handlers surface `SubscriptionsListToolError` without leaking API keys, OAuth tokens, authorization headers, stack traces, raw upstream bodies, or unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T053 [US3] Preserve successful empty subscription collections as `empty: true` results distinct from validation, access, quota, not-found, and upstream failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T054 [US3] Add or update failure examples and contract metadata for all safe subscription list error categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T055 [US3] Add reStructuredText docstrings for every new or modified validation, access, result, and error-mapping function touched by US3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`

### Refactor and Validation for User Story 3

- [X] T056 [US3] Refactor safe error helpers and invalid-request branches while preserving clear field-level feedback in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T057 [US3] Run `pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix US3 failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final cleanup, verification, documentation, and full-suite confidence.

- [X] T058 [P] Review the implemented contract against `/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/contracts/subscriptions_list.md` and update mismatches in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T059 [P] Review quickstart examples against `/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/quickstart.md` and update mismatches in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T060 [P] Review every new or modified Python function for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T061 Run focused quickstart verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/quickstart.md` and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T062 Run `pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any repository test failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T063 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any code-quality failures before completion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T064 Record final focused, full-suite, lint, and docstring evidence for YT-241 in `/Users/ctgunn/Projects/youtube-mcp-server/specs/241-subscriptions-list/tasks.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; T001-T004 can start immediately.
- **Phase 2 Foundational**: Depends on setup files from Phase 1; blocks user story work.
- **Phase 3 US1**: Depends on Phase 2; delivers the MVP executable subscriptions list tool.
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
Task: "T012 [P] [US1] Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
Task: "T013 [P] [US1] Add failing unit validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py"
Task: "T016 [P] [US1] Add failing integration descriptor tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py"
Task: "T017 [P] [US1] Add failing default registry tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

### User Story 2

```text
Task: "T032 [P] [US2] Add failing metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
Task: "T034 [P] [US2] Add failing catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "T035 [P] [US2] Add failing common contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

### User Story 3

```text
Task: "T043 [P] [US3] Add failing validation tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py"
Task: "T046 [P] [US3] Add failing dispatcher invalid-request tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py"
Task: "T047 [P] [US3] Add failing failure-example contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup tasks T001-T004.
2. Complete Phase 2 foundational tasks T005-T011.
3. Complete Phase 3 US1 tasks T012-T031.
4. Validate `subscriptions_list` independently with descriptor and dispatcher calls for valid public and OAuth-backed list paths.
5. Stop for MVP review before metadata enrichment and invalid-request hardening if incremental delivery is desired.

### Incremental Delivery

1. Setup and foundation establish the subscriptions family surface.
2. US1 adds executable subscription listing and default registration.
3. US2 makes the tool self-explanatory through discovery, examples, catalog metadata, conditional auth guidance, selector compatibility, pagination, ordering, empty-result behavior, and caveats.
4. US3 hardens invalid input, access failures, upstream failures, empty-result distinction, and safe sanitization.
5. Polish runs focused quickstart checks, full `pytest`, and `ruff check .`.

### Parallel Team Strategy

1. One person can create setup files while another adds scaffold/export/catalog tests.
2. After Phase 2, separate contributors can write US1, US2, and US3 Red tests in parallel.
3. Coordinate implementation edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py` because most Green tasks converge there.
4. Keep final validation serialized so full-suite and lint evidence reflect the final combined state.

---

## Task Summary

- **Total tasks**: 64
- **Setup tasks**: 4
- **Foundational tasks**: 7
- **US1 tasks**: 20
- **US2 tasks**: 11
- **US3 tasks**: 15
- **Polish tasks**: 7
- **Parallel opportunities identified**: 21 tasks marked `[P]`, plus cross-story Red tests can be drafted in parallel after Phase 2
- **Suggested MVP scope**: Complete through US1, tasks T001-T031

## Final Verification Evidence

- Matched seed slice: `YT-241`
- Focused quickstart verification: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` -> 251 passed
- Full repository verification: `PYTHONPATH=src python3 -m pytest` -> 3218 passed
- Lint verification: `python3 -m ruff check .` -> All checks passed
- Python docstring audit for new or modified Python functions -> `missing_count 0`
