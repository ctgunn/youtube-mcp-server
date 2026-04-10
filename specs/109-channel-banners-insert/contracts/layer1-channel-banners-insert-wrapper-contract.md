# Contract: YT-109 Layer 1 `channelBanners.insert` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `channelBanners.insert` endpoint so maintainers can review endpoint identity, quota behavior, upload expectations, response-URL behavior, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `channelBanners.insert`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and banner-upload boundary rules
- Response-URL behavior that later `channels.update` work can rely on
- Review surfaces used by later channel-branding planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `channelBanners.insert` wrapper must expose:

- `resource_name` as `channelBanners`
- `operation_name` as `insert`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing image constraints, response-URL behavior, and optional delegation context

Maintainer-facing review surfaces should also keep the minimum upload boundary visible, including the requirement that valid requests include one `media` upload payload and may include only the documented `onBehalfOfContentOwner` delegation input.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that this endpoint is a media-upload path rather than a JSON-body mutation
- which request field carries the required banner image payload
- whether `onBehalfOfContentOwner` may accompany an otherwise supported authorized request
- which image constraints are relevant for supported uploads
- which field combinations are unsupported for this internal wrapper

The request contract must remain deterministic. A valid request must include one media upload payload, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that upload banner artwork are successful
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must make it possible for later layers to recover the returned banner URL for follow-on channel-branding work.
The contract must also make it possible for later layers to distinguish an access-related banner-upload failure from an `invalid_request` upload failure or a `target_channel` failure.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `channelBanners.insert` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported boundary for one banner image upload plus optional delegation context
- understand the documented image constraints without reading raw upstream docs
- understand that a successful upload returns a banner URL used by later `channels.update` work

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-upload artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, upload handling, and authorized-request behavior
- consumer-facing checks showing higher layers can summarize `channelBanners.insert` contract details without losing quota, auth, upload, or response-URL visibility

## Invariants

- YT-109 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, content-owner credentials, and raw image payloads must never appear in contract artifacts, tests, or logs
