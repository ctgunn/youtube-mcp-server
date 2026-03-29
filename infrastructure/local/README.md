# Local Hosted-Like Dependency Path

This directory contains the extra local dependency path required to exercise durable hosted-session behavior without provisioning cloud infrastructure. It complements the shared platform contract by preserving a provider-free local verification path.

## What this directory is for

Use this directory when you want local development to behave more like the
hosted deployment, especially around MCP session continuity.

The important distinction is:

- minimal local runtime: fastest path, no shared session backend, best for day-to-day coding
- hosted-like local runtime: adds Redis so session behavior is closer to the
  real hosted deployment

This directory exists only for the second case. It is not required for the
normal local dev loop.

## Mental model

The application itself still runs locally on your machine. What this directory
adds is one supporting dependency: Redis.

That matters because the hosted server can keep MCP session state in a shared
backend. If you want to test:

- session continuation across requests
- replay behavior
- readiness behavior when durable sessions are required

then memory-only local mode is not enough. This hosted-like local path gives
you the missing shared session store without making you provision GCP first.

## Minimal local runtime

The minimal local runtime does not require this directory. It can continue to run with:

- `MCP_ENVIRONMENT=dev`
- `MCP_SESSION_BACKEND=memory`

This remains the provider-free local path and must stay outside any provider adapter prerequisites.

Choose this path when:

- you are building or debugging tool logic
- you do not need Redis-backed session durability
- you want the smallest amount of setup

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

Choose this path when:

- you are testing session creation and continuation
- you are testing reconnect and replay behavior
- you want `/ready` to reflect durable-session requirements
- you want local behavior that is closer to the hosted deployment model

If Redis is not running, hosted-like local verification should fail clearly and the minimal local runtime remains available.

## What does not change here

Even in hosted-like local mode:

- the app still runs locally
- Cloud Run is not involved
- GCP IAM and public reachability are not involved
- this is still a developer verification path, not a deployment path
