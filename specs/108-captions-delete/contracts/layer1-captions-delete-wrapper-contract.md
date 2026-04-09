# Contract: YT-108 Layer 1 `captions.delete` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `captions.delete` endpoint so maintainers can review endpoint identity, quota behavior, ownership-sensitive delete expectations, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `captions.delete`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and delete-boundary rules
- Review surfaces used by later caption-management planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `captions.delete` wrapper must expose:

- `resource_name` as `captions`
- `operation_name` as `delete`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing ownership expectations and optional delegation context

Maintainer-facing review surfaces should also keep the minimum delete boundary visible, including the requirement that valid requests identify one caption track and may include only the documented delegated-ownership input.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request field carries the required caption track identifier
- whether `onBehalfOfContentOwner` may accompany an otherwise supported authorized request
- which field combinations are unsupported for this internal wrapper
- that bulk-delete, selector-style, or body-driven request modes are not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include one caption track identifier, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that delete a caption track are successful
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must make it possible for later layers to distinguish an access-related delete failure from a nonexistent caption-track delete failure.
The contract must also make successful deletion reviewable through a normalized internal result even when the upstream delete response body is empty.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `captions.delete` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary for one caption-track identifier plus optional delegation context
- understand ownership-sensitive delete behavior without reading raw upstream docs
- understand the normalized delete outcome without inspecting raw transport behavior

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `captions.delete` contract details without losing quota or auth visibility

## Invariants

- YT-108 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, caption payloads, and delegation credentials must never appear in contract artifacts, tests, or logs
