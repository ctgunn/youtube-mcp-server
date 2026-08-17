# Tasks: YT-320 Playlist Video Transcript Aggregation

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), and [playlists-get-video-transcripts-contract.md](./contracts/playlists-get-video-transcripts-contract.md)

**Tests**: Tests are mandatory. Each story begins with failing tests, is implemented with the minimum code needed to pass, and ends with a behavior-preserving refactor. Feature completion also requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.

**Documentation**: Every new or modified Python function and test helper must have a reStructuredText docstring that documents purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the feature boundary and existing seams before adding tests or implementation.

- [X] T001 Verify the executable contract, source seams, and focused verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/contracts/playlists-get-video-transcripts-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish reusable deterministic test seams and public-contract expectations that every story depends on.

**⚠️ CRITICAL**: Complete this phase before beginning user-story implementation.

- [X] T002 [P] Add documented recording playlist-listing and timestamped-caption test helpers for bounded fan-out scenarios in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T003 [P] Add failing shared contract assertions for the reserved `playlists_getVideoTranscripts` name, strict schema, concrete descriptor requirement, and safe metadata boundary in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`

**Checkpoint**: Recording doubles and the failing public contract are ready; user-story work can now proceed in priority order.

---

## Phase 3: User Story 1 - Retrieve a Playlist's Available Transcripts (Priority: P1) 🎯 MVP

**Goal**: Return timestamped transcript outcomes for eligible videos in one bounded playlist response, preserving source order and reporting processing limits.

**Independent Test**: Invoke a descriptor with recording playlist and timestamped-caption handlers for a playlist with accessible, unavailable, and empty-caption videos; verify one exact playlist lookup, source-order outcomes, timestamped segments, no attempt for unavailable items, and a correct fan-out summary.

### Red - Tests for User Story 1

- [X] T004 [US1] Add failing unit tests for playlist identifier validation, default and 1–50 `maxResults` bounds, one exact playlist lookup, source-order outcomes, empty playlists, unavailable entries, capped attempts, and fan-out counts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T005 [P] [US1] Add failing contract tests for bounded playlist-transcript fan-out metadata, item/segment provenance, empty-result behavior, limit policy, and no-continuation policy in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`
- [X] T006 [P] [US1] Add a failing injected-descriptor integration test that verifies ordered timestamped transcript retrieval and the exact lower-handler calls in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green - Implementation for User Story 1

- [X] T007 [US1] Add the `playlists_getVideoTranscripts` constants, strict validator, safe error type, one-page playlist lookup adapter, ordered per-video outcome mapper, fan-out summary builder, handler, metadata builder, and descriptor builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`
- [X] T008 [US1] Export the new playlists transcript constants, validator, error type, handler, metadata builder, and descriptor builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`
- [X] T009 [US1] Register the concrete descriptor with injected playlist-item and timestamped-caption handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T010 [US1] Add or update reStructuredText docstrings for every new or modified production function and recording test helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T011 [US1] Run the focused P1 unit, contract, and injected-descriptor integration tests and make them pass in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Refactor - User Story 1

- [X] T012 [US1] Refactor duplicated playlist-item and fan-out-summary mapping while preserving the P1 contract and passing focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`

**Checkpoint**: `playlists_getVideoTranscripts` is independently usable for bounded, source-ordered transcript retrieval with successful and unavailable item outcomes.

---

## Phase 4: User Story 2 - Request a Preferred Transcript Language (Priority: P2)

**Goal**: Apply an explicit language preference or the configured-default-to-English fallback consistently to every eligible video without silently substituting another language.

**Independent Test**: Invoke the tool with recording handlers under explicit-language, configured-default, and no-configured-default conditions; verify the exact normalized language forwarded per eligible video and a safe unavailable outcome when that language is absent.

### Red - Tests for User Story 2

- [X] T013 [US2] Add failing unit tests for language-tag validation, explicit-language forwarding, configured default forwarding, English fallback forwarding, exact-language absence, and no other-language substitution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T014 [P] [US2] Add failing contract tests for explicit → configured default → English resolution, exact-match semantics, result-level language source, and the prohibition on changing the timestamped-caption tool's fallback policy in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`

### Green - Implementation for User Story 2

- [X] T015 [US2] Implement request-level language resolution and per-video exact-language forwarding to the injected timestamped-caption handler, preserving the existing timestamped-caption public behavior, in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`
- [X] T016 [US2] Inject configured transcript-language settings and safe configuration-error state into the playlists transcript descriptor registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T017 [US2] Add or update reStructuredText docstrings for the language-resolution code and affected test helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T018 [US2] Run the focused language unit and contract tests and make them pass in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`

### Refactor - User Story 2

- [X] T019 [US2] Refactor local language normalization and source-label handling without changing `transcripts_getTimestampedCaptions` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`

**Checkpoint**: Clients can request a preferred language or use a predictable configured-default-to-English flow, with exact matching and no silent substitution.

---

## Phase 5: User Story 3 - Understand Incomplete Caption Access (Priority: P3)

**Goal**: Preserve successful playlist transcripts while clearly and safely explaining unavailable, restricted, capacity-limited, and source-failed videos.

**Independent Test**: Invoke the tool with a playlist containing captionless, language-missing, access-restricted, quota-limited, source-failed, and accessible videos; verify a source-ordered per-video outcome for each and successful transcripts retained without sensitive details.

### Red - Tests for User Story 3

- [X] T020 [US3] Add failing unit tests for invalid request shapes, unavailable video entries, captionless videos, missing requested language, authorization, quota, source-unavailable, and upstream failures; verify safe per-video statuses, summary counts, and next-page limited indication in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T021 [P] [US3] Add failing contract tests for safe whole-request categories, per-video status taxonomy, safe recovery guidance, no sensitive fields in failed outcomes, and fan-out partial-result metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`
- [X] T022 [P] [US3] Add failing integration tests for mixed per-video successes and failures plus default-dispatcher discoverability in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Green - Implementation for User Story 3

- [X] T023 [US3] Implement sanitized playlist-level error translation, per-video caption-error translation, unavailable-video no-attempt behavior, partial-result continuation, and safe fan-out status counting in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`
- [X] T024 [US3] Add or update reStructuredText docstrings for every changed error-mapping, outcome-mapping, and test-helper function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T025 [US3] Run the focused partial-result, registration, and protocol-routing tests and make them pass in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Refactor - User Story 3

- [X] T026 [US3] Refactor safe per-video outcome construction and error-category translation while preserving mixed-result behavior and sanitized output in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`

**Checkpoint**: A valid playlist request retains every successful transcript and returns a safe, actionable per-video outcome for all unavailable or restricted videos.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile public documentation, verification guidance, quality gates, and regression evidence across all stories.

- [X] T027 [P] Reconcile the published tool catalog entry with the executable bounded fan-out, language, segment, and safe-outcome contract in `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`
- [X] T028 [P] Audit reStructuredText docstrings for all new or modified Python functions and test helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`
- [X] T029 Run every focused verification command in `/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/quickstart.md` and resolve failures in the affected files before final validation
- [X] T030 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failing test in the reported file before the feature is considered complete
- [X] T031 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every reported issue in the affected file before the feature is considered complete

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 Setup
  -> Phase 2 Foundational
      -> Phase 3 US1 (MVP)
          -> Phase 4 US2
              -> Phase 5 US3
                  -> Phase 6 Polish and full-suite validation
```

### User Story Dependencies

- **US1 (P1)**: Starts after the foundational recording and contract seams. It delivers the concrete bounded fan-out endpoint and is the suggested MVP.
- **US2 (P2)**: Depends on US1's concrete handler and descriptor. It extends that handler with request-level language resolution rather than changing the existing timestamped-caption contract.
- **US3 (P3)**: Depends on the concrete handler from US1 and retains the language behavior completed in US2. It adds safe partial-result and error semantics across the same playlists-family module.

The story phases are intentionally sequential because US1–US3 modify the same public handler in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`. Their independently testable acceptance evidence remains isolated by priority and phase.

### Parallel Opportunities

- **Foundation**: T002 and T003 can proceed in parallel because they modify separate test files.
- **US1 Red tests**: T005 and T006 can proceed in parallel with each other after T004's unit test scope is established.
- **US2 Red tests**: T013 and T014 can proceed in parallel because they modify separate test files.
- **US3 Red tests**: T021 and T022 can proceed in parallel after T020 establishes the unit-test scenarios.
- **Polish**: T027 and T028 can proceed in parallel because they modify different documentation and source/test files.

## Parallel Execution Examples

### User Story 1

```text
Task: "T005 Add bounded fan-out metadata and provenance contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py"
Task: "T006 Add injected-descriptor retrieval integration test in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py"
```

### User Story 2

```text
Task: "T013 Add language-resolution unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py"
Task: "T014 Add language policy contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py"
```

### User Story 3

```text
Task: "T021 Add safe error taxonomy contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py"
Task: "T022 Add mixed-outcome registration integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete all Red, Green, and Refactor tasks in Phase 3.
3. Validate the P1 independent test: one bounded playlist lookup, source-order outcomes, timestamped segments, no caption attempt for unavailable videos, and an accurate fan-out summary.
4. Demo or deploy the bounded transcript aggregation MVP before extending language and partial-access semantics.

### Incremental Delivery

1. Setup + Foundational: deterministic recording seams and the public contract are ready.
2. US1: deliver bounded playlist transcript aggregation and independently validate it.
3. US2: add predictable exact-language selection and independently validate it without changing the timestamped-caption tool's contract.
4. US3: add safe mixed-access partial results and independently validate them.
5. Polish: reconcile documentation, run focused checks, then run the full repository test suite and lint check after the final code changes.

## Notes

- `[P]` tasks modify different files and can proceed concurrently once their stated prerequisite is complete.
- `[US1]`, `[US2]`, and `[US3]` labels provide user-story traceability.
- Every story must demonstrate failing tests before its implementation, passing focused tests after its implementation, docstring compliance, and behavior-preserving refactoring.
- Targeted checks are not final completion evidence; T030 and T031 are mandatory after the final code changes.
