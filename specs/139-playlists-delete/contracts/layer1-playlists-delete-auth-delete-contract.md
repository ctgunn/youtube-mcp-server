# Contract: YT-139 Layer 1 `playlists.delete` Auth and Delete Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `playlists.delete` authorization requirements, delete-target rules, invalid request shape boundaries, and normalized delete outcomes when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-only behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible delete-target guidance for the supported playlist deletion path
- clear rejection of malformed identifiers or unsupported delete shapes
- review surfaces that keep `authMode`, quota cost of `50`, endpoint identity, and delete-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a delete path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported delete shapes are supplied

## Authorization Rules

Required behavior:

- `playlists.delete` requires authorized playlist delete access
- unauthorized access failures must remain explicit rather than blending into invalid request shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Delete-Target Rules

The wrapper contract for this slice must document:

- that the supported delete boundary is removal of one existing playlist
- that the request must include one target playlist identifier
- that the supported delete field is `id` for the one target playlist
- that the supported request does not require `part` or `body`
- that unsupported identifier shapes or extra delete fields fall outside the wrapper boundary
- that the supported delete path is intended for direct later Layer 2 and Layer 3 reuse

For supported delete paths, the contract must explain:

- which field activates the supported delete boundary
- what delete outcome is expected to be reviewable in the normalized result
- that successful normalized results preserve the deleted playlist identity and delete status without requiring a refreshed playlist resource
- what authorization behavior is required before the delete may proceed

## Invalid-Delete Handling

The contract must treat delete-shape validation as deterministic.

Required behavior:

- callers may not omit the target playlist identifier and still expect supported wrapper behavior
- callers may not supply unsupported delete fields or conflicting delete context and still expect supported wrapper behavior
- callers may not rely on bulk deletion through this slice
- contract and test artifacts must keep these boundaries reviewable
- invalid request shape outcomes must remain reviewable as `invalid_request`

## Upstream Boundary Guidance

The contract must explain that:

- some delete requests can fail because the targeted playlist is missing, already removed, unwritable, or otherwise unavailable for deletion
- some delete requests can fail because the authorized caller lacks permission to delete the targeted playlist
- higher-layer callers should treat those outcomes as target-state or normalized upstream delete failures rather than local contract ambiguity
- successful deletion acknowledgments remain separate from upstream delete failures, unavailable-target outcomes, and local validation failures

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `playlists.delete` is OAuth-only
- the endpoint carries a quota cost of `50`
- one playlist identifier is required
- the wrapper remains internal to Layer 1 in this slice
- successful delete outcomes and failure boundaries remain reviewable without reading raw upstream docs

## Validation Expectations

Representative proof for YT-139 must show:

- maintainers can identify OAuth-required behavior in one review pass
- delete-target rules are documented clearly enough for future playlist cleanup features
- malformed or unavailable delete targets are protected by regression coverage
- deletion-acknowledgment handling remains on the success path for valid authorized requests
- invalid request shape, `invalid_request`, unauthorized access, and upstream delete failures remain distinct in review artifacts

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/139-playlists-delete/contracts/`
- unit coverage for delete-shape validation and auth enforcement
- transport coverage showing `DELETE` request construction for `playlists.delete`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
