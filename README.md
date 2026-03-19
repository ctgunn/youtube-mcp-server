# youtube-mcp-server
An MCP-compliant server that wraps the YouTube Data API and exposes searchable tools for use in OpenAI Agent Builder workflows, deployable via Google Cloud Run.

## Local dependency bootstrap

Install the hosted runtime dependencies from the repository root:

```bash
python3 -m pip install -e .
```

## Engineering workflow

Feature specification, planning, and implementation in this repository follow a
mandatory Red-Green-Refactor TDD workflow. Every feature plan and task list
must include explicit failing-test, minimal-pass, and refactor phases.

## Runtime configuration profiles

- `MCP_ENVIRONMENT` is required and must be one of `dev`, `staging`, or `prod`.
- Startup fails fast when required profile configuration is missing or invalid.
- `YOUTUBE_API_KEY` is required for `staging` and `prod`.
- `MCP_AUTH_TOKEN` is required for `staging` and `prod` hosted MCP access.
- `MCP_ALLOWED_ORIGINS` defines the browser origin allowlist for protected `/mcp` requests.
- `MCP_ALLOW_ORIGINLESS_CLIENTS` controls whether non-browser callers without `Origin` can proceed to authentication checks.
- `MCP_SESSION_BACKEND` selects the hosted session backend (`memory` for local-only or shared-memory tests, `redis` for durable hosted deployments).
- `MCP_SESSION_STORE_URL` points at the shared durable session backend when hosted session durability is required.
- `MCP_SESSION_DURABILITY_REQUIRED` forces `/ready` to fail unless a healthy shared session backend is available.
- `MCP_SESSION_TTL_SECONDS` controls how long an inactive hosted session remains reusable.
- `MCP_SESSION_REPLAY_TTL_SECONDS` controls how long reconnect replay history is retained for `Last-Event-ID` resume flows.
- `GET /health` returns liveness (`{"status":"ok"}`).
- `GET /ready` returns readiness based on startup config/secret validation.

## Browser-originated hosted MCP access

- Browser-originated access is explicitly supported only for `/mcp`.
- Approved browser clients must pass preflight before sending authenticated hosted MCP requests.
- Successful browser preflight for `/mcp` returns `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`.
- Successful approved-origin `/mcp` responses expose `MCP-Session-Id`, `MCP-Protocol-Version`, and `X-Stream-Id` so browser clients can continue hosted MCP flows.
- Denied origins and unsupported browser request patterns fail explicitly instead of relying on implicit browser blocking.

Representative browser preflight example:

```bash
curl -i -X OPTIONS \
  -H 'Origin: http://localhost:3000' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: authorization, content-type' \
  https://YOUR_SERVICE_URL/mcp
```

## Cloud Run foundation deployment

Required deployment inputs:

- `PROJECT_ID`
- `REGION`
- `SERVICE_NAME`
- `IMAGE_REFERENCE`
- `SERVICE_ACCOUNT_EMAIL`
- `MCP_SERVER_IMPLEMENTATION` (`uvicorn`)
- `MCP_ASGI_APP` (`mcp_server.cloud_run_entrypoint:app`)
- `MCP_ENVIRONMENT`
- `MCP_AUTH_REQUIRED`
- `MCP_ALLOWED_ORIGINS`
- `MCP_ALLOW_ORIGINLESS_CLIENTS`
- `MIN_INSTANCES`
- `MAX_INSTANCES`
- `CONCURRENCY`
- `TIMEOUT_SECONDS`
- `SECRET_REFERENCES` (`YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN` are required for `staging` and `prod`)

Execute the deployment workflow with explicit revision settings:

```bash
PROJECT_ID=example-project \
REGION=us-central1 \
SERVICE_NAME=youtube-mcp-server \
IMAGE_REFERENCE=us-docker.pkg.dev/example-project/apps/youtube-mcp-server:sha \
SERVICE_ACCOUNT_EMAIL=youtube-mcp-server@example-project.iam.gserviceaccount.com \
MCP_SERVER_IMPLEMENTATION=uvicorn \
MCP_ASGI_APP=mcp_server.cloud_run_entrypoint:app \
MCP_ENVIRONMENT=staging \
MCP_AUTH_REQUIRED=true \
MCP_ALLOWED_ORIGINS=https://chat.openai.com \
MCP_ALLOW_ORIGINLESS_CLIENTS=true \
MCP_SESSION_BACKEND=redis \
MCP_SESSION_STORE_URL=redis://REDIS_HOST:6379/0 \
MCP_SESSION_DURABILITY_REQUIRED=true \
MIN_INSTANCES=0 \
MAX_INSTANCES=2 \
CONCURRENCY=20 \
TIMEOUT_SECONDS=180 \
SECRET_REFERENCES=YOUTUBE_API_KEY,MCP_AUTH_TOKEN \
bash scripts/deploy_cloud_run.sh
```

The deployment workflow now returns a JSON deployment record containing the
deployment outcome, revision name, hosted service URL, and runtime settings
summary. Save that record and use it as the handoff into hosted verification.
The runtime settings summary includes `serverImplementation=uvicorn` and
`appModule=mcp_server.cloud_run_entrypoint:app`.

Example:

```bash
PROJECT_ID=example-project \
REGION=us-central1 \
SERVICE_NAME=youtube-mcp-server \
IMAGE_REFERENCE=us-docker.pkg.dev/example-project/apps/youtube-mcp-server:sha \
SERVICE_ACCOUNT_EMAIL=youtube-mcp-server@example-project.iam.gserviceaccount.com \
MCP_SERVER_IMPLEMENTATION=uvicorn \
MCP_ASGI_APP=mcp_server.cloud_run_entrypoint:app \
MCP_ENVIRONMENT=staging \
MCP_AUTH_REQUIRED=true \
MCP_ALLOWED_ORIGINS=https://chat.openai.com \
MCP_ALLOW_ORIGINLESS_CLIENTS=true \
MCP_SESSION_BACKEND=redis \
MCP_SESSION_STORE_URL=redis://REDIS_HOST:6379/0 \
MCP_SESSION_DURABILITY_REQUIRED=true \
MIN_INSTANCES=0 \
MAX_INSTANCES=2 \
CONCURRENCY=20 \
TIMEOUT_SECONDS=180 \
SECRET_REFERENCES=YOUTUBE_API_KEY,MCP_AUTH_TOKEN \
bash scripts/deploy_cloud_run.sh > artifacts/cloud-run-deployment.json
```

Verify the hosted foundation revision after deployment:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --auth-token "$MCP_AUTH_TOKEN" \
  --evidence-file artifacts/cloud-run-verification.txt
```

The hosted verifier now exercises the streamable MCP transport rather than the
older bare `POST /mcp` flow. It performs `initialize`, captures the returned
`MCP-Session-Id`, reuses that session for subsequent `POST` and `GET` MCP
requests, validates reconnect behavior with `Last-Event-ID`, and accepts both
`application/json` and `text/event-stream` responses as required by the hosted
transport contract.

Manual streamable MCP verification examples:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  https://YOUR_SERVICE_URL/mcp
```

Use the returned `MCP-Session-Id` for subsequent requests:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-call","method":"tools/call","params":{"name":"server_ping","arguments":{}}}' \
  https://YOUR_SERVICE_URL/mcp
```

Successful hosted JSON responses now use protocol-native MCP bodies:

```json
{
  "jsonrpc": "2.0",
  "id": "req-call",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"status\":\"ok\",\"timestamp\":\"...\"}",
        "structuredContent": {
          "status": "ok",
          "timestamp": "..."
        }
      }
    ],
    "isError": false
  }
}
```

Tool discovery responses now include complete baseline tool metadata, including
`inputSchema`, so hosted MCP clients can construct valid calls from `tools/list`
without separate tool documentation.

Representative hosted `tools/list` output still includes the deep research
tools used in earlier foundation slices:

```json
{
  "jsonrpc": "2.0",
  "id": "req-list",
  "result": {
    "tools": [
      {"name":"search","description":"Discover relevant sources for deep research workflows."},
      {"name":"fetch","description":"Retrieve a selected source in consumable content form."}
    ]
  }
}
```

Hosted session durability verification expects the hosted tool catalog to
remain discoverable and then validates session continuation through the same
protected MCP entrypoint.

Representative hosted `POST` continuation example:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-search","method":"tools/call","params":{"name":"search","arguments":{"query":"remote MCP research","pageSize":1}}}' \
  https://YOUR_SERVICE_URL/mcp
```

Representative hosted reconnect example:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -H 'Last-Event-ID: STREAM_EVENT_ID' \
  https://YOUR_SERVICE_URL/mcp
```

Open or resume an SSE stream without a replay cursor:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -H 'Last-Event-ID: STREAM_EVENT_ID' \
  https://YOUR_SERVICE_URL/mcp
```

Protected `/mcp` requests now follow these hosted security rules:

- Browser callers that send `Origin` must match `MCP_ALLOWED_ORIGINS`.
- Non-browser callers may omit `Origin` only when `MCP_ALLOW_ORIGINLESS_CLIENTS=true`.
- Protected `/mcp` requests must send `Authorization: Bearer ...`.
- Missing auth returns `401`, denied origin returns `403`, and malformed security headers return `400`.

You can still provide `--service-url`, `--revision-name`, `--service-name`,
`--runtime-identity`, `--min-instances`, `--max-instances`, `--concurrency`,
and `--timeout-seconds` directly when a deployment record file is not available.

Hosted runtime requests emit structured JSON log events to runtime stdout/stderr
with `timestamp`, `severity`, `requestId`, `path`, `status`, `latencyMs`, and
`toolName` when the request reaches tool dispatch.

Start the migrated hosted runtime locally with the ASGI entrypoint:

```bash
PYTHONPATH=src python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host 0.0.0.0 --port 8080
```

The verification output must record pass/fail results for:

- `liveness`
- `readiness`
- `initialize`
- `list-tools`
- `session-post-continuation`
- `session-get-continuation`
- `session-reconnect`
- `session-invalid`
- `browser-preflight-approved`
- `browser-request-approved`
- `browser-origin-denied`
- `browser-request-unsupported`
