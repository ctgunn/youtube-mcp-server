# Contract: YT-155 Layer 1 `watermarks.unset` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `watermarks.unset` endpoint so maintainers can review endpoint identity, quota behavior, target-channel request scope, no-upload behavior, successful acknowledgement behavior, no-removal-possible handling, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `watermarks.unset`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and no-upload boundary rules
- Review surfaces used by later watermark and channel-branding planning

This contract does not define a public MCP tool, hosted-route behavior, MCP transport changes, watermark-setting behavior, media-upload behavior, bulk channel-branding behavior, or broader channel lifecycle management.

## Required Wrapper Metadata

The `watermarks.unset` wrapper must expose:

- `resource_name` as `watermarks`
- `operation_name` as `unset`
- `operation_key` as `watermarks.unset`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing required `channelId`, absence of watermark metadata or media upload input, optional partner-only delegation boundary, successful acknowledgement behavior, no-removal-possible behavior, and failure-boundary expectations

Maintainer-facing review surfaces should also keep the minimum request boundary visible, including the requirement that valid requests include a `channelId` query input identifying one target channel.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `channelId` identifies the channel whose watermark will be removed
- that a supported request removes one target channel watermark per call
- that a supported request does not include watermark resource metadata
- that a supported request does not include media upload content
- whether partner-only `onBehalfOfContentOwner` is supported for this slice or is outside the guaranteed boundary
- which broader, misspelled, upload-oriented, metadata-oriented, bulk, or undocumented request shapes are outside the promised contract
- that unsupported fields are not silently forwarded as if they were part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required channel identifier, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that are accepted by the upstream service are successful watermark-removal acknowledgement outcomes
- successful no-content upstream responses are normalized into a reviewable acknowledgement instead of an empty or ambiguous result
- invalid request shapes are rejected before execution when determinable locally
- normalized upstream failures remain failure outcomes
- no-current-watermark, already-removed, or not-found outcomes remain distinguishable from both successful removals and generic upstream failures

The contract must also make it possible for later layers to distinguish an access-related failure from an `invalid_request` failure, unsupported payload failure, forbidden channel failure, no-removal-possible outcome, upstream unavailability failure, or successful acknowledgement.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `watermarks.unset` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported target-channel and no-upload boundary for one watermark-unset request
- understand that successful watermark removal is represented as a normalized acknowledgement rather than a returned watermark resource
- understand that no-current-watermark or already-removed states are handled distinctly from successful removal
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-boundary artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, required query parameters, OAuth access, no-upload behavior, and no-content acknowledgement behavior
- consumer-facing checks showing higher layers can summarize `watermarks.unset` contract details without losing quota, auth, target channel, no-upload, no-removal, or acknowledgement visibility

## Invariants

- YT-155 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, channel-owner identity, delegated-owner credentials, and unrelated watermark media data must never appear in contract artifacts, tests, logs, normalized results, or summaries
