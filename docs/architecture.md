# Architecture overview

`youtube-mcp-server` is a remote MCP server, not a library that other
applications import. MCP clients connect to its hosted HTTP endpoint, send
messages to `/mcp`, discover available tools, and invoke them over the network.

## System at a glance

The server provides:

- MCP discovery and request handling
- YouTube Data API tools plus foundational retrieval tools
- Streamable HTTP sessions, event replay, and durable hosted session support
- Health, readiness, security, and observability behavior suitable for Cloud
  Run-style hosting

The repository separates the system into five concerns:

| Concern | Responsibility |
| --- | --- |
| Transport | HTTP routes, MCP envelopes, sessions, streaming, and replay |
| Tool layer | Discovery, validation, dispatch, and stable result contracts |
| Integrations | YouTube Data API resource wrappers and response normalization |
| Runtime | Configuration, logging, metrics, health, readiness, and security |
| Platform | Local dependency assets and provider-specific hosted infrastructure |

## Request lifecycle

1. A client reaches `/mcp` with an MCP request and the required authorization.
2. The transport validates the envelope and establishes or resumes a session.
3. The dispatcher resolves the requested tool and validates its inputs.
4. The tool invokes the integration layer and receives a normalized result or
   protocol-native error.
5. The server records safe observability data and returns the MCP response.
6. Streaming clients receive replayable events when the selected transport mode
   requires them.

Hosted requests can use Redis-backed state so sessions continue across Cloud
Run instances. Local development defaults to in-memory state; the optional
hosted-like local path exercises the durable-session model without cloud
provisioning.

## One request lifecycle

An MCP client begins with `initialize`, receives server capabilities, and then
uses tool discovery before invoking a named tool. HTTP clients retain the
session identifier supplied by the server (`MCP-Session-Id`). Streaming clients
may receive `text/event-stream` responses and reconnect with `Last-Event-ID`.

Remote deployments enforce the configured authentication policy. Clients send
the configured credential with `Authorization: Bearer ...`; operators must not
place that value in example commands, documentation, or release evidence.

## Runtime behavior

- `/health` reports whether the process is alive.
- `/ready` reports whether the configured runtime dependencies are available.
- Hosted deployments use Secret Manager-backed environment injection when
  `MCP_SECRET_ACCESS_MODE=secret_manager_env`.
- `MCP_SECRET_REFERENCE_NAMES` identifies secret names, not secret values.
- `MCP_SESSION_CONNECTIVITY_MODEL` selects the supported hosted session path;
  `MCP_SESSION_STORE_URL` is supplied through the infrastructure handoff.

For complete configuration profiles and browser-origin policy, see
[runtime and security configuration](./engineering.md#runtime-and-security-configuration).
