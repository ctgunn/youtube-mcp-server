# Contract: FND-008 Deployment Execution + Cloud Run Observability

## Purpose

Define the operator-visible deployment workflow outcome and the hosted runtime
log contract for the foundation service. This contract extends the deployment
foundation and hosted HTTP work without changing the MCP request or response
envelopes themselves.

## Scope

- Operator-facing deployment workflow execution outcome
- Required deployment metadata capture for a successful hosted revision
- Hosted structured runtime log behavior for probe, MCP, and failure traffic

## Deployment Workflow Contract

### Executable Workflow

- The documented deployment workflow MUST perform the hosted deployment action.
- A successful shell exit alone is not enough to declare success unless the
  workflow also produces the required deployment record fields.
- Missing or invalid deployment inputs MUST stop the workflow before deployment
  execution and MUST return actionable operator guidance.

### Deployment Outcome Record

Each deployment attempt MUST produce one operator-visible outcome record with:

- deployment timestamp or run identifier
- outcome classification: `success`, `failed`, or `incomplete`
- operator-readable summary
- runtime identity
- environment profile
- minimum instances
- maximum instances
- request concurrency
- request timeout
- non-secret configuration/build summary
- secret reference names only

For `success`, the record MUST also include:

- `revisionName`
- `serviceUrl`

For `failed` or `incomplete`, the record MUST also include:

- failure stage
- remediation guidance

### Incomplete Metadata Contract

- If the hosted platform reports a deployment success but required metadata such
  as `revisionName` or `serviceUrl` cannot be captured, the workflow MUST return
  `incomplete` rather than `success`.
- An incomplete result MUST still preserve any metadata that was captured
  safely.

## Hosted Runtime Log Contract

### Required Event Fields

Every hosted request handled by the service MUST emit one structured log event
with:

- `timestamp`
- `severity`
- `requestId`
- `path`
- `status`
- `latencyMs`

Tool invocation requests that reach tool dispatch MUST also include:

- `toolName`

### Covered Request Classes

Structured hosted log emission MUST cover:

- `GET /health`
- `GET /ready`
- supported `/mcp` requests
- failed `/mcp` requests
- unsupported hosted paths
- other handled hosted request failures

### Runtime Output Rules

- Hosted structured log events MUST be emitted through service runtime output in
  a machine-readable format suitable for direct platform logging ingestion.
- Structured log emission MUST NOT require operators to parse free-form text to
  recover required fields.
- Structured log events MUST NOT include secrets, stack traces, or raw secret
  values from deployment inputs.

## Stability Expectations

- Existing MCP success and error envelopes remain unchanged.
- Existing liveness and readiness payload shapes remain unchanged.
- Deployment execution and hosted log emission MUST preserve current request ID
  correlation behavior between responses and logs.

## Testable Assertions

- Unit and integration tests can prove the deployment workflow executes the
  deployment action rather than only printing the deploy command.
- Tests can prove that successful deployment output includes `revisionName`,
  `serviceUrl`, and the required runtime settings summary.
- Tests can prove that incomplete metadata capture is classified as
  `incomplete`.
- Integration and contract tests can prove that hosted probe, MCP, and failure
  requests emit structured log events with the required fields.
- Regression tests can prove that non-tool hosted requests omit `toolName`
  while tool calls include it when available.
