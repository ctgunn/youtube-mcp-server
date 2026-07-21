# Data Model: Layer 2 Tool `videos_list`

## Videos List Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `videos.list` retrieval operation.

**Fields**:

- `name`: fixed value `videos_list`.
- `upstream.resource`: fixed value `videos`.
- `upstream.method`: fixed value `list`.
- `upstream.operationKey`: fixed value `videos.list`.
- `quotaCost`: fixed value `1`.
- `authMode`: conditional access based on selector; API-key-compatible for `id` and `chart`, OAuth-required for `myRating`.
- `availabilityState`: active unless an upstream response indicates a specific availability problem.
- `inputSchema`: public request schema for one videos-list lookup request.
- `responseBoundary`: near-raw list result boundary.
- `usageNotes`: quota, access, part, selector, pagination, chart-refinement, empty-result, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Videos List Request` as input.
- Produces `Videos List Result` on success.
- Depends on the Layer 1 `videos.list` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 1, conditional access, and active availability in metadata, description, usage notes, and examples.
- Must not claim to search videos, upload media, mutate video metadata, delete videos, change ratings, retrieve transcripts, produce analytics, recommend videos, rank videos, summarize videos, or enrich video data.

## Videos List Request

**Purpose**: Caller-provided request shape for one video-list lookup attempt.

**Fields**:

- `part`: required non-empty video resource part selection.
- `id`: optional selector for one or more direct video identifiers.
- `chart`: optional selector for a supported chart collection.
- `myRating`: optional selector for caller-specific rated-video retrieval.
- `pageToken`: optional pagination token for collection selectors that support traversal.
- `maxResults`: optional page-size control for collection selectors that support traversal.
- `regionCode`: optional chart-only region refinement.
- `videoCategoryId`: optional chart-only category refinement.

**Relationships**:

- Contains exactly one `Video Selector`.
- May include `Pagination Context` for compatible collection selectors.
- May include `Chart Refinement Context` when the selected selector is `chart`.
- Requires `Access Context`.

**Validation Rules**:

- Reject missing, empty, or non-text `part`.
- Reject requests that omit all selectors.
- Reject requests that provide more than one selector from `id`, `chart`, or `myRating`.
- Reject malformed or empty selector values.
- Reject pagination inputs for direct `id` lookup.
- Reject invalid `pageToken` and out-of-range or non-integer `maxResults`.
- Reject `regionCode` or `videoCategoryId` unless `chart` is the active selector.
- Reject unsupported request fields, search text, upload inputs, update inputs, delete inputs, rating mutation inputs, transcript instructions, analytics instructions, recommendation instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes.

## Video Selector

**Purpose**: Mutually exclusive lookup mode that determines which videos are requested.

**Fields**:

- `mode`: one of `id`, `chart`, or `myRating`.
- `id`: comma-delimited or normalized collection of video identifiers when `mode` is `id`.
- `chart`: chart collection name when `mode` is `chart`.
- `myRating`: caller-specific rating view when `mode` is `myRating`.

**Relationships**:

- Belongs to `Videos List Request`.
- Determines the selector metadata included in `Videos List Result`.
- Determines the required `Access Context`.

**Validation Rules**:

- Exactly one selector mode is allowed per request.
- Selector values must be non-empty text.
- `id` lookup uses API-key-compatible access and does not support pagination.
- `chart` lookup uses API-key-compatible access and may use compatible pagination and chart refinements.
- `myRating` lookup requires OAuth-backed access and may use compatible pagination.
- No selector may imply search, upload, update, delete, rating mutation, transcript retrieval, analytics, recommendation, ranking, enrichment, or automatic classification.

## Pagination Context

**Purpose**: Caller-provided and returned page information for supported collection-style selectors.

**Fields**:

- `pageToken`: optional non-empty token supplied by the caller.
- `maxResults`: optional maximum item count within official limits.
- `nextPageToken`: returned token when another page is available.
- `prevPageToken`: returned token when a previous page is available.

**Relationships**:

- Optional part of `Videos List Request` for `chart` and `myRating`.
- Optional part of `Videos List Result` when supplied or returned.

**Validation Rules**:

- Missing pagination fields means the first page or default page size is requested.
- `pageToken` must be non-empty text when supplied.
- `maxResults` must be a valid integer within official limits when supplied.
- Pagination is rejected for direct `id` lookup.

## Chart Refinement Context

**Purpose**: Optional refinement context for chart-based video retrieval.

**Fields**:

- `regionCode`: optional region context for chart lookup.
- `videoCategoryId`: optional category context for chart lookup.

**Relationships**:

- Optional part of `Videos List Request` only when `chart` is the active selector.
- Optional part of `Videos List Result` when supplied.

**Validation Rules**:

- `regionCode` must satisfy the supported regional lookup boundary when supplied.
- `videoCategoryId` must be non-empty when supplied.
- Chart refinements are rejected for `id` and `myRating` selector modes.
- Results must preserve refinement context without claiming chart results apply globally when a regional or category refinement was used.

## Access Context

**Purpose**: Safe caller authorization summary for one videos-list lookup.

**Fields**:

- `mode`: `api_key` for `id` and `chart`, `oauth_required` for `myRating`.
- `path`: `public` for API-key-compatible selectors or `restricted` for caller-specific rating retrieval.
- `eligible`: whether the caller has sufficient access for the selected mode.

**Relationships**:

- Required by every `Videos List Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing API-key credentials for public selectors map to `authentication_failed` when the dispatcher can distinguish missing credentials.
- Missing OAuth credentials for `myRating` map to `authentication_failed`.
- Present but insufficient or denied access maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, authorization headers, signed URLs, stack traces, or raw credential diagnostics.

## Video Resource

**Purpose**: Video item returned by a successful lookup.

**Fields**:

- `kind`: upstream resource kind when present.
- `etag`: upstream entity tag when present.
- `id`: video identifier when present.
- `snippet`: returned snippet fields requested through part selection when present.
- `contentDetails`: returned content details requested through part selection when present.
- `statistics`: returned statistics requested through part selection when present.
- `status`: returned status fields requested through part selection when present.
- Additional returned upstream fields: preserved only when provided by the endpoint and allowed by the near-raw response boundary.

**Relationships**:

- Appears inside `Videos List Result.items`.
- Interpreted with the selected part, selector, access, pagination, and refinement context.

**Validation Rules**:

- Preserve returned fields without fabricating search matches, transcript text, analytics, recommendations, rankings, summaries, mutation status, or enrichment.
- Omitted optional fields remain omitted rather than synthesized.

## Videos List Result

**Purpose**: Successful result for one video-list lookup.

**Fields**:

- `endpoint`: fixed value `videos.list`.
- `quotaCost`: fixed value `1`.
- `items`: video resources returned by Layer 1 or upstream.
- `requestedParts`: normalized part selection.
- `selector`: safe selector summary.
- `pagination`: safe pagination context when supplied or returned.
- `chartRefinement`: safe chart refinement context when supplied.
- `auth`: safe access context.
- `availability`: active availability summary.
- `kind`, `etag`, `pageInfo`, `nextPageToken`, `prevPageToken`: preserved upstream list fields when present.
- `empty`: boolean distinguishing successful empty item collections from populated successes.

**Relationships**:

- Produced by `Videos List Tool`.
- Contains or wraps the upstream returned video collection.
- May include `Pagination Context` and `Chart Refinement Context`.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing video data.
- Preserve empty upstream item collections as successful empty results.
- Do not include unrelated video search, upload, update, delete, rating mutation, transcript, analytics, recommendation, ranking, summary, enrichment, or classification data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part, missing selector, conflicting selectors, invalid selector/refinement/pagination, unsupported shape)
  -> Awaiting Selector-Specific Access Validation
  -> Authentication Failed (missing API key or OAuth credential)
  -> Authorization Failed (insufficient or denied access)
  -> Upstream Lookup Attempted
  -> Videos List Result
  -> Empty Successful Result
  -> Upstream Failure (quota, video not found, invalid request, endpoint unavailable, deprecated behavior, unexpected failure)
```
