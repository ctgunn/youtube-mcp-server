# Tasks: Creator Discovery

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/`

**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/data-model.md), and [channels-find-creators-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/contracts/channels-find-creators-contract.md)

**Tests**: Tests are mandatory. Every story starts with failing tests, follows with the smallest passing implementation, and ends with refactoring while focused tests remain green. Final completion requires `python3 -m pytest` and `python3 -m ruff check .` after all code changes. Every changed Python function requires a reStructuredText docstring.

**Organization**: Tasks are grouped by independently testable user story. `channels_findCreators` is additive and reuses the existing public `search_list`, `channels_list`, and `playlist_items_list` boundaries.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing project needs no new runtime, storage, or client setup and establish the plan-specific verification surface.

- [X] T001 Review the implementation boundaries, 50-video candidate limit, and 0–10 sample limit in `/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/research.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/contracts/channels-find-creators-contract.md` before editing code.
- [X] T002 Confirm the focused verification commands and live-secret safety guidance in `/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/quickstart.md` apply to `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish executable public-contract and default-registration expectations that every story relies on.

**⚠️ CRITICAL**: Complete these Red tasks before implementing user-story behavior.

- [X] T003 [P] Add failing baseline descriptor tests for `channels_findCreators` name, strict schema, additive metadata, bounded composite dependencies, safe error categories, provenance, heuristic disclosure, and no unsafe or representative-only metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T004 [P] Add a failing default-registry discovery test proving `channels_findCreators` is listed as an executable public tool in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

**Checkpoint**: The public contract and registration expectations are failing and ready to drive the first green implementation.

---

## Phase 3: User Story 1 - Discover Creators from Relevant Videos (Priority: P1) 🎯 MVP

**Goal**: Return distinct public channel candidates derived from topic-matching videos, preserving the earliest video order and base-search context.

**Independent Test**: Invoke the descriptor with injected video-search results containing duplicate channels; verify a valid query returns no more than the requested number of distinct candidates, identifies the matched-video basis, preserves the first video position, returns a successful empty collection for no matches, and exposes only base-search continuation context.

### Red - Tests First

- [X] T005 [US1] Add failing validation and handler tests for trimmed query, unknown fields, defaults, result bounds, base `order`, inclusive video-publication windows, a fixed 50-video `type=video` request, matched-video normalization, distinct-channel grouping, deterministic earliest-position selection, empty results, continuation context, and sanitized base-search failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T006 [P] [US1] Add a failing injected-dispatcher test for query-only creator discovery, duplicate-channel collapse, and safe base-search error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Minimum Implementation

- [X] T007 [US1] Define `channels_findCreators` constants, strict input schema, safe error type, timestamp and request validation, base video-search mapping, matched-video normalization, candidate grouping, query-only result shaping, metadata builder, handler factory, and descriptor factory in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T008 [US1] Export the concrete creator-discovery public surface from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and register the descriptor with injected lower-layer handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T009 [US1] Add or update reStructuredText docstrings with purpose, `:param:`, `:return:`, `:raises:`, and relevant side effects for every Python function changed for query-only creator discovery in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

### Refactor - Keep P1 Green

- [X] T010 [US1] Refactor query-only creator-discovery helpers to reuse existing channel-family timestamp, provenance, and safe-error utilities without changing public behavior; run the P1 focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

**Checkpoint**: User Story 1 is independently functional as the MVP.

---

## Phase 4: User Story 2 - Refine Creators by Audience and Activity (Priority: P2)

**Goal**: Filter video-derived candidate channels by public subscriber count, latest upload, and creator-like classification without accepting missing data as a match.

**Independent Test**: Invoke creator discovery with controlled matching videos and injected channel/activity records; verify every returned candidate satisfies all selected refinements, unavailable required data is safely excluded and summarized, and all-unevaluable candidates yield `partial_enrichment_failure`.

### Red - Tests First

- [X] T011 [US2] Add failing handler tests for non-negative inclusive subscriber bands, inclusive latest-upload windows, `creatorOnly`, one batched channel lookup when enrichment is required, per-candidate bounded activity lookup only when needed, missing-data exclusion, partial summaries, and all-candidates-unavailable failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T012 [P] [US2] Add a failing injected-dispatcher refinement test covering subscriber/activity/creator filters and safe partial-enrichment outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Minimum Implementation

- [X] T013 [US2] Extend creator-discovery conditional enrichment and filtering in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` to reuse public `channels_list` and `playlist_items_list`, conservative creator classification, safe lower-layer error translation, and aggregate partial-enrichment rules without using matched-video dates as latest activity.
- [X] T014 [US2] Add or update reStructuredText docstrings for every Python function changed for creator refinement and partial-enrichment behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.

### Refactor - Keep P2 Green

- [X] T015 [US2] Refactor enrichment/filter helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` to preserve one-batch channel lookup, bounded activity fan-out, safe detail sanitization, and public-only data boundaries; run the P2 focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

**Checkpoint**: User Stories 1 and 2 both work, and audience/activity refinement is independently verifiable.

---

## Phase 5: User Story 3 - Prioritize and Inspect Creator Candidates (Priority: P3)

**Goal**: Rank qualifying creator candidates deterministically and return bounded topic-matching video samples for each final candidate.

**Independent Test**: Use controlled eligible candidates with multiple matching videos; verify all five ranking modes, filter-before-rank semantics, stable ties, final channel cap, zero/positive sample limits, and per-channel samples in base-video order.

### Red - Tests First

- [X] T016 [US3] Add failing handler tests for all five `sortBy` modes, filters-before-ranking, earliest-base-video tie resolution, missing-data exclusion for metadata-dependent ranks, final channel cap, `sampleVideosPerChannel=0`, positive sample limits, and per-channel base-video sample order in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T017 [P] [US3] Add failing contract tests for sample input default/bounds, sample/result provenance, candidate-derivation metadata, ranking semantics, base-only continuation caveat, and bounded fan-out disclosure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T018 [P] [US3] Add a failing injected-dispatcher test for ranked creator discovery with final-candidate samples in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Minimum Implementation

- [X] T019 [US3] Implement creator-discovery filter-before-rank ordering, all documented ranking keys with earliest-base-video tie-breaking, final `maxResults` truncation, and post-cap per-channel sample selection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T020 [US3] Add or update reStructuredText docstrings for every Python function changed for ranking and sample selection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.

### Refactor - Keep P3 Green

- [X] T021 [US3] Refactor ranking and sample-selection helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` without changing documented provenance, boundedness, or deterministic ordering; run the P3 focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

**Checkpoint**: All three user stories are independently testable and complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the documented workflow, protocol safety, full-suite regression behavior, linting, and source documentation after all story work.

- [X] T022 [P] Verify the documented creator-discovery expectations and focused commands against the implementation in `/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/quickstart.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T023 [P] Add or update protocol regression coverage for any new creator-discovery safe error serialization gap in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T024 Review every changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` for complete reStructuredText docstrings before feature completion.
- [X] T025 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml` and resolve every failure in the affected files under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/` before marking the feature complete.
- [X] T026 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml` and resolve every reported issue in the affected files under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/` before marking the feature complete.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 Setup
    ↓
Phase 2 Foundational Red contract/registration expectations
    ↓
US1 (P1): query-only video-derived candidate discovery
    ↓
US2 (P2): public enrichment and refinement
    ↓
US3 (P3): ranking and bounded samples
    ↓
Phase 6 Polish, protocol regression, full suite, and lint
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2. It provides the executable descriptor, video grouping, and query-only candidate collection. It is the suggested MVP.
- **US2 (P2)**: Starts after US1 because refinement extends US1's grouped candidates; its controlled-enrichment tests remain independently executable.
- **US3 (P3)**: Starts after US2 because it ranks the same enriched candidates and exposes their samples; its controlled candidate tests remain independently executable.

### Within Each User Story

1. Complete each Red test task and confirm the new assertions fail before the Green task begins.
2. Implement only the behavior required to make that story's Red tests pass.
3. Add or update reStructuredText docstrings for every changed Python function.
4. Refactor only with focused tests green.
5. Do not mark the feature complete until the final full repository suite and Ruff check pass.

## Parallel Opportunities

- T003 and T004 modify different test files and can run in parallel.
- Within US1, T005 and T006 can run in parallel after Phase 2; both are Red tests in different files.
- Within US2, T011 and T012 can run in parallel after US1; both are Red tests in different files.
- Within US3, T016, T017, and T018 can run in parallel after US2; they are Red tests in separate unit, contract, and integration files.
- T022 and T023 can run in parallel after US3 because they target separate documentation and protocol-test files.

## Parallel Example: User Story 3

```text
Task: "Add ranking and sample-selection Red tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py"
Task: "Add sample contract Red tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py"
Task: "Add ranked-sample integration Red tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py"
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete T005 through T010 to deliver video-derived, distinct public creator candidates.
3. Run the US1 focused test targets and demonstrate a valid query, duplicate-channel collapse, empty success, and safe source-failure behavior.
4. The descriptor can be registered and demonstrated as an additive MCP tool before refinement/ranking/samples are added.

### Incremental Delivery

1. Deliver US1 query-only discovery.
2. Add US2 public-metadata refinement with safe partial outcomes.
3. Add US3 deterministic ranking and bounded samples.
4. Complete cross-cutting protocol, full-suite, lint, and documentation verification.

## Format Validation

- All 26 tasks use the required `- [ ] T### [P?] [US?] Description with file path` checklist format.
- Story tasks T005–T010 use `[US1]`, T011–T015 use `[US2]`, and T016–T021 use `[US3]`.
- Setup, foundational, and polish tasks intentionally omit story labels; `[P]` appears only on tasks that can be performed in parallel in different files.
