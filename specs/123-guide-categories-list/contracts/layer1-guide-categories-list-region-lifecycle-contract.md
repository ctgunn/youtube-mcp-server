# Contract: YT-123 Layer 1 `guideCategories.list` Region and Lifecycle Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `guideCategories.list` region lookup rules, deprecated-or-unavailable lifecycle guidance, empty-result handling, and invalid-request boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- visible API-key access behavior for the supported region lookup path
- explicit `part` plus `regionCode` guidance for the supported request shape
- a maintainer-facing lifecycle note explaining that the endpoint is deprecated or may be unavailable in current platform behavior
- review surfaces that keep `authMode`, `quotaCost`, `lifecycleState`, endpoint identity, and request-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a region lookup is supported
- empty responses as the only signal that the endpoint is deprecated or unavailable
- silent fallback behavior when unsupported request fields are supplied

## Region Lookup Rules

Required behavior:

- the supported lookup path for this slice uses one `regionCode` value per request
- every supported request must include non-empty `part` and `regionCode` values
- the wrapper must reject undocumented top-level request fields instead of passing them through silently
- maintainers must be able to determine from feature artifacts that the lookup remains region-scoped and deterministic

## Lifecycle Guidance

The contract must explain that:

- `guideCategories.list` carries a deprecated lifecycle note for this slice
- current platform behavior may make the endpoint unavailable or unsuitable for general reuse even when a request is otherwise well formed
- higher-layer callers should treat lifecycle-aware unavailable outcomes differently from malformed requests
- the lifecycle caveat must remain visible in metadata, contracts, and higher-layer review surfaces

For supported review surfaces, the contract must explain:

- why the endpoint is not treated as a routine always-available lookup surface
- how maintainers should interpret successful empty results compared with lifecycle-aware unavailable outcomes
- that later layers may need to avoid or replace this endpoint when the caveat becomes material to user-facing behavior

## Invalid-Request Handling

The contract must treat request validation as deterministic.

Required behavior:

- callers may not omit `part` or `regionCode`; missing `part` or `regionCode` must remain explicit invalid-request conditions
- callers may not supply unsupported request modifiers or undocumented fields and still expect supported wrapper behavior
- contract and test artifacts must keep these boundaries reviewable without reading implementation code

## Lifecycle-Aware Outcome Guidance

The contract must explain that:

- some validly shaped requests can still fail because the endpoint is deprecated, unavailable, or otherwise not recommended for general use in the current platform context
- higher-layer callers should treat those outcomes as lifecycle-aware unavailable behavior rather than local contract ambiguity
- successful retrievals with zero items remain separate from lifecycle-aware failures, normalized upstream rejections, and local validation failures

## Validation Expectations

Representative proof for YT-123 must show:

- maintainers can identify deprecated lifecycle behavior in one review pass
- supported region lookup rules are documented clearly enough for later legacy-category and localization features
- unsupported request shapes are protected by regression coverage
- lifecycle-aware unavailable outcomes remain distinct from malformed requests and empty-result success cases
- guide-category retrieval handling remains on the success path for valid requests that return zero or more items

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/`
- unit coverage for request validation and lifecycle metadata exposure
- transport coverage showing `GET` request construction for `guideCategories.list`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
