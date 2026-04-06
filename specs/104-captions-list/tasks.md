# Tasks: YT-104 Layer 1 Endpoint `captions.list`

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/`
**Prerequisites**: `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/data-model.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/`

**Tests**: Test tasks are REQUIRED. Every user story and foundational change includes Red-Green-Refactor coverage tasks. Completion requires a passing full repository test-suite run after the final code changes. When Python code changes, tasks include reStructuredText docstring updates for all new or modified functions.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Path Conventions

- Python service code: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/`
- Tests: `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- Feature docs: `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm YT-104 scope, implementation seams, and verification commands before code changes begin.

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/spec.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/quickstart.md` to confirm scope, MVP story, and verification commands
- [X] T002 [P] Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-wrapper-contract.md` to capture selector, auth, and delegation decisions
- [X] T003 [P] Inspect `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` to identify the current Layer 1 implementation seams for YT-104

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish shared endpoint-specific contract and validation scaffolding that all three user stories depend on.

**⚠️ CRITICAL**: No user story work should start until this phase is complete.

- [X] T004 [P] Create `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py` with baseline contract assertions for the YT-104 wrapper and auth-selector artifacts
- [X] T005 Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` so `EndpointRequestShape` or adjacent validation hooks can enforce endpoint-specific selector exclusivity for `captions.list`
- [X] T006 [P] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` so shared exports and wrapper entrypoints remain aligned with the new `captions.list` validation seam
- [X] T007 Update `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-wrapper-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-auth-selector-contract.md` if foundational naming or validation semantics change after T005

**Checkpoint**: Shared YT-104 contract tests and endpoint-specific validation hooks exist; user story work can now proceed.

---

## Phase 3: User Story 1 - Retrieve Caption Track Inventory Through a Typed Wrapper (Priority: P1) 🎯 MVP

**Goal**: Add a typed internal `captions.list` wrapper that supports caption-track retrieval, exposes the required endpoint metadata, and executes through the shared Layer 1 path.

**Independent Test**: Invoke the `captions.list` wrapper with a supported `videoId` request and confirm it validates the request, returns a structured caption-track collection, and exposes the upstream identity and quota metadata without needing raw request assembly.

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [P] [US1] Add failing unit tests for `captions.list` metadata completeness, quota visibility, and required selector validation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T009 [P] [US1] Add failing integration tests for successful `videoId`-based `captions.list` execution through the shared executor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T010 [P] [US1] Add failing transport tests for authorized `captions.list` request construction in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T011 [P] [US1] Add failing contract tests for wrapper review surfaces in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`

### Implementation for User Story 1

- [X] T012 [US1] Implement the representative `captions.list` wrapper metadata and request-shape definition in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T013 [US1] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` so the `captions.list` wrapper can reject missing or malformed `videoId` or `id` selector input before execution
- [X] T014 [US1] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` so request construction preserves the `captions.list` path, selector inputs, and OAuth-backed transport behavior
- [X] T015 [US1] Wire the `captions.list` wrapper for import and reuse in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`
- [X] T016 [US1] Add or update reStructuredText docstrings for changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T017 [US1] Refactor `captions.list` wrapper naming and selector-validation helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` while keeping US1 tests green

**Checkpoint**: User Story 1 is independently functional and testable as the MVP slice.

---

## Phase 4: User Story 2 - Understand OAuth Requirements Before Reuse (Priority: P2)

**Goal**: Make the `captions.list` wrapper clearly state that authorized access is required and explain how delegated content-owner context applies so future higher-layer authors can choose the right path without ambiguity.

**Independent Test**: Review the wrapper contract and integration behavior and confirm that `captions.list` is documented as OAuth-required, `onBehalfOfContentOwner` is documented as delegation context, and unsupported selector or delegation states are clearly rejected.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T018 [P] [US2] Add failing contract tests for OAuth-required and delegation guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`
- [X] T019 [P] [US2] Add failing integration tests for authorized `captions.list` execution with delegated content-owner context in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T020 [P] [US2] Add failing unit tests for mismatched auth expectations and unsupported delegation combinations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T021 [P] [US2] Add failing transport tests for OAuth header and delegation parameter handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

### Implementation for User Story 2

- [X] T022 [US2] Implement maintainer-facing OAuth-required metadata and delegation notes for `captions.list` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`
- [X] T023 [US2] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` so `captions.list` enforces the documented authorized-access semantics
- [X] T024 [US2] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` so `onBehalfOfContentOwner` is carried only as documented delegation context for supported requests
- [X] T025 [US2] Update `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-auth-selector-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/quickstart.md` to reflect the implemented auth and delegation rules
- [X] T026 [US2] Add or update reStructuredText docstrings for changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`
- [X] T027 [US2] Refactor duplicated auth and delegation guidance across `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-auth-selector-contract.md` while keeping US2 tests green

**Checkpoint**: User Stories 1 and 2 both work independently, and later-layer authors can identify the correct auth and delegation path from repository artifacts alone.

---

## Phase 5: User Story 3 - Review Caption Discovery Readiness for Follow-on Work (Priority: P3)

**Goal**: Make the `captions.list` wrapper fully reviewable for follow-on transcript and caption-management work by documenting quota cost, supported selector boundaries, invalid combinations, and empty-success semantics in one place.

**Independent Test**: Inspect the YT-104 contract artifacts and representative tests and confirm that a reviewer can verify quota cost `50`, supported selectors, invalid combinations, delegation rules, and empty-result success semantics without consulting external endpoint documentation.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T028 [P] [US3] Add failing contract tests for quota cost, selector-boundary visibility, delegation notes, and empty-success guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`
- [X] T029 [P] [US3] Add failing integration tests for valid empty `captions.list` results in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`
- [X] T030 [P] [US3] Add failing unit tests for unsupported selector combinations and unexpected request fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`
- [X] T031 [P] [US3] Add failing consumer-facing reviewability checks for downstream reuse in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`

### Implementation for User Story 3

- [X] T032 [US3] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py` so `captions.list` review surfaces expose quota cost, supported selector boundaries, delegation notes, and empty-success semantics clearly
- [X] T033 [US3] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` if needed so higher-layer reuse checks align with the final `captions.list` contract
- [X] T034 [US3] Update `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/quickstart.md` to match the final wrapper reviewability semantics
- [X] T035 [US3] Add or update reStructuredText docstrings for changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`
- [X] T036 [US3] Refactor `captions.list` review-surface wording and empty-result handling helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/layer1-captions-wrapper-contract.md` while keeping US3 tests green

**Checkpoint**: All three user stories are independently functional and reviewable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and repository-wide regression protection.

- [X] T037 [P] Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/quickstart.md` against the implemented workflow and update any stale verification steps
- [X] T038 [P] Add any remaining shared regression coverage for `captions.list` contract drift in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`
- [X] T039 Run targeted YT-104 validation in `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_captions_contract.py`
- [X] T040 Run the full repository test suite in `/Users/ctgunn/Projects/youtube-mcp-server` with `python3 -m pytest` and resolve any failures before completion
- [X] T041 Run `ruff check .` in `/Users/ctgunn/Projects/youtube-mcp-server` and resolve any lint failures before completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1: Setup**: No dependencies; can start immediately.
- **Phase 2: Foundational**: Depends on Phase 1; blocks all user stories because the endpoint-specific validation seam and contract test surface must exist first.
- **Phase 3: User Story 1**: Depends on Phase 2; this is the MVP and should land first.
- **Phase 4: User Story 2**: Depends on Phase 2 and benefits from US1's wrapper metadata baseline, but remains independently testable.
- **Phase 5: User Story 3**: Depends on Phase 2 and benefits from US1 and US2 semantics settling, but remains independently testable.
- **Phase 6: Polish**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other user stories; it is the MVP slice.
- **User Story 2 (P2)**: Depends on the foundational validation seam and should reuse the metadata and wrapper structure stabilized in US1.
- **User Story 3 (P3)**: Depends on the foundational validation seam and should reuse the auth and selector semantics stabilized in US1 and US2.

### Within Each User Story

- Write Red tests first and verify they fail before implementation.
- Implement the minimum code and doc changes needed to satisfy the failing tests.
- Update reStructuredText docstrings for every new or changed Python function before the story is considered complete.
- Refactor only after story tests pass.
- Keep each story independently testable using its stated independent test criteria.
- Before marking the feature complete, run `python3 -m pytest` and `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.

### Dependency Graph

- `T001-T003` → `T004-T007` → `T008-T017` → `T018-T027` → `T028-T036` → `T037-T041`
- US2 and US3 should wait for the Phase 2 foundation and can overlap once the core US1 wrapper structure is stable.

## Parallel Opportunities

- **Setup**: `T002` and `T003`
- **Foundational**: `T004` and `T006`
- **US1**: `T008`, `T009`, `T010`, and `T011`
- **US2**: `T018`, `T019`, `T020`, and `T021`
- **US3**: `T028`, `T029`, `T030`, and `T031`
- **Polish**: `T037` and `T038`

## Parallel Example: User Story 1

```bash
# Run the US1 Red tasks in parallel:
Task: "T008 Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T009 Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T010 Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
Task: "T011 Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py"
```

## Parallel Example: User Story 2

```bash
# Run the US2 Red tasks in parallel:
Task: "T018 Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py"
Task: "T019 Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T020 Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T021 Add failing transport tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py"
```

## Parallel Example: User Story 3

```bash
# Run the US3 Red tasks in parallel:
Task: "T028 Add failing contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py"
Task: "T029 Add failing integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py"
Task: "T030 Add failing unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py"
Task: "T031 Add failing consumer-facing reviewability checks in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate US1 independently using the US1 unit, integration, transport, and contract tests.
5. Stop for review if only the MVP is needed.

### Incremental Delivery

1. Complete Setup + Foundational to establish the endpoint-specific validation base.
2. Deliver User Story 1 as the first usable `captions.list` wrapper increment.
3. Deliver User Story 2 to make auth and delegation reuse safe for higher layers.
4. Deliver User Story 3 to lock in reviewability, invalid-combination handling, and empty-success semantics.
5. Finish with repository-wide regression and lint validation.

### Parallel Team Strategy

1. One teammate completes Phase 1 and the shared Phase 2 contract setup.
2. After the Phase 2 checkpoint:
   - Teammate A drives US1 to stabilize the core wrapper shape.
   - Teammate B prepares US2 auth and delegation tests once the wrapper baseline exists.
   - Teammate C prepares US3 reviewability and empty-result tests once the wrapper baseline exists.
3. Rejoin for Phase 6 validation and cleanup.

## Notes

- `[P]` tasks touch different files or can proceed without waiting on incomplete sibling tasks.
- User story labels appear only on story-phase tasks.
- Every task includes an exact file path so it can be executed directly.
- The recommended MVP scope is **User Story 1**.
