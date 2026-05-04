# Contract: YT-140 Layer 1 `search.list` Auth and Refinement Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `search.list` authorization requirements, search-type rules, pagination behavior, date filtering, language and region refinements, invalid request-shape boundaries, and normalized search outcomes when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- public API-key search behavior being explicit in maintainer-facing wrapper notes and review surfaces
- restricted filter paths being explicit in maintainer-facing wrapper notes and review surfaces
- visible search-type, pagination, date, language, and region guidance for the supported request boundary
- clear rejection of malformed inputs or incompatible refinement combinations
- review surfaces that keep `authMode`, quota cost of `100`, the quota caveat, endpoint identity, and refinement notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a search path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported search refinements are supplied

## Authorization Rules

Required behavior:

- baseline public search requests remain available with API-key access
- restricted filters such as `forContentOwner`, `forDeveloper`, or `forMine` require stronger authorization and must remain explicit in review artifacts
- restricted-auth failures must remain explicit rather than blending into invalid request-shape failures
- maintainers must be able to determine from feature artifacts which search paths are public and which move into the restricted-auth path
- contract and review artifacts must not expose secrets, API keys, OAuth tokens, or raw credential material

## Search Refinement Rules

The wrapper contract for this slice must document:

- that the supported baseline request includes `part` and `q`
- that `type` is the primary search-type refinement
- that `pageToken` and `maxResults` preserve upstream-style pagination semantics
- that `publishedAfter` and `publishedBefore` provide the supported date-filter pair
- that `regionCode` and `relevanceLanguage` provide the supported language and region scoping pair
- that video-specific refinements remain tied to compatible search-type behavior
- that unsupported extra fields or incompatible refinement combinations fall outside the wrapper boundary

For supported search paths, the contract must explain:

- which fields remain optional but reviewable
- when a search request stays on the public path
- when a search request moves into the restricted-auth path
- what empty-result behavior is expected to look like
- what result context remains available for downstream interpretation

## Invalid-Search Handling

The contract must treat search-shape validation as deterministic.

Required behavior:

- callers may not omit `part` or `q` and still expect supported wrapper behavior
- callers may not supply undocumented top-level fields and still expect supported wrapper behavior
- callers may not rely on incompatible search-type or video-filter combinations and still expect supported wrapper behavior
- callers may not treat a restricted-auth requirement as if it were a silent public fallback
- contract and test artifacts must keep these boundaries reviewable
- invalid request-shape outcomes must remain reviewable as `invalid_request`

## Upstream Boundary Guidance

The contract must explain that:

- some valid search requests can return zero results and still be successful
- some valid search requests can fail because the selected restricted filters require stronger authorization than the caller supplied
- some valid search requests can still fail because the upstream search execution is rejected or unavailable
- malformed upstream search requests that reach execution and receive a `400`-style rejection must remain distinguishable as `invalid_request`
- restricted upstream denials that reach execution and receive a `401` or `403` response must remain distinguishable as auth failures rather than local validation failures
- transient `5xx` search failures must remain distinguishable as upstream-service or retryable failures rather than invalid request-shape outcomes
- higher-layer callers should treat those outcomes as empty-result success, restricted-auth failure, or normalized upstream search failure rather than local contract ambiguity
- successful populated results remain separate from empty-result success, invalid-request outcomes, and normalized upstream failures

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `search.list` carries a quota cost of `100`
- `search.list` includes a visible quota caveat
- the endpoint is mixed or conditional rather than purely public-only or purely OAuth-only
- `part` and `q` are required
- search type, pagination, date filtering, and language or region refinements remain reviewable without reading raw upstream docs
- the wrapper remains internal to Layer 1 in this slice

## Validation Expectations

Representative proof for YT-140 must show:

- maintainers can identify mixed or conditional-auth behavior in one review pass
- search refinement rules are documented clearly enough for future search-driven features
- malformed or incompatible search requests are protected by regression coverage
- empty-result handling remains on the success path for valid supported requests
- invalid request shape, restricted-auth failure, empty-result success, and upstream search failures remain distinct in review artifacts

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/140-search-list/contracts/`
- unit coverage for search-shape validation and auth enforcement
- transport coverage showing `GET` request construction for `search.list`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
