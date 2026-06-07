# Research: YT-208 Layer 2 Tool `captions_delete`

## Decision: Implement One Concrete Layer 2 Tool Backed by Existing Layer 1 `captions.delete`

YT-208 should expose only the public `captions_delete` MCP tool and should rely on the existing YT-108 Layer 1 `captions.delete` wrapper for endpoint identity, OAuth behavior, quota cost, delegation context, request validation, upstream execution, and deletion result shape.

**Rationale**: The seed defines YT-208 as a single endpoint-tool slice. YT-201 and YT-202 already define shared Layer 2 naming, metadata, response-boundary, mutation, quota, auth, and safety standards; YT-108 already provides the internal `captions.delete` capability. Reusing those artifacts keeps implementation small and avoids a duplicate upstream request path.

**Alternatives considered**:

- Reimplement `captions.delete` request execution directly in the Layer 2 handler: rejected because it would duplicate Layer 1 execution and error normalization.
- Add bulk caption deletion or recovery behavior in this slice: rejected because YT-208 is scoped to one low-level endpoint and undo/recovery workflows belong outside this endpoint tool.
- Defer public execution and add only another representative descriptor: rejected because YT-208 acceptance requires Layer 2 to expose `captions_delete`.

## Decision: Use Official `captions.delete` Contract as the Public Tool Boundary

The public `captions_delete` input contract should preserve the official endpoint concepts: required caption track `id`, optional `onBehalfOfContentOwner`, official quota cost `50`, OAuth authorization, no request body, and successful HTTP `204 No Content` response. Source: https://developers.google.com/youtube/v3/docs/captions/delete

**Rationale**: Layer 2 is the near-raw endpoint layer. The current official YouTube documentation, last updated 2026-06-01 UTC, describes `captions.delete` as deleting one specified caption track, requiring OAuth authorization, accepting only query parameters, and returning no response body on success. The MCP-facing tool can add a light deletion acknowledgment for clarity, but it must not invent a returned caption resource.

**Alternatives considered**:

- Return a deleted caption resource object: rejected because the upstream success response is no content.
- Accept a request body containing caption metadata: rejected because the official endpoint says not to provide a request body.
- Infer the caption track from a video id or language: rejected because the upstream endpoint requires the caption track id.
- Store deletion audit records in this slice: rejected because the slice introduces no persistence and the public result only needs endpoint-backed acknowledgment context.

## Decision: Declare OAuth-Required Auth With Content-Owner Delegation Notes

`captions_delete` should declare auth mode `oauth_required`. Public metadata and usage notes must make clear that eligible OAuth authorization is required and that `onBehalfOfContentOwner` is optional delegated content-owner context for eligible YouTube content partners.

**Rationale**: Caption deletion is destructive and cannot be represented as public API-key behavior. The official docs list OAuth scopes and describe `onBehalfOfContentOwner` as content-partner delegation that requires linked CMS authorization. Callers need this before invocation so they do not treat caption deletion as public video metadata or unauthenticated cleanup.

**Alternatives considered**:

- Declare the tool `api_key`: rejected because that would misrepresent caption deletion access.
- Declare mixed/conditional auth: rejected because the supported request path requires OAuth.
- Hide delegation details until errors occur: rejected because delegation materially affects valid requests in partner-managed environments.

## Decision: Preserve a Near-Raw Deletion Acknowledgment Result

Successful `captions_delete` results should preserve endpoint-backed deletion semantics and include light MCP clarity fields such as endpoint identity, quota cost, caption track id, no-body success indication, deletion status, and safe delegation context when supplied.

**Rationale**: The upstream result is an HTTP `204 No Content` status. Layer 2 callers still need a machine-readable acknowledgment that the tool call completed, but the result must not fabricate deleted caption data. A thin wrapper aligns with YT-201/YT-202 response-boundary rules for mutation acknowledgments.

**Alternatives considered**:

- Return no MCP result content at all: rejected because clients need a consistent tool result that records the operation outcome.
- Return the caption resource that was deleted: rejected because upstream does not return one and it would mislead callers.
- Return a local recovery token: rejected because no recovery or persistence lifecycle is in scope.

## Decision: Validate Identifier, No-Body Shape, Delegation, and OAuth Before Invocation

The public tool should require a non-empty caption track `id`, eligible OAuth authorization, valid delegated content-owner context when supplied, and no request body or unsupported extra mutation options before treating the request as supported endpoint usage. Missing identifier, malformed identifier, unsupported fields, unsupported body input, and missing authorization requests must be rejected with clear caller-facing guidance.

**Rationale**: The endpoint is destructive and quota-sensitive. Early validation gives MCP callers stable remediation guidance, protects against confusing failed deletion attempts, and keeps unsupported request shapes from becoming ambiguous upstream errors.

**Alternatives considered**:

- Let upstream YouTube reject invalid identifiers or bodies: rejected where local validation can give deterministic guidance from the public contract.
- Treat missing authorization as not found: rejected because callers need to distinguish inaccessible caption tracks from missing caption resources.
- Allow unsupported fields and pass them through: rejected because the public Layer 2 schema should be deterministic.

## Decision: Map Official Delete Errors to Shared Safe Error Categories

The tool should map upstream `forbidden` to `authorization_failed` and upstream `captionNotFound` to `resource_not_found`. Quota exhaustion, unavailable service, invalid request, and unexpected upstream failures should use the shared Layer 2 error categories.

**Rationale**: The official docs identify insufficient permission and missing caption-track failures for `captions.delete`. Shared YT-201/YT-202 error conventions keep MCP-facing errors stable and safe while preserving enough context for callers to correct the request or distinguish repeated deletion from access failure.

**Alternatives considered**:

- Surface raw upstream error payloads directly: rejected because errors must be MCP-safe and must not expose sensitive details.
- Collapse all delete errors into `upstream_failure`: rejected because auth and not-found outcomes are distinct user-remediable categories.
- Treat repeated deletion as success locally: rejected because the endpoint-backed Layer 2 tool should preserve the upstream missing-resource signal unless the upstream call itself reports success.

## Decision: Register Through Existing Dispatcher-Compatible Tool Descriptors

Implementation should add `captions_delete` in the existing MCP tool registration/discovery path, using the same name, description, input schema, metadata, and handler concepts used by `activities_list`, `captions_list`, `captions_insert`, `captions_update`, and `captions_download`.

**Rationale**: The dispatcher already registers callable tools with `name`, `description`, `inputSchema`, `handler`, and optional metadata. YT-203 through YT-207 established concrete Layer 2 endpoint patterns. YT-208 should follow them instead of changing transport or registry architecture.

**Alternatives considered**:

- Add a new destructive-operation route outside MCP tools: rejected because MCP tool discovery/invocation already exists and the feature is a Layer 2 MCP tool.
- Special-case YouTube invocation outside the dispatcher: rejected because it would bypass existing registry and contract tests.
- Change all remaining captions endpoints in this slice: rejected because YT-208 is scoped only to `captions_delete`.

## Decision: Extend the Captions Layer 2 Module

The concrete `captions_delete` tool should live in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, with public exports added through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.

**Rationale**: YT-201 resource-family placement points endpoint tools to family modules, and YT-204 through YT-207 already established the concrete captions resource-module pattern. Extending the captions module keeps endpoint-specific schema, OAuth validation, deletion acknowledgment mapping, examples, and result shaping out of broad shared files while still using common contracts and conventions.

**Alternatives considered**:

- Add `captions_delete` directly to `youtube_common/examples.py`: rejected because examples are representative and not the concrete execution surface.
- Add endpoint-specific behavior to `contracts.py` or `conventions.py`: rejected because those modules own shared cross-cutting primitives.
- Create a separate delete-specific module for one endpoint: rejected until multiple concrete delete/acknowledgment endpoint slices need shared helpers.

## Decision: Keep Discovery Metadata Explicit and Safe

The implementation must ensure callers can inspect `captions_delete` quota, auth, upstream identity, availability, required `id`, delegation caveats, no-body request rule, destructive deletion behavior, and `204 No Content` acknowledgment semantics before invocation. If default dispatcher discovery needs metadata changes, those changes must be additive and preserve existing tool descriptors.

**Rationale**: YT-208 requires cost, OAuth, content-owner delegation, and destructive deletion visibility before calling. Existing shared contracts include safe public metadata validation, and current concrete Layer 2 tools already surface endpoint metadata through dispatcher-compatible descriptors.

**Alternatives considered**:

- Rely only on Python contract objects: rejected because MCP-facing discovery is user-visible behavior.
- Rewrite dispatcher descriptors broadly: rejected because baseline tools and current MCP contract tests must remain stable.
- Hide destructive deletion requirements only in prose docs: rejected because clients and reviewers need deterministic pre-invocation visibility.

## Decision: Keep Verification Constitution-Driven

Implementation must begin with failing tests, add minimal code, refactor, and finish with targeted checks plus `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The project constitution makes Red-Green-Refactor, integration/regression coverage, full-suite validation, and reStructuredText docstrings mandatory. YT-208 extends the concrete Layer 2 endpoint pattern established by YT-203 through YT-207 and will influence later mutation-acknowledgment slices.

**Alternatives considered**:

- Run only focused `captions_delete` tests: rejected because the constitution requires full-suite validation after final code changes.
- Treat docstrings as optional for private helper functions: rejected because the constitution requires every new or modified Python function.
- Skip integration checks because the handler can be unit-tested: rejected because public tool discovery and registration are MCP-facing behavior.
