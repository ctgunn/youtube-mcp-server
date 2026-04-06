# Contract: YT-104 Layer 1 `captions.list` Auth and Selector Contract

## Purpose

Define how maintainers and future higher-layer authors should interpret `captions.list` selector modes, OAuth requirements, and delegation expectations when reusing the internal Layer 1 wrapper.

## Consumer Expectations

Higher-layer planning and review consumers may rely on:

- a clear statement that `captions.list` requires authorized access
- explicit maintainer-facing guidance for selector choice between `videoId` and `id`
- visible guidance for optional `onBehalfOfContentOwner` delegation where it is supported
- visible invalid-combination rules for unsupported or ambiguous selector selection
- review surfaces that keep `authMode`, quota cost, endpoint identity, and delegation notes visible together

Higher-layer planning and review consumers must not need to rely on:

- hidden implementation details to infer whether OAuth is required
- runtime credential payloads to understand delegation semantics
- silent fallback behavior when multiple incompatible selectors are supplied

## Supported Access Paths

The wrapper contract for this slice must document at least:

- one supported caption listing path through `videoId`
- one supported direct caption-track lookup path through `id`

For each supported path, the contract must explain:

- which request fields activate the path
- that the path requires authorized access
- what maintainer-facing auth explanation applies
- whether `onBehalfOfContentOwner` is allowed for that path in this slice
- whether the path is intended for direct later transcript or caption reuse

## Delegation Rules

The contract must explain that:

- `onBehalfOfContentOwner` is delegation context, not a separate auth mode
- delegation guidance must remain visible in maintainer-facing artifacts before reuse
- delegated requests still require authorized access
- unsupported delegation and selector combinations must be rejected or clearly flagged before execution

## Invalid Combination Rules

The contract must treat selector selection as mutually exclusive when request paths imply different meanings.

Required behavior:

- callers may not combine `videoId` and `id` and still expect supported wrapper behavior
- unsupported combinations must be rejected or clearly flagged before execution
- contract and test artifacts must make these boundaries reviewable
- supported selector profiles for this slice are `videoId` and `id`

## Empty Result Rules

The contract must explain that:

- a valid request may return zero caption tracks
- zero returned items does not imply a wrapper failure
- higher-layer callers should treat an empty result as a successful but empty collection

## Validation Expectations

Representative proof for YT-104 must show:

- maintainers can identify the OAuth-required access rule in one review pass
- selector and delegation guidance is documented clearly enough for future transcript or caption-management work
- unsupported selector combinations are protected by regression coverage
- empty-result handling remains on the success path

Required coverage:

- contract checks for the artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/contracts/`
- unit coverage for endpoint-specific selector validation and auth enforcement
- transport coverage showing authorized request construction for `captions.list`
- integration or contract checks proving higher-layer reuse decisions can be made without external endpoint research
- consumer-facing summary checks proving higher layers can see quota, auth, and delegation guidance without parsing raw result payloads
