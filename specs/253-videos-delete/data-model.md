# Data Model: Layer 2 Tool `videos_delete`

## Videos Delete Tool

Represents the public Layer 2 MCP tool named `videos_delete`.

**Fields**

- `name`: `videos_delete`
- `upstreamResource`: `videos`
- `upstreamMethod`: `delete`
- `operationKey`: `videos.delete`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth mutation operation
- `resourceFamily`: `videos`
- `description`: caller-facing summary including endpoint, quota, OAuth, target `id`, no-body rule, destructive-action guidance, no-content acknowledgment, partner-delegation boundary, and out-of-scope caveats
- `inputSchema`: request contract for one video deletion request
- `responseBoundary`: structured mutation acknowledgment boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `videos.delete` wrapper from YT-153.
- Uses shared Layer 2 metadata, naming, response, validation, error, mutation-result, and example conventions from YT-201 and YT-202.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Video Deletion Request

Represents one caller-provided request to delete a target video.

**Fields**

- `id`: required target YouTube video identifier.

**Validation Rules**

- The request must be an object.
- `id` is required and must be non-empty text identifying one target video.
- Request bodies, unsupported top-level fields, alias-only target fields, partner delegation fields, bulk delete shapes, empty values, malformed values, and out-of-scope workflow fields are rejected before endpoint execution.
- OAuth authorization must be available for every supported request.

## Video Identity

Represents the target video being deleted.

**Fields**

- `id`: caller-provided YouTube video identifier.

**Validation Rules**

- Exactly one target video ID is required for each delete request.
- The target ID must be non-empty text.
- Ambiguous multi-target values, duplicate target declarations, or comma-separated values should be rejected where locally detectable.
- Access failures for valid-looking identities must remain distinguishable from missing identity and not-found outcomes.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `delegation`: absent for this slice because `onBehalfOfContentOwner` remains outside the supported public contract
- `scopes`: caller-facing scope guidance when present in metadata or documentation

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but cannot delete the target video produces `authorization_failed`.
- API-key-only access is not a valid state for `videos_delete`.
- Credentials, authorization headers, raw upstream diagnostics, request context, and secret-bearing details must never be exposed.

## Deletion Acknowledgment

Represents a successful `videos_delete` response.

**Fields**

- `endpoint`: `videos.delete`
- `quotaCost`: `50`
- `target`: safe target context containing the target video identity
- `auth`: safe access context
- `availability`: active endpoint state
- `deleted`: deletion status when available from the wrapper or default no-content success behavior
- `acknowledgment`: mutation acknowledgment details
- `status`: no-content success status details

**Validation Rules**

- Successful deletion is represented as an acknowledgment, not as a refreshed video resource, recovery state, list/search result, analytics result, or moderation-status result.
- The result must preserve target video identity, quota cost, access mode, and mapped operation identity.
- The result must not fabricate refreshed video metadata, recovery affordances, analytics, recommendations, rankings, summaries, transcript text, enrichment details, abuse-report outcomes, or fields not returned by the delete operation.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, extra-field, supplied-body, rejected-delegation, bulk-delete, alias-only, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot delete the target video or the caller is not eligible.
- `quota_exhausted`: quota cannot cover the 50-unit operation.
- `resource_not_found`: upstream reports the target video is unavailable or missing.
- `endpoint_unavailable`: delete endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `upstream_failure`: unexpected upstream failure or refusal that cannot be represented more specifically.
- Details must not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, unsafe request context, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, target schema, examples, partner-delegation boundary, destructive-action guidance, and safe error metadata.
2. **Validated**: Caller request passes local checks for `id`, no extra fields, no body, no delegation, and OAuth availability.
3. **Rejected**: Invalid input, missing OAuth, insufficient authorization, quota, policy, not-found, deprecated endpoint, upstream refusal, or upstream failure is returned as a safe categorized error.
4. **Deleted**: Valid request executes through the Layer 1 wrapper and receives a successful no-content acknowledgment.
5. **Reviewed**: Result context is inspectable for endpoint, quota, target video identity, access context, availability state, destructive-action context, and acknowledgment outcome.
