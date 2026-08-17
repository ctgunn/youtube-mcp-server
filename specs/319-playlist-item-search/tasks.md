# Tasks: Search Playlist Items

**Input**: Design documents from `/specs/319-playlist-item-search/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/playlists-search-items-contract.md](./contracts/playlists-search-items-contract.md), and [quickstart.md](./quickstart.md)

**Tests**: Tests are mandatory. Write and run the named Red tests before the matching Green task. Completion requires passing `python3 -m pytest` and `python3 -m ruff check .` after the final code change. Every new or changed Python function, class, and test helper needs a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each increment has a stated independent test. YT-319 extends one public handler, so US2 and US3 build on US1's additive tool rather than duplicating it.

## Phase 1: Setup (Shared Planning Inputs)

**Purpose**: Confirm the existing playlist-family boundaries and use the finalized design artifacts as the implementation source of truth. No project scaffold or dependency installation is needed.

- [X] T001 [P] Reconcile affected playlist-family source and test paths with the implementation structure in `/Users/ctgunn/Projects/youtube-mcp-server/specs/319-playlist-item-search/plan.md`.
- [X] T002 [P] Use the request, result, error, coverage, and rollback rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/319-playlist-item-search/contracts/playlists-search-items-contract.md` as the acceptance contract for all subsequent tasks.

---

## Phase 2: Foundational (Public Tool Contract and Registry)

**Purpose**: Establish the additive public-tool declarations, common safe error boundary, and default registration that block all user-story behavior.

**⚠️ CRITICAL**: Complete this phase before implementing searchable results, result limits, or multi-page coverage.

- [X] T003 [P] Add failing discovery-contract tests for the `playlists_searchItems` strict input schema, composition boundary, safe error taxonomy, and no-token metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`.
- [X] T004 [P] Add failing default-registry discovery coverage asserting one concrete `playlists_searchItems` tool descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T005 Define `PLAYLISTS_SEARCH_ITEMS_*` constants, strict schema, safe error class, and discovery metadata shell in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` to satisfy the foundational contract tests without exposing an executable partial result.
- [X] T006 Export the concrete playlist-search public symbols in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and register its descriptor with existing injected playlist and playlist-item dependencies in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T007 Add or update reStructuredText docstrings for every new or modified Python class, function, and test helper introduced by T005-T006 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T008 Run the foundational contract and registry Red/Green tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, then refactor only duplicated declaration code while retaining passing tests.

**Checkpoint**: A discoverable, additive, safely described descriptor exists; user-story behavior can now be added to it.

---

## Phase 3: User Story 1 - Search a Known Playlist (Priority: P1) 🎯 MVP

**Goal**: An MCP client can search one accessible playlist and receive only literal phrase matches in playlist order, with the fields that matched.

**Independent Test**: Invoke the registered descriptor with an accessible injected playlist and mixed matching/non-matching source items; verify every returned item matches title, description, channel title, or video identifier, is in source order, and identifies matching fields. A no-match playlist returns a successful empty collection.

### Red Tests for User Story 1

- [X] T009 [P] [US1] Add failing unit tests for required `playlistId` and `query`, trim/collapse query normalization, Unicode case-insensitive literal matching across all four searchable fields, deterministic matching-field order, source-order preservation, and no-match success in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.
- [X] T010 [P] [US1] Add failing contract tests for the P1 searchable fields, literal-only semantics, source-order policy, normalized response fields, and provenance metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`.
- [X] T011 [P] [US1] Add failing injected-descriptor integration coverage for one accessible playlist lookup plus matching/non-matching item results in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green Implementation for User Story 1

- [X] T012 [US1] Implement strict playlist-search argument validation, query normalization, accessible-playlist preflight, literal match-field detection, normalized matching-item shaping, source-order result assembly, and successful empty/no-match behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T013 [US1] Complete the public `playlists_searchItems` descriptor metadata and callable handler for the accessible one-page matching flow in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T014 [US1] Add or update reStructuredText docstrings for every Python class, function, nested handler, and test helper changed for P1 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.

### Refactor and Verify User Story 1

- [X] T015 [US1] Run the P1 unit, contract, and injected-descriptor tests from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`; refactor only duplicated validation, matching, or normalization helpers while keeping the tests green.

**Checkpoint**: `playlists_searchItems` delivers the independently useful MVP: explainable literal search for an accessible playlist in source order.

---

## Phase 4: User Story 2 - Bound a Search Result (Priority: P2)

**Goal**: An MCP client controls the number of returned matches and can tell whether observed additional matches were omitted.

**Independent Test**: Search an accessible injected playlist with more matches than the requested result limit; verify the default of 25, accepted 1-50 limits, returned count, applied limit, and `additionalMatchesOmitted` semantics.

### Red Tests for User Story 2

- [X] T016 [P] [US2] Add failing unit tests for default `maxResults`, valid 1-50 limits, invalid limit types and values, result truncation, and true/false/null `additionalMatchesOmitted` states in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.
- [X] T017 [P] [US2] Add failing contract tests for the default/maximum limit policy and tri-state omitted-match semantics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`.
- [X] T018 [P] [US2] Add failing injected-descriptor integration coverage for an explicit result limit that truncates observed matching items in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green Implementation for User Story 2

- [X] T019 [US2] Implement `maxResults` default and bounds, continue inspecting enough source items to establish omission semantics, and emit `appliedLimit`, `returnedCount`, and tri-state `additionalMatchesOmitted` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T020 [US2] Update the playlist-search discovery metadata, response provenance, and normalized result contract fields for limit behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T021 [US2] Add or update reStructuredText docstrings for every Python function, class, nested handler, and test helper changed for P2 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.

### Refactor and Verify User Story 2

- [X] T022 [US2] Run the P2 unit, contract, and injected-descriptor tests from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`; refactor only duplicated limit and result-state code while keeping the tests green.

**Checkpoint**: P1 search remains intact and P2 callers can request a bounded response with honest omission state.

---

## Phase 5: User Story 3 - Understand Search Coverage and Failures (Priority: P3)

**Goal**: An MCP client can distinguish complete no-match results from bounded coverage, unavailable playlists, invalid requests, unavailable items, and safe lower-layer failures.

**Independent Test**: Use injected paged item results and safe lower-layer failures to verify ten-page/500-entry traversal, complete versus capped coverage, accessible empty success, unavailable-item behavior, unavailable playlist outcome, and safe MCP error serialization.

### Red Tests for User Story 3

- [X] T023 [P] [US3] Add failing unit tests for page-by-page source-order traversal, terminal-page complete coverage, the 500-entry cap, repeated continuation detection, accessible-empty versus unavailable playlists, unavailable matching entries, and safe error-category mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.
- [X] T024 [P] [US3] Add failing contract tests for the ten-page/500-entry composite boundary, coverage object, no public continuation value, unavailable-entry policy, and all safe error categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`.
- [X] T025 [P] [US3] Add failing integration and protocol-routing tests for multi-page injected dependencies, default registry invocation, and sanitized structured errors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

### Green Implementation for User Story 3

- [X] T026 [US3] Implement private page-token traversal using the existing lower-layer playlist-item handler, stop at terminal pagination or 500 inspected entries, reject repeated private continuation values safely, and expose only normalized coverage state in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T027 [US3] Implement safe playlist-availability preflight and lower-layer error translation so empty accessible playlists succeed while unavailable, authorization-sensitive, quota, and upstream failures remain distinct safe outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T028 [US3] Finalize public descriptor registration dependencies and metadata for private multi-page composition without exposing continuation values in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T029 [US3] Add or update reStructuredText docstrings for every Python function, class, nested handler, and test helper changed for P3 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.

### Refactor and Verify User Story 3

- [X] T030 [US3] Run the P3 unit, contract, integration, and routing tests from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`; refactor only behavior-preserving traversal and safe-error helpers while keeping the tests green.

**Checkpoint**: All three stories are complete: results are explainable, bounded, coverage-aware, and safely failure-distinguishable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile final documentation and complete the mandatory full-repository quality gates.

- [X] T031 [P] Reconcile examples, result fields, matching semantics, coverage behavior, error guidance, and rollback note with the final executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/specs/319-playlist-item-search/contracts/playlists-search-items-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/319-playlist-item-search/quickstart.md`.
- [X] T032 [P] Review all changed Python production and test code for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T033 Run `python3 -m pytest` from the repository root `/Users/ctgunn/Projects/youtube-mcp-server` after the final code changes and fix every failing test before feature completion.
- [X] T034 Run `python3 -m ruff check .` from the repository root `/Users/ctgunn/Projects/youtube-mcp-server` after T033 and fix every reported violation before feature completion.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1: Setup
    ↓
Phase 2: Contract and registry foundation
    ↓
Phase 3: US1 — searchable playlist MVP
    ↓
Phase 4: US2 — bounded returned results
    ↓
Phase 5: US3 — bounded inspection and safe outcome distinctions
    ↓
Phase 6: Polish and full-suite gates
```

### User Story Dependencies

- **US1 (P1)**: Starts after the contract/registry foundation and is the MVP. It creates the callable search behavior that later stories extend.
- **US2 (P2)**: Starts after US1 because the same public handler must already produce matches before it can limit them. Its acceptance test is independent once US1 is available.
- **US3 (P3)**: Starts after US1 and can follow US2 sequentially to avoid concurrent edits to the same playlist handler. It adds private traversal and safe outcome distinctions without changing P1 matching semantics.

### Parallel Opportunities

- T001 and T002 can proceed together because they only read independent design artifacts.
- T003 and T004 can proceed together because they add Red tests in separate files.
- Within each story, its `[P]` test tasks can proceed together because they touch different test files.
- T031 and T032 can proceed together after all story work because they inspect separate documentation and code surfaces.

## Parallel Execution Examples

### User Story 1

```text
Task T009: Unit matching and validation Red tests in tests/unit/test_youtube_composed_playlists.py
Task T010: Contract metadata Red tests in tests/contract/test_youtube_composed_playlists_contract.py
Task T011: Injected descriptor Red tests in tests/integration/test_youtube_composed_tool_registration.py
```

### User Story 2

```text
Task T016: Unit limit and omission-state Red tests in tests/unit/test_youtube_composed_playlists.py
Task T017: Contract limit-policy Red tests in tests/contract/test_youtube_composed_playlists_contract.py
Task T018: Injected limit integration Red tests in tests/integration/test_youtube_composed_tool_registration.py
```

### User Story 3

```text
Task T023: Unit pagination, coverage, availability, and error Red tests in tests/unit/test_youtube_composed_playlists.py
Task T024: Contract coverage and safe-error Red tests in tests/contract/test_youtube_composed_playlists_contract.py
Task T025: Integration and MCP routing Red tests in tests/integration/ and tests/unit/test_method_routing.py
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 through T015.
3. Validate the US1 independent test: accessible playlist, literal matches only, matching fields, source order, and successful no-match result.
4. Demo the additive tool before adding result-limit and pagination refinements.

### Incremental Delivery

1. Deliver US1 as the explainable searchable-playlist MVP.
2. Deliver US2 to bound returned matches and make observed omission explicit.
3. Deliver US3 to add the ten-page/500-entry inspection bound, coverage state, unavailable-resource distinction, and sanitized failure routing.
4. Complete Phase 6 only after all desired stories are in place; targeted tests do not replace the full-suite gates.

## Format Validation

- All 34 tasks use the required checkbox, sequential `T###` identifier, optional `[P]` marker only for independent paths, and `[US#]` label on every user-story task.
- Every task description names one or more exact absolute file paths.
- User-story phases include Red tests before Green implementation, explicit reStructuredText docstring work, and a Refactor/verification task.
