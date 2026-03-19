# Contract: FND-015 Hosted Session Durability

## Purpose

Define the externally visible hosted MCP contract changes required to make session continuation durable under the supported Cloud Run deployment model.

## Scope

- Hosted `initialize` session creation expectations
- Follow-up `POST /mcp` and `GET /mcp` continuation behavior for valid sessions
- Stable failure categories for invalid, expired, and replay-unavailable sessions
- Readiness and deployment-topology signals related to durable hosted sessions
- Hosted verification expectations for continuation and reconnect behavior

## Relationship to Prior Contracts

- This contract extends [/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md) by hardening the hosted session model behind the existing streamable transport.
- This contract depends on the security boundary in [/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md).
- This contract preserves the MCP-native request and result semantics established in [/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/spec.md).

## Session Creation

### `POST /mcp` with `initialize`

Representative request:

```json
{
  "jsonrpc": "2.0",
  "id": "req-init-durable",
  "method": "initialize",
  "params": {
    "clientInfo": {
      "name": "hosted-client",
      "version": "1.0.0"
    }
  }
}
```

Required behavior:

- Successful hosted initialize MUST return a valid `MCP-Session-Id` header.
- The issued session MUST remain usable by follow-up requests served through the supported hosted topology and MUST NOT depend on the original process retaining local memory.
- Security and origin checks still run before session creation.

## Session Continuation

### Follow-up `POST /mcp`

Representative request headers:

```text
Content-Type: application/json
Accept: application/json, text/event-stream
Authorization: Bearer <token>
MCP-Session-Id: <session-id>
```

Representative request body:

```json
{
  "jsonrpc": "2.0",
  "id": "req-tools",
  "method": "tools/list",
  "params": {}
}
```

Rules:

- A valid session created by `initialize` MUST remain usable for follow-up `POST` requests within the documented continuation window.
- Continuation success MUST be independent of which healthy instance serves the request, provided the deployment matches the supported topology.
- Session continuation failures MUST not be surfaced as tool failures.

### Follow-up `GET /mcp`

Representative request headers:

```text
Accept: text/event-stream
Authorization: Bearer <token>
MCP-Session-Id: <session-id>
Last-Event-ID: <optional-replay-cursor>
```

Rules:

- A valid session MUST remain usable for stream continuation and reconnect within the documented replay window.
- If `Last-Event-ID` refers to retained replayable history, the server MUST replay the subsequent retained events in order.
- If the replay cursor is outside the retained replay window, the server MUST return the documented replay-unavailable failure instead of pretending the session never existed.

## Stable Session-State Failures

| Category | When It Applies | Expected Status Family | Distinguishing Behavior |
|----------|-----------------|------------------------|-------------------------|
| `invalid_session` | Session identifier is missing, malformed, or unknown | `400` or `404` per final mapping | Not treated as tool or security failure |
| `expired_session` | Session existed but is outside the continuation TTL | `404` or equivalent session-state denial | Indicates the client must re-initialize |
| `replay_unavailable` | Session is still known but requested replay history is no longer retained | `409` or equivalent continuity-safe denial | Distinct from unknown session |
| `durability_unavailable` | Hosted topology cannot satisfy durable-session guarantees | readiness failure or hosted request denial per final mapping | Signals operator misconfiguration, not client misuse |

Rules:

- Session-state failures MUST remain distinct from authentication failures, origin denials, and tool execution errors.
- Failure payloads MUST stay safe for hosted exposure and must not leak backend addresses, secrets, or internal stack traces.
- Existing MCP session headers and protocol version headers remain in use for successful hosted flows.

## Readiness and Deployment Contract

### `GET /ready`

Rules:

- Hosted readiness MUST indicate not-ready when the runtime is configured to require durable hosted sessions but the shared session backend is missing or unhealthy.
- Readiness output MUST provide an operator-safe reason that the deployment cannot currently guarantee durable hosted sessions.
- A topology documented as unsupported for session durability MUST not be presented as fully ready for durable hosted MCP traffic.

## Hosted Verification Contract

Hosted verification MUST prove:

1. `initialize` creates a reusable hosted session.
2. A follow-up `POST /mcp` succeeds when served through the supported durable-session model.
3. A follow-up `GET /mcp` succeeds for the same session and can replay recent events when a valid cursor is supplied.
4. A second runtime instance sharing the durable backend can continue the same hosted session.
5. An invalid or expired session fails with the documented session-state category.
6. A replay request outside the retained replay window fails with the documented replay-unavailable behavior.
7. Verification evidence records distinct initialize, continuation, reconnect, and failure-path checks.

## Testable Assertions

- Unit tests can prove durable session records, expiry rules, and replay-window handling behave deterministically.
- Contract tests can prove hosted session creation, continuation, and failure payloads align with this document.
- Integration tests can prove separate app instances sharing the durable backend can resume the same session.
- Hosted verification can prove the documented durable topology and reconnect rules hold on the deployed Cloud Run service.
