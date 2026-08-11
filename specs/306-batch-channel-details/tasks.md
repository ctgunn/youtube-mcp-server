# Tasks: Batch Channel Details

**Input**: Design documents from `/specs/306-batch-channel-details/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/channels-get-channels-contract.md`, and `quickstart.md`

**Tests**: Tests are mandatory. Add failing tests before implementation for every phase and story. Completion requires `python3 -m pytest` and `python3 -m ruff check .` to pass after the final code changes. Every new or modified Python function must have a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each increment has an explicit, independently testable outcome.

## Phase 1: Setup (Existing Project Baseline)

**Purpose**: Confirm the existing composed-channel behavior and registration baseline before adding the batch tool.

- [X] T001 Run the existing YT-305 focused unit and contract suites in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py` and record the passing baseline in pull-request evidence.
- [X] T002 [P] Run the existing composed-tool registration suites in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` and record the passing baseline in pull-request evidence.

---

## Phase 2: Foundational Batch Contract Prerequisites

**Purpose**: Establish shared batch argument validation and safe contract primitives before any public batch behavior is implemented.

**⚠️ CRITICAL**: Complete this phase before implementing the user-story phases.

- [X] T003 Add failing validation tests for a 1–50 item trimmed, distinct `channelIds` list; unknown fields; invalid `parts`; and invalid `includeLatestUpload` values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, then run them and confirm they fail before implementation.
- [X] T004 Implement the `channels_getChannels` constants, public error type or safe-error reuse, supported-parts validation, defaulting, and request normalization in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` so the Phase 2 tests pass.
- [X] T005 Add or update reStructuredText docstrings with `:param:`, `:return:`, and `:raises:` details for every new or modified batch-validation function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T006 Refactor the shared validation and safe-error helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` without changing YT-305 behavior, then rerun the focused tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.

**Checkpoint**: Batch arguments have a deterministic, documented, safe validation boundary; user-story work can begin.

---

## Phase 3: User Story 1 - Retrieve Multiple Channel Details (Priority: P1) 🎯 MVP

**Goal**: Return one ordered, normalized, independently interpretable item for every requested available channel, using one bounded bulk core lookup.

**Independent Test**: Invoke `channels_getChannels` with two or more available IDs and verify that the result retains request order, uses one core lookup, has one successful item per available ID, and preserves the single-channel normalized/provenance semantics.

### Red — Tests First

- [X] T007 [P] [US1] Add failing descriptor-schema and discovery-metadata tests for `channels_getChannels`, its required `channelIds`, 1–50 limit, default `parts`, ordered result convention, and bounded bulk core lookup in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, then confirm they fail.
- [X] T008 [P] [US1] Add failing handler tests for one comma-joined core lookup, source-item indexing, caller-order reconstruction, default `snippet` normalization, provenance, and batch summary counts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, then confirm they fail.
- [X] T009 [P] [US1] Add a failing injected-descriptor registration and invocation test for `channels_getChannels` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, then confirm it fails.

### Green — Minimum Implementation

- [X] T010 [US1] Implement batch core retrieval in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`: call `channels_list` once with comma-joined IDs, index returned source items by canonical ID, rebuild items in request order, reuse the YT-305 public normalization/provenance rules for `snippet`, and calculate the documented summary partition.
- [X] T011 [US1] Add the public `channels_getChannels` metadata and executable descriptor, including the 1–50 batch bound, default `snippet` selection, ordering guarantee, and no representative-only marker, in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T012 [US1] Export the batch handler, metadata builder, and descriptor from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and add the default descriptor registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T013 [US1] Add or update complete reStructuredText docstrings for every new or modified Python function used by the P1 handler, metadata, descriptor, and registration flow in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

### Refactor and Independent Validation

- [X] T014 [US1] Refactor duplicated single- and batch-channel normalization only where behavior remains identical in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, then run the US1 unit, contract, and registration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

**Checkpoint**: P1 is a deployable MVP: clients can retrieve ordered normalized details for several available channels in one request.

---

## Phase 4: User Story 2 - Control Returned Detail and Latest-Upload Enrichment (Priority: P2)

**Goal**: Let callers select public detail groups and choose default-on or explicitly disabled latest-upload enrichment while retaining unambiguous item states.

**Independent Test**: Invoke a batch with supported `parts`, then invoke it with `includeLatestUpload` omitted and `false`; verify selected groups, default-on enrichment, zero enrichment calls when disabled, and correct `complete`, `unavailable`, or `not_requested` state.

### Red — Tests First

- [X] T015 [P] [US2] Add failing unit tests for `snippet` and `contentDetails` selection, omitted default selection, omitted/default `includeLatestUpload=true`, disabled enrichment with zero playlist-item calls, complete enrichment, no-upload unavailable enrichment, and provenance limited to returned paths in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, then confirm they fail.
- [X] T016 [P] [US2] Add failing contract tests for supported `parts`, `includeLatestUpload=true` default, per-item enrichment states, public uploads-playlist detail exposure, and at-most-one enrichment lookup per available item in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, then confirm they fail.

### Green — Minimum Implementation

- [X] T017 [US2] Implement selected-detail shaping and bounded per-item latest-upload enrichment in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`: expose only selected groups, retain identity/outcome/enrichment/provenance, make at most one one-item uploads-playlist call per available item when enabled, and emit `complete`, `unavailable`, or `not_requested` accurately.
- [X] T018 [US2] Add or update reStructuredText docstrings for every new or modified selection or enrichment function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, documenting bounds, selected-data behavior, returned states, and safe side effects.

### Refactor and Independent Validation

- [X] T019 [US2] Refactor detail-selection and enrichment-state handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` while preserving P1 results, then run the US2 unit and contract tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.

**Checkpoint**: P1 and P2 both work independently: callers can control supported details and enrichment without receiving ambiguous timestamps or unselected data.

---

## Phase 5: User Story 3 - Continue Through Individual Unavailable Channels (Priority: P3)

**Goal**: Keep usable channel items when individual IDs are unavailable or one optional enrichment fails, while keeping bulk core failures safe and request-wide.

**Independent Test**: Invoke a batch containing available, unavailable, no-upload, and enrichment-failure fixtures; verify that each ID retains its order, successful core items remain usable, partial and unavailable categories are sanitized, and summary counts partition the batch.

### Red — Tests First

- [X] T020 [P] [US3] Add failing unit tests for unavailable IDs among successful items, per-item partial enrichment categories, safe core request-wide error mapping, sanitized result content, and summary-count partitioning in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, then confirm they fail.
- [X] T021 [P] [US3] Add failing contract tests for `unavailable_resource`, `partial_enrichment_failure`, request-wide authorization/quota/upstream failures, recovery guidance, and secret-free error payloads in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, then confirm they fail.
- [X] T022 [P] [US3] Add a failing integration test that invokes the registered tool with a mixed-outcome injected batch and verifies ordered independent items and summary counts in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, then confirm it fails.

### Green — Minimum Implementation

- [X] T023 [US3] Implement safe per-item unavailable and partial-enrichment outcomes plus request-wide bulk-core error mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`; preserve usable core fields, omit unavailable timestamps, disclose only safe cause categories, and never reveal source availability reasons or sensitive details.
- [X] T024 [US3] Add or update reStructuredText docstrings for every new or modified outcome, error-mapping, summary, and sanitization function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.

### Refactor and Independent Validation

- [X] T025 [US3] Refactor safe outcome and summary construction in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` without altering YT-305 behavior, then run the US3 unit, contract, and integration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

**Checkpoint**: All three stories are independently testable; a bad ID or optional enrichment failure cannot discard unrelated usable results.

---

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Verify compatibility, documentation, security, and final repository quality.

- [X] T026 [P] Verify the discovery and invocation examples in `/Users/ctgunn/Projects/youtube-mcp-server/specs/306-batch-channel-details/quickstart.md` against the registered implementation, and update that file if any documented request, default, result state, or verification command differs.
- [X] T027 [P] Review all functions changed in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` for complete reStructuredText docstrings and for absence of credentials, private owner context, raw source bodies, traces, signed links, and non-public contacts.
- [X] T028 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` after all code changes and record the full-suite passing result.
- [X] T029 Run `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` after all code changes and record the passing result.
- [X] T030 Resolve every failure from the full-suite and lint runs in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the affected files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`, then rerun T028 and T029 until both pass.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1** has no code dependencies and establishes the YT-305 regression baseline.
- **Phase 2** depends on Phase 1 and blocks all story implementation because all stories use the batch argument and safe-error boundary.
- **US1 (Phase 3)** depends on Phase 2 and delivers the MVP descriptor, bulk core lookup, ordering, normalization, and registration.
- **US2 (Phase 4)** depends on US1's descriptor and handler, then adds independently verifiable selected-detail and enrichment behavior.
- **US3 (Phase 5)** depends on US1's ordered item result, then adds independently verifiable mixed safe outcomes. Its Red tests may be prepared in parallel with US2 tests, but source changes share `channels.py` and must be integrated sequentially.
- **Phase 6** depends on every desired user-story phase being complete.

### User Story Completion Graph

```text
Setup → Foundational → US1 (MVP) ─┬→ US2 → Polish
                                 └→ US3 → Polish
```

### Within Each User Story

1. Complete every Red test task and run it to prove the behavior fails.
2. Complete Green implementation tasks in source, exports, and registration.
3. Add or update all required reStructuredText docstrings.
4. Refactor only with focused tests green, then run the listed independent validation.

## Parallel Execution Examples

### User Story 1

```text
Parallel Red work after T006:
- T007: contract discovery/schema tests in tests/contract/test_youtube_composed_channels_contract.py
- T008: handler behavior tests in tests/unit/test_youtube_composed_channels.py
- T009: registered invocation test in tests/integration/test_youtube_composed_tool_registration.py

Then complete T010 → T014 sequentially because they modify the shared composed-tool and registration path.
```

### User Story 2

```text
Parallel Red work after T014:
- T015: selection and enrichment unit tests in tests/unit/test_youtube_composed_channels.py
- T016: selection/enrichment contract tests in tests/contract/test_youtube_composed_channels_contract.py

Then complete T017 → T019 sequentially in src/mcp_server/tools/youtube_composed/channels.py.
```

### User Story 3

```text
Parallel Red work after T014:
- T020: outcome and sanitization unit tests in tests/unit/test_youtube_composed_channels.py
- T021: safe-error contract tests in tests/contract/test_youtube_composed_channels_contract.py
- T022: mixed-outcome registration test in tests/integration/test_youtube_composed_tool_registration.py

After the US2 source integration is complete, finish T023 → T025 sequentially in src/mcp_server/tools/youtube_composed/channels.py.
```

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2.
2. Complete US1 through T014.
3. Validate the P1 independent test: two available IDs produce one ordered normalized item each through the registered public tool.
4. Stop for review or demonstrate the MVP before adding selection/enrichment and mixed-outcome increments.

### Incremental Delivery

1. Deliver US1 for efficient ordered batch details.
2. Deliver US2 for request-scoped public detail selection and deterministic latest-upload controls.
3. Deliver US3 for resilient mixed batches and safe failure semantics.
4. Complete Phase 6 only after all desired increments are integrated; never treat focused tests as final completion evidence.

## Task Summary

| Area | Tasks |
| --- | ---: |
| Setup | 2 |
| Foundational | 4 |
| User Story 1 (P1) | 8 |
| User Story 2 (P2) | 5 |
| User Story 3 (P3) | 6 |
| Polish and cross-cutting | 5 |
| **Total** | **30** |

All 30 tasks use the required `- [ ] T### [P?] [US?] Description with absolute path` checklist format. Story task counts include only tasks labeled `[US1]`, `[US2]`, or `[US3]`; setup, foundational, and polish tasks intentionally have no story label.
