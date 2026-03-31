# Product Requirements Document (PRD)
## Project: YouTube MCP Server on Cloud Run

## 1. Overview
Build an MCP-compliant server that exposes YouTube data and transcript workflows as callable tools for OpenAI Agent Builder, deep research-style workflows, and other MCP clients. The service will run on Google Cloud Run and provide secure, observable, scalable access to YouTube content operations through standards-aligned remote MCP transport.

## 2. Objectives
- Expose reliable YouTube tools through MCP.
- Support interoperable remote MCP consumption from OpenAI Agent Builder and other MCP-capable services.
- Establish deep research-compatible MCP foundations before domain-specific YouTube tool expansion.
- Distinguish generic MCP compatibility from OpenAI-specific retrieval compatibility where OpenAI currently documents additional expectations.
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
- Running MCP server process with Cloud Run-compatible remote MCP transport.
- MCP handshake and capability declaration implemented.
- Tool registry system implemented (register/list/dispatch lifecycle).
- Baseline non-YouTube tools implemented for smoke testing.
- Health/readiness endpoints for operations.
- MCP transport aligned to a standards-supported remote MCP profile suitable for OpenAI Agent Builder and other hosted MCP consumers.
- MCP protocol request/response handling aligned to MCP-compatible contracts rather than a server-specific wrapper.
- Tool discovery and invocation aligned to MCP-compatible metadata and result structures.
- Streaming-capable hosted runtime in place for production MCP transport behavior.
- Remote MCP transport hardening in place (origin-aware handling and documented auth strategy).
- Foundation `search` and `fetch` tools implemented for deep research-compatible retrieval flows.
- Hosted MCP session continuity remains reliable under the supported Cloud Run routing and scaling model.
- Cloud Run service is publicly reachable in the way required for trusted remote MCP consumers, while preserving application-layer authentication at the MCP endpoint.
- Browser-originated hosted MCP access is either fully supported with explicit CORS/preflight behavior or explicitly documented as out of scope for the current release.
- Foundational retrieval tool schemas fully describe valid invocation shapes for MCP consumers.
- Foundational retrieval tools align to the current OpenAI compatibility contract when the target integration is ChatGPT apps, deep research, or company knowledge-style retrieval.
- Error codes are aligned to the expected JSON-RPC / MCP conventions used by downstream clients.
- Infrastructure required for the hosted platform is reproducible through versioned Infrastructure as Code rather than manual setup alone.
- Infrastructure layout is organized so shared platform capabilities can be reproduced across supported cloud providers with provider-specific adapters where necessary.
- Provider-specific hosted infrastructure wiring includes the IAM and network plumbing required for runtime secret access and durable session connectivity.
- Provider-specific hosted infrastructure includes Terraform-managed network resources required for durable hosted connectivity, including the relevant VPC, subnets, and Cloud Run/VPC connector path where the selected provider requires them.
- Local execution remains a supported first-class mode for development, verification, and debugging without requiring cloud infrastructure provisioning.
- Deployment automation is checked into version control and is capable of reconciling infrastructure, rolling out the application image, and verifying hosted MCP behavior.
- Config, logging, error handling, containerization, and CI checks in place.

### 5.2 Minimum Server Features
- MCP protocol support:
  - `initialize` and capability negotiation.
  - Tool discovery/listing.
  - Tool invocation path with structured request/response handling.
  - Remote MCP transport behavior aligned to the selected standards-compliant transport profile.
- Operational endpoints:
  - `GET /health` for liveness.
  - `GET /ready` for readiness (including config checks).
- Baseline tools (no external APIs):
  - `server_ping`: returns service status and timestamp.
  - `server_info`: returns version, environment, and build metadata.
  - `server_list_tools`: returns currently registered tool names/descriptions.
- Foundation retrieval tools:
  - `search`: returns deep research-compatible search results in MCP-compatible content format.
  - `fetch`: returns deep research-compatible fetched content in MCP-compatible content format.
  - If the target integration is OpenAI ChatGPT apps, deep research, or company knowledge, `search` and `fetch` must follow the current OpenAI compatibility contract rather than an internal-only retrieval shape.

### 5.3 Foundation Architecture Requirements
- Layered modules:
  - Transport layer (remote MCP transport handling and MCP message flow).
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
- Hosted readiness must also reflect missing or unusable hosted dependencies that are required for the selected deployment mode.

### 5.5 Error Handling and Validation Requirements
- Central error mapper to normalize internal exceptions into MCP-safe responses.
- Input validation at tool boundary (JSON schema).
- Error shape must include protocol-aligned `code`, `message`, and optional `details`.
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
- Dedicated local environment defaults documented separately from hosted deployment inputs.
- `.env.example` included with documented variables.
- README section: local startup + MCP client connection instructions.
- Local verification path for the selected remote MCP transport documented.
- Local execution MUST remain possible without provisioning cloud infrastructure first.
- If hosted-like local verification requires supporting dependencies such as a durable session backend, that path MUST be reproducible and documented separately from the minimal local run path.

### 5.8 Cloud Run Standup Requirements (Phase 0)
- Build container image for server.
- Deploy one Cloud Run revision with:
  - runtime service account.
  - min/max instances.
  - concurrency and timeout configured.
  - required env vars + secret references.
  - explicit public reachability configuration appropriate for remote MCP consumers.
  - required IAM and network wiring for Secret Manager and durable session connectivity.
  - Terraform-managed VPC/subnet/connector resources required for the hosted session-connectivity model.
- Deployment automation MUST be able to execute the full hosted rollout path without relying on an image-only Cloud Run update.
- Verify:
  - `/health` and `/ready` pass.
  - Hosted MCP transport verification passes against deployed URL.
  - MCP initialize/list tools/invoke baseline tools works against deployed URL.
  - Hosted `search` and `fetch` verification paths are documented and executable.
  - Hosted MCP session continuation succeeds under the supported Cloud Run session model.
  - Failed `initialize` requests do not create hosted sessions or return continuation headers.
  - Cloud Run IAM/public-access failures can be distinguished from MCP-layer auth failures.
  - If browser-originated clients are in scope, approved browser access and denied-origin behavior are both verified.
  - Required hosted infrastructure dependencies can be provisioned reproducibly from versioned infrastructure definitions.
  - Automated deployment fails when hosted verification fails.

### 5.9 Foundation Acceptance Criteria (Exit Gate for Tool Work)
- MCP server successfully initializes from an MCP client.
- Hosted MCP transport is compatible with the selected remote MCP profile for downstream consumers.
- Baseline tools can be listed and invoked end-to-end.
- Tool discovery returns complete MCP-relevant metadata for registered tools.
- Tool invocation returns MCP-compatible result structures.
- `search` and `fetch` are available and callable end-to-end.
- OpenAI-targeted retrieval mode, if claimed as supported, uses the currently documented OpenAI-compatible `search` / `fetch` contract.
- Hosted MCP session behavior is reliable for the supported Cloud Run deployment model.
- Failed initialize handshakes do not leave behind usable hosted sessions.
- Retrieval tool schemas are complete enough for clients to construct valid calls from discovery output alone.
- Error codes follow the protocol conventions expected by supported MCP consumers.
- Hosted infrastructure dependencies are reproducible from versioned IaC for the supported deployment path.
- Hosted deployment includes the provider-specific IAM and network wiring needed for secrets and durable session state.
- Hosted deployment does not depend on manually created VPC, subnet, or VPC connector resources outside the supported IaC path.
- Local runtime and verification workflows remain supported after infrastructure automation is introduced.
- Push-triggered hosted deployment is driven by checked-in automation rather than console-only configuration drift.
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
  - MCP-compatible tool metadata sufficient for discovery and invocation.
  - MCP-compatible structured output.
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
- Support the selected remote MCP transport behavior reliably in the hosted Cloud Run environment.
- Document and enforce the hosted session strategy required to keep MCP session continuity reliable under Cloud Run.
- Make the hosted service publicly reachable for trusted remote MCP consumers by explicit Cloud Run configuration, not by assumption.
- Document how Cloud Run public reachability interacts with MCP-layer authentication so operators do not confuse network reachability with application authorization.
- Provider-specific infrastructure must include the IAM and network plumbing required for runtime secret access and durable hosted session storage.
- Provider-specific infrastructure must also provision the network resources required to support that wiring, including VPC, subnets, and VPC connector resources when applicable.
- Prefer a single checked-in automation workflow that performs infrastructure reconcile, application deploy, and hosted verification over a build-only or image-only update path.
- Prefer reproducible infrastructure provisioning for Cloud Run, secrets, and durable hosted dependencies over manual console-only setup.

## 10. Security and Compliance Requirements
- Secrets stored and injected securely.
- Input validation for all tool parameters.
- Output sanitization to avoid leaking internal stack traces.
- Audit-friendly logs (request ID, tool name, latency, status).
- Rate limiting or request throttling guardrails for abuse prevention.
- For transcript/caption tools, enforce authorization checks and explicit errors when caption access is not permitted.
- Remote MCP transport must include origin-aware handling and a documented authentication strategy appropriate for hosted consumption.
- If browser-originated access is supported, the hosted service must provide explicit CORS and preflight behavior for approved and denied browser clients.

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
- One-command local startup workflow documented and maintained.
- Simple deployment command(s) documented for Cloud Run.
- Tool-by-tool usage examples with sample payloads.
- Automated checks for lint/type/test in CI.
- Remote MCP connection guidance documented for OpenAI Agent Builder and comparable MCP consumers.
- Documentation distinguishes generic remote MCP usage from OpenAI-specific retrieval compatibility requirements.
- Infrastructure provisioning guidance documented for the supported hosted platforms.
- Documentation distinguishes local runtime env files from hosted deployment env/config inputs.

## 14. Acceptance Criteria (v1)
- Phase 0 foundation acceptance criteria are fully met.
- Remote MCP transport is usable by intended hosted consumers.
- `search` and `fetch` are implemented and callable via MCP for deep research-oriented flows.
- If OpenAI ChatGPT apps / deep research compatibility is claimed, `search` and `fetch` match the currently documented OpenAI compatibility contract.
- Hosted session continuity is reliable for the supported deployment model.
- Failed initialize requests do not create or expose hosted continuation sessions.
- Tool discovery metadata is sufficient for supported MCP clients to construct valid foundational tool requests.
- Error codes and error payloads match the supported protocol expectations for downstream consumers.
- All 16 tools in Sections 6.1-6.4 are implemented and callable via MCP.
- Every tool validates inputs and returns structured errors.
- Cloud Run deployment succeeds and serves MCP traffic.
- Cloud Run deployment is publicly reachable to trusted remote MCP consumers using an explicit documented configuration.
- Secrets are managed through Secret Manager.
- Automated deployment reconciles infrastructure, rolls out the application revision, and runs hosted verification as part of the supported path.
- Automated deployment provisions the required hosted network resources through IaC rather than relying on pre-existing manual VPC/subnet/connector configuration.
- Logs and core metrics are visible in Google Cloud.
- README includes setup, config, run, and deploy instructions.
- Composite tools are clearly documented where behavior is not provided by a single native YouTube endpoint (playlist search and transcript text search).

## 15. Milestones
1. Complete MCP server foundation (transport, registry, baseline tools, health endpoints).
2. Align foundation transport and protocol behavior to a standards-compliant remote MCP profile.
3. Add foundation `search` and `fetch` support for deep research-compatible flows.
4. Make hosted MCP sessions reliable for the supported Cloud Run routing and scaling model.
5. Complete browser/CORS behavior and remaining hosted access hardening for supported client types.
6. Finish foundational retrieval schema completeness and protocol-aligned error-code behavior.
7. Add Infrastructure as Code for the hosted platform and durable-session dependencies.
8. Organize infrastructure around a cloud-agnostic platform contract with provider-specific adapters where needed.
9. Make Cloud Run publicly reachable in the documented way required for remote MCP consumers.
10. Complete provider-specific IAM and network wiring for Secret Manager and durable hosted session dependencies.
11. Align foundational retrieval tools to the OpenAI compatibility contract for ChatGPT apps / deep research where that integration is in scope.
12. Correct initialize/session lifecycle behavior so failed handshakes do not create hosted sessions.
13. Check in a full push-triggered deployment pipeline that reconciles infrastructure, deploys the application, and verifies the hosted MCP endpoint.
14. Provide a one-command local startup workflow with dedicated local runtime environment defaults.
15. Provision Terraform-managed hosted networking, including VPC, subnets, and Cloud Run connectivity resources required for durable hosted sessions.
16. Stand up Cloud Run deployment for the expanded foundation build and validate end-to-end hosted MCP behavior.
17. Define YouTube tool schemas and response contracts.
18. Implement video/channel/playlist tools.
19. Implement transcript retrieval/search flows.
20. Add auth, secrets, and quota/error handling hardening.
21. Add monitoring, alerts, and release documentation.

## 16. Open Decisions
- Final transcript fallback approach when official captions are unavailable.
- Required auth model for private/unlisted resource access (if in scope later).
- Caching policy (TTL, storage backend, invalidation strategy).
- Transcript scope decision: owner-authorized captions only vs optional non-YouTube fallback for broader public coverage.
- Final MCP transport profile details for production clients, including whether any secondary transport modes beyond the primary remote MCP profile should be supported.
- Whether OpenAI-targeted support means generic remote MCP only, or the stricter ChatGPT apps / deep research retrieval compatibility contract.
- Which parts of secret-value population remain operator-managed versus automated after the initial platform bootstrap.
