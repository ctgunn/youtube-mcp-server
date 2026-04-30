# Contract: YT-135 Layer 1 `playlistItems.delete` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `playlistItems.delete` so maintainers can review delete-input behavior, OAuth-required expectations, quota visibility, and normalized delete boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `playlistItems.delete`
- Maintainer-visible endpoint identity and quota cost of `50`
- Deterministic delete boundary for one supported playlist-item identifier request
- OAuth-required behavior for playlist-item deletion
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `playlistItems.delete` wrapper must expose:

- `resource_name` as `playlistItems`
- `operation_name` as `delete`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing delete preconditions, authorization expectations, target-state sensitivity, and unsupported-request boundaries

The wrapper must keep delete boundaries, authorization expectations, and quota visibility in one review surface.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that one playlist-item identifier is required for supported delete requests
- that the supported identifier is the `id` field used for one target playlist item
- that the supported request remains identifier-only for this slice and does not require `part` or `body`
- that unsupported fields, malformed identifiers, or incomplete delete requests are rejected or clearly flagged before execution
- that this slice is centered on one deterministic playlist-item delete path rather than bulk deletion

The request contract must remain deterministic. A request must not be silently rewritten to another delete profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized deletion acknowledgment result even when the upstream delete success path returns no content body
- successful normalized results keep the deleted playlist-item identity visible as a stable delete acknowledgment
- invalid request shape outcomes are explicit normalized `invalid_request` failures
- unauthorized access outcomes are explicit and distinct from invalid-request outcomes
- unavailable-target or target-state failures are explicit and distinguishable from auth and upstream failures
- normalized upstream delete failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `playlistItems.delete` identity, quota cost of `50`, and OAuth-required behavior in one review pass
- determine supported delete preconditions without reading implementation code
- determine that one playlist-item identifier is the supported delete boundary for this slice
- understand how unavailable-target cases differ from unauthorized access and normalized upstream delete failures
- identify that unsupported delete shapes are outside the supported wrapper boundary

Validation must include:

- unit tests for wrapper metadata and delete-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `DELETE` request construction and normalized delete handling
- consumer-facing checks showing higher layers can summarize `playlistItems.delete` contract details without losing quota or auth visibility

## Invariants

- YT-135 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
