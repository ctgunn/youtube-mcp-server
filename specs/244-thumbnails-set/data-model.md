# Data Model: Layer 2 Thumbnails Set Tool

## Thumbnails Set Tool

Represents the public Layer 2 MCP tool named `thumbnails_set`.

**Fields**
- `name`: Constant public tool name, always `thumbnails_set`.
- `upstreamResource`: YouTube resource name, always `thumbnails`.
- `upstreamMethod`: YouTube method name, always `set`.
- `quotaCost`: Official per-call quota cost, always `50`.
- `authMode`: Public auth disclosure, always `oauth_required`.
- `availabilityState`: Caller-facing endpoint availability state.
- `inputContract`: The schema for one thumbnail-setting request.
- `responseConvention`: The success result shape for a thumbnail-set mutation.
- `examples`: Caller-facing examples for success, sparse success, validation failure, access failure, target-video failure, upload failure, quota/upstream failure, and out-of-scope requests.

**Relationships**
- Uses one Thumbnails Set Request.
- Produces one Thumbnails Set Result or one Thumbnails Set Failure.
- Depends on the Layer 1 `thumbnails.set` wrapper for endpoint behavior.

**Validation Rules**
- Must expose quota cost `50` in metadata, description, usage notes, examples, and result context.
- Must disclose OAuth-required access before invocation.
- Must not advertise thumbnail generation, image editing, video upload, video metadata updates, channel branding, analytics, enrichment, or bulk behavior.

## Thumbnails Set Request

Represents the caller's request to set one video's custom thumbnail.

**Fields**
- `videoId`: Required non-empty video identifier.
- `media`: Required thumbnail upload content descriptor.

**Relationships**
- Supplies the Video Identifier.
- Supplies the Thumbnail Upload Content.
- Is passed to the Layer 1 `thumbnails.set` wrapper after validation.
- Is summarized in the Thumbnails Set Result as safe target and upload context.

**Validation Rules**
- `videoId` is required.
- `videoId` must be non-empty text after trimming.
- `media` is required.
- `media` must satisfy the documented upload boundary.
- No additional public fields are accepted unless explicitly documented by this tool.
- Video metadata bodies, video URLs, search selectors, thumbnail generation prompts, image transformation options, paging controls, analytics flags, ranking flags, summarization flags, and enrichment flags are invalid for this tool.
- The request represents one thumbnail-setting attempt only; no bulk update or preflight lookup is implied.

## Video Identifier

Represents the video whose custom thumbnail the authorized caller is attempting to set.

**Fields**
- `videoId`: The identifier supplied by the caller.

**Relationships**
- Appears in the request.
- Appears in safe result context when thumbnail setting succeeds.
- May appear in safe error details when validation or target-video failures occur.

**Validation Rules**
- Must be provided by the caller.
- Must not be inferred from video URLs, search terms, channel IDs, playlist IDs, or listing selectors.
- Must not expose OAuth credentials, authorization headers, or raw upstream diagnostics.

## Thumbnail Upload Content

Represents the media content supplied for the thumbnail-setting operation.

**Fields**
- `mimeType`: Safe media type descriptor when supplied or classified.
- `content`: Required upload content, represented in examples with placeholder content only.
- `contentProvided`: Safe boolean descriptor used in result context instead of echoing raw upload bytes.

**Relationships**
- Appears in the request.
- Is summarized as safe upload context in the Thumbnails Set Result.
- May produce a Thumbnails Set Failure when missing, malformed, unsupported, or rejected upstream.

**Validation Rules**
- Must be present for every supported thumbnail-setting request.
- Must not be empty, malformed, or ambiguous.
- Raw upload content must never be echoed in success results, errors, logs, metadata, or examples.
- Unsupported or out-of-scope media fields must be rejected before execution when determinable locally.

## Access Context

Represents the safe caller-facing access mode used for thumbnail setting.

**Fields**
- `mode`: Always `oauth_required` for supported thumbnail-setting requests.

**Relationships**
- Required before the Layer 1 wrapper is called.
- Included in success results and safe access failures.

**Validation Rules**
- Missing, invalid, expired, or insufficient OAuth access is categorized as an access failure.
- API-key-only access is not accepted.
- Tokens, authorization headers, and credential material are never returned in results, errors, logs, metadata, or examples.

## Target Video Eligibility

Represents whether the selected video can receive a custom thumbnail through the authorized request.

**Fields**
- `videoId`: The requested target video identifier.
- `eligibilityState`: Safe category such as `eligible`, `missing`, `unavailable`, `not_writable`, `thumbnail_ineligible`, or `unknown_upstream_failure`.
- `reason`: Optional sanitized explanation when available.

**Relationships**
- Derived from validation or normalized upstream feedback.
- Influences Thumbnails Set Result or Thumbnails Set Failure.

**Validation Rules**
- Missing or malformed identifiers are local validation failures, not target-video failures.
- Target-video restrictions must remain distinguishable from missing OAuth and upload validation failures.
- The tool must not perform extra lookup or recovery unless a later feature explicitly adds that behavior.

## Thumbnails Set Result

Represents the complete successful public result for `thumbnails_set`.

**Fields**
- `endpoint`: `thumbnails.set`.
- `quotaCost`: `50`.
- `updated`: Success marker, expected `true`.
- `target`: Object containing safe target context, including `videoId`.
- `upload`: Object containing safe upload context, such as `mimeType` and `contentProvided`, without raw content.
- `auth`: Safe Access Context.
- `upstream`: Optional safe upstream thumbnail-set context.

**Relationships**
- Produced by a valid authorized Thumbnails Set Request.
- Consumed by MCP clients and higher-layer workflows that need direct endpoint thumbnail-setting behavior.

**Validation Rules**
- Must remain near-raw and endpoint-backed.
- Must support sparse upstream success without fabricating thumbnail image details or video metadata.
- Must not include secret-bearing request or auth data.
- Must not include raw upload bytes.

## Thumbnails Set Failure

Represents a safe caller-facing failure instead of a successful thumbnail-set result.

**Fields**
- `category`: Stable failure category such as `invalid_request`, `authentication_failed`, `authorization_failed`, `target_video_failed`, `unsupported_upload`, `upload_rejected`, `quota_exhausted`, `endpoint_unavailable`, `deprecated_endpoint`, or `upstream_failure`.
- `message`: Human-readable safe summary.
- `details`: Optional sanitized structured details, such as `field`, `videoId`, `mimeType`, `reason`, or `authMode`.

**Relationships**
- Produced by validation, missing OAuth, target-video, upload, quota, availability, deprecation, or unexpected upstream failure.

**Validation Rules**
- Must distinguish local validation failures from access failures, target-video failures, upload failures, and upstream failures.
- Must sanitize API keys, OAuth tokens, authorization headers, raw upstream bodies, raw upload content, stack traces, and unsafe request context.
- Target-video and upload-rejection outcomes should be distinguishable from successful thumbnail-set results.

## State Transitions

- `candidate_request` -> `validation_failed`: Missing, empty, malformed, unsupported, or extra fields.
- `validated_request` -> `access_failed`: OAuth access is missing, invalid, expired, or insufficient.
- `validated_request` -> `target_video_failed`: The target video is missing, unavailable, not writable, or custom-thumbnail-ineligible.
- `validated_request` -> `upload_failed`: Upload content is unsupported locally or rejected upstream.
- `validated_request` -> `upstream_failed`: Quota, invalid request, unavailable service, deprecated behavior, or unexpected upstream failure occurs.
- `validated_request` -> `thumbnail_set`: The thumbnail-setting operation succeeds and returns a thumbnail-set result.
