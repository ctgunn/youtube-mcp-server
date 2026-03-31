# Quickstart: Automated Hosted Network Bootstrap Reconciliation

## 1. Preserve the Minimal Local Runtime

Use this path when you only need the standard local development workflow.

1. Run the MCP server through the normal local development path.
2. Verify local behavior without any hosted deployment automation.
3. Treat local execution as separate from hosted network bootstrap requirements.

Expected outcome: local development remains available without any hosted bootstrap or cloud deployment setup.

## 2. Prepare the One-Time Hosted Bootstrap Inputs

Use this path when you are preparing a hosted environment for automated deployment.

1. Confirm the primary automatic pipeline and manual fallback are both configured for the target environment.
2. Prepare the repository and cloud access prerequisites required by automation.
3. Provide the environment-specific Terraform variable file used by the hosted environment.
4. Confirm required operator-managed secret values already exist for the target environment.

Expected outcome: the remaining external prerequisites are explicit and limited to one-time setup rather than recurring hosted network provisioning.

## 3. Validate the Automatic Hosted Deployment Chain

Use this path when you want to confirm the automatic hosted pipeline still reflects the reviewed deployment contract.

1. Review `cloudbuild.yaml` as the primary push-triggered pipeline.
2. Confirm the stage order still includes quality gates, image publish, infrastructure reconcile, Terraform output export, deploy, and hosted verification.
3. Confirm the fallback workflow under `.github/workflows/hosted-deploy.yml` preserves the same repository-managed handoff.

Expected outcome: the reviewed automation surfaces show one consistent Terraform-to-deploy-to-verify chain.

## 4. Run the Hosted Deployment Path

Use this path when the target hosted environment is ready for automated rollout.

1. Trigger the primary automatic pipeline through the supported revision flow.
2. Confirm the infrastructure reconciliation stage completes before deploy starts.
3. Confirm Terraform outputs are exported and passed into the deploy step.
4. Confirm the deploy step emits a deployment record and hosted verification runs afterward.

Expected outcome: the hosted rollout executes network bootstrap, deployment, and verification in one reviewed pipeline without a separate recurring manual network setup step.

## 5. Interpret Failure by Boundary

Use this path when a hosted deployment run does not succeed.

1. If the run fails before infrastructure reconciliation starts, inspect missing bootstrap inputs first.
2. If the run fails during infrastructure reconciliation, treat it as a managed network bootstrap failure for environments that require the hosted network path.
3. If the run fails after deploy starts, inspect the deployment record for deploy-stage issues.
4. If the run fails after deploy completes, inspect hosted verification evidence for readiness, session-connectivity, or MCP behavior failures.

Expected outcome: operators can identify whether remediation belongs to bootstrap setup, managed network reconciliation, application rollout, or hosted verification without guessing.

## 6. Confirm the Hosted Automation Boundary

Use this path when reviewing or updating documentation for the supported hosted environment.

1. Verify the documentation treats managed hosted networking as part of the recurring automated pipeline.
2. Verify remaining external prerequisites are limited to repository/cloud access setup, Terraform environment inputs, and operator-managed secret values.
3. Verify the local development workflow is still documented separately from hosted deployment automation.

Expected outcome: the supported hosted path is reviewable, reproducible, and clearly bounded from both local development and one-time external setup.
