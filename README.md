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
