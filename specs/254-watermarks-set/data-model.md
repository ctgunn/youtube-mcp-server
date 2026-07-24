# Data Model: Layer 2 Tool `watermarks_set`

## Watermarks Set Tool

Represents the public Layer 2 MCP tool named `watermarks_set`.

**Fields**

- `name`: `watermarks_set`
- `upstreamResource`: `watermarks`
- `upstreamMethod`: `set`
- `operationKey`: `watermarks.set`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: owner-only OAuth upload mutation operation
- `resourceFamily`: `watermarks`
- `description`: caller-facing summary including endpoint, quota, OAuth, required `channelId`, required `body`, required `media`, upload boundary, sparse acknowledgment, partner-delegation boundary, and out-of-scope caveats
- `inputSchema`: request contract for one watermark-set request
- `responseBoundary`: structured upload or mutation acknowledgment boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `watermarks.set` wrapper from YT-154.
- Uses shared Layer 2 metadata, naming, response, validation, error, upload-result, mutation-result, and example conventions from YT-201 and YT-202.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Watermark Set Request

Represents one caller-provided request to set a channel watermark.

**Fields**

- `channelId`: required target YouTube channel identifier.
- `body`: required watermark metadata payload.
- `media`: required watermark image upload payload.

**Validation Rules**

- The request must be an object.
- `channelId` is required and must be non-empty text identifying one target channel.
- `body` is required and must include supported timing and position metadata.
- `media` is required and must include supported upload content and MIME type details.
- Metadata-only requests, media-only requests, unsupported top-level fields, alias-only target fields, partner delegation fields, bulk watermark shapes, empty values, malformed values, and out-of-scope workflow fields are rejected before endpoint execution.
- OAuth authorization must be available for every supported request.

## Channel Identity

Represents the target channel whose watermark is being set.

**Fields**

- `channelId`: caller-provided YouTube channel identifier.

**Validation Rules**

- Exactly one target channel ID is required for each watermark-set request.
- The target channel ID must be non-empty text.
- Ambiguous multi-target values, duplicate target declarations, or comma-separated values should be rejected where locally detectable.
- Access failures for valid-looking identities must remain distinguishable from missing identity and not-found outcomes.

## Watermark Metadata

Represents caller-provided watermark placement and display details.

**Fields**

- `timing`: required timing metadata for when the watermark appears.
- `position`: required position metadata for where the watermark appears.
- `targetChannelId`: optional linked channel identity when supported by the upstream operation and provided as text.

**Validation Rules**

- `body` must be an object.
- `body.timing` is required and must be a non-empty object.
- `body.position` is required and must be a non-empty object.
- `body.targetChannelId`, when provided, must be text.
- Missing, empty, incomplete, incompatible, deprecated, unsupported, or otherwise unusable metadata is rejected or categorized before execution where locally detectable.

## Watermark Upload Payload

Represents the upload-specific content supplied for the watermark image.

**Fields**

- `mimeType`: media type of the watermark upload.
- `content`: image content for the watermark upload.
- `contentProvided`: safe derived flag for result summaries.
- `sizeBytes`: safe derived size when available without exposing private media data.

**Validation Rules**

- `media` must be an object.
- `media.mimeType` is required and must be one supported media type.
- Supported media types remain aligned with the Layer 1 wrapper: `image/jpeg`, `image/png`, and `application/octet-stream`.
- `media.content` is required and must not be empty.
- Upload content must not exceed the documented 10 MB watermark boundary when determinable locally.
- Results, examples, logs, and errors must not expose raw media bytes or private media content.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `delegation`: absent for this slice because `onBehalfOfContentOwner` remains outside the supported public contract
- `scopes`: caller-facing scope guidance when present in metadata or documentation

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but cannot update the target channel watermark produces `authorization_failed`.
- API-key-only access is not a valid state for `watermarks_set`.
- Credentials, authorization headers, raw upstream diagnostics, raw media content, request context, and secret-bearing details must never be exposed.

## Watermark Update Acknowledgment

Represents a successful `watermarks_set` response.

**Fields**

- `endpoint`: `watermarks.set`
- `quotaCost`: `50`
- `target`: safe target context containing the target channel identity
- `metadata`: safe watermark metadata context
- `upload`: safe upload descriptor containing MIME type and content-present information
- `auth`: safe access context
- `availability`: active or owner-only endpoint state
- `updated`: watermark-update status when available from the wrapper or default sparse success behavior
- `acknowledgment`: mutation or upload acknowledgment details
- `status`: upstream success status details when available

**Validation Rules**

- Successful watermark setting is represented as an acknowledgment, not as refreshed channel branding state, watermark lookup data, media hosting URLs, list/search results, analytics results, or automated branding results.
- The result must preserve target channel identity, watermark metadata context, safe upload context, quota cost, access mode, and mapped operation identity.
- The result must not fabricate refreshed channel metadata, watermark lookup results, media hosting URLs, analytics, recommendations, rankings, summaries, transcript text, enrichment details, or fields not returned by the watermark-set operation.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, extra-field, metadata-only, media-only, rejected-delegation, bulk-watermark, alias-only, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot update the target channel watermark or the caller is not eligible.
- `quota_exhausted`: quota cannot cover the 50-unit operation.
- `resource_not_found`: upstream reports the target channel is unavailable or missing.
- `unsupported_upload`: upload media is missing, malformed, too large, or unsupported.
- `endpoint_unavailable`: watermark-set endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `upstream_failure`: unexpected upstream failure or refusal that cannot be represented more specifically.
- Details must not expose API keys, OAuth tokens, authorization headers, raw media content, raw upstream diagnostics, stack traces, unsafe request context, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, input schema, examples, upload boundary, partner-delegation boundary, and safe error metadata.
2. **Validated**: Caller request passes local checks for `channelId`, `body`, `media`, no extra fields, no delegation, and OAuth availability.
3. **Rejected**: Invalid input, unsupported upload, missing OAuth, insufficient authorization, quota, policy, not-found, deprecated endpoint, upstream refusal, or upstream failure is returned as a safe categorized error.
4. **Updated**: Valid request executes through the Layer 1 wrapper and receives a successful watermark-update acknowledgment.
5. **Reviewed**: Result context is inspectable for endpoint, quota, channel identity, watermark metadata, safe upload descriptor, access context, availability state, and acknowledgment outcome.
