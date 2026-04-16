# Contract: YT-119 Layer 1 `comments.setModerationStatus` Auth and Write Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `comments.setModerationStatus` authorization requirements, supported moderation transitions, optional moderation-flag rules, and invalid-moderation boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible moderation-state guidance for the supported moderation path
- clear rejection of unsupported moderation states or incompatible moderation-flag combinations
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and moderation-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a moderation path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported moderation combinations are supplied

## Authorization Rules

Required behavior:

- `comments.setModerationStatus` requires authorized comment-moderation access
- auth mismatch failures must remain explicit rather than blending into invalid moderation-shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- optional delegated-owner guidance, if supported for this slice, must remain visible for eligible authorized requests
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Moderation-State Rules

The wrapper contract for this slice must document:

- that the supported moderation boundary is moderation-state change for existing comments
- that the request must include one or more target comment identifiers
- that the request must include one supported moderation outcome
- that the supported request remains query-only and does not require a moderation body payload
- that the representative supported moderation outcomes for this slice are `published`, `heldForReview`, and `rejected`
- that `banAuthor` is only supported when paired with the rejection-style moderation outcome
- that unsupported moderation states or incompatible moderation-flag combinations fall outside the wrapper boundary

For supported moderation paths, the contract must explain:

- which fields activate the supported moderation boundary
- what moderation outcome is expected to be reviewable in the normalized result
- what authorization behavior is required before the moderation change may proceed
- whether optional delegated-owner inputs are preserved in successful normalized results

## Invalid-Moderation Handling

The contract must treat moderation-shape validation as deterministic.

Required behavior:

- callers may not omit the comment identifiers or moderation outcome and still expect supported wrapper behavior
- callers may not supply unsupported moderation states or conflicting moderation flags and still expect supported wrapper behavior
- callers may not supply duplicate or unusable comment identifiers and still expect supported wrapper behavior
- contract and test artifacts must keep these boundaries reviewable

## Upstream Boundary Guidance

The contract must explain that:

- some moderation requests can fail because the targeted comments are missing, deleted, locked, or otherwise unavailable for moderation
- some moderation requests can fail because the authorized caller lacks permission to moderate the targeted comments
- higher-layer callers should treat those outcomes as normalized upstream moderation failures rather than local contract ambiguity
- successful moderation acknowledgments remain separate from upstream rejections, unsupported-transition failures, and local validation failures

## Validation Expectations

Representative proof for YT-119 must show:

- maintainers can identify OAuth-required behavior in one review pass
- moderation-state rules are documented clearly enough for future moderation features
- unsupported moderation combinations and invalid targets are protected by regression coverage
- moderation-acknowledgment handling remains on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/119-comments-set-moderation-status/contracts/`
- unit coverage for moderation-shape validation and auth enforcement
- transport coverage showing `POST` request construction for `comments.setModerationStatus`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
