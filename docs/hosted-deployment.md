# Hosted deployment

The supported hosted release path is the manually dispatched GitHub Actions
workflow at `.github/workflows/hosted-deploy.yml`. It deploys the GCP provider
adapter: Cloud Run, Secret Manager integration, Redis-backed durable sessions,
and Terraform-managed networking.

For Terraform inputs, resource topology, recovery commands, and provider
details, use the [GCP infrastructure README](../infrastructure/gcp/README.md).

## One-time bootstrap prerequisites

Before the first deployment, an operator must create or configure:

1. A GCP project with the required APIs enabled.
2. A private, versioned GCS bucket for Terraform state.
3. A regional Artifact Registry Docker repository.
4. A GitHub OIDC Workload Identity Provider restricted to the repository, plus
   a deployer service account that the provider may impersonate.
5. Least-privilege service-account access for Artifact Registry, Terraform
   state, infrastructure reconciliation, Cloud Run, and Secret Manager access
   bindings.
6. Secret Manager values for `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN`.
7. A reviewed, secret-free `infrastructure/gcp/staging.tfvars` file that names
   the GCP project, service, browser origin, and managed network resources.

The one-time bootstrap inputs remain outside the recurring automated deployment
run. The workflow can wire secret references and provision the managed network
bootstrap, but it never creates or prints secret values.

## GitHub configuration

In **Settings** → **Secrets and variables** → **Actions**, configure these
repository variables:

- `GCP_PROJECT_ID`
- `GCP_REGION`
- `GCP_SERVICE_NAME`
- `GCP_ARTIFACT_REGISTRY_REPOSITORY`
- `GCP_TERRAFORM_VAR_FILE`
- `GCP_TERRAFORM_STATE_BUCKET`

Configure these repository secrets:

- `GCP_WORKLOAD_IDENTITY_PROVIDER`
- `GCP_DEPLOYER_SERVICE_ACCOUNT`

The GitHub secrets identify the federated deployer only. Application secrets
remain in Secret Manager. Do not add API keys, runtime tokens, or
service-account key files to GitHub variables, source control, artifacts, or
release evidence.

## Release procedure

1. Confirm `make quality` passes on the revision you intend to release.
2. In GitHub, open **Actions** → **hosted-deploy** → **Run workflow**.
3. Select `main` as the workflow source and `target_ref` unless releasing a
   specifically reviewed commit. Use `staging` for the current environment.
4. Wait for the full workflow. It resolves the full commit SHA, runs safe preflight,
   runs `make quality`, publishes an immutable image digest,
   reconciles Terraform, deploys Cloud Run, and performs hosted verification.
5. Download `hosted-deploy-<source-sha>` and retain its evidence.

The evidence includes the resolved commit, immutable image reference,
Terraform outputs, deployment record, and verification result. It must never
include secret values.

## Failure boundaries

- `bootstrap_input_failure`: a one-time prerequisite is missing before release
  work begins.
- `network_reconcile_failure`: managed network bootstrap failed during
  Terraform reconciliation.
- Any later failure occurs only after the earlier quality and preflight gates
  have passed; inspect the deployment record and verification evidence before
  retrying.

The network reconciliation happens before deploy. The managed network bootstrap
provisions the hosted VPC, Direct VPC egress subnet, and Redis connectivity
required for durable sessions; operators should not make recurring manual
network changes for normal releases.

## Break-glass recovery

Use direct Terraform or deployment scripts only when the GitHub workflow is
unavailable and an authorized operator is performing recovery. Run `make
quality`, deploy an immutable `IMAGE@sha256:...` reference, and retain:

- `artifacts/cloud-run-deployment.json`
- `artifacts/cloud-run-verification.json`
- `artifacts/cloud-run-verification.txt`

The former Cloud Build configuration is archived at
[`docs/archive/cloudbuild.yaml`](./archive/cloudbuild.yaml). It is deprecated;
do not create or re-enable a Cloud Build trigger from it.
