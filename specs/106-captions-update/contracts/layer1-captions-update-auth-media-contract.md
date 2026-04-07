# Contract: YT-106 Layer 1 `captions.update` Auth and Media Contract

## Purpose

Define the maintainer-facing rules for authorized access, media-update expectations, invalid request handling, and delegation visibility for the internal `captions.update` wrapper.

## Authorization Rules

- `captions.update` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `captions.update` as a public or API-key-compatible path
- Delegation guidance, when supported, supplements the authorized-access requirement rather than replacing it

## Media-Update Rules

- A supported request must include `body`
- `media` may accompany `body` when the update replaces caption content
- `media` without `body` is an invalid request shape
- body-only and body-plus-media requests are the only supported YT-106 update modes
- Media-update sensitivity must be visible in wrapper metadata, contract artifacts, and implementation docstrings

## Delegation Guidance

- `onBehalfOfContentOwner` may appear only as optional delegation context on an otherwise valid authorized request
- Delegation context must remain reviewable to maintainers before reuse
- Delegation context must not create a separate auth mode or a separate wrapper contract for this feature
- Any delegated request still depends on authorized access for the target update path

## Invalid-Shape Handling

- Unsupported or incomplete update requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-106 wrapper contract
- The wrapper must not silently coerce incomplete update requests into supported behavior
- Media-replacement requests with an invalid or incomplete `body` remain invalid request shapes

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `captions.update` is OAuth-required
- the endpoint carries a quota cost of `450`
- `body` is always required
- `media` is only used for supported content-replacement updates
- optional `onBehalfOfContentOwner` guidance is available when relevant
- the wrapper remains internal to Layer 1 in this slice
