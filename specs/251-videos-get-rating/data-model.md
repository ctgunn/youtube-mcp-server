# Data Model: Layer 2 Tool `videos_getRating`

## Videos Get Rating Tool

Represents the public Layer 2 MCP tool named `videos_getRating`.

**Fields**

- `name`: `videos_getRating`
- `upstreamResource`: `videos`
- `upstreamMethod`: `getRating`
- `operationKey`: `videos.getRating`
- `quotaCost`: `1`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth read operation
- `resourceFamily`: `videos`
- `description`: caller-facing summary including endpoint, quota, OAuth, identifier, no-request-body, returned rating-state, and out-of-scope caveats
- `inputSchema`: request contract for one video rating lookup request
- `responseBoundary`: structured per-video rating lookup boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `videos.getRating` wrapper from YT-151.
- Uses shared Layer 2 metadata, naming, response, validation, error, read-result, and example conventions from YT-201 and YT-202.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Video Rating Lookup Request

Represents one caller-provided request to retrieve viewer rating state.

**Fields**

- `id`: required comma-separated video identifier list.
- `onBehalfOfContentOwner`: optional partner-only delegation context when eligible OAuth access supports it.

**Validation Rules**

- `id` is required for every request.
- `id` must be non-empty text containing one to fifty unique comma-separated video identifiers.
- Duplicate, empty, malformed, ambiguous, or over-limit identifier sets are invalid.
- `onBehalfOfContentOwner`, if exposed, must be non-empty text and is valid only for eligible partner OAuth contexts.
- Request bodies, extra top-level fields, differently named aliases, empty values, malformed values, unsupported modifiers, rating mutation fields, and out-of-scope workflow fields are rejected before endpoint execution.
- OAuth authorization must be available for every supported request.

## Video Identity Set

Represents the requested target videos selected for rating lookup.

**Fields**

- `requestedIds`: ordered list of requested video identifiers.
- `rawId`: original comma-separated identifier string accepted by the endpoint-shaped contract.
- `count`: number of requested video identifiers.
- `identifierLimit`: maximum supported identifier count, expected to remain `50`.

**Validation Rules**

- At least one requested video ID is required.
- No more than fifty requested video IDs are allowed.
- Duplicate requested video IDs are invalid unless the implementation explicitly documents a deterministic normalization rule.
- Access failures for valid-looking identities must remain distinguishable from missing identity and not-found outcomes.

## Rating State Outcome

Represents one per-video returned viewer rating state.

**Fields**

- `videoId`: video identifier returned for the rating entry.
- `rating`: returned viewer rating state.
- `isRated`: whether the returned rating indicates the viewer has an active like or dislike.
- `isUnrated`: whether the returned rating indicates no current viewer rating.

**Validation Rules**

- Each successful rating entry must include the returned video ID.
- Supported returned ratings include `like`, `dislike`, `none`, and `unspecified`.
- `none` and `unspecified` are successful lookup states, not failures.
- Successful unrated entries must remain distinct from omitted entries, not-found failures, access failures, and upstream failures.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `delegation`: optional safe indication that eligible content-owner delegation was requested
- `scopes`: caller-facing scope guidance when present in metadata or documentation

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but cannot retrieve rating state for the selected videos produces `authorization_failed`.
- API-key-only access is not a valid state for `videos_getRating`.
- Credentials, authorization headers, raw upstream diagnostics, request context, and secret-bearing details must never be exposed.

## Video Rating Lookup Result

Represents a successful `videos_getRating` response.

**Fields**

- `endpoint`: `videos.getRating`
- `quotaCost`: `1`
- `lookup`: safe lookup context containing requested IDs and result count
- `auth`: safe access context
- `availability`: active endpoint state
- `items`: per-video rating entries
- `kind`: optional upstream response resource kind if preserved safely
- `etag`: optional upstream response validator if preserved safely

**Validation Rules**

- Successful lookup is represented as per-video rating state, not as a mutation acknowledgment, video resource, list/search result, analytics result, or aggregate engagement result.
- The result must preserve requested video identities, returned rating states, quota cost, access mode, and mapped operation identity.
- The result must not fabricate rating history, aggregate like/dislike counts, refreshed video metadata, recommendations, rankings, summaries, transcript text, enrichment details, mutation acknowledgments, or fields not returned by the rating lookup operation.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, body-bearing, extra-field, duplicate-ID, over-limit-ID, invalid-delegation, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot retrieve rating state for the selected videos or partner delegation is not permitted.
- `quota_exhausted`: quota cannot cover the 1-unit operation.
- `resource_not_found`: upstream reports requested videos are unavailable or missing.
- `endpoint_unavailable`: rating lookup endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `upstream_failure`: unexpected upstream failure.
- Details must not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, unsafe request context, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, identifier, no-body, examples, and schema metadata.
2. **Validated**: Caller request passes local checks for `id`, unique identifier count, optional delegation, no extra fields, no body, and OAuth availability.
3. **Rejected**: Invalid input, missing OAuth, insufficient authorization, quota, policy, not-found, deprecated endpoint, or upstream failure is returned as a safe categorized error.
4. **Looked Up**: Valid request executes through the Layer 1 wrapper and returns per-video rating outcomes.
5. **Reviewed**: Result context is inspectable for endpoint, quota, requested video identities, returned ratings, access context, availability state, and lookup outcome.
