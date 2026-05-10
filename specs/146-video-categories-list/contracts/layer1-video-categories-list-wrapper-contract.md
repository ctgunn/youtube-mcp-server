# Contract: YT-146 Layer 1 `videoCategories.list` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `videoCategories.list` so maintainers can review selector behavior, API-key access expectations, quota visibility, region guidance, optional display-language usage, and normalized result boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `videoCategories.list`
- Maintainer-visible endpoint identity and quota cost (`1`)
- Deterministic request boundary for supported `part` plus exactly one selector from `id` or `regionCode`
- Optional `hl` guidance for display-language-sensitive category review
- API-key behavior for both direct category lookup and region-scoped category browsing
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `videoCategories.list` wrapper must expose:

- `resource_name` as `videoCategories`
- `operation_name` as `list`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as API-key access
- `quota_cost` as `1`
- `lifecycle_state` as the standard active label for this slice
- maintainer-facing notes describing selector boundaries, optional `hl` usage, region behavior, and empty-result interpretation

The wrapper must keep request boundaries, selector guidance, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` is required for all supported requests
- that exactly one selector from `id` or `regionCode` is required
- that `hl` is optional guidance rather than a standalone selector
- that the wrapper supports one category lookup profile per request
- that undocumented modifiers or extra top-level fields are outside the wrapper boundary
- that unsupported fields are rejected or clearly flagged before execution
- that the request contract remains deterministic and is not silently rewritten to another lookup profile

## Response Contract Expectations

The wrapper must preserve the shared executor success or failure split:

- valid requests return normalized success, including empty item lists when no categories match the selected lookup profile
- request-shape failures are explicit normalized `invalid_request` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation, quota visibility, selector visibility, and optional display-language context for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `videoCategories.list` identity, quota cost, and API-key access in one review pass
- determine the supported `part` plus selector boundary without reading implementation code
- distinguish malformed requests from valid requests that return zero categories
- understand that optional `hl` guidance does not replace the required selector
- determine that public Layer 2 exposure is outside this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `GET` request construction and normalized video-category result handling

## Invariants

- YT-146 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
