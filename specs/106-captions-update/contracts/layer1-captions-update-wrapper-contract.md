# Contract: YT-106 Layer 1 `captions.update` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `captions.update` endpoint so maintainers can review endpoint identity, quota behavior, update-sensitive request scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `captions.update`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and media-update-boundary rules
- Review surfaces used by later caption-management planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `captions.update` wrapper must expose:

- `resource_name` as `captions`
- `operation_name` as `update`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing supported body-only and body-plus-media update inputs plus optional delegation context

Maintainer-facing review surfaces should also keep the minimum update boundary visible, including the requirement that valid requests include a caption resource `body`, may remain body-only for metadata updates, and may include `media` only for supported body-plus-media content-replacement updates.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `450` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request field carries the required `body` payload for caption updates
- when the `media` field is optional and when it is part of a supported update path
- whether `onBehalfOfContentOwner` may accompany an otherwise supported authorized request
- which field combinations are unsupported for this internal wrapper
- that `media` without `body` is not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include `body`, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that update a caption resource are successful
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must not reinterpret incomplete update requests as partially supported behavior.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `captions.update` in one review pass
- find the quota cost of `450` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary between body-only updates and body-plus-media updates
- understand optional delegation guidance without reading raw upstream docs

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-media artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `captions.update` contract details without losing quota or auth visibility

## Invariants

- YT-106 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, caption payloads, and delegation credentials must never appear in contract artifacts, tests, or logs
