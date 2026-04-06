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
- Use a layered product model so low-level YouTube integrations and higher-level research-oriented tools can evolve independently.
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
- Product layers for YouTube capability:
  - Layer 1: integration layer that wraps YouTube Data API and transcript providers through typed internal abstractions.
  - Layer 2: lower-level MCP tools that expose raw or near-raw YouTube resource operations for power users, debugging, and direct endpoint access.
  - Layer 3: higher-level MCP tools that normalize, enrich, filter, combine, and rank YouTube data for research workflows.
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

### 6.1 Layered YouTube Capability Model
- Layer 1 is the internal integration layer:
  - typed wrappers around YouTube Data API resources and transcript providers
  - request shaping, retry behavior, quota/error mapping, and auth handling
  - reusable enrichment helpers that can be shared by multiple public tools
  - required for the initial release as the implementation foundation for Layers 2 and 3
- Layer 2 is the low-level public MCP layer for v1:
  - near-direct exposure of documented YouTube Data API resource operations
  - one public MCP tool per documented YouTube Data API endpoint/resource method in the supported inventory
  - useful for debugging, raw exploration, direct endpoint access, and advanced power-user workflows
- Layer 3 is the higher-level public MCP tool layer for v1:
  - the primary research-oriented user-facing tool catalog
  - tools may combine multiple YouTube endpoints and local heuristics
  - tools may perform ETL-style normalization, filtering, enrichment, and ranking before returning results
- Initial scope decision:
  - Layer 1 is required for implementation support.
  - Layer 2 is part of the public v1 tool surface.
  - Layer 3 is also part of the public v1 tool surface.
  - Layer 2 and Layer 3 serve different user needs and are both first-class public layers.

### 6.2 Layer 1 Integration Requirements
- The Layer 1 integration layer MUST serve as the internal endpoint-wrapper layer for the documented YouTube Data API v3 surface used by this product.
- The Layer 1 integration layer MUST begin with shared internal scaffolding for:
  - request execution
  - API key and OAuth credential injection
  - retry and backoff hooks
  - request and response logging hooks
  - upstream error normalization
  - endpoint metadata declaration
- The Layer 1 integration layer MUST expose typed wrappers for each currently documented YouTube Data API v3 endpoint/resource method included in the Layer 1 workstream, not only the subset immediately needed by the first Layer 3 tools.
- For each endpoint/resource method in scope, the corresponding Layer 1 wrapper MUST implement the concrete upstream YouTube Data API call, not only a wrapper contract, metadata surface, validation layer, or fake transport used in tests.
- A Layer 1 endpoint slice is incomplete unless it includes:
  - real request parameter shaping for the named upstream endpoint
  - credential attachment for the supported auth modes
  - outbound HTTP execution against the real YouTube Data API path
  - parsing of successful upstream responses into the Layer 1 result shape
  - normalization of upstream failures into the shared Layer 1 error model
- Test doubles, injected fake transports, or mock executor paths MAY be used in tests, but they MUST NOT be the only implemented execution path for a Layer 1 endpoint slice.
- Every Layer 1 wrapper MUST record:
  - resource and method name
  - HTTP method and path shape
  - official YouTube Data API quota-unit cost
  - auth mode (`api_key`, `oauth_required`, or mixed/conditional)
  - deprecation or availability state when applicable
- Method signatures, docstrings, or adjacent implementation comments for Layer 1 wrappers MUST explicitly include the official quota-unit cost for that endpoint.
- The Layer 1 integration layer MUST support server-side composition where a Layer 3 tool depends on multiple upstream resources.
- The Layer 1 integration layer MUST support direct exposure through Layer 2 tools without requiring each Layer 2 tool to duplicate request execution, auth, quota, or upstream error logic.
- The Layer 1 integration layer MUST keep upstream API naming and transport details out of Layer 3 tool handlers wherever practical.
- The Layer 1 integration layer MUST explicitly document or flag known official-doc inconsistencies encountered during endpoint inventorying, especially around quota or availability/deprecation behavior.

### 6.2.1 Layer 2 Public Endpoint Tool Requirements
- The Layer 2 public MCP layer MUST expose one endpoint-backed tool for each documented YouTube Data API v3 resource method included in the supported Layer 1 inventory.
- Layer 2 public tool names MUST follow `resource_method` naming such as:
  - `videos_list`
  - `playlists_insert`
  - `comments_setModerationStatus`
  - `videos_getRating`
- Layer 2 tools MUST stay close to upstream request and response semantics while remaining usable through MCP-compatible descriptions, validation, and structured results.
- Layer 2 tool definitions MUST explicitly document:
  - mapped YouTube resource and method
  - official quota-unit cost
  - auth mode (`api_key`, `oauth_required`, or mixed/conditional)
  - deprecation or availability caveats when applicable
- Layer 2 tools MAY lightly normalize upstream payloads for MCP clarity, but they MUST NOT masquerade as higher-level composed or heuristic tools.
- Layer 2 tools SHOULD preserve upstream pagination, part-selection, and filter concepts where those concepts exist upstream.

### 6.3 Required Upstream API Surface
- Primary data source: YouTube Data API v3.
- Layer 1 endpoint inventory target:
  - `activities.list`
  - `captions.list`, `captions.insert`, `captions.update`, `captions.download`, `captions.delete`
  - `channelBanners.insert`
  - `channels.list`, `channels.update`
  - `channelSections.list`, `channelSections.insert`, `channelSections.update`, `channelSections.delete`
  - `comments.list`, `comments.insert`, `comments.update`, `comments.setModerationStatus`, `comments.delete`
  - `commentThreads.list`, `commentThreads.insert`
  - `guideCategories.list`
  - `i18nLanguages.list`, `i18nRegions.list`
  - `members.list`, `membershipsLevels.list`
  - `playlistImages.list`, `playlistImages.insert`, `playlistImages.update`, `playlistImages.delete`
  - `playlistItems.list`, `playlistItems.insert`, `playlistItems.update`, `playlistItems.delete`
  - `playlists.list`, `playlists.insert`, `playlists.update`, `playlists.delete`
  - `search.list`
  - `subscriptions.list`, `subscriptions.insert`, `subscriptions.delete`
  - `thumbnails.set`
  - `videoAbuseReportReasons.list`
  - `videoCategories.list`
  - `videos.list`, `videos.insert`, `videos.update`, `videos.rate`, `videos.getRating`, `videos.reportAbuse`, `videos.delete`
  - `watermarks.set`, `watermarks.unset`
- Layer 2 public endpoint tools map one-to-one to that inventory.
- Layer 3 public tools depend on a smaller subset of that inventory, but the Layer 1 product requirement is intentionally broader so the integration layer can support both Layer 2 and future Layer 3 additions without redesign.
- The system MUST maintain a documented per-endpoint quota inventory for the Layer 1 wrappers so downstream tool authors can reason about daily-credit impact before composing multi-call workflows.
- The system MUST maintain equivalent quota visibility in Layer 2 public tool documentation so callers can reason about direct endpoint costs before invocation.
- The system MUST explicitly document which Layer 3 tools depend on single endpoints versus composite multi-endpoint workflows.
- The system MUST distinguish raw upstream fields from server-derived normalized or heuristic fields in the public contract documentation.

### 6.3.1 Layer 2 Public Endpoint Tool Mapping
- Layer 2 exposes one public MCP tool per documented YouTube Data API endpoint/resource method in Section 6.3.
- The Layer 2 public catalog includes the following tool families:
  - `activities_list`
  - `captions_list`, `captions_insert`, `captions_update`, `captions_download`, `captions_delete`
  - `channelBanners_insert`
  - `channels_list`, `channels_update`
  - `channelSections_list`, `channelSections_insert`, `channelSections_update`, `channelSections_delete`
  - `comments_list`, `comments_insert`, `comments_update`, `comments_setModerationStatus`, `comments_delete`
  - `commentThreads_list`, `commentThreads_insert`
  - `guideCategories_list`
  - `i18nLanguages_list`, `i18nRegions_list`
  - `members_list`, `membershipsLevels_list`
  - `playlistImages_list`, `playlistImages_insert`, `playlistImages_update`, `playlistImages_delete`
  - `playlistItems_list`, `playlistItems_insert`, `playlistItems_update`, `playlistItems_delete`
  - `playlists_list`, `playlists_insert`, `playlists_update`, `playlists_delete`
  - `search_list`
  - `subscriptions_list`, `subscriptions_insert`, `subscriptions_delete`
  - `thumbnails_set`
  - `videoAbuseReportReasons_list`
  - `videoCategories_list`
  - `videos_list`, `videos_insert`, `videos_update`, `videos_rate`, `videos_getRating`, `videos_reportAbuse`, `videos_delete`
  - `watermarks_set`, `watermarks_unset`
- Layer 2 tools MUST keep a clear one-to-one relationship with their upstream endpoint identity even when the MCP contract applies light validation or payload reshaping.

### 6.3.2 Initial Layer 3 Endpoint-to-Tool Mapping
- `videos_getVideo`
  - primary dependency: `videos.list`
- `videos_searchVideos`
  - primary dependency: `search.list`
  - optional enrichment/filtering dependency: `channels.list`
- `videos_getStatistics`
  - primary dependency: `videos.list`
- `transcripts_getTranscript`
  - primary dependencies: `captions.list`, `captions.download`
- `transcripts_listLanguages`
  - primary dependency: `captions.list`
- `transcripts_getTimestampedCaptions`
  - primary dependencies: `captions.list`, `captions.download`
- `transcripts_searchTranscript`
  - primary dependencies: transcript retrieval flow plus in-server text search
- `channels_getChannel`
  - primary dependency: `channels.list`
  - optional enrichment dependency for latest upload metadata: `search.list` or uploads-playlist path
- `channels_getChannels`
  - primary dependency: `channels.list`
  - optional enrichment dependency for latest upload metadata: `search.list` or uploads-playlist path
- `channels_searchChannels`
  - primary dependency: `search.list`
  - optional enrichment/filtering dependency: `channels.list`
- `channels_findCreators`
  - primary dependencies: `search.list`, `channels.list`
  - optional enrichment dependency for latest upload/activity and sample videos: uploads-playlist path or additional `search.list` calls
- `channels_listVideos`
  - primary dependency: `search.list` or uploads-playlist path
  - uploads-playlist path dependencies: `channels.list`, `playlistItems.list`
- `channels_listPlaylists`
  - primary dependency: `playlists.list`
- `channels_getStatistics`
  - primary dependency: `channels.list`
- `channels_searchContent`
  - primary dependency: `search.list`
- `playlists_getPlaylist`
  - primary dependency: `playlists.list`
- `playlists_getPlaylistItems`
  - primary dependency: `playlistItems.list`
- `playlists_searchItems`
  - primary dependencies: `playlistItems.list` plus in-server filtering
- `playlists_getVideoTranscripts`
  - primary dependencies: `playlistItems.list` plus transcript retrieval flow

### 6.4 Initial Layer 3 Public Tool Catalog
The initial public Layer 3 catalog contains 19 MCP tools.

#### 6.4.1 `videos_getVideo`
- Purpose:
  - return detailed information about a YouTube video in one normalized response
- Required parameters:
  - `videoId` string
- Optional parameters:
  - `parts` string[]
- Minimum output expectations:
  - normalized core video metadata
  - selected part coverage based on `parts` when provided
  - stable fields for agent consumption

#### 6.4.2 `videos_searchVideos`
- Purpose:
  - search for videos on YouTube with optional channel- and creator-oriented refinement
- Required parameters:
  - `query` string
- Optional parameters:
  - `maxResults` number
  - `order` string
  - `publishedAfter` string (ISO 8601)
  - `publishedBefore` string (ISO 8601)
  - `channelId` string
  - `uniqueChannels` boolean
  - `channelMinSubscribers` number
  - `channelMaxSubscribers` number
  - `channelLastUploadAfter` string (ISO 8601)
  - `channelLastUploadBefore` string (ISO 8601)
  - `creatorOnly` boolean
  - `sortBy` string
- Required behavior:
  - support direct YouTube search behavior for the base query
  - support post-search enrichment and filtering by matched channel metadata
  - support one-result-per-channel behavior when `uniqueChannels=true`
  - support ranking modes including relevance, subscriber-based ordering, indie-priority, and recent-activity

#### 6.4.3 `videos_getStatistics`
- Purpose:
  - return statistics for a single YouTube video
- Required parameters:
  - `videoId` string
- Optional parameters:
  - none
- Required behavior:
  - return available counts such as views, likes, comments, and favorites where available
  - document how hidden or unavailable counts are represented

#### 6.4.4 `transcripts_getTranscript`
- Purpose:
  - retrieve the transcript of a YouTube video
- Required parameters:
  - `videoId` string
- Optional parameters:
  - `language` string
- Required behavior:
  - support transcript language selection
  - fall back to `YOUTUBE_TRANSCRIPT_LANG` or `en` when explicit language is not provided
  - document auth-sensitive behavior when official caption access is required

#### 6.4.5 `transcripts_listLanguages`
- Purpose:
  - list transcript or caption languages available for a video
- Required parameters:
  - `videoId` string
- Optional parameters:
  - none
- Required behavior:
  - expose the language choices and any available track metadata the public contract chooses to surface
  - document auth-sensitive limitations where applicable

#### 6.4.6 `transcripts_getTimestampedCaptions`
- Purpose:
  - return caption segments with explicit timestamp boundaries
- Required parameters:
  - `videoId` string
- Optional parameters:
  - `language` string
- Required behavior:
  - return start/end or equivalent timing information per segment
  - document auth-sensitive behavior when official caption access is required

#### 6.4.7 `transcripts_searchTranscript`
- Purpose:
  - search transcript text and return matching snippets with timing
- Required parameters:
  - `videoId` string
  - `query` string
- Optional parameters:
  - `language` string
  - `maxMatches` number
- Required behavior:
  - this is a composite higher-level tool built on transcript retrieval plus in-server text search
  - document match ranking, snippet extraction, and timestamp behavior clearly

#### 6.4.8 `channels_getChannel`
- Purpose:
  - return information about a single YouTube channel
- Required parameters:
  - `channelId` string
- Optional parameters:
  - none
- Required output enrichment:
  - `latestVideoPublishedAt`
  - `normalizedMetadata`
  - `normalizedMetadata.country`
  - `normalizedMetadata.defaultLanguage`
  - `normalizedMetadata.joinedAt`
  - `normalizedMetadata.customUrl`
  - `normalizedMetadata.emailsFound`
  - `normalizedMetadata.contactLinks`
  - creator-versus-brand heuristic fields

#### 6.4.9 `channels_getChannels`
- Purpose:
  - return information about multiple YouTube channels in one request
- Required parameters:
  - `channelIds` string[]
- Optional parameters:
  - `parts` string[]
  - `includeLatestUpload` boolean
- Required behavior:
  - support batch retrieval and normalization
  - optionally suppress latest-upload enrichment when `includeLatestUpload=false`

#### 6.4.10 `channels_searchChannels`
- Purpose:
  - search for channels by handle, channel name, or general query
- Required parameters:
  - `query` string
- Optional parameters:
  - `maxResults` number
  - `order` string
  - `channelType` string
  - `minSubscribers` number
  - `maxSubscribers` number
  - `lastUploadAfter` string (ISO 8601)
  - `lastUploadBefore` string (ISO 8601)
  - `creatorOnly` boolean
  - `sortBy` string
- Required behavior:
  - support both upstream channel discovery and server-side enrichment/filtering
  - support creator-focused filtering and ranking modes

#### 6.4.11 `channels_findCreators`
- Purpose:
  - discover creator channels from matched or mentioning videos and then rank/filter the resulting channels
- Required parameters:
  - `query` string
- Optional parameters:
  - `maxResults` number
  - `order` string
  - `videoPublishedAfter` string (ISO 8601)
  - `videoPublishedBefore` string (ISO 8601)
  - `channelMinSubscribers` number
  - `channelMaxSubscribers` number
  - `channelLastUploadAfter` string (ISO 8601)
  - `channelLastUploadBefore` string (ISO 8601)
  - `creatorOnly` boolean
  - `sortBy` string
  - `sampleVideosPerChannel` number
- Required behavior:
  - this is a composite higher-level tool, not a single-endpoint passthrough
  - it may search matched videos first, then derive and enrich candidate channels
  - it must document the ranking, filtering, and sample-video inclusion rules clearly

#### 6.4.12 `channels_listVideos`
- Purpose:
  - get videos from a specific channel
- Required parameters:
  - `channelId` string
- Optional parameters:
  - `maxResults` number
- Required behavior:
  - support deterministic listing behavior appropriate for the chosen implementation path
  - document whether the implementation uses ranked search behavior, uploads-playlist behavior, or both

#### 6.4.13 `channels_listPlaylists`
- Purpose:
  - get playlists from a specific channel
- Required parameters:
  - `channelId` string
- Optional parameters:
  - `maxResults` number
- Required behavior:
  - return normalized playlist list results that align with the playlist tool family

#### 6.4.14 `channels_getStatistics`
- Purpose:
  - return statistics for a single YouTube channel
- Required parameters:
  - `channelId` string
- Optional parameters:
  - none
- Required behavior:
  - return available counts such as subscribers, videos, and views where available
  - document how hidden or unavailable counts are represented

#### 6.4.15 `channels_searchContent`
- Purpose:
  - search within the content of a specific channel
- Required parameters:
  - `channelId` string
  - `query` string
- Optional parameters:
  - `maxResults` number
  - `order` string
- Required behavior:
  - document when the behavior is direct upstream search versus additional in-server shaping

#### 6.4.16 `playlists_getPlaylist`
- Purpose:
  - return information about a playlist
- Required parameters:
  - `playlistId` string
- Optional parameters:
  - none

#### 6.4.17 `playlists_getPlaylistItems`
- Purpose:
  - return the videos contained in a playlist
- Required parameters:
  - `playlistId` string
- Optional parameters:
  - `maxResults` number

#### 6.4.18 `playlists_searchItems`
- Purpose:
  - search within a playlist for matching items
- Required parameters:
  - `playlistId` string
  - `query` string
- Optional parameters:
  - `maxResults` number
- Required behavior:
  - this is a composite higher-level tool rather than a single-endpoint passthrough
  - document matching and result-shaping behavior clearly

#### 6.4.19 `playlists_getVideoTranscripts`
- Purpose:
  - retrieve transcript data for videos contained in a playlist
- Required parameters:
  - `playlistId` string
- Optional parameters:
  - `language` string
  - `maxResults` number
- Required behavior:
  - this is a composite higher-level tool built from playlist enumeration plus transcript retrieval
  - document bounded fan-out behavior and auth-sensitive limitations explicitly

### 6.5 Layer 3 Contract Rules
- Layer 3 tools MUST use stable MCP-facing parameter names rather than raw YouTube API parameter names.
- Layer 3 tools MAY combine multiple upstream resources before returning a response.
- Layer 3 tools MAY add derived fields, normalized fields, and heuristic classifications when those fields are documented explicitly.
- Layer 3 tools MUST distinguish:
  - raw upstream fields
  - normalized fields
  - heuristic or inferred fields
- Layer 3 tools MUST return enough structured output that downstream agents can use them without having to understand raw YouTube API response shapes.
- Defaults, bounds, and result-shaping behavior for repeated parameters such as `maxResults`, `parts`, and language fallback MUST be documented in the final tool contract before implementation begins.

## 7. MCP Tool Contract Requirements
- Each tool must include:
  - Clear name and description.
  - JSON schema input validation.
  - MCP-compatible tool metadata sufficient for discovery and invocation.
  - MCP-compatible structured output.
  - Structured error model (`code`, `message`, `details`).
- Consistent pagination fields (`nextPageToken`, `pageSize`, `totalResults` when available).
- Deterministic parameter names across tools (e.g., `videoId`, `channelId`, `playlistId`, `query`, `language`), with explicit mapping to YouTube terms (`query -> q`, `pageSize -> maxResults`).
- Layer 3 public tool names SHOULD avoid redundant provider prefixes when the repository context already makes the provider obvious.
- The initial public Layer 3 catalog uses grouped names such as `videos_*`, `channels_*`, `playlists_*`, and `transcripts_*`.
- Tool contracts MUST explicitly document optional filters and ranking fields whose behavior is implemented partly in-server rather than directly by a single upstream YouTube endpoint.

## 8. API and Data Requirements
- Primary data source: YouTube Data API v3.
- Layer 1 integration inventory must cover the currently documented YouTube Data API v3 endpoint/resource methods listed in Section 6.3.
- The highest-impact quota methods MUST be especially visible in Layer 1 documentation and implementation notes, including but not limited to:
  - `search.list` at `100` units
  - `captions.insert` at `400` units
  - `captions.update` at `450` units
  - `captions.download` at `200` units
  - `videos.insert` at `1600` units
- Layer 3 implementation planning should assume that composite workflows multiply upstream quota usage and should document that impact when a public tool fans out across multiple resources.
- Endpoint alignment notes:
  - Search workflows use `search.list` with resource-specific filtering where appropriate.
  - Channel video listing can use either:
    - `search.list` with `channelId` for ranked/discoverability behavior.
    - Uploads playlist flow (`channels.list` -> `contentDetails.relatedPlaylists.uploads` -> `playlistItems.list`) for deterministic exhaustive listing.
  - Creator-finding and advanced channel/video filters may require composite server-side workflows that enrich search results with channel data before final filtering and ranking.
- Transcript source strategy:
  - Official path: `captions.list(videoId)` and `captions.download(captionTrackId)`.
  - These endpoints require OAuth authorization context for the target caption track.
  - Any public transcript fallback (if used) must be explicitly documented as non-YouTube-Data-API behavior.
- Data-shaping rules:
  - public Layer 3 responses may include raw upstream fields, normalized fields, and heuristic fields
  - normalized and heuristic fields must be documented clearly in the public tool contract
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
- All Layer 2 endpoint-backed tools in the supported inventory are implemented and callable via MCP.
- All 19 initial Layer 3 tools in Section 6.4 are implemented and callable via MCP.
- Every tool validates inputs and returns structured errors.
- Cloud Run deployment succeeds and serves MCP traffic.
- Cloud Run deployment is publicly reachable to trusted remote MCP consumers using an explicit documented configuration.
- Secrets are managed through Secret Manager.
- Automated deployment reconciles infrastructure, rolls out the application revision, and runs hosted verification as part of the supported path.
- Automated deployment provisions the required hosted network resources through IaC rather than relying on pre-existing manual VPC/subnet/connector configuration.
- Logs and core metrics are visible in Google Cloud.
- README includes setup, config, run, and deploy instructions.
- Composite higher-level tools are clearly documented where behavior is not provided by a single native YouTube endpoint.
- The public documentation distinguishes the internal Layer 1 integration layer from the public Layer 2 and Layer 3 tool catalogs.
- The public documentation distinguishes Layer 2 near-raw endpoint tools from Layer 3 higher-level composed tools.
- The public documentation identifies which Layer 3 fields are raw upstream values versus normalized or heuristic values.
- The product requirements and implementation planning document Layer 1 as an endpoint-by-endpoint YouTube Data API integration inventory rather than an ad hoc set of helper calls.
- Layer 1 wrapper standards require per-endpoint quota-cost documentation in metadata plus method-level comments/docstrings.
- Layer 2 public tool contracts expose per-endpoint quota cost, auth mode, and deprecation or availability caveats clearly.

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
17. Define the layered YouTube product model plus the public Layer 2 and Layer 3 tool taxonomies.
18. Define the Layer 1 shared client foundation, endpoint metadata/quota standards, and full documented YouTube Data API endpoint inventory.
19. Implement the Layer 1 endpoint wrappers.
20. Implement the Layer 2 endpoint-backed public MCP catalog with per-endpoint quota/auth/deprecation documentation.
21. Implement the Layer 3 core public tools.
22. Implement the additional Layer 3 value-add tools for statistics, transcript discovery/search, channel playlist/content workflows, and playlist transcript/search workflows.
23. Add auth, secrets, quota/error handling, and transcript-access hardening across low-level and composed public workflows.
24. Add monitoring, alerts, and release documentation.

## 16. Open Decisions
- Final transcript fallback approach when official captions are unavailable.
- Required auth model for private/unlisted resource access (if in scope later).
- Caching policy (TTL, storage backend, invalidation strategy).
- Transcript scope decision: owner-authorized captions only vs optional non-YouTube fallback for broader public coverage.
- Final MCP transport profile details for production clients, including whether any secondary transport modes beyond the primary remote MCP profile should be supported.
- Whether OpenAI-targeted support means generic remote MCP only, or the stricter ChatGPT apps / deep research retrieval compatibility contract.
- Which parts of secret-value population remain operator-managed versus automated after the initial platform bootstrap.
