# Tasks: YT-312 Video Statistics

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/data-model.md), and [videos-get-statistics-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/contracts/videos-get-statistics-contract.md)

**Tests**: Tests are mandatory. Add failing tests before each implementation increment; preserve reStructuredText docstrings for every new or changed Python function; run the full repository suite after the final code change.

**Organization**: Tasks are grouped by independently testable user story and follow Red → Green → Refactor.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing implementation seams and documented public contract before changing code. No new project initialization or dependency installation is required.

- [X] T001 Review the exact input, result, availability, source-caveat, safe-error, and rollback requirements in `/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/spec.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/contracts/videos-get-statistics-contract.md`
- [X] T002 Run the existing video-family baseline tests from `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py` with `PYTHONPATH=src python3 -m pytest` before adding YT-312 tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify the existing Layer 3 catalog, dispatcher, lower-level video lookup, safe-error, and docstring seams that all stories rely on.

**⚠️ CRITICAL**: Complete this phase before starting user-story implementation.

- [X] T003 Verify `videos_getStatistics` remains assigned to the `videos` family in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/contracts.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/families.py`
- [X] T004 Verify the direct `videos_list` handler accepts one `id` with `part=statistics` and preserves source statistics in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T005 Verify the public dispatcher can register composed-video descriptors and safely serialize the documented Layer 3 failure categories in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`

**Checkpoint**: Existing shared seams are confirmed; user-story work may now begin.

---

## Phase 3: User Story 1 - Retrieve Available Video Statistics (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client retrieve a stable normalized set of available view, like, comment, and favorite counts for one video.

**Independent Test**: Inject a lower-level lookup that returns one video with all four source statistics, invoke `videos_getStatistics` with a valid `videoId`, and verify one `part=statistics` lookup plus a normalized result tied to that video. Repeat with a source-reported zero and verify it remains an available value.

### Red - Tests First

- [X] T006 [P] [US1] Add failing unit tests for nonblank `videoId` validation, exactly one `{"id": videoId, "part": "statistics"}` lookup, all expected available metric mappings, and preservation of a source-reported zero in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`
- [X] T007 [P] [US1] Add failing contract tests for the `videos_getStatistics` name, `videoId`-only schema, `videos.list` normalized-retrieval boundary, expected metric provenance, one-unit quota note, and no representative-only marker in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`
- [X] T008 [P] [US1] Add a failing descriptor registration-and-invocation test using an injected successful lookup in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green - Minimum Implementation

- [X] T009 [US1] Implement the `videos_getStatistics` constants, `videoId`-only schema, public error type, argument validator, one-lookup request builder, available-count normalizer, metadata builder, handler, and descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T010 [US1] Export the concrete statistics tool symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py` and default-register the descriptor with an injected `videos_list` handler in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T011 [US1] Update the default lower-level video representative result with safe `statistics` data only if the default-registration success test requires it in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`
- [X] T012 [US1] Add or update reStructuredText docstrings for every new or modified function and test helper introduced for available-statistics retrieval in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Refactor and Independent Validation

- [X] T013 [US1] Refactor only duplicate local video-statistics validation and source-count extraction while preserving the existing videos-family boundaries and passing US1 tests in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T014 [US1] Run the US1 unit, contract, and injected-descriptor integration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` with `PYTHONPATH=src python3 -m pytest`

**Checkpoint**: `videos_getStatistics` can return all source-provided expected statistics for one video, including a true zero, through its concrete MCP descriptor.

---

## Phase 4: User Story 2 - Understand Hidden or Unavailable Counts (Priority: P2)

**Goal**: Let a client distinguish a reported count, including zero, from an expected metric the source did not provide.

**Independent Test**: Inject a successful video lookup with one or more expected source fields absent, invoke `videos_getStatistics`, and verify every expected metric appears with `available` or `unavailable` state; unavailable metrics have no numeric value and no fabricated reason.

### Red - Tests First

- [X] T015 [P] [US2] Add failing unit tests for sparse or absent source `statistics`, explicit unavailable metric entries without `value`, available zero, and no fabricated numeric values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`
- [X] T016 [P] [US2] Add failing contract tests for all four expected metrics, `available` versus `unavailable` states, source-provided versus normalized provenance, favorite-count caveat, and exclusion of `dislikeCount` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`

### Green - Minimum Implementation

- [X] T017 [US2] Extend the statistics normalizer and discovery metadata to return every expected metric with the documented availability/provenance shape, preserve available decimal values, omit `value` when unavailable, document favorite-count deprecation, and exclude dislike count in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T018 [US2] Add or update reStructuredText docstrings for every function or test helper changed for count-availability semantics in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`

### Refactor and Independent Validation

- [X] T019 [US2] Refactor the expected-metric list and availability-state construction into one local videos-family source of truth without widening scope beyond `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T020 [US2] Run sparse-statistics unit and contract coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py` with `PYTHONPATH=src python3 -m pytest`

**Checkpoint**: A client can reliably distinguish reported counts—including zero—from unavailable expected metrics without interpreting raw source data.

---

## Phase 5: User Story 3 - Receive Actionable Lookup Outcomes (Priority: P3)

**Goal**: Give clients safe, actionable results for invalid requests, unavailable videos, authorization-sensitive access, quota exhaustion, and source failures.

**Independent Test**: Exercise invalid `videoId` values, empty lower-level items, and injected lower-level failures for unavailable, authorization, quota, and source-service categories; verify the documented category is returned and serialized without secrets or raw diagnostics.

### Red - Tests First

- [X] T021 [P] [US3] Add failing unit tests for non-object, missing, blank, non-text, and unknown inputs; empty or malformed lookup items; and lower `VideosListToolError` category translation with sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`
- [X] T022 [P] [US3] Add failing injected-descriptor integration tests for unavailable, authorization, quota, and source failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`
- [X] T023 [P] [US3] Add a failing MCP routing test that invokes `videos_getStatistics` and verifies safe numeric protocol errors without credentials, stack traces, or raw source data in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Green - Minimum Implementation

- [X] T024 [US3] Implement empty-result handling and lower `VideosListToolError` translation to `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure` using existing sanitization helpers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T025 [US3] Ensure default registration exposes the concrete statistics descriptor for registry-level safe failure validation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`
- [X] T026 [US3] Add or update reStructuredText docstrings for every function and test helper changed for safe lookup outcomes in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Refactor and Independent Validation

- [X] T027 [US3] Refactor only duplicate error-category mapping and safe-detail handling while retaining shared `safe_upstream_error_message` and `sanitize_error_details` behavior in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`
- [X] T028 [US3] Run error-path unit, descriptor integration, and protocol-routing coverage in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` with `PYTHONPATH=src python3 -m pytest`

**Checkpoint**: All documented error categories are distinguishable, MCP-serializable, and free of sensitive diagnostics.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the complete additive feature, documentation, and regression safety.

- [X] T029 [P] Reconcile implementation behavior, examples, caveats, input schema, provenance, and safe-error wording against `/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/contracts/videos-get-statistics-contract.md` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/data-model.md`
- [X] T030 [P] Run the complete focused verification command from `/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`
- [X] T031 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix any reported issues in the touched Python files
- [X] T032 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server`, fix every failure caused by the feature, and rerun until the full repository suite passes after the final code change

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Begins immediately.
- **Foundational (Phase 2)**: Depends on T001–T002; blocks all user-story code work.
- **User Story 1 (Phase 3, P1)**: Depends on T003–T005; provides the MVP concrete descriptor and successful statistics retrieval.
- **User Story 2 (Phase 4, P2)**: Depends on the US1 descriptor and successful metric normalization (T009–T014); it is independently testable with an injected sparse lookup.
- **User Story 3 (Phase 5, P3)**: Depends on the US1 descriptor and handler (T009–T014); it is independently testable with injected empty and failing lookups.
- **Polish (Phase 6)**: Depends on completion of all selected user stories.

### User Story Completion Order

```text
Foundational verification
        │
        ▼
US1: available normalized statistics (MVP)
   ├──────► US2: unavailable metric semantics
   └──────► US3: safe failure outcomes
                 │
                 ▼
            Polish and full-suite verification
```

US2 and US3 can proceed in parallel after US1's descriptor and successful lookup behavior are complete, because they touch different behavioral slices; coordinate edits to the shared `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`.

### Within Each User Story

- Complete all Red test tasks and confirm they fail for the intended missing behavior before Green implementation tasks.
- Complete the story's Green tasks, then add or update reStructuredText docstrings for all changed Python functions and test helpers.
- Perform the story's Refactor task only after its focused tests pass.
- Run the story's independent validation task before marking the story complete.

## Parallel Execution Examples

### User Story 1

```text
Parallel Red tasks: T006 (unit tests), T007 (contract tests), T008 (descriptor integration test).
Then sequential Green tasks: T009 → T010 → T011 (only when needed) → T012 → T013 → T014.
```

### User Story 2

```text
Parallel Red tasks: T015 (unit availability tests), T016 (contract availability tests).
Then sequential Green and validation: T017 → T018 → T019 → T020.
```

### User Story 3

```text
Parallel Red tasks: T021 (unit errors), T022 (descriptor integration errors), T023 (MCP routing errors).
Then sequential Green and validation: T024 → T025 → T026 → T027 → T028.
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational verification (T001–T005).
2. Complete US1 (T006–T014).
3. Verify the public descriptor returns source-provided view, like, comment, and favorite counts for one video, preserving zero and performing exactly one `statistics` lookup.
4. Demonstrate the MVP before adding availability or failure refinements.

### Incremental Delivery

1. Deliver US1: valid single-video statistics retrieval.
2. Deliver US2: explicit availability semantics for absent metrics without fabricated values.
3. Deliver US3: safe client-recoverable failure outcomes.
4. Complete cross-cutting verification and the full suite (T029–T032).

## Notes

- All 32 tasks use the required checklist format: checkbox, sequential ID, optional `[P]` marker only when parallelizable, `[US#]` label for story work, and absolute file paths.
- Task counts: Setup 2; Foundational 3; US1 9; US2 6; US3 8; Polish 4.
- `videos_getStatistics` is additive. Do not modify lower-layer source request execution, public transport behavior, or other public tool contracts beyond the focused exports, registration, default fixture support, and tests identified above.
