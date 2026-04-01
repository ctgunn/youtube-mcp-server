# youtube-mcp-server
An MCP-compliant server that wraps the YouTube Data API and exposes searchable tools for use in OpenAI Agent Builder workflows. The current primary hosted provider adapter targets Google Cloud Run, while the shared platform contract keeps the hosted deployment model portable across providers.

## What this is

At a high level, this repository contains a remote MCP server. Other
applications do not import this code directly. Instead, they connect to the
hosted HTTP endpoint, send MCP messages to `/mcp`, discover the available
tools, and call those tools over the network.

Today the server includes:

- baseline server tools such as `server_ping`, `server_info`, and `server_list_tools`
- foundational retrieval tools such as `search` and `fetch`
- hosted session management for streamable MCP over HTTP
- health, readiness, security, and observability behavior for Cloud Run-style hosting

If you are new to the repository, the sections below explain the server in the
same layered way a human would usually learn it: from very high level down to
the request-by-request details.

## How to read this README

This README is intentionally layered.

If you are trying to get the server running for the first time, start with the
setup sections immediately below:

- `Setup from scratch: local` gets the server running on your machine as fast
  as possible.
- `Setup from scratch: hosted on GCP` walks through the first full hosted
  deployment path end to end.

After that, come back to the architecture sections when you want to understand
how the server actually works.

You can think about the architecture at five levels:

- 100 ft: what the server is for
- 30 ft: how another application uses it
- 10 ft: which modules are responsible for which jobs
- ground level: what happens during a real request
- underground: where sessions, streams, validation, and tool execution actually live

The rest of this README keeps the detailed deployment and verification material
that already existed, but this section is intended to make the big picture much
easier to follow first.

## Setup From Scratch: Local

Use this path when you want to run the MCP server on your own machine for
development or manual testing before pushing code.

### What you need

- `python3` 3.11 or newer
- `pip`
- `make`
- `docker` and `docker compose` if you want the hosted-like Redis-backed path

### 1. Open the repository

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the project

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

### 4. Review the local environment file

The local runtime path reads defaults from `.env.local`.

For the first run, the important ideas are:

- local development uses `MCP_ENVIRONMENT=dev`
- the default local path uses `MCP_SESSION_BACKEND=memory`
- the default local path does not require hosted cloud infrastructure

### 5. Start the server locally

The simplest local startup command is:

```bash
make dev
```

That command uses `scripts/dev_local.sh`, loads `.env.local`, and starts the
ASGI app locally.

### 6. Verify that the local server is healthy

In a second terminal:

```bash
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/ready
```

You want both endpoints to return `200`.

### 7. Verify the MCP handshake locally

Initialize:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"local-test","version":"1.0.0"}}}' \
  http://127.0.0.1:8080/mcp
```

Copy the returned `MCP-Session-Id` header, then use it to list tools:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: YOUR_SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-list","method":"tools/list","params":{}}' \
  http://127.0.0.1:8080/mcp
```

Then call a baseline tool:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: YOUR_SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-call","method":"tools/call","params":{"name":"server_ping","arguments":{}}}' \
  http://127.0.0.1:8080/mcp
```

### 8. Run the hosted-like local path when you need Redis-backed sessions

This path is useful when you want local behavior that is closer to hosted
session durability.

Start the local Redis dependency:

```bash
docker compose -f infrastructure/local/compose.yaml up -d
```

Start the app in hosted-like mode:

```bash
make dev-hosted
```

When you are done:

```bash
make dev-down
```

This hosted-like local path keeps the same app entrypoint while switching the
session backend to Redis-backed settings under local control.

## Setup From Scratch: Hosted On GCP

Use this path when you want a real hosted MCP endpoint that other applications
can reach over the network.

### What you need

- `gcloud`
- `terraform`
- `docker`
- `python3`
- a GCP project you can administer

### 1. Authenticate to Google Cloud

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable the required Google Cloud APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com \
  compute.googleapis.com \
  iam.googleapis.com
```

### 3. Create the Artifact Registry repository if you do not already have one

```bash
gcloud artifacts repositories create apps \
  --repository-format=docker \
  --location=us-central1
```

### 4. Create the runtime secrets in Secret Manager

The hosted runtime expects operator-managed secret values for:

- `YOUTUBE_API_KEY`
- `MCP_AUTH_TOKEN`

Create them if this is your first setup:

```bash
printf 'YOUR_REAL_YOUTUBE_API_KEY' | gcloud secrets create YOUTUBE_API_KEY --data-file=-
printf 'YOUR_REAL_MCP_AUTH_TOKEN' | gcloud secrets create MCP_AUTH_TOKEN --data-file=-
```

If they already exist, add new versions instead:

```bash
printf 'YOUR_REAL_YOUTUBE_API_KEY' | gcloud secrets versions add YOUTUBE_API_KEY --data-file=-
printf 'YOUR_REAL_MCP_AUTH_TOKEN' | gcloud secrets versions add MCP_AUTH_TOKEN --data-file=-
```

### 5. Review the deployment operator inputs

The repository root `.env` is the operator-oriented deployment input file for
the supported Cloud Run path. Review and set the values you actually intend to
deploy, especially:

- `PROJECT_ID`
- `REGION`
- `SERVICE_NAME`
- `SERVICE_ACCOUNT_EMAIL`
- `MCP_ENVIRONMENT`
- `PUBLIC_INVOCATION_INTENT`
- `MCP_ALLOWED_ORIGINS`

For a real remote MCP deployment, `MCP_ENVIRONMENT=staging` and
`PUBLIC_INVOCATION_INTENT=public_remote_mcp` are the usual starting point.

### 6. Create the Terraform variable file for your environment

```bash
cp infrastructure/gcp/terraform.tfvars.example infrastructure/gcp/staging.tfvars
```

Then edit `infrastructure/gcp/staging.tfvars` with the real values for your
environment, including:

- project and region
- service name and environment
- public invocation intent
- allowed origins
- managed VPC, subnet, and VPC connector names/CIDRs for durable sessions

### 7. Provision the hosted infrastructure

Initialize Terraform:

```bash
terraform -chdir=infrastructure/gcp init
```

Review the plan:

```bash
terraform -chdir=infrastructure/gcp plan -var-file=staging.tfvars
```

Apply the infrastructure:

```bash
terraform -chdir=infrastructure/gcp apply -var-file=staging.tfvars
```

This hosted infrastructure step is what creates and wires the platform around
the app, including the Cloud Run foundation, durable-session Redis path, and
the managed network resources needed for the supported GCP session-connectivity
model.

### 8. Export the Terraform outputs for the deploy handoff

```bash
mkdir -p artifacts
terraform -chdir=infrastructure/gcp output -json > artifacts/gcp-foundation-outputs.json
```

### 9. Build and push the container image

Authenticate Docker to Artifact Registry:

```bash
gcloud auth configure-docker us-docker.pkg.dev --quiet
```

Build the image:

```bash
docker build -t us-docker.pkg.dev/YOUR_PROJECT_ID/apps/youtube-mcp-server:manual-001 .
```

Push it:

```bash
docker push us-docker.pkg.dev/YOUR_PROJECT_ID/apps/youtube-mcp-server:manual-001
```

### 10. Deploy the application through the repository deploy script

```bash
INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json \
IMAGE_REFERENCE=us-docker.pkg.dev/YOUR_PROJECT_ID/apps/youtube-mcp-server:manual-001 \
DEPLOYMENT_RECORD_FILE=artifacts/cloud-run-deployment.json \
bash scripts/deploy_cloud_run.sh
```

This is the supported application rollout path. It uses the Terraform outputs
as the handoff from infrastructure reconciliation into Cloud Run deployment.

### 11. Verify the hosted deployment

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --auth-token "YOUR_REAL_MCP_AUTH_TOKEN" \
  --evidence-file artifacts/cloud-run-verification.txt \
  --summary-file artifacts/cloud-run-verification.json
```

Do not treat the deployment as complete until hosted verification passes.

### 12. Enable push-triggered deployment after the manual path works once

The repository now defines the primary automated rollout in `cloudbuild.yaml`.
Once the manual path above works:

- create or update your Cloud Build trigger for `main`
- point it at `cloudbuild.yaml`
- set the required substitutions for project, region, service name, Artifact
  Registry repository, Terraform var file, and service account
- ensure the Cloud Build service account can manage the infrastructure and read
  the required secret references

After that, a push to `main` should run:

1. tests and lint
2. image build and publish
3. Terraform apply
4. deploy through `scripts/deploy_cloud_run.sh`
5. hosted verification through `scripts/verify_cloud_run_foundation.py`

## 100 Ft View

This server is a network-accessible toolbox.

An MCP-capable client such as OpenAI or another remote MCP consumer talks to
your server over HTTP. The client asks:

- who are you?
- what tools do you have?
- please run this tool for me

Your server answers those questions using the MCP protocol.

In practical terms, the server has four main responsibilities:

1. Start with the correct runtime configuration.
2. Accept HTTP requests on `/health`, `/ready`, and `/mcp`.
3. Maintain MCP session state so a client can continue talking to the same logical session.
4. Route tool requests to Python handlers and return MCP-shaped results.

## 30 Ft View

Another application uses this server through a hosted MCP flow:

1. The client sends `initialize` to `POST /mcp`.
2. If the request is allowed and valid, the server returns MCP capabilities and
   an `MCP-Session-Id` header.
3. The client reuses that session ID on later requests such as `tools/list` and
   `tools/call`.
4. The server validates the request, finds the correct tool, runs it, and
   returns a result in MCP format.
5. If the client needs replay or stream continuation, it can reconnect with the
   same session using `GET /mcp` and `Last-Event-ID`.

The most important thing to remember is that clients interact with this server
through HTTP plus JSON-RPC/MCP messages. They are not calling Python functions
directly.

## 10 Ft View

These modules are the main moving parts:

- [src/mcp_server/cloud_run_entrypoint.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/cloud_run_entrypoint.py)
  This is the hosted front door. It receives raw HTTP requests and turns them
  into hosted MCP behavior.
- [src/mcp_server/app.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/app.py)
  This creates the transport object and loads runtime configuration.
- [src/mcp_server/config.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/config.py)
  This reads environment variables and defines runtime settings such as auth,
  session backend, TTLs, and readiness expectations.
- [src/mcp_server/transport/http.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/http.py)
  This classifies requests, owns hosted route behavior, and routes `/mcp`
  payloads into the MCP protocol layer.
- [src/mcp_server/security.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/security.py)
  This decides whether a request is allowed based on bearer auth, origin
  handling, and browser preflight rules.
- [src/mcp_server/transport/streaming.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/streaming.py)
  This manages sessions, streams, replay windows, and SSE payload encoding.
- [src/mcp_server/protocol/methods.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/protocol/methods.py)
  This implements the MCP methods supported by the server, such as
  `initialize`, `tools/list`, and `tools/call`.
- [src/mcp_server/tools/dispatcher.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py)
  This is the registry and dispatcher for tools.
- [src/mcp_server/tools/retrieval.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/retrieval.py)
  This is one current tool module that implements `search` and `fetch`.
- [src/mcp_server/transport/session_store.py](/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/transport/session_store.py)
  This defines where hosted session state is stored: in memory or in Redis.

## Ground Level: One Request Lifecycle

Here is the normal happy-path lifecycle for a hosted client:

1. Cloud Run receives an HTTPS request.
2. The ASGI entrypoint in `cloud_run_entrypoint.py` passes the request to
   `execute_hosted_request(...)`.
3. The request is classified by path, method, content type, and body shape.
4. `/health` and `/ready` are answered directly by the hosted transport.
5. `/mcp` requests go through security checks first.
6. If the MCP method is `initialize`, the protocol layer validates it and the
   server creates a new session only if initialize succeeds.
7. The server returns an `MCP-Session-Id`, which the client must reuse on later
   requests.
8. Follow-up `tools/list` and `tools/call` requests are routed through the
   dispatcher.
9. The dispatcher validates tool arguments against the published schema and
   calls the correct Python handler.
10. The result is wrapped into an MCP response and returned as JSON or
    streamable HTTP/SSE depending on the flow.

## Underground: What lives under the surface

The server has a few pieces of hidden plumbing that matter a lot:

### Sessions

- A successful `initialize` creates a hosted MCP session.
- The session ID is returned in the `MCP-Session-Id` response header.
- Follow-up requests must include that header.
- If a session is missing or expired, the request fails and the client is
  expected to initialize again.

### Session storage

Session state can live in one of two places:

- memory: useful for local development and simple single-process workflows
- Redis: useful for durable/shared hosted session continuity

The session backend is selected by `MCP_SESSION_BACKEND` and
`MCP_SESSION_STORE_URL`.

### Streaming and replay

This server supports streamable HTTP MCP behavior:

- a client can ask for `text/event-stream`
- the server can return SSE instead of a plain JSON body
- the client can reconnect with `Last-Event-ID`
- the server can replay missed events as long as they are still within the
  replay window

The replay window is controlled by `MCP_SESSION_REPLAY_TTL_SECONDS`.

### Tool discovery and execution

Each tool has:

- a name
- a description
- an `inputSchema`
- a Python handler

That means a client can discover tools dynamically through `tools/list`, then
construct a valid `tools/call` request without knowing Python details.

## Short Example

In plain language, a client does something like this:

1. Send `initialize`.
2. Receive capabilities and `MCP-Session-Id`.
3. Send `tools/list`.
4. Read the published tool schemas.
5. Send `tools/call` for a tool such as `search` or `fetch`.
6. Receive the tool result in MCP format.

That is the core of how this server works. The sections below cover the exact
runtime configuration, deployment, verification, and hosted contract details.

## Local dependency bootstrap

The setup sections above are the recommended first-time path. This section and
the ones that follow are the deeper runtime and operator reference details.

Install the hosted runtime dependencies from the repository root:

```bash
python3 -m pip install -e .
```

## Minimal local runtime path

Use the minimal local runtime path when you only need local development and do
not need Redis-backed session durability. `bash scripts/dev_local.sh` is the
canonical local startup entry point, and it loads the local runtime defaults
from `.env.local` automatically.

```bash
bash scripts/dev_local.sh
```

This path does not require cloud provisioning or local infrastructure under
`infrastructure/`, and it remains outside any provider adapter prerequisites in the shared platform contract.

Local runtime verification:

- `.env.local` is the dedicated local runtime defaults file for this path.
- The script fails immediately if `.env.local` is missing and tells you to restore the local runtime defaults file.
- Successful startup means the app is running with the baseline local profile and no hosted deployment-only inputs.

Hosted deployment-only inputs remain in hosted deployment documentation and `.env.example`; they are not required for the minimal local runtime path.

## Hosted-like local verification path

Use the hosted-like local verification path when you need to exercise the same
Redis-backed session settings used by the hosted deployment without provisioning
cloud infrastructure first:

```bash
docker compose -f infrastructure/local/compose.yaml up -d
```

```bash
LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh
```

When finished:

```bash
docker compose -f infrastructure/local/compose.yaml down
```

These local and hosted-like local workflows are execution modes of the shared platform contract. They remain separate from the primary hosted provider adapter and any future provider adapter.

Hosted-like local verification keeps the same startup entry point but changes the local session profile:

- baseline local values still come from `.env.local`
- hosted-like local overrides are documented in `infrastructure/local/.env.example`
- the Redis bootstrap path must be running before `LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh`
- if the durable-session dependency is unavailable, start `docker compose -f infrastructure/local/compose.yaml up -d` and retry

## Engineering workflow

Feature specification, planning, and implementation in this repository follow a
mandatory Red-Green-Refactor TDD workflow. Every feature plan and task list
must include explicit failing-test, minimal-pass, and refactor phases. Work is
not complete until the full repository test suite has been run after the final
code changes and every test is passing.

## Runtime configuration profiles

- `MCP_ENVIRONMENT` is required and must be one of `dev`, `staging`, or `prod`.
- Startup fails fast when required profile configuration is missing or invalid.
- `YOUTUBE_API_KEY` is required for `staging` and `prod`.
- `MCP_AUTH_TOKEN` is required for `staging` and `prod` hosted MCP access.
- `MCP_ALLOWED_ORIGINS` defines the browser origin allowlist for protected `/mcp` requests.
- `MCP_ALLOW_ORIGINLESS_CLIENTS` controls whether non-browser callers without `Origin` can proceed to authentication checks.
- `MCP_SESSION_BACKEND` selects the hosted session backend (`memory` for local-only or shared-memory tests, `redis` for durable hosted deployments).
- `MCP_SESSION_STORE_URL` points at the shared durable session backend when hosted session durability is required.
- `MCP_SECRET_ACCESS_MODE` documents how the hosted runtime receives secret-backed configuration.
- `MCP_SECRET_REFERENCE_NAMES` records the secret references expected to be available to the hosted runtime.
- `MCP_SESSION_CONNECTIVITY_MODEL` documents the provider-specific connectivity path used to reach the durable session backend.
- The Terraform-managed hosted network layer now provisions the VPC network, subnet, and session connector reference used by the supported GCP durable-session path.
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

If you are deploying for the first time, follow `Setup From Scratch: Hosted On
GCP` earlier in this README first. This section is the lower-level hosted
deployment reference.

The hosted deployment steps below describe the current primary hosted provider adapter. FND-020 preserves these steps while separating them from the provider-neutral application deployment model.

Required deployment inputs:

- `PROJECT_ID`
- `REGION`
- `SERVICE_NAME`
- `IMAGE_REFERENCE`
- `SERVICE_ACCOUNT_EMAIL`
- `MCP_SERVER_IMPLEMENTATION` (`uvicorn`)
- `MCP_ASGI_APP` (`mcp_server.cloud_run_entrypoint:app`)
- `MCP_SECRET_ACCESS_MODE` (`secret_manager_env` for Cloud Run hosted secret injection)
- `MCP_SECRET_REFERENCE_NAMES` (comma-separated runtime secret references, normally matching `SECRET_REFERENCES`)
- `PUBLIC_INVOCATION_INTENT` (`public_remote_mcp` for trusted public remote MCP environments, `private_only` otherwise)
- `MCP_ENVIRONMENT`
- `MCP_AUTH_REQUIRED`
- `MCP_ALLOWED_ORIGINS`
- `MCP_ALLOW_ORIGINLESS_CLIENTS`
- `MIN_INSTANCES`
- `MAX_INSTANCES`
- `CONCURRENCY`
- `TIMEOUT_SECONDS`
- `SECRET_REFERENCES` (`YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN` are required for `staging` and `prod`)
- `INFRA_OUTPUTS_FILE` (optional Terraform `output -json` handoff file for pre-provisioned infrastructure)

When you use the supported GCP Terraform path, deployment evidence also carries
the managed hosted-network references exported by infrastructure reconciliation.
That includes the session connector reference and the managed network
references needed for deployment review and hosted verification.

Execute the deployment workflow with explicit revision settings:

```bash
PROJECT_ID=example-project \
REGION=us-central1 \
SERVICE_NAME=youtube-mcp-server \
IMAGE_REFERENCE=us-docker.pkg.dev/example-project/apps/youtube-mcp-server:sha \
SERVICE_ACCOUNT_EMAIL=youtube-mcp-server@example-project.iam.gserviceaccount.com \
MCP_SERVER_IMPLEMENTATION=uvicorn \
MCP_ASGI_APP=mcp_server.cloud_run_entrypoint:app \
MCP_SECRET_ACCESS_MODE=secret_manager_env \
MCP_SECRET_REFERENCE_NAMES=YOUTUBE_API_KEY,MCP_AUTH_TOKEN \
PUBLIC_INVOCATION_INTENT=public_remote_mcp \
MCP_ENVIRONMENT=staging \
MCP_AUTH_REQUIRED=true \
MCP_ALLOWED_ORIGINS=https://chat.openai.com \
MCP_ALLOW_ORIGINLESS_CLIENTS=true \
MCP_SESSION_BACKEND=redis \
MCP_SESSION_STORE_URL=redis://REDIS_HOST:6379/0 \
MCP_SESSION_CONNECTIVITY_MODEL=serverless_vpc_connector \
MCP_SESSION_DURABILITY_REQUIRED=true \
MIN_INSTANCES=0 \
MAX_INSTANCES=2 \
CONCURRENCY=20 \
TIMEOUT_SECONDS=180 \
SECRET_REFERENCES=YOUTUBE_API_KEY,MCP_AUTH_TOKEN \
bash scripts/deploy_cloud_run.sh
```

If you provisioned the hosted platform through the Terraform workflow in
`infrastructure/gcp/`, you can pass the exported outputs file directly into the
deployment workflow instead of retyping the provisioned values:

```bash
INFRA_OUTPUTS_FILE=artifacts/gcp-foundation-outputs.json \
IMAGE_REFERENCE=us-docker.pkg.dev/example-project/apps/youtube-mcp-server:sha \
bash scripts/deploy_cloud_run.sh
```

The deployment workflow now returns a JSON deployment record containing the
deployment outcome, revision name, hosted service URL, public invocation
intent, published connection point, and runtime settings summary. Save that
record and use it as the handoff into hosted verification.
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
MCP_SECRET_ACCESS_MODE=secret_manager_env \
MCP_SECRET_REFERENCE_NAMES=YOUTUBE_API_KEY,MCP_AUTH_TOKEN \
PUBLIC_INVOCATION_INTENT=public_remote_mcp \
MCP_ENVIRONMENT=staging \
MCP_AUTH_REQUIRED=true \
MCP_ALLOWED_ORIGINS=https://chat.openai.com \
MCP_ALLOW_ORIGINLESS_CLIENTS=true \
MCP_SESSION_BACKEND=redis \
MCP_SESSION_STORE_URL=redis://REDIS_HOST:6379/0 \
MCP_SESSION_CONNECTIVITY_MODEL=serverless_vpc_connector \
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

Set `PUBLIC_INVOCATION_INTENT=public_remote_mcp` only for environments that
should be intentionally reachable by trusted remote MCP consumers. Use
`PUBLIC_INVOCATION_INTENT=private_only` for environments that should remain
outside the public remote MCP workflow. Public invocation intent does not
replace `Authorization: Bearer ...`; it only determines whether the hosted
Cloud Run service is intentionally reachable.

Operator diagnosis now follows two layers:

- `cloud_platform`: the public `reachability` probe failed before the request reached the hosted MCP application.
- `mcp_application`: the hosted service was reachable, but the protected `/mcp` request failed due to bearer-token or browser-origin rules.

The hosted verifier now exercises the streamable MCP transport rather than the
older bare `POST /mcp` flow. It performs `initialize`, captures the returned
`MCP-Session-Id`, reuses that session for subsequent `POST` and `GET` MCP
requests, validates reconnect behavior with `Last-Event-ID`, and accepts both
`application/json` and `text/event-stream` responses as required by the hosted
transport contract. Covered hosted MCP failures now use numeric `error.code`
values and stable `error.data.category` details rather than legacy string-style
top-level error codes. It now records a public `reachability` check before
`liveness`, `readiness`, and authenticated `/mcp` verification so operators can
separate Cloud Run public access from MCP-layer authentication.
It also records `deployment-evidence`, `secret-access`, and
`session-connectivity` checks so operators can distinguish missing runtime
secret access from missing durable session connectivity before session
continuation is attempted.

When hosted verification reports `SECRET_ACCESS_UNAVAILABLE` or
`SECRET_REFERENCE_MISSING`, inspect the Cloud Run runtime service account,
`MCP_SECRET_ACCESS_MODE`, and `MCP_SECRET_REFERENCE_NAMES` first. When hosted
verification reports a session-connectivity failure, inspect
`MCP_SESSION_CONNECTIVITY_MODEL`, the exported session connector reference, the
managed session network reference, and the Redis backend reference first.

## Automated hosted deployment

Push-triggered hosted deployment is primarily defined in `cloudbuild.yaml`.
Cloud Build is the primary auto-deploy path for pushes to `main` when your GCP
trigger is configured to use that file.

The GitHub Actions workflow at `.github/workflows/hosted-deploy.yml` is a
manual fallback for operators and open source users who prefer GitHub-hosted
automation. The GitHub Actions workflow is a manual fallback, and it is
intentionally `workflow_dispatch` only so it does not race with the Cloud Build
trigger on `main`.

Both automation paths keep the same repository-managed rollout path intact:

1. validate bootstrap prerequisites
2. run `pytest` and `ruff check .`
3. build and publish the current image
4. run `terraform -chdir=infrastructure/gcp apply`
5. export Terraform outputs to `artifacts/gcp-foundation-outputs.json`
6. deploy through `scripts/deploy_cloud_run.sh`
7. verify through `scripts/verify_cloud_run_foundation.py`
8. upload the deployment and verification artifacts

For environments that require durable hosted session connectivity, managed
network bootstrap is part of step 4. In other words, network reconciliation
happens before deploy and remains inside the same reviewed automation path.
Stated directly: network reconciliation happens before deploy for the supported hosted path.

The workflow does not replace the repository deployment logic with a direct
image-only Cloud Run update. Terraform outputs remain the handoff between
infrastructure reconciliation and application rollout.

### Push-triggered deployment bootstrap prerequisites

Before trusting a push to `main` as a hosted deployment trigger, confirm these
one-time bootstrap prerequisites:

These one-time bootstrap inputs remain outside the recurring automated
deployment run.

- repository automation can authenticate to GCP through
  `GCP_WORKLOAD_IDENTITY_PROVIDER` and `GCP_SERVICE_ACCOUNT`
- repository variables provide `GCP_PROJECT_ID`, `GCP_REGION`,
  `GCP_SERVICE_NAME`, `GCP_ARTIFACT_REGISTRY_REPOSITORY`, and
  `GCP_TERRAFORM_VAR_FILE`
- the target environment already contains operator-managed secret values for
  `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN`
- the Artifact Registry repository and Terraform variable file already exist
  for the target environment

If any bootstrap prerequisite is missing, the workflow fails before it reports
a hosted deployment result.

The failure boundary is intentional and should remain operator-visible:

- `bootstrap_input_failure` means one-time bootstrap inputs were missing before
  hosted reconciliation could start.
- `network_reconcile_failure` means managed network bootstrap failed during
  infrastructure reconciliation.
- later deploy or hosted verification failures happen only after those earlier
  gates succeed.

For the primary path, configure your existing Cloud Build trigger for `main` to
read `cloudbuild.yaml`. Use the GitHub Actions workflow only when you want a
manual fallback run or a community-managed alternative outside your primary GCP
trigger.

### Secret boundary for automated deployment

Repository automation is allowed to wire secret references, authenticate to the
cloud environment, export infrastructure outputs, deploy the hosted revision,
and run hosted verification.

Repository automation is not allowed to create, print, rotate, or commit secret
values. `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN` remain operator-managed secret
values even when the workflow is fully automated.

### Hosted deployment artifacts

The workflow publishes these artifacts for each push-driven hosted rollout:

- `artifacts/image-reference.txt`
- `artifacts/gcp-foundation-outputs.json`
- `artifacts/cloud-run-deployment.json`
- `artifacts/cloud-run-verification.json`
- `artifacts/cloud-run-verification.txt`

Treat `artifacts/cloud-run-deployment.json` as the handoff from deploy to
verification and `artifacts/cloud-run-verification.json` as the final release
gate summary.

Manual streamable MCP verification examples:

Rejected initialize requests must not return `MCP-Session-Id` and must not create
usable hosted continuation state:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -d '{"jsonrpc":"2.0","id":"req-init-invalid","method":"initialize","params":{}}' \
  https://YOUR_SERVICE_URL/mcp
```

Expected result: invalid initialize error with no `MCP-Session-Id` header.

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

Representative hosted failure responses now use numeric MCP error codes:

```json
{
  "jsonrpc": "2.0",
  "id": "req-invalid",
  "error": {
    "code": -32602,
    "message": "arguments must be an object",
    "data": {
      "category": "invalid_argument"
    }
  }
}
```

Representative hosted resource-missing failures use the shared numeric mapping:

```json
{
  "jsonrpc": "2.0",
  "id": "req-missing-tool",
  "error": {
    "code": -32001,
    "message": "Tool not found.",
    "data": {
      "category": "unknown_tool",
      "toolName": "missing_tool"
    }
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
      {
        "name":"search",
        "description":"Search the retrieval corpus for relevant documents.",
        "inputSchema":{"type":"object","required":["query"],"properties":{"query":{"type":"string","minLength":1}},"additionalProperties":false}
      },
      {
        "name":"fetch",
        "description":"Fetch the full contents of a previously identified document.",
        "inputSchema":{"type":"object","required":["id"],"properties":{"id":{"type":"string","minLength":1}},"additionalProperties":false}
      }
    ]
  }
}
```

For retrieval-contract completeness work, hosted discovery is expected to be
strong enough that clients can build:

- a valid `search` request from the published `query` schema
- a valid `fetch` request from the published `id` schema
- an explicit invalid legacy-shape request that proves the compatibility boundary

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
  -d '{"jsonrpc":"2.0","id":"req-search","method":"tools/call","params":{"name":"search","arguments":{"query":"remote MCP research"}}}' \
  https://YOUR_SERVICE_URL/mcp
```

Representative hosted `fetch` examples derived from discovery:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch","method":"tools/call","params":{"name":"fetch","arguments":{"id":"doc-remote-mcp-001"}}}' \
  https://YOUR_SERVICE_URL/mcp
```

Representative successful retrieval payload:

```json
{
  "id":"doc-remote-mcp-001",
  "url":"https://example.com/remote-mcp-research",
  "content": [
    {
      "type": "text",
      "text": "{\"id\":\"doc-remote-mcp-001\",\"title\":\"Remote MCP Research Workflows\",\"text\":\"Remote MCP research workflows depend on discoverable tools and stable document retrieval.\",\"url\":\"https://example.com/remote-mcp-research\",\"metadata\":{\"sourceName\":\"Example Research\"}}"
    }
  ]
}
```

Representative unsupported legacy-shape example:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer YOUR_MCP_AUTH_TOKEN' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-fetch-legacy","method":"tools/call","params":{"name":"fetch","arguments":{"resourceId":"res_remote_mcp_001"}}}' \
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

- `reachability`
- `liveness`
- `readiness`
- `initialize-invalid-no-session`
- `initialize-success-session-created`
- `initialize-retry-success`
- `initialize`
- `list-tools`
- `search-tool-call-openai`
- `fetch-tool-call-openai`
- `search-tool-call-empty`
- `fetch-tool-call-legacy-shape`
- `fetch-tool-call-missing`
- `session-post-continuation`
- `session-get-continuation`
- `session-reconnect`
- `session-invalid`
- `browser-preflight-approved`
- `browser-request-approved`
- `browser-origin-denied`
- `browser-request-unsupported`
