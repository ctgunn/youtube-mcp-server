# Hosted MCP Security Contract

## Purpose

Define the external contract changes for hosted MCP security hardening in FND-013. This contract applies to the hosted routes exposed by the service and documents required request metadata, denial behavior, and verification expectations.

## Hosted Routes

### `GET /health`

- Remains unauthenticated.
- Returns liveness only.
- Not subject to MCP authentication or origin allowlist denial.

### `GET /ready`

- Remains unauthenticated.
- Returns readiness, including security-configuration failure when required hosted security settings are missing or invalid.
- Must preserve existing success and non-success readiness semantics.

### `POST /mcp`

- Protected route for MCP initialization and request handling.
- Requires supported content negotiation and the hosted authentication contract.
- Applies origin-aware handling before session creation, request execution, or tool dispatch.

### `GET /mcp`

- Protected route for SSE stream continuation and event delivery.
- Requires supported streaming headers plus the hosted authentication contract.
- Applies origin-aware handling before stream access is granted.

## Request Requirements

### Authentication

- Hosted MCP requests must present the documented bearer credential on protected `/mcp` routes.
- The credential is sent as `Authorization: Bearer <token>`.
- Missing, malformed, invalid, expired, or environment-mismatched credentials are denied before protected MCP processing.
- Raw credentials are never echoed in responses or observability output.

### Origin Handling

- Requests that include `Origin` are treated as browser-originated and must match an operator-configured allowlist.
- Requests without `Origin` are treated as non-browser remote clients and may continue only if the runtime configuration explicitly permits originless callers.
- Valid credentials do not override a denied browser origin.

### MCP Session Behavior

- Security checks occur before session creation on `initialize`.
- Security checks occur before session reuse or stream access on follow-up `/mcp` requests.
- Denied requests must not create or mutate MCP sessions.

## Stable Failure Categories

| Category | When It Applies | Expected Status Family | Protected MCP Processing |
|----------|-----------------|------------------------|--------------------------|
| `unauthenticated` | Credential missing or not parseable | `401` | Not allowed |
| `invalid_credential` | Credential present but invalid, expired, or wrong environment | `401` or `403` per final error mapping | Not allowed |
| `origin_denied` | Browser-originated request not in allowlist | `403` | Not allowed |
| `malformed_security_input` | Security-related headers are syntactically invalid | `400` | Not allowed |
| `unsupported_request` | Unsupported hosted method, path, or negotiation pattern | Existing route-specific behavior | Not allowed |

## Observability Contract

- Every protected `/mcp` request produces a request identifier.
- Every denied protected request emits a security decision record with:
  - request identifier
  - hosted path
  - decision category
  - caller classification (`browser` or `non_browser`)
- Denied security decision records must be emitted before protected MCP execution begins.
- Observability output must not include raw tokens, secrets, or internal policy definitions beyond the denial category.

## Verification Contract

### Successful Path

1. Caller presents valid bearer authentication.
2. Caller satisfies origin policy for its client type.
3. `initialize` succeeds and returns the expected hosted MCP response.
4. Follow-up authenticated `/mcp` request succeeds on the same hosted service.

### Denied Paths

1. Missing or malformed authentication returns a stable authentication failure before MCP execution.
2. Disallowed browser origin returns a stable origin denial before MCP execution.
3. A denied request produces an operator-visible decision record that can be correlated with the request identifier.
