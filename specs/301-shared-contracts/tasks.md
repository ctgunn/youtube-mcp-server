# Tasks: YT-301 Layer 3 Shared Scaffolding and Contracts

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/data-model.md), [contracts/](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/contracts/)

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. Python code changes require reStructuredText docstrings for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks in the same phase when files do not overlap
- **[Story]**: Maps to a user story from [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/spec.md)
- Every task below includes an exact repository path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the Layer 3 shared package shell and test placeholders without implementing public Layer 3 tool behavior.

- [X] T001 Create the Layer 3 package directory and empty package initializer in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/__init__.py`
- [X] T002 [P] Create empty shared contract module placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py`
- [X] T003 [P] Create empty shared convention module placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py`
- [X] T004 [P] Create empty representative examples module placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`
- [X] T005 [P] Create empty family registry module placeholder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/families.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add broad Red checks and shared package guardrails that MUST be complete before user story implementation begins.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T006 [P] Add failing import and no-concrete-tool contract checks for the new Layer 3 package in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`
- [X] T007 [P] Add failing package-boundary unit checks that reject hosted transport, persistence, and concrete tool execution dependencies in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`
- [X] T008 Add module-level reStructuredText docstrings and explicit no-concrete-tool scope notes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/__init__.py`
- [X] T009 Add module-level reStructuredText docstrings and safe dependency notes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py`
- [X] T010 Add module-level reStructuredText docstrings and safe dependency notes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py`
- [X] T011 Add module-level reStructuredText docstrings and safe dependency notes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`
- [X] T012 Add module-level reStructuredText docstrings and safe dependency notes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/families.py`
- [X] T013 Run foundational Red checks and confirm they fail for missing Layer 3 primitives from `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`

**Checkpoint**: Layer 3 package shell and failing baseline tests are ready.

---

## Phase 3: User Story 1 - Define Layer 3 Public Contracts Once (Priority: P1) MVP

**Goal**: Maintainers can define shared Layer 3 naming, contract metadata, repeated parameter references, composition notes, lower-layer dependency notes, auth/quota caveats, partial-result policy, and safe review metadata once for later YT-302+ slices.

**Independent Test**: Review and run the US1 checks to confirm representative Layer 3 contracts derive grouped names, reject invalid names, expose required contract fields, and do not implement concrete public tool execution.

### Tests for User Story 1 (REQUIRED)

Write these tests FIRST and confirm they fail before implementation.

- [X] T014 [P] [US1] Add failing contract tests for all 19 grouped Layer 3 public names in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`
- [X] T015 [P] [US1] Add failing contract tests for required Layer 3 tool contract fields and safe public metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`
- [X] T016 [P] [US1] Add failing unit tests for grouped name validation and rejected `youtube_` prefixes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`
- [X] T017 [US1] Run US1 Red tests and record expected failures from `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`

### Implementation for User Story 1

- [X] T018 [US1] Implement `ToolContractError`, `ToolFamily`, `ToolContract`, grouped-name validation, and safe metadata validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py`
- [X] T019 [US1] Implement planned catalog constants for all 19 Layer 3 public tool names in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py`
- [X] T020 [US1] Implement representative public contract builders for at least eight Layer 3 catalog shapes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`
- [X] T021 [US1] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py`
- [X] T022 [US1] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`
- [X] T023 [US1] Run focused US1 Green checks from `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`
- [X] T024 [US1] Refactor Layer 3 contract and example wording while keeping focused checks green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`

**Checkpoint**: User Story 1 is independently testable and provides the MVP shared Layer 3 public contract.

---

## Phase 4: User Story 2 - Use Public Tools With Predictable Results (Priority: P2)

**Goal**: Client developers can rely on consistent response provenance, heuristic disclosures, repeated parameter semantics, ranking/filtering rules, composition boundaries, partial-result notes, and safe error categories across representative Layer 3 results.

**Independent Test**: Review and run the US2 checks to confirm representative Layer 3 responses classify fields as raw upstream, normalized, or heuristic/inferred, and that all heuristics and composition behaviors include basis, limitations, bounds, auth/quota notes, and partial-result behavior.

### Tests for User Story 2 (REQUIRED)

Write these tests FIRST and confirm they fail before implementation.

- [X] T025 [P] [US2] Add failing unit tests for shared parameter conventions, defaults, bounds, and unsupported combinations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`
- [X] T026 [P] [US2] Add failing contract tests for response field provenance categories and heuristic disclosure completeness in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`
- [X] T027 [P] [US2] Add failing contract tests for ranking/filtering semantics, composition boundaries, partial-result policies, and safe error categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`
- [X] T028 [US2] Run US2 Red tests and record expected failures from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`

### Implementation for User Story 2

- [X] T029 [US2] Implement `SharedParameterConvention`, `Requiredness`, and parameter metadata conversion in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py`
- [X] T030 [US2] Implement `ResponseFieldCategory`, `ResponseFieldProvenance`, and response provenance validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py`
- [X] T031 [US2] Implement `HeuristicDisclosure`, `RankingFilteringRule`, `CompositionBoundary`, and safe error category declarations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py`
- [X] T032 [US2] Update representative examples with provenance, heuristic, ranking/filtering, composition, auth/quota, partial-result, and safe-error metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`
- [X] T033 [US2] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py`
- [X] T034 [US2] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`
- [X] T035 [US2] Run focused US2 Green checks from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`
- [X] T036 [US2] Refactor shared conventions and representative metadata while keeping focused checks green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/conventions.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/examples.py`

**Checkpoint**: User Story 2 is independently testable and representative Layer 3 results are predictable for clients.

---

## Phase 5: User Story 3 - Keep Higher-Level Tool Families Cohesive (Priority: P3)

**Goal**: Future Layer 3 authors can identify where definitions, input contracts, schemas, composed handlers, reusable helpers, examples, tests, and caveats belong for videos, channels, playlists, and transcripts without creating one monolithic shared file.

**Independent Test**: Review and run the US3 checks to confirm every planned Layer 3 tool maps to exactly one family, each family has placement metadata, shared conventions stay centralized, and registration/discovery metadata can be prepared without concrete public tool execution.

### Tests for User Story 3 (REQUIRED)

Write these tests FIRST and confirm they fail before implementation.

- [X] T037 [P] [US3] Add failing unit tests for family registry ownership, placement metadata, and no monolithic family leakage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`
- [X] T038 [P] [US3] Add failing integration-style tests for Layer 3 shared metadata registration readiness without concrete handlers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer3_tool_registration.py`
- [X] T039 [P] [US3] Add failing contract tests that map each planned public name to exactly one family and expected source area in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`
- [X] T040 [US3] Run US3 Red tests and record expected failures from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer3_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`

### Implementation for User Story 3

- [X] T041 [US3] Implement `FamilyScaffolding`, family placement records, and planned tool ownership validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/families.py`
- [X] T042 [P] [US3] Add video-family scaffolding declarations without concrete tool handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/videos.py`
- [X] T043 [P] [US3] Add channel-family scaffolding declarations without concrete tool handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/channels.py`
- [X] T044 [P] [US3] Add playlist-family scaffolding declarations without concrete tool handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/playlists.py`
- [X] T045 [P] [US3] Add transcript-family scaffolding declarations without concrete tool handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/transcripts.py`
- [X] T046 [US3] Export shared Layer 3 families and contract primitives from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/__init__.py`
- [X] T047 [US3] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/families.py`
- [X] T048 [US3] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/playlists.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/transcripts.py`
- [X] T049 [US3] Run focused US3 Green checks from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer3_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`
- [X] T050 [US3] Refactor family scaffolding exports while keeping focused checks green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/families.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/__init__.py`

**Checkpoint**: User Story 3 is independently testable and family placement is ready for later YT-302+ slices.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate docs, security boundaries, docstrings, and full repository behavior across the completed shared Layer 3 scaffolding.

- [X] T051 [P] Verify `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/contracts/layer3-public-tool-contract.md` matches implemented public contract fields in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/contracts.py`
- [X] T052 [P] Verify `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/contracts/layer3-scaffolding-contract.md` matches implemented family placement metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/families.py`
- [X] T053 [P] Verify `/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/quickstart.md` targeted checks match the final test file paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`
- [X] T054 [P] Add regression checks that public Layer 3 metadata rejects unsafe secret, token, stack trace, signed URL, and raw media fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`
- [X] T055 Review all new and modified Python functions for reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/`
- [X] T056 Run focused Layer 3 checks from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer3_tool_registration.py`
- [X] T057 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any lint failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/` or `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [X] T058 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and fix any repository test failures before considering YT-301 complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; start immediately.
- **Phase 2 Foundational**: Depends on Phase 1 and blocks all user story implementation.
- **Phase 3 US1 MVP**: Depends on Phase 2; establishes the shared Layer 3 public contract.
- **Phase 4 US2**: Depends on Phase 2 and can be developed independently when it provides its own convention records and examples, but sequential delivery after US1 is recommended because it extends representative contracts.
- **Phase 5 US3**: Depends on Phase 2 and can be developed independently when it provides its own family maps, but sequential delivery after US1 is recommended because it validates planned catalog ownership.
- **Phase 6 Polish**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2. Suggested MVP scope.
- **US2 (P2)**: Can start after Phase 2; it should remain independently testable through response/provenance convention tests.
- **US3 (P3)**: Can start after Phase 2; it should remain independently testable through family registry and placement tests.

### Within Each User Story

- Red tests must be written and observed failing before implementation tasks begin.
- Green implementation must add only the minimum shared records, conventions, examples, or family maps required by that story.
- Docstring tasks must be completed before the story checkpoint.
- Refactor tasks must preserve passing focused tests.
- Final completion requires focused checks, `python3 -m ruff check .`, and full `python3 -m pytest`.

---

## Parallel Opportunities

- Setup placeholders T002 through T005 can run in parallel after T001 because they touch different files.
- Foundational Red tests T006 and T007 can run in parallel because they touch different test files.
- US1 Red tests T014 through T016 can run in parallel, then T017 verifies their failing state.
- US2 Red tests T025 through T027 can run in parallel, then T028 verifies their failing state.
- US3 Red tests T037 through T039 can run in parallel, then T040 verifies their failing state.
- US3 family module tasks T042 through T045 can run in parallel after T041 because they touch separate family files.
- Polish documentation verification tasks T051 through T054 can run in parallel before final focused and full-suite validation.

---

## Parallel Example: User Story 1

```bash
# Launch US1 Red test creation in parallel:
Task: "T014 [P] [US1] Add failing contract tests for all 19 grouped Layer 3 public names in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py"
Task: "T015 [P] [US1] Add failing contract tests for required Layer 3 tool contract fields and safe public metadata in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py"
Task: "T016 [P] [US1] Add failing unit tests for grouped name validation and rejected youtube_ prefixes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py"
```

## Parallel Example: User Story 2

```bash
# Launch US2 Red test creation in parallel:
Task: "T025 [P] [US2] Add failing unit tests for shared parameter conventions, defaults, bounds, and unsupported combinations in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer3_shared_scaffolding.py"
Task: "T026 [P] [US2] Add failing contract tests for response field provenance categories and heuristic disclosure completeness in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_shared_contract.py"
Task: "T027 [P] [US2] Add failing contract tests for ranking/filtering semantics, composition boundaries, partial-result policies, and safe error categories in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer3_tool_catalog_contract.py"
```

## Parallel Example: User Story 3

```bash
# Launch US3 family scaffolding modules in parallel after T041:
Task: "T042 [P] [US3] Add video-family scaffolding declarations without concrete tool handlers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/videos.py"
Task: "T043 [P] [US3] Add channel-family scaffolding declarations without concrete tool handlers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/channels.py"
Task: "T044 [P] [US3] Add playlist-family scaffolding declarations without concrete tool handlers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/playlists.py"
Task: "T045 [P] [US3] Add transcript-family scaffolding declarations without concrete tool handlers in /Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/transcripts.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational Red checks and package guardrails.
3. Complete Phase 3 US1 to produce the shared Layer 3 public contract and representative examples.
4. Stop and validate US1 independently with the focused US1 checks.
5. Continue to US2 and US3 only after the MVP contract is stable.

### Incremental Delivery

1. Setup and foundational tasks create the package shell and failing checks.
2. US1 adds the MVP shared public contract and grouped catalog validation.
3. US2 adds predictable response, heuristic, ranking/filtering, and composition conventions.
4. US3 adds cohesive family scaffolding and registration-readiness metadata.
5. Polish verifies docs, security boundaries, docstrings, lint, and full repository tests.

### Parallel Team Strategy

1. Complete Phase 1 and Phase 2 together.
2. Assign US1, US2, and US3 to separate contributors only after agreeing on shared module ownership to avoid file conflicts.
3. Run focused story checks before integrating each story.
4. Run final `python3 -m ruff check .` and `python3 -m pytest` after all selected stories are integrated.

---

## Notes

- `[P]` tasks touch different files or can be prepared without depending on incomplete implementation tasks.
- `[US1]`, `[US2]`, and `[US3]` labels map to prioritized user stories in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/301-layer3-shared-contracts/spec.md).
- Tests are mandatory and must be written before implementation.
- reStructuredText docstrings are mandatory for every new or modified Python function.
- YT-301 must remain shared scaffolding only; concrete YT-302+ public tool execution is out of scope.
