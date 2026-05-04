# Contract: YT-141 Layer 1 `subscriptions.list` Filter Modes Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `subscriptions.list` selector modes, selector-aware OAuth expectations, paging and ordering behavior, unsupported combinations, and success-versus-failure boundaries when reusing the internal Layer 1 wrapper.

The representative implementation for this contract remains under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`.

## Authorization Expectations

- `subscriptions.list` uses mixed or conditional auth for this slice
- `channelId` and `id` remain public-compatible selector paths
- `mine`, `myRecentSubscribers`, and `mySubscribers` remain OAuth-backed selector paths
- missing or incompatible auth access must fail distinctly from malformed subscription requests
- auth expectations must remain visible in maintainer-facing notes, summaries, and tests

The contract must let maintainers tell, before implementation review, which subscription retrieval modes are public-compatible and which depend on owner-scoped or subscriber-management access.

## Supported Filter-Mode Boundary

The filter-modes contract must make these retrieval expectations reviewable:

- the request must include exactly one supported selector from `channelId`, `id`, `mine`, `myRecentSubscribers`, or `mySubscribers`
- `channelId`, `mine`, `myRecentSubscribers`, and `mySubscribers` support optional `pageToken` and `maxResults` when the selected path returns a collection in this slice
- `id` does not support paging modifiers in this slice because direct subscription lookup remains deterministic without continuation behavior
- `order` is reviewable only for supported collection-style selector modes and is outside the direct `id` lookup path
- unsupported top-level inputs must fail clearly rather than being ignored silently
- the feature does not broaden scope into public MCP tooling, subscription write operations, or generalized subscription management

## Failure Boundary Expectations

Higher layers must be able to distinguish:

- access-related failures caused by missing or incompatible authorization for the selected filter mode
- local validation failures caused by missing selectors, conflicting selectors, or unsupported paging or ordering combinations
- successful empty subscription results caused by valid requests with no returned records
- normalized upstream subscription failures that survive local validation

The contract must make it clear that unsupported filter combinations are enforced locally before a request is treated as supported wrapper usage.

## Review Validation Expectations

The feature must prove that maintainers can identify:

- that `subscriptions.list` uses mixed-auth behavior with both public-compatible and OAuth-backed paths
- that `part` plus exactly one selector define the required request boundary
- that `pageToken` and `maxResults` are supported only for the documented collection-style selector modes
- that malformed requests fail differently from access problems
- that valid empty results remain distinct from validation and access failures

Validation must include:

- unit coverage for auth, selector, paging, and ordering validation boundaries
- contract coverage proving review surfaces expose quota, auth, selector, and paging guidance
- integration coverage showing compatible behavior through the existing executor flow
- transport coverage showing `GET` request construction for `subscriptions.list`

## Invariants

- YT-141 remains internal-only Layer 1 work
- The feature preserves existing Layer 1 metadata, executor, and higher-layer summary abstractions
- Credential material must never appear in docs, tests, or logs
- New or changed Python functions in scope include reStructuredText docstrings
