# Tasks: Layer 4 Configured-Runtime Capability and Live-Verification Matrix

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/data-model.md), [MCP configured-runtime verification contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/contracts/mcp-configured-runtime-verification-contract.md), and [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/quickstart.md)

**Tests**: Tests are mandatory. Write every Red task first and demonstrate its failure before its Green task. New or changed Python functions require complete reStructuredText docstrings. Feature completion requires a passing `make quality` run from `/Users/ctgunn/Projects/youtube-mcp-server/` after the final change.

**Organization**: The deterministic configured-runtime matrix is test-owned in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`; manual live-smoke eligibility belongs to `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py`. Both must use existing public MCP routes rather than direct dispatcher calls.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the approved verification boundaries, existing seams, and completion commands before code changes.

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/contracts/mcp-configured-runtime-verification-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_live_runtime.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py`; confirm that generic baseline/retrieval tools are excluded, deterministic tests use `/mcp`, and OPS-405 retains remote smoke scope.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the test-owned public-route matrix foundation required by every configured-capability story.

**⚠️ CRITICAL**: Complete this phase before starting any user-story task.

- [X] T002 Add failing foundational tests for JSON-RPC `tools/list`/`tools/call` helpers, discovery-derived YouTube-family extraction, explicit generic-tool exclusions, valid capability-case records, and blocked socket/URL networking in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`.
- [X] T003 Implement the immutable `CapabilityMatrixCase` record, configured `create_app` transport factory with a controlled opener, public-route request helpers, descriptor-family extraction, generic-tool exclusion report, and outbound-network guard in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py` so T002 passes without real credentials or network I/O.
- [X] T004 Add complete reStructuredText docstrings for every new or changed Python function and dataclass method from T002–T003 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`, covering purpose, parameters, returns, raised errors, and side effects.
- [X] T005 Refactor duplicated route setup, metadata extraction, and foundation failure diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`, then run `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_configured_runtime_matrix.py` from `/Users/ctgunn/Projects/youtube-mcp-server/` and keep the foundation green.

**Checkpoint**: A configured in-process transport can be exercised only through public MCP routes, with safe test records and no external networking.

---

## Phase 3: User Story 1 - Verify Configured Capability Boundaries (Priority: P1) 🎯 MVP

**Goal**: Give operators one discovery-derived, individually reported API-key, OAuth-required, or unavailable-capability result for every public YouTube family.

**Independent Test**: Run `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_configured_runtime_matrix.py` from `/Users/ctgunn/Projects/youtube-mcp-server/`; it must discover all current YouTube families through MCP, report every matrix case separately, and fail with stable names for missing or stale family cases.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T006 [US1] Add failing parameterized public-route capability tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py` for exact family coverage, API-key executable success, OAuth-required-without-OAuth safe error, API-key-required-without-key safe error, conditional selector choice, and missing/stale matrix-family diagnostics.

### Implementation for User Story 1

- [X] T007 [US1] Define reviewed family capability cases and discovery-derived pytest parametrization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`, using deliberate public or owner-sensitive arguments, exact `resourceFamily`/`family` values, object arguments, safe expected categories, and no hard-coded inventory of public tool names.
- [X] T008 [US1] Implement MCP response classification and bidirectional capability-family coverage validation in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`, requiring structured success for executable cases, safe error envelopes with zero controlled requests for unavailable cases, and an explicit report of the five non-YouTube exclusions.
- [X] T009 [US1] Add or update complete reStructuredText docstrings for every Python function introduced or changed by T006–T008 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`.
- [X] T010 [US1] Refactor case validation and per-family result assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py` while preserving public tool/family pytest IDs, then run the User Story 1 independent-test command from `/Users/ctgunn/Projects/youtube-mcp-server/` with all discovered-family cases green.

**Checkpoint**: The MVP makes configured API-key, OAuth-required, and unavailable capability boundaries visible through the public MCP route for every YouTube family.

---

## Phase 4: User Story 2 - Prove the Live Runtime Boundary (Priority: P2)

**Goal**: Prove configured successful cases build the real live-runtime request through a controlled opener and never silently return representative local data.

**Independent Test**: Run `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_configured_runtime_matrix.py tests/integration/test_layer1_live_runtime.py` from `/Users/ctgunn/Projects/youtube-mcp-server/`; every API-key case must have one bounded sanitized request record, all unavailable cases must have none, and sentinel secrets must appear nowhere in result/error/record evidence.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T011 [US2] Add failing deterministic live-boundary tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py` for expected path shape, HTTP method, selected credential mode, bounded request count, controlled response mapping, no representative fallback, no unplanned outbound request, and secret/header/body redaction in MCP and diagnostic surfaces.

### Implementation for User Story 2

- [X] T012 [US2] Implement sanitized `ControlledRequestRecord` capture, controlled upstream response behavior, expected-request comparison, request-count bounds, representative-data rejection, and secret-redaction assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py` using the existing configured runtime and public MCP route.
- [X] T013 [US2] Add or update complete reStructuredText docstrings for every Python function introduced or changed by T011–T012 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`.
- [X] T014 [US2] Refactor controlled-opener, safe-record, and redaction helpers in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`, then run the User Story 2 independent-test command from `/Users/ctgunn/Projects/youtube-mcp-server/` and keep both the new Layer 4 and existing Layer 1 live-runtime suites green.

**Checkpoint**: A configured MCP success proves actual live-runtime request construction without external I/O, while unavailable configuration remains a safe non-fallback error.

---

## Phase 5: User Story 3 - Run an Opt-In Read-Only Live Smoke Check (Priority: P3)

**Goal**: Give operators an explicit, bounded, credential-safe, API-key public-read live smoke workflow that cannot invoke unapproved operations.

**Independent Test**: Run the deterministic smoke tests with no credential and then with controlled fake MCP responses from `/Users/ctgunn/Projects/youtube-mcp-server/`; they must fail closed before app construction when prerequisites are absent, invoke only reviewed allowlist tools through MCP when enabled, report exclusions separately, and redact all unsafe text.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T015 [P] [US3] Add failing deterministic smoke-workflow tests for enablement and credential preflight, discovery membership, explicit allowlist-only selection, mutation/sensitive-operation exclusion, public MCP invocation, finite request/timeout bounds, per-tool results, and fixed credential-safe failure output in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py`.
- [X] T016 [P] [US3] Add failing operator-command and CI-boundary assertions for `make test-runtime`, `make test-live-smoke`, deterministic-versus-live documentation, quota/upstream caveats, and exclusion of live smoke from `make test`, `make quality`, CI, and deployment gates in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`.

### Implementation for User Story 3

- [X] T017 [US3] Extend `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py` with reviewed API-key public-read allowlist entries, fail-closed preflight before app construction, discovery membership validation, `/mcp` invocation, bounded per-entry execution, selected/excluded per-tool safe reports, and fixed sanitized CLI failures; do not add OAuth, owner-only, mutation, upload, download, delete, rating, report, moderation, or subscription entries.
- [X] T018 [P] [US3] Add `test-runtime` and manual `test-live-smoke` targets plus `.PHONY` declarations in `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, ensuring neither target is a prerequisite of `test` or `quality` and `test-live-smoke` invokes `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py` only when the operator supplies the opt-in environment.
- [X] T019 [P] [US3] Document `make test-tools`, `make test-runtime`, `make test-live-smoke`, the required opt-in flag and credential, read-only allowlist boundary, excluded operation classes, quota/upstream implications, and OPS-405 remote-scope distinction in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`.
- [X] T020 [US3] Add or update complete reStructuredText docstrings for every Python function introduced or changed by T015–T017 in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py`.
- [X] T021 [US3] Refactor gate, selection, bounded reporting, and redaction logic in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py`, then run `PYTHONPATH=src python3 -m pytest tests/integration/test_youtube_live_smoke.py tests/integration/test_ci_quality_gate_docs.py` from `/Users/ctgunn/Projects/youtube-mcp-server/` with no real credential and keep the tests green.

**Checkpoint**: The live smoke command is manual, explicit, public-route-only, API-key public-read-only, bounded, allowlisted, credential-safe, and absent from ordinary quality/deployment execution.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile documentation, contracts, commands, and final required verification after all stories are complete.

- [X] T022 [P] Reconcile final command names, safety boundaries, and expected evidence in `/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/quickstart.md`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/Makefile` against the implemented workflow.
- [X] T023 [P] Review changed Python functions for complete reStructuredText docstrings and review the configured MCP/allowlist behavior against `/Users/ctgunn/Projects/youtube-mcp-server/specs/404-layer4-runtime-verification/contracts/mcp-configured-runtime-verification-contract.md`, recording any required regression assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`.
- [X] T024 Run `make test-tools`, `make test-runtime`, and `PYTHONPATH=src python3 -m pytest tests/integration/test_layer1_live_runtime.py` from `/Users/ctgunn/Projects/youtube-mcp-server/`, then correct all focused deterministic failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_configured_runtime_matrix.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py`, `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py`, `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, and `/Users/ctgunn/Projects/youtube-mcp-server/README.md`.
- [X] T025 Run `make quality` from `/Users/ctgunn/Projects/youtube-mcp-server/` after the final code or documentation change and fix every lint, type-check, and full-test-suite failure in `/Users/ctgunn/Projects/youtube-mcp-server/` before marking OPS-404 complete.
- [X] T026 Source private `.env.local` (with `.env` fallback) for the manual live-smoke target, document the opt-in variable without modifying local secret files, and validate the workflow in `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, `/Users/ctgunn/Projects/youtube-mcp-server/.env.example`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`.
- [X] T027 Report one credential-safe endpoint and item-count outcome for each selected live-smoke tool, return nonzero for safe-error outcomes, and validate the CLI behavior in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_youtube_live.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py`.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1: Setup
    ↓
Phase 2: Public-route configured-runtime foundation
    ↓
Phase 3: US1 — capability classification and family coverage (MVP)
    ↓
Phase 4: US2 — controlled live-runtime boundary proof
    ↓
Phase 5: US3 — opt-in allowlisted live smoke workflow
    ↓
Phase 6: Cross-cutting documentation and full quality gate
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2. It establishes the discovery-derived capability-matrix case registry and is the independently valuable MVP.
- **US2 (P2)**: Starts after US1 because it hardens the same matrix's successful-path evidence, controlled request capture, and no-fallback guarantees. Its independent test includes both the matrix and existing Layer 1 regression suite.
- **US3 (P3)**: Starts after Phase 2 and can be implemented in parallel with US2 after the foundation. It has separate script, test, command, and documentation surfaces; it must not depend on real credentials to complete deterministic testing.

### Within Each User Story

1. Complete its Red task(s) and show the intended failure.
2. Complete the Green implementation task(s) with only the minimum behavior required for the Red assertions.
3. Add or update every required reStructuredText docstring on changed Python functions.
4. Refactor only after focused tests pass, preserving independently testable behavior.
5. Before feature completion, run the final full quality gate and fix all failures.

## Parallel Opportunities

- After T005, US3's T015–T016 may proceed in parallel with US1's T006 because they modify distinct files.
- After T017 is complete, T018 and T019 modify independent command and documentation files and may proceed in parallel.
- T022 and T023 can proceed in parallel after all story refactor tasks; both precede T024 and T025.

## Parallel Example: User Story 3

```text
Task T015: Add deterministic smoke workflow tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_live_smoke.py
Task T016: Add command and CI boundary tests in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py

Task T018: Add focused Make targets in /Users/ctgunn/Projects/youtube-mcp-server/Makefile
Task T019: Document verification boundaries in /Users/ctgunn/Projects/youtube-mcp-server/README.md
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T005 to establish public-route configured-runtime test infrastructure.
2. Complete T006–T010 to classify and report every discovered YouTube family through MCP.
3. Run the User Story 1 independent-test command before proceeding.
4. The resulting matrix is a usable operator/maintainer capability verification increment without a live external request.

### Incremental Delivery

1. Deliver US1 to make API-key, OAuth-required, and unavailable configured capability boundaries visible.
2. Add US2 to prove successful configured cases select the actual live runtime and cannot fall back to representative local data.
3. Add US3 to provide the separately opt-in, explicitly allowlisted, credential-safe local live smoke workflow.
4. Complete T022–T025, ending with a passing `make quality` result.

## Notes

- Every task uses the required checkbox, sequential ID, optional parallel marker, applicable story label, and absolute path format.
- `[P]` appears only for tasks in different files with no unfinished dependency on another task in the same batch.
- Do not bypass MCP routes, infer live-smoke eligibility from names, add real credentials to fixtures/evidence, allow deterministic network access, or add the live smoke workflow to ordinary quality/CI/deployment gates.
