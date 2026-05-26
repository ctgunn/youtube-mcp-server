# Tasks: YT-202 Layer 2 Tool Metadata, Naming, and Quota Standards

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/data-model.md), [contracts/layer2-metadata-standards-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/contracts/layer2-metadata-standards-contract.md), [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/quickstart.md)

**Tests**: Required for every story. Write failing or characterization tests before implementation, then perform Green implementation, Refactor cleanup, focused validation, full repository validation, and Ruff validation.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after foundational safeguards are in place.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase because it touches different files or only reads files
- **[Story]**: User story label for story phases only
- Every task includes an exact repository path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature branch, planning artifacts, and existing YT-201 shared Layer 2 surface before adding YT-202 tests.

- [X] T001 Verify the working branch is `202-layer2-metadata-standards` and confirm `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/plan.md` matches the current implementation scope
- [X] T002 [P] Review the metadata standards contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/contracts/layer2-metadata-standards-contract.md` before editing tests
- [X] T003 [P] Review existing shared Layer 2 exports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py` before adding new public symbols
- [X] T004 [P] Review current representative examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` before adding YT-202 metadata requirements

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add broad safety checks that prevent YT-202 from turning into concrete endpoint implementation or leaking unsafe metadata.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T005 Add a failing guard test that representative descriptors remain non-executing standards artifacts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer2_tool_registration.py`
- [X] T006 Add a failing safe-metadata regression test that rejects credentials, tokens, stack traces, signed URLs, and unsafe raw media fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_shared_contract.py`
- [X] T007 Implement the minimal shared safe metadata validation helper needed for foundational tests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T008 Update reStructuredText docstrings for foundational helper changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T009 Run the foundational focused checks `python3 -m pytest tests/contract/test_layer2_shared_contract.py tests/integration/test_layer2_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Inspect Tool Identity and Cost (Priority: P1) MVP

**Goal**: A client developer can inspect any representative Layer 2 tool and see public name, upstream identity, official quota cost, auth mode, availability state, caveats, description quota visibility, and usage-note quota visibility before invocation.

**Independent Test**: Review representative Layer 2 metadata and run focused tests proving required fields, safe metadata, quota visibility, auth mode, and availability state are present and caller-facing.

### Tests for User Story 1 (REQUIRED)

- [X] T010 [P] [US1] Add failing contract tests for required metadata fields including availability state and usage notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_shared_contract.py`
- [X] T011 [P] [US1] Add failing catalog tests requiring all representative examples to expose quota cost, auth mode, availability state, description quota text, and usage-note quota text in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_tool_catalog_contract.py`
- [X] T012 [P] [US1] Add a failing integration test proving representative descriptor discovery metadata includes quota, auth, availability, caveats, and usage notes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer2_tool_registration.py`

### Implementation for User Story 1

- [X] T013 [US1] Add `AvailabilityState` and usage-note metadata primitives in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T014 [US1] Extend `Layer2ToolContract` validation and `to_tool_metadata()` to include availability state, usage notes, caveats, and quota-visible description requirements in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T015 [US1] Update representative metadata examples with availability state, usage notes, quota-visible descriptions, and safe caveats in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T016 [US1] Export new metadata primitives from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T017 [US1] Update reStructuredText docstrings for all new or modified functions and classes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T018 [US1] Update reStructuredText docstrings for all new or modified helper functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T019 [US1] Refactor duplicated quota, auth, availability, and caveat wording while keeping tests green in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T020 [US1] Run focused User Story 1 checks `python3 -m pytest tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py tests/integration/test_layer2_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 1 is independently testable and delivers the MVP.

---

## Phase 4: User Story 2 - Derive Names Consistently (Priority: P2)

**Goal**: A maintainer can derive every Layer 2 public tool name from its YouTube resource-method pair using a deterministic `resource_method` standard with meaningful upstream camelCase preserved.

**Independent Test**: Apply naming tests to at least 10 representative resource-method pairs and confirm generated names omit `youtube_`, preserve official camelCase method suffixes, and match examples.

### Tests for User Story 2 (REQUIRED)

- [X] T021 [P] [US2] Add failing unit tests for at least 10 representative `derive_tool_name()` cases in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer2_shared_scaffolding.py`
- [X] T022 [P] [US2] Add failing catalog tests that every representative example's `tool_name` equals the derived resource-method name in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_tool_catalog_contract.py`
- [X] T023 [P] [US2] Add failing contract tests rejecting redundant provider-prefixed or casing-drifted names in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_shared_contract.py`

### Implementation for User Story 2

- [X] T024 [US2] Tighten `derive_tool_name()` validation for deterministic resource-method naming and official camelCase preservation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T025 [US2] Update representative examples to include the required naming coverage for `videos.list`, `playlists.insert`, `comments.setModerationStatus`, `videos.getRating`, `videos.reportAbuse`, and `playlistItems.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T026 [US2] Update reStructuredText docstrings for naming-related changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T027 [US2] Refactor naming examples to remove duplicate literal name construction while preserving representative readability in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T028 [US2] Run focused User Story 2 checks `python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 2 is independently testable and naming rules are ready for later endpoint slices.

---

## Phase 5: User Story 3 - Preserve Raw Endpoint Semantics With Clear Boundaries (Priority: P3)

**Goal**: A future Layer 3 author can identify whether each representative Layer 2 result is near-raw, lightly reshaped for MCP clarity, or out of Layer 2 scope, while preserving quota/auth implications for composition.

**Independent Test**: Run response-boundary tests proving representative examples preserve upstream-visible concepts, allow only safe wrapper fields, and reject Layer 3-style composition, enrichment, ranking, or heuristics.

### Tests for User Story 3 (REQUIRED)

- [X] T029 [P] [US3] Add failing contract tests for response-boundary kinds `near_raw`, `lightly_reshaped`, and `out_of_scope` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_shared_contract.py`
- [X] T030 [P] [US3] Add failing catalog tests proving representative examples include response-boundary metadata for list, lookup, mutation acknowledgment, upload result, and download wrapper shapes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer2_tool_catalog_contract.py`
- [X] T031 [P] [US3] Add failing unit tests for response-boundary metadata serialization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer2_shared_scaffolding.py`

### Implementation for User Story 3

- [X] T032 [US3] Add `ResponseBoundaryKind` and response-boundary metadata helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T033 [US3] Integrate response-boundary metadata into Layer 2 tool metadata output in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T034 [US3] Update representative examples with response-boundary metadata and preserved upstream-field expectations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T035 [US3] Export response-boundary primitives from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T036 [US3] Update reStructuredText docstrings for response-boundary helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`
- [X] T037 [US3] Update reStructuredText docstrings for contract integration changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`
- [X] T038 [US3] Refactor response-boundary examples to remove duplicated wrapper-field and preserved-field lists in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T039 [US3] Run focused User Story 3 checks `python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py` from `/Users/ctgunn/Projects/youtube-mcp-server`

**Checkpoint**: User Story 3 is independently testable and response boundaries are ready for future Layer 3 composition planning.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the combined standards slice, update review-facing documentation, and complete repository-wide verification.

- [X] T040 [P] Update the YT-202 implementation notes and validation commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/quickstart.md`
- [X] T041 [P] Update the YT-202 contract alignment notes if implementation changes contract wording in `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/contracts/layer2-metadata-standards-contract.md`
- [X] T042 [P] Review exported public symbols and remove unused exports in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- [X] T043 Run combined focused checks `python3 -m pytest tests/unit/test_layer2_shared_scaffolding.py tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py tests/integration/test_layer2_tool_registration.py` from `/Users/ctgunn/Projects/youtube-mcp-server`
- [X] T044 Run the full repository test suite `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T045 Run lint validation `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any failures before completion
- [X] T046 Confirm all modified Python functions have reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py`
- [X] T047 Confirm `git diff --check` reports no whitespace errors from `/Users/ctgunn/Projects/youtube-mcp-server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user story work
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the MVP
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can run after or alongside US1 if edits to `contracts.py` and `examples.py` are coordinated
- **User Story 3 (Phase 5)**: Depends on Foundational completion; can run after or alongside US1/US2 if edits to `contracts.py`, `conventions.py`, and `examples.py` are coordinated
- **Polish (Phase 6)**: Depends on all selected user stories being complete

### User Story Dependencies

- **US1 Inspect Tool Identity and Cost**: No dependency on US2 or US3 after Foundational; recommended MVP because it establishes the metadata record later stories reuse
- **US2 Derive Names Consistently**: No dependency on US3; benefits from US1 metadata examples but remains independently testable through naming tests
- **US3 Preserve Raw Endpoint Semantics With Clear Boundaries**: No dependency on US2; benefits from US1 metadata output but remains independently testable through response-boundary tests

### Within Each User Story

- Red tests must be written and observed failing before Green implementation
- Shared models/enums/helpers before representative examples
- Representative examples before integration/discovery checks
- reStructuredText docstrings before the story checkpoint
- Refactor only after focused tests pass
- Full repository validation occurs in Phase 6 after final code changes

### Parallel Opportunities

- Setup review tasks T002, T003, and T004 can run in parallel
- US1 Red tests T010, T011, and T012 can run in parallel
- US2 Red tests T021, T022, and T023 can run in parallel
- US3 Red tests T029, T030, and T031 can run in parallel
- Polish documentation/export review tasks T040, T041, and T042 can run in parallel
- Different user stories can be implemented by separate contributors after Phase 2 if shared-file edits are coordinated

---

## Parallel Example: User Story 1

```bash
# Add Red tests for US1 in parallel:
Task: "T010 [US1] Add required metadata field contract tests in tests/contract/test_layer2_shared_contract.py"
Task: "T011 [US1] Add representative example metadata tests in tests/contract/test_layer2_tool_catalog_contract.py"
Task: "T012 [US1] Add discovery metadata integration test in tests/integration/test_layer2_tool_registration.py"
```

## Parallel Example: User Story 2

```bash
# Add Red tests for US2 in parallel:
Task: "T021 [US2] Add derive_tool_name unit cases in tests/unit/test_layer2_shared_scaffolding.py"
Task: "T022 [US2] Add derived-name catalog tests in tests/contract/test_layer2_tool_catalog_contract.py"
Task: "T023 [US2] Add invalid-name contract tests in tests/contract/test_layer2_shared_contract.py"
```

## Parallel Example: User Story 3

```bash
# Add Red tests for US3 in parallel:
Task: "T029 [US3] Add response-boundary contract tests in tests/contract/test_layer2_shared_contract.py"
Task: "T030 [US3] Add response-boundary catalog tests in tests/contract/test_layer2_tool_catalog_contract.py"
Task: "T031 [US3] Add response-boundary serialization unit tests in tests/unit/test_layer2_shared_scaffolding.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 for US1
3. Run `python3 -m pytest tests/contract/test_layer2_shared_contract.py tests/contract/test_layer2_tool_catalog_contract.py tests/integration/test_layer2_tool_registration.py`
4. Stop and validate that representative tool metadata exposes identity, cost, auth, availability, caveats, descriptions, and usage notes before invocation

### Incremental Delivery

1. Complete Setup and Foundational safeguards
2. Deliver US1 metadata completeness as the MVP
3. Deliver US2 deterministic naming validation
4. Deliver US3 response-boundary classification
5. Complete Phase 6 full-suite and lint validation

### Parallel Team Strategy

With multiple contributors:

1. Complete Phase 1 and Phase 2 together
2. Assign US1 to the contributor owning `contracts.py` metadata fields
3. Assign US2 to the contributor owning naming tests and representative naming examples
4. Assign US3 to the contributor owning `conventions.py` response-boundary helpers
5. Coordinate edits to `examples.py` and `__init__.py` before final integration

## Notes

- [P] tasks are safe to start in parallel when they touch different files or only review files
- Story labels map directly to priorities in [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/spec.md)
- This task list intentionally excludes concrete endpoint-backed public tool implementation
- Final completion requires `python3 -m pytest`, `python3 -m ruff check .`, and `git diff --check`
