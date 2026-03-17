# Contract: FND-012 Hosted Runtime Migration for Streaming MCP

## Purpose

Define the externally visible hosted contract for migrating the MCP server to a
streaming-capable runtime without changing the logical MCP and operational
surface already accepted in earlier foundation slices.

## Scope

- Hosted route continuity for `/mcp`, `/health`, and `/ready`
- Startup and readiness behavior after runtime migration
- Local and Cloud Run launch expectations for the migrated runtime
- Preservation of hosted MCP request handling, streaming behavior, and
  observability across the runtime change

## Relationship to Prior Contracts

- This contract preserves the streamable transport rules in
  `/specs/009-mcp-streamable-http-transport/contracts/mcp-streamable-http-contract.md`.
- This contract preserves the MCP protocol behavior defined in
  `/specs/010-mcp-protocol-alignment/contracts/mcp-protocol-contract.md`.
- This contract preserves the tool discovery and invocation result behavior
  defined in
  `/specs/011-tool-metadata-result-alignment/contracts/tool-metadata-contract.md`.
- This contract changes the hosted serving runtime and startup behavior around
  those existing contracts; it does not define new MCP methods.

## Route Continuity

- The hosted service continues to expose `/mcp` as the MCP endpoint.
- The hosted service continues to expose `/health` for liveness checks.
- The hosted service continues to expose `/ready` for readiness checks.
- No client or operator route changes are required to use the migrated runtime.

## Runtime Startup and Readiness

- Process startup and readiness remain distinct observable states.
- `/health` reports that the process is alive even while the runtime is still
  initializing, unless the process itself cannot serve requests.
- `/ready` reports non-ready behavior until runtime startup completes and the
  service can accept MCP traffic safely.
- If runtime initialization fails or becomes degraded, `/ready` reflects that
  state without exposing secrets or internal stack traces.

## Hosted MCP Continuity

- Valid MCP traffic sent to `/mcp` continues to receive the same logical MCP
  transport and protocol behavior accepted before this migration.
- The runtime migration does not require a new session model, a new endpoint,
  or a new discovery/invocation contract.
- Concurrent client sessions remain isolated from one another during hosted
  streaming interactions.
- Runtime-level request failures continue to return stable, sanitized
  client-visible behavior.

## Launch and Deployment Expectations

- Operators have one documented local launch path for the migrated runtime.
- Operators have one documented Cloud Run launch path for the migrated runtime.
- Container and deployment assets align with the migrated runtime entrypoint.
- The previous launch command remains the rollback path until hosted migration
  verification succeeds.

## Verification Expectations

- Local verification proves liveness, readiness, MCP initialization, and at
  least one successful streaming MCP interaction.
- Cloud Run verification proves the same core behaviors against the deployed
  service.
- Verification evidence remains sufficient to correlate runtime health and MCP
  request handling for troubleshooting.

## Testable Assertions

- Contract tests can prove route continuity for `/mcp`, `/health`, and `/ready`
  after the runtime migration.
- Unit and integration tests can prove readiness remains false until runtime
  startup completes.
- Integration tests can prove concurrent streaming sessions remain isolated
  under the migrated runtime.
- Deployment-asset tests can prove the container and documented startup path
  use the migrated runtime consistently.
