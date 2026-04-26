# Contract: YT-128 Layer 1 `playlistImages.list` Filter Modes Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `playlistImages.list` selector modes, selector-specific paging behavior, OAuth requirements, unsupported modifiers, and success-versus-failure boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `playlistImages.list` requires OAuth-required access
- supported selector modes do not create a public API-key retrieval path in this slice
- missing or incompatible OAuth access must fail distinctly from malformed playlist-image requests
- OAuth expectations must remain visible in maintainer-facing notes and tests

The contract must let maintainers tell, before implementation review, that playlist-image retrieval is authorization-gated and not interchangeable with public list endpoints.

## Supported Filter-Mode Boundary

The filter-modes contract must make these retrieval expectations reviewable:

- the request must include exactly one supported selector from `playlistId` or `id`
- `playlistId` supports optional `pageToken` and `maxResults` because playlist-scoped retrieval may span multiple results
- `id` does not support paging modifiers in this slice because direct image lookup remains deterministic without paging
- unsupported top-level inputs must fail clearly rather than being ignored silently
- the feature does not broaden scope into public MCP tooling, playlist-image write operations, or generalized playlist-image management

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- auth failures caused by missing or incompatible OAuth access
- local validation failures caused by missing selectors, conflicting selectors, or unsupported paging/modifier combinations
- successful empty playlist-image results caused by valid authorized requests with no returned records
- normalized upstream playlist-image failures that survive local validation

The contract must make it clear that unsupported filter combinations are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `playlistImages.list` requires OAuth-required access
- that `part` plus exactly one selector define the required request boundary
- that `pageToken` and `maxResults` are supported only for the documented selector mode
- that malformed requests fail differently from access problems
- that valid authorized empty results remain distinct from validation and access failures

Validation must include:

- unit coverage for auth, selector, and paging validation boundaries
- contract coverage proving review surfaces expose quota, auth, selector, and paging guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `GET` request construction for `playlistImages.list`

## Invariants

- YT-128 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata, executor, and higher-layer summary abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
