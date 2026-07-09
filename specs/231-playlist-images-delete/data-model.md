# Data Model: YT-231 Layer 2 Tool `playlistImages_delete`

## Playlist Images Delete Tool

**Purpose**: Public Layer 2 MCP tool for OAuth-backed playlist-image deletion through `playlistImages.delete`.

**Fields**:
- `toolName`: Must be `playlistImages_delete`.
- `upstreamResource`: Must be `playlistImages`.
- `upstreamMethod`: Must be `delete`.
- `operationKey`: Must be `playlistImages.delete`.
- `quotaCost`: Must be `50`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Active with OAuth-required destructive deletion caveats.

**Relationships**:
- Uses one Playlist Images Delete Request.
- Produces one Playlist Images Delete Result or one safe Playlist Images Delete Error.
- Depends on the YT-131 Layer 1 `playlistImages.delete` wrapper.

**Validation Rules**:
- Discovery metadata, descriptions, usage notes, and examples must expose endpoint identity, quota cost, auth mode, required identifier, destructive delete semantics, no-body acknowledgment behavior, and unsupported behaviors.
- Public metadata must not include OAuth tokens, raw request context, stack traces, or unsafe diagnostics.

## Playlist Images Delete Request

**Purpose**: Caller-supplied input for one playlist-image deletion operation.

**Fields**:
- `id`: Required string. Identifies exactly one playlist image to delete.

**Relationships**:
- Playlist Image Identifier selects the target.
- Authorization Context is required before the request can succeed.

**Validation Rules**:
- Reject missing, blank, malformed, duplicate, unsupported, or conflicting identifier values.
- Reject `part`, `body`, `media`, `playlistId`, `pageToken`, `maxResults`, metadata payloads, listing selectors, playlist-management fields, analytics fields, ranking fields, summarization fields, enrichment fields, or unrelated endpoint modifiers.
- Reject API-key-only or missing OAuth access before treating the request as a successful playlist-image deletion.

## Playlist Image Identifier

**Purpose**: Represents the caller-selected target playlist image.

**Fields**:
- `id`: Non-empty playlist image identifier.

**Validation Rules**:
- Must be present.
- Must be string-shaped and non-empty after trimming.
- Must be preserved in successful acknowledgment context for caller review.

## Authorization Context

**Purpose**: Represents the OAuth-backed access needed to delete playlist image data.

**Fields**:
- `authMode`: Must be `oauth_required`.
- `accessState`: Safe summary of whether the caller had sufficient OAuth-backed access.

**Validation Rules**:
- API-key-only access is invalid for this tool.
- Missing OAuth and insufficient OAuth access must be distinguishable from malformed requests and upstream deletion failures.
- Public results and errors must not expose secrets or sensitive authorization details.

## Deleted Playlist Image Target

**Purpose**: Represents the existing playlist image selected for deletion.

**Fields**:
- `id`: Target playlist image identifier from the request.
- `deleted`: Boolean deletion outcome when the delete succeeds.

**Validation Rules**:
- The successful result must identify the target without fabricating full playlist-image resource fields.
- Missing, inaccessible, or already removed targets must remain distinguishable from malformed local input.

## Playlist Images Delete Result

**Purpose**: Successful near-raw response wrapper for playlist-image deletion.

**Fields**:
- `endpoint`: `playlistImages.delete`.
- `quotaCost`: `50`.
- `target`: Safe target context with the deleted playlist image identifier.
- `auth`: Safe auth-mode summary.
- `deleted`: Boolean success indicator.
- `acknowledged`: Boolean indication that no returned resource body is required for success.
- `sourceOperation`: Optional upstream operation identity when returned by Layer 1.

**Validation Rules**:
- The result must provide a clear deletion acknowledgment even when the upstream response has no deleted resource body.
- The result must not fabricate deleted playlist-image resource fields.
- The result must not add playlist image listing, insertion, update, media upload, thumbnail activation, playlist management, analytics, ranking, summarization, enrichment, recommendation, or heuristic classification.

## Playlist Images Delete Error

**Purpose**: Safe caller-facing failure for invalid, inaccessible, quota, missing-resource, unavailable, or unexpected playlist-image deletion outcomes.

**Fields**:
- `category`: One of the shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, or `upstream_failure`.
- `message`: Caller-facing correction or failure summary.
- `details`: Sanitized diagnostic fields such as invalid field name or supported values.

**Validation Rules**:
- Must not include OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.
- Must distinguish malformed input, auth failure, quota failure, missing or inaccessible resources, upstream deletion failure, and successful deletion.

## Quota Disclosure

**Purpose**: Public statement that each invocation costs 50 official quota units.

**Fields**:
- `quotaCost`: `50`.
- `visibleLocations`: Discovery metadata, description, usage notes, examples, and successful result context.

**Validation Rules**:
- Every caller-facing contract surface for this tool must consistently report quota cost `50`.

## Unsupported Boundary Guidance

**Purpose**: Caller-facing explanation of what the low-level playlist-image delete tool does not do.

**Fields**:
- `unsupportedBehaviors`: Playlist image listing, insertion, update, media upload, thumbnail management, playlist management, playlist-item expansion, analytics, ranking, summarization, enrichment, recommendation, and cross-endpoint aggregation.

**Validation Rules**:
- Unsupported behaviors must fail clearly or be documented as separate endpoint or higher-level workflow concerns.
- Unsupported behavior guidance must be visible before invocation.
