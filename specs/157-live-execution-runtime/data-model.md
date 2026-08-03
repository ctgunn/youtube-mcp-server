# Data Model: Layer 1 Live Execution Runtime

## Runtime Configuration

Represents the operator-provided, non-persistent settings used to construct the configured live runtime.

| Field | Description | Validation |
| --- | --- | --- |
| `youtube_api_key` | Optional API-key credential sourced from `YOUTUBE_API_KEY`. | May be absent at startup only where the active profile allows it; it must be nonblank when an API-key operation is invoked. Its value is secret. |
| `youtube_oauth_token` | Optional opaque OAuth credential sourced from `YOUTUBE_OAUTH_TOKEN`. | May be absent until an OAuth-required operation is invoked; it must be nonblank for that operation. Its value is secret. |
| `timeout_seconds` | Existing live-request timeout. | Positive value; default remains 10 seconds. |
| `retry_policy` | Existing shared retry-selection policy. | Valid policy with at least one attempt; configured live default remains three attempts. |
| `execution_mode` | Indicates configured live execution versus explicit test/local injection. | Configured application runtime must be `live`; test/local selection must be explicit. |

## Credential Bundle and Auth Context

Represents credentials made available to a single wrapper execution without disclosing them in public results or logs.

| Field | Description | Validation / relationship |
| --- | --- | --- |
| `api_key` | Selected API-key credential. | Required only when the selected auth mode is `api_key`. |
| `oauth_token` | Selected OAuth credential. | Required only when the selected auth mode is `oauth_required`. |
| `mode` | Existing endpoint-selected authorization mode: `api_key`, `oauth_required`, or conditional. | Conditional operations resolve to the mode selected by existing handler and wrapper rules. |
| `conditional_reason` | Existing justification for a conditional selection. | Required by the existing auth context when conditional mode is represented. |

Relationship: Runtime Configuration supplies credential availability; the existing endpoint metadata and handler/wrapper behavior select an Auth Context; the Auth Context supplies only the needed credential to an Execution Request.

## Execution Request

Represents the existing wrapper-defined request handed to the shared live executor.

| Field | Description | Validation / relationship |
| --- | --- | --- |
| `metadata` | Existing endpoint identity, HTTP method/path shape, quota cost, auth mode, and request shape. | Immutable contract supplied by the wrapper. |
| `arguments` | Validated endpoint arguments. | Must pass the wrapper's existing request-shape and resource-specific validation before execution. |
| `auth_context` | Selected credential mode and credential bundle. | Must match the operation's existing authorization rule. |
| `request_form` | Derived request representation: query-only, structured body, raw media, or multipart body plus media. | Determined from existing metadata and validated arguments. |

Relationship: A wrapper creates an Execution Request; the configured live executor turns it into an authenticated upstream request and gives the result to the existing response normalizer.

## Live Execution Result

Represents the only two outcomes of a configured live attempt.

| Field | Description | Validation / relationship |
| --- | --- | --- |
| `success_payload` | Normalized upstream response. | Must use the existing operation-specific response normalizer and preserve the public result contract. |
| `failure_category` | Existing normalized configuration, authentication, authorization, quota, availability, not-found, transient, or upstream failure category. | Must be client-safe and compatible with existing tool mappings. |
| `retryable` | Whether the shared retry policy may retry the failure. | Derived by existing error normalization and retry policy. |
| `safe_details` | Diagnostic details permitted for logs/tests/client-safe errors. | Must exclude credentials, authorization headers, raw request URLs, raw body/media, stack traces, and secret fields. |

## Observability Record

Represents one request, response, or failure event emitted by the existing shared executor hooks.

| Field | Description | Validation |
| --- | --- | --- |
| `request_id` | Correlation identifier. | Present for the request lifecycle. |
| `resource` and `operation` | Endpoint identity from metadata. | Safe to record. |
| `auth_mode` | Selected mode only, never credential material. | Must be an approved mode label. |
| `phase` and `status` | Request, response, or error lifecycle state. | Must match an existing integration event state. |
| `latency_ms`, `error_category`, `retryable` | Outcome diagnostics. | May be recorded when available; secret data is prohibited. |

## State Transitions

```text
runtime settings loaded
  -> credential availability validated
  -> endpoint/selector determines auth mode
  -> required credential present?
       -> no: safe configuration or authorization failure
       -> yes: validated execution request
  -> configured live executor selected
  -> request event emitted
  -> upstream attempt
       -> retryable normalized failure: retry until policy limit
       -> terminal normalized failure: safe error event and safe failure
       -> success: normalized response event and normalized result
```

The prohibited transition is: missing or failed live execution -> representative success result.
