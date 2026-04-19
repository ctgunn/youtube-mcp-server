# Contract: YT-121 Layer 1 `commentThreads.list` Lookup and Access Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `commentThreads.list` selector modes, public-access expectations, invalid-combination rules, and empty-result guidance when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- a clear distinction between video-based retrieval through `videoId`, channel-related retrieval through `allThreadsRelatedToChannelId`, and thread lookup through `id`
- explicit maintainer-facing notes for the supported selector paths
- visible selector exclusivity and invalid-combination rules
- review surfaces that keep `authMode`, `quotaCost`, and endpoint identity visible together
- explicit guidance that successful no-match retrievals remain success outcomes

Higher-layer planning and review consumers must not rely on:

- hidden implementation details to infer selector behavior
- silent fallback behavior when conflicting selectors are supplied
- undocumented assumptions about unsupported retrieval modifiers
- runtime credential payloads to determine access semantics

## Supported Selector Paths

The wrapper contract for this slice must document at least:

- one video-scoped retrieval path through `videoId`
- one channel-related retrieval path through `allThreadsRelatedToChannelId`
- one direct thread retrieval path through `id`

For each supported path, the contract must explain:

- which request field activates the path
- what type of comment threads the path returns
- what access expectation applies to the path
- whether the path is intended for direct later Layer 2 and Layer 3 reuse

## Selector and Access Rules

Required behavior:

- selector selection is mutually exclusive for supported requests
- `videoId`, `allThreadsRelatedToChannelId`, and `id` stay reviewable as public retrieval paths for this slice
- selector-access mismatches must be explicit failure outcomes when callers use an incompatible auth context
- selector guidance must remain visible in maintainer-facing notes
- video-based, channel-related, and direct thread lookup behavior must stay distinguishable in review artifacts

## Invalid Combination Rules

The contract must treat selector selection as mutually exclusive when paths imply different retrieval goals.

Required behavior:

- callers may not combine multiple primary selectors and still expect supported wrapper behavior
- missing selectors and conflicting selectors must be rejected or clearly flagged before execution
- unsupported retrieval modifiers must be rejected or clearly flagged before execution
- contract and test artifacts must keep these boundaries reviewable

## Empty Result Rules

The contract must explain that:

- a valid selector request may return zero comment-thread items
- zero returned items do not imply wrapper failure
- higher-layer callers should treat empty results as successful retrieval with no matches
- missing selectors, conflicting selectors, unsupported modifiers, and access mismatches must remain separate reviewable failure conditions

## Validation Expectations

Representative proof for YT-121 must show:

- maintainers can identify the supported selector paths in one review pass
- selector and access guidance is documented clearly enough for future comment-thread features
- unsupported selector combinations are protected by regression coverage
- empty-result handling remains on the success path
- higher-layer consumers can identify source quota and selector details without external endpoint research

Required coverage:

- contract checks for feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/contracts/`
- unit coverage for selector validation and access enforcement
- transport coverage showing selector-compatible request construction for `commentThreads.list`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
