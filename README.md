# youtube-mcp-server
An MCP-compliant server that wraps the YouTube Data API and exposes searchable tools for use in OpenAI Agent Builder workflows, deployable via Google Cloud Run.

## Engineering workflow

Feature specification, planning, and implementation in this repository follow a
mandatory Red-Green-Refactor TDD workflow. Every feature plan and task list
must include explicit failing-test, minimal-pass, and refactor phases.

## Runtime configuration profiles

- `MCP_ENVIRONMENT` is required and must be one of `dev`, `staging`, or `prod`.
- Startup fails fast when required profile configuration is missing or invalid.
- `YOUTUBE_API_KEY` is required for `staging` and `prod`.
- `GET /health` returns liveness (`{"status":"ok"}`).
- `GET /ready` returns readiness based on startup config/secret validation.

## Cloud Run foundation deployment

Required deployment inputs:

- `PROJECT_ID`
- `REGION`
- `SERVICE_NAME`
- `IMAGE_REFERENCE`
- `SERVICE_ACCOUNT_EMAIL`
- `MCP_ENVIRONMENT`
- `MIN_INSTANCES`
- `MAX_INSTANCES`
- `CONCURRENCY`
- `TIMEOUT_SECONDS`
- `SECRET_REFERENCES` (`YOUTUBE_API_KEY` is required for `staging` and `prod`)

Execute the deployment workflow with explicit revision settings:

```bash
PROJECT_ID=example-project \
REGION=us-central1 \
SERVICE_NAME=youtube-mcp-server \
IMAGE_REFERENCE=us-docker.pkg.dev/example-project/apps/youtube-mcp-server:sha \
SERVICE_ACCOUNT_EMAIL=youtube-mcp-server@example-project.iam.gserviceaccount.com \
MCP_ENVIRONMENT=staging \
MIN_INSTANCES=0 \
MAX_INSTANCES=2 \
CONCURRENCY=20 \
TIMEOUT_SECONDS=180 \
SECRET_REFERENCES=YOUTUBE_API_KEY \
bash scripts/deploy_cloud_run.sh
```

The deployment workflow now returns a JSON deployment record containing the
deployment outcome, revision name, hosted service URL, and runtime settings
summary. Save that record and use it as the handoff into hosted verification.

Example:

```bash
PROJECT_ID=example-project \
REGION=us-central1 \
SERVICE_NAME=youtube-mcp-server \
IMAGE_REFERENCE=us-docker.pkg.dev/example-project/apps/youtube-mcp-server:sha \
SERVICE_ACCOUNT_EMAIL=youtube-mcp-server@example-project.iam.gserviceaccount.com \
MCP_ENVIRONMENT=staging \
MIN_INSTANCES=0 \
MAX_INSTANCES=2 \
CONCURRENCY=20 \
TIMEOUT_SECONDS=180 \
SECRET_REFERENCES=YOUTUBE_API_KEY \
bash scripts/deploy_cloud_run.sh > artifacts/cloud-run-deployment.json
```

Verify the hosted foundation revision after deployment:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --evidence-file artifacts/cloud-run-verification.txt
```

The hosted verifier now exercises the streamable MCP transport rather than the
older bare `POST /mcp` flow. It performs `initialize`, captures the returned
`MCP-Session-Id`, reuses that session for subsequent MCP requests, and accepts
both `application/json` and `text/event-stream` responses as required by the
hosted transport contract.

Manual streamable MCP verification examples:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  https://YOUR_SERVICE_URL/mcp
```

Use the returned `MCP-Session-Id` for subsequent requests:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
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

Open or resume an SSE stream:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -H 'Last-Event-ID: STREAM_EVENT_ID' \
  https://YOUR_SERVICE_URL/mcp
```

You can still provide `--service-url`, `--revision-name`, `--service-name`,
`--runtime-identity`, `--min-instances`, `--max-instances`, `--concurrency`,
and `--timeout-seconds` directly when a deployment record file is not available.

Hosted runtime requests emit structured JSON log events to runtime stdout/stderr
with `timestamp`, `severity`, `requestId`, `path`, `status`, `latencyMs`, and
`toolName` when the request reaches tool dispatch.

The verification output must record pass/fail results for:

- `liveness`
- `readiness`
- `initialize`
- `list-tools`
- `baseline-tool-call`
