# Contract: YT-105 Layer 1 `captions.insert` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `captions.insert` endpoint so maintainers can review endpoint identity, quota behavior, upload-sensitive request scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `captions.insert`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and upload-boundary rules
- Review surfaces used by later caption-management planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `captions.insert` wrapper must expose:

- `resource_name` as `captions`
- `operation_name` as `insert`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing supported creation inputs and optional delegation context

Maintainer-facing review surfaces should also keep the minimum creation boundary visible, including the requirement that valid requests include both caption metadata and media-upload input.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `400` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request field carries the minimum `body` metadata payload for caption creation
- which request field carries the required `media` upload content
- whether `onBehalfOfContentOwner` may accompany an otherwise supported authorized request
- which field combinations are unsupported for this internal wrapper
- that unsupported metadata-only or upload-only combinations are not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include both metadata and media-upload input, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that create a caption resource are successful
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must not reinterpret incomplete creation requests as partially supported behavior.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `captions.insert` in one review pass
- find the quota cost of `400` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand that the endpoint is upload-sensitive and requires both metadata and media-upload input
- understand optional delegation guidance without reading raw upstream docs

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-upload artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `captions.insert` contract details without losing quota or auth visibility

## Invariants

- YT-105 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, caption media payloads, and delegation credentials must never appear in contract artifacts, tests, or logs
