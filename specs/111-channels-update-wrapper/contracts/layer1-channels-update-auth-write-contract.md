# Contract: YT-111 Layer 1 `channels.update` Auth and Write Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `channels.update` authorization requirements, writable-part rules, and invalid-write boundaries when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- OAuth-required behavior being explicit in maintainer-facing wrapper notes and review surfaces
- visible writable-part guidance for supported update paths
- clear rejection of unsupported or read-only write shapes
- review surfaces that keep `authMode`, `quotaCost`, endpoint identity, and write-boundary notes visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer whether a write path is supported
- runtime credential payloads to determine access semantics
- silent fallback behavior when unsupported writable parts or read-only fields are supplied

## Authorization Rules

Required behavior:

- `channels.update` requires authorized channel-management access
- auth mismatch failures must remain explicit rather than blending into invalid write-shape failures
- maintainers must be able to determine from feature artifacts that public-only access is unsupported for this endpoint
- contract and review artifacts must not expose secrets, tokens, or raw credential material

## Writable-Part Rules

The wrapper contract for this slice must document:

- that `part` activates the intended writable update boundary
- that supported writable parts include `brandingSettings` and `localizations` for this slice
- that the provided channel `body` must align with the selected writable part
- that unsupported or read-only channel fields are outside the supported write boundary
- that maintainers can identify supported write guidance before implementation inspection

For supported write paths, the contract must explain:

- which request field activates the write boundary
- what writable body content is expected
- what channel-management behavior is required before the update may proceed
- whether the path is intended for direct later Layer 2 and Layer 3 reuse

## Invalid-Write Handling

The contract must treat write-shape validation as deterministic.

Required behavior:

- callers may not omit `part` or `body` and still expect supported wrapper behavior
- callers may not supply unsupported writable parts or read-only fields and still expect supported wrapper behavior
- part-to-body mismatches must be rejected or clearly flagged before execution
- contract and test artifacts must keep these boundaries reviewable

## Channel-Specific Guidance

The contract must explain that:

- some channel-update flows may depend on previously retrieved or created channel-managed assets
- maintainers should keep channel-banner reuse notes visible when update inputs depend on prior `channelBanners.insert` output through `brandingSettings.image.bannerExternalUrl`
- higher-layer callers should treat the wrapper as one endpoint-level building block rather than a full channel-management workflow

## Validation Expectations

Representative proof for YT-111 must show:

- maintainers can identify OAuth-required behavior in one review pass
- writable-part and unsupported-write guidance is documented clearly enough for future channel features
- unsupported writable shapes are protected by regression coverage
- updated-resource handling remains on the success path for valid authorized requests

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/contracts/`
- unit coverage for write-shape validation and auth enforcement
- transport coverage showing `PUT` request construction for `channels.update`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
