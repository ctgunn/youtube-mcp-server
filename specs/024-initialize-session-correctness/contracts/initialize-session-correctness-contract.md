# Contract: FND-024 Initialize Session Correctness

## Purpose

Define the externally visible hosted MCP contract changes required so continuation session state is created only after a successful initialize handshake.

## Scope

- Hosted `POST /mcp` behavior for initialize success and initialize failure
- Rules for when `MCP-Session-Id` may and may not be returned
- Continuation behavior after successful initialize and after rejected initialize attempts
- Stable failure behavior for continuation attempts using non-issued session identifiers
- Hosted verification expectations proving both positive and negative initialize/session paths

## Relationship to Prior Contracts

- This contract narrows the initialize/session lifecycle described in [hosted-session-durability-contract.md](~/Projects/youtube-mcp-server/specs/015-hosted-session-durability/contracts/hosted-session-durability-contract.md) by adding the rule that durable continuation state begins only after successful initialize completion.
- This contract preserves the MCP-native initialize request and response semantics established in [mcp-protocol-contract.md](~/Projects/youtube-mcp-server/specs/010-mcp-protocol-alignment/contracts/mcp-protocol-contract.md).
- This contract depends on the hosted security boundary in [hosted-mcp-security.md](~/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md).
- This contract preserves the streamable transport and continuation headers defined by [specs/009-mcp-streamable-http-transport/spec.md](~/Projects/youtube-mcp-server/specs/009-mcp-streamable-http-transport/spec.md).

## Initialize Success Contract

### `POST /mcp` with valid `initialize`

Representative request:

```json
{
  "jsonrpc": "2.0",
  "id": "req-init-success",
  "method": "initialize",
  "params": {
    "clientInfo": {
      "name": "hosted-client",
      "version": "1.0.0"
    }
  }
}
```

Representative response properties:

- HTTP success status
- JSON-RPC success body for `initialize`
- `MCP-Session-Id` response header present
- `MCP-Protocol-Version` response header present

Rules:

- A successful initialize response MUST issue exactly one `MCP-Session-Id` for the accepted initialize attempt.
- The issued session identifier MUST reference usable hosted session state for follow-up continuation.
- Security, origin, and protocol-version checks still run before initialize success can produce session state.

## Initialize Failure Contract

### `POST /mcp` with malformed, invalid, or rejected `initialize`

Representative invalid request:

```json
{
  "jsonrpc": "2.0",
  "id": "req-init-invalid",
  "method": "initialize",
  "params": {}
}
```

Representative response properties:

- HTTP failure or protocol-error status appropriate to the rejection path
- MCP-safe error body
- No `MCP-Session-Id` response header

Rules:

- Rejected initialize requests MUST NOT create hosted session state.
- Rejected initialize requests MUST NOT return `MCP-Session-Id`.
- This rule applies whether initialize is rejected by hosted validation, security checks, protocol-version checks, malformed request handling, or initialize parameter validation.

## Retry Contract

Rules:

- If a client retries initialize after one or more rejected attempts, only the later successful initialize response may issue `MCP-Session-Id`.
- A successful retry MUST create fresh valid session state and MUST NOT depend on any session state from earlier rejected attempts.
- The contract does not require clients to reuse the same request identifier across retries.

## Continuation Contract

### Follow-up continuation after initialize

Representative request headers:

```text
Content-Type: application/json
Accept: application/json, text/event-stream
Authorization: Bearer <token>
MCP-Session-Id: <session-id-from-successful-initialize>
```

Rules:

- Continuation is valid only when the session identifier came from a successful initialize response.
- A continuation request using a session identifier that was never issued from a successful initialize response MUST fail through the existing session-state failure contract.
- Continuation failure after rejected initialize MUST remain distinct from tool execution failure.

## Failure Contract

| Category | When It Applies | Required Behavior |
|----------|-----------------|-------------------|
| `invalid_argument` | Initialize is malformed or missing required initialize inputs | No `MCP-Session-Id`; no hosted session created |
| `unauthenticated` / `invalid_credential` / `origin_denied` / `malformed_security_input` | Hosted security rejects initialize before success | No `MCP-Session-Id`; no hosted session created |
| `session_not_found` | Client attempts continuation with a non-issued or unknown session identifier | Stable session-state failure, not a tool failure |
| `expired_session` | Client attempts continuation with a once-valid session that is no longer valid | Stable session-state failure distinct from initialize rejection |

Rules:

- Failure payloads MUST remain safe for hosted exposure and MUST NOT leak session-store internals, secrets, or stack traces.
- Rejected initialize requests MUST be distinguishable from later continuation failures caused by invalid or expired session identifiers.

## Hosted Verification Contract

Hosted verification MUST prove:

1. One rejected initialize path returns no `MCP-Session-Id`.
2. One rejected initialize path leaves no usable continuation state.
3. One successful initialize path returns exactly one `MCP-Session-Id`.
4. A follow-up continuation using the successful initialize session identifier succeeds.
5. A continuation attempt using a non-issued session identifier fails through the documented session-state contract.
6. A later successful retry after a rejected initialize can establish valid continuation state.
7. Verification evidence records the initialize success and initialize failure distinction explicitly.

Representative verification check names:

- `initialize-invalid-no-session`
- `initialize-success-session-created`
- `session-post-continuation`
- `session-invalid`
- `initialize-retry-success`

## Testable Assertions

- Unit tests can prove initialize success is the only condition that allows session creation.
- Contract tests can prove `MCP-Session-Id` is present on successful initialize and absent on rejected initialize.
- Integration tests can prove continuation succeeds only for session identifiers issued by successful initialize responses.
- Hosted verification can prove the same success and failure rules on the protected `/mcp` route.
