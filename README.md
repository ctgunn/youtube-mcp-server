# youtube-mcp-server

An MCP-compliant server that wraps the YouTube Data API and exposes tools for
remote MCP clients, including OpenAI Agent Builder workflows. The current
hosted provider adapter runs on Google Cloud Run; the shared platform contract
keeps the overall model portable.

## Start here

This is the repository's getting-started page. Choose the path that matches
what you want to do first.

| Goal | Start here | Outcome |
| --- | --- | --- |
| Explore, develop, or test locally | [Run locally](#run-locally) | A local MCP endpoint with no cloud account required |
| Test durable sessions locally | [Hosted-like local path](#test-hosted-like-sessions-locally) | The local server plus Redis in a container |
| Operate your own hosted instance | [Deploy your fork to GCP](#deploy-your-fork-to-gcp) | Cloud Run, durable session storage, and GitHub Actions releases |
| Understand the system before changing it | [Architecture guide](./docs/architecture.md) | The request lifecycle and module responsibilities |

## Run locally

### Prerequisites

- Python 3.11 or newer
- `pip`
- `make`
- A YouTube Data API key only when calling live YouTube tools

Create an isolated environment and install the project:

```bash
git clone https://github.com/<your-account>/youtube-mcp-server.git
cd youtube-mcp-server
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
cp .env.example .env.local
```

Edit `.env.local` for your machine. It is private configuration and must never
be committed. Add `YOUTUBE_API_KEY` only when you need live API calls.

Run the full quality gate, then start the server:

```bash
make quality
bash scripts/dev_local.sh
```

In another terminal, verify the process:

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/ready
```

The minimal local runtime path does not require cloud provisioning, Docker, or
Redis. For MCP examples and local troubleshooting, read the
[local development guide](./docs/local-development.md).

## Verify the default MCP tool catalog

Run the deterministic Layer 4 catalog check when changing default tool
registration, metadata, dispatch, or local fixtures:

```bash
make test-tools
```

It discovers the catalog through the public MCP `tools/list` route and calls
every discovered tool through `tools/call`. The check uses no credential, makes
no outbound YouTube request, and performs no destructive external mutation.
It is a release-verification check for the default catalog, not proof that a
configured runtime can access YouTube.

## Verify configured YouTube runtime capability

Run the deterministic configured-runtime matrix when changing YouTube runtime
configuration, credential selection, or the live execution boundary:

```bash
make test-runtime
```

It discovers public YouTube families through MCP and checks API-key executable,
OAuth-required, and unavailable-capability outcomes through the same public
route. It uses controlled request construction, makes no outbound YouTube
request, and does not need a real credential. This verification is distinct
from both `make test-tools` catalog coverage and the optional live smoke below.

## Run the optional read-only YouTube live smoke

The live smoke is manual and opt-in. It consumes YouTube quota, depends on
upstream availability, and must be run only by an approved operator with a
real API key. It invokes all 12 explicitly reviewed API-key public-read endpoint
tools with bounded public fixtures. It excludes mutations, uploads, downloads,
deletes, ratings, reports, moderation actions, OAuth-required, owner-only,
retrieval, and baseline-server operations. The `comments_list` check derives one
public parent-comment identifier in memory from the approved
`commentThreads_list` fixture; it never prints that identifier or any response body.

```bash
# In .env.local (or .env):
YOUTUBE_API_KEY='operator-supplied-value'
RUN_YOUTUBE_LIVE_SMOKE=1

# Then, from the repository root:
make test-live-smoke
```

Without both prerequisites, the command fails before constructing the app or
making a live request. Its output redacts credentials, authorization material,
request inputs, headers, and upstream response bodies. It is not included in
`make test`, `make quality`, CI, or automated deployment gates. This local
configured-runtime smoke does not verify a running remote MCP endpoint; that
operator workflow is reserved for OPS-405.

The command sources `.env.local` first and falls back to `.env` when the local
file is absent. Both files are ignored by Git; never commit real credentials.

Run the complete repository test suite with:

```bash
make test
```

The credential-gated live smoke remains separate from the complete repository
test suite and must not be included in `make test-tools`.

## Run the optional remote MCP read-only live smoke

This fourth verification workflow is manual and opt-in. It connects to an
already running remote MCP endpoint, initializes a remote session, discovers
the deployed catalog, and invokes only the 12 explicitly reviewed API-key
public-read tools through the public transport. It validates the remote
endpoint's authorization, session, selected handlers, and live YouTube path;
it does not instantiate the local application as a substitute.

Use only an approved staging or production endpoint after deployment. The
workflow consumes YouTube quota and depends on both remote endpoint and
upstream availability. It is never included in `make test`, `make quality`,
CI, or automated deployment gates.

```bash
# In .env.local (or .env):
RUN_REMOTE_MCP_LIVE_SMOKE=1
REMOTE_MCP_URL='approved-remote-mcp-url'
# Set MCP_AUTH_TOKEN only if the selected remote endpoint requires bearer authorization.
MCP_AUTH_TOKEN='operator-supplied-value'
REMOTE_MCP_AUTH_REQUIRED=1

# Then, run both reviewed remote suites from the repository root:
make test-remote-live-smoke
```

The command fails before any remote request when opt-in authorization or the
remote endpoint is absent, and it requires `MCP_AUTH_TOKEN` before a request
when `REMOTE_MCP_AUTH_REQUIRED=1`. It retains the remote MCP session only in
memory and prints a compact selected-tool report plus passed, excluded, and
request-bound summaries. Its output never includes tokens,
authorization headers, session identifiers, request arguments, raw URLs,
exception text, or upstream response bodies.

To exercise either reviewed layer independently with the same authorization
settings, run:

```bash
make test-remote-layer2-live-smoke
make test-remote-layer3-live-smoke
```

The Layer 3 suite is bounded to 10 API-key-compatible public fixtures. It excludes
OAuth caption/transcript workflows and higher-cost search/enrichment fan-out.

Use the correct verification boundary for the question at hand:

- `make test-tools` is deterministic catalog verification with no external calls.
- `make test-runtime` is deterministic configured-runtime verification with controlled requests.
- `make test-live-smoke` is local live smoke against a configured local application.
- `make test-remote-live-smoke` runs the independently bounded Layer 2 and Layer 3 remote smoke suites against a running MCP endpoint.
- `make test-remote-layer2-live-smoke` runs the reviewed Layer 2 API-key public-read suite only.
- `make test-remote-layer3-live-smoke` runs the reviewed Layer 3 API-key public-read suite only.

If remote live smoke reports a safe availability or actionable failure, record
only its safe tool/category summary. Review endpoint authorization, deployment
health, quota, and upstream status privately, then retry only after approval.

## Test hosted-like sessions locally

Use this optional path only when you need Redis-backed durable-session testing,
reconnect behavior, event replay, or hosted readiness behavior:

```bash
./scripts/local_compose.sh up -d
LOCAL_SESSION_MODE=hosted bash scripts/dev_local.sh
```

Stop Redis when finished:

```bash
./scripts/local_compose.sh down
```

This remains local verification—Cloud Run, GCP IAM, and public reachability
are not involved. See the [local infrastructure README](./infrastructure/local/README.md)
for the full hosted-like local verification path.

## Deploy your fork to GCP

Forking copies the workflow definition, but a first deployment needs one-time
configuration in **your** GitHub repository and **your** GCP project. This is
intentional: project identity, Terraform state, and secret values do not belong
in this source repository.

### 1. Fork and enable Actions

1. Fork this repository to an account or organization you control.
2. Open the fork's **Actions** tab and enable Actions if GitHub prompts you.
3. Use the fork's default branch—normally `main`—as the release branch.

`hosted-deploy` is manually dispatched by design. A hosted release is an
explicit, reviewed operator action rather than an automatic effect of a push.

### 2. Create the GCP bootstrap resources

In your GCP project, create the following once:

1. A private, versioned GCS bucket for Terraform state.
2. A regional Artifact Registry Docker repository.
3. A GitHub OIDC Workload Identity Pool/provider restricted to your fork, plus
   a deployer service account that it may impersonate.
4. Least-privilege access for that deployer to publish images, read/write
   Terraform state, reconcile the infrastructure, deploy Cloud Run, and manage
   runtime Secret Manager access bindings. OPS-402 additionally requires
   `roles/logging.configWriter` and `roles/monitoring.alertPolicyEditor` to
   create application metrics and alert policies.
5. Secret Manager secret values for `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN`.

The release workflow manages the Cloud Run foundation, durable Redis session
path, and managed network bootstrap after these prerequisites exist. It does
not create your state bucket, image repository, identity federation, or secret
values.

### 3. Configure `staging.tfvars`

Replace the checked-in values in `infrastructure/gcp/staging.tfvars` with your
own project ID, region, service name, allowed browser origin, and managed
network names/CIDRs. The file may be committed only when it contains
non-sensitive resource configuration—never API keys, tokens, passwords, or
secret values.

### 4. Configure GitHub Actions

In the fork, open **Settings** → **Secrets and variables** → **Actions**.

Add repository variables:

| Variable | Value |
| --- | --- |
| `GCP_PROJECT_ID` | Your GCP project ID |
| `GCP_REGION` | Your Artifact Registry and Cloud Run region |
| `GCP_SERVICE_NAME` | The service name from `staging.tfvars` |
| `GCP_ARTIFACT_REGISTRY_REPOSITORY` | Your Artifact Registry Docker repository |
| `GCP_TERRAFORM_VAR_FILE` | Normally `staging.tfvars` |
| `GCP_TERRAFORM_STATE_BUCKET` | Your private, versioned Terraform state bucket |

Add repository secrets:

| Secret | Value |
| --- | --- |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | The full Workload Identity Provider resource name |
| `GCP_DEPLOYER_SERVICE_ACCOUNT` | The deployer service-account email address |

Keep `YOUTUBE_API_KEY` and `MCP_AUTH_TOKEN` in GCP Secret Manager. The
supported workflow uses short-lived identity federation, so do not create or
store a downloadable service-account key in GitHub or the repository.

### 5. Run the first release

In GitHub, open **Actions** → **hosted-deploy** → **Run workflow**. Select
`main` as both the workflow source and `target_ref`, then choose `staging` as
the target environment unless you are deliberately releasing another reviewed
revision.

The workflow runs safe preflight and `make quality`, publishes an immutable
image, reconciles Terraform, deploys Cloud Run, and runs hosted verification.
After it succeeds, download `hosted-deploy-<source-sha>` and keep the source
revision, image digest, Terraform outputs, deployment record, and verification
result as release evidence.

For detailed Terraform inputs, GCP roles, network/Redis behavior, and
break-glass recovery, continue with the
[hosted deployment guide](./docs/hosted-deployment.md) and the
[GCP infrastructure README](./infrastructure/gcp/README.md).

## Documentation map

| Document | Use it for |
| --- | --- |
| [docs/local-development.md](./docs/local-development.md) | Local runtime, MCP verification, test commands, and hosted-like local sessions |
| [docs/architecture.md](./docs/architecture.md) | System design, request lifecycle, transport, tools, sessions, and runtime behavior |
| [docs/engineering.md](./docs/engineering.md) | Quality rules, pull-request checks, contributor standards, and runtime-security configuration |
| [docs/hosted-deployment.md](./docs/hosted-deployment.md) | GitHub Actions releases, bootstrap boundaries, evidence, failure handling, and break-glass recovery |
| [infrastructure/local/README.md](./infrastructure/local/README.md) | Redis-backed local dependency setup and troubleshooting |
| [infrastructure/gcp/README.md](./infrastructure/gcp/README.md) | Terraform inputs, GCP resources, Secret Manager, Redis, networking, and provider-specific operations |
| [requirements/PRD.md](./requirements/PRD.md) | Product goals, boundaries, and roadmap context |
| [requirements/spec-kit-seed.md](./requirements/spec-kit-seed.md) | Feature-slice catalog and SpecKit branch numbering |
| [requirements/tool-specs.md](./requirements/tool-specs.md) | YouTube tool inventory and detailed tool-level requirements |
| [docs/archive/README.md](./docs/archive/README.md) | Historical material only; not operational guidance |

The root README should stay focused on first use and finding the right guide.
Put detailed operational or technical reference material in the scoped document
that owns it.
