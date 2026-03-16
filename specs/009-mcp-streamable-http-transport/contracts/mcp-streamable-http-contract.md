# Contract: FND-009 MCP Streamable HTTP Transport

## Purpose

Define the externally visible hosted MCP transport contract for the foundation
server after replacing the current request/response-only `/mcp` route with
standards-aligned streamable HTTP behavior.

## Scope

- Hosted `GET /mcp` streaming behavior
- Hosted `POST /mcp` request submission and response-stream behavior
- Session header issuance and reuse
- SSE event delivery, reconnect, and concurrency rules
- Transport-level validation for headers and session state

## Hosted MCP Endpoint Contract

### Endpoint Shape

- The server exposes one MCP endpoint at `/mcp`.
- The endpoint supports both `GET` and `POST`.
- `/health` and `/ready` remain separate operational routes and are unchanged by
  this transport contract except for coexistence with `/mcp`.

## `POST /mcp`

### Request Rules

- Every client-to-server JSON-RPC message is sent as a new HTTP `POST` to
  `/mcp`.
- Clients must advertise support for both `application/json` and
  `text/event-stream` in the `Accept` header.
- The request body may contain:
  - one JSON-RPC request,
  - one JSON-RPC notification,
  - one JSON-RPC response,
  - or a valid batch when the transport adapter accepts batched input.

### Response Rules

- If the posted input is accepted and does not require a streamed response, the
  server may return `Content-Type: application/json` with one response object.
- If the posted input is a request that the server chooses to stream, the
  server returns `Content-Type: text/event-stream`.
- If the posted input consists only of notifications or responses and is
  accepted, the server returns HTTP `202` with no body.
- If the posted input is malformed, unsupported, or not acceptable under the
  transport rules, the server returns a non-success HTTP status and a
  machine-readable error payload when a body is returned.

### Streaming Rules for `POST`

- When the server opens an SSE stream from a `POST`, it should send an initial
  event ID with an empty data field so the client can reconnect with
  `Last-Event-ID` if needed.
- The stream may include server requests or notifications before the final
  response when required by the MCP transport contract.
- After the final response is sent, the stream should terminate.

## `GET /mcp`

### Request Rules

- Clients may issue `GET /mcp` to open an SSE stream for server-driven
  communication.
- Clients must advertise support for `text/event-stream` in the `Accept`
  header.
- If the client is reconnecting a previous stream, it may supply
  `Last-Event-ID`.

### Response Rules

- The server either returns `Content-Type: text/event-stream` or HTTP `405` if
  an SSE stream is not offered for that request condition.
- A `GET` stream may carry server requests and notifications.
- A `GET` stream must not carry a response to a client request unless it is
  resuming a previously interrupted stream associated with that request.

## Session Management

- The server may assign an `MCP-Session-Id` header on the response that carries
  a successful initialization result.
- If a session ID is issued, subsequent `GET`, `POST`, and termination requests
  for that session must include `MCP-Session-Id`.
- Requests missing a required session ID return HTTP `400`.
- Requests carrying a terminated or unknown session ID return HTTP `404`.
- The client may send `DELETE /mcp` with `MCP-Session-Id` to terminate a
  session; the server may respond with `405` if client-driven termination is
  not supported in this slice.

## Reconnect and Redelivery

- SSE events may include unique event IDs scoped to the owning stream.
- Reconnect attempts use `GET /mcp` with `Last-Event-ID`.
- If replay is supported, the server may replay events that belong to the same
  interrupted stream after the supplied event ID.
- The server must not replay or duplicate events that belong to a different
  stream or session.

## Multiple Connections

- A client may keep multiple SSE streams open at once.
- Each server-emitted JSON-RPC message is sent on only one connected stream.
- The server must not broadcast the same stream event to multiple active
  streams for the same session unless the transport contract explicitly
  requires distinct independently generated events.

## Transport Validation Rules

- Invalid or unsupported `MCP-Protocol-Version` values return HTTP `400`.
- Invalid origin validation returns HTTP `403`.
- Unsupported methods on `/mcp` return HTTP `405`.
- Unsupported media types or malformed request bodies return HTTP `400` or
  `415`, according to the transport failure.
- Error responses remain sanitized and must not expose stack traces, secrets,
  or internal transport state that is not required by the client.

## Stability Expectations

- The Cloud Run hosted entrypoint path remains `/mcp`.
- `/health` and `/ready` continue to provide liveness and readiness behavior
  from prior slices.
- Full protocol-native payload alignment is deferred to FND-010; this contract
  changes transport/session semantics first.

## Testable Assertions

- Contract tests can prove `POST /mcp` accepts the required header set and can
  return either JSON or SSE according to request type and server choice.
- Contract tests can prove `GET /mcp` either opens an SSE stream or returns
  `405` for unsupported stream conditions.
- Integration tests can prove session IDs are issued, reused, rejected when
  invalid, and isolated across concurrent sessions.
- Integration tests can prove event ordering, reconnect handling, and
  non-broadcast delivery across multiple streams.
- Hosted verification can prove local and Cloud Run transport behavior match
  for the same valid and invalid request flows.
