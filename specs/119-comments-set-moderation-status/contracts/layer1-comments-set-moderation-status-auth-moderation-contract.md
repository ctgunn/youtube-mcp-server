# Contract: YT-119 Layer 1 `comments.setModerationStatus` Auth and Moderation Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `comments.setModerationStatus` authorization requirements, moderation-state rules, `banAuthor` restrictions, and invalid-moderation boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required owner-scoped moderation behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible moderation-state guidance for the supported moderation path
- clear rejection of unsupported moderation states or incompatible `banAuthor` combinations
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and moderation-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a moderation path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported moderation states or flag combinations are supplied

## Authorization Rules

Required behavior:

- `comments.setModerationStatus` requires authorized moderation access
- auth mismatch failures must remain explicit rather than blending into invalid moderation-request failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- moderation actions are owner-scoped to the channel or video associated with the targeted comments
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Moderation-State Rules

The wrapper contract for this slice must document:

- that the supported moderation outcomes are `heldForReview`, `published`, and `rejected`
- that the request identifies one or more targeted comments by `id`
- that the request does not carry a request body
- that `banAuthor` may accompany a request only when the moderation outcome is `rejected`
- that comments already moved to `published` or `rejected` are not returned to `heldForReview` through this slice
- that the supported moderation path is intended for direct later Layer 2 and Layer 3 reuse

For supported moderation paths, the contract must explain:

- what moderation outcome values are accepted
- what authorization behavior is required before moderation may proceed
- how `banAuthor` changes the moderation intent when it is allowed
- how successful moderation acknowledgments preserve requested status and target comment identity

## Invalid-Moderation Handling

The contract must treat moderation validation as deterministic.

Required behavior:

- callers may not omit `id` or `moderationStatus` and still expect supported wrapper behavior
- callers may not supply unsupported moderation states or duplicate target comment identifiers and still expect supported wrapper behavior
- callers may not rely on `banAuthor` outside the rejection path
- callers may not supply a request body and still expect supported moderation behavior
- contract and test artifacts must keep these boundaries reviewable

## Upstream Boundary Guidance

The contract must explain that:

- some moderation requests can fail because the targeted comments are missing, unavailable, unsupported for moderation, or owned by a different channel or video context
- higher-layer callers should treat those outcomes as normalized upstream moderation failures rather than local contract ambiguity
- successful moderation acknowledgments remain separate from upstream rejections, unsupported-transition failures, and local validation failures

## Validation Expectations

Representative proof for YT-119 must show:

- maintainers can identify OAuth-required owner-scoped behavior in one review pass
- moderation-state rules are documented clearly enough for future moderation features
- `banAuthor` restrictions are protected by regression coverage
- moderation acknowledgments remain on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/`
- unit coverage for moderation-shape validation and auth enforcement
- transport coverage showing `POST` request construction with query parameters and no request body for `comments.setModerationStatus`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
