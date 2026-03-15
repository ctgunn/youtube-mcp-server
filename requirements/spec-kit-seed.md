# SpecKit Seed
## Project: YouTube MCP Server on Cloud Run
## Source Docs
- `requirements/PRD.md`
- `requirements/tool-specs.md`

## 1. Product Goal
Deliver a production-deployed MCP server on Cloud Run that supports a reliable baseline server experience first, then incrementally adds 16 YouTube tools across video, transcript, channel, and playlist domains.

## 2. Scope Model
- Phase 0: MCP server foundation (must be complete before YouTube tools).
- Phase 1: Video and Channel core tools.
- Phase 2: Playlist and Transcript tools.
- Phase 3: Hardening, observability, and production readiness.

## 3. Feature Inventory

### FND-001: MCP Transport + Handshake
Description:
Implement Cloud Run-compatible HTTP transport and MCP initialize/list/invoke flow.

Primary stories:
- As an MCP client, I can initialize against the server and receive capabilities.
- As an MCP client, I can list available tools.
- As an MCP client, I can invoke a tool and receive structured output/errors.

Acceptance criteria:
- `initialize` succeeds with declared server capabilities.
- Tool discovery endpoint returns registered tools.
- Invocation path returns stable response envelope.

Dependencies:
- None.

### FND-002: Tool Registry + Dispatcher
Description:
Implement internal registration and dispatch lifecycle for tools.

Primary stories:
- As a developer, I can register tools with schema and handler.
- As a developer, I can add a new tool without modifying transport code.

Acceptance criteria:
- Registry supports name, description, schema, handler binding.
- Dispatcher validates input and routes to handler by tool name.
- Unknown tools return structured `RESOURCE_NOT_FOUND` errors.

Dependencies:
- `FND-001`

### FND-003: Baseline Server Tools
Description:
Add non-YouTube smoke tools (`server_ping`, `server_info`, `server_list_tools`).

Primary stories:
- As an operator, I can verify server health and metadata through tools.

Acceptance criteria:
- All baseline tools are listed and invokable.
- Tool outputs conform to standard response envelope.

Dependencies:
- `FND-002`

### FND-004: Config + Secrets + Startup Validation
Description:
Centralize configuration, startup validation, and secret-loading contract.

Primary stories:
- As an operator, startup fails fast when required config is missing.
- As a developer, env handling is deterministic across `dev/staging/prod`.

Acceptance criteria:
- Required env vars validated at boot.
- Secret-backed settings documented and injectable.
- Readiness reflects config validity.

Dependencies:
- `FND-001`

### FND-005: Health, Logging, Error Model, Metrics
Description:
Implement `/healthz`, `/readyz`, structured logs, normalized errors, and core metrics.

Primary stories:
- As an operator, I can assess liveness/readiness quickly.
- As a developer, I can trace request execution with request IDs.

Acceptance criteria:
- Health endpoints deployed and returning expected status.
- Structured logs include request/tool/latency fields.
- Errors follow `code/message/details` format.
- Metrics for counts and latency percentiles emitted.

Dependencies:
- `FND-001`, `FND-002`

### FND-006: Cloud Run Foundation Deployment
Description:
Containerize and deploy foundation build, verify MCP round-trip.

Primary stories:
- As an operator, I can deploy one reproducible revision to Cloud Run.
- As an MCP client, I can initialize/list/invoke baseline tool against deployed URL.

Acceptance criteria:
- Deployed revision passes `/healthz` and `/readyz`.
- MCP initialize/list/invoke passes against Cloud Run endpoint.

Dependencies:
- `FND-003`, `FND-004`, `FND-005`

### FND-007: Hosted Probe Semantics + HTTP Hardening
Description:
Harden the hosted HTTP surface so Cloud Run probes and operators can rely on transport-level status codes and consistent endpoint behavior.

Primary stories:
- As an operator, I can trust probe responses because `/healthz` and `/readyz` use correct HTTP semantics.
- As an MCP client, I receive predictable HTTP behavior for supported and unsupported hosted routes.

Acceptance criteria:
- Hosted `/readyz` returns a non-success HTTP status when the instance is not ready.
- Hosted `/healthz`, `/readyz`, and `/mcp` use consistent content-type and request/response handling.
- Unsupported paths and malformed hosted requests return correct HTTP status codes with structured error payloads where applicable.

Dependencies:
- `FND-006`

### FND-008: Deployment Execution + Cloud Run Observability
Description:
Complete the operator deployment workflow by executing the deploy, capturing hosted revision metadata, and emitting structured runtime logs to Cloud Logging-compatible output.

Primary stories:
- As an operator, I can run one deployment workflow that performs the Cloud Run deploy and captures the created revision and URL.
- As an operator, I can inspect hosted request logs in Cloud Logging with request IDs, paths, status, and tool names.

Acceptance criteria:
- Deployment workflow executes the Cloud Run deploy command instead of only rendering it.
- Deployment output records revision name, service URL, and core runtime settings used for the hosted revision.
- Hosted request logs are emitted to stdout/stderr in structured form so Cloud Logging can ingest them.

Dependencies:
- `FND-006`, `FND-005`

### YT-101: YouTube Client Integration Layer
Description:
Build typed wrapper for YouTube Data API v3 with auth, retry, quota, and error mapping.

Primary stories:
- As a tool developer, I can call YouTube endpoints via shared client abstractions.

Acceptance criteria:
- Wrapper supports videos/channels/playlists/search endpoints.
- Quota and upstream errors map to standard server errors.

Dependencies:
- `FND-005`, `FND-006`, `FND-007`, `FND-008`

### YT-102: Video Tools
Description:
Implement video tool set from `tool-specs.md`.

Tools:
- `youtube_get_video_details`
- `youtube_list_channel_videos`
- `youtube_get_video_statistics`
- `youtube_search_videos`

Acceptance criteria:
- All 4 tools implemented with schema validation and documented examples.
- Pagination and parameter mapping (`query -> q`, `pageSize -> maxResults`) enforced.

Dependencies:
- `YT-101`

### YT-103: Channel Tools
Description:
Implement channel tool set from `tool-specs.md`.

Tools:
- `youtube_get_channel_details`
- `youtube_list_channel_playlists`
- `youtube_get_channel_statistics`
- `youtube_search_channel_content`

Acceptance criteria:
- All 4 tools implemented and integrated into registry.
- Consistent response envelope and error handling.

Dependencies:
- `YT-101`

### YT-104: Playlist Tools
Description:
Implement playlist tool set including composite playlist search behavior.

Tools:
- `youtube_list_playlist_items`
- `youtube_get_playlist_details`
- `youtube_search_playlist_items` (composite)

Acceptance criteria:
- All 3 tools implemented.
- Composite search behavior documented and tested.

Dependencies:
- `YT-101`

### YT-105: Transcript/Captions Tools
Description:
Implement transcript tools using authorized captions flow.

Tools:
- `youtube_get_video_transcript`
- `youtube_list_transcript_languages`
- `youtube_get_timestamped_captions`
- `youtube_search_transcript` (composite)
- `youtube_get_playlist_video_transcripts` (composite)

Acceptance criteria:
- Caption-track flow implemented (`captions.list` + `captions.download`).
- Explicit auth-sensitive errors returned when access is not permitted.
- Composite transcript search and playlist transcript behavior documented.

Dependencies:
- `YT-101`, `YT-104`

### OPS-201: CI/CD and Quality Gates
Description:
Add CI checks and deploy automation guardrails.

Primary stories:
- As a maintainer, PRs are blocked on lint/typecheck/tests.

Acceptance criteria:
- CI pipeline executes lint, typecheck, tests.
- Build/deploy instructions reproducible from docs.

Dependencies:
- `FND-008`

### OPS-202: Production Hardening
Description:
Add rate limiting, caching policy, and operational alerts.

Primary stories:
- As an operator, I get alerted on sustained errors/latency spikes.

Acceptance criteria:
- Basic alerting configured.
- Rate limiting strategy implemented.
- Caching strategy documented and applied where appropriate.

Dependencies:
- `YT-102`, `YT-103`, `YT-104`, `YT-105`

## 4. Suggested Delivery Order
1. `FND-001`
2. `FND-002`
3. `FND-003`
4. `FND-004`
5. `FND-005`
6. `FND-006`
7. `FND-007`
8. `FND-008`
9. `YT-101`
10. `YT-102` + `YT-103` (parallel)
11. `YT-104`
12. `YT-105`
13. `OPS-201`
14. `OPS-202`

## 5. Story Template for SpecKit
Use this structure per feature slice:

- Title
- Problem Statement
- User Story
- Scope (In / Out)
- API/Tool Contract Changes
- Data/Schema Changes
- Error Cases
- Observability
- Security Considerations
- Acceptance Criteria
- Test Plan
- Rollout Plan
- Open Questions

## 6. Definition of Ready (DoR)
A feature is ready when:
- Tool contract or endpoint contract is documented.
- Upstream API dependencies are identified.
- Acceptance criteria and tests are listed.
- Required config/secrets are specified.

## 7. Definition of Done (DoD)
A feature is done when:
- Code is merged with passing CI checks.
- Tool is registered and discoverable via MCP list.
- Success and error paths are tested.
- Logs/metrics are visible for the feature.
- Docs updated (`README`, `requirements/tool-specs.md` if contract changed).

## 8. Risks and Watchouts
- Transcript access limitations due to captions authorization scope.
- YouTube quota exhaustion under batch/composite operations.
- Composite tools can hide latency growth; enforce p95 monitoring.
- Schema drift between implementation and `tool-specs.md`.

## 9. Immediate Next SpecKit Inputs
Create first SpecKit specs in this order:
1. `FND-001 MCP Transport + Handshake`
2. `FND-002 Tool Registry + Dispatcher`
3. `FND-003 Baseline Server Tools`
4. `FND-006 Cloud Run Foundation Deployment`
