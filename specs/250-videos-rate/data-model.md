# Data Model: Layer 2 Tool `videos_rate`

## Videos Rate Tool

Represents the public Layer 2 MCP tool named `videos_rate`.

**Fields**

- `name`: `videos_rate`
- `upstreamResource`: `videos`
- `upstreamMethod`: `rate`
- `operationKey`: `videos.rate`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth mutation operation
- `resourceFamily`: `videos`
- `description`: caller-facing summary including endpoint, quota, OAuth, rating-state, no-request-body, acknowledgment-result, and out-of-scope caveats
- `inputSchema`: request contract for one video rating attempt
- `responseBoundary`: structured mutation acknowledgment boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `videos.rate` wrapper from YT-150.
- Uses shared Layer 2 metadata, naming, response, validation, error, mutation, and example conventions from YT-201 and YT-202.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Video Rating Request

Represents one caller-provided request to rate a video.

**Fields**

- `id`: required target video identifier.
- `rating`: required requested rating action. Supported values are `like`, `dislike`, and `none`.

**Validation Rules**

- `id` and `rating` are required for every request.
- `id` must be non-empty text identifying one video.
- `rating` must be exactly one of `like`, `dislike`, or `none`.
- `rating: "none"` explicitly clears the authenticated caller's prior rating and is distinct from an omitted rating.
- Request bodies, extra top-level fields, differently named aliases, empty values, malformed values, unsupported modifiers, and out-of-scope workflow fields are rejected before endpoint execution.
- OAuth authorization must be available for every supported request.

## Video Identity

Represents the target video selected for the rating mutation.

**Fields**

- `id`: required non-empty video identifier.

**Validation Rules**

- Missing, empty, non-text, duplicated, or ambiguous identity values are invalid.
- Access failures for a valid-looking identity must remain distinguishable from missing identity and not-found outcomes.

## Rating Action

Represents the requested rating-state mutation.

**Fields**

- `like`: apply a like rating for the authenticated caller.
- `dislike`: apply a dislike rating for the authenticated caller.
- `none`: remove the authenticated caller's prior rating.

**Validation Rules**

- Missing rating action is invalid.
- Unsupported, empty, differently cased, duplicated, conflicting, or unknown rating actions are invalid.
- The contract must not imply that rating changes alter official aggregate like or dislike counts.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `scopes`: caller-facing scope guidance when present in metadata or documentation

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but cannot rate the target video produces `authorization_failed`.
- API-key-only access is not a valid state for `videos_rate`.
- Credentials, authorization headers, raw upstream diagnostics, request context, and secret-bearing details must never be exposed.

## Video Rating Acknowledgment

Represents a successful `videos_rate` response.

**Fields**

- `endpoint`: `videos.rate`
- `quotaCost`: `50`
- `rating`: safe rating context containing `videoId` and `requestedRating`
- `auth`: safe access context
- `availability`: active endpoint state
- `mutation`: acknowledgment details, with mutation type `rated`
- `status`: optional success status when the implementation records no-content behavior

**Validation Rules**

- Successful rating is represented as an acknowledgment, not as a video resource, list, search result, analytics result, or current-rating lookup.
- The acknowledgment must preserve target video identity, requested rating action, quota cost, access mode, and mapped operation identity.
- The result must not fabricate refreshed video metadata, current-rating lookup results, rating history, aggregate like/dislike counts, analytics, recommendations, rankings, summaries, transcript text, enrichment details, or fields not returned by the rating operation.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, body-bearing, extra-field, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot rate the selected video, the user's email is not verified, the video cannot be rated by the caller, rating is disabled, or policy/access restrictions apply.
- `quota_exhausted`: quota cannot cover the 50-unit operation.
- `resource_not_found`: upstream reports the target video is unavailable or missing.
- `endpoint_unavailable`: rating endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `upstream_failure`: unexpected upstream failure.
- Details must not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, unsafe request context, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, rating-state, no-body, examples, and schema metadata.
2. **Validated**: Caller request passes local checks for `id`, `rating`, no extra fields, no body, and OAuth availability.
3. **Rejected**: Invalid input, missing OAuth, insufficient authorization, quota, policy, disabled rating, not-found, deprecated endpoint, or upstream failure is returned as a safe categorized error.
4. **Rated**: Valid request executes through the Layer 1 wrapper and returns a rating acknowledgment.
5. **Reviewed**: Result context is inspectable for endpoint, quota, target video identity, requested rating action, access context, availability state, and mutation acknowledgment.
