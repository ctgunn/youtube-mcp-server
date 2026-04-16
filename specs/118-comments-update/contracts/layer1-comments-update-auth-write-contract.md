# Contract: YT-118 Layer 1 `comments.update` Auth and Write Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `comments.update` authorization requirements, writable-field rules, optional delegation guidance, and invalid-update boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible writable-field guidance for the supported edit path
- clear rejection of immutable-field or unsupported comment-field changes
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and writable-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a comment-edit path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported update shapes are supplied

## Authorization Rules

Required behavior:

- `comments.update` requires authorized comment-write access
- auth mismatch failures must remain explicit rather than blending into invalid update-shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- optional write-context or delegation guidance, if supported for this slice, must remain visible for eligible authorized requests
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Writable-Field Rules

The wrapper contract for this slice must document:

- that the supported update boundary is existing-comment revision
- that the request body must identify the comment being revised
- that the request body must include non-empty updated comment content
- that unsupported or read-only comment fields fall outside the wrapper boundary
- that the supported update path is intended for direct later Layer 2 and Layer 3 reuse

For supported update paths, the contract must explain:

- which body fields activate the supported writable boundary
- what updated content is expected
- what authorization behavior is required before the update may proceed
- whether optional delegation inputs are preserved in successful normalized results

## Invalid-Update Handling

The contract must treat update-shape validation as deterministic.

Required behavior:

- callers may not omit `part`, `body`, the target comment identifier, or updated comment content and still expect supported wrapper behavior
- callers may not supply unsupported update fields or conflicting update fields and still expect supported wrapper behavior
- callers may not rely on edits to read-only comment fields through this slice
- contract and test artifacts must keep these boundaries reviewable

## Upstream Boundary Guidance

The contract must explain that:

- some update requests can fail because the targeted comment is missing, deleted, locked, or otherwise unavailable for editing
- higher-layer callers should treat those outcomes as normalized upstream update failures rather than local contract ambiguity
- successful updated-comment handling remains separate from upstream rejections, immutable-field violations, and local validation failures

## Validation Expectations

Representative proof for YT-118 must show:

- maintainers can identify OAuth-required behavior in one review pass
- writable-field rules are documented clearly enough for future comment features
- immutable-field and unsupported-update shapes are protected by regression coverage
- updated-comment handling remains on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/118-comments-update/contracts/`
- unit coverage for update-shape validation and auth enforcement
- transport coverage showing `PUT` request construction for `comments.update`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
