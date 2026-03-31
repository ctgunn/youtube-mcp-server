# GCP Infrastructure Foundation

This directory provisions the hosted MCP platform foundation for FND-019 and serves as the primary provider adapter for the shared platform contract defined in FND-020.

## What this directory is for

This directory is the GCP-specific part of the platform.

The application code in `src/` is the MCP server itself. The Terraform in this
directory creates the cloud resources that let that server run in Google Cloud.

In plain terms:

- the app code explains how the MCP server behaves
- this directory explains where that MCP server lives in GCP and what it needs
  around it

If you are trying to understand "how the server works," start with the root
README. If you are trying to understand "what GCP resources are required so the
server can run correctly," this is the right README.

## What this provisions

- Cloud Run service foundation for `youtube-mcp-server`
- Runtime service account used by the hosted service
- Secret Manager integration points for `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN`
- Redis-compatible shared session backend for hosted session durability
- Runtime secret-access bindings for the Cloud Run service account
- Terraform-managed hosted network layer for durable sessions
- Provider-specific session connectivity model for Cloud Run to reach the session backend
- Outputs that feed the existing `scripts/deploy_cloud_run.sh` workflow

This is the provider-specific implementation of the current hosted runtime, identity, secrets, observability handoff, and durable-session capabilities. FND-020 treats this directory as the primary provider adapter rather than as the full platform model.

## Mental model

You can think of the hosted deployment as three layers:

1. Application layer
   The MCP server process that handles `/health`, `/ready`, and `/mcp`.
2. Platform layer
   Cloud Run, the runtime identity, secret injection, and network path to
   shared dependencies.
3. Shared dependency layer
   The durable session backend and secret-backed configuration needed by the
   hosted runtime.

This directory is mostly responsible for layers 2 and 3.

## Required inputs

Copy [`terraform.tfvars.example`](./terraform.tfvars.example) to a local, untracked `.tfvars` file and supply:

- `project_id`
- `region`
- `environment`
- `service_name`
- `service_account_name`
- `public_invocation_intent`
- `secret_access_mode`
- `min_instances`
- `max_instances`
- `concurrency`
- `timeout_seconds`
- `mcp_auth_required`
- `mcp_allowed_origins`
- `mcp_allow_originless_clients`
- `session_backend`
- `session_connectivity_model`
- `managed_network_name`
- `managed_subnet_name`
- `managed_subnet_cidr`
- `managed_vpc_connector_name`
- `managed_vpc_connector_cidr`
- `session_durability_required`
- `session_ttl_seconds`
- `session_replay_ttl_seconds`

These inputs are doing three jobs:

- identifying where the platform should be created
- defining how public and secure the hosted service should be
- defining how the hosted runtime reaches secrets and durable session state

## Provisioning workflow

1. Initialize Terraform:
   `terraform -chdir=infrastructure/gcp init`
2. Review the plan:
   `terraform -chdir=infrastructure/gcp plan -var-file=staging.tfvars`
3. Apply the changes:
   `terraform -chdir=infrastructure/gcp apply -var-file=staging.tfvars`
4. Export deploy-time outputs:
   `terraform -chdir=infrastructure/gcp output -json > artifacts/gcp-foundation-outputs.json`

This workflow creates the infrastructure foundation first. It does not replace
the application deployment step. After Terraform runs, you still deploy the
current application image with `scripts/deploy_cloud_run.sh`.

## Terraform-managed hosted network layer

For durable hosted sessions, the supported GCP path now provisions the managed
network resources directly from Terraform. That managed hosted network layer
includes:

- a managed VPC network for the hosted durable-session path
- a managed subnet for that hosted path
- a Serverless VPC Access connector used by Cloud Run to reach the durable
  session backend
- the authorized network relationship used by the Redis session backend

Operators no longer need to pre-create the supported VPC network, subnet, or
Serverless VPC Access connector manually for this path.

## Expected outputs

The apply step exports values that map directly into the deployment workflow:

- `project_id`
- `region`
- `environment`
- `service_name`
- `service_account_email`
- `public_invocation_intent`
- `secret_reference_names`
- `mcp_secret_access_mode`
- `mcp_secret_reference_names`
- `mcp_auth_required`
- `mcp_allowed_origins`
- `mcp_allow_originless_clients`
- `mcp_session_backend`
- `mcp_session_store_url`
- `mcp_session_connectivity_model`
- `mcp_session_network_reference`
- `mcp_session_subnet_reference`
- `mcp_session_connector_reference`
- `mcp_session_durability_required`
- `mcp_session_ttl_seconds`
- `mcp_session_replay_ttl_seconds`
- `min_instances`
- `max_instances`
- `concurrency`
- `timeout_seconds`

## Deployment handoff

After exporting the Terraform outputs:

```bash
INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json \
IMAGE_REFERENCE=us-docker.pkg.dev/my-gcp-project/apps/youtube-mcp-server:build-20260322-01 \
bash scripts/deploy_cloud_run.sh
```

`IMAGE_REFERENCE` remains an application deployment input and is not produced by Terraform.

The handoff is intentional:

- Terraform creates the GCP foundation and emits the values the app needs
- the deploy script consumes those values and rolls out the MCP server image
- deployment evidence preserves the managed hosted-network references needed for review and verification

## Push-triggered deployment bootstrap

FND-025 adds two checked-in automation entrypoints that share the same
Terraform-to-deploy-to-verify chain:

- `cloudbuild.yaml` for the primary Cloud Build trigger on `main`
- `.github/workflows/hosted-deploy.yml` for a manual GitHub Actions fallback

The Cloud Build trigger should be treated as the primary production path when
you already deploy from GCP. The GitHub Actions fallback exists so maintainers
and open source users can still run the same repository-managed deployment flow
without discarding that work.

Both paths still depend on one-time bootstrap work:

- repository automation needs GCP authentication through workload identity
- repository variables must identify the project, region, service name, image
  repository, and Terraform variable file
- Terraform provisioning remains automation-managed through the versioned
  `infrastructure/gcp/` path
- Secret values remain operator-managed and must already exist for
  `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN`

That boundary is intentional. The workflow may wire references to secrets and
runtime identities, but it must not create or rotate the secret values
themselves.

The managed hosted network layer remains automation-managed for the supported
hosted path. The remaining one-time bootstrap inputs are non-network prerequisites
such as workflow access, Terraform environment inputs, and operator-managed secret
values.

If the push-triggered workflow fails before deploy, inspect bootstrap
prerequisites first. If it fails after deploy, inspect the generated deployment
record and hosted verification artifacts before re-running the workflow.

For operators, the first failure boundary should stay readable:

- `bootstrap_input_failure` means one-time inputs were not ready before
  infrastructure reconciliation started.
- `network_reconcile_failure` means the managed hosted network layer could not
  be reconciled during the recurring automated path.
- this repository does not support recurring manual network provisioning for the
  supported durable-session deployment path.

## Hosted dependency wiring model

- The Cloud Run runtime service account is the runtime identity that reads required secret-backed configuration.
- `secret_access_mode=secret_manager_env` declares that the hosted runtime receives `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN` from Secret Manager-backed environment injection rather than plain-text environment values.
- the Terraform-managed hosted network layer creates the managed VPC network, subnet, and Serverless VPC Access connector used by the durable-session path.
- the exported session connector reference identifies the Cloud Run attachment path used to reach the durable session backend.
- the exported session network reference identifies the managed network that is permitted to reach the Redis session backend.
- `session_connectivity_model=serverless_vpc_connector` is the expected provider-specific connectivity model for durable hosted session support.

If hosted verification reports a secret-access failure, review the runtime service account bindings and secret reference names first. If it reports a session-connectivity failure, review the exported session connector reference, session network reference, and Redis backend path first.

This wiring matters because the server can look correct in code but still fail
at runtime if:

- Cloud Run cannot read the secrets it expects
- Cloud Run cannot reach the Redis-backed session store
- the session durability mode says shared state is required but the platform is
  not actually providing it

## Public invocation intent

- Set `public_invocation_intent=public_remote_mcp` when the environment is intended for trusted public remote MCP consumers.
- Set `public_invocation_intent=private_only` when the environment should remain outside the public remote MCP workflow.
- Public invocation intent does not replace MCP bearer-token authentication; it only controls whether the hosted Cloud Run service is intentionally reachable.

This is a common point of confusion, so it is worth stating directly:

- public invocation answers "can a remote MCP client reach the Cloud Run URL at all?"
- MCP bearer auth answers "once the request reaches `/mcp`, is the caller allowed to use it?"

Those are separate layers and both need to be configured correctly.
