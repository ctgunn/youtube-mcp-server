# Contract: YT-108 Layer 1 `captions.delete` Authorization Contract

## Purpose

Define the maintainer-facing rules for authorized access, ownership-sensitive delete behavior, invalid request handling, and delegation visibility for the internal `captions.delete` wrapper.

## Authorization Rules

- `captions.delete` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `captions.delete` as a public or API-key-compatible path
- Ownership-sensitive behavior must remain visible in metadata and contract artifacts, including when authorized access still does not permit deletion of the requested caption track
- Delegation guidance, when supported, supplements the authorized-access requirement rather than replacing it

## Delete Request Rules

- A supported request must include one caption track identifier
- `onBehalfOfContentOwner` may accompany that identifier when the caller uses a supported delegated ownership path
- The required identifier and optional delegation input must remain reviewable in wrapper metadata, contract artifacts, and implementation docstrings
- Unsupported extra fields or undocumented request modes are outside the promised YT-108 wrapper contract
- Successful deletion must remain reviewable through a normalized internal result even when the upstream response body is empty

## Delegation Guidance

- `onBehalfOfContentOwner` may appear only as optional delegation context on an otherwise valid authorized request
- Delegation context must remain reviewable to maintainers before reuse
- Delegation context must not create a separate auth mode or a separate wrapper contract for this feature
- Any delegated request still depends on authorized access and any endpoint-specific ownership requirement for the target caption track

## Invalid-Shape and Failure Handling

- Unsupported or incomplete delete requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-108 wrapper contract
- The wrapper must not silently coerce incomplete or unsupported requests into supported behavior
- Failure handling must preserve a visible distinction between ownership-restricted caption tracks, nonexistent caption tracks, `access-denied` delete failures, and `not-found` delete failures

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `captions.delete` is OAuth-required
- the endpoint carries a quota cost of `50`
- the request requires a caption track identifier
- optional `onBehalfOfContentOwner` guidance is available when relevant
- some failures indicate ownership or permission limits rather than caption absence
- the wrapper remains internal to Layer 1 in this slice
