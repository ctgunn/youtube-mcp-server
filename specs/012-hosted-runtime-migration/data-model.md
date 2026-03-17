# Data Model: FND-012 Hosted Runtime Migration for Streaming MCP

## Entity: HostedRuntimeProfile
Description: The runtime-level definition of how the hosted service accepts
traffic, exposes routes, and supports streaming MCP behavior after migration.

Fields:
- `runtimeName` (string, required): Stable identifier for the hosted serving
  stack in use.
- `entrypointMode` (string, required): `local` or `cloud_run`.
- `supportsStreaming` (boolean, required): Whether the runtime can serve the
  existing streaming MCP contract.
- `routeSet` (list of strings, required): Hosted routes exposed by the runtime.
- `requestBridgeMode` (string, required): How hosted HTTP requests are adapted
  into the existing MCP handling boundary.
- `logCorrelationEnabled` (boolean, required): Whether request correlation and
  structured runtime logs are available.

Validation rules:
- `routeSet` MUST include `/mcp`, `/health`, and `/ready`.
- `supportsStreaming` MUST be true for the migrated runtime profile.
- `entrypointMode` MUST map to one documented operator launch path.

## Entity: RuntimeLifecycleState
Description: The observable startup and shutdown state of the hosted runtime.

Fields:
- `state` (string, required): `starting`, `ready`, `degraded`, `stopping`, or
  `stopped`.
- `startedAt` (string, optional): Timestamp when runtime startup began.
- `readyAt` (string, optional): Timestamp when the runtime became ready.
- `degradedReason` (string, optional): Sanitized explanation when readiness is
  withheld or lost.
- `acceptingTraffic` (boolean, required): Whether the runtime should accept MCP
  traffic.
- `healthVisible` (boolean, required): Whether liveness should still report the
  process as alive.

Validation rules:
- `acceptingTraffic` MUST be false until `state` is `ready`.
- `healthVisible` MAY remain true while `state` is `starting` or `degraded`.
- `degradedReason` MUST not expose secrets or stack traces.

## Entity: DeploymentLaunchProfile
Description: The operator-facing startup definition used to launch the hosted
service locally and on Cloud Run.

Fields:
- `environment` (string, required): `local` or `cloud_run`.
- `entryCommand` (string, required): The documented command used to start the
  migrated runtime.
- `portBinding` (string, required): The expected network binding for the
  hosted service.
- `runtimeSettings` (object, required): Startup settings that affect request
  serving, concurrency, and timeouts.
- `rollbackCommand` (string, required): The prior launch path operators can use
  if migration verification fails.

Validation rules:
- Each `environment` MUST have exactly one documented `entryCommand`.
- The launch profile MUST be compatible with the same externally visible route
  set in `HostedRuntimeProfile`.
- `rollbackCommand` MUST remain available until hosted verification succeeds.

## Entity: VerificationRun
Description: A documented execution of the migrated runtime used to confirm
runtime behavior locally or on Cloud Run.

Fields:
- `targetEnvironment` (string, required): `local` or `cloud_run`.
- `checks` (list of strings, required): Ordered validations performed during
  the run.
- `expectedOutcomes` (list of strings, required): Observable results required
  for a successful verification.
- `evidenceLocation` (string, optional): File or record that captures the run.
- `result` (string, required): `pending`, `passed`, or `failed`.

Validation rules:
- `checks` MUST include liveness, readiness, initialize, and at least one
  streaming MCP interaction.
- Local and hosted verification runs MUST validate the same core MCP behaviors.
- A failed verification run MUST identify which observable outcome did not
  match expectations.

## Entity: StreamingSessionBoundary
Description: The hosted runtime's isolation boundary for one client session
while serving the existing MCP transport contract.

Fields:
- `sessionId` (string, required): Client-visible session identifier.
- `transportState` (string, required): `open`, `idle`, `reconnecting`, or
  `closed`.
- `runtimeOwner` (string, required): The hosted runtime instance serving the
  session.
- `isolationStatus` (string, required): `isolated` or `violated`.
- `lastObservedAt` (string, required): Timestamp of the last runtime activity
  for the session.

Validation rules:
- A session marked `isolated` MUST not receive traffic from another session.
- A session served by the migrated runtime MUST remain compatible with the
  existing streaming MCP contract.
- Runtime migration MUST not change session ownership semantics for valid
  requests.

## Relationships

- `HostedRuntimeProfile` governs one or more `DeploymentLaunchProfile` values.
- `RuntimeLifecycleState` belongs to one `HostedRuntimeProfile`.
- `VerificationRun` validates one `DeploymentLaunchProfile` against the
  expectations in `HostedRuntimeProfile`.
- `StreamingSessionBoundary` is served by one active `HostedRuntimeProfile` and
  is affected by the current `RuntimeLifecycleState`.

## State Transitions

1. Runtime process starts -> `RuntimeLifecycleState.state` becomes `starting`.
2. Startup initialization completes -> `RuntimeLifecycleState.state` becomes
   `ready` and `acceptingTraffic` becomes true.
3. Runtime loses a required startup dependency -> `RuntimeLifecycleState.state`
   becomes `degraded` and readiness is withheld.
4. Client establishes MCP traffic -> `StreamingSessionBoundary.transportState`
   becomes `open`.
5. Runtime begins shutdown -> `RuntimeLifecycleState.state` becomes `stopping`
   and new traffic stops being accepted.
6. Shutdown completes -> `RuntimeLifecycleState.state` becomes `stopped`.
