# Data Model: YT-229 Layer 2 Tool `playlistImages_insert`

## Playlist Images Insert Tool

**Purpose**: Public Layer 2 MCP tool for OAuth-backed playlist-image insertion through `playlistImages.insert`.

**Fields**:
- `toolName`: Must be `playlistImages_insert`.
- `upstreamResource`: Must be `playlistImages`.
- `upstreamMethod`: Must be `insert`.
- `operationKey`: Must be `playlistImages.insert`.
- `quotaCost`: Must be `50`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Active with OAuth-required playlist-image insertion and media-upload caveats.

**Relationships**:
- Uses one Playlist Images Insert Request.
- Produces one Playlist Images Insert Result or one safe Playlist Images Insert Error.
- Depends on the YT-129 Layer 1 `playlistImages.insert` wrapper.

**Validation Rules**:
- Discovery metadata, descriptions, usage notes, and examples must expose endpoint identity, quota cost, auth mode, required inputs, media-upload boundary, mutation semantics, and unsupported behaviors.
- Public metadata must not include OAuth tokens, raw upload content, raw request context, stack traces, or unsafe diagnostics.

## Playlist Images Insert Request

**Purpose**: Caller-supplied input for one playlist-image insertion operation.

**Fields**:
- `part`: Required string. Determines which playlist image resource sections are returned after creation.
- `body`: Required object. Carries playlist-image creation metadata, including the supported playlist association and creation fields.
- `media`: Required object. Carries supported media-upload content or descriptors for the playlist image.

**Relationships**:
- Part Selection determines returned playlist-image fields.
- Playlist Image Creation Metadata defines the insertion target and creation context.
- Playlist Image Upload Content supplies the image content required for the mutation.
- Authorization Context is required before the request can succeed.

**Validation Rules**:
- Reject missing, blank, malformed, duplicate, unsupported, or conflicting part selections.
- Reject missing, empty, malformed, unsupported, or conflicting `body` metadata.
- Reject `body` metadata that lacks required playlist-image creation fields.
- Reject missing, empty, malformed, inaccessible, oversized, unsupported, or conflicting `media` upload content.
- Reject unsupported request fields, playlist-management fields, analytics fields, ranking fields, summarization fields, enrichment fields, or unrelated endpoint modifiers.
- Reject API-key-only or missing OAuth access before treating the request as a successful playlist-image insertion.

## Part Selection

**Purpose**: Defines which playlist-image resource sections are requested in the creation result.

**Fields**:
- `requestedParts`: Ordered list derived from `part`.

**Validation Rules**:
- Must be present.
- Must not contain unsupported part names.
- Must be preserved in successful results for caller review.

## Playlist Image Creation Metadata

**Purpose**: Represents the playlist-image metadata supplied in `body`.

**Fields**:
- `snippet`: Required supported metadata section for playlist-image insertion.
- `playlistId`: Playlist association when required by the supported metadata contract.
- Other supported playlist-image creation fields only when explicitly allowed by the endpoint contract.

**Validation Rules**:
- Must be object-shaped and non-empty.
- Must include required creation metadata.
- Must not include unsupported fields, unrelated playlist-management instructions, or higher-level workflow directives.
- Safe metadata context may be summarized in results, but sensitive or oversized caller data must not be exposed in errors.

## Playlist Image Upload Content

**Purpose**: Represents the media-upload portion of the request.

**Fields**:
- `mimeType`: Required media type descriptor for the uploaded image.
- `content`: Required upload content or test-safe upload content reference, as supported by the local contract.
- Safe media summary fields such as `mimeType` and content-presence indicators may appear in result context.

**Validation Rules**:
- Must be object-shaped and non-empty.
- Must include supported upload content and media type descriptors.
- Must reject unsupported media types, missing content, inaccessible content, oversized uploads, malformed descriptors, and conflicting upload inputs.
- Raw upload bytes, OAuth tokens, file contents, and secret-bearing details must not appear in public metadata, examples, validation details, or mapped errors.

## Authorization Context

**Purpose**: Represents the OAuth-backed access needed to insert playlist image data.

**Fields**:
- `authMode`: Must be `oauth_required`.
- `accessState`: Safe summary of whether the caller had sufficient OAuth-backed access.

**Validation Rules**:
- API-key-only access is invalid for this tool.
- Missing OAuth and insufficient OAuth access must be distinguishable from malformed requests and upstream insertion failures.
- Public results and errors must not expose secrets or sensitive authorization details.

## Created Playlist Image Resource

**Purpose**: Represents the playlist image record returned after successful insertion.

**Fields**:
- `kind`: Returned resource kind, when present.
- `etag`: Returned resource etag, when present.
- `id`: Created playlist-image identifier, when present.
- `snippet`: Playlist-image descriptive fields, when requested and returned.
- Other returned upstream fields when present.

**Validation Rules**:
- Returned fields must be preserved as received.
- Missing optional fields must not be fabricated.
- No playlist management data, thumbnail activation, playlist item expansion, media transformation, analytics, ranking, summaries, or enrichment should be added to the resource.

## Playlist Images Insert Result

**Purpose**: Successful near-raw response wrapper for playlist-image insertion.

**Fields**:
- `endpoint`: `playlistImages.insert`.
- `quotaCost`: `50`.
- `requestedParts`: Normalized part selection.
- `bodyContext`: Safe metadata summary for the insertion request.
- `mediaContext`: Safe upload summary for the insertion request.
- `auth`: Safe auth-mode summary.
- `item`: Created playlist image resource, when returned as a resource object.
- `kind`: Upstream response kind, when returned.
- `etag`: Upstream etag, when returned.
- `id`: Created playlist-image identifier, when returned.
- `snippet`: Upstream snippet, when returned.

**Validation Rules**:
- Returned fields must be preserved without adding playlist image listing, update, deletion, thumbnail activation, playlist management, analytics, ranking, summarization, enrichment, recommendation, or heuristic classification.
- Missing optional upstream fields must not be fabricated.
- Raw media content must not be echoed in result context.

## Playlist Images Insert Error

**Purpose**: Safe caller-facing failure for invalid, inaccessible, quota, media eligibility, unavailable, or unexpected playlist-image insert outcomes.

**Fields**:
- `category`: One of the shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, or `upstream_failure`.
- `message`: Caller-facing correction or failure summary.
- `details`: Sanitized diagnostic fields such as invalid field name or supported values.

**Validation Rules**:
- Must not include OAuth tokens, API keys, raw media content, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.
- Must distinguish malformed input, auth failure, quota failure, media eligibility failure, missing or inaccessible resources, upstream insertion failure, and successful insertion.

## Quota Disclosure

**Purpose**: Public statement that each invocation costs 50 official quota units.

**Fields**:
- `quotaCost`: `50`.
- `visibleLocations`: Discovery metadata, description, usage notes, examples, and successful result context.

**Validation Rules**:
- Every caller-facing contract surface for this tool must consistently report quota cost `50`.

## Unsupported Boundary Guidance

**Purpose**: Caller-facing explanation of what the low-level playlist-image insertion tool does not do.

**Fields**:
- `unsupportedBehaviors`: Playlist image listing, update, deletion, thumbnail replacement, playlist management, playlist-item expansion, analytics, ranking, summarization, enrichment, recommendation, and cross-endpoint aggregation.

**Validation Rules**:
- Unsupported behaviors must fail clearly or be documented as separate endpoint or higher-level workflow concerns.
- Unsupported behavior guidance must be visible before invocation.
