# Contract: YT-111 Layer 1 `channels.update` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `channels.update` so maintainers can review writable-part behavior, OAuth-required expectations, quota visibility, and normalized update boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `channels.update`
- Maintainer-visible endpoint identity and quota cost (`50`)
- Deterministic write boundary for supported `part` plus writable `body` requests
- OAuth-required behavior for channel-management updates
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `channels.update` wrapper must expose:

- `resource_name` as `channels`
- `operation_name` as `update`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing writable-part limits and supported update-body rules

The wrapper must keep writable-part boundaries, authorization expectations, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` and `body` are required for supported update requests
- which writable channel parts are supported for this slice, including `brandingSettings` and `localizations`
- that the selected writable part must align with the fields present in the provided channel-update body
- which fields remain unsupported or read-only for this slice
- that unsupported fields, unsupported parts, or incomplete update shapes are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another writable-part profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized updated channel result
- invalid update-body or unsupported-write requests are explicit normalized `invalid_request` or unsupported-write outcomes
- auth mismatches are explicit normalized `auth` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `channels.update` identity, quota cost, and OAuth-required behavior in one review pass
- determine supported writable parts and part-to-body alignment rules without reading implementation code
- determine which update fields are unsupported or read-only for this slice
- understand how invalid write shapes differ from auth failures
- understand any channel-specific notes relevant to later channel-management reuse
- understand how `brandingSettings.image.bannerExternalUrl` can reuse banner-upload output in later channel-branding workflows

Validation must include:

- unit tests for wrapper metadata and write-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `PUT` request construction and normalized update handling

## Invariants

- YT-111 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
