# Contract: Deployment Bootstrap Boundary

## Purpose

Define the one-time prerequisites and responsibility boundary that must exist before push-triggered hosted deployment can run safely.

## Actors

- Operator preparing the hosted environment and repository automation
- Maintainer documenting and reviewing deployment prerequisites
- Workflow runner consuming prepared prerequisites during deployment
- Cloud Build trigger consuming `cloudbuild.yaml` as the primary automatic deployment path
- GitHub Actions operator using `.github/workflows/hosted-deploy.yml` as a manual fallback

## Bootstrap Prerequisites

The documented bootstrap set must identify, at minimum:

1. repository automation prerequisites
   - the intended deployment branch
   - workflow permissions and artifact destinations needed by automation
2. cloud access prerequisites
   - access needed to reconcile infrastructure and deploy the hosted runtime
   - access needed to publish the deployable image
3. secret population prerequisites
   - required secret references for the target environment, including `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN`
   - confirmation that required secret values are populated outside the workflow
4. hosted verification prerequisites
   - the hosted environment is prepared to run the repository verification flow after rollout

## Responsibility Boundary

### Automation-managed responsibilities

- reconcile versioned infrastructure
- export infrastructure outputs for deployment handoff
- deploy the current application revision through the repository deployment path
- run hosted verification and publish reviewable artifacts
- report stage-specific failures

### Operator-managed responsibilities

- prepare one-time repository and cloud bootstrap prerequisites
- populate and rotate required secret values
- approve or supply environment-specific inputs not owned by the workflow
- remediate failed bootstrap conditions before re-running deployment

## Secret Boundary Rules

- Automation may reference secret names, secret references, and secret access mode.
- Automation must never create committed secret values, print secret contents, or store secret values in workflow artifacts.
- Missing or inaccessible secret values must surface as workflow failures rather than implicit assumptions.

## Failure Interpretation

- Missing bootstrap prerequisites must fail before hosted deployment is reported successful.
- Missing secret references and missing secret values must remain distinct from general deployment errors when surfaced by repository tooling.
- Secret-access failures, session-connectivity failures, and hosted MCP verification failures must remain reviewable as separate failure classes.

## Workflow Guarantees

- A first-time operator can identify which prerequisites must be completed before push-triggered deployment is expected to pass.
- Reviewers can distinguish infrastructure-managed secret wiring from operator-managed secret value population.
- A successful deployment run implies that bootstrap prerequisites were satisfied well enough for infrastructure reconciliation, rollout, and hosted verification to complete.

## Failure Contract

- If prerequisite documentation does not identify one-time setup requirements, the contract is incomplete.
- If automation implies ownership of secret contents instead of secret wiring, the contract is violated.
- If a workflow run succeeds while required bootstrap conditions remain unmet, the contract is violated.
