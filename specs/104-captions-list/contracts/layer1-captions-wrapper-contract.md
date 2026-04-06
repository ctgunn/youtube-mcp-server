# Contract: YT-104 Layer 1 `captions.list` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `captions.list` endpoint so maintainers can review endpoint identity, quota behavior, request scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `captions.list`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and selector-boundary rules
- Review surfaces used by later transcript and caption-management planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `captions.list` wrapper must expose:

- `resource_name` as `captions`
- `operation_name` as `list`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing supported selector paths and optional delegation context

Maintainer-facing review surfaces should also keep the supported selector boundary visible, including the exclusive selector set `videoId` and `id`.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request fields select caption-track listing by `videoId`
- which request fields select direct caption-track lookup by `id`
- whether `onBehalfOfContentOwner` may accompany an otherwise supported authorized request
- which field combinations are unsupported for this internal wrapper
- that unsupported combinations are not part of the promised Layer 1 contract

The request contract must remain deterministic. Exactly one of `videoId` or `id` must be present for supported requests, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that return caption tracks are successful
- valid requests that return zero caption tracks are also successful
- normalized upstream failures remain failure outcomes

The contract must not reinterpret no available caption tracks as a wrapper error.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `captions.list` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary for `videoId`, `id`, and optional delegation guidance without reading raw upstream docs

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-selector artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `captions.list` contract details without losing quota or auth visibility

## Invariants

- YT-104 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, and delegation credentials must never appear in contract artifacts, tests, or logs
