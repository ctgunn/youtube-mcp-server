# Contract: YT-152 Layer 1 `videos.reportAbuse` Wrapper Contract

## Purpose

Define the internal wrapper contract that the repository will use for the YouTube Data API `videos.reportAbuse` endpoint so maintainers can review endpoint identity, quota behavior, abuse-report request scope, successful acknowledgement semantics, and downstream reuse expectations before implementation details are inspected.

The representative implementation for this contract will remain under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `videos.reportAbuse`
- Maintainer-visible endpoint identity and quota cost
- Supported request-body and acknowledgement boundary rules
- Review surfaces used by later abuse-reporting planning

This contract does not define a public MCP tool, hosted-route behavior, MCP transport changes, abuse-reason discovery behavior, or delegated content-owner reporting behavior.

## Required Wrapper Metadata

The `videos.reportAbuse` wrapper must expose:

- `resource_name` as `videos`
- `operation_name` as `reportAbuse`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode`
- `quota_cost`
- maintainer-facing notes describing required body fields, supported optional body fields, unsupported query modifiers, successful acknowledgement behavior, and failure-boundary expectations

Maintainer-facing review surfaces should also keep the minimum report boundary visible, including the requirement that valid requests include a `body` object with `videoId` and `reasonId`.

The wrapper must also expose a maintainer-visible quota reference with the official quota cost of `50` in a reStructuredText docstring, signature-adjacent note, or equivalent wrapper-facing review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `body.videoId` identifies the video being reported
- that `body.reasonId` identifies the primary abuse-report reason
- that `body.secondaryReasonId`, `body.comments`, and `body.language` are the supported optional body fields for this slice
- that partner-only delegated content-owner query behavior remains outside the guaranteed request boundary for this slice
- which broader, misspelled, or undocumented request shapes are outside the promised contract
- that unsupported body fields or undocumented top-level fields are not part of the promised Layer 1 contract

The request contract must remain deterministic. A valid request must include the required body object and required body fields, and unsupported combinations may not be silently rewritten into another request mode.

## Response Contract Expectations

The wrapper must preserve the current shared executor success and failure split:

- valid requests that are accepted by the upstream service are successful mutation acknowledgement outcomes
- successful no-content upstream responses are normalized into a reviewable acknowledgement instead of an empty or ambiguous result
- invalid request shapes are rejected before execution
- normalized upstream failures remain failure outcomes

The contract must also make it possible for later layers to distinguish an access-related report failure from an `invalid_request` failure, an invalid abuse-reason failure, a rate-limit failure, a video-not-found failure, an upstream unavailability failure, or a successful acknowledgement.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify the wrapper as `videos.reportAbuse` in one review pass
- find the quota cost of `50` without leaving the repository artifacts
- understand that the endpoint requires authorized access
- understand the supported body fields for one report request
- understand that the wrapper remains internal to Layer 1 in this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for the feature-local wrapper and auth-payload artifacts
- integration checks showing the wrapper remains compatible with the existing shared executor flow
- transport checks showing request construction preserves endpoint identity, body handling, OAuth access, and no-content acknowledgement behavior
- consumer-facing checks showing higher layers can summarize `videos.reportAbuse` contract details without losing quota, auth, payload, or acknowledgement visibility

## Invariants

- YT-152 extends the existing YT-101 and YT-102 Layer 1 foundation rather than replacing it
- No public MCP contract is introduced by this feature
- New or changed Python functions involved in the wrapper must include reStructuredText docstrings
- Secrets, OAuth tokens, and report submitter identity must never appear in contract artifacts, tests, logs, or normalized summaries
