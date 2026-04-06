# SpecKit Seed
## Project: YouTube MCP Server on Cloud Run
## Source Docs
- `requirements/PRD.md`
- `requirements/tool-specs.md`

## 1. Product Goal
Deliver a production-deployed MCP server on Cloud Run that supports a reliable baseline server experience first, then adds a layered YouTube capability stack. For planning and numbering:
- `YT-1xx` is reserved for Layer 1 internal integrations and wrappers.
- `YT-2xx` is reserved for Layer 2 lower-level/raw-resource MCP tools.
- `YT-3xx` is reserved for Layer 3 higher-level public MCP tools.

The immediate planning focus is the initial Layer 3 public catalog of 10 higher-level video, transcript, channel, and playlist tools.

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

### YT-101: Layer 1 Shared Client Foundation
Description:
Build the shared Layer 1 integration scaffolding required before individual
YouTube Data API endpoints are wrapped.

Primary stories:
- As a maintainer, I can add endpoint wrappers on top of one consistent
  transport/auth/error foundation.
- As a future Layer 3 tool author, I can depend on typed integration methods
  instead of writing raw HTTP logic inside tool handlers.

Acceptance criteria:
- Shared Layer 1 abstractions exist for:
  - request execution
  - API key and OAuth credential injection
  - retry/backoff hooks
  - request/response logging hooks
  - upstream error normalization
- Endpoint wrappers can declare their HTTP method, path, auth mode, and quota
  metadata through one shared contract.
- Layer 1 remains internal and does not itself expose public MCP tools.

Dependencies:
- `FND-005`, `FND-006`, `FND-007`, `FND-008`, `FND-009`, `FND-010`, `FND-011`, `FND-012`, `FND-013`, `FND-014`, `FND-015`, `FND-016`, `FND-017`, `FND-018`, `FND-019`, `FND-020`, `FND-021`, `FND-022`, `FND-023`, `FND-024`, `FND-025`, `FND-026`, `FND-027`, `FND-028`

### YT-102: Layer 1 Endpoint Metadata, Quota, and Signature Standards
Description:
Define the Layer 1 wrapper contract so every endpoint method clearly records
its upstream identity, quota cost, auth expectations, and documentation notes.

Primary stories:
- As a maintainer, I can look at any Layer 1 method signature or docstring and
  immediately know what endpoint it calls and how expensive it is.
- As a future Layer 2 or Layer 3 author, I can understand quota implications
  before composing higher-level workflows.

Acceptance criteria:
- Every Layer 1 wrapper method records:
  - resource and method name
  - HTTP method and path
  - official quota-unit cost
  - auth mode (`api_key`, `oauth_required`, or mixed/conditional)
  - deprecation state when applicable
- Method signatures, docstrings, or adjacent implementation comments MUST
  include the official quota-unit cost for that endpoint.
- Shared documentation resolves or explicitly flags any official-doc
  inconsistencies encountered during implementation.

Dependencies:
- `YT-101`

## Layer 1 Endpoint Slice Rule

For every `YT-1xx` Layer 1 endpoint slice below:
- “Wrap `GET/POST/PUT/DELETE ...`” means implement the real YouTube Data API call for that endpoint.
- The slice is not complete if it only adds metadata, wrapper signatures, contract markdown, validation logic, or fake/injected test transports.
- Each slice MUST deliver a concrete execution path that can call the named upstream YouTube endpoint using the shared Layer 1 foundation from `YT-101` and `YT-102`.
- Later Layer 2 slices depend on Layer 1 for live upstream execution, not only interface shape.
- Each Layer 1 endpoint slice MUST include:
  - request construction for the real upstream path
  - credential attachment for supported auth modes
  - outbound HTTP execution to the real upstream endpoint
  - response parsing for successful upstream results
  - upstream error normalization through the shared Layer 1 error model

### YT-103: Layer 1 Endpoint `activities.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /activities`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `activities.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Supported auth/filter behavior is documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-104: Layer 1 Endpoint `captions.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /captions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `captions.list`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Required auth expectations are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-105: Layer 1 Endpoint `captions.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /captions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `captions.insert`.
- Official quota cost of `400` units is recorded in method metadata and method
  comments/docstrings.
- Media-upload requirements and OAuth requirements are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-106: Layer 1 Endpoint `captions.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /captions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `captions.update`.
- Official quota cost of `450` units is recorded in method metadata and method
  comments/docstrings.
- Media-upload/update behavior and OAuth requirements are documented in the
  wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-107: Layer 1 Endpoint `captions.download`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /captions/{id}`
YouTube Data API request for caption download.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `captions.download`.
- Official quota cost of `200` units is recorded in method metadata and method
  comments/docstrings.
- Edit-permission requirements, format conversion options, and language
  translation parameters are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-108: Layer 1 Endpoint `captions.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /captions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `captions.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth and content-owner delegation behavior are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-109: Layer 1 Endpoint `channelBanners.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real
`POST /channelBanners/insert` YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `channelBanners.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Media-upload and OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-110: Layer 1 Endpoint `channels.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /channels`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `channels.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Filter modes such as `id`, `mine`, `forHandle`, and username-style lookup are
  documented if supported by the current endpoint.

Dependencies:
- `YT-101`, `YT-102`

### YT-111: Layer 1 Endpoint `channels.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /channels`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `channels.update`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Writable resource-part limitations and OAuth requirements are documented in
  the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-112: Layer 1 Endpoint `channelSections.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /channelSections`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `channelSections.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Filter criteria and deprecation caveats are documented where applicable.

Dependencies:
- `YT-101`, `YT-102`

### YT-113: Layer 1 Endpoint `channelSections.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /channelSections`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `channelSections.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth and content-structure requirements are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-114: Layer 1 Endpoint `channelSections.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /channelSections`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `channelSections.update`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Writable field expectations are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-115: Layer 1 Endpoint `channelSections.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /channelSections`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `channelSections.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-116: Layer 1 Endpoint `comments.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /comments`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `comments.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Parent-comment and ID-based retrieval modes are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-117: Layer 1 Endpoint `comments.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /comments`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `comments.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Reply-creation behavior and OAuth requirements are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-118: Layer 1 Endpoint `comments.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /comments`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `comments.update`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Writable field expectations are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-119: Layer 1 Endpoint `comments.setModerationStatus`
Description:
Implement a typed Layer 1 wrapper that performs the real
`POST /comments/setModerationStatus` YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `comments.setModerationStatus`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Moderation-state transitions and OAuth requirements are documented in the
  wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-120: Layer 1 Endpoint `comments.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /comments`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `comments.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-121: Layer 1 Endpoint `commentThreads.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /commentThreads`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `commentThreads.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Supported filter modes such as `videoId`, `allThreadsRelatedToChannelId`, and
  ID-based retrieval are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-122: Layer 1 Endpoint `commentThreads.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /commentThreads`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `commentThreads.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Top-level-comment creation behavior and OAuth requirements are documented in
  the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-123: Layer 1 Endpoint `guideCategories.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /guideCategories`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `guideCategories.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- The wrapper contract explicitly flags this method as deprecated/unavailable
  in current platform behavior where official docs say so.

Dependencies:
- `YT-101`, `YT-102`

### YT-124: Layer 1 Endpoint `i18nLanguages.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /i18nLanguages`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `i18nLanguages.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Localization-lookup usage is documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-125: Layer 1 Endpoint `i18nRegions.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /i18nRegions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `i18nRegions.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Region-lookup usage is documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-126: Layer 1 Endpoint `members.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /members`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `members.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- OAuth and owner-only visibility requirements are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-127: Layer 1 Endpoint `membershipsLevels.list`
Description:
Implement a typed Layer 1 wrapper that performs the real
`GET /membershipsLevels` YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `membershipsLevels.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- OAuth and owner-only visibility requirements are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-128: Layer 1 Endpoint `playlistImages.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /playlistImages`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistImages.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- OAuth and playlist-image filter modes are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-129: Layer 1 Endpoint `playlistImages.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /playlistImages`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistImages.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Media-upload requirements and OAuth requirements are documented in the
  wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-130: Layer 1 Endpoint `playlistImages.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /playlistImages`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistImages.update`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Media-update requirements and OAuth requirements are documented in the
  wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-131: Layer 1 Endpoint `playlistImages.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /playlistImages`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistImages.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-132: Layer 1 Endpoint `playlistItems.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /playlistItems`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistItems.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Pagination and playlist/ID filter modes are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-133: Layer 1 Endpoint `playlistItems.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /playlistItems`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistItems.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth and writable-part requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-134: Layer 1 Endpoint `playlistItems.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /playlistItems`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistItems.update`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Writable field expectations are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-135: Layer 1 Endpoint `playlistItems.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /playlistItems`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlistItems.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-136: Layer 1 Endpoint `playlists.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /playlists`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlists.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Pagination and filter modes are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-137: Layer 1 Endpoint `playlists.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /playlists`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlists.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth and writable-part requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-138: Layer 1 Endpoint `playlists.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /playlists`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlists.update`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Writable field expectations are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-139: Layer 1 Endpoint `playlists.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /playlists`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `playlists.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-140: Layer 1 Endpoint `search.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /search`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `search.list`.
- Official quota cost of `100` units is recorded in method metadata and method
  comments/docstrings.
- Search type, pagination, date filtering, and language/region refinements are
  documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-141: Layer 1 Endpoint `subscriptions.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /subscriptions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `subscriptions.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Filter modes and OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-142: Layer 1 Endpoint `subscriptions.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /subscriptions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `subscriptions.insert`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth and writable-part requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-143: Layer 1 Endpoint `subscriptions.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /subscriptions`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `subscriptions.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-144: Layer 1 Endpoint `thumbnails.set`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /thumbnails/set`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `thumbnails.set`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Media-upload and OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-145: Layer 1 Endpoint `videoAbuseReportReasons.list`
Description:
Implement a typed Layer 1 wrapper that performs the real
`GET /videoAbuseReportReasons` YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videoAbuseReportReasons.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Localization usage is documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-146: Layer 1 Endpoint `videoCategories.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /videoCategories`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videoCategories.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Region-specific lookup behavior is documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-147: Layer 1 Endpoint `videos.list`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /videos`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videos.list`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- Filter modes such as `id`, `chart`, and other supported selectors are
  documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-148: Layer 1 Endpoint `videos.insert`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /videos`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videos.insert`.
- Official quota cost of `1600` units is recorded in method metadata and
  method comments/docstrings.
- Media-upload, resumable upload, audit/private-default behavior, and OAuth
  requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-149: Layer 1 Endpoint `videos.update`
Description:
Implement a typed Layer 1 wrapper that performs the real `PUT /videos`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videos.update`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Writable-part requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-150: Layer 1 Endpoint `videos.rate`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /videos/rate`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videos.rate`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Rating semantics and OAuth requirements are documented in the wrapper
  contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-151: Layer 1 Endpoint `videos.getRating`
Description:
Implement a typed Layer 1 wrapper that performs the real `GET /videos/getRating`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videos.getRating`.
- Official quota cost of `1` unit is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-152: Layer 1 Endpoint `videos.reportAbuse`
Description:
Implement a typed Layer 1 wrapper that performs the real
`POST /videos/reportAbuse` YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videos.reportAbuse`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Abuse-report payload expectations and OAuth requirements are documented in the
  wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-153: Layer 1 Endpoint `videos.delete`
Description:
Implement a typed Layer 1 wrapper that performs the real `DELETE /videos`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `videos.delete`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-154: Layer 1 Endpoint `watermarks.set`
Description:
Implement a typed Layer 1 wrapper that performs the real `POST /watermarks/set`
YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `watermarks.set`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- Media-upload and OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-155: Layer 1 Endpoint `watermarks.unset`
Description:
Implement a typed Layer 1 wrapper that performs the real
`POST /watermarks/unset` YouTube Data API request.

Acceptance criteria:
- Layer 1 exposes a typed wrapper for `watermarks.unset`.
- Official quota cost of `50` units is recorded in method metadata and method
  comments/docstrings.
- OAuth requirements are documented in the wrapper contract.

Dependencies:
- `YT-101`, `YT-102`

### YT-201: Layer 2 Shared Scaffolding and Contracts
Description:
Build the shared Layer 2 scaffolding required before individual YouTube Data
API endpoint MCP tools are exposed publicly.

Primary stories:
- As a maintainer, I can expose raw or near-raw YouTube endpoint tools without
  redefining the same naming, schema, quota, and auth rules for every method.
- As a power user, I can access low-level YouTube endpoint tools through a
  consistent MCP contract that stays close to the upstream API.

Acceptance criteria:
- Shared Layer 2 naming rules are documented and use resource-grouped public
  tool names without a redundant `youtube_` prefix.
- Shared Layer 2 parameter-mapping rules document how MCP-facing inputs align
  to upstream YouTube Data API request parameters.
- Shared Layer 2 response conventions document when the tool returns near-raw
  upstream fields versus lightly normalized wrapper fields.
- Shared Layer 2 error conventions document how upstream auth, quota, missing
  resource, invalid request, and deprecation errors surface through MCP.
- Layer 2 tool slices can depend on these shared contracts without redefining
  cross-cutting rules in every endpoint tool spec.

Dependencies:
- `YT-101`, `YT-102`

### YT-202: Layer 2 Tool Metadata, Naming, and Quota Standards
Description:
Define the public Layer 2 contract standards so every endpoint-backed MCP tool
clearly communicates its upstream identity, auth mode, and quota cost.

Primary stories:
- As a client developer, I can inspect any Layer 2 tool and immediately know
  which YouTube endpoint it maps to and how expensive it is to call.
- As a future Layer 3 author, I can compose lower-level tools with explicit
  visibility into quota consumption and auth requirements.

Acceptance criteria:
- Every Layer 2 tool definition records:
  - public MCP tool name
  - mapped YouTube resource and method name
  - official quota-unit cost
  - auth mode (`api_key`, `oauth_required`, or mixed/conditional)
  - deprecation state when applicable
- Layer 2 descriptions and example usage notes explicitly include the official
  quota-unit cost for that endpoint.
- Shared documentation defines how low-level tool names are derived from
  resource-method pairs such as `videos_list`, `playlists_insert`, and
  `comments_setModerationStatus`.
- Shared documentation defines when a Layer 2 tool may lightly reshape an
  upstream response and when it must stay near-raw.

Dependencies:
- `YT-201`

### YT-203: Layer 2 Tool `activities_list`
Description:
Expose `activities.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `activities_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Tool contract stays close to upstream filter and pagination behavior.

Dependencies:
- `YT-103`, `YT-201`, `YT-202`

### YT-204: Layer 2 Tool `captions_list`
Description:
Expose `captions.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `captions_list`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements and caption-track lookup behavior are documented clearly.

Dependencies:
- `YT-104`, `YT-201`, `YT-202`

### YT-205: Layer 2 Tool `captions_insert`
Description:
Expose `captions.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `captions_insert`.
- Official quota cost of `400` units is documented in tool metadata and tool
  description/examples.
- Media-upload and OAuth requirements are documented clearly.

Dependencies:
- `YT-105`, `YT-201`, `YT-202`

### YT-206: Layer 2 Tool `captions_update`
Description:
Expose `captions.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `captions_update`.
- Official quota cost of `450` units is documented in tool metadata and tool
  description/examples.
- Update semantics, media-upload behavior, and OAuth requirements are
  documented clearly.

Dependencies:
- `YT-106`, `YT-201`, `YT-202`

### YT-207: Layer 2 Tool `captions_download`
Description:
Expose `captions.download` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `captions_download`.
- Official quota cost of `200` units is documented in tool metadata and tool
  description/examples.
- Permission requirements and format/language conversion options are documented
  clearly.

Dependencies:
- `YT-107`, `YT-201`, `YT-202`

### YT-208: Layer 2 Tool `captions_delete`
Description:
Expose `captions.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `captions_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth and content-owner delegation behavior are documented clearly.

Dependencies:
- `YT-108`, `YT-201`, `YT-202`

### YT-209: Layer 2 Tool `channelBanners_insert`
Description:
Expose `channelBanners.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `channelBanners_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Media-upload and OAuth requirements are documented clearly.

Dependencies:
- `YT-109`, `YT-201`, `YT-202`

### YT-210: Layer 2 Tool `channels_list`
Description:
Expose `channels.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `channels_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Supported filter modes such as `id`, `mine`, `forHandle`, and username-style
  lookup are documented clearly.

Dependencies:
- `YT-110`, `YT-201`, `YT-202`

### YT-211: Layer 2 Tool `channels_update`
Description:
Expose `channels.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `channels_update`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Writable resource-part limitations and OAuth requirements are documented
  clearly.

Dependencies:
- `YT-111`, `YT-201`, `YT-202`

### YT-212: Layer 2 Tool `channelSections_list`
Description:
Expose `channelSections.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `channelSections_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Filter criteria and deprecation caveats are documented clearly.

Dependencies:
- `YT-112`, `YT-201`, `YT-202`

### YT-213: Layer 2 Tool `channelSections_insert`
Description:
Expose `channelSections.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `channelSections_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth and content-structure requirements are documented clearly.

Dependencies:
- `YT-113`, `YT-201`, `YT-202`

### YT-214: Layer 2 Tool `channelSections_update`
Description:
Expose `channelSections.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `channelSections_update`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Writable field expectations are documented clearly.

Dependencies:
- `YT-114`, `YT-201`, `YT-202`

### YT-215: Layer 2 Tool `channelSections_delete`
Description:
Expose `channelSections.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `channelSections_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-115`, `YT-201`, `YT-202`

### YT-216: Layer 2 Tool `comments_list`
Description:
Expose `comments.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `comments_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Parent-comment and ID-based retrieval modes are documented clearly.

Dependencies:
- `YT-116`, `YT-201`, `YT-202`

### YT-217: Layer 2 Tool `comments_insert`
Description:
Expose `comments.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `comments_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Reply-creation behavior and OAuth requirements are documented clearly.

Dependencies:
- `YT-117`, `YT-201`, `YT-202`

### YT-218: Layer 2 Tool `comments_update`
Description:
Expose `comments.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `comments_update`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Writable field expectations are documented clearly.

Dependencies:
- `YT-118`, `YT-201`, `YT-202`

### YT-219: Layer 2 Tool `comments_setModerationStatus`
Description:
Expose `comments.setModerationStatus` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `comments_setModerationStatus`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Moderation-state transitions and OAuth requirements are documented clearly.

Dependencies:
- `YT-119`, `YT-201`, `YT-202`

### YT-220: Layer 2 Tool `comments_delete`
Description:
Expose `comments.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `comments_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-120`, `YT-201`, `YT-202`

### YT-221: Layer 2 Tool `commentThreads_list`
Description:
Expose `commentThreads.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `commentThreads_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Supported filter modes such as `videoId`, `allThreadsRelatedToChannelId`, and
  ID-based retrieval are documented clearly.

Dependencies:
- `YT-121`, `YT-201`, `YT-202`

### YT-222: Layer 2 Tool `commentThreads_insert`
Description:
Expose `commentThreads.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `commentThreads_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Top-level-comment creation behavior and OAuth requirements are documented
  clearly.

Dependencies:
- `YT-122`, `YT-201`, `YT-202`

### YT-223: Layer 2 Tool `guideCategories_list`
Description:
Expose `guideCategories.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `guideCategories_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Deprecated or unavailable platform behavior is documented clearly.

Dependencies:
- `YT-123`, `YT-201`, `YT-202`

### YT-224: Layer 2 Tool `i18nLanguages_list`
Description:
Expose `i18nLanguages.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `i18nLanguages_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Localization lookup usage is documented clearly.

Dependencies:
- `YT-124`, `YT-201`, `YT-202`

### YT-225: Layer 2 Tool `i18nRegions_list`
Description:
Expose `i18nRegions.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `i18nRegions_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Region lookup usage is documented clearly.

Dependencies:
- `YT-125`, `YT-201`, `YT-202`

### YT-226: Layer 2 Tool `members_list`
Description:
Expose `members.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `members_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- OAuth and channel-membership access constraints are documented clearly.

Dependencies:
- `YT-126`, `YT-201`, `YT-202`

### YT-227: Layer 2 Tool `membershipsLevels_list`
Description:
Expose `membershipsLevels.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `membershipsLevels_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- OAuth and channel-membership access constraints are documented clearly.

Dependencies:
- `YT-127`, `YT-201`, `YT-202`

### YT-228: Layer 2 Tool `playlistImages_list`
Description:
Expose `playlistImages.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistImages_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Image lookup behavior and resource-part expectations are documented clearly.

Dependencies:
- `YT-128`, `YT-201`, `YT-202`

### YT-229: Layer 2 Tool `playlistImages_insert`
Description:
Expose `playlistImages.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistImages_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Media-upload and OAuth requirements are documented clearly.

Dependencies:
- `YT-129`, `YT-201`, `YT-202`

### YT-230: Layer 2 Tool `playlistImages_update`
Description:
Expose `playlistImages.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistImages_update`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Update semantics, media-upload behavior, and OAuth requirements are
  documented clearly.

Dependencies:
- `YT-130`, `YT-201`, `YT-202`

### YT-231: Layer 2 Tool `playlistImages_delete`
Description:
Expose `playlistImages.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistImages_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-131`, `YT-201`, `YT-202`

### YT-232: Layer 2 Tool `playlistItems_list`
Description:
Expose `playlistItems.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistItems_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Near-raw playlist item listing and pagination behavior are documented clearly.

Dependencies:
- `YT-132`, `YT-201`, `YT-202`

### YT-233: Layer 2 Tool `playlistItems_insert`
Description:
Expose `playlistItems.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistItems_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Insert semantics and OAuth requirements are documented clearly.

Dependencies:
- `YT-133`, `YT-201`, `YT-202`

### YT-234: Layer 2 Tool `playlistItems_update`
Description:
Expose `playlistItems.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistItems_update`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Update semantics and OAuth requirements are documented clearly.

Dependencies:
- `YT-134`, `YT-201`, `YT-202`

### YT-235: Layer 2 Tool `playlistItems_delete`
Description:
Expose `playlistItems.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlistItems_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-135`, `YT-201`, `YT-202`

### YT-236: Layer 2 Tool `playlists_list`
Description:
Expose `playlists.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlists_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Filter and pagination behavior are documented clearly.

Dependencies:
- `YT-136`, `YT-201`, `YT-202`

### YT-237: Layer 2 Tool `playlists_insert`
Description:
Expose `playlists.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlists_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Create semantics and OAuth requirements are documented clearly.

Dependencies:
- `YT-137`, `YT-201`, `YT-202`

### YT-238: Layer 2 Tool `playlists_update`
Description:
Expose `playlists.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlists_update`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Update semantics and OAuth requirements are documented clearly.

Dependencies:
- `YT-138`, `YT-201`, `YT-202`

### YT-239: Layer 2 Tool `playlists_delete`
Description:
Expose `playlists.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `playlists_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-139`, `YT-201`, `YT-202`

### YT-240: Layer 2 Tool `search_list`
Description:
Expose `search.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `search_list`.
- Official quota cost of `100` units is documented in tool metadata and tool
  description/examples.
- Search cost, supported filter modes, and pagination behavior are documented
  clearly.

Dependencies:
- `YT-140`, `YT-201`, `YT-202`

### YT-241: Layer 2 Tool `subscriptions_list`
Description:
Expose `subscriptions.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `subscriptions_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Supported filter modes and OAuth requirements are documented clearly.

Dependencies:
- `YT-141`, `YT-201`, `YT-202`

### YT-242: Layer 2 Tool `subscriptions_insert`
Description:
Expose `subscriptions.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `subscriptions_insert`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Create semantics and OAuth requirements are documented clearly.

Dependencies:
- `YT-142`, `YT-201`, `YT-202`

### YT-243: Layer 2 Tool `subscriptions_delete`
Description:
Expose `subscriptions.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `subscriptions_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-143`, `YT-201`, `YT-202`

### YT-244: Layer 2 Tool `thumbnails_set`
Description:
Expose `thumbnails.set` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `thumbnails_set`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Media-upload and OAuth requirements are documented clearly.

Dependencies:
- `YT-144`, `YT-201`, `YT-202`

### YT-245: Layer 2 Tool `videoAbuseReportReasons_list`
Description:
Expose `videoAbuseReportReasons.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videoAbuseReportReasons_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Lookup behavior and localization considerations are documented clearly.

Dependencies:
- `YT-145`, `YT-201`, `YT-202`

### YT-246: Layer 2 Tool `videoCategories_list`
Description:
Expose `videoCategories.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videoCategories_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Lookup behavior and localization considerations are documented clearly.

Dependencies:
- `YT-146`, `YT-201`, `YT-202`

### YT-247: Layer 2 Tool `videos_list`
Description:
Expose `videos.list` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videos_list`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Part selection, filter modes, and pagination behavior are documented clearly.

Dependencies:
- `YT-147`, `YT-201`, `YT-202`

### YT-248: Layer 2 Tool `videos_insert`
Description:
Expose `videos.insert` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videos_insert`.
- Official quota cost of `1600` units is documented in tool metadata and tool
  description/examples.
- Media-upload and OAuth requirements are documented clearly.

Dependencies:
- `YT-148`, `YT-201`, `YT-202`

### YT-249: Layer 2 Tool `videos_update`
Description:
Expose `videos.update` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videos_update`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Update semantics, writable parts, and OAuth requirements are documented
  clearly.

Dependencies:
- `YT-149`, `YT-201`, `YT-202`

### YT-250: Layer 2 Tool `videos_rate`
Description:
Expose `videos.rate` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videos_rate`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Rating-state semantics and OAuth requirements are documented clearly.

Dependencies:
- `YT-150`, `YT-201`, `YT-202`

### YT-251: Layer 2 Tool `videos_getRating`
Description:
Expose `videos.getRating` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videos_getRating`.
- Official quota cost of `1` unit is documented in tool metadata and tool
  description/examples.
- Rating lookup behavior and OAuth requirements are documented clearly.

Dependencies:
- `YT-151`, `YT-201`, `YT-202`

### YT-252: Layer 2 Tool `videos_reportAbuse`
Description:
Expose `videos.reportAbuse` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videos_reportAbuse`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Abuse-report payload expectations and OAuth requirements are documented
  clearly.

Dependencies:
- `YT-152`, `YT-201`, `YT-202`

### YT-253: Layer 2 Tool `videos_delete`
Description:
Expose `videos.delete` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `videos_delete`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-153`, `YT-201`, `YT-202`

### YT-254: Layer 2 Tool `watermarks_set`
Description:
Expose `watermarks.set` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `watermarks_set`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- Media-upload and OAuth requirements are documented clearly.

Dependencies:
- `YT-154`, `YT-201`, `YT-202`

### YT-255: Layer 2 Tool `watermarks_unset`
Description:
Expose `watermarks.unset` as a low-level MCP tool.

Acceptance criteria:
- Layer 2 exposes `watermarks_unset`.
- Official quota cost of `50` units is documented in tool metadata and tool
  description/examples.
- OAuth requirements are documented clearly.

Dependencies:
- `YT-155`, `YT-201`, `YT-202`

### YT-301: Layer 3 Shared Scaffolding and Contracts
Description:
Build the shared Layer 3 scaffolding needed by the public tool catalog, including naming, shared schemas, normalized response conventions, heuristic-field documentation, and reusable interfaces the individual tools will depend on.

Primary stories:
- As a maintainer, I can add each Layer 3 tool without redefining the same contract and normalization rules repeatedly.
- As a client developer, I can rely on consistent naming and result-shaping across the Layer 3 public tool catalog.

Acceptance criteria:
- Shared Layer 3 naming rules are documented and use grouped tool prefixes such as `videos_*`, `channels_*`, `playlists_*`, and `transcripts_*`.
- Shared parameter conventions are documented for repeated fields such as `videoId`, `channelId`, `playlistId`, `query`, `language`, `maxResults`, `order`, and ISO 8601 date filters.
- Shared Layer 3 response conventions distinguish raw upstream values from normalized fields and heuristic/inferred fields.
- Shared rules for ranking/filtering semantics such as `creatorOnly`, subscriber-band filters, latest-upload filters, and `sortBy` are documented wherever multiple tools reuse them.
- Layer 3 tool slices can depend on these shared contracts without redefining cross-cutting rules in each tool spec.

Dependencies:
- `FND-005`, `FND-006`, `FND-007`, `FND-008`, `FND-009`, `FND-010`, `FND-011`, `FND-012`, `FND-013`, `FND-014`, `FND-015`, `FND-016`, `FND-017`, `FND-018`, `FND-019`, `FND-020`, `FND-021`, `FND-022`, `FND-023`, `FND-024`, `FND-025`, `FND-026`, `FND-027`, `FND-028`

### YT-302: Layer 3 Tool `videos_getVideo`
Description:
Define and implement the higher-level video detail tool.

Primary stories:
- As an MCP client, I can request detailed information about one YouTube video.

Acceptance criteria:
- `videos_getVideo` supports:
  - required `videoId`
  - optional `parts`
- Response contract documents the normalized video fields returned by default.
- Optional `parts` behavior is documented, including how requested parts map to returned fields.
- Error behavior is documented for invalid IDs, unavailable videos, and upstream quota/access failures.

Dependencies:
- `YT-301`

### YT-303: Layer 3 Tool `videos_searchVideos`
Description:
Define and implement the higher-level video search tool with channel-aware enrichment and ranking/filtering behavior.

Primary stories:
- As an MCP client, I can search for videos and optionally refine results by channel- and creator-oriented filters.

Acceptance criteria:
- `videos_searchVideos` supports:
  - required `query`
  - optional `maxResults`, `order`, `publishedAfter`, `publishedBefore`, `channelId`
  - optional `uniqueChannels`
  - optional `channelMinSubscribers`, `channelMaxSubscribers`
  - optional `channelLastUploadAfter`, `channelLastUploadBefore`
  - optional `creatorOnly`
  - optional `sortBy`
- `sortBy` semantics are documented for:
  - `relevance`
  - `subscribers_asc`
  - `subscribers_desc`
  - `indie_priority`
  - `recent_activity`
- Search enrichment and post-search filtering behavior are documented when channel metadata is required to compute final results.
- `uniqueChannels=true` behavior is documented explicitly.

Dependencies:
- `YT-301`

### YT-304: Layer 3 Tool `transcripts_getTranscript`
Description:
Define and implement the higher-level transcript retrieval tool.

Primary stories:
- As an MCP client, I can retrieve the transcript of a YouTube video in a predictable language-selection flow.

Acceptance criteria:
- `transcripts_getTranscript` supports:
  - required `videoId`
  - optional `language`
- Transcript language fallback behavior is documented:
  - explicit parameter
  - then `YOUTUBE_TRANSCRIPT_LANG`
  - then `en`
- Official caption-access requirements and failure modes are documented.
- Output contract is detailed enough for agents to consume transcript text and/or timestamped segments safely.

Dependencies:
- `YT-301`

### YT-305: Layer 3 Tool `channels_getChannel`
Description:
Define and implement the higher-level single-channel detail tool.

Primary stories:
- As an MCP client, I can retrieve normalized and enriched information about a YouTube channel.

Acceptance criteria:
- `channels_getChannel` supports:
  - required `channelId`
  - enriched output including `latestVideoPublishedAt`
  - `normalizedMetadata`
  - normalized metadata fields for `country`, `defaultLanguage`, `joinedAt`, `customUrl`, `emailsFound`, and `contactLinks`
  - creator-versus-brand heuristic fields
- The contract distinguishes which returned channel fields are raw upstream metadata versus normalized or heuristic fields.

Dependencies:
- `YT-301`

### YT-306: Layer 3 Tool `channels_getChannels`
Description:
Define and implement the higher-level batch channel detail tool.

Primary stories:
- As an MCP client, I can retrieve information about multiple channels in one request.

Acceptance criteria:
- `channels_getChannels` supports:
  - required `channelIds`
  - optional `parts`
  - optional `includeLatestUpload`
- `includeLatestUpload` default behavior is documented as `true`.
- Batch output shape is documented and consistent with the single-channel normalization rules where applicable.

Dependencies:
- `YT-301`

### YT-307: Layer 3 Tool `channels_searchChannels`
Description:
Define and implement the higher-level channel search tool.

Primary stories:
- As an MCP client, I can search for channels by handle, name, or general query and then filter/rank them in useful ways.

Acceptance criteria:
- `channels_searchChannels` supports:
  - required `query`
  - optional `maxResults`, `order`, `channelType`
  - optional `minSubscribers`, `maxSubscribers`
  - optional `lastUploadAfter`, `lastUploadBefore`
  - optional `creatorOnly`
  - optional `sortBy`
- `sortBy` semantics are documented for:
  - `relevance`
  - `subscribers_asc`
  - `subscribers_desc`
  - `indie_priority`
  - `recent_activity`
- Search, enrichment, filtering, and ranking behavior are documented when they require composite in-server logic.

Dependencies:
- `YT-301`

### YT-308: Layer 3 Tool `channels_findCreators`
Description:
Define and implement the higher-level creator-discovery tool.

Primary stories:
- As an MCP client, I can discover creator channels from matched videos and then refine those results by channel size and activity.

Acceptance criteria:
- `channels_findCreators` supports:
  - required `query`
  - optional `maxResults`, `order`
  - optional `videoPublishedAfter`, `videoPublishedBefore`
  - optional `channelMinSubscribers`, `channelMaxSubscribers`
  - optional `channelLastUploadAfter`, `channelLastUploadBefore`
  - optional `creatorOnly`
  - optional `sortBy`
  - optional `sampleVideosPerChannel`
- The contract documents that this is a composite higher-level tool rather than a single-endpoint passthrough.
- Creator-discovery, candidate-channel derivation, sampling behavior, and ranking/filtering semantics are documented explicitly.

Dependencies:
- `YT-301`
- `YT-305`
- `YT-307`

### YT-309: Layer 3 Tool `channels_listVideos`
Description:
Define and implement the higher-level channel video listing tool.

Primary stories:
- As an MCP client, I can retrieve videos from a specific channel through a stable MCP-facing contract.

Acceptance criteria:
- `channels_listVideos` supports:
  - required `channelId`
  - optional `maxResults`
- The contract documents whether the implementation uses ranked search behavior, uploads-playlist behavior, or a documented combination of both.

Dependencies:
- `YT-301`

### YT-310: Layer 3 Tool `playlists_getPlaylist`
Description:
Define and implement the higher-level playlist detail tool.

Primary stories:
- As an MCP client, I can retrieve information about a YouTube playlist.

Acceptance criteria:
- `playlists_getPlaylist` supports:
  - required `playlistId`
- Playlist detail output is normalized for agent consumption.

Dependencies:
- `YT-301`

### YT-311: Layer 3 Tool `playlists_getPlaylistItems`
Description:
Define and implement the higher-level playlist items tool.

Primary stories:
- As an MCP client, I can retrieve the videos contained in a playlist.

Acceptance criteria:
- `playlists_getPlaylistItems` supports:
  - required `playlistId`
  - optional `maxResults`
- Playlist item output is normalized for agent consumption and does not leak raw upstream response complexity unnecessarily.

Dependencies:
- `YT-301`

### YT-312: Layer 3 Tool `videos_getStatistics`
Description:
Define and implement the higher-level video statistics tool.

Primary stories:
- As an MCP client, I can retrieve view, like, comment, and other available statistics for a video.

Acceptance criteria:
- `videos_getStatistics` supports:
  - required `videoId`
- The contract documents which statistics are expected when available from YouTube and how missing/hidden counts are represented.
- Output is normalized for agent consumption and consistent with the rest of the Layer 3 video catalog.

Dependencies:
- `YT-301`

### YT-313: Layer 3 Tool `transcripts_listLanguages`
Description:
Define and implement the transcript-language discovery tool.

Primary stories:
- As an MCP client, I can discover which transcript/caption languages are available for a video before requesting one.

Acceptance criteria:
- `transcripts_listLanguages` supports:
  - required `videoId`
- Output documents available languages, any track identifiers or track metadata exposed to callers, and any auth-sensitive limitations.

Dependencies:
- `YT-301`

### YT-314: Layer 3 Tool `transcripts_getTimestampedCaptions`
Description:
Define and implement the timestamped caption-segment retrieval tool.

Primary stories:
- As an MCP client, I can retrieve caption segments with explicit start/end timing for a video.

Acceptance criteria:
- `transcripts_getTimestampedCaptions` supports:
  - required `videoId`
  - optional `language`
- Output contract documents timestamp fields and segment granularity clearly.
- Auth-sensitive caption access rules and failure modes are documented.

Dependencies:
- `YT-301`

### YT-315: Layer 3 Tool `transcripts_searchTranscript`
Description:
Define and implement the higher-level transcript text search tool.

Primary stories:
- As an MCP client, I can search within a transcript and retrieve matching snippets with timestamps.

Acceptance criteria:
- `transcripts_searchTranscript` supports:
  - required `videoId`
  - required `query`
  - optional `language`
  - optional `maxMatches`
- The contract documents that this is a composite higher-level tool built on transcript retrieval plus in-server text search.
- Match ranking, snippet extraction, and timestamp behavior are documented explicitly.

Dependencies:
- `YT-301`
- `YT-304`

### YT-316: Layer 3 Tool `channels_listPlaylists`
Description:
Define and implement the higher-level channel playlist listing tool.

Primary stories:
- As an MCP client, I can retrieve the playlists associated with a channel.

Acceptance criteria:
- `channels_listPlaylists` supports:
  - required `channelId`
  - optional `maxResults`
- Playlist listing output is normalized for agent consumption and consistent with the playlist tool family.

Dependencies:
- `YT-301`

### YT-317: Layer 3 Tool `channels_getStatistics`
Description:
Define and implement the higher-level channel statistics tool.

Primary stories:
- As an MCP client, I can retrieve statistics for a channel such as subscriber, video, and view counts when available.

Acceptance criteria:
- `channels_getStatistics` supports:
  - required `channelId`
- The contract documents which statistics are expected when available from YouTube and how missing/hidden counts are represented.
- Output is normalized for agent consumption and consistent with the rest of the Layer 3 channel catalog.

Dependencies:
- `YT-301`

### YT-318: Layer 3 Tool `channels_searchContent`
Description:
Define and implement the higher-level channel-content search tool.

Primary stories:
- As an MCP client, I can search within the content of a specific channel.

Acceptance criteria:
- `channels_searchContent` supports:
  - required `channelId`
  - required `query`
  - optional `maxResults`, `order`
  - optional language or other relevance refinements if exposed in the final contract
- The contract documents when behavior is a direct upstream search versus composite in-server enrichment/filtering.

Dependencies:
- `YT-301`
- `YT-309`

### YT-319: Layer 3 Tool `playlists_searchItems`
Description:
Define and implement the higher-level playlist item search tool.

Primary stories:
- As an MCP client, I can search within a playlist for matching videos or items.

Acceptance criteria:
- `playlists_searchItems` supports:
  - required `playlistId`
  - required `query`
  - optional `maxResults`
- The contract documents that this is a composite higher-level tool rather than a single-endpoint passthrough.
- Search matching and result-shaping behavior are documented clearly.

Dependencies:
- `YT-301`
- `YT-311`

### YT-320: Layer 3 Tool `playlists_getVideoTranscripts`
Description:
Define and implement the higher-level playlist transcript aggregation tool.

Primary stories:
- As an MCP client, I can retrieve transcript data for videos contained in a playlist.

Acceptance criteria:
- `playlists_getVideoTranscripts` supports:
  - required `playlistId`
  - optional `language`
  - optional `maxResults` or equivalent bounded playlist-processing controls in the final contract
- The contract documents that this is a composite higher-level tool built from playlist enumeration plus transcript retrieval.
- Auth-sensitive caption-access limitations and bounded fan-out behavior are documented explicitly.

Dependencies:
- `YT-301`
- `YT-304`
- `YT-311`

### OPS-401: CI/CD and Quality Gates
Description:
Add CI checks and deploy automation guardrails.

Primary stories:
- As a maintainer, PRs are blocked on lint/typecheck/tests.

Acceptance criteria:
- CI pipeline executes lint, typecheck, tests.
- Build/deploy instructions reproducible from docs.

Dependencies:
- `FND-008`

### OPS-402: Production Hardening
Description:
Add rate limiting, caching policy, and operational alerts.

Primary stories:
- As an operator, I get alerted on sustained errors/latency spikes.

Acceptance criteria:
- Basic alerting configured.
- Rate limiting strategy implemented.
- Caching strategy documented and applied where appropriate.

Dependencies:
- `YT-203`, `YT-204`, `YT-205`, `YT-206`, `YT-207`, `YT-208`, `YT-209`, `YT-210`, `YT-211`, `YT-212`, `YT-213`, `YT-214`, `YT-215`, `YT-216`, `YT-217`, `YT-218`, `YT-219`, `YT-220`, `YT-221`, `YT-222`, `YT-223`, `YT-224`, `YT-225`, `YT-226`, `YT-227`, `YT-228`, `YT-229`, `YT-230`, `YT-231`, `YT-232`, `YT-233`, `YT-234`, `YT-235`, `YT-236`, `YT-237`, `YT-238`, `YT-239`, `YT-240`, `YT-241`, `YT-242`, `YT-243`, `YT-244`, `YT-245`, `YT-246`, `YT-247`, `YT-248`, `YT-249`, `YT-250`, `YT-251`, `YT-252`, `YT-253`, `YT-254`, `YT-255`, `YT-302`, `YT-303`, `YT-304`, `YT-305`, `YT-306`, `YT-307`, `YT-308`, `YT-309`, `YT-310`, `YT-311`, `YT-312`, `YT-313`, `YT-314`, `YT-315`, `YT-316`, `YT-317`, `YT-318`, `YT-319`, `YT-320`

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
30. `YT-102`
31. `YT-103` through `YT-110` (read and metadata foundations, grouped by resource where practical)
32. `YT-111` through `YT-123` (channel, comments, comment-thread, and legacy-category endpoints)
33. `YT-124` through `YT-139` (localization, member, playlist-image, playlist-item, and playlist endpoints)
34. `YT-140` through `YT-155` (search, subscriptions, thumbnails, video, and watermark endpoints)
35. `YT-201`
36. `YT-202`
37. `YT-203` through `YT-210` (initial read/list Layer 2 endpoint tools)
38. `YT-211` through `YT-223` (update/comment/category Layer 2 endpoint tools)
39. `YT-224` through `YT-239` (localization/member/playlist Layer 2 endpoint tools)
40. `YT-240` through `YT-255` (search/subscription/video/watermark Layer 2 endpoint tools)
41. `YT-301`
42. `YT-302` + `YT-304` + `YT-305` + `YT-309` + `YT-310` (parallel where practical)
43. `YT-303` + `YT-306` + `YT-307` + `YT-311` (parallel where practical)
44. `YT-308`
45. `YT-312` + `YT-313` + `YT-316` + `YT-317` (parallel where practical)
46. `YT-314` + `YT-318` + `YT-319` (parallel where practical)
47. `YT-315` + `YT-320`
48. `OPS-401`
49. `OPS-402`

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
- Derived creator heuristics and normalized metadata fields can drift from their documented semantics unless the public contract distinguishes raw upstream data from inferred/enriched data.

## 9. Immediate Next SpecKit Inputs
Create first SpecKit specs in this order:
1. `FND-001 MCP Transport + Handshake`
2. `FND-002 Tool Registry + Dispatcher`
3. `FND-003 Baseline Server Tools`
4. `FND-006 Cloud Run Foundation Deployment`
