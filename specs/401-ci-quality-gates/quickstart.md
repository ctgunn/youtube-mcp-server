# Quickstart: CI/CD Quality Gates

This guide is the implementation and verification runbook for OPS-401. It distinguishes safe local quality validation from authorized hosted deployment; do not use local commands as a substitute for the deployment procedure.

## 1. Start from a clean checkout

```bash
git clone <repository-url>
cd youtube-mcp-server
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Use Python 3.11 and a supported `make` installation. Do not place credentials in command history, shell output, test fixtures, or release evidence.

## 2. Run the canonical local quality gate

Run individual categories while developing:

```bash
make lint
make typecheck
make test
```

Before proposing a change or release, run the combined gate:

```bash
make quality
```

All three commands must pass. A nonzero exit, cancellation, skip, or missing result is blocking; fix or rerun the named category. After the final implementation change, the constitution-required full-suite evidence is:

```bash
python -m pytest
```

## 3. Verify pull-request governance

An authorized repository administrator configures and reads back the active `main` ruleset (or the documented classic branch-protection fallback). Confirm that it:

1. requires pull requests;
2. requires GitHub-Actions-sourced `lint`, `typecheck`, and `tests` checks;
3. requires the branch to be current before merge; and
4. does not grant normal maintainer bypass.

Open a pull request to `main`. Verify that the PR-only workflow receives no deployment credentials and reports the three exact check names for its newest revision. Repeat with controlled failures of lint, typecheck, and tests. Each failure, cancellation, or missing result must block merge. Push a newer revision and confirm earlier green statuses are not used for eligibility.

## 4. Verify deployment guardrails without a production release

Use the existing hosted deployment prerequisites and non-production setup documented in the root README. Required account access, GCP project setup, Terraform inputs, workflow identity, and secret-reference setup remain external prerequisites; they must be configured before a release attempt. Never copy their values into this document, workflow logs, or artifacts.

For the supported manually dispatched GitHub Actions workflow:

1. In GitHub, open **Actions** → **hosted-deploy** → **Run workflow**.
2. Select `main` for the workflow source and `target_ref` unless releasing a
   specific reviewed revision; select `staging` for the target environment.
3. Confirm the workflow artifact named `hosted-deploy-<source-sha>` is
   available after the run.

Then confirm that the workflow:

1. resolves and records the actual checked-out full commit SHA;
2. passes safe preflight with only non-secret prerequisite categories;
3. passes `make quality` for that SHA before image build/publish, Terraform, or deployment begins;
4. resolves the published image to an immutable digest and records safe evidence linking the SHA and digest; and
5. records the provider revision and pass/fail hosted verification result.

The former Cloud Build configuration is archived and deprecated. Its triggers
must remain disabled unless a future, explicitly approved deployment design
replaces this workflow.

For a controlled negative run, introduce a quality/preflight/provenance failure in an isolated non-production exercise. Confirm the workflow stops before the prohibited downstream stage and reports a safe category rather than a credential value.

## 5. Review evidence

The implementation review must include:

- passing `make lint`, `make typecheck`, `make quality`, and final `python -m pytest` evidence;
- workflow/contract test evidence for the three PR checks and deploy ordering;
- an administrator's read-only confirmation of the active `main` policy;
- one normal PR and controlled blocked-check observations for the newest revision; and
- a clean-checkout local exercise plus non-production release evidence associating source SHA, image digest, deployment revision, and verification result without secrets.
