# Tasks: YT-159 Layer 1 Live Calls for Catalog, Membership, and Playlist Resources

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/data-model.md), and [contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/contracts/layer1-catalog-membership-playlist-live-call-contract.md)

**Tests**: Tests are mandatory. Implement each Red task first and confirm it fails for the missing behavior before completing its Green task. The final gate is a passing `python3 -m pytest` followed by `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.

**Organization**: Tasks are grouped by user story so each story remains independently testable after the shared runtime wiring is complete.

## Phase 1: Setup (Shared Test Infrastructure)

**Purpose**: Prepare reusable, credential-free controlled-runtime test fixtures; the existing Python MCP service and its dependencies are reused without project initialization.

- [X] T001 Establish a 17-operation configured-call matrix, a request-recording controlled opener, and distinctive credential-free response fixtures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`; give every new Python helper a reStructuredText docstring with `:param:`, `:return:`, `:raises:`, and side-effect details where applicable.

---

## Phase 2: Foundational (Shared Configured-Descriptor Wiring)

**Purpose**: Make the existing YT-157 configured runtime the dependency source for every YT-159 descriptor while preserving the intentional no-runtime local-test path.

**⚠️ CRITICAL**: Complete this phase before treating any user story as delivered.

- [X] T002 Add a failing configured-runtime dependency-closure test for all 17 in-scope descriptors in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`, asserting the configured executor and only the applicable API-key, OAuth, or conditional credential values are captured instead of a `_default_*_executor` or placeholder credential.
- [X] T003 [P] Add a failing regression test in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` proving a dispatcher created without `youtube_runtime` retains the existing explicit local/test default behavior rather than changing public schemas or descriptor metadata.
- [X] T004 Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` to pass API-key dependencies to `guideCategories.list`, both localization list descriptors, and `playlistItems.list`; OAuth dependencies to members, membership levels, every playlist-image operation, playlist-item mutations, and playlist mutations; and conditional dependencies to `playlists.list`.
- [X] T005 Update reStructuredText docstrings for every Python function modified in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, including purpose, inputs, outputs, raised errors, and dependency-injection side effects.
- [X] T006 Run the foundational Red/Green checks in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, then refactor only repeated dependency-group construction in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` while keeping both suites green.

**Checkpoint**: All 17 descriptors receive the configured shared runtime when configured, and no-runtime local/test descriptor construction remains compatible.

---

## Phase 3: User Story 1 - Receive Live Catalog, Membership, and Playlist Results (Priority: P1) 🎯 MVP

**Goal**: An agent developer receives normalized live-service results from every one of the 17 supported operations rather than representative defaults.

**Independent Test**: Construct the configured application with a controlled opener, invoke each in-scope public tool with valid input, and verify a distinctive controlled response is returned after a captured live request; no result may contain a representative/static success marker.

### Red: Tests for User Story 1

- [X] T007 [US1] Add a failing parameterized configured-default success test for `guideCategories.list`, `i18nLanguages.list`, `i18nRegions.list`, `members.list`, `membershipsLevels.list`, all four playlist-image operations, all four playlist-item operations, and all four playlist operations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`; assert one captured request and a distinctive normalized response for every case.
- [X] T008 [P] [US1] Add failing compatibility assertions for preserved metadata, validation, quota, result shape, and response-normalizer behavior in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_guide_categories_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_languages_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_i18n_regions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_members_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_memberships_levels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_images_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlists_contract.py`.

### Green: Implementation for User Story 1

- [X] T009 [US1] Complete any descriptor invocation gap exposed by T007 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` so every configured default uses the injected `IntegrationExecutor`, keeps existing wrapper/result-mapper calls intact, and never selects a family-specific representative executor.
- [X] T010 [US1] Add or update reStructuredText docstrings for every Python function changed while completing T009 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, documenting configured dependencies and safe behavior without credential values.

### Refactor: User Story 1

- [X] T011 [US1] Refactor the shared controlled-success fixtures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` to remove duplication without weakening the 17-operation assertions, then run the affected unit, integration, and contract tests named in `/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/quickstart.md`.

**Checkpoint**: All 17 configured default operations return normalized live-path results and preserve their established contracts.

---

## Phase 4: User Story 2 - Apply the Correct Authorization and Request Form (Priority: P2)

**Goal**: Operators can rely on each operation to select the declared authorization and submit the declared query, JSON, or multipart request form while safely handling unavailable access and upstream failure.

**Independent Test**: With a controlled opener, assert each operation's method, path, parameters, credential location, body, or multipart media form; then verify missing credentials and controlled upstream failures return redacted normalized errors without a request or representative success.

### Red: Tests for User Story 2

- [X] T012 [US2] Add failing parameterized authorization/request-shape cases for all 17 operations in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`, covering API-key query credentials, OAuth bearer credentials, `playlists.list` public versus `mine` selector routing, JSON mutation bodies, playlist-image multipart metadata/media, and DELETE acknowledgments.
- [X] T013 [P] [US2] Add failing byte-level request-construction and redaction assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` for playlist-image insert/update multipart content, playlist-item/playlist JSON bodies, no-body deletes, and secret-free normalized timeout, malformed-response, and authorization failures.
- [X] T014 [US2] Add failing configured-app missing-credential cases in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` for guide categories, both localization tools, members, membership levels, playlist images, playlist-item mutations, playlist mutations, and owner-scoped playlist listing; assert safe tool-level failures, no opener call, and no representative result.

### Green: Implementation for User Story 2

- [X] T015 [US2] Update `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py` to defer absent configured API-key handling to invocation and return the existing safe normalized failure rather than failing dispatcher construction; preserve explicit injected credentials and all descriptor contracts.
- [X] T016 [US2] Add or update reStructuredText docstrings for every changed Python function in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`, including inputs, returned safe failures, raised errors, and the absence of credential logging.

### Refactor: User Story 2

- [X] T017 [US2] Refactor only duplicated safe API-key-context selection in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py` and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py`, then run `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` with all new request, retry, and redaction cases green.

**Checkpoint**: All operations use the declared access and request form, while missing or failed live access remains safe and credential-free.

---

## Phase 5: User Story 3 - Use Live Wrappers Through Public Tools (Priority: P3)

**Goal**: An agent developer can use one configured public-tool flow per affected family and prove it reaches the shared live wrapper path rather than bypassing it or returning representative data.

**Independent Test**: Invoke configured guide-category, localization, members, membership-levels, playlist-image, playlist-item, and playlist tools through application/transport/dispatcher composition; a controlled opener must capture the family request and a controlled upstream failure must surface as the established normalized public error.

### Red: Tests for User Story 3

- [X] T018 [US3] Add seven failing configured public-tool flow tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` for guide categories, localization, members, membership levels, playlist images, playlist items, and playlists; for each flow assert transport → dispatcher → descriptor → wrapper → shared live transport and a distinctive result.
- [X] T019 [P] [US3] Add failing public-contract regression tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` that confirm configured runtime wiring changes neither public tool names, schemas, metadata, quota/auth disclosure, nor explicit no-runtime test seams.
- [X] T020 [US3] Add failing normalized-upstream-failure variants for the seven configured public-tool flows in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`; assert no direct resource-specific request path, no representative fallback, no stack trace, and no credential-bearing diagnostic.

### Green: Implementation for User Story 3

- [X] T021 [US3] Make the smallest registration/composition adjustment exposed by T018–T020 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` so each selected public tool receives the same configured runtime dependency path while retaining existing descriptor schemas, metadata, result mappers, and normalized error mappers.
- [X] T022 [US3] Add or update reStructuredText docstrings for every Python function changed by T021 in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, including public-tool composition inputs, outputs, failures, and side effects without secret values.

### Refactor: User Story 3

- [X] T023 [US3] Refactor public-flow test fixtures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py` so seven-family evidence remains readable and duplicate request-recording logic is shared; rerun the affected integration and contract suites.

**Checkpoint**: One configured public-tool flow per family demonstrably reaches the shared live wrapper path and returns only normalized live outcomes.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize contract evidence, documentation, security, and full-suite regression validation.

- [X] T024 [P] Reconcile implementation and test evidence against `/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/contracts/layer1-catalog-membership-playlist-live-call-contract.md`, updating the contract only if an existing documented compatibility guarantee needs clearer wording and without adding implementation-specific public behavior.
- [X] T025 [P] Execute the deterministic verification commands in `/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/quickstart.md` from `/Users/ctgunn/Projects/youtube-mcp-server`, correct any stale test-path references in that quickstart, and confirm no command needs live credentials.
- [X] T026 Review all changed Python functions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/localization.py` for complete reStructuredText docstrings and verify diagnostics, logs, fixtures, and failure assertions redact API keys, OAuth tokens, bearer headers, credential-bearing URLs, raw bodies, and media.
- [X] T027 Run `python3 -m pytest` and then `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server` according to `/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/quickstart.md`, fixing every failure before declaring YT-159 complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately and prepares reusable controlled-runtime evidence.
- **Foundational (Phase 2)**: Depends on T001; blocks delivery of all user stories because the shared dispatcher must inject the configured runtime consistently.
- **User Story 1 (Phase 3)**: Depends on T001–T006; establishes the MVP proof that all 17 configured defaults select the live path.
- **User Story 2 (Phase 4)**: Depends on T001–T006 and can begin after the shared wiring; it is independently testable once configured calls exist.
- **User Story 3 (Phase 5)**: Depends on T001–T006 and verifies public composition independently of the earlier story test suites.
- **Polish (Phase 6)**: Depends on the selected user stories being complete; T027 is the mandatory final completion gate.

### User Story Completion Order

```text
Phase 1 setup
    └── Phase 2 shared configured-descriptor wiring
            ├── US1 (P1): 17 configured-default live results — MVP
            ├── US2 (P2): authorization, request forms, and safe failures
            └── US3 (P3): configured public-tool live-wrapper flows
                    └── Phase 6 cross-cutting verification
```

- **US1 (P1)**: Uses the shared wiring and is the recommended MVP. It has no dependency on US2 or US3.
- **US2 (P2)**: Uses the shared wiring and has no dependency on US1 or US3; its missing-credential correction may be implemented in parallel with US1 if it does not conflict in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.
- **US3 (P3)**: Uses the shared wiring and has no dependency on US1 or US2; serialize its edits to the shared live-runtime integration test file with work on US1/US2.

### Within Each User Story

- Complete every Red task and observe its expected failure before the corresponding Green task.
- Make the smallest code change necessary for Green; do not add endpoint-specific clients, secret sources, retries, or response mappers.
- Update reStructuredText docstrings before Refactor completion.
- Refactor only with the story's targeted tests green.
- Do not treat targeted tests as feature-completion evidence; T027 must pass.

## Parallel Execution Examples

### User Story 1

```text
Parallel after T001–T006:
- T007: configured-default live-result matrix in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py
- T008: contract compatibility assertions in the eight /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_*.py files listed in T008
```

### User Story 2

```text
Parallel after T001–T006:
- T012: configured authorization/request-form matrix in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py
- T013: transport multipart/body/redaction assertions in /Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py
```

### User Story 3

```text
Parallel after T001–T006:
- T018: seven public-flow live-path tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py
- T019: public-contract and no-runtime regression tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py and /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T006 to make configured dependency injection reliable.
2. Complete T007–T011 to prove all 17 configured defaults reach live execution and preserve normalized outcomes.
3. Run the User Story 1 focused commands from `/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/quickstart.md`.
4. Demonstrate the 17-operation configured-default path before adding request-form or public-flow refinements.

### Incremental Delivery

1. Complete setup and shared runtime wiring.
2. Deliver US1 live results with compatibility evidence.
3. Deliver US2 authorization, request-form, upload, and redaction evidence.
4. Deliver US3 public-tool composition evidence.
5. Complete contract/quickstart review and the mandatory full suite/lint gate.

### Parallel Team Strategy

1. Complete Phase 1 and Phase 2 together because `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py` is a shared edit.
2. After Phase 2, assign US1, US2, and US3 to separate developers where possible; serialize changes to `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`.
3. Run the focused suites after each story and resolve shared-file merge conflicts before the final full-suite gate.

## Notes

- All 27 tasks use the required checkbox, sequential task ID, optional parallel marker, required story label for story tasks, and absolute file path format.
- `[P]` tasks touch different files and have no dependency on unfinished tasks in their phase.
- Explicitly injected executors, openers, and credentials remain valid only for test/local development; configured defaults must never use them implicitly or return representative success data.
