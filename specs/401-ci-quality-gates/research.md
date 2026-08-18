# Research: CI/CD Quality Gates

## Decision 1: Use one canonical quality command with three independent checks

**Decision**: Declare a reproducible development toolchain in the project configuration and expose `make lint`, `make typecheck`, `make test`, and `make quality`. Use `pytest`, Ruff, and mypy; mypy checks `src/mcp_server` as the initial checked-in type-validation boundary. The PR workflow exposes three separate, stable jobs named exactly `lint`, `typecheck`, and `tests`; the two deployment workflows invoke `make quality` before later release stages.

**Rationale**: The repository currently has no declared development dependency set, canonical validation target, or designated type checker. Cloud Build and the manual GitHub workflow independently run only `pytest` and `ruff check .`, which can drift and do not fulfill the seed's type-check requirement. Separate check names satisfy the requirement for distinct outcomes and can be selected precisely by repository governance.

**Alternatives considered**:

- Keep duplicated inline commands in every workflow: rejected because local, PR, and deployment behavior will drift.
- Use a single `quality` status: rejected because it hides which category failed and cannot meet the distinct-outcome requirement.
- Treat compilation as type checking: rejected because it does not provide static type validation.
- Type-check tests and the full repository at strict settings immediately: rejected because no existing baseline/configuration exists and remediating legacy annotations would expand OPS-401 beyond its quality-gate purpose. The scope may be tightened in a future dedicated type-quality slice.

## Decision 2: Enforce PR results with an active `main` ruleset

**Decision**: Add a PR-only GitHub Actions workflow using the unprivileged `pull_request` event for pull requests targeting `main`; it has no path filters, commit-message skip logic, deploy work, or secrets. Document an active repository ruleset for `main` that requires pull requests and the exact GitHub-Actions-sourced `lint`, `typecheck`, and `tests` checks, requires the branch to be up to date, and leaves normal maintainer bypass disabled. A classic branch-protection rule with the same settings is an allowed fallback only when a ruleset is unavailable; both must not be configured with divergent requirements.

**Rationale**: The only checked-in GitHub workflow is currently manual (`workflow_dispatch`), while Cloud Build runs after the externally configured main-branch push. Neither can block a pull request before merge. Required checks are selected by check/job name; exact stable names and a current-head policy prevent green results from a previous revision being treated as sufficient.

**Alternatives considered**:

- Rely on Cloud Build's post-push quality step: rejected because a change is already merged when it runs.
- Rely on documentation alone: rejected because it does not block merges.
- Use `pull_request_target`: rejected because it grants a PR validation workflow unnecessary access to privileged context.
- Configure both branch protection and rulesets: rejected because duplicated policies can drift and confuse the protected flow.

## Decision 3: Make deployment quality and provenance revision-specific

**Decision**: Each deployment workflow resolves its actual checked-out full commit SHA, runs the canonical quality command for that commit before image build/publish or infrastructure/deploy stages, resolves the published image to an immutable digest, and records the commit/digest with existing deployment and verification evidence. A failed, cancelled, missing, or mismatched quality/preflight result stops the workflow before later stages.

**Rationale**: A dispatched ref may move and image tags are mutable. Binding the evaluated commit and immutable image bytes to deployment evidence gives release operators a reviewable chain from source through verification, and extends the existing `quality_gate`-before-deployment convention.

**Alternatives considered**:

- Reuse a tag-only image reference: rejected because tags can be overwritten and do not prove the deployed bytes.
- Use only a full SHA image tag: rejected because it ties source strongly but the tag remains mutable.
- Rely only on repository rulesets: rejected because they do not protect a separately invoked deployment path.

## Decision 4: Keep preflight diagnostics non-secret and operator-readable

**Decision**: Retain a preflight stage before build/deploy that validates non-secret configuration, resolved revision, artifact destination, required secret references/access, and workflow permissions. It reports only missing names or safe categories, never values. Evidence contains category statuses, revision/digest identifiers, stage/order, deployment revision, and verification outcome—not raw secret-bearing environment data or logs.

**Rationale**: The existing deployment workflow already fails early for missing bootstrap prerequisites and preserves an operator-managed secret-value boundary. Making this boundary explicit enables safe remediation without creating, exposing, rotating, or serializing credentials.

**Alternatives considered**:

- Let Terraform or deployment discover missing inputs later: rejected because it produces slower, less precise failures.
- Print environment diagnostics: rejected because it risks secret disclosure.
- Create or rotate secret values automatically: rejected because it violates the existing operator-ownership contract.

## Decision 5: Preserve existing deployment ownership and test it as a contract

**Decision**: Cloud Build remains the primary automatic deployment path for the externally configured main-branch trigger. `.github/workflows/hosted-deploy.yml` remains a manual fallback. Tests treat the Makefile, project tool declaration, PR workflow, Cloud Build configuration, GitHub fallback, contracts, and README as one delivery surface; an authorized administrator verifies the external ruleset with a read-only inspection plus controlled PRs.

**Rationale**: The repository already has tested Cloud Build-to-Terraform-to-deploy-to-verification ordering and a documented GitHub fallback. Extending those flows avoids new deployment paths while acknowledging that GitHub governance is external configuration that source-only tests cannot enforce.

**Alternatives considered**:

- Replace Cloud Build with GitHub Actions: rejected because it changes the established primary deployment owner and broadens the scope.
- Avoid testing workflow/documentation files: rejected because these files are the feature's primary behavioral interface.
- Claim a checked-in workflow alone enforces merge protection: rejected because the active ruleset/protection configuration is outside this repository.
