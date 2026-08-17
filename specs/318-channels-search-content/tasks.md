# Tasks: YT-318 Channel Content Search

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/data-model.md), and [channels-search-content-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/contracts/channels-search-content-contract.md)

**Tests**: Tests are mandatory. Add each listed Red test first and verify it fails before the paired Green task. Every new or modified Python function, including test helpers, requires a reStructuredText docstring. Completion requires a passing full repository test suite and Ruff check after the final code changes.

**Organization**: Tasks are grouped by user story. US1 delivers the independently useful MVP; US2 and US3 extend its executable descriptor and therefore follow US1.

## Phase 1: Setup (Shared Planning Baseline)

**Purpose**: Establish the exact implementation and verification seams without adding a new project, dependency, or infrastructure layer.

- [X] T001 Review the public request, result, error, and direct-search invariants in `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/contracts/channels-search-content-contract.md` before changing code.
- [X] T002 [P] Confirm the existing composed-channel, lower-layer search, export, and registration seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

---

## Phase 2: Foundational (Existing Shared Boundaries)

**Purpose**: Verify the existing boundaries that the additive tool must preserve. No new persistence, direct HTTP client, transport, or shared abstraction is introduced.

**⚠️ CRITICAL**: Complete these baseline checks before writing feature tests so the feature only adapts the established public `search_list` and dispatcher paths.

- [X] T003 Run and record the pre-change Layer 2 search and composed-tool catalog baselines in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_tool_catalog_contract.py` using `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- [X] T004 [P] Review existing safe search-error translation and request-routing behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` to preserve the current public taxonomy and sanitization rules.

**Checkpoint**: The existing public search, catalog, error, and dispatcher boundaries are understood and protected; US1 work can begin.

---

## Phase 3: User Story 1 - Search a Channel's Content (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client search public video content in one known channel using a non-empty query and receive only normalized, associated channel results or a safe outcome.

**Independent Test**: Inject a deterministic `search_list` response into `channels_searchContent`; verify one channel-constrained video search, normalized associated items in source order, a complete empty result, and safe errors without relying on US2 or US3 options.

### Red: Tests for User Story 1

- [X] T005 [P] [US1] Add failing validation and handler tests for non-object input, missing/blank/non-text `channelId` or `query`, unknown fields, trimming, one exact `search_list` call, source-order preservation, channel association, empty success, malformed/mismatched/duplicate omission, and sanitized lower-layer errors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T006 [P] [US1] Add failing descriptor-contract tests for the `channels_searchContent` name, required `channelId` and `query`, direct-search metadata, `search.list` as the only dependency, normalized provenance, public-only scope, safe error categories, and no representative-only marker in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T007 [P] [US1] Add failing injected-execution and default-dispatcher registration tests for `channels_searchContent` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green: Implementation for User Story 1

- [X] T008 [US1] Add the `channels_searchContent` constants, input schema, safe `ChannelsSearchContentToolError`, and validator for required trimmed `channelId` and `query` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T009 [US1] Implement the injected one-call `search_list` request (`part=snippet`, requested `channelId` and query, `type=video`), candidate normalization, requested-channel association defense, first-occurrence de-duplication, safe aggregate omission context, direct-search result context/provenance, lower-layer error mapping, metadata, handler, and descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T010 [P] [US1] Export the new public constants, error, validator, handler, metadata builder, and descriptor builder from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` after T009 defines them.
- [X] T011 [P] [US1] Default-register `channels_searchContent` with one injected `build_search_list_handler(**conditional_dependencies)` dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` after T009 defines its descriptor.
- [X] T012 [US1] Add or update complete reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Refactor: User Story 1

- [X] T013 [US1] Refactor only duplicated local validation, source extraction, omission accounting, and safe-error code while preserving direct-search semantics, then run the US1 focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` with `PYTHONPATH=src python3 -m pytest`.

**Checkpoint**: `channels_searchContent` is an executable, default-registered MVP that searches one channel with required inputs and returns normalized public results, an empty collection, or a safe error.

---

## Phase 4: User Story 2 - Control Search Results (Priority: P2)

**Goal**: Let an MCP client bound results and choose the documented direct-source ordering for the existing channel-content search.

**Independent Test**: Invoke the US1 descriptor with default, minimum, maximum, and invalid result limits and each supported order; verify the lower-layer request and response context use the effective values and no local ranking occurs.

### Red: Tests for User Story 2

- [X] T014 [P] [US2] Add failing unit tests for default/minimum/maximum/invalid `maxResults`, boolean rejection, supported/unsupported `order`, exact forwarding, final cap after normalization, and effective ordering context in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T015 [P] [US2] Add failing contract tests for the `maxResults` bounds/default, exact `order` enum/default, one-search boundedness, upstream-order disclosure, and no-local-ranking declaration in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T016 [P] [US2] Add failing integration tests proving default and explicit limits/orders reach the injected and default-registered descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green: Implementation for User Story 2

- [X] T017 [US2] Add bounded `maxResults` and exact `order` validation/defaulting, lower-layer forwarding, final cap behavior, metadata, and applied-input/search-context disclosure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` without adding local ranking or filtering.
- [X] T018 [US2] Add or update complete reStructuredText docstrings for every Python function changed for result-limit or ordering support in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Refactor: User Story 2

- [X] T019 [US2] Refactor only shared limit/order constants and context construction in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, then run the US2 focused unit, contract, and integration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

**Checkpoint**: US1 remains functional, while valid limits and source ordering choices produce bounded, correctly contextualized results without local re-ranking.

---

## Phase 5: User Story 3 - Refine Search by Language (Priority: P3)

**Goal**: Let an MCP client add a valid language preference that refines relevance without changing channel scope or promising language-only results.

**Independent Test**: Invoke the descriptor with a valid language tag and verify it is validated, passed only as the lower-layer relevance hint, and preserved in response context; verify malformed tags fail before search and absent language leaves the request unchanged.

### Red: Tests for User Story 3

- [X] T020 [P] [US3] Add failing unit tests for valid and invalid BCP 47 language tags, whitespace trimming, omitted-language defaults, no lower-layer call on invalid input, exact relevance-language forwarding, applied-input context, and no language-guarantee claim in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T021 [P] [US3] Add failing contract tests for optional `language`, BCP 47 validation, relevance-only semantics, source-order preservation, and language metadata disclosure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T022 [P] [US3] Add failing integration tests proving a valid language preference reaches both injected and default-registered `channels_searchContent` execution paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green: Implementation for User Story 3

- [X] T023 [US3] Implement a scoped BCP 47 language validator, optional `language` normalization, lower-layer `relevanceLanguage` mapping, applied-input/search-context disclosure, and safe invalid-parameter errors in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` without adding locale, region, transcript, or content-language filters.
- [X] T024 [US3] Add or update complete reStructuredText docstrings for every Python function changed for language refinement in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Refactor: User Story 3

- [X] T025 [US3] Refactor only the local language-validation and applied-context seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, then run the US3 focused unit, contract, and integration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

**Checkpoint**: All three stories work: the tool performs direct channel-content search, honors bounded source ordering, and safely refines relevance by language.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Prove public routing, documentation, contract alignment, and repository-wide quality after all desired stories are complete.

- [X] T026 [P] Add or update public MCP routing regression coverage for the default-registered `channels_searchContent` tool in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T027 Add or update complete reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` and re-audit all touched functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T028 Validate implemented inputs, populated/empty results, safe errors, direct-search metadata, limits, ordering, and language behavior against `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/quickstart.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/contracts/channels-search-content-contract.md`.
- [X] T029 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failure in the affected files named by the test output before marking `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/tasks.md` complete.
- [X] T030 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and resolve every reported issue in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 Setup
  -> Phase 2 Existing Shared Boundaries
     -> Phase 3 US1 (MVP core descriptor)
        -> Phase 4 US2 (limit and ordering controls)
           -> Phase 5 US3 (language relevance refinement)
              -> Phase 6 Polish and full validation
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 and is the MVP. It introduces the executable descriptor, one-search composition, normalized items, and safe outcomes.
- **US2 (P2)**: Depends on the US1 descriptor, but its tests independently prove limits and ordering once the core is available.
- **US3 (P3)**: Depends on the US1 descriptor and should follow US2's implementation because both extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`. Its tests independently prove language behavior once the core is available.
- **Polish**: Depends on all implemented stories. T029 is the mandatory final repository test-suite gate.

### Task Dependency Graph

```text
T001,T002 -> T003,T004 -> T005,T006,T007 -> T008 -> T009 -> T010,T011 -> T012 -> T013
T013 -> T014,T015,T016 -> T017 -> T018 -> T019
T019 -> T020,T021,T022 -> T023 -> T024 -> T025
T025 -> T026 -> T027 -> T028 -> T029 -> T030
```

### Within Each User Story

- Write all Red tests first and observe their failure before the corresponding Green implementation.
- Complete the Green implementation only to satisfy the documented story contract.
- Add or update reStructuredText docstrings for every changed Python function before the story checkpoint.
- Refactor only after the focused tests pass, then rerun the affected focused test set.

## Parallel Opportunities

### User Story 1

After Phase 2, T005, T006, and T007 can be authored in parallel because they modify separate test files. After T009, T010 and T011 can be completed in parallel because exports and default registration are separate files.

```text
Parallel: T005 + T006 + T007
Then:     T008 -> T009
Parallel: T010 + T011
Then:     T012 -> T013
```

### User Story 2

After US1 is complete, T014, T015, and T016 can be authored in parallel because they modify separate test files. T017–T019 remain sequential because they modify and validate the shared channel-family implementation.

```text
Parallel: T014 + T015 + T016
Then:     T017 -> T018 -> T019
```

### User Story 3

After US2 is complete, T020, T021, and T022 can be authored in parallel because they modify separate test files. T023–T025 remain sequential because they modify and validate the shared channel-family implementation.

```text
Parallel: T020 + T021 + T022
Then:     T023 -> T024 -> T025
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete T001–T004 to preserve the existing boundary assumptions.
2. Complete T005–T013 to deliver direct channel-constrained search with required inputs, normalized associated results, empty results, safe errors, metadata, exports, and registration.
3. Stop at the US1 checkpoint and run its focused tests. This is the smallest deployable increment.

### Incremental Delivery

1. Add US1 for direct channel search and validate it independently.
2. Add US2 for bounded result limits and source ordering choices; validate it without local ranking.
3. Add US3 for language relevance refinement; validate it without claiming language-only results.
4. Complete T026–T030 before considering the feature done.

### Parallel Team Strategy

One developer can write the three Red test files in a story in parallel with other reviewers preparing contract assertions. Green work on `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` is intentionally serialized to preserve direct-search simplicity and avoid same-file conflicts. Export and dispatcher work can proceed concurrently after the descriptor exists.

## Notes

- Every task follows the required checkbox, sequential ID, optional `[P]`, story-label, and exact-path format.
- `[P]` tasks touch separate files and can run concurrently once their stated dependency is complete.
- Do not treat focused test runs as final completion evidence; T029 and T030 are mandatory after the final code change.
