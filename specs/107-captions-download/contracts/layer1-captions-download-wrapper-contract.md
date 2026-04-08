# Contract: YT-107 Layer 1 `captions.download` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `captions.download` endpoint so maintainers can review endpoint identity, quota behavior, permission-sensitive access, supported download-option scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `captions.download`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape, translation, and format-conversion rules
- Review surfaces used by later transcript and caption-delivery planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `captions.download` wrapper must expose:

- `resource_name` as `captions`
- `operation_name` as `download`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing permission expectations, supported `tfmt` and `tlang` inputs, and optional delegation context

Maintainer-facing review surfaces should also keep the minimum download boundary visible, including the requirement that valid requests identify one caption track and may include only the documented translation and format modifiers.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `200` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request field carries the required caption track identifier
- when `tfmt` is an optional format-conversion input
- when `tlang` is an optional translation input
- whether `onBehalfOfContentOwner` may accompany an otherwise supported authorized request
- which field combinations are unsupported for this internal wrapper

The request contract must remain deterministic. A valid request must include one caption track identifier, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that download caption content are successful
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must make it possible for later layers to distinguish an inaccessible caption track from a nonexistent caption track.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `captions.download` in one review pass
- find the quota cost of `200` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary for `tfmt` and `tlang`
- understand optional delegation guidance without reading raw upstream docs
- understand that some download failures may reflect permissions rather than caption absence

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and access-format artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `captions.download` contract details without losing quota or auth visibility

## Invariants

- YT-107 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, downloaded caption payloads, and delegation credentials must never appear in contract artifacts, tests, or logs
