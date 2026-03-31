# Contract: Hosted Network Bootstrap Pipeline

## Purpose

Define the required behavior of the repository-managed hosted deployment chain when the target environment depends on the managed hosted network layer.

## Actors

- Operator relying on the automatic hosted pipeline to reconcile infrastructure before rollout
- Maintainer reviewing deployment automation and infrastructure handoff behavior
- Workflow runner executing the ordered hosted deployment stages

## Ordered Stages

The hosted deployment chain must preserve these stages in order:

1. `quality_gate`
2. `image_publish`
3. `infrastructure_reconcile`
4. `terraform_output_export`
5. `deploy`
6. `hosted_verification`

## Network Bootstrap Contract

- `cloudbuild.yaml` is the primary automatic pipeline for the hosted deployment path.
- `.github/workflows/hosted-deploy.yml` is a manual fallback and must preserve the same Terraform-to-deploy-to-verify ordering.
- The `infrastructure_reconcile` stage must include reconciliation of the managed hosted network layer for environments that require durable hosted session connectivity.
- The `deploy` stage must not begin until `infrastructure_reconcile` and `terraform_output_export` both complete successfully.
- `scripts/deploy_cloud_run.sh` remains the canonical deployment entrypoint after infrastructure reconciliation.
- `scripts/verify_cloud_run_foundation.py` remains the canonical hosted verification entrypoint after deploy.

## Required Inputs

- primary automatic pipeline definition
- fallback workflow definition
- infrastructure reconciliation inputs for the target environment
- deployable image reference for the target revision
- exported Terraform outputs consumed by the deploy stage

## Workflow Guarantees

- Managed hosted networking is part of the reviewed rollout path, not an implied prerequisite outside the pipeline.
- Terraform outputs remain the canonical handoff between infrastructure reconciliation and application deployment.
- Deployment success cannot be reported unless the managed network bootstrap responsibilities for the target environment have completed successfully.
- The fallback workflow must not bypass the same repository-managed infrastructure handoff, deploy path, or verification path used by the primary automatic pipeline.

## Failure Contract

- If deployment begins before `infrastructure_reconcile` and `terraform_output_export` succeed, the contract is violated.
- If the pipeline treats managed hosted networking as an undocumented prerequisite outside the rollout path, the contract is violated.
- If either automation surface bypasses `scripts/deploy_cloud_run.sh` or `scripts/verify_cloud_run_foundation.py`, the contract is violated.
- If a successful run cannot show that managed network reconciliation occurred before deploy for the targeted hosted path, the contract is violated.
