# Contract: YT-151 Layer 1 `videos.getRating` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `videos.getRating` endpoint so maintainers can review endpoint identity, quota behavior, identifier request scope, returned rating-state semantics, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `videos.getRating`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and returned rating-state boundary rules
- Review surfaces used by later video-rating lookup planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `videos.getRating` wrapper must expose:

- `resource_name` as `videos`
- `operation_name` as `getRating`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing supported identifier inputs, returned rating states, and lookup-boundary expectations

Maintainer-facing review surfaces should also keep the minimum lookup boundary visible, including the requirement that valid requests include the target video identifier field through `id` and that successful results may contain rated or unrated viewer states.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `1` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `id` carries the target video identifier input for the rating lookup
- that the wrapper supports one or more comma-delimited video identifiers through that field
- that one lookup request may include at most 50 video identifiers in this slice
- which broader list-style or undocumented request shapes are outside the promised contract
- that unsupported identifier forms or undocumented fields are not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required identifier input, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that retrieve a viewer rating state are successful lookup outcomes
- successful unrated results remain successful outcomes rather than failure or empty-request states
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must also make it possible for later layers to distinguish an access-related lookup failure from an `invalid_request` failure, an upstream lookup failure returned after execution begins, or a successful unrated result.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `videos.getRating` in one review pass
- find the quota cost of `1` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported identifier boundary for one lookup request
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-rating artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, identifier handling, and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `videos.getRating` contract details without losing quota, auth, or returned-state visibility

## Invariants

- YT-151 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets and OAuth tokens must never appear in contract artifacts, tests, or logs
