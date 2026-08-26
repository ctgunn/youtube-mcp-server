# Tasks: Layer 4 Default MCP Tool-Catalog Integration Coverage

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/`
**Prerequisites**: [plan.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/plan.md), [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/spec.md), [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/data-model.md), and [MCP tool-catalog verification contract](/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/contracts/mcp-tool-catalog-verification-contract.md)

**Tests**: Tests are mandatory. Write each Red task first and demonstrate its failure before Green work. New or changed Python functions require complete reStructuredText docstrings. Feature completion requires a passing `make quality` run from `/Users/ctgunn/Projects/youtube-mcp-server/` after the final change.

**Organization**: Tasks are grouped by user story. The fixture registry and route assertions are intentionally test-owned in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`; the public MCP route remains the only catalog authority.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the approved scope and existing repository surfaces before adding the deterministic verification layer.

- [X] T001 Review `/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/contracts/mcp-tool-catalog-verification-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, and `/Users/ctgunn/Projects/youtube-mcp-server/README.md`; confirm that no implementation will duplicate the default catalog or call the dispatcher directly.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish one test-owned, route-level verification foundation used by every user story.

**⚠️ CRITICAL**: Complete this phase before starting user-story work.

- [X] T002 Add failing foundation tests for a non-empty unique `tools/list` catalog, object-shaped fixture arguments, and a controlled no-network transport in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`.
- [X] T003 Implement the controlled default MCP transport, public-route request builders, fixture record shape, and discovery helper in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py` so T002 passes without credentials or configured YouTube runtime.
- [X] T004 Add complete reStructuredText docstrings for every new or modified Python helper from T003 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, covering purpose, parameters, return values, safe errors, and side effects.
- [X] T005 Refactor repeated public-route setup and failure messages in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, then run `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_tool_catalog_endpoints.py` from `/Users/ctgunn/Projects/youtube-mcp-server/` and keep the foundation tests green.

**Checkpoint**: A credential-free test foundation can discover the real default catalog through the public MCP route and is ready for story-specific assertions.

---

## Phase 3: User Story 1 - Verify the Default Tool Catalog (Priority: P1) 🎯 MVP

**Goal**: Let a maintainer obtain an individually reported route-invocation result for every default public tool discovered at test time.

**Independent Test**: From `/Users/ctgunn/Projects/youtube-mcp-server/`, run `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_tool_catalog_endpoints.py`; it must derive cases from `tools/list`, call every discovered name through `tools/call`, and report each public tool name separately.

### Tests for User Story 1 (REQUIRED) ⚠️

- [X] T006 [US1] Add failing parameterized route-invocation tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py` that require one case per discovered tool, require the `tools/call` route rather than direct dispatcher calls, and require non-error structured content for every successful fixture.

### Implementation for User Story 1

- [X] T007 [US1] Define one reviewed, deterministic safe fixture for every tool discovered from the default catalog in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, using only object arguments and declared success or safe-error outcomes rather than a hard-coded catalog inventory.
- [X] T008 [US1] Implement discovery-derived pytest parametrization and public `tools/call` response assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, including nonempty structured content and conditional `endpoint` to `metadata.upstream.operationKey` comparison.
- [X] T009 [US1] Add or update complete reStructuredText docstrings for every Python function introduced or changed by T006-T008 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`.
- [X] T010 [US1] Refactor the per-tool assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py` to keep pytest IDs equal to public tool names, then run the User Story 1 independent-test command from `/Users/ctgunn/Projects/youtube-mcp-server/` and keep every discovered-tool case green.

**Checkpoint**: The MVP verifies all currently discovered default tools through the public discovery and invocation routes with individual results.

---

## Phase 4: User Story 2 - Keep Tool Coverage Complete (Priority: P2)

**Goal**: Prevent missing, stale, duplicate, malformed, or incorrectly classified fixtures from allowing catalog coverage to drift.

**Independent Test**: In `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, inject missing, stale, duplicate, malformed, and expected-error fixture conditions; each must fail with the affected name or category while the actual reviewed fixture registry remains valid.

### Tests for User Story 2 (REQUIRED) ⚠️

- [X] T011 [US2] Add failing fixture-completeness and expected-error contract tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py` for missing discovered names, stale fixture names, duplicate fixture names, non-object arguments, invalid outcome declarations, error-category mismatches, and escaped route exceptions.

### Implementation for User Story 2

- [X] T012 [US2] Implement deterministic bidirectional fixture validation and expected-error response classification in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, listing missing or stale names in stable order and rejecting invalid fixtures before route invocation.
- [X] T013 [US2] Complete the reviewed expected-error entries and their documented safe MCP categories in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py` so every no-data local outcome is asserted through the public route rather than treated as a success.
- [X] T014 [US2] Add or update complete reStructuredText docstrings for every Python function introduced or changed by T011-T013 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`.
- [X] T015 [US2] Refactor completeness-report and error-category assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, then run the User Story 2 independent-test conditions and the focused pytest command from `/Users/ctgunn/Projects/youtube-mcp-server/` with all cases green.

**Checkpoint**: Any catalog/fixture mismatch is an actionable focused-suite failure, while each actual discovered tool retains exactly one safe expected outcome.

---

## Phase 5: User Story 3 - Operate Verification Safely (Priority: P3)

**Goal**: Give operators a documented, credential-free focused command that is visibly separate from opt-in live YouTube verification.

**Independent Test**: From `/Users/ctgunn/Projects/youtube-mcp-server/`, run `make test-tools` without credentials; it must execute the deterministic suite with no outbound request, and the README must distinguish it from `make test` and the opt-in live smoke workflow.

### Tests for User Story 3 (REQUIRED) ⚠️

- [X] T016 [P] [US3] Add failing safety tests in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py` that prove fixture execution does not require credentials, outbound requests are blocked, and no destructive external mutation path is available.
- [X] T017 [P] [US3] Add failing documentation assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py` requiring `/Users/ctgunn/Projects/youtube-mcp-server/README.md` to document `make test-tools`, `make test`, and their separation from opt-in live verification.

### Implementation for User Story 3

- [X] T018 [P] [US3] Add the `test-tools` Make target and `.PHONY` declaration in `/Users/ctgunn/Projects/youtube-mcp-server/Makefile` to run only `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py` with the project Python interpreter.
- [X] T019 [P] [US3] Document the deterministic `make test-tools` workflow, full `make test` command, zero-credential/no-network safety boundary, and separate opt-in live smoke workflow in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`.
- [X] T020 [US3] Implement the controlled outbound-request guard and fixture-safety assertions required by T016 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, preserving the separate existing live-smoke test path.
- [X] T021 [US3] Add or update complete reStructuredText docstrings for every Python function introduced or changed by T016 and T020 in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`.
- [X] T022 [US3] Refactor the focused target, README wording, and safety diagnostics in `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, then run `make test-tools` from `/Users/ctgunn/Projects/youtube-mcp-server/` with all safety and documentation assertions green.

**Checkpoint**: Operators have a safe, documented focused verification command, and it cannot be confused with credential-gated live verification.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Reconcile final operator guidance and execute the required complete quality evidence after all feature changes.

- [X] T023 [P] Validate the focused and full-suite command instructions in `/Users/ctgunn/Projects/youtube-mcp-server/specs/403-layer4-tool-catalog/quickstart.md` against `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, updating `/Users/ctgunn/Projects/youtube-mcp-server/README.md` only if the implemented command surface differs.
- [X] T024 [P] Run `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_tool_catalog_endpoints.py` from `/Users/ctgunn/Projects/youtube-mcp-server/` and correct focused-suite regressions only in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`.
- [X] T025 Run `make quality` from `/Users/ctgunn/Projects/youtube-mcp-server/` after every final code or documentation change, then fix all lint, type-check, and full-test-suite failures in `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, `/Users/ctgunn/Projects/youtube-mcp-server/README.md`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py` before marking OPS-403 complete.

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1: Setup
    ↓
Phase 2: Foundational route-test foundation
    ↓
Phase 3: US1 — discovery-derived catalog invocation (MVP)
    ↓
Phase 4: US2 — fixture completeness and expected-error enforcement
    ↓
Phase 5: US3 — safe command and operator documentation
    ↓
Phase 6: Polish and full quality gate
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2. It creates the reviewed fixture registry and per-tool route-invocation behavior; it is the MVP.
- **US2 (P2)**: Starts after US1 because it validates deliberate missing/stale/error variants of US1's fixture registry. It must leave the actual registry independently valid.
- **US3 (P3)**: Starts after US2 because it exposes the completed deterministic suite as an operator command and documents the final safety boundary.

### Within Each User Story

1. Complete its Red task(s) and demonstrate failure.
2. Complete its Green implementation tasks with only the minimum behavior required for the Red assertions.
3. Add or update all required reStructuredText docstrings for touched Python functions.
4. Complete its Refactor task, run its focused evidence command, and keep prior-story behavior green.

## Parallel Opportunities

- **US3 Red tests**: T016 and T017 modify different test files and may run in parallel after US2.
- **US3 implementation surfaces**: T018 and T019 modify different files and may run in parallel after the Red assertions are in place.
- **Final checks**: T023 and T024 may run in parallel after US3; both precede T025.

## Parallel Example: User Story 3

```text
Task T016: Add credential and outbound-request safety coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_mcp_tool_catalog_endpoints.py
Task T017: Add README command-boundary documentation coverage in /Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py

Task T018: Add the focused Make target in /Users/ctgunn/Projects/youtube-mcp-server/Makefile
Task T019: Document the command boundary in /Users/ctgunn/Projects/youtube-mcp-server/README.md
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001-T005 to establish the public-route foundation.
2. Complete T006-T010 to supply every discovered tool with a safe fixture and an individually reported `tools/call` result.
3. Run the User Story 1 independent-test command and demonstrate discovery-driven coverage before adding fixture-governance or operator-workflow enhancements.

### Incremental Delivery

1. Deliver US1 as route-level catalog coverage.
2. Add US2 to make catalog/fixture drift fail explicitly and safely.
3. Add US3 to provide the maintainable focused command and clear live-verification boundary.
4. Complete T023-T025, ending with a passing complete quality gate.

## Notes

- Every task follows the required `- [ ] T### [P?] [US?] description with absolute file path` format.
- `[P]` is used only for tasks that modify distinct files and have no unfinished prerequisite task.
- Do not replace discovery with a hard-coded tool-name list, invoke handlers directly, add credentials to fixtures, permit outbound YouTube access, or run live verification from `make test-tools`.
