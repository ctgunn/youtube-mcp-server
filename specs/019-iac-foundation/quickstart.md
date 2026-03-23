# Quickstart: Infrastructure as Code Foundation

## 1. Minimal Local Runtime

Use this path when you only need the default local developer workflow and do not need durable hosted-session behavior.

1. Install dependencies:
   `python3 -m pip install -e .`
2. Export only the minimum local environment values:
   `MCP_ENVIRONMENT=dev`
3. Run the service using the existing local entrypoint.
4. Verify basic local behavior without starting any infrastructure under `infrastructure/`.

Expected outcome: the service runs with the default in-memory session mode and no cloud provisioning prerequisite.

## 2. Hosted-Like Local Verification

Use this path when you need to exercise durable-session behavior locally without provisioning cloud infrastructure.

1. Start the local shared-state dependency stack from `infrastructure/local/`.
   `docker compose -f infrastructure/local/compose.yaml up -d`
2. Export hosted-like local values:
   - `MCP_ENVIRONMENT=dev`
   - `MCP_SESSION_BACKEND=redis`
   - `MCP_SESSION_STORE_URL=<local redis url>`
   - `MCP_SESSION_DURABILITY_REQUIRED=true`
3. Run the application locally.
4. Run the hosted verification workflow against the local endpoint using the same session-oriented checks used for Cloud Run.
5. Stop the local dependency stack after verification.

Expected outcome: developers can reproduce the durable-session path locally while keeping it distinct from the default local workflow.

## 3. GCP Infrastructure Provisioning

Use this path to create the hosted MCP platform from versioned infrastructure definitions.

1. Initialize the GCP infrastructure workspace under `infrastructure/gcp/`.
   `terraform -chdir=infrastructure/gcp init`
2. Supply the required environment-specific inputs for the target environment.
3. Run the infrastructure planning step and review the proposed Cloud Run, secret integration, and Redis-compatible session resources.
   `terraform -chdir=infrastructure/gcp plan -var-file=staging.tfvars`
4. Apply the infrastructure changes.
   `terraform -chdir=infrastructure/gcp apply -var-file=staging.tfvars`
5. Capture the resulting deployment handoff values.
   `terraform -chdir=infrastructure/gcp output -json > artifacts/gcp-foundation-outputs.json`

Expected outcome: the hosted runtime prerequisites exist before application deployment, and the resulting outputs match the contract in `contracts/gcp-hosted-foundation-contract.md`.

## 4. Hosted Application Deployment

Use this path after infrastructure provisioning.

1. Provide the deployment inputs required by `scripts/deploy_cloud_run.sh`, using the values produced by infrastructure provisioning plus the target `IMAGE_REFERENCE`.
2. Execute:
   `INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json IMAGE_REFERENCE=<image> bash scripts/deploy_cloud_run.sh`
3. Save the JSON deployment record emitted by the script.

Expected outcome: the application is deployed without modifying source files and produces a reusable deployment record for verification.

## 5. Hosted Verification

Use this path after a hosted deployment has completed.

1. Run:
   `PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py --deployment-record <deployment-record> --auth-token <token> --evidence-file <path>`
2. Review the generated evidence for health, readiness, MCP initialization, tool listing, retrieval-tool calls, and session continuation checks.

Expected outcome: the hosted deployment proves liveness, readiness, security, retrieval, and session continuity behavior using the provisioned infrastructure and deployment outputs.
