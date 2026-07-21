# Data Model: Layer 2 Tool `videoCategories_list`

## Video Categories List Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `videoCategories.list` retrieval operation.

**Fields**:

- `name`: fixed value `videoCategories_list`.
- `upstream.resource`: fixed value `videoCategories`.
- `upstream.method`: fixed value `list`.
- `upstream.operationKey`: fixed value `videoCategories.list`.
- `quotaCost`: fixed value `1`.
- `authMode`: fixed value `api_key` unless future Layer 1 metadata explicitly expands support.
- `availabilityState`: active unless an upstream response indicates a specific availability problem.
- `inputSchema`: public request schema for one video-category lookup request.
- `responseBoundary`: near-raw list result boundary.
- `usageNotes`: quota, auth, part, selector, region, localization, empty-result, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Video Categories List Request` as input.
- Produces `Video Categories List Result` on success.
- Depends on the Layer 1 `videoCategories.list` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 1, API-key auth, and active availability in metadata, description, usage notes, and examples.
- Must not claim to search videos, choose categories automatically, rank categories, summarize categories, provide category analytics, enrich taxonomy data, or classify videos.

## Video Categories List Request

**Purpose**: Caller-provided request shape for one video-category lookup attempt.

**Fields**:

- `part`: required non-empty video-category part selection.
- `regionCode`: optional selector for one region-scoped category catalog lookup.
- `id`: optional selector for one or more video category identifiers.
- `hl`: optional language preference for localized category labels when available.

**Relationships**:

- Contains exactly one `Video Category Selector`.
- May include `Localization Context`.
- Requires `Read Authorization Context`.

**Validation Rules**:

- Reject missing, empty, or non-text `part`.
- Reject requests that omit both `regionCode` and `id`.
- Reject requests that provide both `regionCode` and `id`.
- Reject empty, malformed, duplicate, excessive, unknown, or unsupported video category IDs with safe feedback or no-match categorization.
- Reject empty, malformed, unknown, or unsupported region selectors with safe feedback or no-match categorization.
- Reject malformed or unsupported `hl` when supplied.
- Reject unsupported request fields, paging controls, ordering controls, search text, video identifiers, channel identifiers, analytics instructions, classification instructions, recommendation instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes.

## Video Category Selector

**Purpose**: Mutually exclusive lookup mode that determines which video categories are requested.

**Fields**:

- `mode`: one of `regionCode` or `id`.
- `regionCode`: region code for region-scoped lookup when `mode` is `regionCode`.
- `id`: comma-delimited or normalized collection of video category identifiers when `mode` is `id`.

**Relationships**:

- Belongs to `Video Categories List Request`.
- Determines the selector metadata included in `Video Categories List Result`.

**Validation Rules**:

- Exactly one selector mode is allowed per request.
- Selector values must be non-empty text.
- `regionCode` values must satisfy the supported regional lookup boundary.
- ID selectors may include multiple IDs only within the dependency-backed public contract.
- No selector may imply video search, video lookup, channel lookup, analytics, recommendation, ranking, enrichment, or automatic classification.

## Localization Context

**Purpose**: Optional caller language preference and returned localization behavior for category labels.

**Fields**:

- `hl`: optional language code requested by the caller.
- `effectiveLanguage`: language context reported or inferred from a valid result when safely available.
- `fallbackApplied`: safe indicator that localized text was unavailable and upstream fallback text was preserved.

**Relationships**:

- Optional part of `Video Categories List Request`.
- Optional part of `Video Categories List Result`.

**Validation Rules**:

- Missing `hl` means no explicit display-language preference.
- Malformed or unsupported `hl` fails validation or maps to the upstream invalid-request category.
- Results must preserve upstream text and must not fabricate translations.

## Read Authorization Context

**Purpose**: API-key-backed caller authorization used for the read-only category lookup.

**Fields**:

- `mode`: fixed value `api_key`.
- `eligible`: whether the caller has sufficient API-key-backed access for the request.

**Relationships**:

- Required by every `Video Categories List Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing API-key credentials map to `authentication_failed` when the dispatcher can distinguish missing credentials.
- Present but insufficient or denied access maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, or raw credential diagnostics.

## Video Category Resource

**Purpose**: Category item returned by a successful lookup.

**Fields**:

- `kind`: upstream resource kind when present.
- `etag`: upstream entity tag when present.
- `id`: video category identifier when present.
- `snippet`: returned category fields requested through part selection when present.
- `assignable`: category assignability indicator when returned by the selected parts.
- Additional returned upstream fields: preserved only when provided by the endpoint and allowed by the near-raw response boundary.

**Relationships**:

- Appears inside `Video Categories List Result.items`.
- Interpreted with the selected region, category identifier, part, and localization context.

**Validation Rules**:

- Preserve returned fields without fabricating category labels, assignability guidance, popularity metrics, analytics, rankings, summaries, or enrichment.
- Omitted optional fields remain omitted rather than synthesized.

## Video Categories List Result

**Purpose**: Successful result for one video-category list lookup.

**Fields**:

- `endpoint`: fixed value `videoCategories.list`.
- `quotaCost`: fixed value `1`.
- `items`: video category resources returned by Layer 1 or upstream.
- `requestedParts`: normalized part selection.
- `selector`: safe region or ID lookup summary.
- `localization`: safe localization context when supplied or returned.
- `availability`: active availability summary.
- `kind`, `etag`, `pageInfo`: preserved upstream list fields when present.

**Relationships**:

- Produced by `Video Categories List Tool`.
- Contains or wraps the upstream returned video category collection.
- May include `Localization Context` metadata.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing video-category data.
- Preserve empty upstream item collections as successful empty results.
- Do not include unrelated video search, video metadata, channel, analytics, recommendation, ranking, summary, enrichment, or classification data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part, missing selector, conflicting selectors, invalid selector/localization, unsupported shape)
  -> Awaiting API-Key Validation
  -> Authentication Failed (missing API key)
  -> Authorization Failed (insufficient or denied access)
  -> Upstream Lookup Attempted
  -> Video Categories List Result
  -> Empty Successful Result
  -> Upstream Failure (quota, category not found, invalid request, endpoint unavailable, deprecated behavior, unexpected failure)
```
