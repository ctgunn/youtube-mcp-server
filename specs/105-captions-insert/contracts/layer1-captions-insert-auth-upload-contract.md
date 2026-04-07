# Contract: YT-105 Layer 1 `captions.insert` Auth and Upload Contract

## Purpose

Define the maintainer-facing rules for authorized access, upload requirements, invalid request handling, and delegation visibility for the internal `captions.insert` wrapper.

## Authorization Rules

- `captions.insert` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `captions.insert` as a public or API-key-compatible path
- Delegation guidance, when supported, supplements the authorized-access requirement rather than replacing it

## Upload Rules

- A supported request must include `body` metadata and `media` upload input together
- `body` metadata without `media` upload input is an invalid request shape
- `media` upload input without the minimum `body` metadata is an invalid request shape
- Metadata-only and upload-only requests are outside the supported YT-105 contract
- Upload sensitivity must be visible in wrapper metadata, contract artifacts, and implementation docstrings

## Delegation Guidance

- `onBehalfOfContentOwner` may appear only as optional delegation context on an otherwise valid authorized request
- Delegation context must remain reviewable to maintainers before reuse
- Delegation context must not create a separate auth mode or a separate wrapper contract for this feature
- Any delegated request still depends on authorized access for the target creation path

## Invalid-Shape Handling

- Unsupported or incomplete creation requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-105 wrapper contract
- The wrapper must not silently coerce incomplete creation requests into supported behavior

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `captions.insert` is OAuth-only
- the endpoint carries a quota cost of `400`
- upload-capable input is required
- optional `onBehalfOfContentOwner` guidance is available when relevant
- the wrapper remains internal to Layer 1 in this slice
