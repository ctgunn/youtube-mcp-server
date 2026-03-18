# Quickstart: Remote MCP Security and Transport Hardening

## Purpose

Verify the FND-013 hosted security contract locally before implementation tasks and again after implementation against a hosted environment.

## Prerequisites

- Repository dependencies installed with `python3 -m pip install -e .`
- Local runtime launched from the repository root
- A configured bearer token value for protected hosted MCP requests
- An allowed browser origin value for browser-style verification

## Task Targets

- Runtime config and security policy validation
- Protected hosted `/mcp` success path verification
- Missing-auth denial verification
- Disallowed-origin denial verification
- Hosted log correlation for denied requests

## Local Runtime Setup

Start the hosted service with development settings and explicit security inputs:

```bash
PYTHONPATH=src \
MCP_ENVIRONMENT=dev \
MCP_AUTH_TOKEN=local-dev-token \
MCP_ALLOWED_ORIGINS=http://localhost:3000 \
python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host 0.0.0.0 --port 8080
```

## Success Verification

Initialize an authenticated hosted MCP session:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Reuse the returned session for a protected tool call:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-call","method":"tools/call","params":{"name":"server_ping","arguments":{}}}' \
  http://127.0.0.1:8080/mcp
```

## Denial Verification

### Missing Authentication

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"req-no-auth","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: stable authentication denial before session creation or tool execution.

### Disallowed Browser Origin

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer local-dev-token' \
  -H 'Origin: https://unapproved.example' \
  -d '{"jsonrpc":"2.0","id":"req-origin-denied","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Expected result: stable origin denial before session creation or tool execution.

## Hosted Verification

Repeat the same success and denial checks against the Cloud Run service URL using the hosted bearer token and the production allowlisted origin.

Record evidence for:

- successful authenticated `initialize`
- successful authenticated follow-up request
- denied missing-auth request
- denied disallowed-origin request
- correlatable security decision record in hosted logs

## Regression Expectations

- `GET /health` remains available without authentication.
- `GET /ready` remains available without authentication and reports security configuration failures through readiness.
- Valid remote MCP clients continue to use the existing hosted `/mcp` route and session model, but now must satisfy the documented security requirements.
