# Contract: YT-132 Layer 1 `playlistItems.list` Selector Modes Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `playlistItems.list` selector modes, selector-specific paging behavior, API-key access expectations, unsupported modifiers, and success-versus-failure boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `playlistItems.list` uses API-key access for the supported selector set in this slice
- supported selector modes do not create an OAuth-required retrieval path in this feature
- incompatible auth usage must fail distinctly from malformed playlist-item requests
- API-key expectations must remain visible in maintainer-facing notes and tests

The contract must let maintainers tell, before implementation review, that the supported playlist-item retrieval paths are public API-key paths and not mixed-auth behavior in this slice.

## Supported Selector-Mode Boundary

The selector-modes contract must make these retrieval expectations reviewable:

- the request must include exactly one supported selector from `playlistId` or `id`
- `playlistId` supports optional `pageToken` and `maxResults` because playlist-scoped retrieval may span multiple results
- `id` does not support paging modifiers in this slice because direct playlist-item lookup remains deterministic without paging
- unsupported top-level inputs must fail clearly rather than being ignored silently
- the feature does not broaden scope into public MCP tooling, playlist-item write operations, or generalized playlist-item management

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- access failures caused by incompatible auth usage
- local validation failures caused by missing selectors, conflicting selectors, or unsupported paging or modifier combinations
- successful empty playlist-item results caused by valid requests with no returned records
- normalized upstream playlist-item failures that survive local validation

The contract must make it clear that unsupported selector combinations are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `playlistItems.list` uses API-key access for the supported selector set
- that `part` plus exactly one selector define the required request boundary
- that `pageToken` and `maxResults` are supported only for the documented selector mode
- that malformed requests fail differently from access problems
- that valid empty results remain distinct from validation and access failures

Validation must include:

- unit coverage for auth, selector, and paging validation boundaries
- contract coverage proving review surfaces expose quota, auth, selector, and paging guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `GET` request construction for `playlistItems.list`

## Invariants

- YT-132 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata, executor, and higher-layer summary abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
