# Quickstart: FND-012 Hosted Runtime Migration for Streaming MCP

## Objective

Migrate the hosted MCP service from the current minimal runtime to a
streaming-capable production runtime while preserving the existing hosted MCP
surface, readiness behavior, deployment workflow, and verification path.

## Prerequisites

- Python 3.11+
- Feature branch: `012-hosted-runtime-migration`
- Existing foundation slices through FND-011 available in the current branch
- Local ability to run the Python test suites
- Ability to install and run the planned ASGI runtime dependencies

## Execution Baseline

- Keep the externally visible `/mcp`, `/health`, and `/ready` routes intact.
- Preserve FND-009 through FND-011 MCP transport, protocol, and tool contracts.
- Treat runtime migration, startup lifecycle, deployment assets, and
  verification documentation as the only in-scope change areas.
- Maintain a rollback path to the prior hosted launch command until Cloud Run
  verification succeeds.

## Red Phase (write failing tests and checks first)

1. Update hosted runtime tests so they fail against the current `http.server`
   implementation when evaluating the new runtime expectations.
2. Add or update failing unit tests for runtime lifecycle transitions,
   readiness gating, and request adaptation into the existing MCP handler
   boundary.
3. Add or update failing contract tests for route continuity and hosted runtime
   behavior on `/mcp`, `/health`, and `/ready`.
4. Add or update failing integration tests for concurrent streaming sessions,
   hosted verification flow, and request observability under the migrated
   runtime.
5. Add or update failing deployment-asset tests for the new container start
   command and documented local runtime startup.
6. Run targeted suites and confirm failures:

```bash
python3 -m unittest tests.unit.test_streamable_http_transport
python3 -m unittest tests.unit.test_hosted_http_semantics
python3 -m unittest tests.unit.test_readiness_state
python3 -m unittest tests.unit.test_runtime_profiles
python3 -m unittest tests.contract.test_streamable_http_contract
python3 -m unittest tests.contract.test_readiness_contract
python3 -m unittest tests.contract.test_operational_observability_contract
python3 -m unittest tests.integration.test_streamable_http_transport
python3 -m unittest tests.integration.test_hosted_http_routes
python3 -m unittest tests.integration.test_cloud_run_verification_flow
python3 -m unittest tests.integration.test_request_observability
python3 -m unittest tests.integration.test_readiness_flow
python3 -m unittest tests.integration.test_cloud_run_deployment_assets
```

## Green Phase (minimal implementation)

1. Introduce the minimum ASGI runtime and lifecycle hooks needed to serve the
   existing hosted MCP behavior.
2. Adapt hosted requests from the new runtime into the existing transport and
   protocol handling boundary.
3. Update readiness initialization and shutdown handling so operational probes
   remain correct during startup and termination.
4. Update container startup, deployment assets, and local run documentation to
   use the migrated runtime consistently.
5. Re-run targeted suites until all pass:

```bash
python3 -m unittest tests.unit.test_streamable_http_transport
python3 -m unittest tests.unit.test_hosted_http_semantics
python3 -m unittest tests.unit.test_readiness_state
python3 -m unittest tests.unit.test_runtime_profiles
python3 -m unittest tests.contract.test_streamable_http_contract
python3 -m unittest tests.contract.test_readiness_contract
python3 -m unittest tests.contract.test_operational_observability_contract
python3 -m unittest tests.contract.test_cloud_run_foundation_contract
python3 -m unittest tests.integration.test_streamable_http_transport
python3 -m unittest tests.integration.test_hosted_http_routes
python3 -m unittest tests.integration.test_cloud_run_verification_flow
python3 -m unittest tests.integration.test_request_observability
python3 -m unittest tests.integration.test_readiness_flow
python3 -m unittest tests.integration.test_cloud_run_deployment_assets
python3 -m unittest tests.integration.test_cloud_run_deployment_metadata
```

## Refactor Phase (behavior-preserving cleanup)

1. Remove duplicated request adaptation and lifecycle-management logic.
2. Consolidate runtime startup/shutdown state handling so health, readiness,
   and hosted request serving cannot drift.
3. Remove stale `http.server`-specific assumptions from docs, deployment
   assets, and tests.
4. Re-run the full regression suite:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Manual Local Validation Flow

1. Start the migrated runtime locally:

```bash
PYTHONPATH=src python3 -m uvicorn mcp_server.cloud_run_entrypoint:app --host 0.0.0.0 --port 8080
```

2. Confirm liveness:

```bash
curl -i http://localhost:8080/health
```

3. Confirm readiness after startup completes:

```bash
curl -i http://localhost:8080/ready
```

4. Initialize an MCP session:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":"req-init","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' \
  http://localhost:8080/mcp
```

5. Reuse the returned `MCP-Session-Id` for a streaming tool call:

```bash
curl -i \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  -d '{"jsonrpc":"2.0","id":"req-call","method":"tools/call","params":{"name":"server_ping","arguments":{}}}' \
  http://localhost:8080/mcp
```

6. Open or resume an SSE stream:

```bash
curl -i \
  -H 'Accept: text/event-stream' \
  -H 'MCP-Session-Id: SESSION_ID' \
  http://localhost:8080/mcp
```

## Hosted Verification Flow

1. Build and deploy the container with the migrated runtime entrypoint.
2. Capture the deployment record from `scripts/deploy_cloud_run.sh`.
   Confirm the runtime settings include `serverImplementation=uvicorn` and
   `appModule=mcp_server.cloud_run_entrypoint:app`.
3. Run the hosted verification script against that deployment record:

```bash
PYTHONPATH=src python3 scripts/verify_cloud_run_foundation.py \
  --deployment-record artifacts/cloud-run-deployment.json \
  --evidence-file artifacts/cloud-run-verification.txt
```

4. Confirm the evidence includes passing checks for liveness, readiness,
   initialize, list-tools, and baseline-tool-call under the migrated runtime.

## Success Evidence

- Hosted runtime serves `/mcp`, `/health`, and `/ready` through the migrated
  runtime with no route changes.
- Liveness and readiness remain correct during startup and steady-state
  operation.
- Local and Cloud Run verification both succeed with the same core streaming
  MCP behaviors.
- Structured request logs remain available for hosted troubleshooting.
- Operators retain a documented rollback path until hosted verification passes.

## Validation Evidence (2026-03-16)

- Full regression:
  `python3 -m unittest discover -s tests -p 'test_*.py'`
  Result: passing (`155` tests)
- Local ASGI quickstart validation:
  `.venv/bin/pip install -e .`
  `MCP_ENVIRONMENT=dev .venv/bin/python -m uvicorn mcp_server.cloud_run_entrypoint:app --host 127.0.0.1 --port 8090`
  `curl -i http://127.0.0.1:8090/health`
  `curl -i http://127.0.0.1:8090/ready`
  `curl -i -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' -d '{"jsonrpc":"2.0","id":"req-init-quickstart-dev","method":"initialize","params":{"clientInfo":{"name":"manual","version":"1.0.0"}}}' http://127.0.0.1:8090/mcp`
  Result: `200 OK` for `/health`, `200 OK` for `/ready`, and `200 OK` with `MCP-Session-Id` for `initialize`
