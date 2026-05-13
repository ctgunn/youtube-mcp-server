# Contract: YT-150 Layer 1 `videos.rate` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `videos.rate` endpoint so maintainers can review endpoint identity, quota behavior, rating request scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `videos.rate`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and rating-action boundary rules
- Review surfaces used by later video-rating planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `videos.rate` wrapper must expose:

- `resource_name` as `videos`
- `operation_name` as `rate`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing supported rating inputs and rating-boundary expectations

Maintainer-facing review surfaces should also keep the minimum rating boundary visible, including the requirement that valid requests include the target video identifier and one supported rating action.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `id` carries the target video identifier for the rating mutation
- that `rating` carries the requested rating action
- that `like`, `dislike`, and `none` are the supported action set for this slice
- that `none` represents the clear-rating path for this slice
- which optional or undocumented fields are outside the promised contract
- that unsupported action values or undocumented fields are not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required identifier and action inputs, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that rate or clear rating on a video are successful acknowledgement outcomes
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must also make it possible for later layers to distinguish an access-related rating failure from an `invalid_request` failure or an upstream rating failure returned after execution begins.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `videos.rate` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary for one video-rating request
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-rating artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, rating-input handling, and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `videos.rate` contract details without losing quota, auth, or rating-boundary visibility

## Invariants

- YT-150 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets and OAuth tokens must never appear in contract artifacts, tests, or logs
