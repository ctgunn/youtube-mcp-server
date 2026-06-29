# Data Model: Layer 2 Tool `guideCategories_list`

## Guide Categories List Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed legacy YouTube `guideCategories.list` retrieval operation.

**Fields**:

- `name`: fixed value `guideCategories_list`.
- `upstream.resource`: fixed value `guideCategories`.
- `upstream.method`: fixed value `list`.
- `upstream.operationKey`: fixed value `guideCategories.list`.
- `quotaCost`: fixed value `1`.
- `authMode`: fixed value `api_key` unless future Layer 1 metadata explicitly expands support.
- `availabilityState`: fixed value `deprecated` unless current platform behavior must be surfaced as `unavailable` for a specific response.
- `inputSchema`: public request schema for one guide-category lookup request.
- `responseBoundary`: near-raw list result boundary.
- `usageNotes`: quota, auth, part, selector, localization, deprecated endpoint, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Guide Categories List Request` as input.
- Produces `Guide Categories List Result` on success.
- Produces `Legacy Availability Outcome` when the platform reports deprecated, removed, or unavailable behavior.
- Depends on the Layer 1 `guideCategories.list` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 1, API-key auth, and deprecated availability in metadata, description, usage notes, and examples.
- Must not claim to list channels, assign channel categories, list video categories, perform search, generate recommendations, rank categories, summarize categories, enrich taxonomy data, or migrate callers to another taxonomy.

## Guide Categories List Request

**Purpose**: Caller-provided request shape for one legacy guide-category lookup attempt.

**Fields**:

- `part`: required non-empty guide-category part selection.
- `regionCode`: optional primary selector for one region-scoped lookup.
- `id`: optional primary selector for one or more guide category identifiers when the Layer 1 dependency supports it.
- `hl`: optional language preference for localized category text when the legacy endpoint accepts it.

**Relationships**:

- Contains exactly one `Guide Category Selector`.
- May include `Localization Context`.
- Requires `Read Authorization Context`.

**Validation Rules**:

- Reject missing or empty `part`.
- Reject requests that omit both `regionCode` and `id`.
- Reject requests that provide both `regionCode` and `id`.
- Reject empty, malformed, duplicate, excessive, unknown, deprecated, removed, or unsupported guide category IDs with safe feedback or no-match categorization.
- Reject empty, malformed, unknown, deprecated, or unsupported region selectors with safe feedback or no-match categorization.
- Reject unsupported request fields, channel-listing filters, channel category assignment requests, video-category lookup requests, search instructions, recommendation instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes.

## Guide Category Selector

**Purpose**: Mutually exclusive lookup mode that determines which guide categories are requested.

**Fields**:

- `mode`: one of `regionCode` or `id`.
- `regionCode`: non-empty region code for region-scoped lookup when `mode` is `regionCode`.
- `id`: comma-delimited or normalized collection of guide category identifiers when `mode` is `id`.

**Relationships**:

- Belongs to `Guide Categories List Request`.
- Determines the selector metadata included in `Guide Categories List Result`.

**Validation Rules**:

- Exactly one selector mode is allowed per request.
- Selector values must be non-empty text.
- ID selectors may include multiple IDs only within the dependency-backed public contract.
- No selector may imply channel lookup, channel category assignment, video-category lookup, search, recommendation, ranking, enrichment, or taxonomy migration.

## Localization Context

**Purpose**: Optional caller language preference and returned localization behavior for guide-category text fields.

**Fields**:

- `hl`: optional language code requested by the caller.
- `effectiveLanguage`: language context reported or inferred from a valid upstream result when safely available.
- `fallbackApplied`: safe indicator that localized text was unavailable and upstream fallback text was preserved.

**Relationships**:

- Optional part of `Guide Categories List Request`.
- Optional part of `Guide Categories List Result`.

**Validation Rules**:

- Missing `hl` means no explicit localization preference.
- Malformed or unsupported `hl` fails validation or maps to the upstream invalid-request category.
- Results must preserve upstream text and must not fabricate translations.

## Read Authorization Context

**Purpose**: API-key-backed caller authorization used for the read-only legacy lookup.

**Fields**:

- `mode`: fixed value `api_key`.
- `eligible`: whether the caller has sufficient API-key-backed access for the request.

**Relationships**:

- Required by every `Guide Categories List Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing API-key credentials map to `authentication_failed` when the dispatcher can distinguish missing credentials.
- Present but insufficient or denied access maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, or raw credential diagnostics.

## Guide Categories List Result

**Purpose**: Successful result for one guide-category list lookup.

**Fields**:

- `endpoint`: fixed value `guideCategories.list`.
- `quotaCost`: fixed value `1`.
- `items`: guide-category resources returned by Layer 1 or upstream.
- `requestedParts`: normalized part selection.
- `selector`: safe region or ID lookup summary.
- `localization`: safe localization context when supplied or returned.
- `availability`: safe deprecated availability summary.
- `kind`, `etag`, `id`, `snippet`: preserved upstream guide-category fields when present.

**Relationships**:

- Produced by `Guide Categories List Tool`.
- Contains or wraps the upstream returned guide-category collection.
- May include `Localization Context` and `Legacy Availability Outcome` metadata.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing guide-category data.
- Preserve empty upstream item collections as successful empty results.
- Do not include unrelated channel listing, channel category assignment, video-category, search, recommendation, ranking, summary, enrichment, analytics, or taxonomy migration data.
- Do not expose secret-bearing request or authorization details.

## Legacy Availability Outcome

**Purpose**: Caller-facing classification for deprecated, removed, or unavailable guide-category platform behavior.

**Fields**:

- `availabilityState`: `deprecated` or `unavailable`.
- `reason`: safe reason such as `deprecated_endpoint`, `removed_resource`, `endpoint_unavailable`, or `current_reference_omission`.
- `message`: caller-facing guidance that the endpoint is legacy and may not be available on the current platform.

**Relationships**:

- May appear in `Guide Categories List Result` when lookup succeeds but remains legacy.
- May appear in safe error details when the platform rejects or no longer supports the method.

**Validation Rules**:

- Must distinguish legacy-unavailable behavior from local validation failures, empty successful results, quota failures, authorization failures, and unexpected upstream failures.
- Must not instruct callers to use unrelated tools as if migration were automatic.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part, missing selector, conflicting selectors, invalid selector/localization, unsupported shape)
  -> Awaiting API-Key Validation
  -> Authentication Failed (missing API key)
  -> Authorization Failed (insufficient or denied access)
  -> Upstream Lookup Attempted
  -> Guide Categories List Result
  -> Empty Successful Result
  -> Legacy Availability Outcome
  -> Upstream Failure (quota, guide category not found, endpoint deprecated/unavailable, unexpected failure)
```
