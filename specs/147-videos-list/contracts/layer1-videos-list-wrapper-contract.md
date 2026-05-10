# Contract: YT-147 Layer 1 `videos.list` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `videos.list` so maintainers can review selector behavior, mixed-auth access expectations, quota visibility, collection-refinement boundaries, and normalized result boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `videos.list`
- Maintainer-visible endpoint identity and quota cost (`1`)
- Deterministic request boundary for supported `part` plus exactly one selector from `id`, `chart`, or `myRating`
- Collection-only refinements through `pageToken` and `maxResults`
- Chart-oriented refinements through `regionCode` and `videoCategoryId`
- Mixed-auth behavior for public-compatible and OAuth-required selector paths
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `videos.list` wrapper must expose:

- `resource_name` as `videos`
- `operation_name` as `list`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as mixed or conditional access
- `quota_cost` as `1`
- `auth_condition_note` explaining which selector paths use API-key access and which require OAuth
- `lifecycle_state` as the standard active label for this slice
- maintainer-facing notes describing selector boundaries, paging limits, chart refinements, and empty-result interpretation

The wrapper must keep request boundaries, auth guidance, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` is required for all supported requests
- that exactly one selector from `id`, `chart`, or `myRating` is required
- that `pageToken` and `maxResults` are supported only for collection-style retrieval
- that `regionCode` and `videoCategoryId` are chart-oriented refinements for this slice
- that the wrapper supports one video lookup profile per request
- that undocumented modifiers or extra top-level fields are outside the wrapper boundary
- that unsupported fields are rejected or clearly flagged before execution
- that the request contract remains deterministic and is not silently rewritten to another lookup profile

## Response Contract Expectations

The wrapper must preserve the shared executor success or failure split:

- valid requests return normalized success, including empty item lists when no videos match the selected lookup profile
- request-shape failures are explicit normalized `invalid_request` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation, quota visibility, selector visibility, auth-path visibility, and supported refinement context for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `videos.list` identity, quota cost, and mixed-auth behavior in one review pass
- determine the supported `part` plus selector boundary without reading implementation code
- distinguish malformed requests from valid requests that return zero videos
- determine which refinements are allowed only for chart retrieval or collection retrieval
- determine that public Layer 2 exposure is outside this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `GET` request construction and normalized video-result handling

## Invariants

- YT-147 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
