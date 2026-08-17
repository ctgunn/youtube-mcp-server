# MCP Contract: `channels_searchContent`

## Purpose

Search publicly searchable video content within one known YouTube channel through a stable, bounded MCP result. This higher-level tool performs direct channel-constrained search and normalizes the public result; it does not enrich records, apply local filters, or perform local ranking.

## Compatibility and Migration

This is an additive public MCP tool. It does not alter an existing public tool name, schema, or result shape, so no client migration is required. Discovery metadata must not include `representativeOnly`.

## Input Contract

```json
{
  "type": "object",
  "required": ["channelId", "query"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["relevance", "date", "viewCount"], "default": "relevance" },
    "language": { "type": "string", "minLength": 1, "description": "Optional BCP 47 language preference used only to refine relevance." }
  }
}
```

The tool additionally enforces trimmed nonblank text, whole-number values distinct from booleans, and a valid BCP 47 tag when `language` is supplied. It accepts no continuation input; each invocation is one bounded search.

## Composition Boundary

| Aspect | Contract |
| --- | --- |
| Kind | `direct_search_normalization` |
| Lower-layer dependency | One `search.list` request through the existing public `search_list` boundary. |
| Search scope | The normalized query is constrained to the requested channel and public video content. |
| Boundedness | Exactly one source search and 1–50 normalized returned items, default 10. |
| Matching | Direct source search; the tool does not perform a second match, enrichment, or filter stage. |
| Ordering | The selected `order` is applied by the source. Usable records retain received source order after first-occurrence de-duplication; no local re-ranking occurs. |
| Language | A supplied BCP 47 tag is a relevance preference only; it does not guarantee that every returned item is in that language. |
| Authentication | Uses configured public-read capability only; no owner-scoped content is requested. |
| Capacity caveat | The one bounded source request consumes available public-search capacity and can fail when capacity is exhausted. |
| Partial-result policy | A successful no-match response is a successful empty result. Malformed, duplicate, or out-of-scope returned records are omitted with safe aggregate disclosure. A failed required search is a whole-request error. |

## Processing Semantics

1. Validate and normalize `channelId`, `query`, `maxResults`, `order`, and optional `language`.
2. Make one direct public video search constrained to the requested channel, using the effective query, cap, ordering, and optional relevance language preference.
3. Read source items in received order. Omit a record lacking a usable video identity or requested-channel association; retain the first usable occurrence of each video identity.
4. Apply the final `maxResults` cap after normalization and duplicate handling.
5. Return the public items, complete applied-input and direct-search context, provenance, and safe aggregate partial-availability context when applicable.

No caller-controlled pagination, content hydration, transcript retrieval, owner-scoped access, local enrichment, local filtering, or local ranking is included. Results can differ across requests as publicly searchable content and source ranking can change.

## Successful Result Contract

```json
{
  "channelId": "UC123",
  "query": "release notes",
  "items": [
    {
      "videoId": "video-123",
      "contentType": "video",
      "title": "Release notes overview",
      "description": "Available public description",
      "publishedAt": "2026-03-01T12:00:00Z",
      "channelId": "UC123",
      "channelTitle": "Example channel",
      "thumbnails": { "medium": "https://example.invalid/thumbnail" }
    }
  ],
  "returnedCount": 1,
  "maxResults": 10,
  "appliedInputs": {
    "channelId": "UC123",
    "query": "release notes",
    "maxResults": 10,
    "order": "relevance",
    "language": "en"
  },
  "searchContext": {
    "source": "channel_constrained_public_video_search",
    "matching": "direct_upstream_search",
    "ordering": "upstream_order",
    "order": "relevance",
    "rankingApplied": false,
    "enrichmentApplied": false,
    "localFilteringApplied": false,
    "publicContentOnly": true,
    "languageRefinesRelevance": true,
    "requestTimeVariability": "search_results_can_change"
  },
  "fieldProvenance": {
    "items.videoId": "raw_upstream",
    "items.contentType": "normalized",
    "items.title": "raw_upstream",
    "items.description": "raw_upstream",
    "items.publishedAt": "raw_upstream",
    "items.channelId": "raw_upstream",
    "items.channelTitle": "raw_upstream",
    "items.thumbnails": "raw_upstream",
    "channelId": "normalized",
    "query": "normalized",
    "returnedCount": "normalized",
    "maxResults": "normalized",
    "appliedInputs": "normalized",
    "searchContext": "normalized"
  }
}
```

Optional item fields appear only when publicly available. A no-match response has `items: []` and `returnedCount: 0` while retaining the complete response context. `language` appears in `appliedInputs` only when supplied.

`partialAvailability`, when applicable, has `status: "partial"`, an aggregate `omittedItemCount`, and safe reason categories only. It never identifies omitted content or exposes raw source details.

## Field Provenance and Direct-Search Disclosure

| Field or group | Provenance | Caller guidance |
| --- | --- | --- |
| `items.videoId`, `items.title`, `items.description`, `items.publishedAt`, `items.channelId`, `items.channelTitle`, `items.thumbnails` | `raw_upstream` | Available public values preserve their source meaning; absent optional fields are not fabricated. |
| `items.contentType` | `normalized` | The value is `video` because this tool's direct search is fixed to public video content. |
| `channelId`, `query`, `returnedCount`, `maxResults`, `appliedInputs`, `searchContext` | `normalized` | Stable context derived from validated input and the bounded direct search. |
| Item sequence | `normalized` ordering rule | Retains usable source order after duplicate handling; source-selected ordering is not locally re-ranked. |
| `partialAvailability` | `normalized` | Safe aggregate completeness context only; it never reveals unavailable content identity or sensitive source detail. |

Use a listing-oriented tool for an uploads-collection view, or another specialized workflow for enrichment or transcript retrieval. This tool is limited to direct query matching within one channel's publicly searchable video content.

## Error Contract

The tool returns safe MCP-compatible errors with a stable category and sanitized details. It never exposes credentials, keys, tokens, stack traces, raw request or response bodies, signed URLs, private owner context, or non-public video data.

| Category | When returned | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Request shape, blank text, field type, result limit, order, or language validation fails. | Correct the identified field and retry. |
| `unavailable_resource` | The requested public search scope cannot be accessed. | Use another accessible channel identifier or retry later. |
| `authorization_sensitive_data` | Configured public access cannot retrieve the required search. | Obtain applicable public-read capability if available. |
| `quota_exhaustion` | Available capacity prevents the required search. | Retry after capacity is available. |
| `upstream_failure` | The required source search fails for another reason. | Retry when the source service is available. |

## Discovery Metadata Requirements

The executable descriptor must expose the exact public schema; default and bounds; `direct_search_normalization` composition boundary; `search.list` as its only lower-layer dependency; one-search boundedness; public-video and requested-channel scope; direct matching and upstream-order semantics; no enrichment/filtering/re-ranking declaration; language-hint limitation; source-versus-normalized field provenance; empty and aggregate partial-availability policies; safe error categories; capacity caveat; and recovery guidance. It must not expose representative-only markers, continuation controls, raw upstream payloads, credentials, or unsafe metadata keys.
