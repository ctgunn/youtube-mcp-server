# Contract: Layer 2 `channelBanners_insert` Tool

## Public Tool Identity

- **Tool name**: `channelBanners_insert`
- **Mapped upstream operation**: `channelBanners.insert`
- **Resource family**: `channelBanners`
- **Layer**: Layer 2 endpoint-backed public MCP tool
- **Official quota cost**: `50` units per invocation
- **Auth mode**: `oauth_required`
- **Availability**: Active, media-constrained

## Scope

`channelBanners_insert` uploads one channel banner image through the upstream banner upload endpoint and returns the uploaded `channelBanner` resource or upload outcome in a near-raw shape.

The tool does not:

- Activate the uploaded banner on a channel.
- Call `channels.update`.
- Resize, crop, transform, preview, or validate visual placement beyond documented upload constraints.
- Update channel profile images or other channel metadata.
- Perform bulk channel branding operations.
- Add Layer 3 enrichment, ranking, summarization, or heuristic interpretation.

## Input Contract

The input is a JSON-compatible object.

```json
{
  "type": "object",
  "required": ["media"],
  "properties": {
    "media": {
      "type": "object",
      "properties": {
        "mimeType": {
          "type": "string",
          "enum": ["image/jpeg", "image/png", "application/octet-stream"]
        },
        "content": {
          "type": "string",
          "minLength": 1
        },
        "contentRef": {
          "type": "string",
          "minLength": 1
        },
        "filename": {
          "type": "string",
          "minLength": 1
        },
        "sizeBytes": {
          "type": "integer",
          "minimum": 0,
          "maximum": 6291456
        }
      },
      "additionalProperties": false
    },
    "onBehalfOfContentOwner": {
      "type": "string",
      "minLength": 1
    }
  },
  "additionalProperties": false
}
```

### Input Rules

- `media` is required.
- The media descriptor must provide a supported media source through the implementation-supported path.
- Accepted MIME types are `image/jpeg`, `image/png`, and `application/octet-stream`.
- The uploaded image must respect the documented maximum 6 MB limit.
- Caller-facing notes must state the documented 16:9 image expectation, minimum 2048x1152 resolution, and 2560x1440 recommendation.
- `onBehalfOfContentOwner` is optional and only valid for properly authorized YouTube content partner requests.
- The tool must not accept JSON channel metadata bodies, `channels.update` fields, profile-image fields, image-editing instructions, active-banner publication options, or bulk update instructions.

## Discovery Metadata Requirements

Tool discovery metadata must include:

- `name`: `channelBanners_insert`
- `upstream.resource`: `channelBanners`
- `upstream.method`: `insert`
- `upstream.operationKey`: `channelBanners.insert`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: media-constrained active availability
- `resourceFamily`: `channelBanners`
- `inputContract`: the public input contract
- `responseConvention`: upload-result convention
- `responseBoundary`: near-raw boundary
- `usageNotes`: quota, OAuth, media, delegation, no-body, returned URL, and `channels.update` boundary notes
- `caveats`: media constraints, upload-only scope, and activation boundary

Discovery descriptions and usage notes must visibly include `Quota cost: 50`.

## Response Contract

Successful responses must preserve the upstream `channelBanner` resource or upload outcome.

Representative successful shape:

```json
{
  "endpoint": "channelBanners.insert",
  "quotaCost": 50,
  "item": {
    "kind": "youtube#channelBannerResource",
    "etag": "etag-value",
    "url": "https://yt3.googleusercontent.com/example-banner"
  },
  "media": {
    "mimeType": "image/png",
    "sizeBytes": 2048
  },
  "delegation": {
    "onBehalfOfContentOwner": "content-owner-id"
  }
}
```

Response rules:

- Preserve returned upstream fields when present.
- Include the returned banner URL when present.
- Include only safe media summaries; never include raw image payloads.
- Include safe operation context such as endpoint identity and quota cost.
- Do not fabricate channel branding state or claim the banner is active on the channel.
- Do not persist the returned URL for later calls.

## Error Contract

The tool must surface safe shared Layer 2 error categories:

- `invalid_request`
- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `endpoint_unavailable`
- `upstream_failure`

Endpoint-specific invalid request examples:

- Missing `media`.
- Missing or empty media content/reference.
- Unsupported `media.mimeType`.
- Media over the 6 MB limit.
- Unsupported JSON metadata request body.
- Unsupported channel update fields, profile image fields, active-banner options, image-editing options, or bulk update fields.
- Upstream `mediaBodyRequired`.
- Upstream `bannerAlbumFull`.

Security rules:

- Errors must not expose OAuth tokens, API keys, stack traces, raw image payloads, binary payloads, private channel data, signed URLs, or secret values.
- Authorization failures must be distinguishable from invalid media failures.
- Delegation failures must clearly identify the authorization-sensitive content-owner context without exposing sensitive owner credentials.

## Required Examples

The implementation must provide safe caller-facing examples for:

- Authorized banner upload with supported media input.
- Delegated content-owner upload context.
- Missing media validation failure.
- Invalid media validation failure.
- Unsupported channel update or image-editing option failure.
- Authorization-sensitive failure.
- Successful returned URL with explicit note that `channels.update` is separate.

## Verification Requirements

Before implementation is considered complete:

- Focused contract tests must prove discovery metadata includes endpoint identity, quota cost, OAuth requirement, media requirement, delegation notes, no-body metadata rule, returned URL behavior, and activation boundary.
- Unit tests must prove media and delegation validation rejects unsupported inputs safely.
- Integration tests must prove default registration exposes executable `channelBanners_insert`.
- Handler tests must prove successful upload result mapping preserves returned resource fields without raw image leakage.
- Regression tests must preserve existing baseline, retrieval, activities, and captions tools.
- Final validation must include `python3 -m pytest` and `python3 -m ruff check .`.
- Every new or changed Python function must include a reStructuredText docstring.
