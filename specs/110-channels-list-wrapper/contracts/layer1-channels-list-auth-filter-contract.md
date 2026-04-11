# Contract: YT-110 Layer 1 `channels.list` Auth and Filter Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `channels.list` selector modes, mixed-auth expectations, and invalid-combination rules when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- a clear distinction between public selector paths and owner-scoped `mine` behavior
- explicit maintainer-facing notes for selector-dependent auth behavior
- visible selector exclusivity and invalid-combination rules
- review surfaces that keep `authMode`, `authConditionNote`, `quotaCost`, and endpoint identity visible together

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer selector-auth behavior
- runtime credential payloads to determine access semantics
- silent fallback behavior when conflicting selectors are supplied

## Supported Selector Paths

The wrapper contract for this slice must document at least:

- one public retrieval path through `id`
- one public retrieval path through `forHandle`
- one public retrieval path through username-style lookup when supported
- one owner-scoped retrieval path through `mine`

For each supported path, the contract must explain:

- which request field activates the path
- whether the path is public or owner-scoped
- what auth expectation applies to the path
- whether the path is intended for direct later Layer 2 and Layer 3 reuse

## Selector and Auth Rules

Required behavior:

- selector selection is mutually exclusive for supported requests
- `mine` requires authorized-user context
- public selectors are treated as public retrieval paths
- selector-auth mismatches must be explicit failure outcomes
- selector support caveats (for example username-style support conditions) must be visible in maintainer-facing notes

## Invalid Combination Rules

The contract must treat selector selection as mutually exclusive when paths imply different access semantics.

Required behavior:

- callers may not combine multiple selectors and still expect supported wrapper behavior
- missing selectors and conflicting selectors must be rejected or clearly flagged before execution
- contract and test artifacts must keep these boundaries reviewable

## Empty Result Rules

The contract must explain that:

- a valid selector request may return zero channel items
- zero returned items does not imply wrapper failure
- higher-layer callers should treat empty results as successful retrieval with no matches

## Validation Expectations

Representative proof for YT-110 must show:

- maintainers can identify mixed-auth behavior in one review pass
- selector and auth guidance is documented clearly enough for future channel features
- unsupported selector combinations are protected by regression coverage
- empty-result handling remains on the success path

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/contracts/`
- unit coverage for selector validation and auth enforcement
- transport coverage showing selector-compatible request construction for `channels.list`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
