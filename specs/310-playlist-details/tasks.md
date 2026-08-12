# Tasks: YT-310 Playlist Details

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/data-model.md), and [playlists-get-playlist-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/contracts/playlists-get-playlist-contract.md)

**Tests**: Tests are mandatory. Each story starts with failing tests, reaches the smallest passing implementation, then refactors with focused checks. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` after the final code change. Every new or modified Python function, including test helpers and doubles, requires a reStructuredText docstring.

**Organization**: Tasks are grouped by prioritized user story. The P2 and P3 behavior extends the same public descriptor introduced by P1, so those phases are incremental contract additions rather than competing implementations.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing implementation seams and establish the feature's test baseline without creating new infrastructure.

- [X] T001 Reconcile the fixed one-lookup request, normalized field list, safe-error taxonomy, and rollback boundary across `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/contracts/playlists-get-playlist-contract.md`
- [X] T002 [P] Run the existing dependent-layer regression baseline in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlists_registration.py` with `PYTHONPATH=src python3 -m pytest`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify the existing composed-tool and protocol seams that every YT-310 behavior will use.

**⚠️ CRITICAL**: Complete this phase before modifying the composed playlists family.

- [X] T003 [P] Verify the analogous concrete-descriptor, export, and default-registration conventions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T004 [P] Verify safe Layer 3 error serialization and lower-layer detail sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

**Checkpoint**: The one-read `playlists_list` dependency, composed-tool registration seam, and safe protocol-routing seam are confirmed; P1 implementation can begin.

---

## Phase 3: User Story 1 - Retrieve Playlist Details (Priority: P1) 🎯 MVP

**Goal**: An MCP client can submit one `playlistId` and receive normalized public details for exactly one accessible playlist, with sparse source values omitted rather than fabricated.

**Independent Test**: Inject a controlled direct playlist lookup, call `playlists_getPlaylist` with a valid identifier, and verify exactly one request using `snippet,contentDetails,status` returns all available normalized public fields; repeat with sparse metadata and verify no substitutes appear.

### Red - Tests for User Story 1

- [X] T005 [P] [US1] Add failing validation, exact-one-lookup, full field-mapping, and sparse-metadata unit tests with reStructuredText docstrings for all new test helpers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T006 [P] [US1] Add failing MCP contract tests for the one-field input schema, normalized playlist field mapping, one-read `playlists.list` boundary, and additive compatibility in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`
- [X] T007 [P] [US1] Add a failing injected-descriptor registration-and-execution test with reStructuredText docstrings for new test helpers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green - Implementation for User Story 1

- [X] T008 [US1] Implement the `playlists_getPlaylist` constants, input schema, safe public error type, `playlistId` validator, fixed lower-layer argument builder, available-field normalizer, one-lookup handler, and concrete descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`
- [X] T009 [US1] Export the concrete playlist-detail symbols and default-register `playlists_getPlaylist` with an injected `build_playlists_list_handler(**conditional_dependencies)` lookup in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T010 [US1] Add or update reStructuredText docstrings for every new or modified Python function and class in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Refactor - User Story 1

- [X] T011 [US1] Refactor only duplicated playlist field extraction or request-building logic while preserving the one-read behavior, then run the focused P1 checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

**Checkpoint**: `playlists_getPlaylist` is usable as an independently testable MVP for populated and sparse publicly available playlists.

---

## Phase 4: User Story 2 - Interpret Playlist Details for Research (Priority: P2)

**Goal**: A client can identify source-preserved versus normalized values, understand request-time variability, and see that playlist video entries require `playlists_getPlaylistItems`.

**Independent Test**: Inspect discovery metadata and one successful result and verify field provenance, one-playlist boundedness, public-content scope, request-time state wording, and explicit guidance to the playlist-items tool without any entry data.

### Red - Tests for User Story 2

- [X] T012 [P] [US2] Add failing contract assertions for provenance categories, normalized retrieval metadata, no representative-only marker, public-content caveats, request-time variability, and playlist-items guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`
- [X] T013 [P] [US2] Add failing injected-descriptor assertions that a successful result contains `fieldProvenance` and `contentScope` but no playlist entries, with reStructuredText docstrings for new helpers, in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green - Implementation for User Story 2

- [X] T014 [US2] Extend playlist normalization and discovery metadata to return coherent `fieldProvenance` and `contentScope`, disclose request-time public state and the `playlists_getPlaylistItems` handoff, and keep all item data out of the result in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`
- [X] T015 [US2] Add or update reStructuredText docstrings for every Python function or class modified for provenance and scope behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Refactor - User Story 2

- [X] T016 [US2] Reconcile provenance keys, scope wording, and discovery metadata with `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/contracts/playlists-get-playlist-contract.md`, then run the focused P2 contract and integration checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

**Checkpoint**: Clients can interpret the returned playlist detail correctly and are not led to treat it as a playlist-item listing.

---

## Phase 5: User Story 3 - Receive Safe Outcomes for Unavailable Playlists (Priority: P3)

**Goal**: A client receives safe, actionable categories for invalid, unavailable, authorization-sensitive, capacity, and source-service outcomes without private playlist data or diagnostics.

**Independent Test**: Exercise invalid arguments, empty and malformed lookup results, and each lower-layer failure category through the descriptor and MCP router; verify category mapping, recovery-safe details, and absence of credentials, raw payloads, traces, and private context.

### Red - Tests for User Story 3

- [X] T017 [P] [US3] Add failing unit tests for invalid object, missing, blank, non-text, and unknown inputs; generic unavailable empty or malformed results; lower-layer category translation; and secret-detail removal in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T018 [P] [US3] Add failing contract assertions for every safe public error category and caller recovery guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`
- [X] T019 [P] [US3] Add a failing MCP routing regression that serializes a playlist-detail capacity failure without unsafe details, with reStructuredText docstrings for all new helpers, in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Green - Implementation for User Story 3

- [X] T020 [US3] Implement generic unavailable-result handling and sanitized `PlaylistsListToolError` translation to `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`
- [X] T021 [US3] Add or update reStructuredText docstrings for every Python function, error class, and new test helper modified for validation or safe-error behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Refactor - User Story 3

- [X] T022 [US3] Refactor duplicated safe-error mapping only after the failure-path tests pass, preserve public error categories and sanitization, and run the focused P3 checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

**Checkpoint**: Every documented failure outcome is safe, machine-readable, and independently verified through the MCP route.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete additive tool without expanding scope.

- [X] T023 [P] Run the focused end-to-end feature command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T024 [P] Review the implemented discovery output and result examples against `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/contracts/playlists-get-playlist-contract.md` and update only verified documentation drift in that contract or `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/quickstart.md`
- [X] T025 Review all changed Python symbols for complete reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the changed `/Users/ctgunn/Projects/youtube-mcp-server/tests/` files
- [X] T026 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve every issue in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and affected `/Users/ctgunn/Projects/youtube-mcp-server/tests/` files
- [X] T027 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` after the final code change and fix every failure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and affected `/Users/ctgunn/Projects/youtube-mcp-server/tests/` files before completing the feature

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 has no dependencies and establishes the implementation baseline.
- Phase 2 depends on Phase 1 and confirms the existing seams used by all work.
- Phase 3 delivers the P1 executable descriptor and is the MVP.
- Phase 4 depends on the P1 descriptor because it extends that descriptor's result and discovery contract.
- Phase 5 depends on the P1 descriptor and may begin after Phase 3; it can proceed alongside Phase 4 except where both changes touch `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` or the same test file.
- Phase 6 depends on all desired story phases.

### User Story Completion Graph

```text
Setup → Foundational → US1 (P1 MVP) → US2 (P2 interpretation)
                                  └──→ US3 (P3 safe outcomes)
US2 + US3 → Polish and full-suite verification
```

### Within Each User Story

- Red tests must be added and observed failing before the corresponding Green implementation begins.
- Green implementation is limited to the behavior required for that story's tests.
- ReStructuredText docstrings are completed before Refactor.
- Refactor happens only after focused tests pass and preserves existing public contracts.

### Parallel Opportunities

- T003 and T004 can run in parallel after the Phase 1 baseline check T002 completes.
- T005, T006, and T007 can run in parallel because they modify distinct test files.
- T012 and T013 can run in parallel because they modify distinct test files.
- T017, T018, and T019 can run in parallel because they modify distinct test files.
- T023 and T024 can run in parallel after all story work is complete.

## Parallel Execution Examples

### User Story 1

```text
Task: "T005 Add unit Red tests in tests/unit/test_youtube_composed_playlists.py"
Task: "T006 Add contract Red tests in tests/contract/test_youtube_composed_playlists_contract.py"
Task: "T007 Add integration Red tests in tests/integration/test_youtube_composed_tool_registration.py"
```

### User Story 2

```text
Task: "T012 Add provenance contract Red tests in tests/contract/test_youtube_composed_playlists_contract.py"
Task: "T013 Add scope integration Red tests in tests/integration/test_youtube_composed_tool_registration.py"
```

### User Story 3

```text
Task: "T017 Add safe-error unit Red tests in tests/unit/test_youtube_composed_playlists.py"
Task: "T018 Add error-contract Red tests in tests/contract/test_youtube_composed_playlists_contract.py"
Task: "T019 Add protocol routing Red tests in tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1 and 2 to confirm the existing seams.
2. Complete Phase 3 in Red-Green-Refactor order.
3. Run the focused P1 checks and demonstrate one populated and one sparse playlist lookup.
4. Stop here if the normalized core retrieval is the only required release increment.

### Incremental Delivery

1. Add P1 core playlist retrieval and validate it independently.
2. Add P2 provenance and playlist-item scope guidance, then validate the client interpretation contract.
3. Add P3 safe failure handling and protocol-routing coverage.
4. Complete polish, lint, and full-suite validation only after the final code change.

### Notes

- Every task uses the required checkbox, sequential ID, optional parallel marker, story label where applicable, and exact path format.
- Do not introduce new persistence, clients, pagination, playlist-item traversal, ranking, or transport behavior while completing these tasks.
- Never treat focused checks as final completion evidence; T027 requires the complete repository test suite to pass.
