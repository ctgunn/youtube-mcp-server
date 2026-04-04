# youtube-mcp-server Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-01

## Active Technologies
- In-memory registry state (no persistent storage in this slice) (002-tool-registry-dispatcher)
- In-memory runtime state only (tool registry and runtime metadata) (003-baseline-server-tools)
- In-memory runtime configuration state only (no persistent storage in this slice) (004-config-secrets-startup-validation)
- In-memory runtime state only (tool registry, request context, metric aggregates) (005-health-logging-metrics)
- In-memory runtime state only; deployment artifacts are file-based documentation and packaging assets (006-cloud-run-foundation)
- Python 3.11 + Python standard-library HTTP server for hosted entrypoint plus in-repo MCP transport, protocol, health, config, and observability modules (007-hosted-http-hardening)
- In-memory runtime state only; no persistent storage for this feature (007-hosted-http-hardening)
- Python 3.11 + Python standard-library HTTP server, Python standard-library subprocess and JSON tooling, in-repo MCP transport/protocol/config/observability modules (008-deployment-cloud-observability)
- In-memory runtime state only; deployment evidence and planning artifacts are file-based (008-deployment-cloud-observability)
- Python 3.11 + Python standard-library HTTP server, Python standard-library threading and queue primitives, in-repo MCP transport/protocol/config/observability modules, MCP Streamable HTTP specification (protocol version `2025-11-25`) for transport behavior (009-mcp-streamable-http-transport)
- In-memory runtime state only for transport sessions, stream cursors, and event queues; planning and verification artifacts are file-based (009-mcp-streamable-http-transport)
- Python 3.11 + Python standard-library HTTP server and JSON tooling, in-repo MCP transport/protocol/config/observability modules, MCP Streamable HTTP transport behavior from FND-009, MCP protocol-native request/result/error semantics for hosted and local flows (010-mcp-protocol-alignment)
- In-memory runtime state only for tool registry, request context, and hosted transport sessions; planning artifacts are file-based (010-mcp-protocol-alignment)
- Python 3.11 + Python standard-library HTTP server and JSON tooling, in-repo MCP transport/protocol/config/observability modules, in-repo tool registry and dispatcher modules, MCP-native protocol contract from FND-010 (011-tool-metadata-result-alignment)
- Python 3.11 + FastAPI, Pydantic v2, Uvicorn, existing in-repo MCP transport/protocol/config/observability modules, current streamable transport session helpers (012-hosted-runtime-migration)
- In-memory runtime state only for tool registry, request context, readiness state, and MCP streaming sessions; planning artifacts are file-based (012-hosted-runtime-migration)
- Python 3.11 + FastAPI, Uvicorn, Pydantic v2, Python standard library transport/config/logging modules (013-remote-mcp-security)
- In-memory runtime state only; configuration and secrets are environment/secret-backed (013-remote-mcp-security)
- Python 3.11 + FastAPI, Uvicorn, Pydantic v2, Python standard library JSON/HTTP/config/logging modules (014-deep-research-tools)
- In-memory runtime state only; no persistent storage for retrieval references or fetched conten (014-deep-research-tools)
- Python 3.11 + FastAPI, Uvicorn, Pydantic v2, Python standard library JSON/HTTP/config/logging modules, Redis-compatible shared session store client (015-hosted-session-durability)
- In-memory runtime state for local-only execution plus Redis-compatible shared ephemeral state for hosted session metadata, stream cursors, and replayable event history (015-hosted-session-durability)
- In-memory runtime state for request handling plus existing runtime configuration from environment variables; no new persistent storage required for browser access policy in this slice (016-browser-mcp-cors)
- Python 3.11 + FastAPI, Uvicorn, Pydantic v2, Redis client, Python standard library JSON/HTTP/config/logging modules (017-retrieval-tool-contract)
- In-memory runtime state only for tool registry, request handling, and retrieval sample data; no new persistent storage required for this slice (017-retrieval-tool-contract)
- In-memory runtime state only for request handling, tool dispatch, observability state, and hosted session metadata backed by the existing shared session store where already configured (018-mcp-error-alignment)
- Python 3.11 for service and verification tooling; Terraform-compatible IaC definitions for infrastructure provisioning + FastAPI, Pydantic v2, Uvicorn, Redis client, Google Cloud Run deployment surface, Secret Manager integration points, Redis-compatible shared session backend, Docker Compose for hosted-like local dependency startup (019-iac-foundation)
- In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted sessions; file-based infrastructure definitions and operator documentation (019-iac-foundation)
- Python 3.11 for service and verification tooling; Terraform-compatible IaC definitions for hosted infrastructure modules + FastAPI, Pydantic v2, Uvicorn, Redis client, Terraform-compatible IaC assets under `infrastructure/`, Docker Compose for hosted-like local dependency startup (020-cloud-agnostic-iac)
- In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted session durability; file-based infrastructure definitions, contracts, and operator documentation (020-cloud-agnostic-iac)
- Python 3.11 for service, deployment, and verification tooling; Terraform-compatible IaC definitions for the GCP provider adapter + FastAPI, Pydantic v2, Uvicorn, Python standard library HTTP tooling, Terraform-compatible assets under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py` (021-cloud-run-reachability)
- In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted session durability; file-based infrastructure definitions, contracts, and operator verification evidence (021-cloud-run-reachability)
- Python 3.11 for service, deployment, and verification tooling; Terraform-compatible IaC definitions for the GCP provider adapter + FastAPI, Pydantic v2, Uvicorn, Redis client, Python standard library HTTP/config/logging tooling, Terraform-compatible assets under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py` (022-hosted-dependency-wiring)
- In-memory runtime state for request handling; Redis-compatible shared ephemeral state for hosted session durability; secret-backed runtime configuration; file-based infrastructure definitions, contracts, and operator evidence artifacts (022-hosted-dependency-wiring)
- Python 3.11 + FastAPI, Pydantic v2, Uvicorn, Redis client, Python standard-library JSON/HTTP/config/logging tooling, existing MCP transport/protocol/tooling modules under `src/mcp_server/` (023-openai-retrieval-compatibility)
- In-memory runtime state only for tool registry, request handling, and retrieval sample data; no persistent storage introduced for this slice (023-openai-retrieval-compatibility)
- Python 3.11 + FastAPI, Pydantic v2, Uvicorn, Redis-compatible session store support, Python standard-library JSON and HTTP tooling, existing MCP transport and protocol modules under `src/mcp_server/` (024-initialize-session-correctness)
- In-memory runtime state for local execution plus shared ephemeral hosted session state when durable session configuration is enabled; no new persistent storage for this slice (024-initialize-session-correctness)
- Python 3.11 + FastAPI, Pydantic v2, Uvicorn, Redis-compatible session store support, Python standard-library JSON/HTTP/config/logging tooling, existing MCP transport/protocol/tooling modules under `src/mcp_server/` (024-initialize-session-correctness)
- In-memory runtime state for local execution plus shared ephemeral session state through the existing hosted session store abstraction; no new persistent storage introduced for this slice (024-initialize-session-correctness)
- Python 3.11 for service, deployment, and verification tooling; checked-in CI workflow definition for push-triggered orchestration + FastAPI, Pydantic v2, Uvicorn, Terraform-compatible IaC under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, `scripts/verify_cloud_run_foundation.py`, container image build/publish tooling, repository-hosted workflow automation (025-hosted-deploy-orchestration)
- In-memory runtime state for request handling; Redis-compatible shared ephemeral state for hosted sessions; file-based Terraform definitions, workflow definitions, deployment records, verification evidence, and specification artifacts (025-hosted-deploy-orchestration)
- Python 3.11 for service and verification tooling; Bash for the local startup wrapper + FastAPI, Pydantic v2, Uvicorn, existing runtime/config modules under `src/mcp_server/`, `scripts/dev_local.sh`, `.env.local`, Docker Compose assets under `infrastructure/local/` (026-local-runtime-entrypoint)
- In-memory runtime state only for local execution; file-based local environment defaults, documentation, and specification artifacts (026-local-runtime-entrypoint)
- Python 3.11 for service, deployment, and verification tooling; Terraform-compatible IaC definitions for the GCP provider adapter + FastAPI, Pydantic v2, Uvicorn, Redis client, Terraform-compatible assets under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, and hosted verification tooling (027-terraform-hosted-networking)
- In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted sessions; file-based Terraform definitions, deployment records, verification evidence, and specification artifacts (027-terraform-hosted-networking)
- Python 3.11 for service, deployment, verification, and workflow-support tooling; checked-in workflow definitions for automated and fallback hosted rollou + FastAPI, Pydantic v2, Uvicorn, Terraform-compatible IaC under `infrastructure/gcp`, `cloudbuild.yaml`, `.github/workflows/hosted-deploy.yml`, deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, `scripts/verify_cloud_run_foundation.py` (028-hosted-network-bootstrap)
- In-memory runtime state for the service; Redis-compatible shared ephemeral state for hosted sessions; file-based workflow definitions, Terraform assets, deployment records, verification evidence, and planning artifacts (028-hosted-network-bootstrap)

- Python 3.11 + FastAPI, Pydantic v2, Uvicorn (001-mcp-transport-handshake)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.11: Follow standard conventions and require reStructuredText docstrings for all new or changed functions

## Recent Changes
- 028-hosted-network-bootstrap: Added Python 3.11 for service, deployment, verification, and workflow-support tooling; checked-in workflow definitions for automated and fallback hosted rollou + FastAPI, Pydantic v2, Uvicorn, Terraform-compatible IaC under `infrastructure/gcp`, `cloudbuild.yaml`, `.github/workflows/hosted-deploy.yml`, deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, `scripts/verify_cloud_run_foundation.py`
- 027-terraform-hosted-networking: Added Python 3.11 for service, deployment, and verification tooling; Terraform-compatible IaC definitions for the GCP provider adapter + FastAPI, Pydantic v2, Uvicorn, Redis client, Terraform-compatible assets under `infrastructure/gcp`, existing deployment helpers in `src/mcp_server/deploy.py`, `scripts/deploy_cloud_run.sh`, and hosted verification tooling
- 026-local-runtime-entrypoint: Added Python 3.11 for service and verification tooling; Bash for the local startup wrapper + FastAPI, Pydantic v2, Uvicorn, existing runtime/config modules under `src/mcp_server/`, `scripts/dev_local.sh`, `.env.local`, Docker Compose assets under `infrastructure/local/`


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
