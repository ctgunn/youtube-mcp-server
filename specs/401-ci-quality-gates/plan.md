# Implementation Plan: CI/CD Quality Gates

**Branch**: `401-ci-quality-gates` | **Date**: 2026-08-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/401-ci-quality-gates/spec.md`

## Summary

Deliver OPS-401 by making repository quality an explicit, reusable gate: a pull-request workflow reports separate stable `lint`, `typecheck`, and `tests` outcomes; an active GitHub ruleset for `main` requires those outcomes for the current revision; and both supported deployment paths run the same canonical quality command before any build, publish, infrastructure, or deploy stage. The work will add declared, reproducible development tooling and concise operator guidance for clean-checkout validation, release provenance, and safe prerequisite failures. It will extend the existing Cloud Build primary deployment path and GitHub Actions manual fallback without changing the MCP runtime or creating another deployment route.

Canonical terms: **quality command**, **quality evaluation**, **required check**, **protected revision**, **release provenance**, **preflight**, **deployment record**, and **verification record**.

## Technical Context

**Language/Version**: Python 3.11 for test and deployment-support tooling; YAML for checked-in automation; Make for canonical developer commands  
**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn service; declared development tooling comprising `pytest`, Ruff, and mypy; existing Cloud Build, GitHub Actions, Terraform, Docker, `scripts/deploy_cloud_run.sh`, and `scripts/verify_cloud_run_foundation.py`  
**Storage**: No new runtime storage. Checked-in workflow/configuration/documentation files, an externally configured GitHub `main` ruleset, and existing file-based image, deployment, and verification evidence artifacts  
**Testing**: `python -m pytest` for the full repository suite; `make lint`, `make typecheck`, `make test`, and `make quality` for canonical quality commands; focused unit, integration, and contract tests for workflow shape, provenance, gate ordering, and documentation  
**Documentation Style**: Markdown runbooks and contracts; every new or changed Python function, including test helpers, must have a complete reStructuredText docstring documenting purpose, inputs, outputs, relevant raised errors, and side effects  
**Target Platform**: GitHub pull requests targeting `main`; Cloud Build as the primary push-triggered GCP deployment path; GitHub Actions as the manually dispatched fallback; local Python 3.11 developer environment  
**Project Type**: Python web service with checked-in CI/CD automation, GCP deployment tooling, and an external repository-governance policy  
**Performance Goals**: Every PR revision receives all three quality outcomes before it is eligible to merge; no supported deployment begins build/publish/reconcile/deploy after a non-passing quality evaluation; an authorized operator reproduces the documented non-production release and verification procedure within the spec's 30-minute target, excluding declared external provisioning  
**Constraints**: The `main` ruleset is repository configuration outside the worktree and must be documented and verified read-only; check names must be stable, unique, and GitHub-Actions-sourced; no path/commit-message filters may skip a required PR workflow; type checking is initially scoped to `src/mcp_server` to establish a reliable checked-in baseline without expanding OPS-401 into a legacy type-remediation project; deployment must bind quality evidence, source commit, image digest, and verification evidence to one revision; secrets must never appear in commands, reports, artifacts, or diagnostics  
**Scale/Scope**: One canonical quality command surface, three required PR checks, one `main` governance rule, one primary Cloud Build path, one GitHub Actions fallback path, one non-production reproducibility procedure, and no public MCP contract changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

**Pre-design gate result: PASS.** This feature changes repository-governance and deployment-workflow contracts, not public MCP messages. `contracts/quality-gate-contract.md` and `contracts/release-procedure-contract.md` define those external operator and automation boundaries. Implementation must finish with `python -m pytest` after the final code changes; it must also retain passing `make lint` and `make typecheck` evidence. Python functions are not expected in the minimal workflow/configuration implementation, but any introduced or modified function—including a test helper—requires a complete reStructuredText docstring.

## Project Structure

### Documentation (this feature)

```text
specs/401-ci-quality-gates/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── quality-gate-contract.md
│   └── release-procedure-contract.md
└── tasks.md                  # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
.github/
└── workflows/
    ├── quality.yml           # New PR quality workflow
    └── hosted-deploy.yml     # Existing manual deployment fallback

cloudbuild.yaml               # Existing primary automatic deployment workflow
Makefile                      # Canonical quality commands
pyproject.toml                # Declared development tools and their configuration
README.md                     # Local-quality and hosted-release runbook

scripts/
├── deploy_cloud_run.sh
└── verify_cloud_run_foundation.py

src/mcp_server/
└── deploy.py                 # Provenance/preflight helpers only if workflow files cannot safely own them

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service, Cloud Build primary pipeline, GitHub Actions fallback, deployment script, verification script, and artifact model. Add one PR-only quality workflow and one canonical local command surface. Prefer declarative workflow and Makefile changes; add a small Python helper only if necessary to create/validate non-secret provenance or preflight records, with reStructuredText docstrings and direct unit coverage.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Demonstrate the current gaps with tests or inspections: no PR-triggered quality workflow, no enforceable `main` rule, no designated type-check command, and duplicated deployment quality commands that only run tests and lint.
- **Green**: Record the selected required-check names, ruleset policy, canonical toolchain and commands, source/image provenance rules, release preflight boundary, and secret-safe evidence model in `research.md`.
- **Refactor**: Remove ambiguous references to an all-in-one check or tag-only release identity so the design consistently uses separate status names and immutable release provenance.

### Phase 1 - Design and Contracts

- **Red**: Define contract tests that fail until the PR workflow exposes the three required check names, the ruleset policy requires them for the latest protected revision, and the deployment contract makes the quality/preflight boundary precede build and deploy.
- **Green**: Produce `data-model.md`, `contracts/quality-gate-contract.md`, `contracts/release-procedure-contract.md`, and `quickstart.md`; define quality states, provenance fields, safe failure classes, operator commands, and read-only ruleset verification.
- **Refactor**: Normalize check names, stage names, command names, revision terminology, and secret-handling language across all design artifacts. Re-run the Constitution Check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Start implementation with failing workflow, contract, and integration tests for each missing PR check, a missing/cancelled/failing result, a stale or mismatched revision, a deployment gate bypass, and stale/missing operator instructions.
- **Green**: Add the minimum declared development-tool setup; canonical Make targets; PR-only workflow; Cloud Build and GitHub fallback use of the canonical command; non-secret preflight/provenance evidence; `main` ruleset setup/verification guidance; and README runbook updates needed to make the tests pass.
- **Refactor**: Collapse duplicated quality commands into the canonical target, remove redundant workflow/documentation wording, verify any new or changed Python functions have reStructuredText docstrings, then run `make lint`, `make typecheck`, and the required final full suite `python -m pytest`.

## User Story Delivery Strategy

### User Story 1 - Protect Changes with Required Quality Checks

- **Red**: Add failing contract tests proving that no PR workflow emits all of `lint`, `typecheck`, and `tests`, that each check is not individually identifiable, and that the documented `main` policy is missing or permits stale, skipped, cancelled, or failed outcomes.
- **Green**: Add the PR workflow with three independent, uniquely named checks; add the canonical commands and declared tool versions/configuration; document and verify the active `main` ruleset requiring pull requests, the three GitHub Actions checks, and up-to-date revision evaluation.
- **Refactor**: Keep check names and command invocation identical between workflow, ruleset verification, contracts, tests, and README; run the full suite after the final change.

### User Story 2 - Reproduce Build and Deployment Procedures

- **Red**: Add failing documentation/integration tests proving a clean checkout cannot install the complete development toolchain, run all quality categories through one command, or identify the source revision, image identity, deployment revision, and verification result from documented evidence.
- **Green**: Declare reproducible development dependencies; add canonical `make` targets; update the operator runbook with local versus hosted prerequisites, safe missing-input handling, build/deploy/verify commands, and non-secret evidence expectations. Bind the checked-out full commit SHA and resolved immutable image digest to the deployment and verification records.
- **Refactor**: Consolidate repeated installation and release commands into one documented canonical source; preserve existing hosted deployment and verification entry points; run the full suite after the final change.

### User Story 3 - Guard Automated Deployments

- **Red**: Add failing workflow/integration coverage proving a non-passing quality result, absent type check, mismatched requested ref, or missing preflight prerequisite can reach image publication, infrastructure reconciliation, or deployment.
- **Green**: Route Cloud Build and GitHub Actions fallback through the canonical quality command after resolving the exact checkout commit and before all later stages. Validate safe prerequisite categories, record quality/revision/image provenance without secrets, and stop the workflow before build/deploy on a failing, cancelled, or incomplete quality outcome.
- **Refactor**: Align primary and fallback stage ordering and evidence names, leave no second deployment path or duplicated quality sequence, then run the final full suite.

## Coverage Strategy

- **Unit coverage**: Validate any introduced provenance, preflight, check-state, or mismatch helpers; assert that their serialized data contains names/statuses but never secrets. Every new or modified test/helper function carries a reStructuredText docstring.
- **Contract coverage**: Lock the quality command names, PR workflow trigger/forbidden skip filters, exact required ruleset settings, release provenance fields, quality-before-deploy order, and secret-safe failure descriptions in the two contract documents.
- **Integration coverage**: Read and validate the PR workflow, Cloud Build pipeline, GitHub fallback workflow, Make targets, project tool declaration, and README as one delivery surface. Verify a failed/missing/cancelled quality status and a revision/digest mismatch stop later release stages.
- **Manual governance coverage**: From an authorized repository administrator account, inspect the active `main` ruleset or documented branch-protection fallback and perform one passing PR plus controlled lint, typecheck, and test failures. Confirm the current head (or merge-queue revision when enabled) is blocked until all exact check names pass.
- **Regression coverage**: Preserve the existing FND-025/FND-028 ordered `quality_gate -> image_publish -> infrastructure_reconcile -> terraform_output_export -> deploy -> hosted_verification` contract, FND-008 deployment/verification records, secret boundary, local-first workflow, and public MCP behavior.
- **Completion commands**: `make lint`; `make typecheck`; and, after the final code change, `python -m pytest` (the constitution-required full repository suite). A passing `make quality` is retained as the canonical combined evidence command.

## Observability, Security, and Simplicity

- **Observability**: Each quality check reports its own stable result for the evaluated commit. Release evidence associates quality outcomes, resolved commit, immutable image digest, deployment revision, and verification result; a failure identifies its stage and safe remediation class.
- **Security**: PR validation uses `pull_request` rather than a privileged pull-request trigger and receives no deployment credentials. Ruleset verification is read-only. Preflight reports only missing prerequisite names/categories. Workflows, docs, and artifacts must never print, persist, or accept secret values as evidence.
- **Simplicity**: One canonical quality command backs local, PR, primary deployment, and fallback deployment use cases. Cloud Build remains the automatic deployment owner; GitHub Actions remains manual fallback. The feature does not add a separate CI service, image-only deploy path, runtime endpoint, database, or public MCP tool.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

**Post-design gate result: PASS.** The design defines the external repository-governance and release contracts, maintains mandatory Red-Green-Refactor sequencing, and has a clear final full-suite command: `python -m pytest`. It adds no public MCP contract. All planned Python changes are optional and narrowly constrained; any such function must receive a complete reStructuredText docstring and unit coverage. No constitution exception is needed.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
