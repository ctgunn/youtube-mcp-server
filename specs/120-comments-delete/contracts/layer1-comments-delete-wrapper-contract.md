# Contract: YT-120 Layer 1 `comments.delete` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `comments.delete` so maintainers can review delete-target behavior, OAuth-required expectations, quota visibility, and normalized delete boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `comments.delete`
- Maintainer-visible endpoint identity and quota cost (`50`)
- Deterministic delete boundary for one supported comment identifier request
- OAuth-required behavior for comment deletion
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `comments.delete` wrapper must expose:

- `resource_name` as `comments`
- `operation_name` as `delete`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing delete preconditions, authorization expectations, any optional delegation inputs surfaced for this slice, and unavailable-target or unsupported-request boundaries

The wrapper must keep delete boundaries, authorization expectations, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that one comment identifier is required for supported delete requests
- that the supported identifier is the `id` field used for one target comment
- that the supported request remains query-only and does not require a request body
- which optional delegation inputs are accepted for eligible authorized requests, with `onBehalfOfContentOwner` treated as the supported delegated-owner field for this slice
- that unsupported fields, malformed identifiers, or incomplete delete requests are rejected or clearly flagged before execution
- that this slice is centered on one deterministic comment delete path rather than bulk deletion

The request contract must remain deterministic. A request must not be silently rewritten to another delete profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized deletion acknowledgment result even when the upstream delete success path returns no content body
- successful normalized results keep the deleted comment identity visible as a stable delete acknowledgment
- invalid delete requests are explicit normalized `invalid_request` outcomes
- auth mismatches are explicit normalized `auth` outcomes
- unavailable-target or target-state failures are explicit and distinguishable from auth and upstream failures
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `comments.delete` identity, quota cost, and OAuth-required behavior in one review pass
- determine supported delete preconditions without reading implementation code
- determine whether optional delegation inputs are supported for eligible authorized requests
- understand how unavailable-target cases differ from auth failures and normalized upstream delete failures
- identify that unsupported delete shapes are outside the supported wrapper boundary

Validation must include:

- unit tests for wrapper metadata and delete-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `DELETE` request construction and normalized delete handling

## Invariants

- YT-120 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
