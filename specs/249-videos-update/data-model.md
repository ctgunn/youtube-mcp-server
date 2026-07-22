# Data Model: Layer 2 Tool `videos_update`

## Videos Update Tool

Represents the public Layer 2 MCP tool named `videos_update`.

**Fields**

- `name`: `videos_update`
- `upstreamResource`: `videos`
- `upstreamMethod`: `update`
- `operationKey`: `videos.update`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active mutation operation with OAuth and writable-part caveats
- `resourceFamily`: `videos`
- `description`: caller-facing summary including endpoint, quota, OAuth, writable-part, update-body, and replacement-semantics caveats
- `inputSchema`: request contract for one video update attempt
- `responseBoundary`: near-raw mutation result boundary
- `examples`: safe caller-facing examples and validation failures

**Relationships**

- Depends on the Layer 1 `videos.update` wrapper from YT-149.
- Uses shared Layer 2 metadata, naming, response, validation, error, mutation, and example conventions from YT-201 and YT-202.
- Is registered in the default MCP tool catalog through the existing dispatcher path.

## Video Update Request

Represents one caller-provided request to update a video.

**Fields**

- `part`: required non-empty text identifying writable video resource parts selected for update.
- `body`: required video resource update body.
- `onBehalfOfContentOwner`: optional delegated content-owner identifier requiring eligible OAuth authorization when supported.

**Validation Rules**

- `part` and `body` are required for every request.
- `part` must be non-empty text and must match supported writable parts.
- The current supported writable part is `snippet`.
- `body` must be an object and must include `id` and `snippet`.
- `body.id` must identify the existing target video.
- `body.snippet.title` is required for the minimum supported update path.
- Unsupported top-level fields are rejected before endpoint execution.
- Unsupported body fields, unsupported snippet fields, read-only fields, media fields, and out-of-scope workflow fields are rejected before endpoint execution.

## Video Identity

Represents the existing video targeted by the update.

**Fields**

- `body.id`: required non-empty video identifier.

**Validation Rules**

- Missing, empty, non-text, malformed, duplicated, or ambiguous identity values are invalid.
- Access failures for a valid-looking identity must remain distinguishable from missing identity and not-found outcomes.

## Writable Part Selection

Represents the video resource section selected for mutation.

**Fields**

- `part`: current supported value `snippet`.

**Validation Rules**

- Missing or empty part selection is invalid.
- Unsupported, read-only, duplicate, conflicting, or unknown parts are invalid.
- Selected parts must match compatible fields in the update body.
- Part-selection guidance must warn callers about replacement-oriented semantics for included sections.

## Update Body

Represents caller-provided fields intended to update the selected writable parts.

**Fields**

- `id`: target video identifier.
- `kind`: optional safe upstream resource hint when accepted by the current contract.
- `snippet.title`: required title value for the current minimum update path.

**Validation Rules**

- `body.id` and `body.snippet.title` are required for the current supported update path.
- `body.snippet` must be an object.
- `body.snippet.title` must be non-empty text.
- Unsupported body fields such as unapproved `status`, `localizations`, or read-only sections are invalid unless the contract deliberately expands.
- Unsupported snippet fields such as unapproved `description`, `tags`, or category fields are invalid unless the contract deliberately expands.

## Update Body Context

Represents the safe caller-facing summary of which update inputs shaped the mutation.

**Fields**

- `videoId`: safe target video identifier.
- `requestedParts`: normalized writable parts selected by the caller.
- `bodyFields`: safe list of accepted body fields.
- `snippetFields`: safe list of accepted snippet fields.

**Validation Rules**

- Context must not include credentials, authorization headers, raw upstream diagnostics, stack traces, unsafe request context, or secret-bearing details.
- Context must not claim unsupported or omitted fields were updated.

## Access Context

Represents OAuth access state without exposing credentials.

**Fields**

- `mode`: `oauth_required`
- `path`: `restricted`
- `delegated`: true when a delegated content-owner context is used

**Validation Rules**

- Missing or unusable OAuth produces `authentication_failed`.
- OAuth that exists but lacks permission to update the selected video produces `authorization_failed`.
- API-key-only access is not a valid state for `videos_update`.

## Updated Video Resource Result

Represents a successful `videos_update` response.

**Fields**

- `endpoint`: `videos.update`
- `quotaCost`: `50`
- `requestedParts`: normalized requested parts
- `update`: safe update body context
- `auth`: safe access context
- `delegation`: safe delegation summary when applicable
- `item`: returned updated video resource or equivalent upstream payload
- `mutation`: update outcome details

**Validation Rules**

- Returned video fields are preserved without fabrication.
- Successful update is not represented as a list.
- The result must not invent media state, upload state, publication workflow state, analytics, recommendations, rankings, summaries, transcript text, thumbnails, captions, playlist membership, comments, or enrichment.

## Error Outcome

Represents a safe caller-facing failure.

**Fields**

- `category`: stable shared error category
- `message`: caller-facing guidance
- `details`: sanitized field and context information

**Validation Rules**

- `invalid_request`: malformed, missing, unsupported, ambiguous, read-only, part/body-mismatched, or out-of-scope request.
- `authentication_failed`: missing or unusable OAuth credentials.
- `authorization_failed`: credentials exist but cannot update the video for the selected account, channel, or delegated owner.
- `quota_exhausted`: quota cannot cover the 50-unit operation.
- `resource_not_found`: upstream reports the target video is unavailable or missing.
- `endpoint_unavailable`: update endpoint is unavailable.
- `deprecated_endpoint`: upstream reports deprecated behavior.
- `upstream_failure`: unexpected upstream failure.
- Details must not expose API keys, OAuth tokens, authorization headers, raw upstream diagnostics, stack traces, unsafe request context, or secrets.

## State Transitions

1. **Discovered**: Tool appears in public discovery with identity, quota, OAuth, writable-part, update-body, replacement-semantics, examples, and schema metadata.
2. **Validated**: Caller request passes local checks for `part`, `body.id`, writable fields, optional delegation, and OAuth availability.
3. **Rejected**: Invalid input, missing OAuth, insufficient authorization, quota, policy, not-found, deprecated endpoint, or upstream failure is returned as a safe categorized error.
4. **Updated**: Valid request executes through the Layer 1 wrapper and returns an updated video resource result.
5. **Reviewed**: Result context is inspectable for endpoint, quota, requested parts, update body context, access context, optional delegation context, and returned video fields.
