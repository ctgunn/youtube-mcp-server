# Data Model: FND-006 Cloud Run Foundation Deployment

## Entity: DeploymentInputSet
Description: The operator-supplied deployment values and references required to create a hosted revision consistently.

Fields:
- `environment` (string, required): Runtime profile for the revision, constrained to supported deployment profiles.
- `serviceName` (string, required): Hosted service identifier used for deployment and verification targeting.
- `runtimeIdentity` (string, required): Execution identity assigned to the hosted revision.
- `imageReference` (string, required): Versioned deployable artifact reference for the revision.
- `secretReferences` (list, required): Named secret inputs required by the selected environment profile.
- `configValues` (list, required): Non-secret configuration values and build metadata required at startup.
- `minInstances` (integer, required): Lower autoscaling bound for the deployed revision.
- `maxInstances` (integer, required): Upper autoscaling bound for the deployed revision.
- `concurrency` (integer, required): Maximum concurrent requests allowed per instance.
- `timeoutSeconds` (integer, required): Request timeout limit for the hosted revision.

Validation rules:
- All required fields MUST be present before deployment is treated as ready to execute.
- `environment` MUST map to a supported runtime profile.
- `minInstances` MUST be less than or equal to `maxInstances`.
- `concurrency` and `timeoutSeconds` MUST be positive values.
- Required secret references MUST be present for hosted environments that enforce secret-backed startup validation.

## Entity: HostedRevisionRecord
Description: The identity and configuration summary for the revision produced by a deployment run.

Fields:
- `revisionName` (string, required): Unique hosted revision identifier.
- `serviceName` (string, required): Hosted service receiving the revision.
- `deploymentTimestamp` (timestamp, required): Time the revision was created or updated.
- `endpointUrl` (string, required): Stable endpoint used for health and MCP verification.
- `runtimeIdentity` (string, required): Effective execution identity assigned to the revision.
- `scalingSettings` (object, required): Applied min/max instance bounds and concurrency settings.
- `timeoutSeconds` (integer, required): Applied request timeout.
- `status` (string, required): Deployment state used by operators to distinguish created, verified, or failed revisions.

Validation rules:
- A revision cannot move to `verified` status until all required checks pass.
- `endpointUrl` MUST be populated before verification begins.

## Entity: VerificationCheckResult
Description: One post-deploy validation outcome recorded as deployment evidence.

Fields:
- `checkName` (string, required): Named validation step such as liveness, readiness, initialize, list-tools, or baseline-tool-call.
- `endpointUrl` (string, required): Target endpoint used for the check.
- `executedAt` (timestamp, required): Time the verification step was performed.
- `result` (string, required): `pass` or `fail`.
- `statusCode` (integer, optional): Transport-level response code when applicable.
- `summary` (string, required): Human-readable outcome summary for operators.
- `evidenceLocation` (string, optional): Reference to captured output or log artifact.

Validation rules:
- Every required post-deploy check MUST produce exactly one recorded result per verification run.
- Failed checks MUST include a summary that identifies the stage of failure without exposing secrets.

## Entity: HostedVerificationRun
Description: The full verification session that proves the hosted revision is usable.

Fields:
- `revisionName` (string, required): Hosted revision under test.
- `startedAt` (timestamp, required): Verification session start time.
- `completedAt` (timestamp, optional): Verification session completion time.
- `overallResult` (string, required): Aggregate pass/fail result for the hosted verification flow.
- `checks` (list of `VerificationCheckResult`, required): Ordered verification outcomes.

Validation rules:
- `overallResult` MUST be `pass` only if all required checks pass.
- Check order MUST keep health and readiness ahead of MCP verification.

## Relationships

- `DeploymentInputSet` is consumed to create one `HostedRevisionRecord`.
- `HostedRevisionRecord` is evaluated by one or more `HostedVerificationRun` sessions.
- Each `HostedVerificationRun` contains ordered `VerificationCheckResult` entries.

## State Transitions

1. Deployment inputs prepared -> `DeploymentInputSet` validated.
2. Deployment executed -> `HostedRevisionRecord` created with `status=created`.
3. Hosted verification starts -> `HostedVerificationRun` created.
4. Liveness and readiness checks pass -> MCP verification checks proceed.
5. All required checks pass -> `HostedRevisionRecord.status=verified`, `HostedVerificationRun.overallResult=pass`.
6. Any required check fails -> `HostedRevisionRecord.status=failed_verification`, `HostedVerificationRun.overallResult=fail`.
