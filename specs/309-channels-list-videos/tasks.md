# Tasks: YT-309 Channel Video Listing

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [channels-list-videos-contract.md](contracts/channels-list-videos-contract.md), [quickstart.md](quickstart.md)

**Tests**: Test tasks are required. Each story begins with failing tests (Red), adds only the behavior necessary to pass them (Green), then refactors while preserving passing focused tests. Feature completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` after the final code change.

**Documentation**: Every new or changed Python function, including test doubles, must have a reStructuredText docstring describing purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.

**Organization**: Tasks are grouped by independently testable user story in priority order. The feature uses the existing single Python MCP service and extends its composed channels family.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes a different file and has no dependency on another incomplete task.
- **[Story]**: Maps the task to a user story from [spec.md](spec.md).

## Phase 1: Setup (Existing Service Orientation)

**Purpose**: Establish the current seams and a passing baseline; no project, dependency, storage, or infrastructure initialization is required.

- [X] T001 [P] Review the public request/result, ordering, error, and provenance rules in `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/contracts/channels-list-videos-contract.md` before changing code.
- [X] T002 [P] Run the existing composed-channel and default-registration tests as a clean baseline: `PYTHONPATH=src python3 -m pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T003 [P] Inspect the established dependency-injection, safe-error, export, and default-registration seams in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

---

## Phase 2: Foundational (Shared Preconditions)

**Purpose**: Confirm the existing lower-layer behavior that blocks every user-story implementation. No new shared infrastructure is needed.

- [X] T004 Verify the public uploads-collection lookup arguments, source item order, and safe lower-layer error types against `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py`.
- [X] T005 Run the lower-layer channel and playlist-item regression checks before composed-tool work: `PYTHONPATH=src python3 -m pytest /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_common_contract.py`.

**Checkpoint**: Existing channel and playlist-item handlers, dispatcher injection, safe error serialization, and test seams are confirmed; user-story implementation can begin.

---

## Phase 3: User Story 1 - List a Channel's Videos (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client retrieve a bounded, distinct, source-ordered collection of publicly available videos for one known channel.

**Independent Test**: Invoke the registered descriptor with a controlled available channel and uploads collection; verify one channel lookup and at most one collection lookup, no more than the requested number of distinct videos in first-occurrence source order, documented public item fields, and a successful empty collection for a channel with no uploads.

### Red - Write Failing Tests First

- [X] T006 [P] [US1] Add failing validator and handler tests for trimmed `channelId`, unknown-field rejection, default/minimum/maximum `maxResults`, rejected boolean/fraction/out-of-range limits, exact two-read dependency calls, item extraction, first-occurrence de-duplication before cap, source-order preservation, and successful empty results in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T007 [P] [US1] Add failing executable-discovery contract tests for `channels_listVideos`, its exact input schema, default/bounds, `source_ordered_collection` boundary, lower-layer dependencies, source-versus-normalized provenance, no-ranking disclosure, and absence of `representativeOnly` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T008 [P] [US1] Add failing injected-descriptor execution and default-dispatcher registration tests for a populated and empty channel uploads collection in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T009 [US1] Run the new focused US1 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`; confirm they fail for the missing `channels_listVideos` behavior before implementing it.

### Green - Implement the Minimum Viable Listing

- [X] T010 [US1] Add `channels_listVideos` constants, public input schema, safe public error type, strict request validator, uploads-collection reference handling, video-item normalizer, ordered first-occurrence de-duplication, result/provenance builders, handler, metadata builder, and executable descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T011 [US1] Export the `channels_listVideos` constants, safe error type, validator, metadata builder, handler, and descriptor through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`.
- [X] T012 [US1] Default-register `channels_listVideos` with existing configured `channels_list` and `playlist_items_list` handler injection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T013 [US1] Add or update reStructuredText docstrings for every new or changed Python function and test double in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the US1 tests.

### Refactor - Preserve Behavior and Verify the MVP

- [X] T014 [US1] Refactor only local duplicate extraction, provenance, and result-shaping logic for `channels_listVideos` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, preserving the one-channel/one-collection bound and all US1 behavior.
- [X] T015 [US1] Run the focused MVP checks from `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/quickstart.md` and confirm all US1 unit, contract, injected-registration, and default-registration cases pass.

**Checkpoint**: `channels_listVideos` is discoverable and independently usable for bounded public channel-video listing, including an accessible empty result.

---

## Phase 4: User Story 2 - Understand Result Meaning and Ordering (Priority: P2)

**Goal**: Let an MCP client determine from discovery metadata and a result which values are source-preserved or normalized and why the collection is not relevance-ranked.

**Independent Test**: Inspect the executable descriptor and a controlled successful result; verify uploads-collection source, source-order-at-request-time context, applied limit, no-ranking declaration, public-content boundary, request-time variability, and field-provenance labels without requiring any search result.

### Red - Write Failing Tests First

- [X] T016 [P] [US2] Add failing result-shape tests for `appliedInputs`, `collectionContext`, and field-provenance completeness, including no-ranking and request-time source-order declarations, in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T017 [P] [US2] Add failing discovery-metadata tests for ordering semantics, public-read/capacity caveats, source-order behavior, no-ranking guidance, request-time variability, empty-result policy, and recovery guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T018 [P] [US2] Add a failing registered-descriptor test proving callers can distinguish `channels_listVideos` from relevance-ranked search through discovered metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.
- [X] T019 [US2] Run the new US2 unit, contract, and descriptor tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`; confirm they fail before changing result or discovery behavior.

### Green - Expose Meaningful Collection Context

- [X] T020 [US2] Complete the `channels_listVideos` response context, provenance mapping, and executable metadata for source order, no-ranking behavior, request-time variability, public-content boundary, bounded dependencies, and recovery guidance in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T021 [US2] Add or update reStructuredText docstrings for every US2-modified Python function and test double in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and the US2 test files.

### Refactor - Keep Contract and Behavior Aligned

- [X] T022 [US2] Reconcile result field names, provenance categories, ordering terminology, and caller guidance between `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/contracts/channels-list-videos-contract.md` without changing the additive public scope.
- [X] T023 [US2] Run the focused US2 unit, contract, and registration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and keep all US1 tests green.

**Checkpoint**: Callers can identify source-preserved values, normalized collection context, and source-order/no-ranking semantics from discovery and results alone.

---

## Phase 5: User Story 3 - Receive Safe Outcomes for Unavailable Content (Priority: P3)

**Goal**: Return safe, distinguishable outcomes for invalid requests, unavailable channels, public-read access limits, exhausted capacity, source failures, and known item-level availability omissions.

**Independent Test**: Exercise malformed input, an empty/malformed core channel result, a missing uploads collection reference, lower-layer unavailable/access/capacity/source errors, an empty collection, and a known item-level omission. Verify documented safe category or successful empty/partial result, no unsafe diagnostics, and no fabricated or placeholder video.

### Red - Write Failing Tests First

- [X] T024 [P] [US3] Add failing handler tests for safe mapping of malformed input, unavailable core channel, missing uploads reference, empty collection, core and required collection access/capacity/source failures, and known item-level omissions without leaking unsafe details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`.
- [X] T025 [P] [US3] Add failing contract tests for the complete safe error taxonomy, empty-result policy, partial-availability policy, sanitized metadata, and caller recovery guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`.
- [X] T026 [P] [US3] Add failing protocol-routing tests for `channels_listVideos` safe error category serialization and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- [X] T027 [US3] Run the new US3 handler, contract, and protocol tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`; confirm they fail before changing safe-outcome behavior.

### Green - Implement Safe Outcome Behavior

- [X] T028 [US3] Add local safe translation for channel and required uploads-collection errors; return a successful empty result for a missing uploads reference or empty collection; omit known unavailable items and emit only safe aggregate `partialAvailability` context in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`.
- [X] T029 [US3] Update the default registered descriptor's error metadata and guidance for every US3 safe outcome in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` and verify the existing registration path in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` needs no protocol or transport change.
- [X] T030 [US3] Add or update reStructuredText docstrings for every US3-modified Python function and test double in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and the US3 test files.

### Refactor - Preserve Safe Boundaries

- [X] T031 [US3] Refactor `channels_listVideos` error mapping and partial-availability helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` to reuse existing sanitization without exposing lower-layer categories or diagnostics.
- [X] T032 [US3] Run the focused US3 unit, contract, protocol, and default-registration checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`; keep US1 and US2 behavior green.

**Checkpoint**: The tool distinguishes successful empty listings from safe failures and exposes no private, credential, raw-source, or internal diagnostic data.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile documentation and evidence across all stories, then complete mandatory full-suite verification.

- [X] T033 [P] Reconcile the implemented public schema, result example, provenance, ordering, partial-availability, error, and discovery wording in `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/contracts/channels-list-videos-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/quickstart.md`.
- [X] T034 [P] Review every changed Python function and test double for required reStructuredText docstrings in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`.
- [X] T035 Run the full focused verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/quickstart.md` and fix every feature-related failure in the referenced `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` paths.
- [X] T036 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every reported issue in the changed `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/` paths.
- [X] T037 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` after the final code change, fix any failures, and rerun it until the complete repository suite passes.
- [X] T038 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` after all test fixes and confirm the final changed Python code remains lint-clean.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1: Setup
  -> Phase 2: Foundational lower-layer confirmation
      -> Phase 3: US1 (MVP listing)
          -> Phase 4: US2 (result meaning and ordering)
              -> Phase 5: US3 (safe unavailable-content outcomes)
                  -> Phase 6: Polish and final verification
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2. It delivers the executable descriptor, bounded two-read listing behavior, and default registration; it is the recommended MVP.
- **US2 (P2)**: Starts after US1 because it completes result and metadata semantics on the same descriptor and handler. It remains independently testable using a controlled successful listing.
- **US3 (P3)**: Starts after US1 and is scheduled after US2 to avoid simultaneous edits to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`. It remains independently testable through controlled safe outcomes.

### Within Each User Story

1. Complete all Red test tasks and confirm their expected failure before Green tasks.
2. Complete Green implementation and required reStructuredText docstring tasks.
3. Complete the Refactor task and rerun that story's focused tests.
4. Do not consider the feature complete until Phase 6's full repository suite and final lint checks pass.

## Parallel Opportunities

- **Setup**: T001–T003 can run in parallel because they are read-only orientation and baseline tasks.
- **US1 Red**: T006, T007, and T008 can run in parallel because they change separate unit, contract, and integration test files.
- **US2 Red**: T016, T017, and T018 can run in parallel because they change separate unit, contract, and integration test files.
- **US3 Red**: T024, T025, and T026 can run in parallel because they change separate unit, contract, and protocol test files.
- **Polish review**: T033 and T034 can run in parallel because they update feature documentation and audit Python documentation separately.
- Green/refactor tasks touching `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py` are intentionally sequential.

### Parallel Example: User Story 1

```text
Task: "T006 — Add US1 handler and validation Red tests in tests/unit/test_youtube_composed_channels.py"
Task: "T007 — Add US1 discovery-contract Red tests in tests/contract/test_youtube_composed_channels_contract.py"
Task: "T008 — Add US1 injected/default-registration Red tests in tests/integration/"
```

### Parallel Example: User Story 2

```text
Task: "T016 — Add US2 response-context Red tests in tests/unit/test_youtube_composed_channels.py"
Task: "T017 — Add US2 ordering/discovery Red tests in tests/contract/test_youtube_composed_channels_contract.py"
Task: "T018 — Add US2 descriptor discovery Red test in tests/integration/test_youtube_composed_tool_registration.py"
```

### Parallel Example: User Story 3

```text
Task: "T024 — Add US3 safe-outcome Red tests in tests/unit/test_youtube_composed_channels.py"
Task: "T025 — Add US3 error-policy Red tests in tests/contract/test_youtube_composed_channels_contract.py"
Task: "T026 — Add US3 protocol-routing Red tests in tests/unit/test_method_routing.py"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete the US1 Red tasks, confirm they fail, then complete its Green, docstring, and Refactor tasks.
3. Run T015 to validate bounded, source-ordered public listing independently.
4. Demo or deliver the additive descriptor if ready; do not claim feature completion until final cross-cutting verification passes.

### Incremental Delivery

1. Setup and foundational confirmation establish reuse boundaries.
2. US1 adds usable bounded public channel-video listing.
3. US2 makes ordering, provenance, and no-ranking semantics self-explanatory to MCP clients.
4. US3 adds complete safe-outcome and partial-availability behavior.
5. Polish reconciles documentation and proves full-suite regression safety.

### Task Validation

- **Total tasks**: 38.
- **US1**: 10 tasks (T006–T015); independently verifies bounded ordered listing and an empty accessible collection.
- **US2**: 8 tasks (T016–T023); independently verifies response/discovery meaning and ordering.
- **US3**: 9 tasks (T024–T032); independently verifies safe unavailable-content outcomes.
- Every task uses the required checkbox, sequential task ID, valid optional `[P]` marker, story label for story-phase tasks, and one or more absolute file paths.
- No task alters lower-layer contracts, storage, transport, authentication flow, or unrelated tool families.
