# Research: Layer 2 Tool `videoAbuseReportReasons_list`

## Decision: Implement `videoAbuseReportReasons_list` as the concrete Layer 2 tool for `videoAbuseReportReasons.list`

**Rationale**: The YT-245 seed requires exposing `videoAbuseReportReasons.list` as a low-level MCP tool named `videoAbuseReportReasons_list`. The PRD requires one Layer 2 public endpoint-backed tool per supported YouTube Data API resource method, using resource-method naming and near-direct endpoint semantics. The `video_abuse_report_reasons` family is already reserved in the shared family registry, so a concrete video-abuse-report-reasons Layer 2 module is the cohesive place for this tool.

**Alternatives considered**: Add reason lookup behavior to videos or moderation/reporting tools; rejected because `videoAbuseReportReasons.list` is a distinct lookup endpoint and must stay separate from `videos.reportAbuse`, moderation action, report submission, policy interpretation, and higher-level workflows. Keep a representative placeholder only; rejected because YT-245 requires a public endpoint-backed tool.

## Decision: Rely on the existing Layer 1 `build_video_abuse_report_reasons_list_wrapper()`

**Rationale**: YT-145 already provides the Layer 1 `videoAbuseReportReasons.list` wrapper, including endpoint identity, `GET /youtube/v3/videoAbuseReportReasons`, required `part`, required `hl`, API-key access, quota cost `1`, localization guidance, and empty-result handling. YT-245 should expose that capability publicly instead of redefining upstream behavior in Layer 2.

**Alternatives considered**: Implement a direct upstream call inside Layer 2; rejected because Layer 2 tools must depend on Layer 1 wrappers for endpoint behavior. Change Layer 1 as part of YT-245; rejected unless implementation tests later reveal a narrow export, metadata, or validation gap.

## Decision: Support only `part` plus `hl` as required public inputs

**Rationale**: The Layer 1 wrapper and local tool inventory identify `part` and `hl` as the relevant request inputs for deterministic localized abuse-reason lookup. Keeping the request shape to required `part` and required `hl` preserves the existing wrapper boundary, avoids selector ambiguity, and prevents callers from mistaking this tool for video abuse report submission or policy evaluation.

**Alternatives considered**: Accept video identifiers, reason identifiers, report text, paging controls, report payloads, moderation instructions, policy evaluation options, or enrichment flags; rejected because those fields belong to report-submission endpoints, higher-level workflows, or unsupported request shapes. Add implicit default `hl`; rejected because the existing Layer 1 contract requires an explicit display-language value.

## Decision: Use API-key access expectations for every `videoAbuseReportReasons_list` call

**Rationale**: The YT-145 wrapper and local tool inventory mark `videoAbuseReportReasons.list` as API-key based. The public Layer 2 contract must make this access expectation visible in discovery metadata, descriptions, examples, and failure categories while avoiding exposure of actual credential material.

**Alternatives considered**: Require OAuth because the reason catalog supports later reporting workflows; rejected because this slice only retrieves public reason metadata and the Layer 1 wrapper is API-key scoped. Accept mixed/conditional auth; rejected because the local endpoint inventory does not require it for this lookup.

## Decision: Publish official quota cost `1` everywhere the caller evaluates the tool

**Rationale**: The YT-245 seed identifies official quota cost `1`. YT-202 requires quota visibility in metadata, descriptions, and examples. Result context should also carry quota cost so callers can audit direct lookup workflows.

**Alternatives considered**: Put quota only in shared metadata; rejected because the seed explicitly requires tool description/examples to document the cost. Defer quota to external documentation; rejected because clients must understand cost from discovery and contract artifacts alone.

## Decision: Return a near-raw reason-list result with localization and empty-result context

**Rationale**: `videoAbuseReportReasons.list` returns a reason catalog for the requested language view, and valid requests may return zero items. The Layer 2 result should preserve endpoint identity, quota cost, requested parts, requested `hl`, API-key access context, returned items, and safe upstream fields without fabricating translations, policy guidance, report status, moderation outcomes, rankings, summaries, or enrichments.

**Alternatives considered**: Return only the item list; rejected because callers need operation, quota, and localization context. Fabricate fallback labels or policy explanations when localized fields are absent; rejected because the tool must stay near-raw and endpoint-backed. Treat empty item collections as failures; rejected because YT-145 explicitly models empty results as successful outcomes for valid requests.

## Decision: Map validation, access, quota, availability, and upstream failures into safe Layer 2 categories

**Rationale**: The spec requires callers to distinguish malformed requests, missing or invalid access, empty successful results, quota failures, upstream invalid requests, unavailable service responses, deprecated behavior, and unexpected upstream failures. Existing read/list Layer 2 tools map normalized upstream categories to safe caller-facing categories while sanitizing credentials, stack traces, raw request context, and raw diagnostics.

**Alternatives considered**: Pass through raw upstream failures; rejected because the constitution requires secure, deterministic, machine-readable outputs without secret or diagnostic leaks. Collapse empty result, invalid request, and upstream failures into a generic no-result response; rejected because callers need to tell valid empty lookup from a broken or malformed request.

## Decision: Add focused video-abuse-report-reasons family tests and shared registry coverage

**Rationale**: The video-abuse-report-reasons Layer 2 family is not yet concrete, so this slice should add `tests/contract/test_youtube_video_abuse_report_reasons_contract.py`, `tests/unit/test_youtube_video_abuse_report_reasons.py`, and `tests/integration/test_youtube_video_abuse_report_reasons_registration.py`, while also updating common catalog and registration tests. This matches YT-201/YT-202 patterns and proves public discovery, validation, execution, and default registry behavior.

**Alternatives considered**: Place all assertions in shared common tests; rejected because endpoint-specific localization and empty-result behavior deserves a cohesive family test file. Use only unit tests; rejected by the constitution and spec, which require contract, integration, and full-suite validation.

## Decision: Require reStructuredText docstrings for all new or changed Python functions

**Rationale**: Constitution v1.2.0 requires every new or modified Python function to include a reStructuredText docstring covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. YT-245 implementation will likely add or change contract builders, descriptor builders, handlers, validators, result mappers, error mappers, default executor helpers, exports, and fake wrapper methods in tests.

**Alternatives considered**: Add docstrings only to public functions; rejected because the constitution applies to every new or changed Python function. Defer docstrings to review cleanup; rejected because docstrings are a planning and implementation gate.
