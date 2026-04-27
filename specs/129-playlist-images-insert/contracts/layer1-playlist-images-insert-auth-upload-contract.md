# Contract: YT-129 Layer 1 `playlistImages.insert` Auth and Upload Contract

## Purpose

Define the maintainer-facing rules for authorized access, playlist-image creation inputs, upload requirements, and invalid request handling for the internal `playlistImages.insert` wrapper.

## Authorization Rules

- `playlistImages.insert` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `playlistImages.insert` as a public or API-key-compatible path
- Authorized access guidance must remain visible in wrapper metadata, contract artifacts, consumer summaries, and implementation docstrings

## Upload Rules

- A supported request must include `body` metadata and `media` upload input together
- `body` metadata without `media` upload input is an invalid request shape
- `media` upload input without the minimum `body` metadata is an invalid request shape
- `metadata-only` and `upload-only` requests are outside the supported YT-129 contract
- Upload sensitivity must be visible in wrapper metadata, contract artifacts, and implementation docstrings

## Invalid-Shape Handling

- Unsupported or incomplete creation requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-129 wrapper contract
- The wrapper must not silently coerce incomplete creation requests into supported behavior
- The wrapper must preserve a meaningful distinction between `invalid_request` failures represented by incomplete or malformed input, unauthorized access, and normalized upstream create failures after execution begins

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `playlistImages.insert` is OAuth-only
- the endpoint carries a quota cost of `50`
- playlist-image metadata plus media-upload input is required
- the wrapper remains internal to Layer 1 in this slice
- successful creation outcomes and failure boundaries remain reviewable without reading raw upstream docs
