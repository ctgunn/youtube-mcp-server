# Contract: YT-123 Layer 1 `guideCategories.list` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `guideCategories.list` so maintainers can review region lookup behavior, API-key access expectations, quota visibility, deprecated lifecycle guidance, and normalized result boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `guideCategories.list`
- Maintainer-visible endpoint identity and quota cost (`1`)
- Deterministic request boundary for supported `part` plus `regionCode` lookups
- API-key behavior for region-based guide-category retrieval
- Reviewable deprecated-or-unavailable lifecycle guidance
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `guideCategories.list` wrapper must expose:

- `resource_name` as `guideCategories`
- `operation_name` as `list`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as API-key access
- `quota_cost` as `1`
- `lifecycle_state` as a reviewable deprecated lifecycle label for this slice
- a maintainer-facing `caveat_note` describing deprecated or unavailable endpoint behavior
- maintainer-facing notes describing request boundaries, empty-result interpretation, and lifecycle-aware failure guidance

The wrapper must keep request boundaries, lifecycle caveat handling, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` and `regionCode` are required for supported lookup requests
- that the wrapper supports one region-scoped lookup per request
- that undocumented modifiers or extra top-level fields are outside the wrapper boundary
- that unsupported fields are rejected or clearly flagged before execution
- that the request contract remains deterministic and is not silently rewritten to another lookup profile

## Response Contract Expectations

The wrapper must preserve the shared executor success or failure split:

- valid requests return normalized success, including empty item lists when no guide categories match the selected region
- request-shape failures are explicit normalized `invalid_request` outcomes
- deprecated-or-unavailable endpoint outcomes are explicit normalized lifecycle-aware failures
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation, quota visibility, and lifecycle visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `guideCategories.list` identity, quota cost, API-key access, and deprecated lifecycle status in one review pass
- determine the supported `part` plus `regionCode` request boundary without reading implementation code
- distinguish malformed requests from valid requests that encounter deprecated-or-unavailable endpoint behavior
- understand that empty results remain successful retrieval outcomes rather than lifecycle failures
- determine that public Layer 2 exposure is outside this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `GET` request construction and normalized guide-category result handling

## Invariants

- YT-123 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
