# Contract: YT-144 Layer 1 `thumbnails.set` Auth and Upload Contract

## Purpose

Define the maintainer-facing rules for authorized access, thumbnail-update inputs, upload requirements, target-video handling, and invalid request handling for the internal `thumbnails.set` wrapper.

## Authorization Rules

- `thumbnails.set` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `thumbnails.set` as a public or API-key-compatible path
- Authorized access guidance must remain visible in wrapper metadata, contract artifacts, consumer summaries, and implementation docstrings

## Upload Rules

- A supported request must include `videoId` and `media` upload input together
- `videoId` without `media` upload input is an invalid request shape
- `media` upload input without `videoId` is an invalid request shape
- `target-only` and `upload-only` requests are outside the supported YT-144 contract
- Upload sensitivity must be visible in wrapper metadata, contract artifacts, and implementation docstrings

## Invalid-Shape Handling

- Unsupported or incomplete thumbnail-update requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-144 wrapper contract
- The wrapper must not silently coerce incomplete thumbnail-update requests into supported behavior
- The wrapper must preserve a meaningful distinction between `invalid_request` failures represented by incomplete or malformed input, unauthorized access represented by `auth`, target-video failures represented by `target_video`, and normalized `upstream_service` upstream thumbnail-update failures after execution begins

## Target-Video Failure Expectations

- A validly shaped authorized request may still fail because the target video is unavailable, inaccessible, not writable by the caller, or otherwise ineligible for thumbnail update
- Target-video restrictions must remain distinguishable from malformed `videoId` input
- Target-video failures must remain distinguishable from generic upstream update failures
- Successful thumbnail updates must preserve the targeted `videoId` for downstream review

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `thumbnails.set` is OAuth-only
- the endpoint carries a quota cost of `50`
- `videoId` plus media-upload input is required
- the wrapper remains internal to Layer 1 in this slice
- successful thumbnail-update outcomes and failure boundaries remain reviewable without reading raw upstream docs
