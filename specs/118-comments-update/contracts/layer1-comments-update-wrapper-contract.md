# Contract: YT-118 Layer 1 `comments.update` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `comments.update` so maintainers can review writable-field behavior, OAuth-required expectations, quota visibility, and normalized update boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `comments.update`
- Maintainer-visible endpoint identity and quota cost (`50`)
- Deterministic write boundary for supported `part` plus writable `body` requests
- OAuth-required behavior for comment edits
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `comments.update` wrapper must expose:

- `resource_name` as `comments`
- `operation_name` as `update`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing writable-field rules, authorization expectations, any optional delegation inputs surfaced for this slice, and unsupported update-shape boundaries

The wrapper must keep writable boundaries, authorization expectations, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` and `body` are required for supported update requests
- that the update body must identify the comment being revised
- that the update body must include writable comment content suitable for one deterministic edit path
- which optional delegation inputs are accepted for eligible authorized requests if any are supported for this slice
- that unsupported fields, immutable-field edits, or incomplete update bodies are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another comment-update profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized updated comment result
- invalid update-body or unsupported-update requests are explicit normalized `invalid_request` or unsupported-update outcomes
- auth mismatches are explicit normalized `auth` outcomes
- immutable-field violations are explicit and distinguishable from auth and upstream failures
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `comments.update` identity, quota cost, and OAuth-required behavior in one review pass
- determine supported writable-field rules without reading implementation code
- determine whether optional delegation inputs are supported for eligible authorized requests
- understand how immutable-field violations differ from auth failures and normalized upstream update failures
- identify that unsupported comment field edits are outside the supported wrapper boundary

Validation must include:

- unit tests for wrapper metadata and update-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `PUT` request construction and normalized update handling

## Invariants

- YT-118 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
