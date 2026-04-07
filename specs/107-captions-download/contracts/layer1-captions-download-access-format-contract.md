# Contract: YT-107 Layer 1 `captions.download` Access and Format Contract

## Purpose

Define the maintainer-facing rules for authorized access, permission-sensitive behavior, translation and format options, invalid request handling, and delegation visibility for the internal `captions.download` wrapper.

## Authorization Rules

- `captions.download` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `captions.download` as a public or API-key-compatible path
- Permission-sensitive behavior must remain visible in metadata and contract artifacts, including when authorized access still does not permit download of the requested caption track
- Delegation guidance, when supported, supplements the authorized-access requirement rather than replacing it

## Format and Translation Rules

- A supported request must include one caption track identifier
- `tfmt` may accompany that identifier when the caller requests a supported output format
- `tlang` may accompany that identifier when the caller requests a supported translation language
- `tfmt` and `tlang` must remain reviewable in wrapper metadata, contract artifacts, and implementation docstrings
- Unsupported option combinations or undocumented extra fields are outside the promised YT-107 wrapper contract

## Delegation Guidance

- `onBehalfOfContentOwner` may appear only as optional delegation context on an otherwise valid authorized request
- Delegation context must remain reviewable to maintainers before reuse
- Delegation context must not create a separate auth mode or a separate wrapper contract for this feature
- Any delegated request still depends on authorized access and any endpoint-specific permission requirement for the target caption track

## Invalid-Shape and Failure Handling

- Unsupported or incomplete download requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-107 wrapper contract
- The wrapper must not silently coerce incomplete or unsupported requests into supported behavior
- Failure handling must preserve a visible distinction between inaccessible caption tracks, nonexistent caption tracks, `access-denied` caption-track failures, and `not-found` caption-track failures

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `captions.download` is OAuth-required
- the endpoint carries a quota cost of `200`
- the request requires a caption track identifier
- `tfmt` and `tlang` are the documented optional output modifiers for this slice
- optional `onBehalfOfContentOwner` guidance is available when relevant
- some failures indicate permission limits rather than caption absence
- the wrapper remains internal to Layer 1 in this slice
