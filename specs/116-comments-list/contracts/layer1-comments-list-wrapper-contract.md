# Contract: YT-116 Layer 1 `comments.list` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `comments.list` so maintainers can review selector behavior, quota visibility, optional modifier boundaries, and normalized result handling before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `comments.list`
- Maintainer-visible endpoint identity and quota cost (`1`)
- Selector-based request boundary for supported retrieval paths
- Public retrieval behavior for the seed-required selector set
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `comments.list` wrapper must expose:

- `resource_name` as `comments`
- `operation_name` as `list`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as `api_key` for the seed-supported selector set
- `quota_cost` as `1`
- maintainer-facing notes describing selector rules, optional modifiers, access implications, and empty-result guidance relevant to comments retrieval

The wrapper must keep selector behavior, quota visibility, and successful no-match handling in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which selectors are supported for this slice (`id` and `parentId`)
- that exactly one selector may be active in a supported request
- which optional near-raw retrieval fields are accepted (`pageToken`, `maxResults`, `textFormat`)
- which selector combinations are unsupported
- that unsupported fields or combinations are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another selector profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success or failure split:

- valid requests return normalized success, including empty item lists when no comments match
- selector-validation failures are explicit normalized `invalid_request` outcomes
- selector-access mismatches are explicit normalized `auth` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `comments.list` identity, quota cost, and supported selector set in one review pass
- determine supported selectors and selector exclusivity rules without reading implementation code
- understand that direct-comment lookup and reply lookup are separate supported paths
- distinguish validation failures, access mismatches, and successful empty results
- identify which optional modifiers stay inside the supported wrapper boundary

Validation must include:

- unit tests for wrapper metadata and selector validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing selector-compatible request construction and normalization

## Invariants

- YT-116 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
