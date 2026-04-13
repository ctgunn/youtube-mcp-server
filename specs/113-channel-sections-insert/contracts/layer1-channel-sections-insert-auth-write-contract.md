# Contract: YT-113 Layer 1 `channelSections.insert` Auth and Write Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `channelSections.insert` authorization requirements, section-type content rules, delegation guidance, and invalid-create boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible section-type guidance for supported create paths
- clear rejection of unsupported, duplicated, or mismatched playlist and channel content
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and create-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a create path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported type-and-content combinations are supplied

## Authorization Rules

Required behavior:

- `channelSections.insert` requires authorized channel-management access
- auth mismatch failures must remain explicit rather than blending into invalid create-shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- optional `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` guidance must remain visible for eligible partner-authorized requests
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Section-Type and Content Rules

The wrapper contract for this slice must document:

- that `snippet.type` activates the intended channel-section create boundary
- that `singlePlaylist` requires exactly one playlist ID
- that `singlePlaylist` and `multiplePlaylists` require playlist IDs and do not accept channel IDs
- that `multipleChannels` requires channel IDs and does not accept playlist IDs
- that `multiplePlaylists` and `multipleChannels` require a custom section title
- that non playlist-backed and non channel-backed section types must not be paired with unexpected `contentDetails` lists

For supported create paths, the contract must explain:

- which body fields activate the create boundary
- what content details are expected
- what channel-management behavior is required before the create may proceed
- whether the path is intended for direct later Layer 2 and Layer 3 reuse

## Invalid-Create Handling

The contract must treat create-shape validation as deterministic.

Required behavior:

- callers may not omit `part`, `body`, or `snippet.type` and still expect supported wrapper behavior
- callers may not supply unsupported section-type and content combinations and still expect supported wrapper behavior
- callers may not supply duplicated playlists or duplicated channels and still expect supported wrapper behavior
- title-required section types must fail clearly when the title is missing
- contract and test artifacts must keep these boundaries reviewable

## Upstream Boundary Guidance

The contract must explain that:

- one channel can only create a limited number of sections, including upstream failures that report the maximum number of sections has already been reached
- some create requests can fail because referenced channels or playlists are inactive, private, duplicated, or not found
- higher-layer callers should treat those outcomes as normalized upstream create failures rather than local contract ambiguity

## Validation Expectations

Representative proof for YT-113 must show:

- maintainers can identify OAuth-required behavior in one review pass
- section-type, title, and content rules are documented clearly enough for future channel-section features
- unsupported or duplicated create shapes are protected by regression coverage
- created-resource handling remains on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/`
- unit coverage for create-shape validation and auth enforcement
- transport coverage showing `POST` request construction for `channelSections.insert`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
