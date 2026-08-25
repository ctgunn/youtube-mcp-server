# Contract: Hosted Deployment Pipeline

## Purpose

Define the required behavior of the manually dispatched GitHub Actions
deployment automation that deploys the hosted MCP service.

## Actors

- Operator relying on the repository to deploy the hosted service
- Maintainer reviewing deployment automation changes in version control
- Workflow runner executing the deployment stages for an explicitly selected revision

## Trigger Contract

- `.github/workflows/hosted-deploy.yml` is the supported deployment workflow and
  is explicitly dispatched by an authorized operator.
- The workflow resolves the actual checked-out revision selected by the
  operator; it must not automatically deploy `main` pushes by default.
- `docs/archive/cloudbuild.yaml` is deprecated and its disabled Cloud Build
  triggers must not be treated as a second deployment owner.

## Ordered Stages

The workflow must execute these stages in order:

1. `quality_gate`
   - Runs repository checks required before hosted rollout.
   - Must fail the workflow before build or deploy begins if required checks fail.
2. `image_publish`
   - Produces the deployable application image reference for the pushed revision.
   - Must publish or resolve the image reference needed by the deploy script.
3. `infrastructure_reconcile`
   - Reconciles hosted infrastructure through the versioned infrastructure path.
   - Must produce or refresh deployment-ready infrastructure outputs.
4. `terraform_output_export`
   - Exports the infrastructure outputs consumed by the deploy script.
   - Must complete before the deploy stage starts.
5. `deploy`
   - Calls the repository deployment path through `scripts/deploy_cloud_run.sh`.
   - Must use infrastructure outputs and the current image reference.
   - Must emit a structured deployment record.
6. `hosted_verification`
   - Calls the repository verification path through `scripts/verify_cloud_run_foundation.py`.
   - Must consume the deployment record.
   - Must fail the workflow if hosted verification fails.

## Required Inputs

- intended deployment revision
- deployable image reference for the resolved revision
- infrastructure reconciliation inputs for the target environment
- operator-managed secret values already populated in the target environment
- repository access needed to publish workflow artifacts

## Required Outputs

- one deployment workflow result for the resolved revision
- one infrastructure-output artifact for the deploy stage
- one deployment record artifact emitted by the deploy stage
- one hosted verification evidence artifact emitted by the verification stage

## Failure Gates

- The workflow must fail if required repository quality gates fail.
- The workflow must fail if infrastructure reconciliation or output export fails.
- The workflow must fail if the repository deployment path reports `failed` or `incomplete`.
- The workflow must fail if hosted verification reports `fail`.
- The workflow must report the failing stage in operator-readable form.

## Workflow Guarantees

- Infrastructure reconciliation is always completed before application rollout is treated as valid.
- Application rollout always uses the repository deployment path rather than a direct image-only runtime update.
- Hosted deployment is never reported successful without a passing hosted verification result.
- Deployment artifacts remain reviewable from repository automation outputs.

## Failure Contract

- If the deploy stage bypasses Terraform-output handoff or the repository deploy script, the contract is violated.
- If the workflow reports success without hosted verification evidence, the contract is violated.
- If a hosted deployment runs without explicit operator intent, the contract is violated.
- If artifacts are missing or unusable after a reported successful run, the workflow result is incomplete.
