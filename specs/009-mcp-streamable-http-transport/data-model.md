# Data Model: FND-009 MCP Streamable HTTP Transport

## Entity: HostedMCPSession
Description: The in-memory server record representing one logical hosted MCP
session established through the streamable HTTP transport.

Fields:
- `sessionId` (string, required): Cryptographically strong visible-ASCII
  session identifier returned to the client after initialization.
- `protocolVersion` (string, required): MCP protocol version associated with
  the session.
- `createdAt` (string, required): Session creation timestamp.
- `lastActivityAt` (string, required): Timestamp of the most recent accepted
  request or stream activity for the session.
- `state` (string, required): `pending`, `active`, `closing`, or `closed`.
- `clientMetadata` (object, optional): Sanitized client identity information
  learned during initialization.
- `streamIds` (list of strings, required): Active or resumable stream IDs owned
  by the session.

Validation rules:
- `sessionId` MUST be unique among active sessions.
- `protocolVersion` MUST be one the server recognizes for the streamable
  transport.
- Requests for a closed session MUST not be accepted as active session traffic.

## Entity: StreamChannel
Description: The in-memory record describing one SSE stream owned by a hosted
MCP session.

Fields:
- `streamId` (string, required): Unique identifier for one SSE channel.
- `sessionId` (string, required): Owning session identifier.
- `originMethod` (string, required): `GET` or `POST`, indicating how the stream
  was initiated.
- `state` (string, required): `open`, `idle`, `reconnecting`, `completed`, or
  `closed`.
- `createdAt` (string, required): Stream creation timestamp.
- `lastEventId` (string, optional): Most recent emitted SSE event ID.
- `retryMs` (integer, optional): Suggested reconnect delay when the server
  closes the connection without ending the stream.
- `pendingResponseId` (string, optional): Request identifier for the
  client-originated MCP request whose response is expected on this stream.

Validation rules:
- A `streamId` MUST belong to exactly one `sessionId`.
- A completed or closed stream MUST NOT receive new events.
- `pendingResponseId` MUST be absent for unsolicited `GET` streams unless the
  stream is resuming an earlier request.

## Entity: StreamEvent
Description: A single SSE event emitted on a streamable HTTP channel.

Fields:
- `eventId` (string, required): Unique per-stream event cursor value.
- `streamId` (string, required): Target stream.
- `eventType` (string, required): `message`, `retry`, `keepalive`, or
  transport-specific control event.
- `payloadClass` (string, required): `jsonrpc_response`, `jsonrpc_request`,
  `jsonrpc_notification`, or `empty`.
- `payload` (object or null, required): Event body content when present.
- `createdAt` (string, required): Event emission timestamp.
- `deliveryState` (string, required): `queued`, `sent`, `replayed`, or
  `dropped`.

Validation rules:
- `eventId` MUST be unique within the owning stream.
- Events replayed after reconnect MUST belong to the same `streamId` that the
  reconnect cursor references.
- A `jsonrpc_response` event MUST only appear on a `GET` stream when resuming a
  prior stream initiated by client request.

## Entity: TransportRequestContext
Description: The normalized hosted transport input used to validate and route a
`GET` or `POST` request at the MCP endpoint.

Fields:
- `method` (string, required): HTTP method used by the client.
- `path` (string, required): Hosted endpoint path.
- `acceptTypes` (list of strings, required): Normalized `Accept` header values.
- `contentType` (string, optional): Normalized request content type.
- `protocolVersion` (string, optional): MCP protocol version header value.
- `sessionId` (string, optional): Session header value.
- `lastEventId` (string, optional): Resume cursor from reconnect attempts.
- `originState` (string, required): `trusted`, `missing`, or `rejected`.
- `bodyClass` (string, required): `json_request`, `json_notification`,
  `json_response`, `batch`, `empty`, or `malformed`.

Validation rules:
- `POST` requests MUST advertise support for both `application/json` and
  `text/event-stream`.
- `GET` requests for streaming MUST advertise support for `text/event-stream`.
- Invalid protocol-version or invalid-session combinations MUST produce a
  transport failure before request routing.

## Entity: SessionOutcome
Description: The client-visible result of a transport interaction after request
validation and session resolution.

Fields:
- `outcomeClass` (string, required): `json_response`, `sse_stream`,
  `accepted_no_body`, `bad_request`, `forbidden`, `not_found`, `method_not_allowed`,
  or `session_closed`.
- `statusCode` (integer, required): HTTP status returned for the interaction.
- `sessionState` (string, optional): Resulting session state after handling the
  request.
- `streamState` (string, optional): Resulting stream state after handling the
  request.
- `responseMediaType` (string, optional): `application/json`,
  `text/event-stream`, or absent when no body is returned.

Validation rules:
- `accepted_no_body` MUST map to HTTP `202`.
- `sse_stream` MUST map to `text/event-stream`.
- Requests for expired or terminated sessions MUST not be reported as normal
  successful session traffic.

## Relationships

- `HostedMCPSession` owns one or more `StreamChannel` records.
- `StreamChannel` emits ordered `StreamEvent` records.
- `TransportRequestContext` resolves to one `SessionOutcome`.
- `SessionOutcome` may create, reuse, reconnect, complete, or close a
  `StreamChannel`.

## State Transitions

1. Initialization request accepted -> `HostedMCPSession.state` moves from
   `pending` to `active` and may issue `sessionId`.
2. `GET /mcp` stream opened -> `StreamChannel.state` becomes `open`.
3. `POST /mcp` request accepted for streaming -> response stream created or
   reused and moves to `open`.
4. Events emitted -> `StreamEvent.deliveryState` moves from `queued` to `sent`.
5. Disconnect with resumable stream -> `StreamChannel.state` becomes
   `reconnecting`.
6. Reconnect with valid `Last-Event-ID` -> eligible events move to `replayed`
   and stream returns to `open`.
7. Final response delivered or session explicitly terminated -> stream moves to
   `completed` or `closed`; session may move to `closing` then `closed`.
