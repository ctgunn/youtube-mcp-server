# Quickstart: FND-006 Cloud Run Foundation Deployment

## Objective

Implement the deployment packaging, operator workflow, and hosted verification
steps required to prove the MCP foundation service can run as a reproducible
hosted revision.

## Prerequisites

- Python 3.11+
- Feature branch: `006-cloud-run-foundation`
- Existing foundation slices from FND-003 through FND-005 available in the current branch
- Access to the target hosted environment and required deployment inputs

## Red Phase (write failing tests and checks first)

1. Add failing contract coverage for:
   - required deployment inputs and revision settings
   - required hosted verification stages and evidence fields
2. Add failing integration coverage for:
   - deployment packaging/configuration assembly
   - hosted verification helper ordering and failure handling
3. Add failing validation for operator-facing docs so the deployment workflow
   cannot omit:
   - required environment/config/secret inputs
   - runtime identity, scaling, concurrency, and timeout settings
   - rollback or remediation guidance
4. Run targeted suites and confirm failures:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

## Green Phase (minimal implementation)

1. Add the minimum deployment packaging assets needed to build and release the
   current MCP service as one hosted revision.
2. Add or update deployment documentation so operators can supply all required
   inputs and apply explicit revision settings.
3. Add hosted verification helpers or documented commands for:
   - `/health`
   - `/ready`
   - MCP initialize
   - MCP list-tools
   - one baseline tool invocation
4. Add evidence capture requirements for revision name, endpoint URL, and
   per-check pass/fail results.
5. Re-run targeted suites until all pass:

```bash
python3 -m unittest discover -s tests/unit -p 'test_*.py'
python3 -m unittest discover -s tests/integration -p 'test_*.py'
python3 -m unittest discover -s tests/contract -p 'test_*.py'
```

6. Render the deploy command with explicit runtime settings:

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

## Refactor Phase (behavior-preserving cleanup)

1. Consolidate duplicated deployment variables and hosted verification steps.
2. Simplify deployment instructions so one operator can execute them cleanly
   without hidden assumptions.
3. Re-run the full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Hosted Validation Flow

1. Prepare deployment inputs using `.env.example`, runtime profile rules, and
   the documented hosted revision settings.
2. Execute the deployment workflow and capture the revision name and endpoint.
3. Call the hosted `/health` endpoint and record the outcome.
4. Call the hosted `/ready` endpoint and record the outcome.
5. Send MCP initialize to the hosted endpoint and record the outcome.
6. Send MCP list-tools to the hosted endpoint and record the returned baseline
   tools.
7. Invoke one baseline tool against the hosted endpoint and record the outcome.
8. If any step fails, capture the failed stage and apply the documented
   remediation path before re-running verification.

Hosted verification command:

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

## Success Evidence

- Deployment inputs and revision settings are explicitly documented.
- A hosted revision is created and identified in deployment evidence.
- Hosted liveness, readiness, initialize, list-tools, and baseline tool call
  each have recorded pass/fail results.
- Full regression and targeted tests pass before declaring the feature done.

## Validation Evidence (2026-03-13)

- Unit suite: `python3 -m unittest tests.unit.test_cloud_run_config` -> passing
- Contract suite: `python3 -m unittest tests.contract.test_cloud_run_foundation_contract` -> passing
- Integration suites:
  - `python3 -m unittest tests.integration.test_cloud_run_verification_flow` -> passing
  - `python3 -m unittest tests.integration.test_cloud_run_deployment_assets` -> passing
  - `python3 -m unittest tests.integration.test_cloud_run_docs_examples` -> passing
