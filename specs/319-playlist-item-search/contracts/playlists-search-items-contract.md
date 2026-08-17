# MCP Tool Contract: `playlists_searchItems`

## Purpose

Search accessible items in one playlist using an explainable, case-insensitive literal phrase match. This is a composite higher-level tool; it does not pass a single source response through unchanged.

## Request Contract

```json
{
  "playlistId": "PL123",
  "query": "climate science",
  "maxResults": 25
}
```

| Field | Required | Contract |
| --- | --- | --- |
| `playlistId` | Yes | Non-empty text after trimming. |
| `query` | Yes | Non-empty text after trimming. Repeated internal whitespace is collapsed. |
| `maxResults` | No | Whole number from 1 through 50. Defaults to 25. |

The request object permits no additional fields. It does not accept a pagination or continuation value.

## Matching Contract

- The normalized query is compared as a literal phrase using Unicode case-insensitive matching.
- A source item matches when its available `title`, `description`, `channelTitle`, or `videoId` contains the normalized query.
- The response identifies every available matched field in this fixed order: `title`, `description`, `channelTitle`, `videoId`.
- The tool does not provide semantic, synonym, fuzzy, transcript, or relevance-ranked search.
- Matches remain in ascending playlist position; no ranking or reordering is applied.

## Successful Result Contract

```json
{
  "playlistId": "PL123",
  "query": "climate science",
  "items": [
    {
      "position": 4,
      "playlistItemId": "PLI456",
      "videoId": "VID789",
      "title": "Climate Science Explained",
      "description": "A beginner overview",
      "channelId": "UC456",
      "channelTitle": "Example Lab",
      "publishedAt": "2026-01-15T12:00:00Z",
      "availabilityState": "available",
      "matchingFields": ["title"]
    }
  ],
  "returnedCount": 1,
  "appliedLimit": 25,
  "searchCoverage": {
    "inspectedEntryCount": 42,
    "isComplete": true,
    "terminationReason": "end_of_playlist"
  },
  "additionalMatchesOmitted": false,
  "searchContext": {
    "matching": "case_insensitive_literal_phrase",
    "searchableFields": ["title", "description", "channelTitle", "videoId"],
    "ordering": "source_playlist_order_at_request_time",
    "rankingApplied": false,
    "excludedSearchTypes": ["semantic", "synonym", "fuzzy", "transcript"]
  },
  "fieldProvenance": {}
}
```

### Result Rules

- At most 50 matches are returned. `returnedCount` equals the number of entries in `items`.
- The tool inspects at most 500 accessible playlist entries. `isComplete` is false only when the inspection cap is reached before the end of the playlist.
- `additionalMatchesOmitted` is true only when a further match has been observed beyond the result limit; false only when complete coverage proves no match was omitted; otherwise it is null.
- A no-match result and an accessible empty playlist are successful results with an empty `items` array. They are distinguishable from a failed availability lookup by the absence of an error.
- An unavailable entry is never enriched or guessed. It is returned only if its exposed searchable value matches and is marked `unavailable`.
- No raw source response, continuation value, credential, private value, internal trace, or unfiltered source diagnostic is returned.

## Discovery Metadata Contract

Discovery metadata must expose:

- tool name, strict input schema, family, description, and the 25 default / 50 maximum result policy;
- a composite boundary with one playlist availability lookup, up to ten 50-entry item pages, and in-server literal filtering;
- lower-layer dependencies on playlist lookup and playlist-item retrieval, without exposing continuation values;
- the 500-entry inspection bound, coverage fields, source-order policy, no-ranking policy, matching semantics, excluded search types, and partial-result policy;
- normalized response fields with provenance categories; and
- the five safe error categories and caller recovery guidance below.

## Error Contract

| Category | When returned | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | Required values are missing, invalid, or unsupported fields are supplied. | Correct the identified request field and retry. |
| `unavailable_resource` | The requested playlist cannot be safely retrieved. | Use a different accessible playlist identifier. |
| `authorization_sensitive_data` | Access requires authorization unavailable to the request. | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Source capacity is exhausted. | Retry after capacity is available. |
| `upstream_failure` | A source failure or invalid pagination state prevents completion. | Retry when the source service is available. |

All errors are structured and safe. They do not disclose whether an unavailable playlist is deleted, private, hidden, restricted, or absent.

## Compatibility and Rollback

This is an additive public MCP tool and does not change an existing request or response schema. Rollback removes this tool from default registration; existing tools and their contracts remain unchanged.
