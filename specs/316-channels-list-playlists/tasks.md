# Tasks: YT-316 Channel Playlist Listing

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/316-channels-list-playlists/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/channels-list-playlists-contract.md`, and `quickstart.md`

**Tests**: Tests are mandatory. Write each Red task first and confirm it fails before its Green task. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` after the final code change. Every new or changed Python function, including test doubles, requires a reStructuredText docstring.

## Phase 1: Setup

**Purpose**: Establish the focused verification baseline and trace the approved contract to implementation files.

- [X] T001 Run the focused composed-channel baseline suite and record the current result in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T002 Map the approved input, two-read composition, result, provenance, and error clauses from `/Users/ctgunn/Projects/youtube-mcp-server/specs/316-channels-list-playlists/contracts/channels-list-playlists-contract.md` to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` before editing code

---

## Phase 2: Foundational - Descriptor Exposure and Registration

**Purpose**: Add the blocking public descriptor and registration seams used by every story.

**⚠️ CRITICAL**: Complete this phase before story-specific behavior.

- [X] T003 [P] Add failing discovery-schema and metadata assertions for `channels_listPlaylists`, including no `representativeOnly` marker, in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`
- [X] T004 [P] Add failing package-export and default-dispatcher registration assertions for `channels_listPlaylists` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T005 Implement the public tool constant, input schema, descriptor metadata, safe error type, package exports, and default dispatcher registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 Add or update reStructuredText docstrings for every new or modified Python function introduced by the descriptor and registration work in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T007 Refactor the foundational descriptor, export, and registration changes without changing the public contract, then run the foundational focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

**Checkpoint**: The concrete descriptor is discoverable and default-registered; user-story implementation can begin.

---

## Phase 3: User Story 1 - List a Channel's Playlists (Priority: P1) 🎯 MVP

**Goal**: Return a normalized, source-ordered playlist collection for one verified channel.

**Independent Test**: Inject a known channel and ordered playlist response, call `channels_listPlaylists`, and verify exactly one channel verification and one playlist listing produce the expected normalized records and count.

- [X] T008 [P] [US1] Add failing unit tests for trimmed required `channelId`, exact channel verification and `snippet,contentDetails,status` playlist-listing requests, ordered normalized records, optional-field omission, and returned count in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T009 [P] [US1] Add failing contract tests for the successful result shape, normalized-versus-source field provenance, source-order disclosure, and no-ranking policy in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`
- [X] T010 [P] [US1] Add a failing injected-descriptor integration test for successful channel verification and playlist normalization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`
- [X] T011 [US1] Implement request validation, one channel-verification adapter, one channel-scoped playlist-listing adapter, normalized playlist-record mapping, source-order preservation, provenance, collection context, and returned-count shaping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T012 [US1] Add or update reStructuredText docstrings for every validator, adapter, normalizer, descriptor, and test double changed for successful playlist listing in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T013 [US1] Refactor successful-listing helpers to remove duplicated field extraction while preserving the P1 contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, then run the P1 unit, contract, and injected-descriptor tests

**Checkpoint**: A verified channel with accessible playlists returns an independently usable normalized listing.

---

## Phase 4: User Story 2 - Bound a Playlist Listing (Priority: P2)

**Goal**: Apply the documented default and caller-requested result bound without changing source order.

**Independent Test**: Call the tool with omitted, minimum, maximum, and invalid limits against an ordered collection and verify the applied lower-layer limit, result count, order, and validation behavior.

- [X] T014 [P] [US2] Add failing unit tests for the default of 25; inclusive 1–50 bounds; and rejection of zero, negative, above-limit, boolean, fractional, string, and unknown input values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T015 [P] [US2] Add failing contract tests for `maxResults` default/bounds, no continuation input, applied-limit context, and bounded source-order semantics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`
- [X] T016 [US2] Implement applied-limit normalization and exact forwarding to the playlist listing without local re-ranking, over-fetching, or continuation traversal in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T017 [US2] Add or update reStructuredText docstrings for every Python validator, handler, descriptor, and test double changed by bounded-list behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T018 [US2] Refactor limit validation and collection-context construction while preserving P1 behavior, then run the P1/P2 unit and contract tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`

**Checkpoint**: Callers can independently control a 1–50 bounded, source-ordered listing, with an omitted value defaulting to 25.

---

## Phase 5: User Story 3 - Receive Actionable Unavailable Outcomes (Priority: P3)

**Goal**: Distinguish safe invalid, unavailable, restricted, quota, and source-failure outcomes from a successful empty playlist listing.

**Independent Test**: Exercise invalid input, an unverified channel, a verified channel with an empty listing, restricted access, quota exhaustion, and source failure; verify documented categories and sanitized details.

- [X] T019 [P] [US3] Add failing unit tests for missing/blank/non-text `channelId`, unavailable channel verification, verified-empty success, malformed source records, and all lower-layer error-category mappings in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T020 [P] [US3] Add failing contract tests for safe error categories, recovery guidance, empty-versus-unavailable semantics, and absence of unsafe diagnostic fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`
- [X] T021 [P] [US3] Add failing dispatcher and protocol-routing tests for serialized safe outcomes without raw source details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T022 [US3] Implement safe verification-result handling, verified-empty success, malformed-record omission, lower-layer category translation, sanitized details, and caller-safe messages in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T023 [US3] Add or update reStructuredText docstrings for every Python error mapper, handler, descriptor, and test double changed for safe outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T024 [US3] Refactor safe-error translation to reuse existing sanitization while preserving P1/P2 behavior, then run all focused unit, contract, integration, and routing tests listed in `/Users/ctgunn/Projects/youtube-mcp-server/specs/316-channels-list-playlists/quickstart.md`

**Checkpoint**: Empty success and every documented limitation are independently distinguishable and safe.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, complete regression evidence, and readiness review.

- [X] T025 [P] Reconcile implementation-specific caller examples and verification guidance with the final contract in `/Users/ctgunn/Projects/youtube-mcp-server/specs/316-channels-list-playlists/contracts/channels-list-playlists-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/316-channels-list-playlists/quickstart.md`
- [X] T026 [P] Review every changed Python function and test double for compliant reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T027 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failure in the affected source and test files before considering the feature complete
- [X] T028 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every reported issue in the affected source and test files before considering the feature complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** has no dependencies.
- **Phase 2** depends on Phase 1 and blocks all story work.
- **Phase 3 (US1)** depends on Phase 2 and is the MVP.
- **Phase 4 (US2)** extends the same public handler after US1, so it depends on Phase 3.
- **Phase 5 (US3)** depends on the descriptor and successful handler from Phases 2–3; schedule it after Phase 4 to retain one focused change stream in `channels.py`.
- **Phase 6** depends on all desired stories.

### User Story Dependencies

- **US1 (P1)**: Concrete descriptor foundation only; independently proves populated normalized listings.
- **US2 (P2)**: Builds on US1's listing handler; independently proves valid bounded and invalid-limit behavior.
- **US3 (P3)**: Builds on the common descriptor and request path; independently proves safe unavailable and failure outcomes, including the successful-empty distinction.

### Parallel Opportunities

- T003 and T004 can proceed in parallel because they change separate test files.
- For US1, T008, T009, and T010 can proceed in parallel; they modify separate unit, contract, and integration files before T011.
- For US2, T014 and T015 can proceed in parallel before T016.
- For US3, T019, T020, and T021 can proceed in parallel before T022.
- T025 and T026 can proceed in parallel after story implementation is complete.

## Parallel Execution Examples

### User Story 1

```text
T008: unit Red tests in tests/unit/test_youtube_composed_channels.py
T009: contract Red tests in tests/contract/test_youtube_composed_channels_contract.py
T010: integration Red test in tests/integration/test_youtube_composed_tool_registration.py
```

### User Story 2

```text
T014: limit-validation Red tests in tests/unit/test_youtube_composed_channels.py
T015: limit-contract Red tests in tests/contract/test_youtube_composed_channels_contract.py
```

### User Story 3

```text
T019: outcome-mapping Red tests in tests/unit/test_youtube_composed_channels.py
T020: safe-error contract Red tests in tests/contract/test_youtube_composed_channels_contract.py
T021: registration/routing Red tests in tests/integration/test_youtube_tool_registration.py and tests/unit/test_method_routing.py
```

## Implementation Strategy

### MVP First

1. Complete Phases 1 and 2.
2. Complete US1 through T013.
3. Verify the populated source-ordered listing independently with its focused unit, contract, and integration tests.
4. Demo or release the MVP before adding limits and expanded failure behavior if appropriate.

### Incremental Delivery

1. Add US1 for verified, normalized playlist listings.
2. Add US2 for caller-controlled bounded listings without altering US1 source-order behavior.
3. Add US3 for safe distinction of unavailable, restricted, capacity, and source conditions from a successful empty collection.
4. Complete final contract/docstring review and full-suite verification.

## Format Validation

All 28 tasks use the required `- [ ] T### [P?] [US?] Description with absolute file path` checklist format. Story tasks are labeled `[US1]`, `[US2]`, or `[US3]`; setup, foundational, and polish tasks intentionally have no story label.
