# Tasks: YT-102 Layer 1 Endpoint Metadata, Quota, and Signature Standards

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Path Conventions

- Python service code: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Tests: `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- Feature docs: `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the YT-102 feature workspace and align the tasking baseline with the plan, contracts, and existing Layer 1 modules.

- [x] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/spec.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/quickstart.md` to confirm scope, MVP story, and verification commands
- [x] T002 [P] Inspect `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` to capture the current `EndpointMetadata` and wrapper docstring baseline for YT-102
- [x] T003 [P] Inspect `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` to map existing YT-101 coverage to YT-102 gaps

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared metadata-standard scaffolding and test surfaces that all user stories depend on.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [x] T004 [P] Create `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` with a baseline test module for YT-102 artifact and contract assertions
- [x] T005 Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` to define the foundational metadata fields and validation hooks needed for `caveat_note`, `auth_condition_note`, and lifecycle reviewability
- [x] T006 [P] Update `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/layer1-metadata-standard.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/layer1-reviewability-contract.md` if implementation naming or validation semantics need tightening after T005
- [x] T007 Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` so shared metadata exports and wrapper surfaces stay aligned with the tightened contract

**Checkpoint**: Shared metadata standard and test entrypoints exist; user story work can now proceed.

---

## Phase 3: User Story 1 - Review Wrapper Metadata Quickly (Priority: P1) 🎯 MVP

**Goal**: Make representative Layer 1 wrappers visibly complete for identity, HTTP semantics, quota cost, auth mode, and required lifecycle caveats.

**Independent Test**: A maintainer can inspect representative wrapper artifacts and tests and confirm that missing identity, path, quota, auth, or required caveat fields fail validation while complete wrappers expose those fields without outside research.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Add failing metadata completeness tests for required identity, HTTP, quota, auth, and lifecycle fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [x] T009 [P] [US1] Add failing contract artifact tests for metadata visibility requirements in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`

### Implementation for User Story 1

- [x] T010 [US1] Implement metadata completeness validation and lifecycle-state handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`
- [x] T011 [US1] Update representative wrapper docstrings and maintainer-visible metadata usage in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [x] T012 [US1] Add or update reStructuredText docstrings for changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [x] T013 [US1] Refactor metadata field naming and validation messages in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` green

**Checkpoint**: User Story 1 should now be independently reviewable and testable as the MVP.

---

## Phase 4: User Story 2 - Plan Higher-Layer Work With Quota Awareness (Priority: P2)

**Goal**: Make representative wrappers easy to compare for quota and auth implications so future Layer 2 and Layer 3 planning can happen without raw upstream research.

**Independent Test**: A future higher-layer author can compare representative wrappers using contract artifacts and integration coverage and determine quota and auth tradeoffs without tracing raw transport details.

### Tests for User Story 2 (REQUIRED) ⚠️

- [x] T014 [P] [US2] Add failing reviewability contract tests for quota and auth comparison flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`
- [x] T015 [P] [US2] Add failing integration coverage for representative wrapper comparison and higher-layer planning outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

### Implementation for User Story 2

- [x] T016 [US2] Implement maintainer-visible quota and auth comparison support in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`
- [x] T017 [US2] Update higher-layer planning and comparison documentation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/layer1-reviewability-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/quickstart.md`
- [x] T018 [US2] Update representative higher-layer usage expectations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` if needed to reflect the new comparison semantics
- [x] T019 [US2] Add or update reStructuredText docstrings for changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [x] T020 [US2] Refactor duplicated quota and auth review wording across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/layer1-reviewability-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/quickstart.md` while keeping US2 tests green

**Checkpoint**: User Stories 1 and 2 should both work independently, and higher-layer planning should be possible from wrapper-facing artifacts.

---

## Phase 5: User Story 3 - Flag Documentation Gaps Before Endpoint Expansion (Priority: P3)

**Goal**: Make deprecation, limited availability, and official-doc inconsistencies explicit, structured, and reusable before later endpoint slices expand coverage.

**Independent Test**: A reviewer can inspect a representative caveated wrapper and its contract artifacts and see the caveat type, implication, and reuse impact without re-reading external documentation.

### Tests for User Story 3 (REQUIRED) ⚠️

- [x] T021 [P] [US3] Add failing unit tests for required `caveat_note` and `auth_condition_note` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [x] T022 [P] [US3] Add failing contract artifact tests for deprecation, availability, and inconsistent-doc caveat disclosure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`

### Implementation for User Story 3

- [x] T023 [US3] Implement caveat categorization and required explanatory-note behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`
- [x] T024 [US3] Update representative auth-mode and lifecycle guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` to keep mixed or caveated flows understandable to maintainers
- [x] T025 [US3] Update caveat examples and maintainer guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/contracts/layer1-metadata-standard.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/quickstart.md`
- [x] T026 [US3] Add or update reStructuredText docstrings for changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [x] T027 [US3] Refactor caveat naming and validation helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` while keeping `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` green

**Checkpoint**: All three user stories should now be independently functional and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and repository-wide regression protection.

- [x] T028 [P] Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/quickstart.md` against the implemented workflow and update any stale verification steps
- [x] T029 [P] Add any remaining shared regression coverage for metadata reviewability drift in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [x] T030 Run targeted YT-102 validation in `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_metadata_contract.py`
- [x] T031 Run the full repository test suite in `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest` and resolve any failures before completion
- [x] T032 Run `ruff check .` in `/Users/ctgunn/Projects/youtube-mcp-server` and resolve any lint failures before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies; can start immediately.
- **Phase 2: Foundational**: Depends on Phase 1; blocks all user stories because the shared metadata standard and contract test surface must exist first.
- **Phase 3: User Story 1**: Depends on Phase 2; this is the MVP and should land first.
- **Phase 4: User Story 2**: Depends on Phase 2 and can build after US1 if shared metadata semantics from US1 are in place.
- **Phase 5: User Story 3**: Depends on Phase 2 and benefits from US1’s metadata completeness changes, but remains independently testable.
- **Phase 6: Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories; it is the MVP slice.
- **User Story 2 (P2)**: Depends on the foundational metadata standard and should reuse the metadata fields and validation introduced in US1.
- **User Story 3 (P3)**: Depends on the foundational metadata standard and should reuse the visibility model established in US1.

### Within Each User Story

- Write Red tests first and verify they fail before implementation.
- Implement the minimum code and doc changes needed to satisfy the failing tests.
- Update reStructuredText docstrings for every new or changed Python function before the story is considered complete.
- Refactor only after story tests pass.
- Keep each story independently testable using its stated independent test criteria.
- Before marking the feature complete, run `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.

### Dependency Graph

- `T001-T003` → `T004-T007` → `T008-T013` → `T014-T020` and `T021-T027` → `T028-T032`
- US2 and US3 can proceed in parallel after US1’s shared metadata changes settle, but both still depend on the Phase 2 foundation.

## Parallel Opportunities

- **Setup**: `T002` and `T003`
- **Foundational**: `T004` and `T006`
- **US1**: `T008` and `T009`
- **US2**: `T014` and `T015`
- **US3**: `T021` and `T022`
- **Polish**: `T028` and `T029`

## Parallel Example: User Story 1

```bash
# Run the US1 Red tasks in parallel:
Task: "T008 Add failing metadata completeness tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T009 Add failing contract artifact tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
```

## Parallel Example: User Story 2

```bash
# Run the US2 Red tasks in parallel:
Task: "T014 Add failing reviewability contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
Task: "T015 Add failing integration coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
```

## Parallel Example: User Story 3

```bash
# Run the US3 Red tasks in parallel:
Task: "T021 Add failing unit tests for caveat notes in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T022 Add failing contract artifact tests for caveat disclosure in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate US1 independently using the US1 unit and contract tests.
5. Stop for review if only the MVP is needed.

### Incremental Delivery

1. Complete Setup + Foundational to establish the metadata-standard base.
2. Deliver User Story 1 as the first usable increment for wrapper reviewability.
3. Deliver User Story 2 to support quota-aware higher-layer planning.
4. Deliver User Story 3 to lock in caveat disclosure before endpoint expansion.
5. Finish with repository-wide regression and lint validation.

### Parallel Team Strategy

1. One teammate completes Phase 1 and the shared Phase 2 contract setup.
2. After the Phase 2 checkpoint:
   - Teammate A drives US1 to stabilize core metadata validation.
   - Teammate B prepares US2 comparison tests and docs once US1 field names settle.
   - Teammate C prepares US3 caveat tests and examples once US1 visibility semantics settle.
3. Rejoin for Phase 6 validation and cleanup.

## Notes

- `[P]` tasks touch different files or can proceed without waiting on incomplete sibling tasks.
- User story labels appear only on story-phase tasks.
- Every task includes an exact file path so it can be executed directly.
- The recommended MVP scope is **User Story 1**.
