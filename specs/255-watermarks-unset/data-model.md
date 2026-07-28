# Data Model: Layer 2 Tool `watermarks_unset`

## Watermarks Unset Tool

Represents the public Layer 2 MCP tool named `watermarks_unset`.

**Fields**

- `name`: `watermarks_unset`
- `upstreamResource`: `watermarks`
- `upstreamMethod`: `unset`
- `operationKey`: `watermarks.unset`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: owner-only OAuth mutation operation
- `resourceFamily`: `watermarks`
- `description`: caller-facing summary including endpoint, quota, OAuth, required `channelId`, no-upload boundary, sparse acknowledgment, no-removal-possible caveat, partner-delegation boundary, and out-of-scope caveats
- `inputSchema`: request contract for one watermark-unset request
- `responseBoundary`: structured mutation acknowledgment boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `watermarks.unset` wrapper from YT-155.
- Uses shared Layer 2 metadata, naming, response, validation, error, mutation-result, and example conventions from YT-201 and YT-202.
- Lives beside `watermarks_set` in the existing Layer 2 watermarks resource-family module.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Watermark Removal Request

Represents one caller-provided request to remove a channel watermark.

**Fields**

- `channelId`: required target YouTube channel identifier.

**Validation Rules**

- The request must be an object.
- `channelId` is required and must be non-empty text identifying one target channel.
- Ambiguous multi-target values, duplicate target declarations, comma-separated target values, and alias-only target fields are rejected where locally detectable.
- `body`, `media`, watermark placement metadata, watermark display metadata, media-upload content, partner delegation fields, unsupported top-level fields, bulk watermark shapes, empty values, malformed values, and out-of-scope workflow fields are rejected before endpoint execution.
- OAuth authorization must be available for every supported request.

## Channel Context

Represents the target channel whose watermark is being removed.

**Fields**

- `channelId`: caller-provided YouTube channel identifier.

**Validation Rules**

- Exactly one target channel ID is required for each watermark-unset request.
- The target channel ID must be non-empty text.
- Ambiguous multi-target values, duplicate target declarations, or comma-separated values should be rejected where locally detectable.
- Access failures for valid-looking identities must remain distinguishable from missing identity, unavailable channel, and no-removal-possible outcomes.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `delegation`: absent for this slice because `onBehalfOfContentOwner` remains outside the supported public contract
- `scopes`: caller-facing scope guidance when present in metadata or documentation

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but cannot remove the target channel watermark produces `authorization_failed`.
- API-key-only access is not a valid state for `watermarks_unset`.
- Credentials, authorization headers, raw upstream diagnostics, raw media content, request context, and secret-bearing details must never be exposed.

## No-Upload Boundary

Represents the caller-facing guarantee that unset does not accept watermark media or metadata payloads.

**Fields**

- `acceptedMedia`: none
- `acceptedWatermarkMetadata`: none
- `rejectedFields`: `body`, `media`, upload descriptors, timing metadata, position metadata, placement metadata, display metadata, and setting-only fields

**Validation Rules**

- Any supplied `body` or `media` field is rejected as unsupported for `watermarks_unset`.
- Metadata-only, media-only, and mixed set/unset requests are rejected before execution where locally detectable.
- Results, examples, logs, and errors must not expose raw media bytes, private media content, or unsupported supplied upload content.

## Watermark Removal Acknowledgment

Represents a successful `watermarks_unset` response.

**Fields**

- `endpoint`: `watermarks.unset`
- `sourceOperation`: `watermarks.unset`
- `quotaCost`: `50`
- `target`: safe target context containing the target channel identity
- `auth`: safe access context
- `availability`: active or owner-only endpoint state
- `removed`: watermark-removal status when available from the wrapper or default sparse success behavior
- `acknowledgment`: mutation acknowledgment details
- `status`: upstream success status details when available

**Validation Rules**

- Successful watermark removal is represented as an acknowledgment, not as refreshed channel branding state, watermark lookup data, media hosting URLs, list/search results, analytics results, or automated branding results.
- The result must preserve target channel context, quota cost, access mode, and mapped operation identity.
- The result must not fabricate refreshed channel metadata, watermark lookup results, media hosting URLs, analytics, recommendations, rankings, summaries, transcript text, enrichment details, or fields not returned by the watermark-unset operation.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, extra-field, upload-oriented, metadata-oriented, rejected-delegation, bulk-watermark, alias-only, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot remove the target channel watermark or the caller is not eligible.
- `quota_exhausted`: quota cannot cover the 50-unit operation.
- `target_channel_failed`: upstream reports the target channel is unavailable, missing, policy-restricted, or cannot be acted on.
- `no_removal_possible`: target channel has no removable watermark, is already removed, or the upstream indicates there is nothing to unset.
- `endpoint_unavailable`: watermark-unset endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `conflict`: upstream reports a conflict that is distinct from validation and access failures.
- `upstream_refused`: upstream refusal that does not fit a more specific safe category.
- `upstream_failure`: unexpected upstream failure that cannot be represented more specifically.
- Details must not expose API keys, OAuth tokens, authorization headers, raw media content, raw upstream diagnostics, stack traces, unsafe request context, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, input schema, examples, no-upload boundary, partner-delegation boundary, and safe error metadata.
2. **Validated**: Caller request passes local checks for `channelId`, no extra fields, no body/media payload, no delegation, and OAuth availability.
3. **Rejected**: Invalid input, unsupported upload or metadata payload, missing OAuth, insufficient authorization, quota, policy, not-found, no-removal-possible, deprecated endpoint, upstream refusal, or upstream failure is returned as a safe categorized error.
4. **Removed**: Valid request executes through the Layer 1 wrapper and receives a successful watermark-removal acknowledgment.
5. **Reviewed**: Result context is inspectable for endpoint, quota, channel context, access context, availability state, and acknowledgment outcome.
