# Contract: FND-016 Browser-Originated MCP Access + CORS Support

## Purpose

Define the externally visible hosted MCP contract for browser-originated access, including preflight behavior, response headers for approved origins, and stable denial behavior for unsupported browser requests.

## Scope

- Browser-originated preflight behavior for documented hosted routes
- Browser-originated response-header behavior for approved hosted MCP requests
- Stable denial behavior for disallowed origins and unsupported browser request patterns
- Interaction between browser access, existing authentication requirements, and existing hosted session behavior
- Hosted verification expectations for approved and denied browser access

## Relationship to Prior Contracts

- This contract extends [~/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md](~/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md) by making browser-originated hosted access explicit rather than implicit.
- This contract preserves the hosted streamable transport expectations established in [~/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md](~/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md).
- This contract preserves the MCP-native request, result, and error semantics established in [~/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/spec.md](~/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/spec.md).
- This contract must remain compatible with the durable hosted session behavior established in [~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/contracts/hosted-session-durability-contract.md](~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/contracts/hosted-session-durability-contract.md).

## Browser Access Model

Rules:

- Browser-originated access is supported only for hosted routes and methods that are explicitly documented as browser-accessible.
- In this feature slice, `/mcp` is the only browser-accessible hosted route.
- The existing origin allowlist remains the approval source of truth for browser-originated requests.
- A successful browser preflight does not replace authentication or session requirements for the actual hosted MCP request.
- Originless clients continue on the non-browser path and are not treated as browser requests solely because this contract exists.

## Browser Preflight

### `OPTIONS` to a supported hosted route

Representative request headers:

```text
Origin: http://localhost:3000
Access-Control-Request-Method: POST
Access-Control-Request-Headers: authorization, content-type
```

Required behavior:

- A browser preflight to a documented browser-accessible hosted route MUST receive a stable response that reflects whether the origin, method, and requested headers are supported.
- Approved preflight responses MUST include the documented allow headers for the target route and request pattern.
- Disallowed origins and unsupported browser request patterns MUST fail with stable documented behavior and MUST NOT appear to grant browser access.
- Preflight behavior MUST be explicit for hosted MCP routes rather than falling through to generic unsupported-method handling.

## Approved Actual Browser Requests

### `POST /mcp`

Representative request headers:

```text
Origin: http://localhost:3000
Content-Type: application/json
Accept: application/json, text/event-stream
Authorization: Bearer <token>
```

Representative request body:

```json
{
  "jsonrpc": "2.0",
  "id": "req-browser-init",
  "method": "initialize",
  "params": {
    "clientInfo": {
      "name": "browser-client",
      "version": "1.0.0"
    }
  }
}
```

Rules:

- An approved browser-originated hosted MCP request MUST return the documented cross-origin response headers on the actual response.
- Existing hosted authentication and MCP request validation still apply to the actual request.
- Successful browser support MUST preserve existing session headers and other response metadata needed by the documented hosted flow.

### `GET /mcp`

Representative request headers:

```text
Origin: http://localhost:3000
Accept: text/event-stream
Authorization: Bearer <token>
MCP-Session-Id: <session-id>
```

Rules:

- If browser-originated stream access is documented as supported, the actual hosted response MUST include the documented browser response headers while preserving the existing session and stream behavior.
- If a particular browser-originated `GET /mcp` pattern is not supported, the denial behavior MUST be explicit and documented rather than relying on browser failure alone.

## Stable Browser Denials

| Category | When It Applies | Expected Status Family | Distinguishing Behavior |
|----------|-----------------|------------------------|-------------------------|
| `origin_denied` | Origin is present but not allowed for browser access | denial | Does not include a successful browser grant |
| `unsupported_browser_route` | Browser preflight or actual request targets a hosted route that is not browser-accessible | unsupported | Distinct from unknown non-browser path handling |
| `unsupported_browser_method` | Browser requests a method not allowed for the target route | unsupported | Distinct from approved preflight behavior |
| `unsupported_browser_headers` | Browser requests headers outside the documented supported set | unsupported | Distinct from authentication failure |
| `unauthenticated` or equivalent existing auth failure | Actual approved-origin request omits or fails authentication | authentication failure | Browser support does not bypass auth |
| `malformed_origin` | Browser request presents an invalid origin value | malformed | Distinct from denied but well-formed origin |

Rules:

- Browser denials MUST remain distinguishable from authentication failures, invalid-session failures, and malformed MCP protocol requests.
- Failure payloads MUST remain safe for hosted exposure and MUST NOT leak secrets or internal stack traces.
- Denied browser responses MUST not imply that cross-origin access was granted.

## Response Header Contract

Approved browser responses MUST document:

- which origin value is granted for the response
- which methods are granted for browser access on the target route
- which request headers are granted for browser use
- which response headers are exposed for browser clients to read when the hosted flow depends on them
- `MCP-Session-Id`, `MCP-Protocol-Version`, and `X-Stream-Id` remain exposed when present on approved hosted MCP responses

Rules:

- The header contract MUST be applied consistently across preflight and actual responses for supported browser flows.
- The response header contract MUST be absent or denial-safe for unsupported browser requests.
- The header contract MUST preserve the client-visible headers required for the existing hosted MCP flow.

## Hosted Verification Contract

Hosted verification MUST prove:

1. An approved browser origin can complete preflight for a documented hosted route.
2. An approved browser origin can complete an authenticated hosted MCP request and receive the documented browser response headers.
3. A disallowed origin fails with the documented browser denial behavior.
4. An unsupported browser route, method, or requested-header pattern fails with the documented unsupported-browser behavior.
5. Browser verification evidence records distinct approved and denied request identifiers and outcomes.

## Testable Assertions

- Unit tests can prove origin normalization, browser-policy evaluation, and response-header selection behave deterministically.
- Contract tests can prove hosted browser preflight and actual-response behavior align with this document.
- Integration tests can prove approved and denied browser flows work end-to-end through the hosted request entrypoint.
- Hosted verification can prove the deployed service exposes explicit browser behavior rather than relying on incidental framework defaults.
