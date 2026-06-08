# Data Model: YT-209 Layer 2 Tool `channelBanners_insert`

## Channel Banners Insert Tool

**Purpose**: Public Layer 2 MCP tool named `channelBanners_insert` that exposes the upstream `channelBanners.insert` banner upload operation.

**Fields**:

- `toolName`: Must be `channelBanners_insert`.
- `upstreamResource`: Must be `channelBanners`.
- `upstreamMethod`: Must be `insert`.
- `operationKey`: Must be `channelBanners.insert`.
- `quotaCost`: Must be `50`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Should indicate media-constrained active availability.
- `description`: Caller-facing description that includes endpoint identity, quota cost, OAuth requirement, and media-upload requirement.
- `inputContract`: JSON-compatible schema for the upload request.
- `responseConvention`: Upload-result convention preserving returned channel banner fields.
- `responseBoundary`: Near-raw endpoint boundary with allowed safe wrapper fields.
- `usageNotes`: Caller-facing notes that include quota, OAuth, media, delegation, no-body, and follow-on `channels.update` boundary.
- `caveats`: Safe caveats for media constraints, upload-only behavior, and activation boundary.

**Validation Rules**:

- Tool name must derive from `channelBanners.insert` without adding a `youtube_` prefix.
- Quota cost must be visible in metadata, description, and usage notes.
- Auth mode must not imply API-key-only access.
- Public metadata must not include credentials, stack traces, signed URLs, raw image payloads, binary payloads, private channel data, or secret values.
- The contract must remain scoped to upload behavior and must not claim to activate the banner on a channel.

**Relationships**:

- Uses the `Channel Banner Upload Request` as input.
- Produces a `Banner Upload Result`.
- Depends on the YT-109 Layer 1 `channelBanners.insert` wrapper for endpoint execution.
- Follows YT-201 and YT-202 shared Layer 2 contract standards.

## Channel Banner Upload Request

**Purpose**: Caller-provided arguments for one `channelBanners_insert` invocation.

**Fields**:

- `media` (required): Banner media descriptor.
- `onBehalfOfContentOwner` (optional): Content-owner delegation context for properly authorized YouTube content partners.

**Validation Rules**:

- `media` is required for every request.
- `media.mimeType` is required when using inline media content and must be one of `image/jpeg`, `image/png`, or `application/octet-stream`.
- `media.content` or a supported safe media reference is required by the implementation contract; public examples must avoid raw binary image payloads.
- Media must respect the documented maximum 6 MB file size.
- Caller-facing notes must document that banner images are expected to be 16:9 and at least 2048x1152 pixels, with 2560x1440 recommended.
- JSON metadata request bodies, channel update fields, profile image fields, image-editing instructions, resizing requests, preview-generation requests, and active-banner publication requests are unsupported.
- `onBehalfOfContentOwner`, when present, must be non-empty and must be treated as authorization-sensitive delegation context.

**Relationships**:

- Contains one `Banner Media Input`.
- May contain one `Delegated Content-Owner Context`.
- Is validated before calling the Layer 1 wrapper.

## Banner Media Input

**Purpose**: Safe description of the banner image to upload.

**Fields**:

- `mimeType`: Media MIME type.
- `content`: Inline media content when supported by the implementation path.
- `contentRef`: Optional safe reference to media content when supported by the implementation path.
- `filename`: Optional caller-facing filename for diagnostics.
- `sizeBytes`: Optional safe declared media size.

**Validation Rules**:

- A supported media source must be present.
- Empty media content is invalid.
- Unsupported MIME types are invalid.
- Media larger than the documented maximum 6 MB limit is invalid.
- Public metadata, examples, errors, and logs must not expose raw private image bytes.

**Relationships**:

- Belongs to a `Channel Banner Upload Request`.
- Contributes safe media summary fields to a `Banner Upload Result`.

## Delegated Content-Owner Context

**Purpose**: Optional context that lets a properly authorized YouTube content partner act on behalf of a content owner.

**Fields**:

- `onBehalfOfContentOwner`: Content owner identifier supplied as an optional query parameter.

**Validation Rules**:

- Must be a non-empty string when present.
- Must be documented as partner-only and authorization-sensitive.
- Must not be accepted as a substitute for eligible OAuth authorization.
- Errors must distinguish missing or insufficient authorization from invalid media input.

**Relationships**:

- May be included in a `Channel Banner Upload Request`.
- May appear in safe operation context for a `Banner Upload Result`.

## Banner Upload Result

**Purpose**: Caller-facing result from a successful `channelBanners_insert` upload.

**Fields**:

- `endpoint`: Safe operation identity such as `channelBanners.insert`.
- `quotaCost`: Official quota cost, `50`.
- `item` or `resource`: Near-raw returned channel banner resource fields.
- `url`: Returned banner URL when present in the upstream resource.
- `media`: Safe media summary only; no raw image payload.
- `delegation`: Safe indication of delegation context when present.

**Validation Rules**:

- Must preserve returned upstream channel banner fields such as `kind`, `etag`, and `url` when present.
- Must not fabricate active channel branding state.
- Must not automatically imply that the uploaded banner URL has been applied to a channel.
- Must not expose credentials, signed URLs beyond the returned upstream banner resource URL contract, private channel data, raw image payloads, binary payloads, or secret values.

**Relationships**:

- Produced by `channelBanners_insert`.
- Contains the returned URL that a separate `channels.update` operation may use outside this slice.

## Error Outcome

**Purpose**: Safe caller-facing representation of validation and upstream failures.

**Fields**:

- `category`: Shared Layer 2 error category.
- `message`: Caller-facing correction guidance.
- `details`: Safe diagnostic context, such as invalid field name or upstream error detail code when safe.

**Validation Rules**:

- Missing media input maps to a safe invalid-request outcome.
- Unsupported MIME type, empty media content, oversized media, unsupported request body fields, unsupported upload options, and unsupported image-editing instructions map to safe invalid-request outcomes.
- Missing OAuth, insufficient permission, or invalid delegation context must be distinguishable from invalid media input.
- Upstream `mediaBodyRequired`, `bannerAlbumFull`, quota, authorization, unavailable service, and unexpected upstream failures must follow shared Layer 2 error conventions.
- Errors must not expose stack traces, credentials, raw media, signed URLs, private channel data, or secret values.

## State Transitions

1. **Discovered**: `channelBanners_insert` appears in the public tool catalog with full metadata.
2. **Validated**: Caller arguments satisfy media, OAuth, and optional delegation constraints.
3. **Upload Attempted**: The request is routed to the Layer 1 `channelBanners.insert` wrapper.
4. **Succeeded**: The tool returns a near-raw `Banner Upload Result` with returned resource fields and safe operation context.
5. **Rejected**: Invalid input or authorization-sensitive failures return a safe `Error Outcome`.
6. **Out of Scope**: Requests to activate, resize, preview, edit, or bulk-apply banners are rejected or documented as separate behavior.
