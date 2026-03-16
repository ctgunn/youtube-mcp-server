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

Python 3.11: Follow standard conventions

## Recent Changes
- 009-mcp-streamable-http-transport: Added Python 3.11 + Python standard-library HTTP server, Python standard-library threading and queue primitives, in-repo MCP transport/protocol/config/observability modules, MCP Streamable HTTP specification (protocol version `2025-11-25`) for transport behavior
- 008-deployment-cloud-observability: Added Python 3.11 + Python standard-library HTTP server, Python standard-library subprocess and JSON tooling, in-repo MCP transport/protocol/config/observability modules
- 007-hosted-http-hardening: Added Python 3.11 + Python standard-library HTTP server for hosted entrypoint plus in-repo MCP transport, protocol, health, config, and observability modules


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
