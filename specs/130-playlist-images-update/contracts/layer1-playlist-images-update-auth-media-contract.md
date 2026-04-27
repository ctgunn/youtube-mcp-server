# Contract: YT-130 Layer 1 `playlistImages.update` Auth and Media Contract

## Purpose

Define the maintainer-facing rules for authorized access, playlist-image update inputs, media-update requirements, and invalid request handling for the internal `playlistImages.update` wrapper.

## Authorization Rules

- `playlistImages.update` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `playlistImages.update` as a public or API-key-compatible path
- Authorized access guidance must remain visible in wrapper metadata, contract artifacts, consumer summaries, and implementation docstrings

## Media-Update Rules

- A supported request must include `body` update metadata and `media` update input together
- `body` update metadata without `media` update input is an invalid request shape for this slice
- `media` update input without the minimum `body` metadata is an invalid request shape
- `metadata-only` and `media-only` requests are outside the supported YT-130 contract
- Media-update sensitivity must be visible in wrapper metadata, contract artifacts, and implementation docstrings

## Invalid-Shape Handling

- Unsupported or incomplete update requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-130 wrapper contract
- The wrapper must not silently coerce incomplete update requests into supported behavior
- The wrapper must preserve a meaningful distinction between `invalid_request` failures represented by incomplete or malformed input, unauthorized access, and normalized upstream update failures after execution begins

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `playlistImages.update` is OAuth-only
- the endpoint carries a quota cost of `50`
- playlist-image identifying metadata plus media-update input is required
- the wrapper remains internal to Layer 1 in this slice
- successful update outcomes and failure boundaries remain reviewable without reading raw upstream docs
