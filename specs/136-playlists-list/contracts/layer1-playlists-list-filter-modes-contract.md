# Contract: YT-136 Layer 1 `playlists.list` Filter Modes Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `playlists.list` selector modes, selector-aware auth expectations, filter-specific paging behavior, unsupported modifiers, and success-versus-failure boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `playlists.list` uses conditional auth for this slice
- `channelId` and `id` remain public API-key selector paths
- `mine` remains an owner-scoped OAuth-backed selector path
- missing or incompatible auth access must fail distinctly from malformed playlist requests
- auth expectations must remain visible in maintainer-facing notes, summaries, and tests

The contract must let maintainers tell, before implementation review, which playlist retrieval modes are public and which depend on owner-scoped access.

## Supported Filter-Mode Boundary

The filter-modes contract must make these retrieval expectations reviewable:

- the request must include exactly one supported selector from `channelId`, `id`, or `mine`
- `channelId` supports optional `pageToken` and `maxResults` because channel-scoped retrieval may span multiple results
- `mine` supports optional `pageToken` and `maxResults` because owner-scoped retrieval may span multiple results
- `id` does not support paging modifiers in this slice because direct playlist lookup remains deterministic without paging
- unsupported top-level inputs must fail clearly rather than being ignored silently
- the feature does not broaden scope into public MCP tooling, playlist write operations, or generalized playlist management

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- auth failures caused by missing or incompatible access for the selected filter mode
- local validation failures caused by missing selectors, conflicting selectors, or unsupported paging or modifier combinations
- successful empty playlist results caused by valid requests with no returned records
- normalized upstream playlist failures that survive local validation

The contract must make it clear that unsupported filter combinations are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `playlists.list` uses conditional auth with both public and owner-scoped paths
- that `part` plus exactly one selector define the required request boundary
- that `pageToken` and `maxResults` are supported only for the documented collection-style selector modes
- that malformed requests fail differently from access problems
- that valid empty results remain distinct from validation and access failures

Validation must include:

- unit coverage for auth, selector, and paging validation boundaries
- contract coverage proving review surfaces expose quota, auth, selector, and paging guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `GET` request construction for `playlists.list`

## Invariants

- YT-136 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata, executor, and higher-layer summary abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
