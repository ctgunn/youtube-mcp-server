# Contract: YT-110 Layer 1 `channels.list` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `channels.list` so maintainers can review selector behavior, mixed-auth expectations, quota visibility, and normalized result boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `channels.list`
- Maintainer-visible endpoint identity and quota cost (`1`)
- Selector-based request boundary for supported retrieval paths
- Mixed-auth behavior driven by active selector mode
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `channels.list` wrapper must expose:

- `resource_name` as `channels`
- `operation_name` as `list`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as mixed or conditional
- `quota_cost` as `1`
- maintainer-facing notes describing selector rules and auth implications

The wrapper must keep selector-dependent auth behavior and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which selectors are supported for this slice (`id`, `mine`, `forHandle`, and username-style lookup when supported)
- that exactly one selector may be active in a supported request
- which optional near-raw retrieval fields are accepted
- which selector combinations are unsupported
- that unsupported fields or combinations are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another selector profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid requests return normalized success, including empty item lists when no channels match
- selector-validation failures are explicit normalized `invalid_request` outcomes
- selector-auth mismatches are explicit normalized `auth` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `channels.list` identity, quota cost, and mixed-auth behavior in one review pass
- determine supported selectors and selector exclusivity rules without reading implementation code
- determine how `mine` differs from public selector paths
- understand the username-style conditional support caveat where applicable
- distinguish validation failures, auth failures, and successful empty results

Validation must include:

- unit tests for wrapper metadata and selector validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing selector-compatible request construction and normalization

## Invariants

- YT-110 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
