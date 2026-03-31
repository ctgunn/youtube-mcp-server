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
Implement `/health`, `/ready`, structured logs, normalized errors, and core metrics.

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
- Deployed revision passes `/health` and `/ready`.
- MCP initialize/list/invoke passes against Cloud Run endpoint.

Dependencies:
- `FND-003`, `FND-004`, `FND-005`

### FND-007: Hosted Probe Semantics + HTTP Hardening
Description:
Harden the hosted HTTP surface so Cloud Run probes and operators can rely on transport-level status codes and consistent endpoint behavior.

Primary stories:
- As an operator, I can trust probe responses because `/health` and `/ready` use correct HTTP semantics.
- As an MCP client, I receive predictable HTTP behavior for supported and unsupported hosted routes.

Acceptance criteria:
- Hosted `/ready` returns a non-success HTTP status when the instance is not ready.
- Hosted `/health`, `/ready`, and `/mcp` use consistent content-type and request/response handling.
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

### FND-009: MCP Streamable HTTP Transport
Description:
Replace the current request/response-only hosted MCP endpoint with standards-aligned MCP streamable HTTP transport so remote MCP consumers can establish compliant hosted sessions over Cloud Run.

Primary stories:
- As an MCP consumer, I can connect to one hosted MCP endpoint using a transport compatible with modern MCP clients.
- As a platform integrator, I can use this server with OpenAI Agent Builder and other MCP-capable services without relying on a custom transport contract.

Acceptance criteria:
- The MCP endpoint supports the streamable HTTP transport contract defined by the MCP specification.
- The MCP endpoint supports both `GET` and `POST` semantics required by the selected transport behavior.
- Streaming responses and server-driven events are supported where required by the transport contract.
- Existing Cloud Run deployment remains compatible with the hosted MCP entrypoint.
- Transport behavior is documented with concrete local and hosted verification steps.

Dependencies:
- `FND-008`

### FND-010: MCP Protocol Contract Alignment
Description:
Align request, response, error, and lifecycle behavior with the MCP protocol contract so the server is a true MCP server rather than a custom MCP-like HTTP API.

Primary stories:
- As an MCP client, I receive protocol-native responses and errors that conform to MCP expectations.
- As a developer, I can reason about hosted behavior using the official MCP contract instead of a server-specific wrapper.

Acceptance criteria:
- Request handling and response payloads conform to the selected MCP protocol contract rather than the current custom `success/data/meta/error` envelope.
- Initialization, tool listing, tool invocation, and unsupported-method handling follow MCP-compatible semantics.
- Protocol error mapping is documented and validated against contract tests.
- Hosted and local behavior remain consistent across initialize, list, call, and failure scenarios.

Dependencies:
- `FND-009`

### FND-011: Tool Metadata + Invocation Result Alignment
Description:
Expand the tool registry and invocation layer so tool discovery exposes full MCP-relevant metadata and tool execution returns MCP-compatible result content structures.

Primary stories:
- As an MCP client, I can discover complete tool definitions including schemas needed for invocation.
- As an MCP client, I receive tool results in a content structure that downstream agents can consume reliably.

Acceptance criteria:
- Tool discovery returns complete tool metadata including input schema and any required MCP-facing fields.
- Tool invocation responses return MCP-compatible result content instead of the current simplified tool wrapper.
- Baseline tools are updated to the new metadata and result contract without regressions in discoverability.
- Registry and dispatcher abstractions remain extensible for later YouTube tool addition.

Dependencies:
- `FND-010`, `FND-002`, `FND-003`

### FND-012: Hosted Runtime Migration for Streaming MCP
Description:
Migrate the hosted server runtime from the current minimal `http.server` implementation to a production-appropriate streaming-capable runtime aligned with the project technology direction.

Primary stories:
- As an operator, I can run a hosted MCP server that supports streaming transport reliably on Cloud Run.
- As a developer, I can extend transport behavior without fighting low-level server limitations.

Acceptance criteria:
- Hosted runtime uses a streaming-capable application stack suitable for Cloud Run.
- Cloud Run entrypoint, container startup, and deployment artifacts are updated to the new runtime.
- Health/readiness behavior remains correct after the runtime migration.
- Streaming MCP flows can be exercised locally and on Cloud Run.

Dependencies:
- `FND-009`, `FND-006`

### FND-013: Remote MCP Security + Transport Hardening
Description:
Harden the remote MCP surface with origin-aware transport validation, documented authentication strategy, and security controls required for safe third-party MCP consumption.

Primary stories:
- As an operator, I can expose the MCP endpoint with clear transport security expectations.
- As a client integrator, I can understand what auth and request-origin behavior is required to consume the hosted server safely.

Acceptance criteria:
- Transport layer validates or explicitly handles `Origin`-related concerns appropriate to the chosen MCP transport.
- Remote authentication approach is defined and implemented to the degree required for hosted MCP consumption.
- Security-relevant failure cases are documented and surfaced with stable error behavior.
- Cloud Run deployment and runtime documentation reflect the hardened transport expectations.

Dependencies:
- `FND-009`, `FND-012`

### FND-014: Deep Research Tool Foundation (`search` + `fetch`)
Description:
Add foundational MCP-native retrieval tools required for deep research-style consumers before any YouTube domain-specific tool slices are introduced.

Primary stories:
- As an OpenAI workflow or deep research consumer, I can call `search` to discover relevant results.
- As an OpenAI workflow or deep research consumer, I can call `fetch` to retrieve a selected result in a consumable content format.

Acceptance criteria:
- `search` and `fetch` are registered as MCP tools with complete schemas and MCP-compatible result content.
- Tool behavior is documented for hosted MCP consumers, including sample requests and responses.
- Deep research-oriented invocation paths are covered by contract/integration tests.
- Baseline hosted verification includes successful discovery and invocation of `search` and `fetch`.

Dependencies:
- `FND-010`, `FND-011`, `FND-013`

### FND-015: Hosted MCP Session Durability
Description:
Eliminate process-local session fragility so hosted streamable MCP sessions remain usable under real Cloud Run routing, scaling, and restart behavior.

Primary stories:
- As an MCP consumer, I can initialize a hosted session and continue using it without random `session not found` failures caused by instance routing.
- As an operator, I can deploy the hosted MCP service on Cloud Run with confidence that session continuity does not depend on undocumented single-instance assumptions.

Acceptance criteria:
- Hosted MCP session behavior is reliable under the supported Cloud Run deployment topology and does not depend on process-local memory alone.
- Session establishment, follow-up `GET`, and follow-up `POST` flows remain valid across the supported hosted routing model.
- The deployment and verification story explicitly documents any required session-affinity, single-instance, or shared-state assumptions.
- Contract and integration coverage includes hosted session continuation and reconnect scenarios relevant to the chosen session strategy.

Dependencies:
- `FND-009`, `FND-012`, `FND-013`

### FND-016: Browser-Originated MCP Access + CORS Support
Description:
Complete the browser-facing hosted access contract by adding explicit preflight and response-header behavior for approved browser-originated MCP clients.

Primary stories:
- As a browser-originated MCP consumer, I can complete preflight and authenticated hosted requests when my origin is allowed.
- As an operator, I can distinguish supported browser access from denied browser access using stable transport behavior rather than implicit failures.

Acceptance criteria:
- Hosted MCP routes explicitly handle browser preflight behavior for supported paths and methods.
- Approved browser-originated requests receive the required CORS response headers for the documented access model.
- Disallowed origins and unsupported browser request patterns fail with stable documented behavior.
- Browser-originated verification coverage is added for both successful and denied hosted access scenarios.

Dependencies:
- `FND-013`

### FND-017: Retrieval Tool Contract Completeness
Description:
Complete the machine-readable tool contract for foundational retrieval tools so MCP clients can construct valid `search` and `fetch` calls from discovery output alone.

Primary stories:
- As an MCP client, I can infer a valid `fetch` request shape directly from tool discovery without trial-and-error.
- As a developer, I can rely on the published tool schema to describe real validation rules instead of deferring core requirements to runtime-only checks.

Acceptance criteria:
- `search` and `fetch` discovery metadata fully expresses the required invocation contract in machine-readable form.
- `fetch` metadata clearly represents the valid required-input combinations supported by the server.
- Runtime validation and discovered schema stay aligned for successful and failing calls.
- Contract examples and hosted verification evidence demonstrate that clients can construct valid retrieval requests from discovery output alone.

Dependencies:
- `FND-011`, `FND-014`

### FND-018: JSON-RPC / MCP Error Code Alignment
Description:
Align hosted and local error responses with the expected JSON-RPC / MCP error-code conventions so downstream clients do not have to tolerate server-specific error-code typing.

Primary stories:
- As an MCP client, I receive error responses whose code fields follow the expected protocol conventions.
- As a developer, I can map transport, validation, protocol, and tool failures through one documented error-code contract without mixing protocol-native and server-specific code formats.

Acceptance criteria:
- Error responses use protocol-aligned error-code types and documented mappings for covered transport, protocol, validation, and tool failure categories.
- Hosted and local error behavior remain consistent for equivalent malformed request, unsupported method, invalid argument, authentication, and tool execution scenarios.
- Client-visible error payloads remain safe and structured while removing ambiguous server-specific code typing.
- Contract and integration coverage prove the aligned error-code behavior for representative success-adjacent failure paths.

Dependencies:
- `FND-010`, `FND-013`

### FND-019: Infrastructure as Code Foundation
Description:
Introduce Infrastructure as Code for the hosted MCP platform so required infrastructure can be provisioned reproducibly rather than relying on manual cloud console setup.

Primary stories:
- As an operator, I can provision the infrastructure required by the hosted MCP service from versioned code.
- As a maintainer, I can review infrastructure changes alongside application changes and trust that required dependencies are created consistently.

Acceptance criteria:
- Infrastructure required for the hosted MCP foundation is defined in versioned IaC rather than only in manual setup steps.
- The IaC covers the currently required hosted dependencies, including application runtime infrastructure, secret/config integration points, and durable session backend requirements.
- Environment-specific inputs are documented and injectable without modifying application code.
- Operator documentation includes one reproducible infrastructure provisioning path and one reproducible application deployment path.
- Local execution remains supported without requiring cloud infrastructure provisioning as a prerequisite.
- Documentation distinguishes the minimum local runtime path from the full hosted-infrastructure provisioning path.
- If durable hosted dependencies such as Redis are needed for hosted-like local verification, that local dependency path is reproducible and documented separately from the cloud provisioning path.

Dependencies:
- `FND-015`, `FND-016`, `FND-017`, `FND-018`

### FND-020: Cloud-Agnostic Infrastructure Module Strategy
Description:
Design and implement a cloud-agnostic infrastructure layout so the MCP platform can be reproduced across supported providers without rewriting the application-level deployment model for each cloud.

Primary stories:
- As an operator, I can understand which infrastructure capabilities are required regardless of cloud provider.
- As a maintainer, I can add or adapt provider-specific infrastructure modules while preserving one shared platform contract for the MCP service.

Acceptance criteria:
- IaC is organized around provider-agnostic platform capabilities with provider-specific implementations where needed.
- The infrastructure contract identifies the shared requirements for hosted runtime, networking, secrets, observability integration, and durable session storage across supported clouds.
- At least one secondary provider path beyond the current primary cloud target is planned or scaffolded strongly enough to prove the layout is not locked to one provider-specific design.
- Documentation makes clear which parts of the infrastructure model are portable and which parts are provider-specific adapters.
- The provider-agnostic infrastructure layout preserves a first-class local runtime path for development and verification.
- Cloud-provider modules do not become a prerequisite for running the MCP server locally or for executing the minimal local verification workflow.
- Documentation explains how local execution, hosted-like local execution, and cloud deployment relate to the same shared platform contract.

Dependencies:
- `FND-019`

### FND-021: Cloud Run Public Reachability for Remote MCP
Description:
Make the hosted MCP service publicly reachable in the specific way required for trusted remote MCP consumers while preserving MCP-layer authentication inside the application surface.

Primary stories:
- As an OpenAI-hosted MCP consumer, I can reach the deployed Cloud Run service over the public Internet.
- As an operator, I can configure Cloud Run public access intentionally instead of depending on platform defaults or console-only setup.

Acceptance criteria:
- Deployment workflow explicitly supports the Cloud Run public-invocation model required for remote MCP access.
- Operator documentation explains the difference between Cloud Run public reachability and MCP bearer-token authentication.
- Hosted verification can distinguish Cloud Run IAM denial from MCP-layer authentication denial.
- Public reachability is validated with at least one reproducible operator workflow.

Dependencies:
- `FND-006`, `FND-013`, `FND-020`

### FND-022: Hosted Dependency Wiring for Secrets and Durable Sessions
Description:
Complete the provider-specific infrastructure wiring required for the Cloud Run runtime to access Secret Manager and the durable hosted session backend in real deployments.

Primary stories:
- As an operator, I can deploy the hosted runtime with working secret access and durable session connectivity.
- As an MCP consumer, I do not encounter readiness or continuation failures caused by missing Cloud Run network or IAM wiring.

Acceptance criteria:
- Runtime identity has the least-privilege IAM bindings required for runtime secret access.
- Hosted runtime can reach the configured durable session backend through documented network plumbing.
- Verification and readiness behavior cover missing secret-access and missing session-backend-connectivity failure cases.
- Infrastructure documentation explains the required Cloud Run-to-session-backend connectivity model.

Dependencies:
- `FND-015`, `FND-019`, `FND-020`

### FND-023: OpenAI Retrieval Compatibility for ChatGPT Apps and Deep Research
Description:
Align the foundational `search` and `fetch` tools with the current OpenAI compatibility guidance for ChatGPT apps, deep research, and company-knowledge-style retrieval integrations.

Primary stories:
- As an OpenAI retrieval integration, I can use `search` and `fetch` in the argument and result shape OpenAI currently documents.
- As a developer, I can target OpenAI-hosted retrieval flows without relying on best-effort schema interpretation.

Acceptance criteria:
- `search` and `fetch` schemas and outputs align to the current OpenAI compatibility contract or are wrapped through an explicit compatibility adapter.
- Documentation includes OpenAI-specific discovery and invocation examples for the supported retrieval flow.
- Compatibility coverage proves the intended OpenAI retrieval flow works end-to-end.
- Any intentional divergence from generic MCP or prior internal retrieval shapes is documented clearly.

Dependencies:
- `FND-014`, `FND-017`, `FND-021`

### FND-024: Initialize Handshake and Session Creation Correctness
Description:
Ensure hosted session creation only occurs after a valid MCP initialization handshake so clients never receive a continuation session for a failed initialize request.

Primary stories:
- As an MCP client, I only receive `MCP-Session-Id` after a successful initialize response.
- As a developer, I can trust that hosted session state reflects valid MCP lifecycle progress.

Acceptance criteria:
- Failed or malformed initialize requests do not create hosted sessions or return continuation headers.
- Successful initialize requests create hosted sessions exactly once.
- Hosted contract coverage includes both successful and failing initialize paths.
- Session lifecycle documentation matches the actual handshake behavior.

Dependencies:
- `FND-009`, `FND-010`, `FND-015`

### FND-025: Automated Hosted Deployment Orchestration
Description:
Turn the current image-only hosted deployment behavior into a checked-in automated pipeline that reconciles infrastructure, deploys the current application revision, and verifies the hosted MCP endpoint on push to the intended branch.

Primary stories:
- As an operator, I can push to the deployment branch and trust that the hosted platform is reconciled instead of only updating the container image.
- As a maintainer, I can review deployment automation in version control and evolve it alongside the application and infrastructure definitions.

Acceptance criteria:
- A checked-in deployment pipeline definition orchestrates tests, image build/push, Terraform apply, application deploy, and hosted verification.
- The deployment pipeline consumes Terraform outputs and uses the existing deploy script rather than bypassing repository deployment logic with an image-only Cloud Run update.
- Deployment fails if hosted verification fails after rollout.
- Automation clearly distinguishes secret resource wiring from operator-managed secret value population.
- Pipeline documentation explains the one-time bootstrap prerequisites required before push-triggered deployment becomes fully automated.

Dependencies:
- `FND-019`, `FND-021`, `FND-022`, `FND-024`

### FND-026: Local Runtime Ergonomics and Environment Entry Point
Description:
Provide a one-command local startup workflow with dedicated local environment defaults so developers can run and verify the MCP server without manually reconstructing runtime settings every session.

Primary stories:
- As a developer, I can start the MCP server locally with a single command.
- As a maintainer, I can keep local runtime settings separate from hosted deployment inputs while preserving a predictable local developer experience.

Acceptance criteria:
- The repository exposes a single-command local startup path for the minimal local runtime.
- A dedicated local environment file documents the variables used for local execution.
- Hosted-like local verification remains available through a simple companion command when Redis-backed local session continuity is needed.
- Local run documentation distinguishes deployment-time Cloud Run variables from local runtime variables.

Dependencies:
- `FND-015`, `FND-020`

### FND-027: Terraform-Managed Hosted Networking for Durable Sessions
Description:
Extend the hosted infrastructure foundation so the network resources required for durable hosted session connectivity are provisioned through Terraform instead of being treated as external/manual prerequisites.

Primary stories:
- As an operator, I can provision the hosted MCP platform without manually creating the VPC, subnets, or Cloud Run connectivity resources required for Redis-backed session durability.
- As a maintainer, I can review hosted networking changes in version control alongside the application and deployment automation changes that depend on them.

Acceptance criteria:
- Terraform provisions the provider-specific network resources required by the hosted durable-session model, including the relevant VPC and subnet resources.
- Terraform provisions the Cloud Run connectivity path required to reach the durable session backend, such as a Serverless VPC Access connector when applicable.
- Hosted deployment outputs expose the network/connectivity values needed by the deployment and verification workflow.
- Hosted verification and operator documentation no longer rely on pre-existing manually created networking prerequisites for the supported GCP path.

Dependencies:
- `FND-022`, `FND-025`

### FND-028: Automated Terraform Network Bootstrap in Hosted Deployment Pipeline
Description:
Ensure the checked-in hosted deployment pipeline reconciles the newly Terraform-managed network layer as part of the automated push-triggered rollout path.

Primary stories:
- As an operator, I can push to the deployment branch and trust that required hosted networking is reconciled before the application rollout.
- As a maintainer, I can rely on the same automated pipeline to provision application, secret, session, and network prerequisites together.

Acceptance criteria:
- The checked-in deployment pipeline runs Terraform against the hosted networking resources before application deployment.
- Pipeline documentation identifies the remaining one-time bootstrap inputs, if any, that must exist before the automated networking reconcile can succeed.
- Hosted deployment failure output makes it clear when rollout failed in the network/bootstrap layer versus the application deployment layer.

Dependencies:
- `FND-025`, `FND-027`

### YT-101: YouTube Client Integration Layer
Description:
Build typed wrapper for YouTube Data API v3 with auth, retry, quota, and error mapping.

Primary stories:
- As a tool developer, I can call YouTube endpoints via shared client abstractions.

Acceptance criteria:
- Wrapper supports videos/channels/playlists/search endpoints.
- Quota and upstream errors map to standard server errors.

Dependencies:
- `FND-005`, `FND-006`, `FND-007`, `FND-008`, `FND-009`, `FND-010`, `FND-011`, `FND-012`, `FND-013`, `FND-014`, `FND-015`, `FND-016`, `FND-017`, `FND-018`, `FND-019`, `FND-020`, `FND-021`, `FND-022`, `FND-023`, `FND-024`, `FND-025`, `FND-026`, `FND-027`, `FND-028`

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
9. `FND-009`
10. `FND-010`
11. `FND-011`
12. `FND-012`
13. `FND-013`
14. `FND-014`
15. `FND-015`
16. `FND-016`
17. `FND-017`
18. `FND-018`
19. `FND-019`
20. `FND-020`
21. `FND-021`
22. `FND-022`
23. `FND-023`
24. `FND-024`
25. `FND-025`
26. `FND-026`
27. `FND-027`
28. `FND-028`
29. `YT-101`
30. `YT-102` + `YT-103` (parallel)
31. `YT-104`
32. `YT-105`
33. `OPS-201`
34. `OPS-202`

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
