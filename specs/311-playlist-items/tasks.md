# Tasks: YT-311 Playlist Items

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/data-model.md), and [contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/contracts/playlists-get-playlist-items-contract.md)

**Tests**: Tests are mandatory. Start each story by adding failing tests, implement only the behavior needed to pass them, then refactor with focused tests green. After final code changes, `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` must both pass.

**Documentation**: Every new or modified Python function, including nested handlers and test doubles, must have a reStructuredText docstring with relevant `:param:`, `:return:`, `:raises:`, and side-effect documentation.

## Phase 1: Setup

**Purpose**: Confirm the feature boundary and establish reproducible test evidence before changes.

- [X] T001 Review the accepted one-read, source-order, availability, and safe-error decisions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/{plan.md,research.md,data-model.md,contracts/playlists-get-playlist-items-contract.md}` before editing code.
- [X] T002 Run and record the pre-change focused baseline for `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

---

## Phase 2: Foundational Descriptor Exposure

**Purpose**: Establish the additive executable tool, public schema, exports, and default registration that all stories require.

**⚠️ CRITICAL**: Complete this phase before user-story implementation; it creates the public MCP delivery seam.

- [X] T003 Add failing concrete-discovery and default-registration regression tests for `playlists_getPlaylistItems` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T004 Implement the minimal tool-name constant, public input schema, executable descriptor, composed-package exports, and default dispatcher registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` so the new descriptor is concrete rather than representative-only.
- [X] T005 Add or update reStructuredText docstrings for every Python function changed by the foundational descriptor and registration work in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T006 Refactor only the foundational descriptor/export/registration changes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/{youtube_composed/playlists.py,youtube_composed/__init__.py,dispatcher.py}` after T003 passes, preserving existing tool registrations and rerunning the focused registration tests.

**Checkpoint**: The concrete tool is discoverable through the default dispatcher and ready for story-local behavior.

---

## Phase 3: User Story 1 - Retrieve Videos in a Playlist (Priority: P1) 🎯 MVP

**Goal**: Return an ordered, concise collection for one playlist using exactly one lower-layer lookup.

**Independent Test**: Inject a controlled playlist-item lookup, invoke `playlists_getPlaylistItems` with a valid `playlistId`, and verify one exact `snippet,contentDetails,status` lookup plus ordered normalized video summaries and count/provenance context.

### Red Tests

- [X] T007 [US1] Add failing validation, exact lower-request, populated-item mapping, sparse-item mapping, source-order preservation, and returned-count unit tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.
- [X] T008 [US1] Add failing public-contract tests for source-ordered collection metadata, `playlistItems.list` as the sole dependency, normalized item fields, provenance, and no representative-only marker in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`.
- [X] T009 [US1] Add a failing injected-descriptor execution test proving one ordered result is callable through the MCP dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green Implementation

- [X] T010 [US1] Implement strict `playlistId` validation, one lower-layer request builder using `part=snippet,contentDetails,status`, ordered playlist-item normalization, returned-count calculation, collection context, field provenance, metadata, and handler behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T011 [US1] Add or update reStructuredText docstrings for every new or modified validator, request builder, item normalizer, handler, descriptor helper, and test double in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/{unit/test_youtube_composed_playlists.py,integration/test_youtube_composed_tool_registration.py}`.

### Refactor and Verification

- [X] T012 [US1] Refactor local source-field extraction and provenance construction without changing the one-read or source-order contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, then rerun the US1 unit, contract, and integration tests.

**Checkpoint**: A valid playlist can be retrieved as a normalized ordered collection without relying on P2 limit behavior or P3 safe-failure mapping.

---

## Phase 4: User Story 2 - Bound Playlist Research (Priority: P2)

**Goal**: Let callers choose a bounded first-page result size while clearly understanding the applied limit and whether the source indicates more entries.

**Independent Test**: Invoke the tool with omitted, minimum, and maximum `maxResults` values against a controlled lookup and verify the lower request uses 25, 1, and 50 respectively, never accepts continuation input, and returns the documented applied-limit and limited-result fields.

### Red Tests

- [X] T013 [US2] Add failing unit tests for default `maxResults=25`, accepted 1 and 50 boundaries, rejection of zero, values above 50, booleans, fractions, strings, unknown fields, and lower-request limit propagation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.
- [X] T014 [US2] Add failing contract tests for the default, 1–50 bounds, one-page/no-continuation behavior, source-signaled `isLimited` semantics, and no-ranking collection context in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`.

### Green Implementation

- [X] T015 [US2] Implement Layer 3 limit normalization, default application, strict type/range rejection, applied-limit result context, and source-signaled `isLimited` calculation without pagination traversal in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T016 [US2] Add or update reStructuredText docstrings for all limit validators, limited-result helpers, modified handler paths, and US2 test helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.

### Refactor and Verification

- [X] T017 [US2] Refactor repeated limit and collection-context construction in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, retain the no-continuation boundary, and rerun the US2 unit and contract tests.

**Checkpoint**: Callers can independently use default or explicit bounded playlist retrieval and understand whether the one response is limited.

---

## Phase 5: User Story 3 - Understand Unavailable Results (Priority: P3)

**Goal**: Distinguish successful empty collections, unavailable exposed entries, and safe whole-request failures without leaking private or raw source detail.

**Independent Test**: Use controlled successful and failing lower-layer outcomes to verify an empty collection succeeds, unavailable entries remain ordered and labeled, and invalid, unavailable, access, capacity, and upstream failures return only documented safe categories and sanitized details.

### Red Tests

- [X] T018 [US3] Add failing unit tests for successful empty collections, malformed exposed entries, retained unavailable entries, no fabricated details, and safe translation/sanitization of every lower-layer error category in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`.
- [X] T019 [US3] Add failing contract tests for empty-collection, unavailable-entry, safe-error-category, recovery-guidance, and unsafe-metadata exclusion rules in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`.
- [X] T020 [US3] Add failing integration and protocol-routing regression tests for dispatcher invocation and serialized safe `playlists_getPlaylistItems` errors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

### Green Implementation

- [X] T021 [US3] Implement availability-state normalization that retains every exposed source item, successful empty-result shaping, local `PlaylistItemsListToolError` translation to the Layer 3 safe taxonomy, and sanitized error details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`.
- [X] T022 [US3] Add or update reStructuredText docstrings for all error classes, error mappers, availability helpers, changed handlers, and US3 test doubles in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/{unit/test_youtube_composed_playlists.py,integration/test_youtube_composed_tool_registration.py,unit/test_method_routing.py}`.

### Refactor and Verification

- [X] T023 [US3] Refactor local safe-error and availability-state logic in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` while preserving sanitization and source order, then rerun the US3 unit, contract, integration, and routing tests.

**Checkpoint**: Empty, unavailable-entry, and whole-request failure outcomes are independently testable and safely distinguishable under the public contract.

---

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Verify the delivered behavior against the accepted contract and constitution gates.

- [X] T024 [P] Reconcile the implemented discovery schema, result fields, availability semantics, and error guidance with `/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/contracts/playlists-get-playlist-items-contract.md` and update contract tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py` if a testable documented clause is missing.
- [X] T025 [P] Execute the review scenarios and commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/quickstart.md`, recording evidence for populated, sparse, empty, limited, unavailable-entry, invalid-input, and safe-error outcomes.
- [X] T026 Review every changed Python function and test helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the modified test files for complete reStructuredText docstrings.
- [X] T027 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failure in the affected source or test file before declaring the feature complete.
- [X] T028 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every reported issue in the affected source or test file before declaring the feature complete.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately.
- **Phase 2 (Foundational Descriptor Exposure)**: Depends on Phase 1 and blocks all user-story work because it exposes the executable public tool.
- **Phase 3 (US1)**: Depends on Phase 2; delivers the MVP retrieval increment.
- **Phase 4 (US2)**: Depends on the US1 handler seam; extends it with caller-controlled limits.
- **Phase 5 (US3)**: Depends on the US1 handler seam; it can begin after Phase 3 and may proceed in parallel with Phase 4 if changes to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` are coordinated.
- **Phase 6 (Polish)**: Depends on all desired user stories being complete.

### User Story Completion Order

```text
Foundational descriptor exposure
        │
        ▼
US1: ordered playlist retrieval (MVP)
        ├──────────────► US2: bounded retrieval
        └──────────────► US3: safe unavailable outcomes
                              │
                              ▼
                      Polish and full-suite validation
```

### Within Each User Story

- Write and run the Red tests first; confirm they fail for the absent behavior.
- Implement only the Green behavior necessary to satisfy that story’s tests.
- Add or update all required reStructuredText docstrings before the story is marked complete.
- Refactor only after the story tests pass; rerun its focused test set after refactoring.

## Parallel Opportunities

- T003’s contract and integration assertions can be split by file if separate implementers coordinate the shared expected metadata.
- Within US1, T007, T008, and T009 affect different test files and can be prepared in parallel before T010.
- Within US2, T013 and T014 affect different test files and can be prepared in parallel before T015.
- Within US3, T018, T019, and T020 can be prepared in parallel before T021 because they affect different test files.
- After US1 is complete, US2 and US3 test design can proceed in parallel; serialize changes to the shared playlists module during implementation.
- T024 and T025 can run in parallel after all feature behavior is in place.

## Parallel Example: User Story 1

```text
Task: "Add failing unit retrieval and order tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py"
Task: "Add failing contract metadata tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py"
Task: "Add failing dispatcher execution test in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py"
```

## Parallel Example: User Story 3

```text
Task: "Add failing availability and safe-error unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py"
Task: "Add failing empty/error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py"
Task: "Add failing dispatcher and routing error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational Descriptor Exposure.
2. Complete US1 through T012.
3. Validate the US1 independent test criterion: one exact lower-layer listing returns a source-ordered normalized collection.
4. Demonstrate the additive MCP tool before adding limit and unavailable-outcome refinements.

### Incremental Delivery

1. Deliver US1 for basic ordered playlist retrieval.
2. Add US2 to make result size explicit and bounded for research workflows.
3. Add US3 to make empty, unavailable-entry, and safe failure outcomes unambiguous.
4. Complete cross-cutting verification, docstring review, full tests, and lint before release.

## Notes

- All 28 tasks use the required checkbox, sequential ID, optional parallel marker, appropriate story label, and absolute file path format.
- `[US1]`, `[US2]`, and `[US3]` map directly to the P1, P2, and P3 stories in the feature specification.
- Do not expose raw lower-layer envelopes, continuation tokens, credentials, private owner context, stack traces, or non-public data while implementing these tasks.
