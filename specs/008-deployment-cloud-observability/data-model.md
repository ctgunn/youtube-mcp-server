# Data Model: FND-008 Deployment Execution + Cloud Run Observability

## Entity: DeploymentRunRecord
Description: The operator-visible result of one deployment attempt, combining
execution outcome, hosted revision identity, endpoint information, and applied
runtime settings.

Fields:
- `deploymentId` (string, required): Unique identifier for the deployment run
  record or execution timestamp key.
- `executedAt` (timestamp, required): Time the deployment workflow was run.
- `outcome` (string, required): `success`, `failed`, or `incomplete`.
- `summary` (string, required): Operator-readable deployment outcome summary.
- `revisionName` (string, optional): Hosted revision created by the deployment.
- `serviceUrl` (string, optional): Hosted endpoint for the deployed service.
- `runtimeSettings` (object, required): Effective runtime identity, environment
  profile, scaling bounds, concurrency, timeout, and non-secret configuration
  summary used for the attempted revision.
- `failureStage` (string, optional): `input_validation`, `deployment_execution`,
  or `metadata_capture` when the outcome is not `success`.
- `remediation` (string, optional): Operator guidance for the next recovery
  action.

Validation rules:
- `outcome` MUST resolve to exactly one of `success`, `failed`, or `incomplete`.
- `revisionName` and `serviceUrl` MUST be present when `outcome` is `success`.
- `failureStage` MUST be present when `outcome` is `failed` or `incomplete`.
- `runtimeSettings` MUST be present for every deployment attempt.
- `summary` and `remediation` MUST remain sanitized and MUST NOT include secret
  values.

## Entity: RuntimeSettingsSnapshot
Description: The retained subset of deployment inputs and applied runtime
configuration that operators need for hosted verification and audit.

Fields:
- `serviceName` (string, required): Hosted service identifier.
- `environmentProfile` (string, required): Deployment profile used for the run.
- `runtimeIdentity` (string, required): Execution identity assigned to the
  revision.
- `minInstances` (integer, required): Lower autoscaling bound.
- `maxInstances` (integer, required): Upper autoscaling bound.
- `concurrency` (integer, required): Request concurrency limit.
- `timeoutSeconds` (integer, required): Hosted request timeout.
- `secretReferenceNames` (list of strings, required): Secret names referenced
  for the run, without exposing secret values.
- `configSummary` (object, required): Non-secret configuration and build
  metadata summary used for the deployment.

Validation rules:
- `environmentProfile` MUST map to a supported runtime profile.
- `minInstances` MUST be less than or equal to `maxInstances`.
- `concurrency` and `timeoutSeconds` MUST be positive values.
- Secret values MUST NOT appear in `secretReferenceNames` or `configSummary`.

## Entity: HostedRequestLogEvent
Description: One structured log record emitted for a hosted request handled by
the service.

Fields:
- `timestamp` (timestamp, required): Event creation time.
- `severity` (string, required): Hosted log severity derived from request
  outcome.
- `requestId` (string, required): Correlation identifier for the handled
  request.
- `path` (string, required): Hosted request path.
- `status` (string, required): `success` or `error`.
- `latencyMs` (number, required): Request handling duration in milliseconds.
- `toolName` (string, optional): Invoked tool name when the request is a tool
  call and tool context is available.

Validation rules:
- Every hosted request MUST emit exactly one `HostedRequestLogEvent`.
- `toolName` MUST be omitted for non-tool requests.
- `latencyMs` MUST be non-negative.
- Event payloads MUST remain structured and JSON-serializable.
- Event payloads MUST NOT contain secrets or stack traces.

## Entity: HostedLogEmissionResult
Description: The outcome of writing a structured hosted request log event to
runtime output.

Fields:
- `requestId` (string, required): Request associated with the emission attempt.
- `destination` (string, required): Runtime output target such as `stdout` or
  `stderr`.
- `result` (string, required): `emitted` or `fallback_only`.
- `reason` (string, optional): Sanitized explanation when normal emission does
  not occur.

Validation rules:
- Normal request handling MUST prefer `result=emitted`.
- Failures to emit MUST not change the client-visible response contract.

## Relationships

- `DeploymentRunRecord` contains one `RuntimeSettingsSnapshot`.
- `DeploymentRunRecord` provides the revision and endpoint inputs used by
  hosted verification.
- Each handled hosted request produces one `HostedRequestLogEvent`.
- `HostedLogEmissionResult` records how a `HostedRequestLogEvent` reached
  runtime output.

## State Transitions

1. Deployment inputs validated -> `RuntimeSettingsSnapshot` prepared.
2. Deployment command executed -> `DeploymentRunRecord.outcome` tentatively set
   to `success` or `failed`.
3. Revision metadata captured -> outcome remains `success` if all required
   metadata exists, else transitions to `incomplete`.
4. Hosted request handled -> `HostedRequestLogEvent` created from request
   context and outcome.
5. Structured event written to runtime output -> `HostedLogEmissionResult`
   recorded as `emitted`.
6. If log emission degrades, client response still completes and emission result
   is tracked as `fallback_only`.
