# Tasks: Layer 2 Tool `subscriptions_delete`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/data-model.md), [contracts/subscriptions_delete.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/contracts/subscriptions_delete.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/quickstart.md)

**Tests**: Tests are mandatory. Each user story begins with failing tests, then minimal implementation, then refactor/docstring validation. Completion requires focused tests, full `pytest`, and `ruff check .` after final code changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm local context and identify the exact surfaces that YT-243 will touch.

- [X] T001 Confirm branch `243-subscriptions-delete` and review feature docs in `/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/plan.md`
- [X] T002 Review existing Layer 2 subscriptions patterns for list and insert in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T003 Review existing Layer 1 delete dependency `build_subscriptions_delete_wrapper()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/subscriptions.py`
- [X] T004 Review current subscriptions tests to extend in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T005 Review current subscriptions unit tests to extend in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T006 Review current subscriptions registration tests to extend in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the shared export, catalog, and registration expectations that every user story depends on.

**CRITICAL**: No user story implementation should begin until these tests have been added and observed failing for the missing `subscriptions_delete` surface.

- [X] T007 [P] Add failing public export checks for `SUBSCRIPTIONS_DELETE_TOOL_NAME` and `build_subscriptions_delete_tool_descriptor` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T008 [P] Add failing catalog checks that `subscriptions_delete` appears once with resource family `subscriptions` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T009 [P] Add failing default registration checks that `subscriptions_delete` is discoverable through the tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T010 [P] Add failing subscriptions-family registration checks for `subscriptions_delete` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T011 Run focused foundational tests and confirm they fail for missing delete symbols from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation tests are red and ready for story implementation.

---

## Phase 3: User Story 1 - Delete a Subscription Through a Public Tool (Priority: P1) MVP

**Goal**: A caller can invoke `subscriptions_delete` with a valid subscription relationship `id` and OAuth-backed access, and receive a safe deletion acknowledgment with endpoint, quota, request, and auth context.

**Independent Test**: Invoke the tool handler with `{"id": "subscription-123"}` and an OAuth token using a fake Layer 1 wrapper; verify one wrapper call and a result containing `endpoint: subscriptions.delete`, `quotaCost: 50`, `deleted: true`, `deletion.id`, and `auth.mode: oauth_required`.

### Tests for User Story 1 (REQUIRED)

> Write these tests first and confirm they fail before implementation.

- [X] T012 [P] [US1] Add contract tests for `subscriptions_delete` input schema, upstream identity, quota cost, OAuth mode, response convention, and executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T013 [P] [US1] Add unit tests for successful `validate_subscriptions_delete_arguments`, `map_subscriptions_delete_result`, and `build_subscriptions_delete_handler` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T014 [P] [US1] Add integration tests proving `subscriptions_delete` is registered and callable through the subscriptions family registry in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py`
- [X] T015 [US1] Run US1 focused tests and confirm they fail for missing `subscriptions_delete` implementation from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 1

- [X] T016 [US1] Import `build_subscriptions_delete_wrapper` and define `SUBSCRIPTIONS_DELETE_TOOL_NAME`, `SUBSCRIPTIONS_DELETE_QUOTA_COST`, unsafe-detail keys, and `SUBSCRIPTIONS_DELETE_INPUT_SCHEMA` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T017 [US1] Implement `SubscriptionsDeleteToolError` and shared safe detail sanitization support for delete errors in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T018 [US1] Implement `validate_subscriptions_delete_arguments` requiring one non-empty `id` and rejecting additional fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T019 [US1] Implement `map_subscriptions_delete_result` to return endpoint, quota cost 50, `deleted: true`, safe deletion id context, OAuth auth context, and safe upstream acknowledgment fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T020 [US1] Implement OAuth-required auth context and `build_subscriptions_delete_handler` using the Layer 1 delete wrapper once per valid call in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T021 [US1] Implement `build_subscriptions_delete_contract` and `build_subscriptions_delete_tool_descriptor` with acknowledgment-style response metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T022 [US1] Export `subscriptions_delete` constants and builders from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T023 [US1] Register `build_subscriptions_delete_tool_descriptor()` in the default tool registry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T024 [US1] Add or update reStructuredText docstrings for all new or modified US1 Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T025 [US1] Add or update reStructuredText docstrings for all new or modified US1 fake wrapper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T026 [US1] Run US1 focused contract, unit, and integration tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T027 [US1] Refactor US1 delete execution code for consistency with list and insert helpers while keeping focused tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: User Story 1 is independently functional and testable as the MVP.

---

## Phase 4: User Story 2 - Understand Delete Semantics, Cost, and OAuth Before Calling (Priority: P2)

**Goal**: A client developer can inspect `subscriptions_delete` metadata, descriptions, usage notes, caveats, and examples before invocation and understand deletion semantics, quota cost `50`, required `id`, OAuth requirement, acknowledgment result shape, and out-of-scope behavior.

**Independent Test**: Inspect the tool descriptor and verify metadata text and examples include `subscriptions.delete`, quota cost `50`, OAuth-required access, required `id`, deletion acknowledgment behavior, target-state caveats, and no listing/creation/enrichment behavior.

### Tests for User Story 2 (REQUIRED)

> Write these tests first and confirm they fail before implementation.

- [X] T028 [P] [US2] Add contract tests for delete metadata text, usage notes, caveats, quota visibility, OAuth visibility, availability state, response boundary, and examples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T029 [P] [US2] Add catalog contract tests confirming `subscriptions_delete` metadata exposes quota cost 50 and OAuth-required auth before invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T030 [P] [US2] Add common contract tests confirming shared YouTube metadata exports include `subscriptions_delete` without replacing list or insert entries in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T031 [US2] Run US2 focused metadata tests and confirm they fail for incomplete description/example coverage from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 2

- [X] T032 [US2] Add `SUBSCRIPTIONS_DELETE_DESCRIPTION`, `SUBSCRIPTIONS_DELETE_USAGE_NOTES`, and `SUBSCRIPTIONS_DELETE_CAVEATS` with quota cost 50, OAuth-required access, required id, deletion warning, target-state caveats, and out-of-scope boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T033 [US2] Add `SUBSCRIPTIONS_DELETE_CALLER_EXAMPLES` covering successful deletion, missing id, empty id, access failure, already-removed or missing target, non-removable target, quota/upstream failure, and out-of-scope request rejection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T034 [US2] Update `build_subscriptions_delete_contract` and `build_subscriptions_delete_tool_descriptor` to include delete metadata, examples, caveats, response boundary, availability state, and quota/auth details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T035 [US2] Update shared examples or catalog entries if required so `subscriptions_delete` replaces any representative placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T036 [US2] Add or update reStructuredText docstrings for all new or modified US2 Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T037 [US2] Run US2 focused metadata, catalog, and common contract tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T038 [US2] Refactor US2 metadata and example wording for consistency with `subscriptions_insert` without removing endpoint-specific delete caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: User Story 2 is independently testable through discovery metadata and caller-facing examples.

---

## Phase 5: User Story 3 - Reject Invalid, Missing, or Under-Authorized Delete Requests Clearly (Priority: P3)

**Goal**: Callers receive clear, sanitized validation, access, target-state, quota, availability, deprecation, and unexpected-upstream failures that remain distinct from successful deletion acknowledgments.

**Independent Test**: Submit missing, empty, non-string, extra-field, channel-id, body-shape, missing-OAuth, missing target, non-removable target, quota, unavailable, deprecated, and unexpected upstream cases; verify each returns the expected safe category and sanitized details.

### Tests for User Story 3 (REQUIRED)

> Write these tests first and confirm they fail before implementation.

- [X] T039 [P] [US3] Add unit validation tests for missing `id`, empty `id`, non-string `id`, unsupported top-level fields, channel-id lookup attempts, body/create-shape attempts, notification modifiers, analytics modifiers, ranking modifiers, summarization modifiers, and enrichment modifiers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T040 [US3] Add unit handler tests for missing OAuth, invalid OAuth mode, wrapper call prevention on access failure, and safe auth error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T041 [US3] Add unit upstream error mapping tests for already-removed or missing target, not-owned target, blocked or non-removable target, quota failure, invalid request, authorization failure, endpoint unavailable, deprecated endpoint, unexpected upstream failure, and secret sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T042 [P] [US3] Add contract tests proving failure examples cover invalid request, access failure, target-state failure, quota/upstream failure, and out-of-scope workflow rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py`
- [X] T043 [US3] Run US3 focused validation and error tests and confirm they fail for incomplete failure handling from `/Users/ctgunn/Projects/youtube-mcp-server`

### Implementation for User Story 3

- [X] T044 [US3] Extend `validate_subscriptions_delete_arguments` to return field-specific `invalid_request` errors for missing, empty, non-string, and unsupported fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T045 [US3] Extend `validate_subscriptions_delete_arguments` to reject out-of-scope fields such as `channelId`, `body`, `deleteExistingSubscription`, `includeChannelStatistics`, `notificationSettings`, `includeAnalytics`, `rankResults`, and `summarize` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T046 [US3] Implement missing-OAuth rejection before wrapper execution with sanitized `authentication_failed` details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T047 [US3] Implement upstream error mapping for authentication, authorization, missing/already-removed targets, non-removable targets, quota, invalid request, unavailable endpoint, deprecated endpoint, and unexpected upstream failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T048 [US3] Ensure delete error detail sanitization removes API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, and unsafe request context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T049 [US3] Add or update reStructuredText docstrings for all new or modified US3 Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T050 [US3] Add or update reStructuredText docstrings for all new or modified US3 fake wrapper methods in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T051 [US3] Run US3 focused validation and error tests and fix failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T052 [US3] Refactor US3 validation and error mapping for consistency with `SubscriptionsInsertToolError` while preserving delete-specific failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`

**Checkpoint**: User Story 3 is independently testable through invalid, access, target-state, and upstream failure scenarios.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete endpoint tool and finish cross-cutting quality gates.

- [X] T053 [P] Review `subscriptions_delete` contract alignment against `/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/contracts/subscriptions_delete.md`
- [X] T054 [P] Review quickstart coverage and update implementation evidence notes in `/Users/ctgunn/Projects/youtube-mcp-server/specs/243-subscriptions-delete/quickstart.md`
- [X] T055 Run focused verification command from quickstart and fix failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T056 Run `ruff check .` and fix lint failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T057 Review all changed Python functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
- [X] T058 Review all changed Python test helper functions for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py`
- [X] T059 Run full repository test suite `pytest` and fix all failures from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T060 Confirm `git status --short` contains only intended YT-243 changes from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Setup; blocks all user story implementation.
- **Phase 3 US1**: Depends on Foundational; delivers MVP executable deletion.
- **Phase 4 US2**: Depends on Foundational and is easiest after US1 descriptor scaffolding exists.
- **Phase 5 US3**: Depends on Foundational and is easiest after US1 handler/error scaffolding exists.
- **Phase 6 Polish**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories after Foundational; recommended MVP.
- **US2 (P2)**: Can start after Foundational if descriptor scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `subscriptions.py`.
- **US3 (P3)**: Can start after Foundational if validation/error scaffolding is coordinated, but sequentially follows US1 to reduce file conflicts in `subscriptions.py`.

### Within Each User Story

- Red tests must be added and observed failing before implementation tasks.
- Green implementation should be the minimum needed to pass that story's tests.
- reStructuredText docstrings must be added or updated before story completion.
- Refactor only after focused tests pass.
- Final completion requires focused tests, full `pytest`, and `ruff check .`.

## Parallel Opportunities

- T007, T008, T009, and T010 can be written in parallel because they touch different test files.
- T012, T013, and T014 can be written in parallel because they touch contract, unit, and integration test files.
- T028, T029, and T030 can be written in parallel because they touch different contract test scopes.
- T039 and T042 can run in parallel because they touch unit validation tests and contract failure examples in different files; T040 and T041 should be serialized because they touch the same unit-test file.
- T053 and T054 can run in parallel after implementation is complete because they review separate documentation files.

## Parallel Example: User Story 1

```bash
Task: "Add contract tests for subscriptions_delete input schema, upstream identity, quota cost, OAuth mode, response convention, and executable descriptor in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
Task: "Add unit tests for successful validate_subscriptions_delete_arguments, map_subscriptions_delete_result, and build_subscriptions_delete_handler behavior in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py"
Task: "Add integration tests proving subscriptions_delete is registered and callable through the subscriptions family registry in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_subscriptions_registration.py"
```

## Parallel Example: User Story 2

```bash
Task: "Add contract tests for delete metadata text, usage notes, caveats, quota visibility, OAuth visibility, availability state, response boundary, and examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
Task: "Add catalog contract tests confirming subscriptions_delete metadata exposes quota cost 50 and OAuth-required auth before invocation in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
Task: "Add common contract tests confirming shared YouTube metadata exports include subscriptions_delete without replacing list or insert entries in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "Add unit validation tests for missing id, empty id, non-string id, unsupported top-level fields, channel-id lookup attempts, body/create-shape attempts, notification modifiers, analytics modifiers, ranking modifiers, summarization modifiers, and enrichment modifiers in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_subscriptions.py"
Task: "Add contract tests proving failure examples cover invalid request, access failure, target-state failure, quota/upstream failure, and out-of-scope workflow rejection in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_subscriptions_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup and Phase 2 foundational red tests.
2. Complete Phase 3 US1 tests and minimal implementation.
3. Validate `subscriptions_delete` can execute a successful authorized deletion path through the handler and registry.
4. Stop and review before adding metadata polish and broad failure handling.

### Incremental Delivery

1. US1 delivers executable deletion with safe success context.
2. US2 makes discovery metadata, quota, OAuth, examples, and caveats complete for caller planning.
3. US3 completes invalid request, access, target-state, and upstream failure boundaries.
4. Polish runs focused tests, full `pytest`, `ruff check .`, docstring review, and final status review.

### Parallel Team Strategy

1. One engineer writes foundational and US1 tests while another prepares metadata/catalog tests for US2.
2. Implementation in `subscriptions.py` should be serialized or carefully coordinated because US1, US2, and US3 all edit the same file.
3. Contract, unit, and integration test files can be updated in parallel when assigned by file owner.

## Notes

- `[P]` tasks are limited to work that can proceed without depending on incomplete tasks and usually touches different files.
- Story labels map to `US1`, `US2`, and `US3` from the feature specification.
- All implementation tasks touching Python code include explicit docstring follow-up tasks.
- Do not mark the feature complete until full `pytest` and `ruff check .` pass after final changes.
- Keep the implementation endpoint-backed and avoid subscription listing, creation, lookup, enrichment, analytics, notification, or bulk-delete behavior.
