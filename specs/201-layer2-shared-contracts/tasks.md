# Tasks: YT-201 Shared YouTube Scaffolding and Contracts

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/`

**Tests**: Test tasks are required for every user story and foundational behavior. Completion requires a passing full repository test-suite run after final code changes. Python code tasks include explicit reStructuredText docstring work before each story is complete.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. US1 is the MVP because it establishes the shared YouTube contract records and naming rules that later endpoint slices depend on.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the shared YouTube package and empty test files without adding endpoint behavior.

- [X] T001 Create shared YouTube package directory and empty package initializer in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T002 [P] Create empty shared contract test file in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T003 [P] Create empty shared scaffolding unit test file in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T004 [P] Create empty YouTube tool foundation registration integration test file in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T005 [P] Create empty YouTube tool catalog contract test file in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the minimal shared module boundaries that all user stories use.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 Create shared contract module skeleton with module-level reStructuredText-style documentation notes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T007 [P] Create shared representative examples module skeleton in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T008 [P] Create shared schema and result convention module skeleton in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T009 [P] Create shared resource-family scaffolding module skeleton in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- [X] T010 Export placeholder shared YouTube symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T011 Run import smoke check from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_youtube_common_scaffolding.py` and confirm no collection errors from the new files

**Checkpoint**: shared YouTube module files exist and user story implementation can begin.

---

## Phase 3: User Story 1 - Define shared YouTube Contracts Once (Priority: P1) MVP

**Goal**: Maintainers can derive and validate shared YouTube public tool contracts without redefining naming, upstream identity, auth, quota, caveat, input, response, or error rules per endpoint.

**Independent Test**: Review and run the US1 contract/unit tests to confirm a representative endpoint contract cannot pass unless it declares public name, upstream resource and method, official quota cost, auth mode, caveats when applicable, input mapping, near-raw response convention, and safe error categories.

### Tests for User Story 1 (REQUIRED)

- [X] T012 [P] [US1] Add failing contract tests for required YouTube tool metadata fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T013 [P] [US1] Add failing unit tests for `resource_method` name derivation, camelCase preservation, and `youtube_` prefix rejection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T014 [P] [US1] Add failing contract tests for representative examples including `activities.list`, `comments.setModerationStatus`, `videos.getRating`, and `watermarks.unset` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 1

- [X] T015 [US1] Implement `YouTubeToolContract`, `AuthMode`, and `YouTubeToolContractError` primitives in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T016 [US1] Implement `derive_tool_name` and metadata validation helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T017 [US1] Add representative contract examples for simple read, camelCase, OAuth-only, and constrained endpoint shapes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T018 [US1] Export US1 contract primitives and representative examples from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T019 [US1] Add or update reStructuredText docstrings for every new or changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T020 [US1] Add or update reStructuredText docstrings for every new or changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T021 [US1] Run focused US1 checks from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T022 [US1] Refactor duplicated metadata validation paths while keeping US1 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`

**Checkpoint**: User Story 1 is independently testable and provides the MVP shared YouTube contract foundation.

---

## Phase 4: User Story 2 - Use Low-Level Tools With Predictable Semantics (Priority: P2)

**Goal**: Power users and endpoint authors can rely on consistent near-raw input, response, auth, quota, and safe error conventions across representative YouTube endpoint shapes.

**Independent Test**: Apply the shared conventions to representative read, paginated, camelCase, OAuth-only, mutation, upload/media, high-quota, and constrained/deprecated examples and verify schema, response, and error expectations without implementing real endpoint behavior.

### Tests for User Story 2 (REQUIRED)

- [X] T023 [P] [US2] Add failing unit tests for input convention helpers covering required fields, selector groups, `part`, pagination, request body, media, and delegation metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T024 [P] [US2] Add failing contract tests for near-raw response conventions covering list, mutation acknowledgment, upload/media, download-safe wrapper, and lookup result kinds in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T025 [P] [US2] Add failing contract tests for safe error categories and secret-leak prevention in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T026 [P] [US2] Extend representative catalog tests for paginated, mutation, upload/media, high-quota, and deprecated/availability-constrained shapes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py`

### Implementation for User Story 2

- [X] T027 [US2] Implement input convention records and validation helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T028 [US2] Implement response convention records for list, mutation acknowledgment, upload/media, download-safe wrapper, and lookup result kinds in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T029 [US2] Implement safe YouTube tool error category records and detail sanitization helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T030 [US2] Add representative examples for paginated, mutation, upload/media, high-quota, and deprecated/availability-constrained endpoint shapes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T031 [US2] Export US2 convention primitives from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T032 [US2] Add or update reStructuredText docstrings for every new or changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T033 [US2] Add or update reStructuredText docstrings for every US2-changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T034 [US2] Run focused US2 checks from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py`
- [X] T035 [US2] Refactor convention helper names and duplicate example setup while keeping US1 and US2 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`

**Checkpoint**: User Stories 1 and 2 work independently and prove predictable near-raw YouTube endpoint semantics for representative shapes.

---

## Phase 5: User Story 3 - Keep Endpoint Tool Families Cohesive (Priority: P3)

**Goal**: Future endpoint authors can locate where YouTube tool definitions, input contracts, handlers, response expectations, tests, examples, and caveats belong by resource family without creating a monolithic endpoint-tool file.

**Independent Test**: Select representative resource families and verify the scaffolding map identifies family ownership, shared helper boundaries, Layer 1 dependency boundaries, and expected test/documentation locations in under 3 minutes.

### Tests for User Story 3 (REQUIRED)

- [X] T036 [P] [US3] Add failing unit tests for required YouTube resource-family names and placement metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py`
- [X] T037 [P] [US3] Add failing contract tests proving endpoint-specific facts stay with resource-family scaffolding while shared rules remain centralized in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`
- [X] T038 [P] [US3] Add failing integration tests for registering representative YouTube tool descriptors with the existing dispatcher without endpoint execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Implementation for User Story 3

- [X] T039 [US3] Implement `YouTubeResourceFamily` and required family registry helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- [X] T040 [US3] Implement scaffolding placement metadata for tool definitions, handlers, schemas, tests, examples, caveats, and Layer 1 dependency boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- [X] T041 [US3] Implement representative descriptor factory for registration/discovery tests without adding real endpoint behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- [X] T042 [US3] Export US3 family scaffolding primitives from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T043 [US3] Add or update reStructuredText docstrings for every new or changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- [X] T044 [US3] Add or update reStructuredText docstrings for every US3-changed export helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T045 [US3] Run focused US3 checks from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/integration/test_youtube_tool_registration.py`
- [X] T046 [US3] Refactor resource-family scaffolding to remove duplicate placement strings while keeping US1, US2, and US3 tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`

**Checkpoint**: All user stories are independently functional and later endpoint slices have a cohesive resource-family scaffold.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish documentation, regression, lint, and full-suite verification across all stories.

- [X] T047 [P] Update quickstart implementation notes with final focused test commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/quickstart.md`
- [X] T048 [P] Update public tool contract notes if implementation changed shared naming, metadata, response, or error wording in `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/youtube-public-tool-contract.md`
- [X] T049 [P] Update scaffolding contract notes if implementation changed family placement or test-location guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/contracts/youtube-scaffolding-contract.md`
- [X] T050 [P] Review all changed Python files for reStructuredText docstrings and fix missing purpose/input/output/error/side-effect coverage in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`
- [X] T051 Run all focused YouTube tool foundation tests from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` and fix failures in affected files
- [X] T052 Run the full repository test suite from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest` and fix failures in affected files
- [X] T053 Run lint validation from `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m ruff check .` and fix failures in affected files
- [X] T054 Verify no concrete endpoint-backed YouTube tool behavior was added outside representative examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies and can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can run after US1 contract primitives exist for smoother integration
- **User Story 3 (Phase 5)**: Depends on Foundational completion; can run after US1/US2 or in parallel if shared interfaces are agreed
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories after Foundational; establishes MVP shared contracts
- **User Story 2 (P2)**: Uses US1 contract primitives but remains independently testable through convention tests and representative examples
- **User Story 3 (P3)**: Uses US1 contract primitives and may reference US2 examples, but remains independently testable through family scaffolding and registration tests

### Within Each User Story

- Red tests must be written first and confirmed failing before Green implementation
- Contract and unit tests precede implementation helpers
- Shared records and helpers precede exports and integration registration checks
- reStructuredText docstring tasks must complete before each story checkpoint
- Refactor tasks run only after focused story tests pass
- Full repository `python3 -m pytest` and `python3 -m ruff check .` run in Polish after the final code change

### Parallel Opportunities

- T002, T003, T004, and T005 can run in parallel after T001 decision on package path
- T007, T008, and T009 can run in parallel after T006 establishes the shared package convention
- US1 Red tests T012, T013, and T014 can run in parallel
- US2 Red tests T023, T024, T025, and T026 can run in parallel
- US3 Red tests T036, T037, and T038 can run in parallel
- Polish documentation checks T047, T048, T049, and docstring review T050 can run in parallel after implementation stabilizes

---

## Parallel Example: User Story 1

```bash
Task: "T012 [US1] Add failing contract tests for required YouTube tool metadata fields in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T013 [US1] Add failing unit tests for resource_method name derivation in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py"
Task: "T014 [US1] Add failing contract tests for representative examples in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
```

## Parallel Example: User Story 2

```bash
Task: "T023 [US2] Add failing unit tests for input convention helpers in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py"
Task: "T024 [US2] Add failing contract tests for response conventions in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T025 [US2] Add failing contract tests for safe error categories in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T026 [US2] Extend representative catalog tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_tool_catalog_contract.py"
```

## Parallel Example: User Story 3

```bash
Task: "T036 [US3] Add failing unit tests for required YouTube resource-family names in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_common_scaffolding.py"
Task: "T037 [US3] Add failing contract tests for family/shared boundary rules in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py"
Task: "T038 [US3] Add failing integration tests for representative descriptor registration in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup
2. Complete Phase 2 foundational module skeletons
3. Complete Phase 3 User Story 1
4. Stop and validate with `python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
5. Demo MVP by deriving names and validating representative shared YouTube contracts without adding endpoint behavior

### Incremental Delivery

1. Setup and Foundational phases create the shared YouTube package
2. US1 adds the MVP naming and metadata contract
3. US2 adds predictable input, response, and safe error conventions
4. US3 adds resource-family placement and registration/discovery scaffolding
5. Polish runs focused checks, full repository tests, and lint

### Parallel Team Strategy

With multiple contributors:

1. Complete Setup and Foundational phases together
2. Assign US1 contract primitives to one contributor
3. Assign US2 convention helpers to another contributor after US1 interfaces are stable
4. Assign US3 family scaffolding to another contributor after package boundaries are stable
5. Merge only after focused checks, full-suite tests, lint, and docstring review pass

## Notes

- Every task uses the required checkbox, sequential task ID, optional `[P]`, optional story label, and an exact path
- Tests are mandatory and appear before implementation in each user story
- Python docstring tasks are explicit in every story that changes Python files
- YT-201 must remain shared scaffolding; endpoint-specific public tools belong to later YT-203 through YT-255 slices
