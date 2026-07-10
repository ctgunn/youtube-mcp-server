# Data Model: YT-235 Layer 2 Tool `playlistItems_delete`

## Playlist Items Delete Tool

**Purpose**: Public Layer 2 MCP tool for OAuth-backed playlist-item deletion through `playlistItems.delete`.

**Fields**:
- `toolName`: Must be `playlistItems_delete`.
- `upstreamResource`: Must be `playlistItems`.
- `upstreamMethod`: Must be `delete`.
- `operationKey`: Must be `playlistItems.delete`.
- `quotaCost`: Must be `50`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Active with OAuth-required destructive deletion caveats.

**Relationships**:
- Uses one Playlist Items Delete Request.
- Produces one Playlist Items Delete Result or one safe Playlist Items Delete Error.
- Depends on the YT-135 Layer 1 `playlistItems.delete` wrapper.

**Validation Rules**:
- Discovery metadata, descriptions, usage notes, and examples must expose endpoint identity, quota cost, auth mode, required identifier, destructive delete semantics, no-body acknowledgment behavior, and unsupported behaviors.
- Public metadata must not include OAuth tokens, API keys, raw request context, stack traces, or unsafe diagnostics.

## Playlist Items Delete Request

**Purpose**: Caller-supplied input for one playlist-item deletion operation.

**Fields**:
- `id`: Required string. Identifies exactly one playlist item to delete.

**Relationships**:
- Playlist Item Identifier selects the target.
- Authorization Context is required before the request can succeed.

**Validation Rules**:
- Reject missing, blank, malformed, duplicate, unsupported, or conflicting identifier values.
- Reject `part`, `body`, playlist-item metadata payloads, playlist/video assignment data, placement controls, paging controls, listing selectors, playlist-management fields, analytics fields, ranking fields, summarization fields, enrichment fields, or unrelated endpoint modifiers.
- Reject API-key-only or missing OAuth access before treating the request as a successful playlist-item deletion.

## Playlist Item Identifier

**Purpose**: Represents the caller-selected target playlist item.

**Fields**:
- `id`: Non-empty playlist item identifier.

**Validation Rules**:
- Must be present.
- Must be string-shaped and non-empty after trimming.
- Must be preserved in successful acknowledgment context for caller review.

## Authorization Context

**Purpose**: Represents the OAuth-backed access needed to delete playlist item data.

**Fields**:
- `authMode`: Must be `oauth_required`.
- `accessState`: Safe summary of whether the caller had sufficient OAuth-backed access.

**Validation Rules**:
- API-key-only access is invalid for this tool.
- Missing OAuth and insufficient OAuth access must be distinguishable from malformed requests and upstream deletion failures.
- Public results and errors must not expose secrets or sensitive authorization details.

## Deleted Playlist Item Target

**Purpose**: Represents the existing playlist item selected for deletion.

**Fields**:
- `id`: Target playlist item identifier from the request.
- `deleted`: Boolean deletion outcome when the delete succeeds.

**Validation Rules**:
- The successful result must identify the target without fabricating full playlist-item resource fields.
- Missing, inaccessible, unwritable, or already removed targets must remain distinguishable from malformed local input.

## Playlist Items Delete Result

**Purpose**: Successful near-raw response wrapper for playlist-item deletion.

**Fields**:
- `endpoint`: `playlistItems.delete`.
- `quotaCost`: `50`.
- `target`: Safe target context with the deleted playlist item identifier.
- `auth`: Safe auth-mode summary.
- `deleted`: Boolean success indicator.
- `acknowledged`: Boolean indication that no returned resource body is required for success.
- `sourceOperation`: Optional upstream operation identity when returned by Layer 1.

**Validation Rules**:
- The result must provide a clear deletion acknowledgment even when the upstream response has no deleted resource body.
- The result must not fabricate deleted playlist-item resource fields.
- The result must not add playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, automated curation, or heuristic classification.

## Playlist Items Delete Error

**Purpose**: Safe caller-facing failure for invalid, inaccessible, quota, missing-resource, unavailable, deprecated, or unexpected playlist-item deletion outcomes.

**Fields**:
- `category`: One of the shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated`, or `upstream_failure`.
- `message`: Caller-facing correction or failure summary.
- `details`: Sanitized diagnostic fields such as invalid field name or supported values.

**Validation Rules**:
- Must not include OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.
- Must distinguish malformed input, auth failure, quota failure, missing or inaccessible resources, deprecated behavior, upstream deletion failure, and successful deletion.

## Quota Disclosure

**Purpose**: Public statement that each invocation costs 50 official quota units.

**Fields**:
- `quotaCost`: `50`.
- `visibleLocations`: Discovery metadata, description, usage notes, examples, and successful result context.

**Validation Rules**:
- Every caller-facing contract surface for this tool must consistently report quota cost `50`.

## Unsupported Boundary Guidance

**Purpose**: Caller-facing explanation of what the low-level playlist-item delete tool does not do.

**Fields**:
- `unsupportedBehaviors`: Playlist-item listing, insertion, update, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, enrichment, automated curation, and cross-endpoint aggregation.

**Validation Rules**:
- Unsupported behaviors must fail clearly or be documented as separate endpoint or higher-level workflow concerns.
- Unsupported behavior guidance must be visible before invocation.
