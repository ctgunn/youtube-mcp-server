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
- `GET /healthz` returns liveness (`{"status":"ok"}`).
- `GET /readyz` returns readiness based on startup config/secret validation.

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

Render the deployment command with explicit revision settings:

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

Verify the hosted foundation revision after deployment:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --service-url https://example-service-uc.a.run.app \
  --revision-name youtube-mcp-server-00001 \
  --service-name youtube-mcp-server \
  --runtime-identity youtube-mcp-server@example-project.iam.gserviceaccount.com \
  --min-instances 0 \
  --max-instances 2 \
  --concurrency 20 \
  --timeout-seconds 180 \
  --evidence-file artifacts/cloud-run-verification.txt
```

The verification output must record pass/fail results for:

- `liveness`
- `readiness`
- `initialize`
- `list-tools`
- `baseline-tool-call`
