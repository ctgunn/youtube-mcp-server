# Tasks: Transcript Search

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/315-transcript-search/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/transcripts-search-transcript-contract.md](./contracts/transcripts-search-transcript-contract.md), and [quickstart.md](./quickstart.md)

**Tests**: Test tasks are mandatory. Every story follows Red–Green–Refactor. Completion requires the final passing `PYTHONPATH=src python3 -m pytest` run and `PYTHONPATH=src python3 -m ruff check .` after all code changes. Every new or changed Python function requires a reStructuredText docstring.

**Organization**: Tasks are grouped by independently verifiable user story. The P1 concrete descriptor is the shared public capability; P2 and P3 add independently testable language and bounded/empty-search behavior to it.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing project seams and verification commands before introducing feature code.

- [X] T001 Run the existing transcript-focused baseline command from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py` and record the starting result for the feature work.
- [X] T002 [P] Review the accepted public fields, match states, and verification expectations in `/Users/ctgunn/Projects/youtube-mcp-server/specs/315-transcript-search/contracts/transcripts-search-transcript-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/315-transcript-search/quickstart.md` before writing tests.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify the reusable timestamped-caption dependency and existing safe MCP-category route that all story increments rely on.

**⚠️ CRITICAL**: Complete this phase before changing the public search tool.

- [X] T003 Verify the YT-314 timed-segment dependency contract and its one-list/at-most-one-download behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T004 [P] Verify that the documented `invalid_parameters`, `language_unavailable`, `authorization_sensitive_data`, `quota_exhaustion`, `source_unavailable`, and `upstream_failure` categories already serialize safely in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

**Checkpoint**: The timed-segment composition and safe MCP error route are confirmed; public search implementation can begin.

---

## Phase 3: User Story 1 - Find Relevant Transcript Moments (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client search one video's timestamped transcript and receive chronological segment-local matches with contextual snippets.

**Independent Test**: Inject a known timed-segment result into the descriptor, search for a phrase occurring in several segments, and verify source-preserving matches, deterministic snippets, timestamps, chronological ordering, and exactly one dependency invocation.

### Red — Write Failing Tests First

- [X] T005 [P] [US1] Add failing validation, case-insensitive literal matching, one-match-per-segment, segment-local phrase, chronological-order, equal-timestamp tie, snippet, timestamp, and one-dependency-call tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T006 [P] [US1] Add failing concrete descriptor contract tests for the `videoId`/`query` schema, transcript-text-search metadata, timed dependency disclosure, result fields, provenance, and absence of `representativeOnly` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.
- [X] T007 [P] [US1] Add failing injected-descriptor dispatch and default-catalog registration tests for `transcripts_searchTranscript` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green — Implement the Minimum P1 Slice

- [X] T008 [US1] Implement the search tool name, input schema, safe error type, request validator, case-folded segment matcher, 160-character same-segment snippet builder, chronological match builder, handler, metadata builder, and descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py` to pass T005–T007 without duplicating caption retrieval or VTT parsing.
- [X] T009 [P] [US1] Export the concrete search tool constants, error type, validator, handler, metadata builder, and descriptor from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` after T008 exposes them.
- [X] T010 [P] [US1] Register `transcripts_searchTranscript` with one injected `build_transcripts_get_timestamped_captions_handler` dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, without nested descriptor or dispatcher invocation.
- [X] T011 [US1] Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

### Refactor — Preserve the P1 Contract

- [X] T012 [US1] Run the P1 focused unit, contract, and integration tests from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`; refactor only local transcript-family helpers while keeping the tests green.

**Checkpoint**: `transcripts_searchTranscript` is discoverable and independently returns chronological timestamped matches for a valid selected transcript.

---

## Phase 4: User Story 2 - Search a Requested Language (Priority: P2)

**Goal**: Let a client select a transcript language and receive matches only from that language, with no silent fallback.

**Independent Test**: Inject timed retrieval supporting multiple languages, call the search descriptor with `language`, and verify forwarding, selected-language result context, exact-language results, and a safe unavailable-language outcome.

### Red — Write Failing Tests First

- [X] T013 [P] [US2] Add failing explicit-language forwarding, exact-language result-context, and no-substitution tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T014 [P] [US2] Add failing metadata and error-category contract tests for exact language selection, no fallback, and `language_unavailable` guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.
- [X] T015 [P] [US2] Add failing descriptor-dispatch coverage for forwarded language and safe unavailable-language serialization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

### Green — Implement the Minimum P2 Slice

- [X] T016 [US2] Update the public request validation, timed-dependency argument construction, selected-language result mapping, and sanitized language-error propagation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py` so explicit `language` is passed once to the existing timed handler and is never resolved or substituted locally.
- [X] T017 [US2] Add or update reStructuredText docstrings for every Python function changed for language forwarding and error propagation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.

### Refactor — Preserve Language Semantics

- [X] T018 [US2] Run the focused language unit, contract, integration, and routing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T019 [US2] Refactor duplicate language and error-mapping branches only within `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, then re-run the T018 test set with all results green.

**Checkpoint**: Explicit language selection is independently verifiable, exact, safe, and does not change P1 matching behavior.

---

## Phase 5: User Story 3 - Handle Empty and Bounded Searches (Priority: P3)

**Goal**: Let clients constrain broad searches and distinguish valid no-match results from unavailable captions or safe failures.

**Independent Test**: Search an injected selected transcript with no literal match and a common query exceeding the requested cap; verify a successful `no_matches` result, chronological truncation, default/bounds validation, and distinct unavailable/error categories.

### Red — Write Failing Tests First

- [X] T020 [P] [US3] Add failing `maxMatches` default, bounds, type, unsupported-field, post-sort truncation, valid `no_matches`, no-accessible-captions, empty-segment, and sanitized dependency-error tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T021 [P] [US3] Add failing contract tests for `maxMatches` bounds/default, `no_matches` empty-result policy, `transcript_unavailable`, and the complete safe error taxonomy in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.
- [X] T022 [P] [US3] Add failing integration and MCP-routing tests for bounded successful search, unavailable-caption failure, and sanitized error data in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

### Green — Implement the Minimum P3 Slice

- [X] T023 [US3] Implement `maxMatches` default/range validation, chronological truncation after sorting, successful `availability: no_matches` result shaping, conversion of completed `no_accessible_captions` to `transcript_unavailable`, and safe propagation of all timed-dependency failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.
- [X] T024 [US3] Add or update reStructuredText docstrings for every Python function changed for result limits, empty results, and safe error handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.

### Refactor — Preserve Bounded and Empty-Result Behavior

- [X] T025 [US3] Run the focused bounded/empty-result unit, contract, integration, and routing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T026 [US3] Refactor result construction and safe error conversion only in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, then re-run the T025 test set with all results green.

**Checkpoint**: All stories are complete: valid empty searches, unavailable captions, and safe failures are distinct and bounded results remain chronological.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify documentation, safety, regression coverage, and repository-wide completion evidence.

- [X] T027 [P] Reconcile the implemented schema, field names, snippet rule, dependency boundary, and error guidance with `/Users/ctgunn/Projects/youtube-mcp-server/specs/315-transcript-search/contracts/transcripts-search-transcript-contract.md` and update the contract only if implementation evidence requires it.
- [X] T028 [P] Re-run the focused workflow documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/315-transcript-search/quickstart.md` and correct any stale command or expectation in that file.
- [X] T029 [P] Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` for safe observability and error details; remove any feature-path logging or output that could expose query, caption, credential, raw-response, or trace data.
- [X] T030 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failure caused by the feature in `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/` before completion.
- [X] T031 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every reported feature change in `/Users/ctgunn/Projects/youtube-mcp-server/src/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 — Setup**: Starts immediately.
- **Phase 2 — Foundational**: Depends on T001–T002; confirms the existing timed-segment and safe-error prerequisites before feature changes.
- **Phase 3 — US1**: Depends on T003–T004. It establishes the concrete public tool and is the MVP.
- **Phase 4 — US2**: Depends on the P1 concrete descriptor from T008–T012; its language scenarios remain independently verifiable with an injected timed dependency.
- **Phase 5 — US3**: Depends on the P1 concrete descriptor from T008–T012; it can follow US2 or be performed after P1 if the shared `transcripts.py` changes are coordinated.
- **Phase 6 — Polish**: Depends on all selected user-story phases; T030 and T031 are final completion gates.

### User Story Completion Order

```text
Setup → Foundation → US1 (MVP concrete transcript search)
                         ├── US2 (explicit language behavior)
                         └── US3 (bounds, no-match, and safe empty/error behavior)
                                   ↓
                               Polish / full suite / lint
```

### Within Each User Story

1. Complete the listed Red tasks and confirm the new tests fail for the missing behavior.
2. Complete Green tasks with only the code required to make that story's tests pass.
3. Add or update reStructuredText docstrings for every changed Python function.
4. Run the story's focused suite, refactor without behavioral changes, and rerun it.
5. Do not mark the feature complete until T030 and T031 pass.

## Parallel Opportunities

- **Setup**: T001 and T002 can proceed independently.
- **Foundation**: T003 and T004 inspect disjoint prerequisite behavior and can proceed in parallel.
- **US1 Red**: T005, T006, and T007 modify distinct unit, contract, and integration test surfaces in parallel.
- **US1 registration**: After T008, T009 and T010 modify distinct export and dispatcher files in parallel.
- **US2 Red**: T013, T014, and T015 modify disjoint test surfaces in parallel.
- **US3 Red**: T020, T021, and T022 modify disjoint test surfaces in parallel.
- **Polish**: T027, T028, and T029 can be performed in parallel before final test and lint gates.

## Parallel Example: User Story 1

```text
Task T005: Add unit tests in tests/unit/test_youtube_composed_transcripts.py
Task T006: Add contract tests in tests/contract/test_youtube_composed_transcripts_contract.py
Task T007: Add integration tests in tests/integration/test_youtube_composed_tool_registration.py and tests/integration/test_youtube_tool_registration.py
```

After T008:

```text
Task T009: Export the descriptor from src/mcp_server/tools/youtube_composed/__init__.py
Task T010: Register the descriptor in src/mcp_server/tools/dispatcher.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T004 to confirm the dependency and protocol foundation.
2. Complete T005–T012 to expose a concrete, timestamped, chronological literal-search tool.
3. Validate the P1 independent test before adding optional-language and bounded/empty behavior.

### Incremental Delivery

1. Deliver US1 as the usable core transcript-search experience.
2. Add US2 to make language-sensitive research reliable without altering P1 matching.
3. Add US3 to make broad and empty searches predictable for automated clients.
4. Complete Polish only after all desired increments are green, then collect full-suite and lint evidence.

## Notes

- All 31 tasks use the required checkbox, sequential ID, optional parallel marker, required story label for story phases, and explicit file-path format.
- Do not add `matchScore`, semantic relevance ranking, cross-segment snippets, language fallback, nested MCP dispatch, persistence, or a generic search abstraction.
- The final repository suite and lint tasks are mandatory even if all focused tests pass.
