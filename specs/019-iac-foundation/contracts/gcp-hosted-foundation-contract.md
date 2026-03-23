# Contract: GCP Hosted Foundation

## Purpose

Define the operator-facing contract for provisioning the hosted MCP platform on GCP and handing off the resulting inputs to the existing application deployment workflow.

## Actors

- Operator provisioning the hosted platform
- Maintainer deploying the application revision
- Reviewer validating infrastructure changes alongside application changes

## Provisioning Inputs

- `project_id`
- `region`
- `environment`
- `service_name`
- `service_account_name` or pre-approved runtime identity input
- Hosted scaling settings:
  - `min_instances`
  - `max_instances`
  - `concurrency`
  - `timeout_seconds`
- Secret integration declarations for:
  - `YOUTUBE_API_KEY` in `staging` and `prod`
  - `MCP_AUTH_TOKEN` in `staging` and `prod`
- Hosted security configuration inputs:
  - `mcp_auth_required`
  - `mcp_allowed_origins`
  - `mcp_allow_originless_clients`
- Durable session inputs:
  - backend type `redis`
  - session TTL
  - replay TTL

## Managed Resource Coverage

The GCP infrastructure foundation must provision or declare, in versioned code, the hosted dependencies required for the MCP service:

- Cloud Run service foundation
- Runtime identity for the hosted service
- Secret integration points used by deployment/runtime configuration
- Redis-compatible durable session backend required for hosted session continuity
- Output values needed by the application deployment workflow

## Required Outputs

The provisioning workflow must produce or document how to obtain these deploy-time values without additional undocumented console steps:

- `PROJECT_ID`
- `REGION`
- `SERVICE_NAME`
- `SERVICE_ACCOUNT_EMAIL`
- `MCP_ENVIRONMENT`
- `MCP_AUTH_REQUIRED`
- `MCP_ALLOWED_ORIGINS`
- `MCP_ALLOW_ORIGINLESS_CLIENTS`
- `MCP_SESSION_BACKEND=redis`
- `MCP_SESSION_STORE_URL` or a secret-backed reference for it
- `MCP_SESSION_DURABILITY_REQUIRED`
- `MIN_INSTANCES`
- `MAX_INSTANCES`
- `CONCURRENCY`
- `TIMEOUT_SECONDS`
- Secret reference names for deployment

`IMAGE_REFERENCE` remains an application deployment input and is not created by infrastructure provisioning.

## Workflow Guarantees

- Provisioning must be reproducible from repository assets and documented inputs.
- Deployment must be executable after provisioning without editing application source files.
- Missing required inputs must fail fast with operator-facing guidance.
- Secret values must never be emitted in plaintext outputs committed to the repository.

## Failure Contract

- If required environment inputs are missing, validation must stop before partial deployment.
- If secret integration is not configured for `staging` or `prod`, the deployment handoff is invalid.
- If the durable session backend is unavailable, the hosted deployment path may exist but the hosted verification path must fail clearly.

## Verification Evidence

Successful use of this contract produces:

- A recorded infrastructure apply or plan result
- A deployment record emitted by `scripts/deploy_cloud_run.sh`
- Hosted verification evidence emitted by `scripts/verify_cloud_run_foundation.py`
