# Data Model: Layer 2 Tool `videos_insert`

## Videos Insert Tool

Represents the public Layer 2 MCP tool named `videos_insert`.

**Fields**

- `name`: `videos_insert`
- `upstreamResource`: `videos`
- `upstreamMethod`: `insert`
- `operationKey`: `videos.insert`
- `quotaCost`: `1600`
- `authMode`: `oauth_required`
- `availabilityState`: media-constrained or limited upload operation
- `resourceFamily`: `videos`
- `description`: caller-facing summary including endpoint, quota, OAuth, media-upload, and caveats
- `inputSchema`: request contract for one video creation attempt
- `responseBoundary`: near-raw upload result boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `videos.insert` wrapper from YT-148.
- Uses shared Layer 2 metadata, naming, response, validation, error, and example conventions from YT-201 and YT-202.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Video Creation Request

Represents one caller-provided request to create a video.

**Fields**

- `part`: required non-empty text identifying requested video resource parts.
- `body`: required video metadata object.
- `media`: required media-upload descriptor object.
- `uploadMode`: optional upload-mode value, limited to supported modes such as `multipart` or `resumable`.
- `notifySubscribers`: optional boolean when supported by the endpoint contract.
- `onBehalfOfContentOwner`: optional delegated content-owner identifier requiring eligible OAuth authorization.

**Validation Rules**

- `part`, `body`, and `media` are required for every request.
- `part` must be non-empty text.
- `body` must be an object and must include the supported metadata shape required by the current Layer 2 contract.
- `media` must be an object and must include the supported safe media descriptor fields required by the current Layer 2 contract.
- `uploadMode`, when supplied, must be one of the supported upload modes.
- `notifySubscribers`, when supplied, must be boolean.
- `onBehalfOfContentOwner`, when supplied, must be non-empty text and must be paired with eligible OAuth authorization.
- Unsupported fields are rejected before endpoint execution.

## Video Metadata

Represents caller-supplied metadata used to create the video resource.

**Fields**

- `snippet`: required metadata section for the primary supported creation path.
- Additional supported resource sections: only those explicitly allowed by the public input contract and selected by `part`.

**Validation Rules**

- Metadata must be present even when media input is present.
- Metadata-only requests are invalid because media upload input is also required.
- Unsupported or read-only metadata fields must be rejected or clearly categorized according to shared Layer 2 validation conventions.

## Media Upload Input

Represents the safe media descriptor for uploaded video content.

**Fields**

- `mimeType`: media type for the uploaded video when required by the supported descriptor.
- `content` or safe content reference: media content or a test-safe media reference accepted by the implementation contract.
- Additional upload descriptor fields: only those explicitly supported by the public contract.

**Validation Rules**

- Media input must be present even when metadata is present.
- Media-only requests are invalid because metadata and part selection are also required.
- Public metadata, examples, logs, and errors must not expose raw media payloads, signed URLs, credentials, or secret-bearing details.

## Upload Context

Represents the safe caller-facing summary of the upload path used for the request.

**Fields**

- `mode`: selected upload mode, when provided.
- `mediaType`: safe media type summary, when provided.
- `hasMedia`: true for validated creation attempts.
- `descriptorFields`: safe list of accepted descriptor fields, without raw payload values.

**Validation Rules**

- Upload context must never include raw video content, signed URLs, secret values, or credential material.
- Unsupported upload modes or descriptor fields produce `invalid_request`.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `delegated`: true when a delegated content-owner context is used

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but lacks permission to create the video produces `authorization_failed`.
- API-key-only access is not a valid state for `videos_insert`.

## Availability Context

Represents caller-facing upload availability and caveats.

**Fields**

- `state`: media-constrained, limited, active-with-caveat, deprecated, unavailable, or closest shared value available.
- `caveats`: safe notes about audit, private-default behavior, release gating, policy constraints, or owner-only behavior.

**Validation Rules**

- Availability caveats must be visible in discovery metadata and examples.
- Policy or availability refusals must be distinguishable from malformed requests and missing OAuth.

## Created Video Resource Result

Represents a successful `videos_insert` response.

**Fields**

- `endpoint`: `videos.insert`
- `quotaCost`: `1600`
- `requestedParts`: normalized requested parts
- `upload`: safe upload context
- `auth`: safe access context
- `availability`: safe availability context
- `delegation`: safe delegation summary when applicable
- `item`: returned created video resource or equivalent upstream payload
- `mutation`: creation outcome details

**Validation Rules**

- Returned video fields are preserved without fabrication.
- Successful creation is not represented as a list.
- The result must not invent publication state, processing state, analytics, recommendations, rankings, summaries, transcript text, thumbnails, captions, playlist membership, or enrichment.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, metadata-only, media-only, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot create the video for the selected account, channel, or delegated owner.
- `quota_exhausted`: quota cannot cover the 1600-unit operation.
- `resource_not_found`: upstream reports a required resource is unavailable or missing.
- `endpoint_unavailable`: upload endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `upstream_failure`: unexpected upstream failure.
- Details must not expose API keys, OAuth tokens, authorization headers, raw media payloads, signed URLs, raw upstream diagnostics, stack traces, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, upload, availability, examples, and schema metadata.
2. **Validated**: Caller request passes local checks for `part`, `body`, `media`, upload mode, optional fields, and OAuth availability.
3. **Rejected**: Invalid input, missing OAuth, insufficient authorization, quota, policy, availability, upload, deprecated endpoint, or upstream failure is returned as a safe categorized error.
4. **Created**: Valid request executes through the Layer 1 wrapper and returns a created video resource result.
5. **Reviewed**: Result context is inspectable for endpoint, quota, requested parts, upload context, access context, availability context, and returned video fields.
