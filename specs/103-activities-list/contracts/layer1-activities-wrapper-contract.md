# Contract: YT-103 Layer 1 `activities.list` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `activities.list` endpoint so maintainers can review endpoint identity, quota behavior, request scope, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `activities.list`
- Maintainer-visible endpoint identity and quota cost
- Supported request-shape and filter-boundary rules
- Review surfaces used by later Layer 2 and Layer 3 planning

This contract does not define a public MCP tool, hosted-route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `activities.list` wrapper must expose:

- `resource_name` as `activities`
- `operation_name` as `list`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- `auth_condition_note` describing when access is public versus authorized-user-only

Maintainer-facing review surfaces should also keep the supported selector boundary visible, including the exclusive selector set `channelId`, `mine`, and `home`.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `1` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- which request fields select public channel activity retrieval through `channelId`
- which request fields select authorized-user activity retrieval through `mine` or `home`
- which field combinations are unsupported for this internal wrapper
- that unsupported combinations are not part of the promised Layer 1 contract

The request contract must remain deterministic. Exactly one of `channelId`, `mine`, or `home` must be present for supported requests, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that return activity items are successful
- valid requests that return zero items are also successful
- normalized upstream failures remain failure outcomes

The contract must not reinterpret "no recent activity" as a wrapper error.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `activities.list` in one review pass
- find the quota cost of `1` without leaving the repository artifacts
- understand that the endpoint has filter-dependent auth behavior
- understand the supported boundary for public and authorized-user access without reading raw upstream docs

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth/filter artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow

## Invariants

- YT-103 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, and credential payloads must never appear in contract artifacts, tests, or logs
