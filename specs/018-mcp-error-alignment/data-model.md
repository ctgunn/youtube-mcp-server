# Data Model: FND-018 JSON-RPC / MCP Error Code Alignment

## Entity: ErrorCodeContract
Description: The documented numeric error-code mapping the service promises to expose for covered MCP failure scenarios.

Fields:
- `code` (integer, required): Numeric client-visible error code returned in the MCP `error.code` field.
- `family` (string, required): Broad classification such as protocol, validation, security, resource, or execution failure.
- `defaultMessage` (string, required): Sanitized default message associated with the mapping.
- `httpStatusFamily` (string, optional): Hosted status-family expectation when the contract applies to hosted flows.
- `covered` (boolean, required): Whether the failure category is in scope for FND-018 alignment.

Validation rules:
- Every covered client-visible MCP failure MUST map to exactly one numeric code.
- The contract MUST not mix string and numeric code types for covered MCP responses.
- The contract MUST remain stable across local and hosted flows for equivalent covered failures.

## Entity: FailureCategory
Description: A normalized category used internally and in `error.data.category` to preserve actionable detail after the top-level code is aligned.

Fields:
- `name` (string, required): Stable category identifier such as malformed_request, invalid_argument, unauthenticated, resource_missing, or internal_execution_failure.
- `layer` (string, required): Where the failure originates, such as transport, protocol, security, session, or tool execution.
- `precedence` (integer, required): Relative order used when more than one category could apply to the same request.
- `clientRecoverable` (boolean, required): Whether a client can reasonably correct the request and retry without operator intervention.

Validation rules:
- Every covered failure response MUST expose a stable category value.
- Categories MUST be specific enough for tests and operators to distinguish failure classes without parsing free-form message text.
- Precedence ordering MUST be deterministic and documented.

## Entity: ClientVisibleErrorPayload
Description: The structured MCP error body returned to a caller for a covered failure.

Fields:
- `jsonrpc` (string, required): Protocol version marker.
- `id` (string or number or null, optional): Matching request identifier when available.
- `error.code` (integer, required): Numeric code from `ErrorCodeContract`.
- `error.message` (string, required): Sanitized human-readable message.
- `error.data.category` (string, optional): Stable failure category.
- `error.data.context` (object, optional): Safe additional details such as tool name, session identifier, or denial reason.

Validation rules:
- The payload MUST never expose stack traces, raw exceptions, secret values, or internal-only diagnostics.
- The payload MUST remain JSON-RPC-shaped for local and hosted MCP flows.
- Safe detail fields MAY vary by category, but the top-level shape must remain stable.

## Entity: HostedErrorOutcome
Description: The hosted representation of a covered MCP failure, combining HTTP status behavior with the numeric MCP error body.

Fields:
- `statusCode` (integer, required): Hosted HTTP response status returned for the failure.
- `errorPayload` (ClientVisibleErrorPayload, required): Numeric MCP error body returned to the caller.
- `originPolicyApplied` (boolean, required): Whether hosted origin or browser policy was evaluated before the denial.
- `authEvaluated` (boolean, required): Whether hosted credential checks were evaluated before the denial.

Validation rules:
- Hosted outcomes MUST preserve the previously documented status-family behavior for equivalent denial classes.
- Hosted outcomes MUST reuse the same numeric `error.code` mapping as local flows for equivalent covered failures.
- Hosted outcomes MUST not create or mutate MCP sessions when denial happens before protected processing.

## Entity: MappingPrecedenceRule
Description: A deterministic rule defining which category wins when multiple failure descriptions could apply.

Fields:
- `higherPriorityCategory` (string, required): The category that must be returned first.
- `lowerPriorityCategory` (string, required): The category suppressed when both could apply.
- `scope` (string, required): Where the rule applies, such as hosted edge, local protocol router, or tool execution.
- `reason` (string, required): Explanation of why the higher-priority category wins.

Validation rules:
- Every ambiguous covered scenario MUST be resolvable through one precedence rule.
- Precedence rules MUST be consistent with existing security boundaries and protocol lifecycle rules.

## Entity: VerificationScenario
Description: A documented unit, contract, integration, or hosted check proving that observed failure behavior matches the published mapping.

Fields:
- `scenarioName` (string, required): Stable verification name.
- `requestShape` (object, required): Representative failing request or hosted interaction.
- `expectedCode` (integer, required): Numeric code expected from the mapping contract.
- `expectedCategory` (string, required): Stable `error.data.category` value expected from the response.
- `expectedStatusCode` (integer, optional): Hosted HTTP status expected when applicable.
- `verificationLevel` (string, required): Unit, contract, integration, or hosted.

Validation rules:
- Verification scenarios MUST cover malformed request, unsupported method, invalid argument, auth or authorization denial, resource-missing, and unexpected tool-execution failures.
- Equivalent local and hosted scenarios MUST assert the same numeric code and category even when the hosted status code is also asserted.

## Relationships

- `ErrorCodeContract` maps one or more `FailureCategory` values to one numeric code family.
- `FailureCategory` is surfaced through `ClientVisibleErrorPayload.error.data.category`.
- `HostedErrorOutcome` wraps a `ClientVisibleErrorPayload` with the hosted status semantics already defined by prior hosted contracts.
- `MappingPrecedenceRule` determines which `FailureCategory` is exposed when a request matches more than one category.
- `VerificationScenario` proves that the implemented `ErrorCodeContract` and `MappingPrecedenceRule` values are honored.

## State Transitions

1. A request reaches the hosted edge or local protocol router.
2. The earliest applicable `FailureCategory` is identified according to `MappingPrecedenceRule`.
3. The selected category resolves to one `ErrorCodeContract` entry.
4. A sanitized `ClientVisibleErrorPayload` is constructed with the mapped numeric code and stable category detail.
5. Hosted flows wrap that payload in the appropriate `HostedErrorOutcome` without changing the mapped numeric code.
6. `VerificationScenario` evidence confirms the observed response matches the documented contract.
