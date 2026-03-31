# Quickstart: Terraform-Managed Hosted Networking for Durable Sessions

## 1. Preserve the Minimal Local Runtime

Use this path when you only need the default developer workflow.

1. Run the MCP server through the normal local development path.
2. Verify local behavior without any hosted GCP infrastructure provisioning.
3. Treat this path as separate from durable hosted networking.

Expected outcome: local development remains available without Cloud Run network setup.

## 2. Preserve Hosted-Like Local Verification as a Separate Path

Use this path when you need local Redis-backed session behavior but do not need provider-specific hosted networking.

1. Start the hosted-like local dependency path from `infrastructure/local/`.
2. Run the application locally with the hosted-like local settings.
3. Verify session-oriented behavior locally without treating it as proof of the hosted GCP network path.

Expected outcome: hosted-like local verification remains useful for application behavior while staying separate from hosted GCP networking evidence.

## 3. Provision the Managed Hosted Network Layer for GCP

Use this path when the target environment is intended to support durable hosted sessions on Cloud Run.

1. Prepare the hosted GCP environment inputs for the supported deployment profile.
2. Run the Terraform provisioning path from `infrastructure/gcp/`.
3. Confirm the managed hosted network layer is included in the reviewed infrastructure outputs.
4. Export the infrastructure outputs that will feed the deployment and hosted verification workflow.

Expected outcome: the supported GCP path produces reviewable evidence that the durable-session network layer is Terraform-managed rather than manually pre-created.

## 4. Deploy the Hosted Revision Through the Existing Handoff

Use this path after the managed network layer has been provisioned.

1. Supply the exported infrastructure outputs to `scripts/deploy_cloud_run.sh`.
2. Deploy the hosted revision through the existing repository rollout path.
3. Save the emitted deployment record for later verification.

Expected outcome: operators have one deployment record that preserves the durable-session connectivity model and the managed networking handoff evidence.

## 5. Verify the Managed Networking Path

Use this path to prove the hosted GCP environment is ready for durable sessions.

1. Run the hosted verification workflow against the deployment record.
2. Confirm the deployment evidence includes the managed hosted-networking handoff.
3. Confirm the hosted runtime reports readiness for durable session support.
4. Confirm at least one durable hosted session flow succeeds after the managed network layer is in place.

Expected outcome: operators have reviewable proof that the durable-session network path is both provisioned and usable through the supported GCP deployment chain.

## 6. Diagnose a Managed-Networking Failure

Use this path when the hosted environment cannot claim durable session readiness.

1. Review the Terraform evidence for the managed hosted-network layer.
2. Confirm the exported networking outputs are complete before deployment begins.
3. Check the deployment record and hosted verification evidence for the first failure layer.
4. Follow the runbook guidance for missing network provisioning, incomplete handoff evidence, or hosted connectivity failure.

Expected outcome: operators can identify whether the failure is in Terraform-managed network provisioning, deployment handoff, or later hosted connectivity validation without guessing about undocumented prerequisites.
