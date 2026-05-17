# Contract: YT-153 Layer 1 `videos.delete` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `videos.delete` endpoint so maintainers can review endpoint identity, quota behavior, target-video request scope, destructive delete semantics, successful acknowledgement behavior, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `videos.delete`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and delete-boundary rules
- Review surfaces used by later video-management planning

This contract does not define a public MCP tool, hosted-route behavior, MCP transport changes, bulk deletion behavior, video listing behavior, or broader video lifecycle management.

## Required Wrapper Metadata

The `videos.delete` wrapper must expose:

- `resource_name` as `videos`
- `operation_name` as `delete`
- `operation_key` as `videos.delete`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing required target identifier, no-body delete behavior, optional partner-only delegation boundary, destructive-action semantics, successful acknowledgement behavior, and failure-boundary expectations

Maintainer-facing review surfaces should also keep the minimum delete boundary visible, including the requirement that valid requests include an `id` query input identifying one target video.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `id` identifies the target video being deleted
- that a supported request deletes one target video per call
- that the endpoint does not accept a request body
- whether partner-only `onBehalfOfContentOwner` is supported for this slice or is outside the guaranteed boundary
- which broader, misspelled, bulk, body-driven, or undocumented request shapes are outside the promised contract
- that unsupported fields are not silently forwarded as if they were part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required target identifier, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that are accepted by the upstream service are successful deletion acknowledgement outcomes
- successful no-content upstream responses are normalized into a reviewable acknowledgement instead of an empty or ambiguous result
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must also make it possible for later layers to distinguish an access-related delete failure from an `invalid_request` failure, an upstream forbidden failure, a video-not-found failure, an upstream unavailability failure, or a successful acknowledgement.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `videos.delete` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported target-video identifier boundary for one delete request
- understand that successful deletion is represented as a normalized acknowledgement rather than a returned video resource
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-delete artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, required query parameters, OAuth access, no-body behavior, and no-content acknowledgement behavior
- consumer-facing checks showing higher layers can summarize `videos.delete` contract details without losing quota, auth, target identifier, or acknowledgement visibility

## Invariants

- YT-153 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, target-owner identity, and delegated-owner credentials must never appear in contract artifacts, tests, logs, or normalized summaries
