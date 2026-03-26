# Quickstart: Hosted Dependency Wiring for Secrets and Durable Sessions

## 1. Preserve the Minimal Local Runtime

Use this path when you only need the default local developer workflow.

1. Set `MCP_ENVIRONMENT=dev`.
2. Run the service with the default local runtime path.
3. Verify local behavior without any provider-specific secret or hosted network wiring.

Expected outcome: the minimal local workflow remains available without Cloud Run dependency setup.

## 2. Prepare a Hosted Environment with Runtime Secret Access and Durable Sessions

Use this path when the target environment is intended to support hosted MCP sessions reliably.

1. Provision the GCP hosted foundation from `infrastructure/gcp/`.
2. Confirm the hosted environment records its runtime identity, required secret references, and durable session backend references in reviewable infrastructure outputs.
3. Export the deployment handoff values from the GCP provider adapter.
4. Deploy the hosted revision through `scripts/deploy_cloud_run.sh`.
5. Save the emitted deployment record for hosted verification.

Expected outcome: operators have a deployment record that identifies the hosted revision, runtime identity, secret references, and session backend references needed for verification.

## 3. Verify the Healthy Hosted Dependency Path

Use this path to prove the deployed environment has working dependency wiring.

1. Run the hosted verification flow against the deployment record.
2. Confirm the hosted runtime can access required secret-backed configuration.
3. Confirm `/ready` reports a healthy hosted state.
4. Confirm the hosted runtime can reach the durable session backend.
5. Confirm at least one hosted session continuation flow succeeds.

Expected outcome: operators have reviewable evidence that the hosted deployment is ready for durable session use.

## 4. Verify the Secret-Access Failure Path

Use this path when diagnosing an environment with missing permissions or broken secret references.

1. Run the hosted verification flow against the deployment record for the environment under test.
2. Observe the failure before session-connectivity or continuation success is reported.
3. Confirm the evidence identifies the failure as a secret-access problem.
4. Follow the remediation path for runtime identity or secret-reference wiring.

Expected outcome: operators can distinguish secret-access problems from generic configuration or session failures on the first diagnostic pass.

## 5. Verify the Session-Connectivity Failure Path

Use this path when diagnosing an environment whose durable session backend cannot be reached.

1. Run the hosted verification flow against the deployment record for the environment under test.
2. Confirm the hosted runtime can still evaluate secret access if that path is healthy.
3. Observe the failure before hosted session continuation is reported as successful.
4. Confirm the evidence identifies the failure as a session-connectivity problem.
5. Follow the remediation path for the provider-specific connectivity model.

Expected outcome: operators can distinguish session-backend connectivity failures from secret-access failures on the first diagnostic pass.

## 6. Preserve Hosted-Like Local Verification as a Separate Path

Use this path when you need Redis-backed local session verification but do not need provider-specific Cloud Run dependency wiring.

1. Start the local dependency path from `infrastructure/local/`.
2. Run the application locally with hosted-like local settings.
3. Verify session-oriented behavior locally without treating that run as proof of Cloud Run secret access or Cloud Run-to-backend connectivity.

Expected outcome: hosted-like local verification remains useful for application behavior and session continuity, but it stays separate from the hosted dependency evidence required by FND-022.
