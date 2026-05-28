# Research: YT-204 Layer 2 Tool `captions_list`

## Decision: Implement One Concrete Layer 2 Tool Backed by Existing Layer 1 `captions.list`

YT-204 should expose only the public `captions_list` MCP tool and should rely on the existing YT-104 Layer 1 `captions.list` wrapper for endpoint identity, OAuth behavior, quota cost, delegation context, request validation, and upstream execution.

**Rationale**: The seed defines YT-204 as a single endpoint-tool slice. YT-201 and YT-202 already define shared Layer 2 naming, metadata, response-boundary, quota, auth, and safety standards; YT-104 already provides the internal `captions.list` capability. Reusing those artifacts keeps the implementation small and avoids a duplicate upstream request path.

**Alternatives considered**:

- Reimplement `captions.list` request execution directly in the Layer 2 handler: rejected because it would duplicate Layer 1 execution and error normalization.
- Add a broad captions endpoint framework in this slice: rejected because YT-201/YT-202 already provide shared scaffolding, and YT-204 is scoped to one endpoint.
- Defer public execution and add only another representative descriptor: rejected because YT-204 acceptance requires Layer 2 to expose `captions_list`.

## Decision: Use Official `captions.list` Contract as the Public Tool Boundary

The public `captions_list` input contract should preserve the official endpoint concepts: required `part`, required `videoId`, optional `id`, optional `maxResults`, optional `pageToken`, optional `onBehalfOfContentOwner`, no request body, and official quota cost `50`.

**Rationale**: Layer 2 is the near-raw endpoint layer. The current official YouTube documentation describes `GET https://www.googleapis.com/youtube/v3/captions`, quota cost `50`, required `part` and `videoId`, optional `id`, `maxResults`, `pageToken`, and `onBehalfOfContentOwner`, OAuth scope requirements, and a response with `nextPageToken`, `prevPageToken`, `pageInfo`, and `items`. Source: https://developers.google.com/youtube/v3/docs/captions/list

**Alternatives considered**:

- Require only `id` and omit `videoId`: rejected because the official endpoint requires `videoId` for caption listing.
- Add friendlier aliases for caption lookup fields: rejected because Layer 2 should stay close to upstream semantics.
- Auto-discover caption tracks through higher-level transcript or video tools: rejected because cross-endpoint discovery belongs to higher layers.

## Decision: Declare OAuth-Required Auth With Delegation Notes

`captions_list` should declare auth mode `oauth_required`. Public metadata and usage notes must make clear that eligible OAuth authorization is required and that `onBehalfOfContentOwner` is optional delegated content-owner context when the caller has the matching permission.

**Rationale**: Caption access is permission-sensitive, and the official docs require OAuth scopes for `captions.list`. The existing YT-104 Layer 1 wrapper already models `AuthMode.OAUTH_REQUIRED` and optional `onBehalfOfContentOwner` delegation. Public callers need this before invocation so they do not treat caption tracks as public video metadata.

**Alternatives considered**:

- Declare the tool `api_key`: rejected because that would misrepresent caption access.
- Declare mixed/conditional auth: rejected because the official endpoint and current Layer 1 wrapper require OAuth for the supported request path.
- Hide delegation details until errors occur: rejected because delegated-owner context materially affects valid caption access.

## Decision: Preserve Near-Raw Caption Track Collection Results

Successful `captions_list` results should preserve upstream-visible caption collection concepts: `items`, requested parts, `nextPageToken`, `prevPageToken`, `pageInfo`, endpoint identity, quota cost, lookup summary, and delegation summary when present. Valid empty results are successful empty collections.

**Rationale**: Layer 2 callers need endpoint-backed data for raw exploration, debugging, and transcript preparation. Shared YT-201/YT-202 conventions allow light wrapper fields for MCP clarity but reject higher-level composition, language ranking, transcript download, and heuristics.

**Alternatives considered**:

- Return only normalized language summaries: rejected because that belongs to higher-layer transcript discovery.
- Download caption content after listing: rejected because `captions.download` is a separate endpoint and Layer 2 tool.
- Treat no items as an error: rejected because a valid video can have zero visible caption tracks.

## Decision: Validate Required Lookup and OAuth Before Invocation

The public tool should require `part` and `videoId`, allow `id` only as an additional filter for caption-track lookup, reject unsupported fields, enforce page-size bounds, and reject missing OAuth authorization or invalid delegation context before treating the request as supported endpoint usage.

**Rationale**: The official endpoint requires `videoId`, and YT-104 already documents selector boundaries and authorization expectations. Early validation gives MCP callers stable remediation guidance and protects against ambiguous access failures.

**Alternatives considered**:

- Let upstream YouTube reject invalid combinations: rejected because MCP callers should receive stable local validation guidance.
- Allow selector-free defaults: rejected because the endpoint requires `videoId`.
- Treat missing authorization as not found: rejected because callers need to distinguish inaccessible captions from true absence of caption tracks.

## Decision: Register Through Existing Dispatcher-Compatible Tool Descriptors

Implementation should add `captions_list` in the existing MCP tool registration/discovery path, using the same name, description, input schema, metadata, and handler concepts used by `activities_list` and current shared YouTube descriptors.

**Rationale**: The dispatcher already registers callable tools with `name`, `description`, `inputSchema`, `handler`, and optional metadata. YT-203 established the first concrete Layer 2 endpoint pattern. YT-204 should follow it instead of changing transport or registry architecture.

**Alternatives considered**:

- Add a new transport route for captions tools: rejected because MCP tool discovery/invocation already exists.
- Special-case YouTube invocation outside the dispatcher: rejected because it would bypass existing registry and contract tests.
- Change all captions endpoints into executable tools in this slice: rejected because YT-204 is scoped only to `captions_list`.

## Decision: Add a Captions-Specific Layer 2 Module

The concrete `captions_list` tool should live in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, with public exports added through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.

**Rationale**: YT-201 resource-family placement points endpoint tools to family modules, and YT-203 already established the concrete resource-module pattern. A focused `captions.py` keeps endpoint-specific schema, OAuth validation, handler wiring, examples, and result shaping out of broad shared files while still using common contracts and conventions.

**Alternatives considered**:

- Add `captions_list` directly to `youtube_common/examples.py`: rejected because examples are representative and non-executing.
- Add endpoint-specific behavior to `contracts.py` or `conventions.py`: rejected because those modules own shared cross-cutting primitives.
- Create a top-level `tools/youtube.py` catalog module for all endpoints: rejected because the seed and YT-201 require resource-family cohesion and avoidance of one large endpoint module.

## Decision: Keep Discovery Metadata Explicit and Safe

The implementation must ensure callers can inspect `captions_list` quota, auth, upstream identity, availability, lookup inputs, delegation caveats, and usage notes before invocation. If default dispatcher discovery needs metadata changes, those changes must be additive and preserve existing tool descriptors.

**Rationale**: YT-204 requires cost and OAuth visibility before calling. Existing shared contracts include safe public metadata validation, and YT-203 already surfaced concrete endpoint metadata through dispatcher-compatible descriptors.

**Alternatives considered**:

- Rely only on Python contract objects: rejected because MCP-facing discovery is user-visible behavior.
- Rewrite dispatcher descriptors broadly: rejected because baseline tools and current MCP contract tests must remain stable.
- Hide metadata only in prose docs: rejected because clients and reviewers need deterministic pre-invocation visibility.

## Decision: Keep Verification Constitution-Driven

Implementation must begin with failing tests, add minimal code, refactor, and finish with targeted checks plus `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The project constitution makes Red-Green-Refactor, integration/regression coverage, full-suite validation, and reStructuredText docstrings mandatory. YT-204 follows the concrete Layer 2 endpoint pattern established by YT-203 and will influence later captions endpoint slices.

**Alternatives considered**:

- Run only focused `captions_list` tests: rejected because the constitution requires full-suite validation after final code changes.
- Treat docstrings as optional for private helper functions: rejected because the constitution requires every new or modified Python function.
- Skip integration checks because the handler can be unit-tested: rejected because public tool discovery and registration are MCP-facing behavior.
