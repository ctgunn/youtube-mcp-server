# Tasks: YT-305 Channel Details

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/channels-get-channel-contract.md](./contracts/channels-get-channel-contract.md), and [quickstart.md](./quickstart.md)

**Tests**: Tests are mandatory. Every user story uses Red-Green-Refactor and completion requires `PYTHONPATH=src python3 -m pytest` plus `PYTHONPATH=src python3 -m ruff check .` after final code changes. Every new or modified Python function requires a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each increment can be independently exercised after the shared public-boundary prerequisite is complete.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks once their phase prerequisite is complete and the worktree is coordinated.
- **[US#]**: Maps a task to the corresponding user story in [spec.md](./spec.md).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the contract-first implementation boundary and focused verification locations before changing code.

- [X] T001 Review and reconcile the public contract, research decisions, data model, and verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/contracts/channels-get-channel-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the concrete public-boundary test seams shared by all channel-detail behavior.

**⚠️ CRITICAL**: Complete this phase before beginning user-story implementation.

- [X] T002 [P] Add failing default-dispatcher discovery and injected-descriptor registration tests for `channels_getChannel` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`
- [X] T003 [P] Add failing safe MCP error-category serialization regression coverage for `partial_enrichment_failure` and the documented core failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T004 Add the concrete public schema, safe public error type, metadata builder, descriptor builder, package exports, and dispatcher dependency injection for `channels_getChannel` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T005 Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T006 Refactor the descriptor exposure and registration seam without changing its public contract, then run the foundational registration and routing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

**Checkpoint**: The concrete public descriptor is available through the default dispatcher with safe error serialization; user-story behavior can now be added.

---

## Phase 3: User Story 1 - Retrieve One Channel's Details (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client retrieve one available channel as a stable public profile with normalized metadata, complete provenance, and a bounded successful latest-video enrichment.

**Independent Test**: Invoke the concrete descriptor with controlled channel and uploads-playlist handlers for an available channel. Verify one core channel read, at most one one-item playlist read, required public and normalized fields, a latest publication timestamp when available, and field provenance for every returned path.

### Red - Tests for User Story 1

- [X] T007 [P] [US1] Add failing unit tests for nonblank `channelId` validation, unknown-field rejection, trimmed lookup arguments, core profile normalization, sparse public metadata, complete provenance, and a successful one-item uploads-playlist timestamp in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T008 [P] [US1] Add failing executable-contract tests for the `channels_getChannel` schema, normalized-and-enriched composition boundary, two-dependency bound, core field provenance, success metadata, and absence of `representativeOnly` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`
- [X] T009 [P] [US1] Add failing injected-descriptor integration coverage for successful one-channel invocation and discovery output in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green - Implementation for User Story 1

- [X] T010 [US1] Implement request validation, the one-channel `channels_list` adapter, source-preserving core profile mapping, normalized country/default-language/joined-date/custom-URL mapping, field-provenance generation, and successful bounded uploads-playlist timestamp enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T011 [US1] Wire the default descriptor to configured `channels_list` and `playlist_items_list` handlers while preserving existing default-tool behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T012 [US1] Add or update reStructuredText docstrings for every new or modified Python function supporting core channel normalization and successful enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor - User Story 1

- [X] T013 [US1] Refactor repeated source extraction, normalized metadata assembly, and provenance mapping without changing the public result, then run the focused US1 checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

**Checkpoint**: A client can retrieve one available channel with stable core data, normalized metadata, provenance, and a latest-video timestamp when it is available.

---

## Phase 4: User Story 2 - Assess Channel Type With Appropriate Caution (Priority: P2)

**Goal**: Add safe public-contact extraction and a non-canonical creator-versus-brand assessment that returns `unknown` whenever public evidence is insufficient or conflicting.

**Independent Test**: Invoke the available-channel flow with public profile material containing valid and invalid contact candidates plus creator-like, brand-like, conflicting, and insufficient signals. Verify deterministic public-only contacts, `creator`/`brand`/`unknown` results, safe signal identifiers, and heuristic provenance.

### Red - Tests for User Story 2

- [X] T014 [P] [US2] Add failing unit tests for deterministic de-duplication of valid public email addresses and HTTP(S) links, omission of malformed/duplicate/unsupported/private values, and public-only source limits in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T015 [P] [US2] Add failing unit tests for positive creator signals, positive brand signals, conflicting signals, insufficient signals, stable signal identifiers, and `unknown` fallback in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T016 [P] [US2] Add failing contract tests for heuristic-inferred contact and classification provenance, basis, limitations, and non-canonical caller guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`

### Green - Implementation for User Story 2

- [X] T017 [US2] Implement public-material-only contact extraction, validation, deterministic de-duplication, and heuristic-inferred contact provenance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T018 [US2] Implement positive-evidence-only `creator`, `brand`, and `unknown` classification with safe signal identifiers, conflict handling, provenance, and discovery limitations in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T019 [US2] Add or update reStructuredText docstrings for every new or modified contact and channel-type heuristic Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`

### Refactor - User Story 2

- [X] T020 [US2] Refactor contact normalization and classification token handling without widening source scope or changing caller-visible semantics, then run the focused US2 unit and contract checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`

**Checkpoint**: An available channel can include cautious, public-only contact context and a clearly non-canonical creator-versus-brand assessment without breaking the P1 result.

---

## Phase 5: User Story 3 - Handle Missing Channels and Incomplete Enrichment Safely (Priority: P3)

**Goal**: Return safe whole-request failures for unavailable core channels and preserve a usable core profile when no latest video exists or enrichment fails after the profile succeeds.

**Independent Test**: Exercise empty and unavailable core results, core access/capacity/source failures, no uploads playlist, empty or malformed latest-item data, and post-profile access/capacity/source failures. Verify the exact whole-request categories or the successful `unavailable`/`partial` enrichment state with no unsafe details.

### Red - Tests for User Story 3

- [X] T021 [P] [US3] Add failing unit tests for empty core results, unavailable core lookup mapping, and safe translation of core authorization, quota, and source failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T022 [P] [US3] Add failing unit tests for no uploads-playlist identifier, empty playlist items, malformed or missing publication timestamps, exactly one playlist-item call, and safe partial enrichment after playlist authorization, quota, or source failure in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`
- [X] T023 [P] [US3] Add failing contract and integration tests for safe whole-request error guidance, `enrichment.status` values, `partial_enrichment_failure` with a safe cause category, and invoked partial results in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green - Implementation for User Story 3

- [X] T024 [US3] Implement sanitized core lookup error translation to `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T025 [US3] Implement `unavailable` latest-enrichment state for absent uploads or timestamp data and `partial` enrichment state with `partial_enrichment_failure` plus a safe cause category for post-profile dependency failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`
- [X] T026 [US3] Add or update reStructuredText docstrings for every new or modified error-mapping and enrichment-state Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`

### Refactor - User Story 3

- [X] T027 [US3] Refactor local safe-error and enrichment-state helpers while preserving sanitized details and one-channel/two-read boundedness, then run the focused US3 unit, contract, integration, and routing checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

**Checkpoint**: Clients receive either a safe whole-request failure or a complete/safely partial channel profile; no invalid, unavailable, or enrichment failure leaks private or internal data.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete documentation, review safety boundaries, and capture final repository-wide evidence.

- [X] T028 Update the published `channels_getChannel` tool description, response shape, heuristic caveats, bounded enrichment, and safe error guidance in `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`
- [X] T029 [P] Review all changed channel-detail Python functions for complete reStructuredText docstrings and all public examples/errors for secrets, owner context, raw payloads, signed links, and non-public contacts in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/contracts/channels-get-channel-contract.md`
- [X] T030 Run the feature quickstart verification and reconcile any documentation or focused-test mismatch in `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/quickstart.md`
- [X] T031 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failing repository test before completing the feature
- [X] T032 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`, fix every reported issue, and rerun the required focused checks documented in `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/quickstart.md`
- [X] T033 Re-run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` after final fixes and record passing completion evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 Setup
  -> Phase 2 Foundational public boundary
      -> Phase 3 US1: core channel details (MVP)
          -> Phase 4 US2: contacts and classification
          -> Phase 5 US3: unavailable and partial enrichment
              -> Phase 6 Polish and full verification
```

### User Story Dependencies

- **User Story 1 (P1)**: Begins after the shared public-boundary phase. It is the MVP and establishes the executable core result used by later enhancements.
- **User Story 2 (P2)**: Depends on US1's stable channel profile and provenance map, but is independently testable by injecting public profile material into the completed core flow.
- **User Story 3 (P3)**: Depends on US1's core lookup and successful enrichment seam, but is independently testable through controlled empty/error core and playlist responses. It can proceed in parallel with US2 after US1 when agents coordinate edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.

### Within Each User Story

- Complete every Red task and confirm it fails before starting its related Green task.
- Add only the minimum code necessary to make that story's Red tests pass.
- Add or update reStructuredText docstrings for every changed Python function before Refactor.
- Run the listed focused tests after refactoring; do not mark the feature complete until the Phase 6 full suite passes.

### Parallel Opportunities

- T002 and T003 can run in parallel because they change distinct test surfaces.
- T007, T008, and T009 can run in parallel before any US1 implementation task.
- T014, T015, and T016 can run in parallel before US2 implementation tasks.
- T021, T022, and T023 can run in parallel before US3 implementation tasks.
- After US1, US2 and US3 test design can proceed in parallel. Coordinate implementation because both extend the channels family module and its focused unit test file.
- T029 can run in parallel with the documentation update in T028 once implementation is stable.

## Parallel Execution Examples

### User Story 1

```text
Task: "T007 [US1] core validation/normalization tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py"
Task: "T008 [US1] contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py"
Task: "T009 [US1] injected registration test in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py"
```

### User Story 2

```text
Task: "T014 [US2] contact-extraction tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py"
Task: "T016 [US2] heuristic-contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py"
```

### User Story 3

```text
Task: "T021 [US3] core-error tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py"
Task: "T023 [US3] partial-result contract and integration tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2 so the descriptor is concrete and registered.
2. Complete Phase 3 to deliver one normalized channel profile with bounded successful latest-video enrichment.
3. Run the US1 focused tests and demonstrate the result through injected descriptor registration.
4. Do not expose contact or creator/brand inferences until their explicit safety and provenance tests are passing.

### Incremental Delivery

1. Setup and foundational public boundary establish a concrete, safe MCP registration path.
2. US1 delivers the core single-channel research result.
3. US2 adds public-only contact context and cautious type classification without changing core semantics.
4. US3 adds safe unavailable and partial behavior while retaining a successfully retrieved core profile.
5. Polish updates public documentation and completes full-suite/lint evidence.

## Task Summary

| Area | Tasks |
| --- | ---: |
| Setup | 1 |
| Foundational | 5 |
| User Story 1 (P1) | 7 |
| User Story 2 (P2) | 7 |
| User Story 3 (P3) | 7 |
| Polish and cross-cutting | 6 |
| **Total** | **33** |

All 33 tasks use the required checkbox, sequential task ID, optional `[P]` marker only where parallel work is identified, story label for every user-story task, and an exact file path.
