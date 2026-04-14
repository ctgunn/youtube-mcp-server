# Contract: YT-114 Layer 1 `channelSections.update` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `channelSections.update` so maintainers can review writable update behavior, OAuth-required expectations, quota visibility, delegation guidance, and normalized update boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `channelSections.update`
- Maintainer-visible endpoint identity and quota cost (`50`)
- Deterministic write boundary for supported `part` plus channel-section `body` requests
- OAuth-required behavior for channel-section updates
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `channelSections.update` wrapper must expose:

- `resource_name` as `channelSections`
- `operation_name` as `update`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing writable field limits, section-type alignment rules, title behavior, optional delegation inputs, and supported update-body rules

The wrapper must keep writable boundaries, authorization expectations, delegation guidance, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` and `body` are required for supported update requests
- that the update body must identify the existing channel section being modified through `body.id`
- which writable body areas are supported for this slice
- which section types require playlist IDs, which require channel IDs, and which do not accept either list
- when `snippet.title` is required, optional, or ignored for the selected section type
- that unsupported fields, unsupported type-and-content combinations, duplicate references, or incomplete update shapes are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another section-type profile or have unsupported fields ignored implicitly.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized updated channel-section result
- invalid update-body or unsupported-content requests are explicit normalized `invalid_request` or unsupported-update outcomes
- auth mismatches are explicit normalized `auth` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `channelSections.update` identity, quota cost, and OAuth-required behavior in one review pass
- determine supported writable field boundaries without reading implementation code
- determine when custom titles are required and when they are ignored
- determine which optional delegation inputs are supported for partner-authorized requests
- understand how invalid update shapes differ from auth failures and normalized upstream update failures

Validation must include:

- unit tests for wrapper metadata and update-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `PUT` request construction and normalized update handling

## Invariants

- YT-114 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
