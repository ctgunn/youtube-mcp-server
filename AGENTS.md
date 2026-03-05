# youtube-mcp-server Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-01

## Active Technologies
- In-memory registry state (no persistent storage in this slice) (002-tool-registry-dispatcher)
- In-memory runtime state only (tool registry and runtime metadata) (003-baseline-server-tools)
- In-memory runtime configuration state only (no persistent storage in this slice) (004-config-secrets-startup-validation)
- In-memory runtime state only (tool registry, request context, metric aggregates) (005-health-logging-metrics)

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
- 005-health-logging-metrics: Added Python 3.11 + FastAPI, Pydantic v2, Uvicorn
- 005-health-logging-metrics: Added [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
- 004-config-secrets-startup-validation: Added Python 3.11 + FastAPI, Pydantic v2, Uvicorn


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
