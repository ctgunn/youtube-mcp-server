<!--
Sync Impact Report
- Version change: 1.0.0 -> 1.1.0
- Modified principles:
  - Template Principle 1 -> I. MCP Contract-First Design
  - Template Principle 2 -> II. CLI and Tooling Consistency
  - Template Principle 3 -> III. Red-Green-Refactor TDD (NON-NEGOTIABLE)
  - IV. Integration and Regression Coverage -> IV. Full-Suite Integration and Regression Coverage
  - Template Principle 5 -> V. Observability, Security, and Simplicity
- Added sections:
  - None
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ updated: .specify/templates/plan-template.md
  - ✅ updated: .specify/templates/spec-template.md
  - ✅ updated: .specify/templates/tasks-template.md
  - ⚠ pending: .specify/templates/commands/*.md (directory not present in repository)
  - ✅ updated: .codex/prompts/speckit.tasks.md
  - ✅ updated: .codex/prompts/speckit.implement.md
  - ✅ updated: README.md
- Deferred follow-up TODOs:
  - TODO(RATIFICATION_DATE): Original adoption date not recoverable from repository history in this workspace.
-->

# YouTube MCP Server Constitution

## Core Principles

### I. MCP Contract-First Design
Every feature MUST begin by defining or updating explicit interface contracts
before implementation. Contract changes MUST be documented in feature artifacts,
and breaking contract changes MUST include a migration or versioning plan.
Rationale: Stable interfaces are the core reliability boundary for MCP clients.

### II. CLI and Tooling Consistency
All exposed tools MUST provide deterministic behavior, clear error messaging,
and machine-readable outputs where applicable. New feature work MUST preserve
command and schema compatibility unless a documented breaking change is approved.
Rationale: Predictable tooling enables safe automation and agent reliability.

### III. Red-Green-Refactor TDD (NON-NEGOTIABLE)
When planning and implementing features, teams MUST apply Red-Green-Refactor
test-driven development in every phase. Plans MUST include explicit Red, Green,
and Refactor steps for each user story and shared foundation work. Implementation
MUST begin with failing tests (Red), proceed with minimal passing code (Green),
and conclude with behavior-preserving cleanup (Refactor) before task completion.
Feature work MUST NOT be considered complete until the full repository test
suite has been executed after the final code changes for that work item.
Rationale: Mandatory TDD controls regression risk and keeps scope focused.

### IV. Full-Suite Integration and Regression Coverage
Each feature MUST include integration coverage for contract boundaries and
cross-component behavior, plus regression tests for fixed defects. Validation
MUST include a full repository test-suite run after changes are made, not just
targeted or feature-local tests. If any test fails during that full run, the
failure MUST be fixed before the feature or bugfix is considered complete.
Rationale: Unit-only validation is insufficient for MCP server interoperability.

### V. Observability, Security, and Simplicity
Changes MUST include actionable logs for failure diagnosis, MUST avoid exposing
secrets in code or logs, and MUST prefer the simplest architecture that meets
stated requirements. Complexity MUST be justified in the plan's constitution
exceptions table.
Rationale: Maintainability and safe operations are required for production use.

## Engineering Constraints

- Python-based implementation and test tooling MUST remain the default unless
  a plan documents and justifies an exception.
- Every feature plan MUST define:
  - required test frameworks and commands,
  - contract validation approach,
  - rollback or mitigation strategy for breaking behavior,
  - the command used to run the full repository test suite before completion.
- Feature specs MUST define independently testable user stories and measurable
  success criteria.

## Delivery Workflow and Quality Gates

Feature work MUST follow this lifecycle:
1. Specification: define user stories, acceptance scenarios, and measurable outcomes.
2. Planning: pass Constitution Check, with explicit Red-Green-Refactor steps per phase.
3. Tasking: generate ordered tasks that place Red before Green and Refactor before done.
4. Implementation: execute tasks in dependency order; do not mark tasks complete until
   all required tests pass and the full repository test suite is green.
5. Review: verify constitution compliance, evidence of a passing full repository
   test-suite run, and migration notes for contract-impacting changes.

## Governance

This constitution is authoritative over project workflow and quality standards.
Amendments require: (1) a documented proposal, (2) explicit update of impacted
templates and operational prompts, and (3) approval by project maintainers.

Versioning policy for this document uses semantic versioning:
- MAJOR: removing or redefining a principle in a backward-incompatible way.
- MINOR: adding a principle/section or materially expanding governance requirements.
- PATCH: non-semantic clarifications or editorial improvements.

Compliance review expectations:
- Every plan and task artifact MUST include a constitution compliance check.
- Pull requests MUST provide evidence of Red-Green-Refactor execution and a
  passing full repository test-suite run performed after the final code changes.
- Reviewers MUST reject changes that bypass mandatory TDD, omit required
  coverage, or rely only on partial test runs when full-suite validation is expected.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): Original adoption date unknown | **Last Amended**: 2026-03-21
