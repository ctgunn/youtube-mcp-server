# Layer 1 Live Execution Runtime Contract

## Purpose

Define the shared execution behavior that converts a validated Layer 1 wrapper request into a real authenticated YouTube Data API request and returns an existing normalized result or safe normalized failure.

## Inputs

| Input | Contract |
| --- | --- |
| Endpoint metadata | Supplies the existing operation identity, request method/path, authorization requirement, quota metadata, and request shape. |
| Validated arguments | Have passed existing generic and resource-specific wrapper validation. |
| Auth context | Uses the mode selected by the existing operation rules and contains the required runtime credential. |
| Explicit execution override | May be supplied only by a test or deliberate local-development caller. |

## Execution Behavior

1. Validate arguments through the existing wrapper contract before any upstream attempt.
2. Build the request through the existing concrete transport. It supports query parameters, structured JSON bodies, raw media, and multipart metadata-plus-media forms as declared by the endpoint.
3. Attach an API key as a request credential for API-key mode or an OAuth bearer credential for OAuth-required mode. Credentials must never be copied to outputs or diagnostics.
4. Emit existing safe request/response/error observability events that include endpoint identity and auth mode but no secret material.
5. Apply the existing retry-selection policy to normalized retryable failures. Preserve the current maximum-attempt behavior; no new sleep, jitter, or backoff algorithm is introduced here.
6. Normalize successful responses through the existing operation-specific response normalizer and return the established public result shape.
7. Normalize upstream failures through the existing error model and public tool mapping, preserving client-safe categories and redaction.

## Failure Rules

| Condition | Required outcome |
| --- | --- |
| Missing/blank required credential | Safe normalized configuration or authorization failure before upstream execution. |
| Authorization or authentication rejection upstream | Existing normalized authentication/authorization failure with secret-free details. |
| Quota/rate limit, transient network failure, timeout | Existing normalized failure and retry selection; terminal outcome is safe and secret-free. |
| Malformed or unexpected upstream payload | Existing normalized upstream failure; no raw body is returned. |
| Explicit test/local representative transport | Permitted only when supplied explicitly; behavior must be apparent to the test/local caller. |
| Any configured runtime failure | Must never produce a representative or static successful payload. |

## Observability and Security

- Safe records may contain request ID, resource, operation, auth mode, phase, status, latency, error category, and retryability.
- Records and client-visible failures must not contain API keys, OAuth tokens, bearer headers, query strings with credentials, raw request bodies, raw media, stack traces, or unfiltered upstream payloads.
- Request/response/error hooks remain the centralized observability boundary; endpoint wrappers do not add independent secret-bearing logging.

## Verification Obligations

- Unit tests prove runtime configuration, credential selection, request construction, media forms, retry selection, safe failure mapping, and redaction using controlled transports.
- Integration tests prove a wrapper and one configured public descriptor select the live executor with a controlled opener.
- Contract tests prove public MCP schemas, metadata, normalized result shape, and error categories stay compatible.
- Final verification must run `python3 -m pytest` and `python3 -m ruff check .`.
