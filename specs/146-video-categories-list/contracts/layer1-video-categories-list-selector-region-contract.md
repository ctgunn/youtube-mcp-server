# Contract: YT-146 Layer 1 `videoCategories.list` Selector and Region Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `videoCategories.list` selector rules, region-specific behavior, optional display-language guidance, empty-result handling, and invalid-request boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- visible API-key access behavior for the supported category lookup paths
- explicit `part` plus selector guidance for direct category-id lookup and region-scoped category browsing
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, selector boundaries, and region notes visible together
- optional `hl` guidance being treated as a display-language hint rather than a required selector

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether `id` or `regionCode` is supported
- simultaneous `id` and `regionCode` use being treated as a supported path
- silent fallback behavior when unsupported request fields are supplied

## Selector Rules

Required behavior:

- the supported lookup path for this slice uses exactly one selector from `id` or `regionCode`
- every supported request must include non-empty `part` and one non-empty selector value
- the wrapper must reject undocumented top-level request fields instead of passing them through silently
- maintainers must be able to determine from feature artifacts that selector choice remains deterministic

## Region and Display-Language Guidance

The contract must explain that:

- `regionCode` is the region-scoped browsing selector for this endpoint
- `id` is the direct category lookup selector for this endpoint
- optional `hl` may be supplied as a display-language hint without changing which selector drives the lookup
- maintainers must be able to tell how region browsing differs from category-id lookup without reading implementation code

For supported review surfaces, the contract must explain:

- when downstream work should prefer `regionCode` to browse categories available in one regional context
- when downstream work should prefer `id` to inspect one known category directly
- how to interpret valid requests that include `hl` and still return zero categories

## Invalid-Request Handling

The contract must treat request validation as deterministic.

Required behavior:

- callers may not omit `part`
- callers may not omit both `id` and `regionCode`
- callers may not supply both `id` and `regionCode` in the same supported request
- callers may not supply unsupported request modifiers or undocumented fields and still expect supported wrapper behavior
- contract and test artifacts must keep these boundaries reviewable without reading implementation code

## Outcome Guidance

The contract must explain that:

- successful empty results remain successful retrieval outcomes
- invalid requests remain separate from successful retrievals with zero or more returned categories
- optional `hl` presence does not change the success-versus-invalid boundary by itself
- higher-layer callers should preserve selector context when interpreting results

## Validation Expectations

Representative proof for YT-146 must show:

- maintainers can identify selector rules and region behavior in one review pass
- supported request rules are documented clearly enough for later category-aware video features
- unsupported request shapes are protected by regression coverage
- successful empty results remain distinct from malformed requests
- category retrieval handling remains on the success path for valid requests that return zero or more items

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/146-video-categories-list/contracts/`
- unit coverage for selector validation and metadata exposure
- transport coverage showing `GET` request construction for `videoCategories.list`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
