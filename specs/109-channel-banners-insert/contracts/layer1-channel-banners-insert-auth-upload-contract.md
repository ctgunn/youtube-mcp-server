# Contract: YT-109 Layer 1 `channelBanners.insert` Auth and Upload Contract

## Purpose

Define the maintainer-facing rules for authorized access, banner-image upload requirements, invalid request handling, response-URL behavior, and delegation visibility for the internal `channelBanners.insert` wrapper.

## Authorization Rules

- `channelBanners.insert` is an OAuth-required endpoint
- The wrapper must make the authorized-access requirement visible before higher-layer reuse
- The wrapper must not present `channelBanners.insert` as a public or API-key-compatible path
- Delegation guidance, when supported, supplements the authorized-access requirement rather than replacing it

## Upload Rules

- A supported request must include one `media` upload input
- The upload must remain reviewable for the documented image constraints: 16:9 aspect ratio, minimum 2048x1152 resolution, recommended 2560x1440 resolution, maximum 6 MB file size, and accepted MIME types `image/jpeg`, `image/png`, or `application/octet-stream`
- Do not include a JSON request body for this endpoint
- Upload sensitivity must be visible in wrapper metadata, contract artifacts, and implementation docstrings

## Delegation Guidance

- `onBehalfOfContentOwner` may appear only as optional delegation context on an otherwise valid authorized request
- Delegation context must remain reviewable to maintainers before reuse
- Delegation context must not create a separate auth mode or a separate wrapper contract for this feature
- Any delegated request still depends on authorized access for the target channel-branding path

## Response-URL Expectations

- A successful upload returns a banner URL that later channel-branding work can pass into `channels.update`
- The wrapper's normalized result must keep that URL visible enough for higher-layer review and reuse
- The feature must not merge the later `channels.update` call into this wrapper slice

## Invalid-Shape Handling

- Unsupported or incomplete banner-upload requests must be rejected or clearly flagged before execution
- Unexpected request fields are outside the promised YT-109 wrapper contract
- Missing image content is an invalid request boundary and must not be silently coerced into supported behavior
- The wrapper must preserve a meaningful distinction between `invalid upload input` failures represented as `invalid_request`, unauthorized access, and `target-channel restrictions` represented as `target_channel`

## Higher-Layer Review Expectations

Later Layer 2 and Layer 3 authors must be able to determine in one review pass that:

- `channelBanners.insert` is OAuth-only
- the endpoint carries a quota cost of `50`
- banner image upload input is required
- optional `onBehalfOfContentOwner` guidance is available when relevant
- a successful result returns the banner URL needed for later `channels.update`
- the wrapper remains internal to Layer 1 in this slice
