# Quickstart: Cloud Run Public Reachability for Remote MCP

## 1. Preserve the Minimal Local Runtime

Use this path when you only need the default local developer workflow.

1. Set `MCP_ENVIRONMENT=dev`.
2. Run the service with the default local runtime path.
3. Verify local behavior without provisioning Cloud Run or exposing any public endpoint.

Expected outcome: the local workflow remains available without any public hosted infrastructure requirement.

## 2. Prepare a Hosted Environment Intended for Public Remote MCP Access

Use this path when the target environment is meant to serve trusted remote MCP consumers.

1. Provision the GCP hosted foundation from `infrastructure/gcp/`.
2. Record the environment as `public_remote_mcp` in the operator workflow or release evidence.
3. Export the deployment handoff values from the GCP provider adapter.
4. Deploy the hosted revision through `scripts/deploy_cloud_run.sh`.
5. Save the emitted deployment record with the hosted connection point.

Expected outcome: operators have a deployment record that identifies the revision, connection point, and intended exposure state for the hosted environment.

## 3. Verify the Successful Public-and-Authenticated Path

Use this path to prove the environment is both reachable and still protected.

1. Run the hosted verification flow against the deployment record.
2. Confirm the service is reachable at the published connection point.
3. Confirm `/health` and `/ready` succeed.
4. Confirm an authenticated MCP request succeeds on `/mcp`.

Expected outcome: the hosted environment is publicly reachable as intended, and the authenticated MCP workflow succeeds afterward.

## 4. Verify the MCP-Layer Denial Path

Use this path to prove public reachability did not weaken bearer-token protection.

1. Re-run the hosted verification flow without valid MCP credentials.
2. Confirm the hosted service remains reachable.
3. Confirm the protected `/mcp` request is denied by the MCP application layer.
4. Review the verification evidence to confirm the denial is classified separately from platform reachability.

Expected outcome: operators can prove the difference between a reachable hosted service and an unauthorized MCP caller.

## 5. Verify the Cloud-Level Denial Interpretation

Use this path when diagnosing an environment that should be public but is not reachable, or when confirming that an environment is intentionally private.

1. Run the hosted verification workflow against the published connection point for the environment under test.
2. Observe the failure before authenticated MCP checks are reported as successful.
3. Confirm the evidence identifies the failure as a cloud-level access or public-invocation problem.
4. Follow the remediation path for Cloud Run reachability rather than bearer-token configuration.

Expected outcome: operators can distinguish a platform-access problem from an MCP authentication problem on the first diagnostic pass.

## 6. Preserve Hosted-Like Local Verification as a Separate Path

Use this path when you need Redis-backed local session verification but do not need public Internet exposure.

1. Start the local dependency path from `infrastructure/local/`.
2. Run the application locally with hosted-like local settings.
3. Verify session-oriented behavior locally without treating that run as proof of public Cloud Run reachability.

Expected outcome: hosted-like local verification remains useful for application behavior and session continuity, but it stays separate from the public-hosted evidence required by FND-021.
