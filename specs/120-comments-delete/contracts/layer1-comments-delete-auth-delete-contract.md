# Contract: YT-120 Layer 1 `comments.delete` Auth and Delete Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `comments.delete` authorization requirements, delete-target rules, optional delegation guidance, and invalid-delete boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible delete-target guidance for the supported deletion path
- clear rejection of malformed identifiers or unsupported delete shapes
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and delete-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a delete path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported delete shapes are supplied

## Authorization Rules

Required behavior:

- `comments.delete` requires authorized comment-delete access
- auth mismatch failures must remain explicit rather than blending into invalid delete-shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- optional delegated-owner guidance, if supported for this slice, must remain visible for eligible authorized requests
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Delete-Target Rules

The wrapper contract for this slice must document:

- that the supported delete boundary is removal of one existing comment
- that the request must include one target comment identifier
- that the supported delete field is `id` for the one target comment
- that the supported request remains query-only and does not require a delete body payload
- that unsupported identifier shapes or extra delete fields fall outside the wrapper boundary
- that the supported delete path is intended for direct later Layer 2 and Layer 3 reuse

For supported delete paths, the contract must explain:

- which field activates the supported delete boundary
- what delete outcome is expected to be reviewable in the normalized result
- that successful normalized results preserve the deleted comment identity and delete status without requiring a refreshed comment resource
- what authorization behavior is required before the delete may proceed
- whether optional delegated-owner inputs are preserved in successful normalized results

## Invalid-Delete Handling

The contract must treat delete-shape validation as deterministic.

Required behavior:

- callers may not omit the target comment identifier and still expect supported wrapper behavior
- callers may not supply unsupported delete fields or conflicting delete context and still expect supported wrapper behavior
- callers may not rely on bulk deletion through this slice
- contract and test artifacts must keep these boundaries reviewable

## Upstream Boundary Guidance

The contract must explain that:

- some delete requests can fail because the targeted comment is missing, already removed, locked, or otherwise unavailable for deletion
- some delete requests can fail because the authorized caller lacks permission to delete the targeted comment
- higher-layer callers should treat those outcomes as normalized upstream or target-state delete failures rather than local contract ambiguity
- successful deletion acknowledgments remain separate from upstream rejections, unavailable-target outcomes, and local validation failures

## Validation Expectations

Representative proof for YT-120 must show:

- maintainers can identify OAuth-required behavior in one review pass
- delete-target rules are documented clearly enough for future comment cleanup features
- malformed or unavailable delete targets are protected by regression coverage
- deletion-acknowledgment handling remains on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/contracts/`
- unit coverage for delete-shape validation and auth enforcement
- transport coverage showing `DELETE` request construction for `comments.delete`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
