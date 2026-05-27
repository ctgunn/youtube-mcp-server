# Research: YT-203 Layer 2 Tool `activities_list`

## Decision: Implement One Concrete Layer 2 Tool Backed by Existing Layer 1 `activities.list`

YT-203 should expose only the public `activities_list` MCP tool and should rely on the existing YT-103 Layer 1 `activities.list` wrapper for endpoint identity, selector-aware auth behavior, quota cost, and upstream execution.

**Rationale**: The seed defines YT-203 as a single endpoint-tool slice. YT-201 and YT-202 already define shared Layer 2 naming, metadata, response-boundary, quota, auth, and safety standards; YT-103 already provides the internal `activities.list` capability. Reusing those artifacts keeps the implementation small and avoids a duplicate upstream request path.

**Alternatives considered**:

- Reimplement `activities.list` request execution directly in the Layer 2 handler: rejected because it would duplicate Layer 1 execution and error normalization.
- Add a broad Layer 2 YouTube endpoint framework in this slice: rejected because YT-201/YT-202 already provide shared scaffolding, and YT-203 is scoped to one endpoint.
- Defer public execution and add only another representative descriptor: rejected because YT-203 acceptance requires Layer 2 to expose `activities_list`.

## Decision: Use Official `activities.list` Contract as the Public Tool Boundary

The public `activities_list` input contract should preserve the official endpoint concepts: required `part`, exactly one selector from `channelId`, `home`, or `mine`, optional `maxResults`, `pageToken`, `publishedAfter`, `publishedBefore`, and `regionCode`, and no request body. The official quota cost is `1`.

**Rationale**: Layer 2 is the near-raw endpoint layer. The current official YouTube documentation describes `GET https://www.googleapis.com/youtube/v3/activities`, quota cost `1`, required `part`, filters that specify exactly one selector, optional pagination/date/region parameters, and a response with `nextPageToken`, `prevPageToken`, `pageInfo`, and `items`. Source: https://developers.google.com/youtube/v3/docs/activities/list

**Alternatives considered**:

- Hide deprecated `home` entirely: rejected for planning because it remains an official selector but must carry a deprecation/auth caveat.
- Support only `channelId`: rejected because the Layer 1 wrapper and upstream endpoint also define authorized-user selectors; callers need visible conditional auth behavior.
- Add friendlier non-upstream aliases for selectors: rejected because Layer 2 should stay close to upstream semantics.

## Decision: Declare Mixed/Conditional Auth With Selector-Level Notes

`activities_list` should declare auth mode `mixed/conditional`: `channelId` supports public channel activity retrieval, while `mine` and `home` require eligible user authorization. The `home` selector must also be flagged as deprecated.

**Rationale**: The feature spec requires callers to understand access before invocation. The existing Layer 1 wrapper already distinguishes `channelId` from `mine` and `home`, and the official docs mark `home` as deprecated and authorized-request-only. Public metadata and usage notes should expose that split before a caller invokes the tool.

**Alternatives considered**:

- Declare the whole tool `api_key`: rejected because authorized-user selectors would be misleading.
- Declare the whole tool `oauth_required`: rejected because public `channelId` use would be unnecessarily hidden.
- Model each selector as a separate public tool: rejected because the seed names one `activities_list` tool that stays close to upstream filter behavior.

## Decision: Preserve Near-Raw Activity Collection Results

Successful `activities_list` results should preserve upstream-visible activity collection concepts: `items`, requested parts, `nextPageToken`, `prevPageToken`, `pageInfo`, and endpoint/quota metadata allowed by shared Layer 2 response-boundary rules. Valid empty results are successful empty collections.

**Rationale**: Layer 2 callers need endpoint-backed data for raw exploration and debugging. Shared YT-201/YT-202 conventions allow light wrapper fields for MCP clarity but reject higher-level composition, ranking, enrichment, and heuristics.

**Alternatives considered**:

- Return a normalized activity summary only: rejected because that belongs to higher-layer consumer helpers or Layer 3.
- Hide pagination behind automatic multi-page fetching: rejected because Layer 2 should preserve upstream pagination behavior.
- Treat no items as an error: rejected because the upstream endpoint can validly return an empty collection.

## Decision: Validate Selector Exclusivity Before Invocation

The public tool should require exactly one supported selector mode for each request and reject missing or conflicting selectors with stable caller-facing validation feedback before treating the request as supported endpoint usage.

**Rationale**: The official endpoint requires exactly one filter selector, and YT-103 requires deterministic selector validation. Early validation avoids ambiguous auth behavior and prevents silent fallback between public and authorized-user views.

**Alternatives considered**:

- Let upstream YouTube reject invalid combinations: rejected because MCP callers should receive stable local validation guidance.
- Prefer one selector when multiple are supplied: rejected because that would silently change request meaning and auth expectations.
- Allow selector-free defaults: rejected because the endpoint requires an explicit filter selector.

## Decision: Register Through Existing Dispatcher-Compatible Tool Descriptors

Implementation should add `activities_list` in the existing MCP tool registration/discovery path, using the same name, description, input schema, and handler concepts that current tools and representative YouTube descriptors already use.

**Rationale**: The dispatcher already registers callable tools with `name`, `description`, `inputSchema`, and `handler`. Existing YouTube representative descriptors prove metadata can be attached for review/discovery while remaining safe. YT-203 should make one concrete endpoint tool executable without changing transport or dispatcher architecture.

**Alternatives considered**:

- Add a new transport route for YouTube tools: rejected because MCP tool discovery/invocation already exists.
- Special-case YouTube invocation outside the dispatcher: rejected because it would bypass existing registry and contract tests.
- Change all representative descriptors into executable tools: rejected because YT-203 should affect only `activities_list`.

## Decision: Add an Activities-Specific Layer 2 Module

The concrete `activities_list` tool should live in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/activities.py`, with public exports added through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.

**Rationale**: YT-201 resource-family placement already points activities endpoint tools to a family module. A focused `activities.py` keeps endpoint-specific schema, selector validation, handler wiring, examples, and result shaping out of broad shared files while still using common contracts and conventions.

**Alternatives considered**:

- Add `activities_list` directly to `youtube_common/examples.py`: rejected because examples are representative and non-executing.
- Add endpoint-specific behavior to `contracts.py` or `conventions.py`: rejected because those modules own shared cross-cutting primitives.
- Create a top-level `tools/youtube.py` catalog module for all endpoints: rejected because the seed and YT-201 require resource-family cohesion and avoidance of one large endpoint module.

## Decision: Treat Discovery Metadata as an Explicit Implementation Question

The implementation must decide, through tests, whether `activities_list` metadata needs to be visible through the default dispatcher `tools/list` response or through adjacent catalog/contract surfaces. If public discovery must expose metadata, dispatcher changes should be additive and preserve existing baseline tool descriptors.

**Rationale**: Existing representative YouTube descriptors include a `metadata` object, but `InMemoryToolDispatcher.register_tool()` currently stores only `name`, `description`, `inputSchema`, and `handler`, and `list_tools()` returns only the first three public descriptor fields. The YT-203 spec requires callers to inspect quota/auth/upstream identity before invocation, so tasks must make this visibility path explicit.

**Alternatives considered**:

- Ignore dispatcher metadata because contract tests can inspect Python objects: rejected because MCP-facing discovery is user-visible behavior.
- Rewrite dispatcher descriptors broadly: rejected because baseline tools and current MCP contract tests must remain stable.
- Hide metadata only in prose docs: rejected because callers and reviewers need deterministic pre-invocation visibility.

## Decision: Enforce Selector Exclusivity Outside Basic Dispatcher Schema Composition

`activities_list` must enforce exactly-one selector behavior in endpoint-specific validation or a deliberately small reusable validator, not rely solely on current dispatcher `oneOf` support.

**Rationale**: The dispatcher currently checks whether one required option is satisfied but does not reject requests that satisfy more than one selector option. `activities.list` requires exactly one selector, and selector choice also determines auth requirements. The concrete tool must therefore protect this rule before endpoint execution.

**Alternatives considered**:

- Depend only on JSON-schema `oneOf` metadata: rejected because current dispatcher validation is intentionally simplified.
- Let Layer 1 reject conflicts after dispatch: rejected because public Layer 2 validation should give direct caller-facing guidance and protect auth semantics.
- Silently prefer `channelId` over `mine` or `home`: rejected because that changes request meaning and can mask authorization errors.

## Decision: Keep Verification Constitution-Driven

Implementation must begin with failing tests, add minimal code, refactor, and finish with targeted checks plus `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The project constitution makes Red-Green-Refactor, integration/regression coverage, full-suite validation, and reStructuredText docstrings mandatory. This is the first concrete Layer 2 tool, so the verification pattern will influence later endpoint slices.

**Alternatives considered**:

- Run only focused `activities_list` tests: rejected because the constitution requires full-suite validation after final code changes.
- Treat docstrings as optional for private helper functions: rejected because the constitution requires every new or modified Python function.
- Skip integration checks because the handler can be unit-tested: rejected because public tool discovery and registration are MCP-facing behavior.
