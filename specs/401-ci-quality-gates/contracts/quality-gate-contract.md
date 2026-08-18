# Quality Gate Contract

## Purpose

Define the repository-facing contract that evaluates each pull-request revision and controls its quality-gate eligibility. This contract changes repository governance and automation only; it does not add or change an MCP tool, endpoint, or client payload.

## Canonical Quality Interface

An authorized contributor installs the declared development tooling from a clean checkout with:

```bash
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

The repository exposes these stable commands:

| Command | Required result |
|---|---|
| `make lint` | Runs `python -m ruff check .`; exits nonzero for a lint violation. |
| `make typecheck` | Runs `python -m mypy src/mcp_server`; exits nonzero for a type-validation error. |
| `make test` | Runs `python -m pytest`; exits nonzero for any test failure. |
| `make quality` | Runs lint, typecheck, and test in that order; exits nonzero if any constituent command does not pass. |

The declared project configuration owns versions and configuration for all three tools. Workflows and documentation must call these command names rather than restating individual tool commands.

## Pull-Request Workflow Contract

| Property | Required behavior |
|---|---|
| Trigger | A dedicated GitHub Actions workflow runs on the unprivileged `pull_request` event for pull requests targeting `main`. |
| Checks | The workflow exposes three unique, stable GitHub Actions job/check names: `lint`, `typecheck`, and `tests`. Each reports only its own category outcome for the checked-out revision. |
| Scope | The workflow has no deployment steps, cloud credentials, secrets, path filters, commit-message skip logic, or privileged pull-request trigger. |
| Revision | Each check records/executes for the current pull-request head revision (or the merge-queue revision if such a queue is later enabled). A result for an earlier revision is not eligible. |
| Failure | A failed, cancelled, missing, skipped, or pending check is non-passing and remains visible as the blocking category. |

## Required `main` Governance Contract

The repository administrator configures one active rule for `main`:

- It requires pull requests before merge.
- It requires the exact `lint`, `typecheck`, and `tests` checks, sourced from GitHub Actions.
- It requires the branch to be up to date before merge.
- It does not grant normal maintainer bypass.
- It is either an active GitHub ruleset or a classic branch-protection rule. If classic branch protection is the fallback, it has equivalent requirements; the two mechanisms must not have divergent check sets or policies.

This external configuration is verified with authorized, read-only repository settings inspection and controlled pull requests. A source-only workflow test is necessary but not sufficient to prove that the active rule is enforced.

## Eligibility and Failure Contract

| Check state for current revision | Quality-gate result | Merge/deployment behavior |
|---|---|---|
| All `pass` | `eligible` | May continue to independent review/authorization or release preflight. |
| Any `fail` | `blocked` | Protected merge and supported deployment must stop. |
| Any `cancelled`, `missing`, `skipped`, or `pending` | `blocked` | Protected merge and supported deployment must stop; rerun or remediate the named category. |
| Result for another revision | `blocked` | Re-evaluate the exact current revision. |

## Verification Obligations

- Contract and integration tests must assert the trigger, exact check names, canonical command use, no skip filters, and lack of deploy secrets in the PR workflow.
- An authorized administrator must prove enforcement using one passing PR and controlled lint, typecheck, and test failures, checking the newest eligible revision after each update.
- Repository reports and test fixtures must retain only safe statuses, identifiers, and remediation categories; no credential value may be emitted.
