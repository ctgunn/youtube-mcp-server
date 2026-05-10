# Contract: YT-147 Layer 1 `videos.list` Selector and Auth Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `videos.list` selector rules, mixed-auth behavior, collection-refinement boundaries, empty-result handling, and invalid-request boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- visible mixed-auth behavior for the supported video lookup paths
- explicit `part` plus selector guidance for direct video lookup, chart retrieval, and personal-rating retrieval
- review surfaces that keep `authMode`, `authConditionNote`, `quotaCost`, endpoint identity, selector boundaries, and refinement notes visible together
- collection-only and chart-only refinement rules being treated as deterministic request boundaries rather than implementation details

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether `id`, `chart`, or `myRating` is supported
- simultaneous selector use being treated as a supported path
- silent fallback behavior when unsupported request fields or unsupported selector-refinement combinations are supplied

## Selector Rules

Required behavior:

- the supported lookup path for this slice uses exactly one selector from `id`, `chart`, or `myRating`
- every supported request must include non-empty `part` and one non-empty selector value
- the wrapper must reject undocumented top-level request fields instead of passing them through silently
- maintainers must be able to determine from feature artifacts that selector choice remains deterministic

## Auth and Refinement Guidance

The contract must explain that:

- `id` is the direct video lookup selector for this endpoint
- `chart` is the chart-oriented collection selector for this endpoint
- `myRating` is the personal-rating selector for this endpoint
- `id` and `chart` follow the public-compatible access path for this slice
- `myRating` requires the OAuth-backed access path for this slice
- `pageToken` and `maxResults` are collection-style refinements rather than direct-lookup inputs
- `regionCode` and `videoCategoryId` are chart-oriented refinements for this slice

For supported review surfaces, the contract must explain:

- when downstream work should prefer `id` for exact known-video retrieval
- when downstream work should prefer `chart` to browse one chart-oriented collection
- when downstream work should prefer `myRating` for caller-specific retrieval
- how to interpret valid requests that include chart refinements or paging inputs and still return zero videos

## Invalid-Request Handling

The contract must treat request validation as deterministic.

Required behavior:

- callers may not omit `part`
- callers may not omit all supported selectors
- callers may not supply more than one selector in the same supported request
- callers may not supply chart-only refinements outside the chart selector path
- callers may not supply collection-only refinements outside the collection selectors supported by this slice
- callers may not supply unsupported request modifiers or undocumented fields and still expect supported wrapper behavior
- contract and test artifacts must keep these boundaries reviewable without reading implementation code

## Outcome Guidance

The contract must explain that:

- successful empty results remain successful retrieval outcomes
- invalid requests remain separate from successful retrievals with zero or more returned videos
- mixed-auth guidance does not change the success-versus-invalid boundary by itself
- higher-layer callers should preserve selector and auth-path context when interpreting results

## Validation Expectations

Representative proof for YT-147 must show:

- maintainers can identify selector rules and mixed-auth behavior in one review pass
- supported request rules are documented clearly enough for later direct-video and chart-aware features
- unsupported request shapes are protected by regression coverage
- successful empty results remain distinct from malformed requests
- video retrieval handling remains on the success path for valid requests that return zero or more items

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/147-videos-list/contracts/`
- unit coverage for selector validation, mixed-auth metadata exposure, and refinement boundaries
- transport coverage showing `GET` request construction for `videos.list`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
