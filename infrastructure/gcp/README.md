# GCP Infrastructure Foundation

This directory provisions the hosted MCP platform foundation for FND-019.

## What this provisions

- Cloud Run service foundation for `youtube-mcp-server`
- Runtime service account used by the hosted service
- Secret Manager integration points for `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN`
- Redis-compatible shared session backend for hosted session durability
- Outputs that feed the existing `scripts/deploy_cloud_run.sh` workflow

## Required inputs

Copy [`terraform.tfvars.example`](./terraform.tfvars.example) to a local, untracked `.tfvars` file and supply:

- `project_id`
- `region`
- `environment`
- `service_name`
- `service_account_name`
- `min_instances`
- `max_instances`
- `concurrency`
- `timeout_seconds`
- `mcp_auth_required`
- `mcp_allowed_origins`
- `mcp_allow_originless_clients`
- `session_backend`
- `session_durability_required`
- `session_ttl_seconds`
- `session_replay_ttl_seconds`

## Provisioning workflow

1. Initialize Terraform:
   `terraform -chdir=infrastructure/gcp init`
2. Review the plan:
   `terraform -chdir=infrastructure/gcp plan -var-file=staging.tfvars`
3. Apply the changes:
   `terraform -chdir=infrastructure/gcp apply -var-file=staging.tfvars`
4. Export deploy-time outputs:
   `terraform -chdir=infrastructure/gcp output -json > artifacts/gcp-foundation-outputs.json`

## Expected outputs

The apply step exports values that map directly into the deployment workflow:

- `project_id`
- `region`
- `environment`
- `service_name`
- `service_account_email`
- `secret_reference_names`
- `mcp_auth_required`
- `mcp_allowed_origins`
- `mcp_allow_originless_clients`
- `mcp_session_backend`
- `mcp_session_store_url`
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
