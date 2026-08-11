# Tasks: Transcript Retrieval

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), and [contracts/transcripts-get-transcript-contract.md](./contracts/transcripts-get-transcript-contract.md)

**Tests**: Tests are mandatory and must be written to fail before their implementation work. Completion requires `python3 -m pytest` and `ruff check .` after final code changes. Every new or changed Python function requires a reStructuredText docstring.

**Organization**: Tasks are grouped by user story so each delivered increment can be tested independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the contract-first implementation boundary and focused verification locations before changing code.

- [X] T001 Review and align the implementation boundary, language-selection policy, and verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/contracts/transcripts-get-transcript-contract.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/quickstart.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the centrally configured, testable default-language dependency required by all transcript flows.

**⚠️ CRITICAL**: Complete this phase before beginning user-story implementation.

- [X] T002 Add failing configuration tests for unset, blank, valid normalized, and malformed `YOUTUBE_TRANSCRIPT_LANG` values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_runtime_config_validation.py`
- [X] T003 Add a non-secret transcript-language setting, centralized parsing/validation, safe diagnostics, and reStructuredText docstrings for every changed function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py`
- [X] T004 Verify the configured runtime and dispatcher can receive the transcript-language setting without direct environment reads in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T005 Refactor the default-language configuration path while preserving the focused configuration tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_runtime_config_validation.py`

**Checkpoint**: Centralized transcript-language configuration is ready; user-story implementation can begin.

---

## Phase 3: User Story 1 - Retrieve a Video Transcript (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client retrieve complete normalized transcript text for one accessible video through the official authorized-caption flow.

**Independent Test**: Invoke a concrete `transcripts_getTranscript` descriptor with injected successful caption discovery and VTT download handlers; verify exactly one discovery call and one download call, then verify the stable response identity, provenance, availability, and text fields. Verify a successful download with no cues returns `availability: "empty"` and `text: ""`.

### Red - Tests for User Story 1

- [X] T006 [P] [US1] Add failing unit tests for required `videoId`, one-list/one-download composition, VTT-to-plain-text normalization, successful empty text, and result shaping in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`
- [X] T007 [P] [US1] Add failing executable-contract tests for the concrete schema, `transcript_retrieval` metadata, lower-layer dependencies, boundedness, field provenance, quota/auth caveats, and absence of `representativeOnly` in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`
- [X] T008 [P] [US1] Add failing dispatcher-registration integration tests for injected caption handlers, discovery metadata, and successful transcript invocation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

### Green - Implementation for User Story 1

- [X] T009 [US1] Implement the transcript tool constants, public schema, safe error type, `videoId` validation, caption-list/download composition, VTT parser, successful-result normalizer, metadata builder, handler, and descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`
- [X] T010 [US1] Export the concrete transcript tool constants, validator, metadata builder, handler, descriptor, and error type from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`
- [X] T011 [US1] Register `transcripts_getTranscript` with injected OAuth caption-list and caption-download handlers in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- [X] T012 [US1] Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

### Refactor - User Story 1

- [X] T013 [US1] Refactor transcript-family parsing and result helpers without changing the public contract, then run the focused US1 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`

**Checkpoint**: A client can retrieve an accessible video transcript as complete normalized text without relying on language-selection enhancements beyond the foundational default.

---

## Phase 4: User Story 2 - Control Transcript Language (Priority: P2)

**Goal**: Make transcript language selection reproducible: explicit input, configured default, then English, with one deterministic exact-language caption track selected.

**Independent Test**: With controlled caption-track results, invoke the tool with explicit language, configured default only, and neither. Verify the selected `language` and `languageSource` for each request; verify no non-exact language, translation, or source-order-dependent result is selected.

### Red - Tests for User Story 2

- [X] T014 [P] [US2] Add failing unit tests for explicit-over-configured-over-English resolution, whitespace/case normalization, malformed language tags, exact-only matching, and deterministic track ranking in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`
- [X] T015 [P] [US2] Add failing contract tests for the language priority, no-translation/no-fallback policy, selection rule, and `languageSource` field in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`
- [X] T016 [P] [US2] Add failing configured-runtime integration coverage proving `YOUTUBE_TRANSCRIPT_LANG` reaches default dispatcher behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

### Green - Implementation for User Story 2

- [X] T017 [US2] Implement injected configured-default consumption, three-level language resolution, exact normalized BCP-47 matching, and documented deterministic track selection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`
- [X] T018 [US2] Complete transcript-language propagation into the default descriptor without handler environment access in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`
- [X] T019 [US2] Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/runtime.py`

### Refactor - User Story 2

- [X] T020 [US2] Refactor language normalization and selector-key construction while retaining exact-match and deterministic behavior, then run the focused US2 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`

**Checkpoint**: Clients can predict the language and selected track for every successful request, with no silent substitution.

---

## Phase 5: User Story 3 - Understand Unavailable Caption Access (Priority: P3)

**Goal**: Return distinct safe MCP outcomes when a transcript cannot be retrieved because it is unavailable, unauthorized, quota-limited, or affected by an upstream failure.

**Independent Test**: Inject no matching track, stale selected track, authorization, quota, and source/decode failures. Verify each produces its documented category, includes resolved language only for unavailable results, and exposes no text, token, raw source body, or trace.

### Red - Tests for User Story 3

- [X] T021 [P] [US3] Add failing unit tests for no matching track, stale track, lower-layer authorization/quota/source failures, malformed VTT content, and sanitized error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`
- [X] T022 [P] [US3] Add failing contract tests for every safe error category, recovery guidance, and no-content/no-secret metadata guarantee in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`
- [X] T023 [P] [US3] Add failing integration and MCP protocol-routing tests for safe default-dispatcher errors and stable serialized categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

### Green - Implementation for User Story 3

- [X] T024 [US3] Implement safe mapping from caption-list/download failures to `invalid_parameters`, `transcript_unavailable`, `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure`, including stale-track and malformed-content handling, in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`
- [X] T025 [US3] Add only any required additive public-category serialization support and sanitized-detail handling in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`
- [X] T026 [US3] Add or update reStructuredText docstrings for every new or modified Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/envelope.py`

### Refactor - User Story 3

- [X] T027 [US3] Refactor transcript error translation to keep safe-category mapping local and preserve lower-layer contracts, then run the focused US3 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`

**Checkpoint**: All retrieval, language, and failure user stories are independently verifiable through the public tool contract.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the complete feature, documentation, observability, and regression posture.

- [X] T028 [P] Reconcile the final implementation with `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/contracts/transcripts-get-transcript-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/data-model.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/quickstart.md`
- [X] T029 Review all changed Python functions for required reStructuredText docstrings, safe observability, no credential/text leakage, and one-list/at-most-one-download boundedness in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/`
- [X] T030 Run the documented quickstart focused suite and resolve every failure using `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/quickstart.md`
- [X] T031 Run `python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every failing test before feature completion
- [X] T032 Run `ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` and fix every reported issue before feature completion

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately.
- **Phase 2 (Foundational)**: Depends on T001 and blocks all user-story work.
- **Phase 3 (US1, P1)**: Depends on T002–T005; it delivers the MVP.
- **Phase 4 (US2, P2)**: Depends on the concrete handler and descriptor from T009–T013, plus the foundational configuration path.
- **Phase 5 (US3, P3)**: Depends on the concrete retrieval flow from T009–T013; it can be developed alongside US2 after that flow exists because it changes distinct behavior and test cases.
- **Phase 6 (Polish)**: Depends on all desired user stories.

### User Story Completion Order

```text
Setup → Foundational configuration → US1 (core retrieval MVP) → US2 (language control)
                                                    └──────────→ US3 (safe failure outcomes)
US2 + US3 → Polish and full verification
```

### Parallel Opportunities

- T006–T008 can proceed in parallel because they modify separate unit, contract, and integration test files.
- T014–T016 can proceed in parallel because they modify separate unit, contract, and integration test files.
- T021–T023 can proceed in parallel because they modify separate unit, contract, and integration/protocol test files.
- After US1 core retrieval is complete, US2 and US3 can be assigned to different developers, subject to coordinating changes to `transcripts.py`.
- T028 may run in parallel with a final docstring/security review only when that review uses non-overlapping source files.

## Parallel Execution Examples

### User Story 1

```text
T006: Add unit Red tests in tests/unit/test_youtube_composed_transcripts.py
T007: Add contract Red tests in tests/contract/test_youtube_composed_transcripts_contract.py
T008: Add registration Red tests in tests/integration/test_youtube_composed_tool_registration.py
```

### User Story 2

```text
T014: Add language-selection unit Red tests in tests/unit/test_youtube_composed_transcripts.py
T015: Add language-contract Red tests in tests/contract/test_youtube_composed_transcripts_contract.py
T016: Add configured-runtime integration Red tests in tests/integration/test_youtube_tool_registration.py
```

### User Story 3

```text
T021: Add failure-mapping unit Red tests in tests/unit/test_youtube_composed_transcripts.py
T022: Add safe-error contract Red tests in tests/contract/test_youtube_composed_transcripts_contract.py
T023: Add error registration/protocol Red tests in tests/integration/test_youtube_composed_tool_registration.py and tests/unit/test_method_routing.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T005 to establish central default-language configuration.
2. Complete T006–T013 to deliver one authorized caption discovery/download flow and normalized transcript text.
3. Run the US1 focused suite and demonstrate the concrete descriptor before adding language refinements or failure-policy expansion.

### Incremental Delivery

1. Foundational configuration → centralized default behavior ready.
2. US1 → core transcript retrieval tested independently (MVP).
3. US2 → deterministic language control tested independently.
4. US3 → safe unavailable/access outcomes tested independently.
5. Polish → contract reconciliation, quickstart verification, full suite, and lint.

### Format Validation

All 32 tasks use the required `- [ ] T### [P?] [US?] Description with absolute file path` checklist format. Story tasks carry `[US1]`, `[US2]`, or `[US3]`; setup, foundational, and polish tasks intentionally carry no story label.
