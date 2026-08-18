# Tasks: CI/CD Quality Gates

**Input**: Design documents from `/Users/ctgunn/Projects/youtube-mcp-server/specs/401-ci-quality-gates/`
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/](contracts/), and [quickstart.md](quickstart.md)

**Tests**: Tests are mandatory. Every phase follows Red-Green-Refactor. Completion requires passing `make lint`, `make typecheck`, and the constitution-required full repository suite `python -m pytest` after the final code changes. Every new or modified Python function, including test helpers and test methods, must have a complete reStructuredText docstring.

**Organization**: Tasks are grouped by independently testable user story. The quality-tooling foundation is intentionally completed first because every story relies on its canonical commands.

## Phase 1: Setup (Shared Test Scaffold)

**Purpose**: Establish the failing, repository-level command contract before adding the development toolchain.

- [X] T001 [P] Add failing canonical quality-command contract coverage, with reStructuredText docstrings on new test methods, in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_ci_quality_commands_contract.py`

---

## Phase 2: Foundational (Canonical Quality Tooling)

**Purpose**: Make lint, type checking, and full tests reproducible through one declared command surface; this blocks all user-story work.

**⚠️ CRITICAL**: Complete this phase before starting any user-story phase.

- [X] T002 Declare the `dev` dependency group and configure pytest, Ruff, and the `src/mcp_server` mypy baseline in `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml`
- [X] T003 Add deterministic `lint`, `typecheck`, `test`, and serial `quality` targets that invoke the declared tools in `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`
- [ ] T004 Repair all errors reported by `make typecheck` within `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` without broadening the type-check scope beyond the approved baseline
- [ ] T005 Add or update complete reStructuredText docstrings for every Python function modified by T004 and every new/modified test method in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_ci_quality_commands_contract.py`
- [ ] T006 Run the T001 contract test, make the command surface pass, and refactor duplicated configuration/target wording while preserving `make lint`, `make typecheck`, `make test`, and `make quality` in `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml` and `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`

**Checkpoint**: The declared toolchain installs from a clean checkout and the four canonical commands are defined. User stories can now proceed.

---

## Phase 3: User Story 1 - Protect Changes with Required Quality Checks (Priority: P1) 🎯 MVP

**Goal**: Every pull-request revision receives distinct `lint`, `typecheck`, and `tests` results, and the active `main` governance rule blocks a merge until the exact latest revision passes all three.

**Independent Test**: Open a PR to `main`, observe the three exact checks for its newest revision, and use controlled lint, typecheck, and test failures to confirm the protected merge flow is blocked until each failure is corrected and rerun.

### Red: Failing Tests for User Story 1

- [ ] T007 [P] [US1] Add failing PR-workflow contract coverage, with reStructuredText docstrings on new test methods, for the `pull_request` trigger, exact check names, no skip filters, no secrets, and canonical command use in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_ci_pull_request_quality_contract.py`
- [ ] T008 [P] [US1] Add failing unit coverage, with reStructuredText docstrings on new test methods, for active-rule validation, latest-revision checks, source identity, and safe JSON failures in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_github_quality_gate_verifier.py`

### Green: Implementation for User Story 1

- [ ] T009 [US1] Create the unprivileged PR-only workflow with separately named `lint`, `typecheck`, and `tests` jobs that use canonical targets and no deployment context in `/Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/quality.yml`
- [ ] T010 [US1] Implement a read-only, machine-readable `main` ruleset/branch-protection verifier that rejects missing, stale, bypassed, or incorrectly sourced required checks in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_github_quality_gate.py`
- [ ] T011 [US1] Add complete reStructuredText docstrings for all new or modified functions and test methods in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_github_quality_gate.py` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_github_quality_gate_verifier.py`
- [ ] T012 [US1] Document the exact active-`main` ruleset settings, the branch-protection fallback prohibition on divergent policies, the read-only verifier command, and controlled PR evidence procedure in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [ ] T013 [US1] Apply and read back the active `main` ruleset (or equivalent documented branch-protection fallback) with an authorized administrator using `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_github_quality_gate.py` and record the safe verification procedure in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`

### Refactor: User Story 1

- [ ] T014 [US1] Run the User Story 1 contract and verifier tests, remove duplicated check-name/policy definitions, and keep the workflow, verifier, tests, and runbook aligned in `/Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/quality.yml`, `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_github_quality_gate.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_ci_pull_request_quality_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_github_quality_gate_verifier.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/README.md`

**Checkpoint**: User Story 1 is independently complete when the three named checks and active external policy block non-passing latest revisions.

---

## Phase 4: User Story 2 - Reproduce Build and Deployment Procedures (Priority: P2)

**Goal**: An authorized maintainer can follow one complete, safe local-quality and non-production release procedure from a clean checkout without undocumented repository steps.

**Independent Test**: In a clean checkout, install the documented development tooling, run `make quality`, and follow the README's non-production release/verification path to identify source revision, deployment revision, and pass/fail verification evidence without exposing secrets.

### Red: Failing Tests for User Story 2

- [ ] T015 [P] [US2] Add failing documentation integration coverage, with reStructuredText docstrings on new test methods, for clean-checkout installation, four canonical commands, local-versus-hosted separation, safe prerequisite guidance, and release-evidence instructions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`

### Green: Implementation for User Story 2

- [ ] T016 [US2] Update the local engineering and hosted release sections with one clean-checkout install path, canonical quality commands, prerequisites, safe missing-input handling, source/image/deployment/verification evidence, and local-versus-hosted boundaries in `/Users/ctgunn/Projects/youtube-mcp-server/README.md`
- [ ] T017 [US2] Add or update complete reStructuredText docstrings for every new or modified Python test method in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`
- [ ] T018 [US2] Reproduce the documented local procedure in a clean checkout, update ambiguous README wording discovered during the run, and run the User Story 2 documentation integration test in `/Users/ctgunn/Projects/youtube-mcp-server/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`

### Refactor: User Story 2

- [ ] T019 [US2] Consolidate duplicate install, quality, and release instructions while preserving the tested procedure in `/Users/ctgunn/Projects/youtube-mcp-server/README.md` and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_quality_gate_docs.py`

**Checkpoint**: User Story 2 is independently complete when a clean-checkout maintainer can follow the documented procedure without an undocumented repository step.

---

## Phase 5: User Story 3 - Guard Automated Deployments (Priority: P3)

**Goal**: The Cloud Build primary path and GitHub Actions fallback both run a passing canonical quality gate for the actual checkout before build/deploy work, preserve safe provenance, and stop before later stages on a non-passing result.

**Independent Test**: Use controlled workflow fixtures to show that a failed/missing/cancelled quality result, a commit mismatch, a missing safe prerequisite, or a digest mismatch prevents image publication, infrastructure reconciliation, and deployment; show that a passing exact revision proceeds to existing hosted verification.

### Red: Failing Tests for User Story 3

- [ ] T020 [P] [US3] Add failing release-guard contract coverage, with reStructuredText docstrings on new test methods, for `make quality`, preflight ordering, immutable revision/image provenance, and secret-safe artifact fields in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_ci_release_guard_contract.py`
- [ ] T021 [P] [US3] Add failing unit coverage, with reStructuredText docstrings on new test methods, for quality-state eligibility, SHA/digest mismatch rejection, preflight categories, and secret-free provenance serialization in `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_ci_release_provenance.py`
- [ ] T022 [P] [US3] Add failing end-to-end workflow-shape coverage, with reStructuredText docstrings on new test methods, proving both deployment paths stop before build/deploy after a bad gate and preserve one resolved revision in `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_release_guard_workflows.py`

### Green: Implementation for User Story 3

- [ ] T023 [US3] Extend release provenance and safe preflight state validation/serialization for quality statuses, full source SHA, immutable image digest, deployment revision, and verification outcome in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`
- [ ] T024 [US3] Update the deployment entrypoint to validate and persist non-secret release provenance while deploying the digest-qualified image in `/Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`
- [ ] T025 [US3] Add complete reStructuredText docstrings for every new or modified Python function and test method in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_ci_release_provenance.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_ci_release_guard_workflows.py`
- [ ] T026 [US3] Change the Cloud Build primary path to resolve the checkout's full SHA, run safe preflight and `make quality` before later stages, resolve the image digest, deploy that digest, and publish non-secret provenance evidence in `/Users/ctgunn/Projects/youtube-mcp-server/cloudbuild.yaml`
- [ ] T027 [US3] Change the manual GitHub fallback to resolve the actual checked-out SHA rather than trust a mutable dispatch ref, run the same preflight and `make quality` gate, deploy a digest-qualified image, and upload the provenance evidence in `/Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml`
- [ ] T028 [US3] Update existing deployment-pipeline expectations from inline lint/test commands to the canonical quality gate and add provenance/order assertions in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_hosted_deployment_pipeline_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_hosted_deployment_workflow.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_cloud_run_deployment_assets.py`
- [ ] T029 [US3] Run the authorized non-production fallback release and a controlled failing-gate exercise according to `/Users/ctgunn/Projects/youtube-mcp-server/specs/401-ci-quality-gates/quickstart.md`, confirming safe SHA/digest/deployment/verification evidence and no downstream action after failure

### Refactor: User Story 3

- [ ] T030 [US3] Run all User Story 3 unit, contract, and integration tests; remove duplicate provenance or quality-stage logic while preserving the `quality_gate -> image_publish -> infrastructure_reconcile -> terraform_output_export -> deploy -> hosted_verification` contract in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`, `/Users/ctgunn/Projects/youtube-mcp-server/scripts/deploy_cloud_run.sh`, `/Users/ctgunn/Projects/youtube-mcp-server/cloudbuild.yaml`, and `/Users/ctgunn/Projects/youtube-mcp-server/.github/workflows/hosted-deploy.yml`

**Checkpoint**: User Story 3 is independently complete when both supported deployment paths block before later stages on any ineligible gate/provenance condition and link a passing release to one SHA and image digest.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the feature as one secure, maintainable delivery surface.

- [ ] T031 [P] Add cross-path regression coverage, with reStructuredText docstrings on new test methods, that rejects secret-bearing workflow/artifact output and PR deployment credentials in `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_ci_quality_gate_security_contract.py`
- [ ] T032 Review every changed Python function and test method for complete reStructuredText docstrings and update omissions in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/deploy.py`, `/Users/ctgunn/Projects/youtube-mcp-server/scripts/verify_github_quality_gate.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [ ] T033 Run `make lint`, `make typecheck`, and `make quality`; fix all reported failures in `/Users/ctgunn/Projects/youtube-mcp-server/pyproject.toml`, `/Users/ctgunn/Projects/youtube-mcp-server/Makefile`, `/Users/ctgunn/Projects/youtube-mcp-server/src/`, `/Users/ctgunn/Projects/youtube-mcp-server/scripts/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/`
- [ ] T034 Run the final `python -m pytest` full repository suite after all code changes and fix every failure before completion in `/Users/ctgunn/Projects/youtube-mcp-server/tests/`

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1: setup test scaffold
  -> Phase 2: canonical quality tooling (blocks all stories)
     -> Phase 3: US1 PR protection (MVP)
        -> Phase 4: US2 reproducible procedures
           -> Phase 5: US3 deployment guardrails
              -> Phase 6: polish and final full-suite verification
```

### User Story Dependencies

- **US1 (P1)** starts after canonical quality tooling and is the MVP. It depends on an authorized administrator for the external `main` ruleset, but its workflow/verifier code remains testable with fixtures.
- **US2 (P2)** starts after canonical quality tooling. It consumes the canonical commands and incorporates the US1 governance procedure in the same README, so schedule its README edit after T012 to avoid conflicting edits.
- **US3 (P3)** starts after canonical quality tooling. It can develop its provenance helpers/tests in parallel with US1/US2, but its workflow edits must incorporate the canonical commands produced in Phase 2 and its final documentation references from US2.

### Within Each User Story

1. Complete the Red tasks and confirm they fail for the intended missing behavior.
2. Complete the Green tasks in listed order, with no behavior outside that story's contract.
3. Add/review reStructuredText docstrings for every touched Python function before the Refactor task.
4. Complete the Refactor task and run its focused tests before treating the story checkpoint as complete.

## Parallel Opportunities

- **Phase 1/2**: T001 is independent test scaffolding; after it is complete, T002 and T003 can be handled concurrently because they edit different configuration files. T004 depends on both.
- **US1**: T007 and T008 can run in parallel because they create separate contract and unit test files.
- **US2**: T015 can run while US1's verifier implementation is in progress, but its README implementation must follow T012 to avoid a same-file conflict.
- **US3**: T020, T021, and T022 can run in parallel because they create separate contract, unit, and integration test files. T026 and T027 can run in parallel after T023-T025 because they update separate workflow files.
- **Polish**: T031 can run in parallel with the docstring review in T032. T033 and T034 remain final sequential validation gates.

## Parallel Example: User Story 1

```bash
# Launch the independent Red tests together:
Task: "T007 Add PR-workflow contract coverage in tests/contract/test_ci_pull_request_quality_contract.py"
Task: "T008 Add active-rule verifier unit coverage in tests/unit/test_github_quality_gate_verifier.py"
```

## Parallel Example: User Story 2

```bash
# While workflow/verifier work continues in a different branch, start the isolated Red documentation test:
Task: "T015 Add documentation integration coverage in tests/integration/test_ci_quality_gate_docs.py"
```

## Parallel Example: User Story 3

```bash
# Launch the independent Red tests together:
Task: "T020 Add release-guard contract coverage in tests/contract/test_ci_release_guard_contract.py"
Task: "T021 Add release-provenance unit coverage in tests/unit/test_ci_release_provenance.py"
Task: "T022 Add deployment workflow-shape integration coverage in tests/integration/test_ci_release_guard_workflows.py"

# After provenance helpers exist, launch the independent workflow edits together:
Task: "T026 Update cloudbuild.yaml"
Task: "T027 Update .github/workflows/hosted-deploy.yml"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2 to establish an installable, canonical quality command surface.
2. Complete Phase 3, including the authorized active-`main` ruleset configuration and controlled PR evidence.
3. Run the User Story 1 focused tests and independently verify that a failing latest revision cannot merge.
4. Stop here if only PR protection is needed; the canonical tooling and protected flow already deliver the highest-value OPS-401 outcome.

### Incremental Delivery

1. Deliver the canonical command foundation.
2. Deliver US1 and verify enforced PR protection.
3. Deliver US2 and verify a clean-checkout maintainer can reproduce the procedure.
4. Deliver US3 and verify automatic/fallback release guardrails with non-production evidence.
5. Complete Phase 6 only after all desired stories are integrated.

## Notes

- `[P]` identifies work on different files with no dependency on unfinished tasks.
- `[US#]` labels provide story traceability; setup, foundational, and polish tasks intentionally have no story label.
- The active GitHub `main` ruleset is an external repository setting. T013 is an explicit implementation task because a checked-in workflow alone cannot block merges.
- Do not treat targeted test success as feature completion: T034 requires the full repository suite after the final code change.
