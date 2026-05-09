# Contract: YT-145 Layer 1 `videoAbuseReportReasons.list` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `videoAbuseReportReasons.list` so maintainers can review localized abuse-reason lookup behavior, API-key access expectations, quota visibility, and normalized result boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `videoAbuseReportReasons.list`
- Maintainer-visible endpoint identity and quota cost (`1`)
- Deterministic request boundary for supported `part` plus `hl` lookups
- API-key behavior for localized abuse-reason retrieval
- Reviewable localization guidance for downstream reuse
- Normalized success and failure boundaries suitable for later Layer 2 and Layer 3 video-reporting work

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `videoAbuseReportReasons.list` wrapper must expose:

- `resource_name` as `videoAbuseReportReasons`
- `operation_name` as `list`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as API-key access
- `quota_cost` as `1`
- maintainer-facing notes describing localization usage, request boundaries, and empty-result interpretation

The wrapper must keep request boundaries, localization guidance, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` and `hl` are required for supported localized lookup requests
- that the wrapper supports one localized view per request
- that undocumented modifiers or extra top-level fields are outside the wrapper boundary
- that unsupported fields are rejected or clearly flagged before execution
- that the request contract remains deterministic and is not silently rewritten to another lookup profile

## Response Contract Expectations

The wrapper must preserve the shared executor success or failure split:

- valid requests return normalized success, including empty item lists when no abuse-report reasons match the selected localization view
- request-shape failures are explicit normalized `invalid_request` outcomes
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation, quota visibility, and display-language context for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `videoAbuseReportReasons.list` identity, quota cost, and API-key access in one review pass
- determine the supported `part` plus `hl` request boundary without reading implementation code
- understand the localization usage and empty-result interpretation for downstream reuse
- determine that public Layer 2 exposure is outside this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `GET` request construction and normalized abuse-reason result handling

## Invariants

- YT-145 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
