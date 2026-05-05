# Contract: YT-142 Layer 1 `subscriptions.insert` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `subscriptions.insert` endpoint so maintainers can review endpoint identity, quota behavior, writable request scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `subscriptions.insert`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and subscription-creation boundary rules
- Review surfaces used by later subscription planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `subscriptions.insert` wrapper must expose:

- `resource_name` as `subscriptions`
- `operation_name` as `insert`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing supported creation inputs and writable-boundary expectations

Maintainer-facing review surfaces should also keep the minimum creation boundary visible, including the requirement that valid requests include a writable `snippet` carrying the target subscription relationship used to create the channel subscription.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request field carries the minimum `body` metadata payload for subscription creation
- which nested writable field identifies the minimum required target channel
- that `part=snippet` and the supported writable `snippet` form the minimum supported create boundary for this slice
- which optional writable fields are supported and which are outside the promised contract, including unsupported top-level or nested request fields in this slice
- that unsupported field combinations are not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required target-channel input, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that create a subscription relationship are successful
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must also make it possible for later layers to distinguish an access-related create failure from an `invalid_request` failure, a duplicate or ineligible target outcome, or an upstream create failure returned after execution begins.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `subscriptions.insert` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary for one writable subscription-create request
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-write artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, writable input handling, and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `subscriptions.insert` contract details without losing quota, auth, or writable-boundary visibility

## Invariants

- YT-142 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets and OAuth tokens must never appear in contract artifacts, tests, or logs
