# Tasks: Video Search with Channel Refinement

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [videos-search-videos.md](./contracts/videos-search-videos.md), and [quickstart.md](./quickstart.md)

**Tests**: Tests are mandatory. Each increment starts with failing tests, implements only the behavior needed to pass them, refactors while tests remain green, and ends with full-suite evidence. Every changed Python function must have a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each delivery increment has a stated goal and independent test. Because all three stories extend one concrete public tool, US2 builds on US1's executable base-search seam and US3 builds on US2's enrichment fields; their focused acceptance tests remain separately runnable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the existing repository and establish a known-good verification baseline; no new project scaffold is required.

- [X] T001 [P] Install the development package and lint dependency using the commands documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/quickstart.md`.
- [X] T002 [P] Run the existing focused composed-video and protocol tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` to record the pre-change baseline.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Make documented Layer 3 error categories safely serializable through the MCP protocol before the new public tool can expose them.

**⚠️ CRITICAL**: No user-story implementation begins until this phase is complete.

- [X] T003 [P] Add failing protocol regression cases for every YT-303 Layer 3 category (`invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, `upstream_failure`, `partial_enrichment_failure`, and `unsupported_filter_or_sort`) in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`; assert numeric MCP errors and stable `error.data.category` values without unsafe details.
- [X] T004 Add additive Layer 3-to-protocol category translation and any required numeric envelope support in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py` so T003 passes without changing existing Layer 2 outcomes.
- [X] T005 Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`, covering parameters, returns, errors, and side effects.
- [X] T006 Refactor the category mapping for the minimum maintainable additive design in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`, then run `python3 -m pytest tests/unit/test_method_routing.py`.

**Checkpoint**: Safe public error delivery is ready; user-story implementation may begin.

---

## Phase 3: User Story 1 - Search for Relevant Videos (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client execute a valid query-only public video search with documented base filters, bounded results, stable normalized video fields, empty-success behavior, and continuation context.

**Independent Test**: Build `videos_searchVideos` with an injected recording base-search handler, invoke it with a valid query and optional base constraints, and verify mapped `type=video` search arguments, at most the requested number of normalized items, preserved base order, a successful empty collection, and a discovered executable descriptor.

### Red - Failing Tests for User Story 1

- [X] T007 [P] [US1] Add failing validator and handler tests for trimmed query text, unknown fields, strict booleans/integers, 1–50 `maxResults`, base-order enum values, explicit-timezone ISO 8601 publication windows, reversed-window rejection, base-search mapping, normalized candidates, empty success, continuation, and sanitized base-search failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`.
- [X] T008 [P] [US1] Add failing discovery-contract tests for the concrete `videos_searchVideos` name, exact input schema, `ranked_enrichment` boundary, base `search.list` dependency, core field provenance, safe error categories, and absence of `representativeOnly` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`.
- [X] T009 [P] [US1] Add failing injected-descriptor and default-dispatcher registration tests for query-only `videos_searchVideos` execution in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green - Implementation for User Story 1

- [X] T010 [US1] Define the `videos_searchVideos` tool name, public input schema, safe error type, argument validator, ISO 8601 parsing, normalized request fields, and base-search request builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.
- [X] T011 [US1] Implement base video-candidate normalization, safe `search_list` error translation, query-only result shaping (`items`, `appliedInputs`, `returnedCount`, `maxResults`, optional continuation, and field provenance), executable metadata, injected handler, and descriptor builder in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.
- [X] T012 [US1] Export the concrete video-search constants, error type, validator, handler, metadata builder, and descriptor builder from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`.
- [X] T013 [US1] Register the video-search descriptor with an injected `search_list` handler beside the existing video-detail descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T014 [US1] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

### Refactor and Verify User Story 1

- [X] T015 [US1] Refactor only the base-search helpers and test fixtures needed to keep the videos family cohesive in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, then run the focused US1 unit, contract, and integration tests from `/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/quickstart.md`.

**Checkpoint**: Query-only `videos_searchVideos` is independently executable, discoverable, and safe to demonstrate as the MVP.

---

## Phase 4: User Story 2 - Find Videos from Suitable Channels (Priority: P2)

**Goal**: Let clients filter base video candidates by public channel subscriber range, latest public upload activity, or conservative creator classification, and request one eligible video per channel while receiving safe partial-enrichment disclosure.

**Independent Test**: Build the tool with controlled base-search, batched-channel, and date-ordered latest-activity handlers; verify every returned candidate satisfies selected channel filters, `uniqueChannels=true` has no repeated channel ID, missing required metadata is excluded and disclosed, and all-unavailable required enrichment produces the safe category.

### Red - Failing Tests for User Story 2

- [X] T016 [P] [US2] Add failing unit tests for subscriber bounds, batched distinct channel-ID enrichment, hidden subscriber counts, `creatorOnly`, inclusive latest-upload windows, missing channel IDs, requested-only enrichment, safe partial summaries, and all-unavailable enrichment behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`.
- [X] T017 [P] [US2] Add failing contract tests for conditional `channels.list` and latest-activity `playlistItems.list` disclosure, boundedness, quota/auth caveats, channel-field provenance, creator heuristic limitations, partial-result policy, and `uniqueChannels` semantics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`.
- [X] T018 [P] [US2] Add failing integration tests that inject recording base-search, batched-channel, and latest-activity handlers and prove the composed partial-result behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Implementation for User Story 2

- [X] T019 [US2] Implement conditional distinct-channel collection, batched `channels_list` request mapping, channel metadata normalization, non-fabricated subscriber handling, and lower-layer channel-error translation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.
- [X] T020 [US2] Implement conditional per-channel uploads-playlist latest-activity lookup, conservative positive-only creator classification with safe public signals, inclusive channel filters, required-data exclusion, and aggregate partial-enrichment disclosure in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.
- [X] T021 [US2] Extend the handler, executable metadata, and descriptor dependency injection for channel and latest-activity enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py` and pass the configured `channels_list` and `playlist_items_list` dependencies from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T022 [US2] Add or update reStructuredText docstrings for every new or modified function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, documenting composition, bounded fan-out, partial results, and safe errors.

### Refactor and Verify User Story 2

- [X] T023 [US2] Refactor enrichment and partial-result helpers only where reuse is already needed within the videos family in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, preserve the public contract in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, and run the focused US2 unit, contract, and integration tests.

**Checkpoint**: Channel-aware refinement and `uniqueChannels` work without returning unverified candidates as qualified results.

---

## Phase 5: User Story 3 - Rank Results for a Research Goal (Priority: P3)

**Goal**: Let clients rank eligible candidates by relevance, channel subscriber size, independent-creator priority, or latest public activity with stable tie handling.

**Independent Test**: Invoke the enriched tool with controlled eligible candidates for every `sortBy` value and verify filter-before-rank processing, base-order tie preservation, post-rank `uniqueChannels` selection, final truncation, and exclusion/disclosure when a selected ranking datum is unavailable.

### Red - Failing Tests for User Story 3

- [X] T024 [P] [US3] Add failing unit tests for all five `sortBy` values, default relevance, filter-before-rank order, stable base-position ties, unavailable ranking data, ranking-before-unique-channel selection, and final `maxResults` truncation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`.
- [X] T025 [P] [US3] Add failing contract tests for all ranking semantics, deterministic tie guidance, ranking provenance, and metadata-dependent candidate exclusion in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`.
- [X] T026 [P] [US3] Add failing composed-handler integration coverage for ranked results and post-rank one-result-per-channel behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Implementation for User Story 3

- [X] T027 [US3] Implement filter-before-rank sequencing, stable ranking keys for `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, and `recent_activity`, metadata-dependent ranking exclusions, post-rank channel de-duplication, and final capping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.
- [X] T028 [US3] Extend concrete discovery metadata and result provenance to describe final-ranking behavior, ties, heuristic limitations, and required-data partial outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.
- [X] T029 [US3] Add or update reStructuredText docstrings for every new or modified ranking, de-duplication, metadata, and handler function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.

### Refactor and Verify User Story 3

- [X] T030 [US3] Refactor ranking-key and de-duplication helpers for the smallest behavior-preserving videos-family design in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, then run all focused composed-video unit, contract, and integration tests listed in `/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/quickstart.md`.

**Checkpoint**: All documented ranking modes are deterministic, bounded, and independently verified against controlled candidates.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete contract, documentation, observability, security, and final regression evidence after all desired stories are implemented.

- [X] T031 [P] Compare executable discovery metadata and result/error behavior against `/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/contracts/videos-search-videos.md`; add any missing contract regression assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`.
- [X] T032 [P] Audit all changed Python functions for complete reStructuredText docstrings and safe observability/security behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`.
- [X] T033 Validate every verification flow in `/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/quickstart.md`, correcting only documentation that no longer matches the implemented focused test commands or contract behavior.
- [X] T034 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml`, fix all failures in the relevant files, and rerun until the full repository suite passes.
- [X] T035 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml`, fix all lint failures in the relevant files, and rerun until lint passes.
- [X] T036 Rerun the full repository suite and lint commands from `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml` after the final fixes; record passing `python3 -m pytest` and `ruff check .` evidence before completion.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1: Setup
    ↓
Phase 2: Safe Layer 3 protocol error mapping (BLOCKS public tool work)
    ↓
Phase 3: US1 — query-only searchable MVP
    ↓
Phase 4: US2 — channel-aware filtering and partial enrichment
    ↓
Phase 5: US3 — ranking and post-rank de-duplication
    ↓
Phase 6: Polish, full-suite, and lint evidence
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2. It is the MVP and owns the executable base-search descriptor, registration, and normalized result shape.
- **US2 (P2)**: Starts after US1 because it extends the same executable handler and result shape with conditional enrichment. Its focused tests independently prove channel filtering and partial-result behavior.
- **US3 (P3)**: Starts after US2 because four ranking modes consume enrichment data. Its focused tests independently prove ranking, tie, de-duplication, and cap behavior.

### Within-Story Order

1. Complete every Red task and confirm the targeted tests fail for the intended reason.
2. Complete Green implementation tasks in listed order until those tests pass.
3. Complete docstring work before the story checkpoint.
4. Complete the Refactor task while preserving focused green tests.
5. Do not start the dependent next phase until its predecessor checkpoint passes.

## Parallel Opportunities

### Phase-Level Opportunities

- T001 and T002 can run in parallel.
- T003 can be prepared while the existing environment baseline is recorded, but T004–T006 remain sequential.
- Within each user story, its Red tasks edit separate test files and can be prepared in parallel.
- T031 and T032 can run in parallel after US3; T034–T036 are final sequential evidence tasks because remediation may modify shared files.

### Parallel Example: User Story 1

```text
Parallel Red work after Phase 2:
- T007 in tests/unit/test_youtube_composed_videos.py
- T008 in tests/contract/test_youtube_composed_videos_contract.py
- T009 in tests/integration/test_youtube_composed_tool_registration.py and tests/integration/test_youtube_tool_registration.py
```

### Parallel Example: User Story 2

```text
Parallel Red work after US1:
- T016 in tests/unit/test_youtube_composed_videos.py
- T017 in tests/contract/test_youtube_composed_videos_contract.py
- T018 in tests/integration/test_youtube_composed_tool_registration.py
```

### Parallel Example: User Story 3

```text
Parallel Red work after US2:
- T024 in tests/unit/test_youtube_composed_videos.py
- T025 in tests/contract/test_youtube_composed_videos_contract.py
- T026 in tests/integration/test_youtube_composed_tool_registration.py
```

## Implementation Strategy

### MVP First

1. Complete setup and the safe protocol error-mapping foundation.
2. Complete US1 only.
3. Verify the query-only search through its injected handler, contract, registry, empty-result, and safe-error tests.
4. Demonstrate or deploy the P1 tool before accepting any channel-aware enrichment scope.

### Incremental Delivery

1. **US1** adds a bounded, normalized query-only search tool.
2. **US2** adds conditional channel enrichment, filters, safe partial-result behavior, and one-result-per-channel support without changing the base-search contract.
3. **US3** adds deterministic ranking and final de-duplication/capping using the US2 enrichment data.
4. **Polish** confirms all contract, security, docstring, full-suite, and lint obligations.

### Completion Criteria

- All 36 checklist tasks are complete in order, with every task retaining its required format.
- The focused story tests demonstrate each independent test criterion.
- Every changed Python function has a reStructuredText docstring.
- `python3 -m pytest` and `ruff check .` pass after the final code changes.
