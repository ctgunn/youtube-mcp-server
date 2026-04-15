# Contract: YT-117 Layer 1 `comments.insert` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `comments.insert` so maintainers can review reply-creation behavior, OAuth-required expectations, quota visibility, and normalized create boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `comments.insert`
- Maintainer-visible endpoint identity and quota cost (`50`)
- Deterministic write boundary for supported `part` plus reply `body` requests
- OAuth-required behavior for comment reply creation
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `comments.insert` wrapper must expose:

- `resource_name` as `comments`
- `operation_name` as `insert`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing reply-body rules, authorization expectations, optional delegation inputs, and unsupported create-shape boundaries

The wrapper must keep reply boundaries, authorization expectations, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` and `body` are required for supported create requests
- that the create body must identify the parent comment being answered
- that the create body must include reply content suitable for publishing a reply
- which optional delegation inputs are accepted for eligible authorized requests
- that unsupported fields, unsupported create shapes, or incomplete reply bodies are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another comment-create profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized created comment result
- invalid reply-body or unsupported-create requests are explicit normalized `invalid_request` or unsupported-create outcomes
- auth mismatches are explicit normalized `auth` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `comments.insert` identity, quota cost, and OAuth-required behavior in one review pass
- determine supported reply-create rules without reading implementation code
- determine which optional delegation inputs are supported for eligible authorized requests
- understand how invalid create shapes differ from auth failures and normalized upstream create failures
- identify that unsupported top-level comment creation is outside the supported wrapper boundary

Validation must include:

- unit tests for wrapper metadata and create-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `POST` request construction and normalized create handling

## Invariants

- YT-117 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
