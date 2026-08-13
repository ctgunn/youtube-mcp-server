# Tasks: Transcript Language Discovery

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/313-transcript-languages/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), and [contracts/transcripts-list-languages-contract.md](./contracts/transcripts-list-languages-contract.md)

**Tests**: Tests are mandatory. Write each Red task and confirm it fails before its paired Green task. Completion requires a passing full repository suite after the final code changes. Every new or modified Python function must have a reStructuredText docstring with purpose, parameters, return value, raised errors where relevant, and observable side effects where relevant.

**Organization**: Tasks are grouped by independently testable user story. `transcripts_listLanguages` is additive and composes the existing authorized `captions.list` handler exactly once; it must not download or return caption content.

## Phase 1: Setup

**Purpose**: Establish the implementation baseline from the approved feature design without changing runtime behavior.

- [X] T001 Review the bounded one-list/no-download composition, source-field allowlist, safe-error policy, and verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/313-transcript-languages/{plan.md,research.md,data-model.md,contracts/transcripts-list-languages-contract.md,quickstart.md}` before writing tests.

---

## Phase 2: Foundational - Registration and Safe MCP Boundary

**Purpose**: Establish the shared public-tool wiring and safe error-delivery checks that support every story.

**⚠️ CRITICAL**: Complete these Red checks before adding the concrete public handler. The Green registration work completes with User Story 1 once the descriptor exists.

- [X] T002 [P] Add failing default-catalog registration coverage for a concrete `transcripts_listLanguages` descriptor with no `representativeOnly` metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- [X] T003 [P] Add failing protocol-routing coverage proving the new safe discovery failure categories serialize without unsafe error details in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.

**Checkpoint**: Foundational Red coverage is in place; User Story 1 may implement the executable descriptor and satisfy the registration boundary.

---

## Phase 3: User Story 1 - Discover Available Transcript Languages (Priority: P1) 🎯 MVP

**Goal**: Let an MCP client discover every accessible caption-language track for one valid video through a single authorized listing.

**Independent Test**: Inject a caption-list handler that returns tracks in several languages, including duplicate languages, invoke `transcripts_listLanguages` with a valid `videoId`, and verify a concrete descriptor makes exactly one `{ "part": "snippet", "videoId": ... }` call and returns each track in source order.

### Red - Failing Tests First

- [X] T004 [US1] Add failing argument-validation, one-list-call, source-order, duplicate-language, normalized availability, and no-caption-text unit tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T005 [P] [US1] Add failing MCP contract tests for the required-only `videoId` schema, `captions.list` dependency, one-read/no-download composition boundary, provenance, OAuth/quota caveats, and executable metadata in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.
- [X] T006 [P] [US1] Add failing dispatcher integration coverage that injects a caption-list result and invokes the concrete descriptor exactly once in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`.

### Green - Minimum Implementation

- [X] T007 [US1] Add the `transcripts_listLanguages` name, required-only input schema, safe error type, `videoId` validator, source-order language-option normalizer, one-call handler, metadata builder, and descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.
- [X] T008 [US1] Export the `transcripts_listLanguages` public constants, error type, validation, handler, metadata, and descriptor builders in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`.
- [X] T009 [US1] Register `transcripts_listLanguages` in the default tool catalog with only the existing injected `build_captions_list_handler(**oauth_dependencies)` dependency in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

### Refactor and Story Validation

- [X] T010 [US1] Add or update reStructuredText docstrings for every new or modified Python function used by language discovery in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
- [X] T011 [US1] Refactor only duplicated transcript-family validation, normalization, or registration code while preserving the one-list/no-download boundary, then run the focused P1 tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/{unit/test_youtube_composed_transcripts.py,contract/test_youtube_composed_transcripts_contract.py,integration/test_youtube_composed_tool_registration.py,integration/test_youtube_tool_registration.py,unit/test_method_routing.py}`.

**Checkpoint**: `transcripts_listLanguages` is concrete, default-registered, and independently returns every discovered language track from one source listing.

---

## Phase 4: User Story 2 - Select a Suitable Transcript Track (Priority: P2)

**Goal**: Give clients the source-provided identifier and distinguishing metadata needed to select among returned tracks without inventing data.

**Independent Test**: Inject tracks with the same language, with and without identifiers and optional metadata; verify that each remains a separate option and that the response exposes only supplied approved metadata with raw-versus-normalized provenance.

### Red - Failing Tests First

- [X] T012 [US2] Add failing unit tests for source-provided caption identifiers, name/status/track-kind/draft/automatic-sync metadata, missing optional fields, unknown-field exclusion, repeated-language preservation, and no fabricated values in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T013 [P] [US2] Add failing contract tests for the `Language Option` and `fieldProvenance` contract, including nullable or omitted identifiers and source-only track metadata, in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.

### Green - Minimum Implementation

- [X] T014 [US2] Restrict language-option shaping to the approved source metadata allowlist, preserve missing values without inference, and identify raw upstream and normalized fields correctly in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.

### Refactor and Story Validation

- [X] T015 [US2] Add or update reStructuredText docstrings for every Python function changed for source metadata presentation in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.
- [X] T016 [US2] Refactor language-option field extraction without changing source order, provenance, or missing-value behavior, then run the focused P2 unit and contract tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/{unit/test_youtube_composed_transcripts.py,contract/test_youtube_composed_transcripts_contract.py}`.

**Checkpoint**: A client can distinguish same-language tracks and choose a source-provided identifier or metadata value without receiving invented or unsafe information.

---

## Phase 5: User Story 3 - Understand Restricted or Missing Access (Priority: P3)

**Goal**: Let clients distinguish a completed empty discovery result from invalid input, authorization limits, quota limits, source unavailability, and unexpected source failures.

**Independent Test**: Exercise invalid arguments, a completed empty listing, and injected lower-layer failure categories; verify the empty case is a successful `no_accessible_languages` result and every failure is distinct, sanitized, and contains no protected caption information.

### Red - Failing Tests First

- [X] T017 [US3] Add failing unit tests for no lower call after invalid input, successful empty listings, authentication and authorization denial, quota exhaustion, endpoint unavailability, other upstream failures, and detail sanitization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`.
- [X] T018 [P] [US3] Add failing contract tests for `no_accessible_languages`, `invalid_parameters`, `authorization_sensitive_data`, `quota_exhaustion`, `source_unavailable`, `upstream_failure`, and safe recovery guidance in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`.

### Green - Minimum Implementation

- [X] T019 [US3] Map lower caption-list outcomes so only a completed empty list becomes `no_accessible_languages`, while validation, authorization, quota, unavailable endpoint, and other source failures use their documented safe categories and sanitized details in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.
- [X] T020 [US3] Extend safe discovery error serialization only if the Red protocol-routing test requires it, keeping MCP error details sanitized in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`.

### Refactor and Story Validation

- [X] T021 [US3] Add or update reStructuredText docstrings for every Python function changed for safe outcome mapping in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py` and, only if changed, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py`.
- [X] T022 [US3] Refactor lower-layer error translation without collapsing empty success into failure or exposing protected information, then run the focused P3 unit, contract, integration, and routing tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/{unit/test_youtube_composed_transcripts.py,contract/test_youtube_composed_transcripts_contract.py,integration/test_youtube_composed_tool_registration.py,unit/test_method_routing.py}`.

**Checkpoint**: Empty, restricted, quota-limited, unavailable, and failed discovery outcomes are safely distinct and independently testable.

---

## Phase 6: Polish and Cross-Cutting Validation

**Purpose**: Reconcile final behavior with the approved public contract and prove no regressions remain.

- [X] T023 [P] Verify the implemented descriptor and focused test coverage against the one-call/no-download, provenance, empty-result, and safe-error expectations in `/Users/ctgunn/Projects/youtube-mcp-server/specs/313-transcript-languages/{contracts/transcripts-list-languages-contract.md,quickstart.md}`.
- [X] T024 [P] Review every touched Python function for complete reStructuredText docstrings and remove any caption text, credential, token, raw-payload, signed-URL, or trace exposure from public metadata and errors in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`.
- [X] T025 Run `PYTHONPATH=src python3 -m pytest` from `/Users/ctgunn/Projects/youtube-mcp-server` against `/Users/ctgunn/Projects/youtube-mcp-server/tests/` and fix every failure before considering the feature complete.
- [X] T026 Run `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` using `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml` and fix every reported violation before considering the feature complete.

---

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Starts immediately.
- **Phase 2 (Foundational)**: Depends on T001; its failing checks must exist before concrete public-tool implementation.
- **Phase 3 (US1, P1)**: Depends on T001–T003. It creates the executable handler, exports, and registration that the later presentation and error stories extend.
- **Phase 4 (US2, P2)**: Depends on T011 because it extends the P1 language-option result shape.
- **Phase 5 (US3, P3)**: Depends on T011 because it extends the P1 handler's outcome behavior; it may proceed in parallel with Phase 4 after T011 if separate changes to `transcripts.py` are coordinated.
- **Phase 6 (Polish)**: Depends on all selected story phases being complete.

### User Story Completion Order

```text
Setup → Foundational Red checks → US1 (MVP)
                                      ├── US2 (track metadata)
                                      └── US3 (empty/restricted outcomes)
US2 + US3 → Polish and full validation
```

### Within Each User Story

1. Complete the listed Red tasks and observe failure for the intended missing behavior.
2. Implement only the Green behavior needed for those tests.
3. Add or update reStructuredText docstrings for every changed Python function.
4. Refactor with focused tests still green.
5. Do not treat focused tests as final completion evidence; Phase 6 must pass the full repository suite.

## Parallel Opportunities

- T002 and T003 modify separate test modules and may run in parallel.
- In US1, T005 and T006 may run in parallel with the non-overlapping unit-test work in T004 once expectations are agreed.
- In US2, T012 and T013 modify separate test modules and may run in parallel.
- In US3, T017 and T018 modify separate test modules and may run in parallel.
- US2 and US3 can run concurrently after T011 only with coordinated ownership of `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/transcripts.py`; otherwise execute them in priority order.
- T023 and T024 may run in parallel after all code changes are complete.

## Parallel Example: User Story 1

```text
Task: "T005 Add the public MCP contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py"
Task: "T006 Add descriptor invocation coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py"
```

## Parallel Example: User Story 3

```text
Task: "T017 Add safe-outcome unit tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py"
Task: "T018 Add safe-error contract tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py"
```

## Implementation Strategy

### MVP First

1. Complete T001–T003 to establish the contract and safe public boundary.
2. Complete US1 (T004–T011).
3. Validate the independent P1 test: one authorized listing produces ordered language options, and default registration exposes a concrete descriptor.
4. The resulting MVP delivers language discovery without metadata enrichment or all failure distinctions beyond the foundation checks.

### Incremental Delivery

1. Add US1 for executable, bounded language discovery.
2. Add US2 so callers can distinguish and choose among same-language tracks using source-provided metadata.
3. Add US3 so caller recovery decisions are safe and unambiguous for empty, restricted, quota, and source conditions.
4. Finish only after T023–T026 pass.

## Format Validation

- All 26 tasks use the required `- [ ] T### [P?] [US#?] Description with absolute file path` checklist format.
- Story tasks T004–T022 include exactly one user-story label; setup, foundational, and polish tasks have no story label.
- `[P]` appears only on tasks that can be performed against different files without an incomplete dependency.
