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

## 5. Core Functional Requirements

### 5.1 Video Information Tools
- Get video details (title, description, duration, publish date, tags, category, thumbnails).
- List channel videos (filterable by date/order/page).
- Get video statistics (views, likes, comments, favorites where available).
- Search videos across YouTube (query/q, sort, date range, `relevanceLanguage`, region filters).

### 5.2 Transcript Management Tools
- Retrieve video transcripts.
- Support transcript retrieval in multiple languages.
- Return timestamped caption segments.
- Search within transcript text and return matching timestamps.
- Transcript/caption operations are authorization-sensitive and require caption track access context.

### 5.3 Channel Management Tools
- Get channel details (metadata/branding fields available from API).
- List channel playlists.
- Get channel statistics.
- Search within channel content.

### 5.4 Playlist Management Tools
- List playlist items.
- Get playlist details.
- Search within playlists.
- Get playlist video transcripts.

## 6. MCP Tool Contract Requirements
- Each tool must include:
  - Clear name and description.
  - JSON schema input validation.
  - Typed JSON output.
  - Structured error model (`code`, `message`, `details`).
- Consistent pagination fields (`nextPageToken`, `pageSize`, `totalResults` when available).
- Deterministic parameter names across tools (e.g., `videoId`, `channelId`, `playlistId`, `query`, `language`), with explicit mapping to YouTube terms (`query -> q`, `pageSize -> maxResults`).

## 7. API and Data Requirements
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

## 8. Cloud Run Deployment Requirements
- Containerized server image.
- Deploy to Cloud Run with:
  - Minimum one revision in production.
  - Configured concurrency/timeouts suitable for API calls.
  - Autoscaling bounds (min/max instances).
- Use Secret Manager for API keys/tokens (no secrets in source or env files committed to git).
- Use dedicated service account with least-privilege IAM.
- Support environment-based config (`dev`, `staging`, `prod`).

## 9. Security and Compliance Requirements
- Secrets stored and injected securely.
- Input validation for all tool parameters.
- Output sanitization to avoid leaking internal stack traces.
- Audit-friendly logs (request ID, tool name, latency, status).
- Rate limiting or request throttling guardrails for abuse prevention.
- For transcript/caption tools, enforce authorization checks and explicit errors when caption access is not permitted.

## 10. Reliability and Performance Requirements
- Availability target: 99.5% monthly (v1 target).
- p95 tool latency target: < 3s for cached/simple calls, < 8s for transcript-heavy calls.
- Graceful handling of YouTube API failures, empty results, and partial data.
- Optional response caching for high-frequency reads.

## 11. Observability Requirements
- Structured logging enabled by default.
- Metrics:
  - Request count by tool.
  - Success/error rates by tool.
  - Latency percentiles.
  - Quota-related failures.
- Basic alerting for sustained error rate or elevated latency.

## 12. Developer Experience Requirements
- Local run instructions and required env vars documented.
- Simple deployment command(s) documented for Cloud Run.
- Tool-by-tool usage examples with sample payloads.
- Automated checks for lint/type/test in CI.

## 13. Acceptance Criteria (v1)
- All 16 tools in Sections 5.1-5.4 are implemented and callable via MCP.
- Every tool validates inputs and returns structured errors.
- Cloud Run deployment succeeds and serves MCP traffic.
- Secrets are managed through Secret Manager.
- Logs and core metrics are visible in Google Cloud.
- README includes setup, config, run, and deploy instructions.
- Composite tools are clearly documented where behavior is not provided by a single native YouTube endpoint (playlist search and transcript text search).

## 14. Milestones
1. Define tool schemas and response contracts.
2. Implement video/channel/playlist tools.
3. Implement transcript retrieval/search flows.
4. Add auth, secrets, and quota/error handling hardening.
5. Deploy to Cloud Run and validate end-to-end MCP integration.
6. Add monitoring, alerts, and release documentation.

## 15. Open Decisions
- Final transcript fallback approach when official captions are unavailable.
- Required auth model for private/unlisted resource access (if in scope later).
- Caching policy (TTL, storage backend, invalidation strategy).
- Transcript scope decision: owner-authorized captions only vs optional non-YouTube fallback for broader public coverage.
