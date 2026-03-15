# Data Model: FND-007 Hosted Probe Semantics + HTTP Hardening

## Entity: HostedRouteContract
Description: The externally visible rule set for one hosted path, including
allowed methods, expected request shape, status behavior, and response-body
policy.

Fields:
- `path` (string, required): Hosted route identifier such as `/healthz`,
  `/readyz`, `/mcp`, or an unsupported-path class.
- `allowedMethods` (list of strings, required): HTTP methods accepted for the
  route.
- `successStatus` (string, required): Status class or exact status expected for
  successful requests.
- `failureStatuses` (list, required): Supported failure categories and their
  mapped status outcomes.
- `requestBodyPolicy` (string, required): Whether the route ignores, requires,
  or validates a request body.
- `responseBodyPolicy` (string, required): Whether the route returns a success
  payload, an error payload, or no body for a given outcome.
- `contentTypePolicy` (string, required): Response media type rule for success
  and failure responses.

Validation rules:
- Supported routes MUST have at least one allowed method.
- Each failure category MUST map to exactly one transport-level status outcome.
- `contentTypePolicy` MUST remain consistent with the hosted contract when a
  response body is returned.

## Entity: ReadinessCheckResult
Description: The machine-readable status of one readiness check category.

Fields:
- `checkName` (string, required): Readiness check category such as
  `configuration` or `secrets`.
- `result` (string, required): `pass` or `fail`.
- `reasonCode` (string, optional): Stable failure code when the check fails.
- `reasonMessage` (string, optional): Sanitized operator-visible explanation.

Validation rules:
- `reasonCode` and `reasonMessage` MUST be present when `result` is `fail`.
- Only sanitized, non-secret messages may appear in failure details.

## Entity: HostedErrorPayload
Description: The structured client-visible error body used for malformed,
unsupported, or unknown hosted requests.

Fields:
- `code` (string, required): Normalized error category.
- `message` (string, required): Sanitized summary of the request problem.
- `details` (object or null, required): Optional machine-readable error detail.
- `requestId` (string, optional): Correlation identifier when available.

Validation rules:
- `code` and `message` MUST be present on every error payload.
- `details` MUST be machine-readable or null.
- Error payloads MUST NOT include stack traces or secrets.

## Entity: ProbeOutcome
Description: The transport-level result observed by a hosted liveness or
readiness caller.

Fields:
- `path` (string, required): Probe route invoked.
- `statusCode` (integer, required): HTTP status returned to the caller.
- `serviceState` (string, required): `alive`, `ready`, or `not_ready`.
- `bodyType` (string, required): Response body class such as liveness payload,
  readiness payload, or error payload.

Validation rules:
- `/healthz` MUST map liveness success to a success status.
- `/readyz` MUST map `ready` and `not_ready` to different status outcomes.

## Entity: HostedRequestClassification
Description: The normalized classification used to choose hosted status and
payload behavior before a response is written.

Fields:
- `pathClass` (string, required): `healthz`, `readyz`, `mcp`, or `unknown`.
- `methodClass` (string, required): `supported` or `unsupported`.
- `mediaTypeClass` (string, required): `supported`, `unsupported`, or
  `not_applicable`.
- `bodyClass` (string, required): `valid`, `malformed`, `missing`, or
  `ignored`.
- `outcomeClass` (string, required): `success`, `not_ready`, `bad_request`,
  `unsupported_media_type`, `method_not_allowed`, or `not_found`.

Validation rules:
- Each hosted request MUST resolve to exactly one `outcomeClass`.
- `method_not_allowed` and `not_found` MUST remain distinguishable.
- A request with malformed syntax MUST not be classified as successful.

## Relationships

- `HostedRouteContract` governs one or more `HostedRequestClassification`
  outcomes for its path.
- `HostedRequestClassification` determines whether the response body is a
  readiness payload, MCP success envelope, or `HostedErrorPayload`.
- `ReadinessCheckResult` entries populate the not-ready form of the readiness
  contract.
- `ProbeOutcome` is derived from a `HostedRouteContract` plus a resolved
  `HostedRequestClassification`.

## State Transitions

1. Hosted request received -> `HostedRequestClassification` created.
2. Path, method, media type, and body validity evaluated.
3. Classification resolves to one `outcomeClass`.
4. `outcomeClass` selects the applicable `HostedRouteContract` behavior.
5. Response body and status code are emitted together.
6. For `/readyz`, readiness check results determine whether the final
   `ProbeOutcome.serviceState` is `ready` or `not_ready`.
