# Local Hosted-Like Dependency Path

This directory contains the extra local dependency path required to exercise durable hosted-session behavior without provisioning cloud infrastructure. It complements the shared platform contract by preserving a provider-free local verification path.

## Minimal local runtime

The minimal local runtime does not require this directory. It can continue to run with:

- `MCP_ENVIRONMENT=dev`
- `MCP_SESSION_BACKEND=memory`

This remains the provider-free local path and must stay outside any provider adapter prerequisites.

## Hosted-like local verification

Use this path when you need Redis-backed session continuity locally.

1. Copy [`./.env.example`](./.env.example) to a local shell environment file if needed.
2. Start the shared-state dependency:
   `docker compose -f infrastructure/local/compose.yaml up -d`
3. Export the hosted-like local runtime values:
   - `MCP_ENVIRONMENT=dev`
   - `MCP_SESSION_BACKEND=redis`
   - `MCP_SESSION_STORE_URL=redis://127.0.0.1:6379/0`
   - `MCP_SESSION_DURABILITY_REQUIRED=true`
4. Start the app locally and run the verification flow against the local endpoint.
5. Stop the dependency when finished:
   `docker compose -f infrastructure/local/compose.yaml down`

Hosted-like local verification remains part of the shared platform contract, but it is still distinct from hosted cloud deployment.

If Redis is not running, hosted-like local verification should fail clearly and the minimal local runtime remains available.
