# Product Requirements Document (PRD)
## Project: YouTube MCP Server on Cloud Run

## 1. Overview
Build an MCP-compliant server that exposes YouTube data and transcript workflows as callable tools for Agent Builder and MCP clients. The service will run on Google Cloud Run and provide secure, observable, scalable access to YouTube content operations.

## 2. Objectives
- Expose reliable YouTube tools through MCP.
- Support video, channel, playlist, and transcript workflows.
- Deploy as a production-ready Cloud Run service.
- Keep response formats structured for agent consumption.

## 3. Non-Goals
- No video upload/edit/publish operations in v1.
- No channel owner account management UI.
- No long-term analytics warehouse in v1.

## 4. Primary Users
- Agent developers building workflows in OpenAI Agent Builder.
- Internal teams needing programmatic YouTube research/retrieval.

## 5. MCP Server Foundation Requirements (Phase 0)
This phase establishes a working MCP server before any YouTube tools are added.

### 5.1 Foundation Deliverables
- Running MCP server process with Cloud Run-compatible HTTP transport.
- MCP handshake and capability declaration implemented.
- Tool registry system implemented (register/list/dispatch lifecycle).
- Baseline non-YouTube tools implemented for smoke testing.
- Health/readiness endpoints for operations.
- Config, logging, error handling, containerization, and CI checks in place.

### 5.2 Minimum Server Features
- MCP protocol support:
  - `initialize` and capability negotiation.
  - Tool discovery/listing.
  - Tool invocation path with structured request/response handling.
- Operational endpoints:
  - `GET /healthz` for liveness.
  - `GET /readyz` for readiness (including config checks).
- Baseline tools (no external APIs):
  - `server_ping`: returns service status and timestamp.
  - `server_info`: returns version, environment, and build metadata.
  - `server_list_tools`: returns currently registered tool names/descriptions.

### 5.3 Foundation Architecture Requirements
- Layered modules:
  - Transport layer (HTTP request handling and MCP message flow).
  - MCP core (tool registry, dispatcher, schema validation, errors).
  - Integrations layer (YouTube API client wrapper, transcript adapters).
  - Domain/tool layer (individual tool handlers).
- Dependency boundaries:
  - Tools must depend on integration interfaces, not concrete HTTP clients.
  - Config and secrets must be injected, not read ad-hoc inside tools.
- Standard request context:
  - `requestId`, `traceId` (if present), `toolName`, `startTime`.

### 5.4 Configuration and Environment Requirements
- Required env vars defined and validated at startup.
- Environment profiles: `dev`, `staging`, `prod`.
- Secret-backed values (API keys/tokens) loaded from Secret Manager in deployed environments.
- Fail-fast startup behavior when required config is missing.

### 5.5 Error Handling and Validation Requirements
- Central error mapper to normalize internal exceptions into MCP-safe responses.
- Input validation at tool boundary (JSON schema).
- Error shape must include `code`, `message`, and optional `details`.
- No stack traces returned to clients.

### 5.6 Logging and Observability Requirements
- Structured JSON logs with:
  - `timestamp`, `severity`, `requestId`, `toolName`, `latencyMs`, `status`.
- Core metrics instrumented:
  - request count, success/error count, p50/p95 latency.
- Correlatable logs across request lifecycle.

### 5.7 Local Developer Workflow Requirements
- Single command to install deps.
- Single command to run server locally.
- Single command to run tests/lint/typecheck.
- `.env.example` included with documented variables.
- README section: local startup + MCP client connection instructions.

### 5.8 Cloud Run Standup Requirements (Phase 0)
- Build container image for server.
- Deploy one Cloud Run revision with:
  - runtime service account.
  - min/max instances.
  - concurrency and timeout configured.
  - required env vars + secret references.
- Verify:
  - `/healthz` and `/readyz` pass.
  - MCP initialize/list tools/invoke baseline tool works against deployed URL.

### 5.9 Foundation Acceptance Criteria (Exit Gate for Tool Work)
- MCP server successfully initializes from an MCP client.
- Baseline tools can be listed and invoked end-to-end.
- Structured logs appear in Cloud Logging for each request.
- Health/readiness endpoints pass in Cloud Run.
- CI checks pass (lint/typecheck/tests).
- Deployment is reproducible via documented commands.

## 6. Core Functional Requirements (Phase 1+)

### 6.1 Video Information Tools
- Get video details (title, description, duration, publish date, tags, category, thumbnails).
- List channel videos (filterable by date/order/page).
- Get video statistics (views, likes, comments, favorites where available).
- Search videos across YouTube (query/q, sort, date range, `relevanceLanguage`, region filters).

### 6.2 Transcript Management Tools
- Retrieve video transcripts.
- Support transcript retrieval in multiple languages.
- Return timestamped caption segments.
- Search within transcript text and return matching timestamps.
- Transcript/caption operations are authorization-sensitive and require caption track access context.

### 6.3 Channel Management Tools
- Get channel details (metadata/branding fields available from API).
- List channel playlists.
- Get channel statistics.
- Search within channel content.

### 6.4 Playlist Management Tools
- List playlist items.
- Get playlist details.
- Search within playlists.
- Get playlist video transcripts.

## 7. MCP Tool Contract Requirements
- Each tool must include:
  - Clear name and description.
  - JSON schema input validation.
  - Typed JSON output.
  - Structured error model (`code`, `message`, `details`).
- Consistent pagination fields (`nextPageToken`, `pageSize`, `totalResults` when available).
- Deterministic parameter names across tools (e.g., `videoId`, `channelId`, `playlistId`, `query`, `language`), with explicit mapping to YouTube terms (`query -> q`, `pageSize -> maxResults`).

## 8. API and Data Requirements
- Primary data source: YouTube Data API v3.
- Endpoint alignment (verified against YouTube docs on February 26, 2026):
  - Search workflows use `search.list` with `type=video`.
  - Channel video listing can use either:
    - `search.list` with `channelId` for ranked/discoverability behavior.
    - Uploads playlist flow (`channels.list` -> `contentDetails.relatedPlaylists.uploads` -> `playlistItems.list`) for deterministic exhaustive listing.
  - Playlist search is composite behavior (list playlist items then filter in-server).
- Transcript source strategy:
  - Official path: `captions.list(videoId)` and `captions.download(captionTrackId)`.
  - These endpoints require OAuth authorization context for the target caption track.
  - Any public transcript fallback (if used) must be explicitly documented as non-YouTube-Data-API behavior.
- Handle quota limits with explicit error responses and retry guidance.
- Normalize disparate API responses into stable MCP output schemas.

## 9. Cloud Run Deployment Requirements
- Containerized server image.
- Deploy to Cloud Run with:
  - Minimum one revision in production.
  - Configured concurrency/timeouts suitable for API calls.
  - Autoscaling bounds (min/max instances).
- Use Secret Manager for API keys/tokens (no secrets in source or env files committed to git).
- Use dedicated service account with least-privilege IAM.
- Support environment-based config (`dev`, `staging`, `prod`).

## 10. Security and Compliance Requirements
- Secrets stored and injected securely.
- Input validation for all tool parameters.
- Output sanitization to avoid leaking internal stack traces.
- Audit-friendly logs (request ID, tool name, latency, status).
- Rate limiting or request throttling guardrails for abuse prevention.
- For transcript/caption tools, enforce authorization checks and explicit errors when caption access is not permitted.

## 11. Reliability and Performance Requirements
- Availability target: 99.5% monthly (v1 target).
- p95 tool latency target: < 3s for cached/simple calls, < 8s for transcript-heavy calls.
- Graceful handling of YouTube API failures, empty results, and partial data.
- Optional response caching for high-frequency reads.

## 12. Observability Requirements
- Structured logging enabled by default.
- Metrics:
  - Request count by tool.
  - Success/error rates by tool.
  - Latency percentiles.
  - Quota-related failures.
- Basic alerting for sustained error rate or elevated latency.

## 13. Developer Experience Requirements
- Local run instructions and required env vars documented.
- Simple deployment command(s) documented for Cloud Run.
- Tool-by-tool usage examples with sample payloads.
- Automated checks for lint/type/test in CI.

## 14. Acceptance Criteria (v1)
- Phase 0 foundation acceptance criteria are fully met.
- All 16 tools in Sections 6.1-6.4 are implemented and callable via MCP.
- Every tool validates inputs and returns structured errors.
- Cloud Run deployment succeeds and serves MCP traffic.
- Secrets are managed through Secret Manager.
- Logs and core metrics are visible in Google Cloud.
- README includes setup, config, run, and deploy instructions.
- Composite tools are clearly documented where behavior is not provided by a single native YouTube endpoint (playlist search and transcript text search).

## 15. Milestones
1. Complete MCP server foundation (transport, registry, baseline tools, health endpoints).
2. Stand up Cloud Run deployment for foundation build and validate end-to-end MCP handshake.
3. Define tool schemas and response contracts.
4. Implement video/channel/playlist tools.
5. Implement transcript retrieval/search flows.
6. Add auth, secrets, and quota/error handling hardening.
7. Add monitoring, alerts, and release documentation.

## 16. Open Decisions
- Final transcript fallback approach when official captions are unavailable.
- Required auth model for private/unlisted resource access (if in scope later).
- Caching policy (TTL, storage backend, invalidation strategy).
- Transcript scope decision: owner-authorized captions only vs optional non-YouTube fallback for broader public coverage.
- Final MCP transport profile details for production clients (if multiple transport modes are supported).
