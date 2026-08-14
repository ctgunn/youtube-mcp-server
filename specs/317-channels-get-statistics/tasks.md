# Tasks: YT-317 Channel Statistics

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/data-model.md), [contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/contracts/channels-get-statistics-contract.md), and [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/quickstart.md)

**Tests**: Tests are mandatory. Use Red-Green-Refactor for every story, add reStructuredText docstrings to every new or modified Python function, and complete with passing full-suite and Ruff checks.

**Organization**: Tasks are grouped by independently testable user story. The tool descriptor established by US1 is the prerequisite for the deeper result semantics in US2 and failure behavior in US3.

## Phase 1: Setup

**Purpose**: Confirm the feature's additive boundary and the existing extension seams before changing code.

- [X] T001 Review the accepted public input, result, provenance, hiddenness, safe-error, and rollback rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/contracts/channels-get-statistics-contract.md`.
- [X] T002 [P] Review the existing composed-channel, lower-level channel lookup, package-export, and default-registration seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

---

## Phase 2: Foundational

**Purpose**: Verify the existing reusable lower-layer and testing foundations; no new shared infrastructure is required.

- [X] T003 Run the pre-change channel and registration baseline in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` with `PYTHONPATH=src python3 -m pytest`.
- [X] T004 Verify the reusable `channels_list` path accepts exactly one public ID selector plus `part="statistics"`, returns its near-raw item collection, and maps safe lower-layer failures in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.

**Checkpoint**: Existing lower-layer lookup, sanitization, and dispatcher seams are understood and passing; User Story 1 can begin.

---

## Phase 3: User Story 1 - Retrieve Available Channel Statistics (Priority: P1) 🎯 MVP

**Goal**: Deliver `channels_getStatistics` for exactly one valid channel, returning source-provided subscriber, video, and view counts in a stable normalized result.

**Independent Test**: Register an injected descriptor, call it with a trimmed `channelId`, and verify one exact lower-layer request of `{"id": "UC123", "part": "statistics"}` plus all three available count values, including a reported zero.

### Red - Failing Tests

- [X] T005 [P] [US1] Add failing validation and successful-normalization unit tests for non-object, missing, blank, non-text, and unknown `channelId` inputs; trimming; one exact statistics lookup; all three available metric mappings; and reported zero preservation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T006 [P] [US1] Add failing public-contract tests for the executable `channels_getStatistics` descriptor, exact one-field schema, normalized-retrieval boundary, `channels.list` dependency, expected metrics, provenance, and absence of `representativeOnly` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T007 [P] [US1] Add failing injected-descriptor and default-registry tests proving discovery, one-call invocation, and default dispatcher presence in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.

### Green - Minimum Implementation

- [X] T008 [US1] Add the statistics tool constant, strict input schema, safe error type, metadata builder, validator, one-lookup argument builder, source-count normalizer, result normalizer, handler, and descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` so valid requests make one `channels_list` statistics lookup and return source-provided available counts.
- [X] T009 [US1] Export the concrete channel-statistics schema, error, validator, normalizer, metadata builder, handler, and descriptor from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and register the descriptor with an injected `build_channels_list_handler(**conditional_dependencies)` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T010 [US1] Add or update reStructuredText docstrings for every new or modified Python function, nested handler, and test helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the US1 test files.

### Refactor - Preserve Behavior

- [X] T011 [US1] Run the US1-focused unit, contract, and integration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`; refactor only duplicated local statistics shaping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` while keeping the tests green.

**Checkpoint**: `channels_getStatistics` is discoverable and independently returns all available expected statistics for one channel; this is the MVP.

---

## Phase 4: User Story 2 - Understand Hidden or Unavailable Counts (Priority: P2)

**Goal**: Make hidden subscriber counts and unavailable source data unambiguous without fabricating a numeric value.

**Independent Test**: Invoke the US1 descriptor against controlled source results containing `hiddenSubscriberCount=true`, missing or malformed statistics, individual missing metrics, and a reported zero; verify the correct `available`, `hidden`, or `unavailable` state and absence of a numeric value for non-reported metrics.

### Red - Failing Tests

- [X] T012 [P] [US2] Add failing unit tests for hidden-subscriber precedence over an inconsistent supplied subscriber value, missing or malformed statistics objects, absent video or view metrics, reported zero, and no `value` key for hidden or unavailable metrics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T013 [P] [US2] Add failing contract tests for all three metric state rules, `hiddenSubscriberCount` exclusion from results, source caveats, and value/state provenance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.

### Green - Minimum Implementation

- [X] T014 [US2] Update the expected-metric and result-normalization logic in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` so `hiddenSubscriberCount=true` yields a hidden subscriber metric with no value, valid source counts including zero remain available, and malformed or absent metrics are unavailable with no value.
- [X] T015 [US2] Update reStructuredText docstrings for every changed metric-normalization function and test helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.

### Refactor - Preserve Behavior

- [X] T016 [US2] Run the US2-focused unit and contract tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`; consolidate repeated metric-state construction in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` without changing the public result contract.

**Checkpoint**: A client can independently distinguish a reported zero, a source-flagged hidden subscriber count, and unavailable statistics.

---

## Phase 5: User Story 3 - Receive Actionable Lookup Outcomes (Priority: P3)

**Goal**: Return safe, distinct outcomes for invalid input, unavailable channels, authorization-sensitive access, quota exhaustion, and source failures.

**Independent Test**: Invoke the registered tool with invalid arguments, empty or malformed source results, and injected lower-layer errors for each category; verify the documented public category and that no sensitive diagnostic survives routing.

### Red - Failing Tests

- [X] T017 [P] [US3] Add failing unit tests mapping empty and malformed channel result collections to `unavailable_resource` and mapping lower `ChannelsListToolError` categories for unavailable, authorization, quota, and source failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T018 [P] [US3] Add failing integration and protocol-routing tests that call the injected descriptor through the dispatcher, verify safe category serialization, and prove token or secret-like lower-layer details are absent in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T019 [P] [US3] Add failing public-contract tests for the complete safe error-category and caller-guidance set in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.

### Green - Minimum Implementation

- [X] T020 [US3] Add the local lower-layer error translator and unavailable-result handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, reusing the existing safe upstream message and detail-sanitization utilities without exposing raw source payloads or diagnostics.
- [X] T021 [US3] Update reStructuredText docstrings for every changed error-mapping function, handler, and test helper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

### Refactor - Preserve Behavior

- [X] T022 [US3] Run the US3-focused unit, contract, integration, and protocol-routing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`; remove only duplicated local safe-error translation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` while retaining all safe outcomes.

**Checkpoint**: All documented errors are safe and actionable, distinct from a successful result whose individual metrics are hidden or unavailable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate documentation, contract alignment, regressions, and the final quality gates.

- [X] T023 [P] Reconcile the public examples, source caveats, expected metrics, state semantics, error categories, and verification commands across `/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/contracts/channels-get-statistics-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/quickstart.md`.
- [X] T024 [P] Review all changed Python functions and test helpers for complete reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`.
- [X] T025 Run the focused verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/317-channels-get-statistics/quickstart.md` against the listed channel, contract, registration, and routing test files; fix only YT-317 regressions in the exact failing file paths.
- [X] T026 Run `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`; fix every failure in its reported file path before marking YT-317 complete.

---

## Dependencies & Execution Order

### Phase Dependencies

`Phase 1 Setup` → `Phase 2 Foundational` → `Phase 3 US1 (MVP)` → `Phase 4 US2` and `Phase 5 US3` → `Phase 6 Polish`

US2 and US3 share the completed US1 descriptor and handler. Their Red test tasks can be prepared independently after US1, but their Green and Refactor tasks both modify `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and must be serialized to avoid conflicts.

### User Story Dependencies

- **US1 (P1)**: Starts after foundational verification and creates the executable descriptor, export, and registration seam.
- **US2 (P2)**: Starts after US1 and extends only the result-state semantics; its acceptance test remains an isolated call using a controlled lower-layer response.
- **US3 (P3)**: Starts after US1 and extends only safe error behavior; its acceptance test remains an isolated dispatcher call with injected lower-layer failures.

### Parallel Opportunities

- T002 can run alongside T001.
- Within US1, T005, T006, and T007 target different test files and can run in parallel before T008.
- Within US2, T012 and T013 target different test files and can run in parallel before T014.
- Within US3, T017, T018, and T019 target different test files and can run in parallel before T020.
- T023 and T024 can run in parallel after all story phases; T025 and T026 remain sequential final quality gates.

## Parallel Execution Examples

### User Story 1

```text
T005: tests/unit/test_youtube_composed_channels.py
T006: tests/contract/test_youtube_composed_channels_contract.py
T007: tests/integration/test_youtube_composed_tool_registration.py and tests/integration/test_youtube_tool_registration.py
```

### User Story 2

```text
T012: tests/unit/test_youtube_composed_channels.py
T013: tests/contract/test_youtube_composed_channels_contract.py
```

### User Story 3

```text
T017: tests/unit/test_youtube_composed_channels.py
T018: tests/integration/test_youtube_composed_tool_registration.py and tests/unit/test_method_routing.py
T019: tests/contract/test_youtube_composed_channels_contract.py
```

## Implementation Strategy

### MVP First

1. Complete setup and foundational verification.
2. Complete US1 Red tasks, then the minimum descriptor, export, registration, documentation, and refactor tasks.
3. Stop and validate the US1 independent test: one trimmed channel ID yields one statistics lookup and a normalized result containing all source-provided expected counts.

### Incremental Delivery

1. Deliver US1 for normal available counts.
2. Deliver US2 for explicit hidden and unavailable semantics without changing US1's input or available-count behavior.
3. Deliver US3 for safe error outcomes without changing successful result semantics.
4. Complete the documentation audit, focused checks, full suite, and Ruff before completion.

## Notes

- Every task uses the required checklist format: checkbox, sequential ID, optional `[P]`, story label for story work, and exact file path.
- Write and observe failing Red tests before the related Green task.
- Do not change the lower-level `channels_list` contract, source execution path, or its default empty-result fixture solely for this feature.
- Do not treat targeted test runs as final completion evidence; T026 is required before the feature is complete.
