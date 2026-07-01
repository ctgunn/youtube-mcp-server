# Data Model: Layer 2 Tool `i18nRegions_list`

## I18n Regions List Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `i18nRegions.list` retrieval operation.

**Fields**:

- `name`: fixed value `i18nRegions_list`.
- `upstream.resource`: fixed value `i18nRegions`.
- `upstream.method`: fixed value `list`.
- `upstream.operationKey`: fixed value `i18nRegions.list`.
- `quotaCost`: fixed value `1`.
- `authMode`: fixed value `api_key` unless future Layer 1 metadata explicitly expands support.
- `availabilityState`: fixed value `active`.
- `inputSchema`: public request schema for one localization-region lookup request.
- `responseBoundary`: near-raw list result boundary.
- `usageNotes`: quota, auth, part, display-language, active endpoint, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `I18n Regions List Request` as input.
- Produces `I18n Regions List Result` on success.
- Depends on the Layer 1 `i18nRegions.list` wrapper for endpoint behavior.
- Lives in the same Layer 2 localization family as `i18nLanguages_list`.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 1, API-key auth, and active availability in metadata, description, usage notes, and examples.
- Must not claim to look up languages, translate text, validate countries, convert region codes, geotarget content, search content, recommend regions, rank regions, summarize region data, enrich region data, perform analytics, or aggregate across endpoints.

## I18n Regions List Request

**Purpose**: Caller-provided request shape for one localization-region lookup attempt.

**Fields**:

- `part`: required non-empty localization-region part selection. The official supported value for this slice is `snippet`.
- `hl`: optional language preference for returned region names. When omitted, default upstream display-language behavior applies.

**Relationships**:

- May include `Display-Language Context`.
- Requires `Read Authorization Context`.

**Validation Rules**:

- Reject missing or empty `part`.
- Reject unsupported part values.
- Reject empty, malformed, unknown, or unsupported `hl` values with safe feedback or upstream invalid-request categorization.
- Reject unsupported request fields, lookup selectors, paging controls, country validation fields, language filters, search filters, geotargeting instructions, audience analytics instructions, translation instructions, language-lookup instructions, recommendation instructions, ranking instructions, summarization instructions, enrichment instructions, and unsupported retrieval shapes.

## Display-Language Context

**Purpose**: Optional caller language preference and returned localization behavior for region-name text fields.

**Fields**:

- `hl`: optional language code requested by the caller.
- `effectiveLanguage`: language context reported or inferred from a valid upstream result when safely available.
- `defaultApplied`: safe indicator that the caller omitted `hl` and upstream default display-language behavior applied.
- `fallbackApplied`: safe indicator that localized names were unavailable and upstream fallback text was preserved.

**Relationships**:

- Optional part of `I18n Regions List Request`.
- Optional part of `I18n Regions List Result`.

**Validation Rules**:

- Missing `hl` means no explicit display-language preference and default upstream behavior applies.
- Malformed or unsupported `hl` fails validation or maps to the upstream invalid-request category.
- Results must preserve upstream region names and must not fabricate translations.

## Read Authorization Context

**Purpose**: API-key-backed caller authorization used for the read-only localization-region lookup.

**Fields**:

- `mode`: fixed value `api_key`.
- `eligible`: whether the caller has sufficient API-key-backed access for the request.

**Relationships**:

- Required by every `I18n Regions List Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing API-key credentials map to `authentication_failed` when the dispatcher can distinguish missing credentials.
- Present but insufficient or denied access maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, or raw credential diagnostics.

## I18n Region Resource

**Purpose**: One supported YouTube content region returned by the upstream endpoint.

**Fields**:

- `kind`: expected value `youtube#i18nRegion` when present.
- `etag`: upstream resource tag when present.
- `id`: region identifier used by YouTube.
- `snippet.gl`: two-letter region code returned by YouTube.
- `snippet.name`: region name written in the requested or default display language.

**Relationships**:

- Appears in the `items` collection of `I18n Regions List Result`.
- Region codes can be used by callers as reference values for other region-aware YouTube requests, but this tool does not perform those downstream requests.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing region data.
- Do not infer country validity, search availability, video availability, geotargeting reach, popularity, analytics, or ranking from the resource.

## I18n Regions List Result

**Purpose**: Successful result for one localization-region list lookup.

**Fields**:

- `endpoint`: fixed value `i18nRegions.list`.
- `quotaCost`: fixed value `1`.
- `items`: localization-region resources returned by Layer 1 or upstream.
- `requestedParts`: normalized part selection.
- `localization`: safe display-language context when supplied or defaulted.
- `availability`: safe active availability summary.
- `kind`, `etag`: preserved upstream list response fields when present.

**Relationships**:

- Produced by `I18n Regions List Tool`.
- Contains or wraps the upstream returned localization-region collection.
- May include `Display-Language Context` metadata.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing localization-region data.
- Preserve empty upstream item collections as successful empty results.
- Do not include unrelated language lookup, translation, country validation, geotargeting, search filtering, recommendation, ranking, summary, enrichment, analytics, or cross-endpoint data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part, unsupported part, invalid display language, unsupported shape)
  -> Awaiting API-Key Validation
  -> Authentication Failed (missing API key)
  -> Authorization Failed (insufficient or denied access)
  -> Upstream Lookup Attempted
  -> I18n Regions List Result
  -> Empty Successful Result
  -> Upstream Failure (quota, invalid request, endpoint unavailable, unexpected failure)
```
