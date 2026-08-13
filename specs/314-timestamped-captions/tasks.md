# Tasks: Timestamped Caption Retrieval

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/314-timestamped-captions/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contract](./contracts/transcripts-get-timestamped-captions-contract.md), and [quickstart.md](./quickstart.md)

**Tests**: Tests are mandatory. Write and demonstrate failing tests before each implementation increment, then retain focused passing evidence. Final completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` to pass after all changes. Every new or modified Python function requires a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each increment has a clear independent verification target. The stories extend the same public tool and source module, so P2 and P3 follow the P1 foundation rather than changing the same files concurrently.

## Phase 1: Setup

**Purpose**: Confirm the existing project seams and verification commands before modifying the additive public tool. No new dependency, configuration setting, persistence, provider, or transport is needed.

- [X] T001 Confirm the existing transcript-family, caption-list/download, dispatcher, and focused verification seams against `/Users/ctgunn/Projects/youtube-mcp-server/specs/314-timestamped-captions/plan.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/314-timestamped-captions/quickstart.md` before editing code.

---

## Phase 2: Foundational Protocol Routing

**Purpose**: Ensure the new public `language_unavailable` error category can be safely rendered by MCP routing before any story emits it.

**⚠️ CRITICAL**: Complete this phase before beginning the user-story phases.

- [X] T002 Add a failing `language_unavailable` Layer 3 routing case with sanitized-detail assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T003 Add the minimal `language_unavailable` protocol-category mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` so the T002 route returns a numeric safe MCP error.
- [X] T004 Run `PYTHONPATH=src python3 -m pytest tests/unit/test_method_routing.py`, refactor only the new routing coverage if needed, and keep existing protocol mappings unchanged in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`.

**Checkpoint**: Safe protocol routing is ready; timestamped-caption behavior can now be added.

---

## Phase 3: User Story 1 - Retrieve Timed Caption Segments (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client retrieve one video’s authorized caption track as ordered VTT-derived segments with explicit start and end elapsed seconds.

**Independent Test**: Invoke `transcripts_getTimestampedCaptions` with only a valid `videoId` and injected authorized caption doubles. Verify one list request, at most one VTT download, a selected usable source track, and one output segment per valid source cue with preserved order, timing, and cleaned text.

### Red - Tests for User Story 1

- [X] T005 [P] [US1] Add failing VTT segment unit tests for trimmed `videoId`, one list call, one VTT download, hour/decimal timing, adjacent/overlapping cues, blank cue text, markup removal, source order, and no partial result on malformed content in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T006 [P] [US1] Add failing public-descriptor contract tests for the required-only schema, both caption dependencies, boundedness, segment timing/provenance metadata, quota/auth caveats, and absence of `representativeOnly` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.
- [X] T007 [P] [US1] Add a failing descriptor-dispatch integration test that records exactly one caption listing and one `tfmt: vtt` download and validates timed segments in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Implementation for User Story 1

- [X] T008 [US1] Add the `transcripts_getTimestampedCaptions` constants, safe error type, required-`videoId` validator, source-order usable-track selection for omitted language, UTF-8 VTT cue parser, normalized segment result builder, and lower-layer error translation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py` to pass T005.
- [X] T009 [US1] Add executable timestamped-caption metadata and the MCP tool descriptor, including composition kind, one-list/at-most-one-download bound, VTT timing units, source-granularity policy, provenance, quota/auth notes, and safe recovery guidance, in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py` to pass T006.
- [X] T010 [US1] Export the timestamped-caption constants, error type, validator, handler, metadata builder, and descriptor from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`.
- [X] T011 [US1] Register the timestamped-caption descriptor with the existing OAuth caption-list and caption-download handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` to pass T007.
- [X] T012 [US1] Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py` and any changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

### Refactor - User Story 1

- [X] T013 [US1] Run `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_composed_transcripts.py tests/contract/test_youtube_composed_transcripts_contract.py tests/integration/test_youtube_composed_tool_registration.py`, refactor only duplicated VTT parsing or result-shaping logic in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, and keep all focused tests green.

**Checkpoint**: The MVP returns a default selected track’s timed source cues and is independently demonstrable.

---

## Phase 4: User Story 2 - Retrieve a Requested Language (Priority: P2)

**Goal**: Let a client request one exact accessible caption language without receiving a substituted language.

**Independent Test**: Invoke the P1 tool with an explicit valid language against several source tracks. Verify an exact usable match is downloaded and identified; an unavailable requested language produces `language_unavailable` and makes no download.

### Red - Tests for User Story 2

- [X] T014 [P] [US2] Add failing unit tests for language normalization, invalid/blank language rejection, exact explicit matching, failed-track exclusion, multiple same-language candidates, unavailable requested language, and no other-language download in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T015 [P] [US2] Add failing contract tests for optional `language`, exact-match/no-substitution policy, language selection source, `language_unavailable` guidance, and selected-language provenance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.

### Green - Implementation for User Story 2

- [X] T016 [US2] Extend timestamped-caption argument validation, track selection, result shaping, error mapping, metadata, and descriptor behavior for explicit exact-language selection and `language_unavailable` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.
- [X] T017 [US2] Add or update reStructuredText docstrings for every Python function modified for language validation or selection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.

### Refactor - User Story 2

- [X] T018 [US2] Run `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_composed_transcripts.py tests/contract/test_youtube_composed_transcripts_contract.py`, refactor selection helpers only where they preserve the documented source-order fallback and exact-language behavior, and keep focused tests green.

**Checkpoint**: P1 timed retrieval and P2 explicit-language retrieval both work without returning an unintended language.

---

## Phase 5: User Story 3 - Understand Unavailable or Restricted Captions (Priority: P3)

**Goal**: Let clients distinguish completed absence, restricted access, quota/source problems, and malformed caption content without exposing protected data.

**Independent Test**: Exercise empty listings, unavailable requested language, authorization denial, quota exhaustion, source unavailability, malformed/undecodable VTT, and unexpected lower-layer failures. Verify each documented result or error category is distinct, safe, and contains no caption data or sensitive diagnostic details.

### Red - Tests for User Story 3

- [X] T019 [P] [US3] Add failing unit tests for completed empty listings, no-download absence behavior, authorization/quotas/source error translation, malformed or undecodable VTT, unexpected failure, and detail sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T020 [P] [US3] Add failing contract tests for `no_accessible_captions`, authorization-sensitive, quota, source-unavailable, and upstream-failure result/error semantics and safe metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.
- [X] T021 [P] [US3] Add a failing integration test for restricted or malformed lower-layer behavior through the timestamped-caption descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.
- [X] T022 [P] [US3] Add a failing default-catalog registration and invocation/error-routing regression test for `transcripts_getTimestampedCaptions` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green - Implementation for User Story 3

- [X] T023 [US3] Finalize timestamped-caption empty-listing, access/quota/source-failure, malformed-VTT, and safe-detail behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`; return `no_accessible_captions` only for a completed empty listing without explicit language and never return partial segments after a failed download.
- [X] T024 [US3] Add or update reStructuredText docstrings for every Python function changed while implementing safe unavailable, restricted, and malformed-content outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.

### Refactor - User Story 3

- [X] T025 [US3] Run `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_composed_transcripts.py tests/contract/test_youtube_composed_transcripts_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py tests/unit/test_method_routing.py`, refactor duplicate safe-error mapping only in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, and keep all focused tests green.

**Checkpoint**: All three user stories are independently verifiable, with caller-safe access and failure behavior.

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Validate the released public contract, documentation, code quality, and repository-wide regression state.

- [X] T026 Reconcile the completed tool’s discovery metadata, result examples, error categories, and selection/timing behavior with `/Users/ctgunn/Projects/youtube-mcp-server/specs/314-timestamped-captions/contracts/transcripts-get-timestamped-captions-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/314-timestamped-captions/quickstart.md`.
- [X] T027 Run `PYTHONPATH=src python3 -m pytest`, fix every failure caused by the feature in `/Users/ctgunn/Projects/youtube-mcp-server/src/` or `/Users/ctgunn/Projects/youtube-mcp-server/tests/`, and rerun until the full repository suite passes.
- [X] T028 Run `PYTHONPATH=src python3 -m ruff check .`, fix every reported feature-related issue in `/Users/ctgunn/Projects/youtube-mcp-server/src/` or `/Users/ctgunn/Projects/youtube-mcp-server/tests/`, then rerun both `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` for final passing evidence.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately.
- **Phase 2 (Foundational)**: Depends on T001 and blocks all user stories because `language_unavailable` must route safely.
- **Phase 3 (US1)**: Depends on T004; delivers the MVP timed-segment path.
- **Phase 4 (US2)**: Depends on T013 because it extends the P1 parser/handler and public descriptor in the same source module.
- **Phase 5 (US3)**: Depends on T018 because it completes the P1/P2 tool’s safe results and error behavior.
- **Phase 6 (Polish)**: Depends on T025.

### User Story Completion Order

```text
Foundational protocol routing
        │
        ▼
US1: timed VTT segments (MVP)
        │
        ▼
US2: explicit language selection
        │
        ▼
US3: safe unavailable/restricted outcomes
        │
        ▼
Cross-cutting validation
```

### Parallel Opportunities

- In US1, T005, T006, and T007 can be written in parallel because they modify separate unit, contract, and integration test modules.
- In US2, T014 and T015 can be written in parallel because they modify separate unit and contract test modules.
- In US3, T019, T020, T021, and T022 can be written in parallel because they modify separate unit, contract, and integration test modules.
- Green implementation tasks are intentionally sequential where they edit the same public transcript-family module or depend on a prior exported/registered descriptor.

## Parallel Execution Examples

### User Story 1

```text
T005: tests/unit/test_youtube_composed_transcripts.py
T006: tests/contract/test_youtube_composed_transcripts_contract.py
T007: tests/integration/test_youtube_composed_tool_registration.py
```

### User Story 2

```text
T014: tests/unit/test_youtube_composed_transcripts.py
T015: tests/contract/test_youtube_composed_transcripts_contract.py
```

### User Story 3

```text
T019: tests/unit/test_youtube_composed_transcripts.py
T020: tests/contract/test_youtube_composed_transcripts_contract.py
T021: tests/integration/test_youtube_composed_tool_registration.py
T022: tests/integration/test_youtube_tool_registration.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T004 to establish safe protocol routing.
2. Complete T005–T013 to deliver a default selected caption track as ordered timed VTT segments.
3. Run the US1 focused suite from T013 and demonstrate the P1 independent test before extending the public tool.

### Incremental Delivery

1. Add US1 timed-segment retrieval and verify it independently.
2. Add US2 exact explicit-language selection without cross-language fallback and verify it independently.
3. Add US3 safe absence, access, quota, source, and malformed-content outcomes and verify it independently.
4. Complete T026–T028 before considering the feature complete.

## Notes

- All 28 tasks use the required checkbox, sequential ID, optional parallel marker, story label where required, and absolute file path format.
- `[P]` marks only tasks that can proceed simultaneously without editing the same file or depending on incomplete work.
- Do not mark a Red task complete until its expected failure is observed.
- Do not treat targeted test runs as final completion evidence; T027 and T028 are required.
