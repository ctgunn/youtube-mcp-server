# Contract: YT-136 Layer 1 `playlists.list` Wrapper Contract

## Purpose

Define the internal wrapper contract for YouTube Data API `playlists.list` so maintainers can review playlist retrieval behavior, selector-aware auth expectations, filter boundaries, paging visibility, quota visibility, and normalized result boundaries before implementation details are inspected.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Contract Scope

- Internal-only Layer 1 wrapper behavior for `playlists.list`
- Maintainer-visible endpoint identity and quota cost (`1`)
- Deterministic request boundary for supported `part` plus exactly one selector from `channelId`, `id`, or `mine`
- Filter-specific paging behavior through explicitly documented `pageToken` and `maxResults` rules
- Conditional auth behavior that keeps public and owner-scoped playlist retrieval reviewable
- Reviewable playlist lookup guidance for downstream reuse
- Normalized success, invalid-request, and access-failure boundaries suitable for later playlist and channel work

This contract does not define a public MCP tool, hosted route behavior, or MCP transport changes.

## Required Wrapper Metadata

The `playlists.list` wrapper must expose:

- `resource_name` as `playlists`
- `operation_name` as `list`
- `operation_key`
- `http_method`
- `path_shape`
- `request_shape`
- `auth_mode` as conditional auth
- `auth_condition_note` describing which selector paths require API-key access and which require OAuth-backed access
- `quota_cost` as `1`
- maintainer-facing notes describing required `part`, supported selector usage, paging boundaries, unsupported modifiers, and empty-result interpretation

The wrapper must keep request boundaries, filter guidance, auth expectations, and quota visibility in one review surface.

## Request Contract Expectations

The wrapper contract must make the supported request boundary clear enough that a maintainer can tell:

- that `part` is required for supported playlist lookup requests
- that exactly one selector from `channelId`, `id`, or `mine` is required per request
- that `pageToken` and `maxResults` are optional only when the selected filter mode supports paging
- that undocumented modifiers or extra top-level fields are outside the wrapper boundary
- that unsupported fields are rejected or clearly flagged before execution
- that this slice does not broaden scope into public MCP tooling or playlist write operations

## Response Contract Expectations

The wrapper must preserve the shared executor success or failure split:

- valid requests return normalized success, including empty item lists when no playlists match the selected lookup
- request-shape failures are explicit normalized `invalid_request` outcomes
- missing or incompatible auth access is surfaced as a distinct normalized access-related failure
- normalized upstream failures preserve category distinctions needed by downstream callers

The wrapper must preserve source operation, quota visibility, auth guidance, and selector context for higher-layer review surfaces.

## Review Validation Expectations

The feature must prove that maintainers can:

- identify `playlists.list` identity, quota cost, and conditional-auth behavior in one review pass
- determine the supported selector and paging boundary without reading implementation code
- understand which request modes are supported for downstream reuse
- determine that public Layer 2 exposure is outside this slice

Validation must include:

- unit tests for wrapper metadata and request validation rules
- contract tests for this feature-local contract and review surfaces
- integration tests showing compatibility with existing executor flow
- transport tests showing `GET` request construction and normalized playlist result handling

## Invariants

- YT-136 extends YT-101 and YT-102 foundations instead of replacing them
- No public MCP contract is introduced by this feature
- New or changed Python functions in scope include reStructuredText docstrings
- Secrets and credential material must not appear in contracts, tests, or logs
