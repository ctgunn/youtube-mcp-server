# Quickstart: Automated Hosted Deployment Orchestration

## 1. Preserve the Local Development Path

Use this path when you are changing application behavior but are not preparing a hosted rollout.

1. Run the existing local developer workflow.
2. Use repository tests and local verification before touching hosted deployment automation.

Expected outcome: local development and verification remain supported without requiring a push to the deployment branch.

## 2. Complete One-Time Hosted Bootstrap

Use this path before relying on push-triggered hosted deployment for the first time.

1. Prepare the intended deployment branch for hosted rollout automation.
2. Prepare the hosted cloud access and image-publication prerequisites for the target environment.
3. Provision the hosted infrastructure foundation through the versioned infrastructure path.
4. Populate the required secret values through the operator-managed secret process.
5. Confirm the hosted environment is ready to run the repository deployment and verification path.

Expected outcome: the target environment has the prerequisites needed for infrastructure reconciliation, application rollout, and hosted verification.

## 3. Validate the Manual Deployment Chain Before Automating It

Use this path to confirm the repository deployment chain works end to end before depending on push-triggered automation.

1. Reconcile infrastructure and export deployment-ready outputs.
2. Deploy the current application revision through `scripts/deploy_cloud_run.sh`.
3. Save the deployment record emitted by the deploy stage.
4. Run `scripts/verify_cloud_run_foundation.py` against that deployment record.

Expected outcome: operators confirm the repository deploy-and-verify chain works for the target environment before the workflow automates it.

## 4. Trigger Push-Driven Hosted Deployment

Use this path once bootstrap is complete and the manual chain is proven.

1. Commit the desired infrastructure and application changes.
2. Push the revision to the intended deployment branch (`main`) so the existing Cloud Build trigger runs `cloudbuild.yaml`.
3. Observe one Cloud Build deployment run for that pushed revision.
4. Review the generated artifacts for `artifacts/gcp-foundation-outputs.json`, `artifacts/cloud-run-deployment.json`, `artifacts/cloud-run-verification.json`, and `artifacts/cloud-run-verification.txt`.

Expected outcome: one repository-managed workflow reconciles infrastructure, deploys the current revision, verifies the hosted endpoint, and reports success only if the verification gate passes.

## 5. Run the GitHub Actions Fallback

Use this path when Cloud Build is unavailable or when an open source operator
prefers GitHub-hosted automation.

1. Open the `hosted-deploy` workflow in GitHub Actions.
2. Trigger `workflow_dispatch` manually.
3. Provide the target ref and environment inputs if you need something other than the defaults.
4. Review the uploaded fallback artifacts after the run completes.

Expected outcome: the fallback workflow runs the same repository-managed
Terraform-to-deploy-to-verify path without taking ownership of automatic `main`
push deployment.

## 6. Diagnose a Failed Deployment Run

Use this path when the workflow fails and you need to determine the blocking stage quickly.

1. Inspect the workflow result and identify the first failing stage.
2. If infrastructure reconciliation failed, correct the hosted platform inputs or bootstrap prerequisites.
3. If deployment failed, inspect the repository deployment record and its failure stage.
4. If hosted verification failed, inspect the verification evidence to determine whether the failure is reachability, secret access, session connectivity, or another hosted MCP contract issue.

Expected outcome: operators can correct the blocking issue without guessing whether the problem came from infrastructure, rollout, or hosted verification.
