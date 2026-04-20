# Contract: YT-122 Layer 1 `commentThreads.insert` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `commentThreads.insert` so maintainers can review top-level thread-creation behavior, OAuth-required expectations, quota visibility, and normalized create boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `commentThreads.insert`
- Maintainer-visible endpoint identity and quota cost (`50`)
- Deterministic write boundary for supported `part` plus video-targeted top-level thread `body` requests
- OAuth-required behavior for top-level comment-thread creation
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 reuse

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `commentThreads.insert` wrapper must expose:

- `resource_name` as `commentThreads`
- `operation_name` as `insert`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as OAuth-required
- `quota_cost` as `50`
- maintainer-facing notes describing top-level-thread rules, authorization expectations, optional delegation inputs, target-eligibility handling, and unsupported create-shape boundaries

The wrapper must keep top-level create boundaries, authorization expectations, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` and `body` are required for supported create requests
- that the create body must identify one supported video target
- that the create body must include top-level comment content suitable for publishing a new thread
- that the supported shape uses `body.snippet.videoId` plus `body.snippet.topLevelComment.snippet.textOriginal`
- which optional delegation inputs are accepted for eligible authorized requests
- that unsupported fields, unsupported reply-style shapes, or incomplete top-level bodies are rejected or clearly flagged before execution

The request contract must remain deterministic. A request must not be silently rewritten to another comment-thread create profile.

## Response Contract Expectations

The wrapper must preserve the shared executor success/failure split:

- valid authorized requests return a normalized created comment-thread result
- invalid top-level bodies or unsupported create shapes are explicit normalized `invalid_request` or unsupported-create outcomes
- auth mismatches are explicit normalized `auth` outcomes
- target-ineligible requests are explicit normalized target-eligibility outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation and quota visibility for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `commentThreads.insert` identity, quota cost, and OAuth-required behavior in one review pass
- determine supported top-level create rules without reading implementation code
- determine which optional delegation inputs are supported for eligible authorized requests
- understand how invalid create shapes differ from auth failures, target-eligibility failures, and normalized upstream create failures
- identify that reply-style or mixed comment creation is outside the supported wrapper boundary

Validation must include:

- unit tests for wrapper metadata and create-shape validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `POST` request construction and normalized create handling

## Invariants

- YT-122 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
