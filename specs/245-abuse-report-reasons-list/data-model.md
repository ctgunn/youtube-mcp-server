# Data Model: Layer 2 Tool `videoAbuseReportReasons_list`

## Video Abuse Report Reasons List Tool

Represents the public Layer 2 MCP tool named `videoAbuseReportReasons_list`.

**Fields**
- `name`: Constant public tool name, always `videoAbuseReportReasons_list`.
- `upstreamResource`: YouTube resource name, always `videoAbuseReportReasons`.
- `upstreamMethod`: YouTube method name, always `list`.
- `quotaCost`: Official per-call quota cost, always `1`.
- `authMode`: Public auth disclosure, always `api_key`.
- `availabilityState`: Caller-facing endpoint availability state.
- `inputContract`: The schema for one localized reason-list request.
- `responseConvention`: The success result shape for an abuse-report-reason list lookup.
- `examples`: Caller-facing examples for populated success, empty success, validation failure, access failure, quota/upstream failure, and out-of-scope requests.

**Relationships**
- Uses one Video Abuse Report Reasons List Request.
- Produces one Video Abuse Report Reasons List Result or one Video Abuse Report Reasons List Failure.
- Depends on the Layer 1 `videoAbuseReportReasons.list` wrapper for endpoint behavior.

**Validation Rules**
- Must expose quota cost `1` in metadata, description, usage notes, examples, and result context.
- Must disclose API-key access expectations before invocation.
- Must not advertise abuse report submission, report status lookup, moderation, policy adjudication, ranking, summarization, enrichment, or bulk behavior.

## Video Abuse Report Reasons List Request

Represents the caller's request to retrieve one localized abuse-report-reason catalog.

**Fields**
- `part`: Required non-empty part selection.
- `hl`: Required non-empty display-language input.

**Relationships**
- Supplies the Part Selection.
- Supplies the Display-Language Input.
- Is passed to the Layer 1 `videoAbuseReportReasons.list` wrapper after validation.
- Is summarized in the Video Abuse Report Reasons List Result as safe request, localization, quota, and access context.

**Validation Rules**
- `part` is required.
- `part` must be non-empty text after trimming.
- `hl` is required.
- `hl` must be non-empty text after trimming and must remain within the documented display-language boundary.
- No additional public fields are accepted unless explicitly documented by this tool.
- Video identifiers, reason identifiers, report text, moderation actions, policy evaluation instructions, paging controls, selectors, ranking flags, summarization flags, and enrichment flags are invalid for this tool.
- The request represents one localized reason-catalog lookup only; no report submission or cross-endpoint composition is implied.

## Part Selection

Represents the caller-selected abuse-reason resource sections that determine which reason properties are returned.

**Fields**
- `part`: Caller-provided part selection, represented as one or more non-empty part names.

**Relationships**
- Appears in the request.
- Appears in success result context as selected parts.
- May appear in safe error details when validation fails.

**Validation Rules**
- Must be provided by the caller.
- Must not be inferred from examples, defaults, video identifiers, report payloads, or endpoint-specific heuristics.
- Must not include empty or unsupported selections.

## Display-Language Input

Represents the caller-provided language preference used to request localized abuse-reason labels and descriptions.

**Fields**
- `hl`: Caller-provided display-language value.

**Relationships**
- Appears in the request.
- Appears in Localization Context.
- Influences returned Abuse Report Reason Resources when localized fields are available.

**Validation Rules**
- Must be provided by the caller.
- Must be non-empty text after trimming.
- Must not contain unsupported or ambiguous formatting.
- Missing localized fields in a successful response must not cause fabricated translations.

## Localization Context

Represents the safe caller-facing record of the requested language view.

**Fields**
- `hl`: Requested display-language value.
- `fallback`: Optional safe note when returned fields do not fully match the requested localization.

**Relationships**
- Derived from Display-Language Input.
- Included in Video Abuse Report Reasons List Result.
- Used by callers to understand which language view produced the returned reason catalog.

**Validation Rules**
- Must preserve the caller's requested `hl` value in success context.
- Must not invent translated labels or descriptions.
- Must remain distinct from report-reason classification, ranking, or policy interpretation.

## Abuse Report Reason Resource

Represents one returned reason item that callers may present or validate before separate video-reporting workflows.

**Fields**
- `kind`: Optional returned resource kind.
- `etag`: Optional returned resource tag.
- `id`: Optional returned reason identifier.
- `snippet`: Optional returned reason metadata, such as localized label or description when supplied.

**Relationships**
- Appears within the Video Abuse Report Reasons List Result item collection.
- May be consumed by later reporting workflows outside this slice.

**Validation Rules**
- Preserve returned fields without fabricating missing labels, descriptions, policy details, or moderation outcomes.
- Missing optional fields remain missing rather than becoming validation failures.
- Reason items are lookup data only and do not imply a report has been submitted.

## Video Abuse Report Reasons List Result

Represents the complete successful public result for `videoAbuseReportReasons_list`.

**Fields**
- `endpoint`: `videoAbuseReportReasons.list`.
- `quotaCost`: `1`.
- `requestedParts`: Selected parts derived from `part`.
- `localization`: Localization Context.
- `auth`: Safe access context indicating API-key access expectations.
- `items`: Returned Abuse Report Reason Resources, possibly empty.
- `upstream`: Optional safe upstream list context such as `kind`, `etag`, or paging-like fields if returned.

**Relationships**
- Produced by a valid Video Abuse Report Reasons List Request.
- Consumed by MCP clients and higher-layer workflows that need direct endpoint reason-catalog lookup behavior.

**Validation Rules**
- Must remain near-raw and endpoint-backed.
- Must support empty upstream success without recategorizing it as failure.
- Must not include secret-bearing request or auth data.
- Must not fabricate translations, policy interpretations, moderation outcomes, report-submission status, recommendations, rankings, summaries, or enrichment.

## Video Abuse Report Reasons List Failure

Represents a safe caller-facing failure instead of a successful reason-list result.

**Fields**
- `category`: Stable failure category such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `endpoint_unavailable`, `deprecated_endpoint`, or `upstream_failure`.
- `message`: Human-readable safe summary.
- `details`: Optional sanitized structured details, such as `field`, `quotaCost`, `authMode`, or `reason`.

**Relationships**
- Produced by validation, access, quota, availability, deprecation, or unexpected upstream failure.

**Validation Rules**
- Must distinguish local validation failures from access failures, empty successful results, and upstream failures.
- Must sanitize API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, and unsafe request context.
- Empty successful item collections must not be represented as failures.

## State Transitions

- `candidate_request` -> `validation_failed`: Missing, empty, malformed, unsupported, or extra fields.
- `validated_request` -> `access_failed`: API-key access is missing, invalid, or unavailable.
- `validated_request` -> `upstream_failed`: Quota, invalid request, unavailable service, deprecated behavior, or unexpected upstream failure occurs.
- `validated_request` -> `empty_success`: The lookup succeeds and returns an empty reason collection.
- `validated_request` -> `populated_success`: The lookup succeeds and returns one or more reason resources.
