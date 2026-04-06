# Contract: YT-103 Layer 1 `activities.list` Auth and Filter Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `activities.list` filter modes and authorization expectations when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- a clear distinction between public-channel activity retrieval and authorized-user activity views
- explicit maintainer-facing guidance when auth expectations change by filter mode
- visible invalid-combination rules for unsupported or ambiguous filter selection
- review surfaces that keep `authMode`, `authConditionNote`, `quotaCost`, and endpoint identity visible together

Higher-layer planning and review consumers must not need to rely on:

- hidden implementation details to infer whether OAuth is required
- runtime credential payloads to understand auth semantics
- silent fallback behavior when multiple incompatible filters are supplied

## Supported Access Paths

The wrapper contract for this slice must document at least:

- one supported public-channel activity path through `channelId`
- two supported authorized-user-only activity paths through `mine` and `home`

For each supported path, the contract must explain:

- which request fields activate the path
- whether the path is public or authorized-user-only
- what maintainer-facing auth explanation applies
- whether the path is intended for direct later Layer 2 reuse

## Invalid Combination Rules

The contract must treat filter selection as mutually exclusive when the request paths imply different access modes or meanings.

Required behavior:

- callers may not combine multiple incompatible activity selectors and still expect supported wrapper behavior
- unsupported combinations must be rejected or clearly flagged before execution
- contract and test artifacts must make these boundaries reviewable
- supported selector profiles for this slice are `channelId`, `mine`, and `home`

## Empty Result Rules

The contract must explain that:

- a valid request may return zero activity items
- zero returned items does not imply a wrapper failure
- higher-layer callers should treat an empty result as a successful but empty collection

## Validation Expectations

Representative proof for YT-103 must show:

- maintainers can identify the public-versus-authorized access split in one review pass
- mixed or conditional auth guidance is documented clearly enough for future Layer 2 or Layer 3 work
- unsupported filter combinations are protected by regression coverage
- empty-result handling remains on the success path

Required coverage:

- contract checks for the artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/contracts/`
- unit coverage for endpoint-specific filter validation
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
