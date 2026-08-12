# Tasks: Channel Search

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/307-channel-search/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), and [contracts/channels-search-channels-contract.md](./contracts/channels-search-channels-contract.md)

**Tests**: Test tasks are required. Every implementation increment follows Red–Green–Refactor; completion requires a successful full repository test suite after final changes. Every new or changed Python function requires a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each increment has a clear independently verifiable outcome.

## Phase 1: Setup (Shared Planning Inputs)

**Purpose**: Confirm the contract-first test boundary and repository commands before code changes.

- [X] T001 Review the public request, result, safe-error, provenance, and boundedness rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/307-channel-search/contracts/channels-search-channels-contract.md` before writing Red tests.
- [X] T002 Confirm the focused and full verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/307-channel-search/quickstart.md` can be used from `/Users/ctgunn/Projects/youtube-mcp-server` without adding secrets to fixtures or logs.

---

## Phase 2: Foundational (Blocking Prerequisite: `channelType` Search Support)

**Purpose**: Add the narrow Layer 1/2 search-contract support that `channels_searchChannels` requires. No user-story implementation starts until this phase is complete.

- [X] T003 [P] Add failing Layer 1 contract coverage for optional `channelType`, accepted values `any`/`show`, and safe invalid-value handling in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_search_contract.py`.
- [X] T004 [P] Add failing Layer 2 validation and request-shaping coverage for `channelType`, including omitted-field compatibility and invalid type/value rejection, in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py`.
- [X] T005 [P] Add failing discovery-contract and executable-registration coverage showing `search_list` exposes and preserves `channelType` safely in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py`.
- [X] T006 Add `channelType` to the Layer 1 search request shape and enforce its safe compatible use with channel searches in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/search.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/search.py`.
- [X] T007 Add `channelType` to the Layer 2 `search_list` schema, allowed-field set, validation, request forwarding, and safe metadata in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`.
- [X] T008 Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/search.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/search.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`.
- [X] T009 Refactor only the new `channelType` validation/request path while preserving existing `search_list` behavior, then run the focused search tests from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_search.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_search_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_search_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_search_registration.py`.

**Checkpoint**: The existing search path accepts only documented `channelType` values, preserves legacy callers that omit it, and is ready for the composed tool.

---

## Phase 3: User Story 1 - Search for Relevant Channels (Priority: P1) 🎯 MVP

**Goal**: Deliver a query-only public channel search for handle, name, and general queries with a bounded, distinct, provenance-aware result collection.

**Independent Test**: Invoke the registered tool with valid handle-like, name, and general queries; verify its default and requested limit, supported base ordering/type constraint, distinct channel identifiers, normalized public fields, source-continuation caveat, and successful empty collection.

### Red - Tests for User Story 1

- [X] T010 [P] [US1] Add failing unit tests for query trimming, strict allowed fields, defaults, limit/order/channelType validation, base `type=channel` request mapping, `id.channelId` candidate normalization, earliest-position de-duplication, empty success, and safe base-search error translation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T011 [P] [US1] Add failing contract tests for the exact `channels_searchChannels` schema, non-representative metadata, base dependency, boundedness, continuation caveat, result provenance, and safe error metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T012 [P] [US1] Add failing integration tests that register an injected query-only descriptor and discover/execute it through the dispatcher in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green - Implementation for User Story 1

- [X] T013 [US1] Define the `channels_searchChannels` tool name, input schema, safe error type, argument validator, and safe lower-level search-error mapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T014 [US1] Implement base-search argument construction, `id.channelId` candidate normalization, earliest-position de-duplication, source-continuation disclosure, query-only response shaping, field provenance, discovery metadata, handler, and executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T015 [US1] Export the public search tool symbols and register its descriptor with configured lower-level search, channel, and playlist handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T016 [US1] Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

### Refactor - User Story 1

- [X] T017 [US1] Refactor the query-only implementation to reuse existing channel-family normalization, provenance, sanitization, and request-correlation conventions without adding a generic abstraction; run the focused US1 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

**Checkpoint**: `channels_searchChannels` provides independently usable query-only public channel discovery before refinement or ranking is added.

---

## Phase 4: User Story 2 - Refine Channels by Research Criteria (Priority: P2)

**Goal**: Let clients apply subscriber, latest-upload, and creator-only refinements using bounded public enrichment and safe partial-result behavior.

**Independent Test**: Invoke the tool against controlled candidates with known public channel metadata; verify that every returned channel satisfies selected inclusive subscriber/activity/creator refinements, that no enrichment occurs for a query-only request, and that unavailable required data is excluded and safely disclosed.

### Red - Tests for User Story 2

- [X] T018 [P] [US2] Add failing unit tests for conditional batched channel enrichment, inclusive subscriber ranges, inclusive latest-upload windows, `creatorOnly`, hidden/unavailable values, partial-enrichment aggregation, and all-candidates-unavailable failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T019 [P] [US2] Add failing contract tests for conditional enrichment dependencies, public field provenance, conservative creator-heuristic disclosure, partial-result policy, quota/access caveats, and recovery guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T020 [P] [US2] Add failing integration tests for an injected search/channel/uploads-playlist composition, no unnecessary enrichment for query-only search, and safe dispatcher outcomes for enrichment failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Implementation for User Story 2

- [X] T021 [US2] Implement bounded batched public channel enrichment, subscriber-count handling, latest-upload retrieval from public uploads playlists only when active rules require it, and safe lower-layer error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T022 [US2] Implement inclusive subscriber/activity filters, conservative creator-only filtering using the existing channel-family classifier, required-data exclusion, and safe aggregate `partialEnrichment`/`partial_enrichment_failure` result behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T023 [US2] Add or update reStructuredText docstrings for every Python function changed for enrichment, filtering, error mapping, or result shaping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.

### Refactor - User Story 2

- [X] T024 [US2] Refactor refinement helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` only after tests pass, retain bounded fan-out and safe diagnostic data, and run the focused US2 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

**Checkpoint**: The tool safely refines channels by available public research criteria without treating unknown data as a match.

---

## Phase 5: User Story 3 - Rank Channels for a Research Goal (Priority: P3)

**Goal**: Provide deterministic `relevance`, subscriber, independent-creator, and recent-activity rankings after all selected refinements.

**Independent Test**: Invoke the tool with controlled eligible candidates for each `sortBy` value; verify exact documented order, filter-before-rank sequencing, earliest-base-position ties, metadata-dependent candidate exclusion, and final result capping.

### Red - Tests for User Story 3

- [X] T025 [P] [US3] Add failing unit tests for all five `sortBy` values, filter-before-rank ordering, stable earliest-base-position ties, metadata-dependent ranking exclusion, and final `maxResults` capping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T026 [P] [US3] Add failing contract tests for the exact ranking semantics, deterministic tie policy, `indie_priority` heuristic limitation, recent-activity derivation, and unavailable-data policy in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T027 [P] [US3] Add failing integration tests that execute subscriber, independent-creator, and recent-activity ranking through the registered descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Implementation for User Story 3

- [X] T028 [US3] Implement deterministic ranking keys for `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, and `recent_activity`, preserving base-search position for every tie, in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T029 [US3] Integrate filter-before-rank sequencing, metadata-dependent ranking exclusions, safe partial-enrichment aggregation, and final result capping into the `channels_searchChannels` handler in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T030 [US3] Add or update reStructuredText docstrings for every Python function changed for ranking, partial-result shaping, or handler execution in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.

### Refactor - User Story 3

- [X] T031 [US3] Refactor ranking-key construction in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` without changing public ordering, run the focused US3 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

**Checkpoint**: All documented ranking modes are independently verifiable and deterministic over the same source data.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the completed public contract, documentation, protocol safety, and repository-wide regression state.

- [X] T032 [P] Validate the public discovery, behavior, and verification expectations documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/307-channel-search/quickstart.md` against the completed focused test suites; update that file only if command paths or documented behavior changed.
- [X] T033 [P] Verify the existing Layer 3 category serialization regression coverage still covers every `channels_searchChannels` safe error category in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and add only missing category-safe serialization coverage there.
- [X] T034 Review every changed Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/search.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/search.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` for complete reStructuredText docstrings and safe observability/security behavior.
- [X] T035 Run `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`, then resolve every failure in the affected files before marking YT-307 complete.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 Setup
    │
    ▼
Phase 2 Foundation: Layer 1/2 channelType support
    │
    ▼
Phase 3 US1: query-only channel search (MVP)
    │
    ▼
Phase 4 US2: public enrichment and refinement
    │
    ▼
Phase 5 US3: deterministic ranking
    │
    ▼
Phase 6 Polish: quickstart, protocol regression, docstrings, full suite, lint
```

### User Story Dependencies

- **US1 (P1)** depends on Phase 2 and is the MVP public-tool foundation.
- **US2 (P2)** depends on the US1 descriptor and base-candidate flow; its controlled tests independently prove refinement behavior.
- **US3 (P3)** depends on the US2 enriched-candidate flow; its controlled tests independently prove ranking behavior.

### Within Each User Story

1. Complete every Red test task and confirm the tests fail for the intended missing behavior.
2. Complete the minimum Green tasks needed to make those tests pass.
3. Update reStructuredText docstrings for all changed Python functions.
4. Refactor only after focused tests are green, then rerun the affected test files.

### Parallel Opportunities

- T003, T004, and T005 can run in parallel because they change distinct foundational test files.
- Within US1, T010–T012 can run in parallel; within US2, T018–T020 can run in parallel; within US3, T025–T027 can run in parallel because each set changes distinct unit, contract, and integration test files.
- T032 and T033 can run in parallel after user stories are complete. T034 and T035 are final sequential quality gates.

## Parallel Execution Examples

### Foundational Search Support

```text
Task: "T003 Add Layer 1 channelType contract coverage in tests/contract/test_layer1_search_contract.py"
Task: "T004 Add Layer 2 channelType validation coverage in tests/unit/test_youtube_search.py"
Task: "T005 Add search discovery/registration coverage in tests/contract/test_youtube_search_contract.py and tests/integration/test_youtube_search_registration.py"
```

### User Story 1

```text
Task: "T010 [US1] Add channel-search unit tests in tests/unit/test_youtube_composed_channels.py"
Task: "T011 [US1] Add channel-search contract tests in tests/contract/test_youtube_composed_channels_contract.py"
Task: "T012 [US1] Add channel-search registration tests in tests/integration/test_youtube_composed_tool_registration.py and tests/integration/test_youtube_tool_registration.py"
```

### User Story 2

```text
Task: "T018 [US2] Add refinement unit tests in tests/unit/test_youtube_composed_channels.py"
Task: "T019 [US2] Add enrichment contract tests in tests/contract/test_youtube_composed_channels_contract.py"
Task: "T020 [US2] Add composed-enrichment integration tests in tests/integration/test_youtube_composed_tool_registration.py"
```

### User Story 3

```text
Task: "T025 [US3] Add ranking unit tests in tests/unit/test_youtube_composed_channels.py"
Task: "T026 [US3] Add ranking contract tests in tests/contract/test_youtube_composed_channels_contract.py"
Task: "T027 [US3] Add ranking integration tests in tests/integration/test_youtube_composed_tool_registration.py"
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and the blocking Phase 2 `channelType` support.
2. Complete Phase 3 to ship query-only `channels_searchChannels` with strict validation, stable public response, discovery metadata, registration, and focused tests.
3. Validate the US1 independent test criteria before adding enrichment or ranking.

### Incremental Delivery

1. Setup plus the foundational lower-level extension establishes a safe public search boundary.
2. US1 adds usable channel discovery and can be demonstrated independently.
3. US2 adds public-metadata refinement and safely discloses incomplete enrichment.
4. US3 adds deterministic research-oriented ranking without changing prior filter semantics.
5. Polish verifies documentation, protocol safety, full-suite regression, and lint before completion.

## Notes

- `[P]` tasks affect independent files and can be run in parallel only after their prerequisite phase is complete.
- `[US1]`, `[US2]`, and `[US3]` identify story-local work for traceability.
- Do not begin a Green task before its corresponding Red tests have demonstrated the intended failure.
- Targeted test runs are not completion evidence; T035 requires the full repository suite and lint to pass.
