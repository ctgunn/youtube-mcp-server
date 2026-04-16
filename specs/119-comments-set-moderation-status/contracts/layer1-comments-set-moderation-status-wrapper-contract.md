# Contract: YT-119 Layer 1 `comments.setModerationStatus` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `comments.setModerationStatus` so maintainers can review moderation-state behavior, OAuth-required expectations, quota visibility, and normalized moderation boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `comments.setModerationStatus`
- Maintainer-visible endpoint identity and quota cost (`50`)
- Deterministic moderation boundary for supported query-only comment identifier plus moderation-status requests
- OAuth-required behavior for comment moderation changes
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `comments.setModerationStatus` wrapper must expose:

- `resource_name` as `comments`
- `operation_name` as `setModerationStatus`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing supported moderation states, optional moderation-flag behavior, authorization expectations, any optional delegation inputs surfaced for this slice, and unsupported moderation-shape boundaries

The wrapper must keep moderation boundaries, authorization expectations, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that comment identifiers and one moderation status are required for supported moderation requests
- that the comment identifier field may carry one or more target comment IDs for one moderation request
- that the selected moderation status must be one of the supported moderation outcomes for this slice
- that the supported request remains query-only and does not require a request body
- that `banAuthor` is the representative optional moderation flag and is only valid with the supported rejection-style moderation path
- which optional delegation inputs are accepted for eligible authorized requests if any are supported for this slice
- that unsupported fields, incompatible moderation-flag combinations, duplicate targets, or incomplete moderation requests are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another moderation profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized moderation acknowledgment result even when the upstream moderation success path returns no content body
- invalid moderation requests are explicit normalized `invalid_request` outcomes
- auth mismatches are explicit normalized `auth` outcomes
- unsupported moderation-transition or moderation-flag combinations are explicit and distinguishable from auth and upstream failures
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `comments.setModerationStatus` identity, quota cost, and OAuth-required behavior in one review pass
- determine supported moderation states and optional moderation-flag boundaries without reading implementation code
- determine whether optional delegation inputs are supported for eligible authorized requests
- understand how unsupported moderation combinations differ from auth failures and normalized upstream moderation failures
- identify that unsupported moderation states or flag combinations are outside the supported wrapper boundary

Validation must include:

- unit tests for wrapper metadata and moderation-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `POST` request construction and normalized moderation handling

## Invariants

- YT-119 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
