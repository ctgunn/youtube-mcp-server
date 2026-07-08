# Data Model: YT-228 Layer 2 Tool `playlistImages_list`

## Playlist Images List Tool

**Purpose**: Public Layer 2 MCP tool for OAuth-backed playlist-image retrieval through `playlistImages.list`.

**Fields**:
- `toolName`: Must be `playlistImages_list`.
- `upstreamResource`: Must be `playlistImages`.
- `upstreamMethod`: Must be `list`.
- `operationKey`: Must be `playlistImages.list`.
- `quotaCost`: Must be `1`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Active with OAuth-required playlist-image access caveats.

**Relationships**:
- Uses one Playlist Images List Request.
- Produces one Playlist Images List Result or one safe Playlist Images List Error.
- Depends on the YT-128 Layer 1 `playlistImages.list` wrapper.

**Validation Rules**:
- Discovery metadata, descriptions, usage notes, and examples must expose endpoint identity, quota cost, auth mode, supported inputs, selector rules, paging boundaries, and unsupported behaviors.
- Public metadata must not include OAuth tokens, raw request context, stack traces, or unsafe diagnostics.

## Playlist Images List Request

**Purpose**: Caller-supplied input for one playlist-image list operation.

**Fields**:
- `part`: Required string. Determines which playlist image resource sections are returned.
- `playlistId`: Optional string selector for playlist-scoped image lookup.
- `id`: Optional string selector for direct playlist-image lookup.
- `pageToken`: Optional non-empty string supported only with `playlistId`.
- `maxResults`: Optional integer supported only with `playlistId`.

**Relationships**:
- Part Selection determines returned playlist-image fields.
- Playlist Image Lookup Selector determines retrieval mode.
- Authorization Context is required before the request can succeed.

**Validation Rules**:
- Reject missing, blank, malformed, duplicate, unsupported, or conflicting part selections.
- Require exactly one selector from `playlistId` or `id`.
- Reject missing selectors and conflicting selectors.
- Reject paging fields for `id` lookup.
- Reject empty page tokens, non-integer page sizes, out-of-range page sizes, unsupported fields, request bodies, mutation fields, media upload fields, analytics fields, ranking, summarization, and enrichment.
- Reject API-key-only or missing OAuth access before treating the request as a successful playlist-image list call.

## Part Selection

**Purpose**: Defines which playlist-image resource sections are requested.

**Fields**:
- `requestedParts`: Ordered list derived from `part`.

**Validation Rules**:
- Must be present.
- Must not contain unsupported part names.
- Must be preserved in successful results for caller review.

## Playlist Image Lookup Selector

**Purpose**: Defines the retrieval mode for one `playlistImages_list` request.

**Fields**:
- `selectorName`: Either `playlistId` or `id`.
- `selectorValue`: Non-empty caller-supplied selector value.
- `pagingSupported`: True only for `playlistId`.

**Validation Rules**:
- Exactly one selector must be present.
- `playlistId` mode may include `pageToken` and `maxResults`.
- `id` mode must reject `pageToken` and `maxResults`.
- Selector context must be preserved in successful results.

## Authorization Context

**Purpose**: Represents the OAuth-backed access needed to retrieve playlist image data.

**Fields**:
- `authMode`: Must be `oauth_required`.
- `accessState`: Safe summary of whether the caller had sufficient OAuth-backed access.

**Validation Rules**:
- API-key-only access is invalid for this tool.
- Missing OAuth and insufficient OAuth access must be distinguishable from malformed requests and successful empty results.
- Public results and errors must not expose secrets or sensitive authorization details.

## Playlist Image Resource

**Purpose**: Represents one returned playlist image visible for the selected lookup.

**Fields**:
- `kind`: Returned resource kind, when present.
- `etag`: Returned resource etag, when present.
- `id`: Playlist-image identifier, when present.
- `snippet`: Playlist-image descriptive fields, when requested and returned.

**Validation Rules**:
- Returned fields must be preserved as received.
- Missing optional fields must not be fabricated.
- No playlist management data, playlist item expansion, media transformation, analytics, ranking, summaries, or enrichment should be added to the resource.

## Playlist Images List Result

**Purpose**: Successful near-raw response wrapper for playlist-image collections.

**Fields**:
- `endpoint`: `playlistImages.list`.
- `quotaCost`: `1`.
- `requestedParts`: Normalized part selection.
- `selector`: Safe selector summary with selector name and value.
- `paging`: Safe paging context when applicable.
- `auth`: Safe auth-mode summary.
- `items`: Returned playlist image resources, possibly empty.
- `kind`: Upstream response kind, when returned.
- `etag`: Upstream etag, when returned.
- `nextPageToken`: Upstream continuation token, when returned.
- `prevPageToken`: Upstream previous-page token, when returned.
- `pageInfo`: Upstream page information, when returned.

**Validation Rules**:
- Empty `items` is a successful result when request shape and access are valid.
- Returned fields must be preserved without adding playlist image mutation, media upload, playlist management, analytics, ranking, summarization, enrichment, recommendation, or heuristic classification.
- Missing optional upstream fields must not be fabricated.

## Playlist Images List Error

**Purpose**: Safe caller-facing failure for invalid, inaccessible, quota, unavailable, or unexpected playlist-image list outcomes.

**Fields**:
- `category`: One of the shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, or `upstream_failure`.
- `message`: Caller-facing correction or failure summary.
- `details`: Sanitized diagnostic fields such as invalid field name or supported values.

**Validation Rules**:
- Must not include OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.
- Must distinguish malformed input, auth failure, missing or inaccessible resources, empty successful results, and upstream failures.

## Quota Disclosure

**Purpose**: Public statement that each invocation costs 1 official quota unit.

**Fields**:
- `quotaCost`: `1`.
- `visibleLocations`: Discovery metadata, description, usage notes, examples, and successful result context.

**Validation Rules**:
- Every caller-facing contract surface for this tool must consistently report quota cost `1`.

## Unsupported Boundary Guidance

**Purpose**: Caller-facing explanation of what the low-level playlist-image listing tool does not do.

**Fields**:
- `unsupportedBehaviors`: Playlist image insertion, update, deletion, media upload, thumbnail replacement, playlist management, playlist-item expansion, analytics, ranking, summarization, enrichment, recommendation, and cross-endpoint aggregation.

**Validation Rules**:
- Unsupported behaviors must fail clearly or be documented as separate endpoint or higher-level workflow concerns.
- Unsupported behavior guidance must be visible before invocation.
