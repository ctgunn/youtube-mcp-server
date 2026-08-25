# Engineering workflow

This guide defines the quality, pull-request, and runtime-configuration rules
for repository contributors.

## Quality gate

Install the declared development tooling from a clean checkout:

```bash
python -m pip install -e '.[dev]'
```

The canonical checks are:

```bash
make lint
make typecheck
make test
make quality
```

`make quality` runs linting, static type checking, and the full test suite.
Run it before opening a pull request and before any break-glass deployment.
The release workflow runs the same command against the resolved source revision.

## Pull-request quality gate

`.github/workflows/quality.yml` runs for pull requests targeting `main` and
reports three stable GitHub Actions checks:

- `lint`
- `typecheck`
- `tests`

Repository administrators must enforce those exact checks through an active
ruleset or branch-protection rule for `main`, require pull requests, and require
the branch to be up to date. Do not use path filters or skipped jobs for these
required checks: a cancelled, missing, skipped, or pending quality result must
never authorize a merge or deployment.

Verify the policy with a normal pull request and controlled lint, typecheck,
and test failures. After every update, confirm the newest revision is blocked
until all three checks pass.

## Runtime and security configuration

Use `.env.local` for private local configuration and Secret Manager-backed
values for hosted deployment. The runtime recognizes configuration for:

- YouTube API access and optional OAuth use
- MCP authentication and allowed browser origins
- in-memory versus Redis-backed session storage
- session durability, replay retention, and connectivity model
- logging, readiness, and deployment-output handoff

For a public remote MCP service, `PUBLIC_INVOCATION_INTENT=public_remote_mcp`
is the normal starting point. `MCP_ALLOWED_ORIGINS` controls browser access;
configure explicit trusted origins rather than broadly allowing arbitrary
browser sites.

Never commit application secrets, service-account keys, `.env.local`, or
Terraform state. Hosted releases use workload identity federation and Secret
Manager rather than long-lived credentials in the repository.

## Python documentation standard

Every new or modified Python function must have a complete reStructuredText
docstring. Keep the docstring aligned with observable behavior, parameters,
return values, side effects, and raised exceptions.
