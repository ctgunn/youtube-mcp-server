# Data Model: FND-014 Deep Research Tool Foundation

## Entity: SearchRequest
Description: The consumer-provided discovery input sent to the `search` tool.

Fields:
- `query` (string, required): The natural-language or keyword search text used to discover candidate sources.
- `pageSize` (integer, optional): The maximum number of results requested for one discovery page.
- `cursor` (string, optional): The pagination token used to continue a prior discovery result set.

Validation rules:
- `query` MUST be present, non-empty, and trimmed before execution.
- `pageSize`, when provided, MUST be a positive integer within the documented discovery limit.
- `cursor`, when provided, MUST be syntactically valid for the retrieval contract or the request is rejected as invalid.

## Entity: SearchResult
Description: One candidate source returned by the `search` tool for downstream evaluation and follow-up retrieval.

Fields:
- `resourceId` (string, required): The stable search-derived reference that can be passed to `fetch`.
- `uri` (string, required): The canonical source identifier for the discovered result.
- `title` (string, required): The source title shown to the consumer.
- `snippet` (string, optional): A short content preview used to decide whether retrieval is worthwhile.
- `sourceName` (string, optional): Human-readable source or publisher label when available.
- `position` (integer, required): The result order within the current page.

Validation rules:
- `resourceId` MUST be stable for immediate follow-up retrieval and MUST map to the same canonical source as `uri`.
- `uri` MUST be valid and consumable by the retrieval contract.
- Result ordering MUST be deterministic for the same request and response page.
- Duplicate results, if returned, MUST remain distinguishable by `resourceId` and `uri`.

## Entity: SearchResultsPage
Description: The complete logical payload returned by `search`.

Fields:
- `results` (list of SearchResult, required): Ordered candidate sources for the current request.
- `nextCursor` (string, optional): Continuation token for the next discovery page.
- `totalReturned` (integer, required): Count of results in the current page.

Validation rules:
- A no-results outcome MUST return an empty `results` list and MUST NOT be represented as an error.
- `nextCursor` MUST be absent when no additional page exists.
- `totalReturned` MUST match the number of items in `results`.

## Entity: FetchRequest
Description: The consumer-provided retrieval input sent to the `fetch` tool.

Fields:
- `resourceId` (string, conditionally required): The stable search-derived reference for a discovered result.
- `uri` (string, conditionally required): The canonical source identifier used as an equivalent retrieval target.

Validation rules:
- At least one of `resourceId` or `uri` MUST be present.
- If both are provided, they MUST refer to the same canonical source or the request is rejected as invalid.
- A malformed, expired, or unknown retrieval target MUST return a stable retrieval failure rather than partial content.

## Entity: FetchedContent
Description: The logical retrieval payload returned by `fetch` for one selected source.

Fields:
- `resourceId` (string, optional): The stable reference associated with the retrieved source when available.
- `uri` (string, required): The canonical source identifier that was retrieved.
- `title` (string, optional): The retrieved source title.
- `content` (string, required): The consumable text body returned for downstream reasoning.
- `excerpt` (string, optional): A short preview or leading passage used for quick inspection.
- `contentType` (string, optional): High-level content classification for the retrieved source.
- `retrievalStatus` (string, required): Outcome summary such as complete or partial.

Validation rules:
- Successful fetches MUST include `uri`, `content`, and `retrievalStatus`.
- Partial retrieval MUST be explicit in `retrievalStatus` rather than implied.
- Fetched content MUST stay attributable to the selected source through `resourceId`, `uri`, or both.

## Entity: RetrievalFailure
Description: The structured error context returned when discovery or retrieval cannot complete successfully.

Fields:
- `category` (string, required): Stable failure group such as invalid_input, unavailable_source, or upstream_failure.
- `message` (string, required): Consumer-safe description of the failure.
- `details` (object, optional): Additional non-sensitive context for correction or troubleshooting.

Validation rules:
- Failure categories MUST be stable across local and hosted flows for the same logical problem.
- Failure details MUST never expose secrets, stack traces, or internal-only diagnostics.
- Empty discovery results MUST not use this entity.

## Entity: HostedVerificationEvidence
Description: The operator-facing record that proves `search` and `fetch` are discoverable and callable through the hosted MCP endpoint.

Fields:
- `discoveryEvidence` (object, required): Proof that `tools/list` exposes `search` and `fetch`.
- `searchEvidence` (object, required): Proof of one successful and one failing or empty `search` invocation.
- `fetchEvidence` (object, required): Proof of one successful and one failing `fetch` invocation.
- `requestIds` (list of string, required): Correlatable hosted request identifiers captured during verification.

Validation rules:
- Hosted verification MUST cover both discovery and invocation.
- Evidence MUST be sufficient to distinguish success, empty results, and failure cases.
- Request identifiers MUST be capturable without exposing sensitive input values.

## Relationships

- `SearchRequest` produces one `SearchResultsPage`.
- `SearchResultsPage` contains zero or more `SearchResult` values.
- `SearchResult` provides the follow-up identifier for `FetchRequest`.
- `FetchRequest` resolves to either one `FetchedContent` value or one `RetrievalFailure`.
- `HostedVerificationEvidence` references outcomes from both `SearchResultsPage` and `FetchedContent` flows.

## State Transitions

1. Consumer submits `SearchRequest` -> request validates or returns `RetrievalFailure` with `invalid_input`.
2. Valid `SearchRequest` executes -> service returns `SearchResultsPage` with one or more `SearchResult` values or an empty `results` list.
3. Consumer selects one `SearchResult` -> client forms `FetchRequest` using `resourceId`, `uri`, or both.
4. Valid `FetchRequest` executes -> service returns `FetchedContent` or `RetrievalFailure` with unavailable or upstream categories.
5. Operator runs hosted verification -> `HostedVerificationEvidence` records discovery, search, and fetch outcomes for release readiness.
