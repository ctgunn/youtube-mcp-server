# Contract: YT-134 Layer 1 `playlistItems.update` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `playlistItems.update` endpoint so maintainers can review endpoint identity, quota behavior, writable request scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `playlistItems.update`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and playlist-item update boundary rules
- Review surfaces used by later playlist-item planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `playlistItems.update` wrapper must expose:

- `resource_name` as `playlistItems`
- `operation_name` as `update`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing supported update inputs and writable-boundary expectations

Maintainer-facing review surfaces should also keep the minimum update boundary visible, including the requirement that valid requests include the existing playlist-item identifier plus a writable `snippet` carrying playlist and referenced-video context.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request field carries the minimum `body` metadata payload for playlist-item updates
- which nested writable fields identify the existing playlist item, its target playlist, and the referenced video
- that `part` and the supported writable `snippet` form the minimum supported update boundary for this slice
- which optional writable fields are supported and which are outside the promised contract
- that unsupported field combinations are not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required identifier and playlist/video context inputs, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that update a playlist-item resource are successful
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must also make it possible for later layers to distinguish an access-related update failure from an `invalid_request` failure or an upstream update failure returned after execution begins.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `playlistItems.update` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary for one writable playlist-item update request
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-write artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, writable input handling, and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `playlistItems.update` contract details without losing quota, auth, or writable-boundary visibility

## Invariants

- YT-134 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets and OAuth tokens must never appear in contract artifacts, tests, or logs
