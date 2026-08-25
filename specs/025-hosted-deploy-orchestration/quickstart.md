# Quickstart: Hosted Deployment Orchestration

## 1. Preserve the Local Development Path

Use this path when you are changing application behavior but are not preparing a hosted rollout.

1. Run the existing local developer workflow.
2. Use repository tests and local verification before touching hosted deployment automation.

Expected outcome: local development and verification remain supported without a hosted deployment release.

## 2. Complete One-Time Hosted Bootstrap

Use this path before relying on the hosted release workflow for the first time.

1. Configure the repository variables, secrets, and GitHub Actions workload identity described in the root README.
2. Prepare the hosted cloud access and image-publication prerequisites for the target environment.
3. Provision the hosted infrastructure foundation through the versioned infrastructure path.
4. Populate the required secret values through the operator-managed secret process.
5. Confirm the hosted environment is ready to run the repository deployment and verification path.

Expected outcome: the target environment has the prerequisites needed for infrastructure reconciliation, application rollout, and hosted verification.

## 3. Validate the Repository Deployment Chain

Use this path to confirm that the repository deployment chain and hosted
verification remain understood before dispatching a release.

1. Reconcile infrastructure and export deployment-ready outputs.
2. Deploy the current application revision through `scripts/deploy_cloud_run.sh`.
3. Save the deployment record emitted by the deploy stage.
4. Run `scripts/verify_cloud_run_foundation.py` against that deployment record.

Expected outcome: operators understand the Terraform-to-deploy-to-verify chain
that the workflow executes.

## 4. Run the Hosted Deployment Workflow

Use this path once bootstrap is complete.

1. Merge the reviewed revision to `main`.
2. Open **Actions** → **hosted-deploy** → **Run workflow**.
3. Select `main` for the workflow source and `target_ref`, plus `staging` for the target environment unless an approved alternative revision is intended.
4. Review the generated artifacts for `artifacts/gcp-foundation-outputs.json`, `artifacts/cloud-run-deployment.json`, `artifacts/cloud-run-verification.json`, and `artifacts/cloud-run-verification.txt`.

Expected outcome: one repository-managed workflow reconciles infrastructure, deploys the current revision, verifies the hosted endpoint, and reports success only if the verification gate passes.

The former Cloud Build file is archived in `docs/archive/cloudbuild.yaml`; its
triggers are disabled and it is not a supported release route.

## 5. Diagnose a Failed Deployment Run

Use this path when the workflow fails and you need to determine the blocking stage quickly.

1. Inspect the workflow result and identify the first failing stage.
2. If infrastructure reconciliation failed, correct the hosted platform inputs or bootstrap prerequisites.
3. If deployment failed, inspect the repository deployment record and its failure stage.
4. If hosted verification failed, inspect the verification evidence to determine whether the failure is reachability, secret access, session connectivity, or another hosted MCP contract issue.

Expected outcome: operators can correct the blocking issue without guessing whether the problem came from infrastructure, rollout, or hosted verification.
