# Contract: YT-117 Layer 1 `comments.insert` Auth and Write Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `comments.insert` authorization requirements, reply-create rules, delegation guidance, and invalid-create boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible reply-create guidance for the supported write path
- clear rejection of unsupported top-level or mixed comment-create shapes
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and create-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a comment-create path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported create shapes are supplied

## Authorization Rules

Required behavior:

- `comments.insert` requires authorized comment-write access
- auth mismatch failures must remain explicit rather than blending into invalid create-shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- optional write-context or delegation guidance must remain visible for eligible authorized requests
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Reply-Create Rules

The wrapper contract for this slice must document:

- that the supported create boundary is reply creation
- that the request body must identify the parent comment being answered
- that the request body must include non-empty reply content
- that unsupported top-level comment-create shapes fall outside the wrapper boundary
- that the supported reply path is intended for direct later Layer 2 and Layer 3 reuse

For supported create paths, the contract must explain:

- which body fields activate the reply-create boundary
- what reply content is expected
- what authorization behavior is required before the create may proceed
- whether optional delegation inputs are preserved in successful normalized results

## Invalid-Create Handling

The contract must treat create-shape validation as deterministic.

Required behavior:

- callers may not omit `part`, `body`, the parent-comment reference, or reply content and still expect supported wrapper behavior
- callers may not supply unsupported create fields or conflicting create fields and still expect supported wrapper behavior
- callers may not rely on top-level comment creation through this slice
- contract and test artifacts must keep these boundaries reviewable

## Upstream Boundary Guidance

The contract must explain that:

- some create requests can fail because the referenced parent comment is missing, deleted, closed to replies, or otherwise unavailable
- higher-layer callers should treat those outcomes as normalized upstream create failures rather than local contract ambiguity
- successful created-comment handling remains separate from upstream rejections and local validation failures

## Validation Expectations

Representative proof for YT-117 must show:

- maintainers can identify OAuth-required behavior in one review pass
- reply-create rules are documented clearly enough for future comment features
- unsupported create shapes are protected by regression coverage
- created-comment handling remains on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/117-comments-insert/contracts/`
- unit coverage for create-shape validation and auth enforcement
- transport coverage showing `POST` request construction for `comments.insert`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
