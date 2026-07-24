# Data Model: Layer 2 Tool `videos_reportAbuse`

## Videos Report Abuse Tool

Represents the public Layer 2 MCP tool named `videos_reportAbuse`.

**Fields**

- `name`: `videos_reportAbuse`
- `upstreamResource`: `videos`
- `upstreamMethod`: `reportAbuse`
- `operationKey`: `videos.reportAbuse`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active OAuth mutation operation
- `resourceFamily`: `videos`
- `description`: caller-facing summary including endpoint, quota, OAuth, report body, no-content acknowledgment, partner-delegation boundary, and out-of-scope caveats
- `inputSchema`: request contract for one video abuse-report request
- `responseBoundary`: structured mutation acknowledgment boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `videos.reportAbuse` wrapper from YT-152.
- Uses shared Layer 2 metadata, naming, response, validation, error, mutation-result, and example conventions from YT-201 and YT-202.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Video Abuse Report Request

Represents one caller-provided request to submit an abuse report.

**Fields**

- `body`: required report payload object.
- `body.videoId`: required target video identifier.
- `body.reasonId`: required primary abuse reason identifier.
- `body.secondaryReasonId`: optional secondary abuse reason identifier.
- `body.comments`: optional caller-provided explanatory comments.
- `body.language`: optional language code for report comments or reason context where supported.

**Validation Rules**

- `body` is required and must be an object.
- `body.videoId` is required, non-empty text identifying one target video.
- `body.reasonId` is required, non-empty text identifying one abuse reason.
- `body.secondaryReasonId`, `body.comments`, and `body.language`, when supplied, must be non-empty text within the documented payload boundary.
- Unsupported body fields, unsupported top-level fields, alias-only target or reason fields, partner delegation fields, empty values, malformed values, and out-of-scope workflow fields are rejected before endpoint execution.
- OAuth authorization must be available for every supported request.

## Video Identity

Represents the target video being reported.

**Fields**

- `videoId`: caller-provided YouTube video identifier.

**Validation Rules**

- Exactly one target video ID is required for each report.
- The target ID must be non-empty text.
- Access failures for valid-looking identities must remain distinguishable from missing identity and not-found outcomes.

## Abuse Reason

Represents the primary or secondary reason supplied by the caller.

**Fields**

- `reasonId`: required primary reason identifier.
- `secondaryReasonId`: optional secondary reason identifier.

**Validation Rules**

- The primary reason is required for every report.
- Secondary reason is optional and must remain subordinate to the primary reason.
- Empty, malformed, unsupported, deprecated, or unavailable reason values are invalid when locally detectable, or surfaced as upstream refusal/failure when only the upstream service can determine eligibility.
- Reason discovery is not performed by this tool.

## Abuse Report Details

Represents supported optional body details.

**Fields**

- `comments`: optional explanatory text supplied by the caller.
- `language`: optional language context for the report.

**Validation Rules**

- Optional details must be text values when present.
- Unsupported details must be rejected rather than silently dropped or reinterpreted.
- Safe acknowledgments may preserve only enough detail to identify that optional details were submitted; they must not expose credentials, authorization headers, raw upstream diagnostics, or secret-bearing request context.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `delegation`: absent for this slice because `onBehalfOfContentOwner` remains outside the supported public contract
- `scopes`: caller-facing scope guidance when present in metadata or documentation

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but cannot submit the report produces `authorization_failed`.
- API-key-only access is not a valid state for `videos_reportAbuse`.
- Credentials, authorization headers, raw upstream diagnostics, request context, and secret-bearing details must never be exposed.

## Abuse Report Acknowledgment

Represents a successful `videos_reportAbuse` response.

**Fields**

- `endpoint`: `videos.reportAbuse`
- `quotaCost`: `50`
- `report`: safe report context containing target video identity, submitted reason identifiers, and optional-detail presence
- `auth`: safe access context
- `availability`: active endpoint state
- `acknowledgment`: mutation acknowledgment details

**Validation Rules**

- Successful report submission is represented as an acknowledgment, not as a refreshed video resource, abuse classification, policy decision, evidence record, list/search result, analytics result, or moderation-status result.
- The result must preserve target video identity, submitted reason context, quota cost, access mode, and mapped operation identity.
- The result must not fabricate moderation decisions, abuse classification, evidence, refreshed video metadata, recommendations, rankings, summaries, transcript text, enrichment details, deletion acknowledgments, or fields not returned by the report-abuse operation.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, extra-field, invalid-body, invalid-reason, invalid-optional-field, rejected-delegation, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot submit the report or the caller is not eligible.
- `quota_exhausted`: quota cannot cover the 50-unit operation.
- `resource_not_found`: upstream reports the target video is unavailable or missing.
- `endpoint_unavailable`: report-abuse endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `upstream_failure`: unexpected upstream failure or refusal that cannot be represented more specifically.
- Details must not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, unsafe request context, sensitive report details beyond safe caller context, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, body schema, examples, partner-delegation boundary, and safe error metadata.
2. **Validated**: Caller request passes local checks for `body`, `videoId`, `reasonId`, supported optional body fields, no extra fields, no delegation, and OAuth availability.
3. **Rejected**: Invalid input, missing OAuth, insufficient authorization, quota, policy, not-found, deprecated endpoint, upstream refusal, or upstream failure is returned as a safe categorized error.
4. **Submitted**: Valid request executes through the Layer 1 wrapper and receives a successful no-content acknowledgment.
5. **Reviewed**: Result context is inspectable for endpoint, quota, target video identity, submitted reason, access context, availability state, and acknowledgment outcome.
