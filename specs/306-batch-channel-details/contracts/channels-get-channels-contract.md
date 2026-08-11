# MCP Contract: `channels_getChannels`

## Purpose and Compatibility

Return normalized public details for multiple YouTube channels in one request. This additive Layer 3 tool returns an ordered, independently interpretable item for every requested ID and applies the existing `channels_getChannel` semantics to each available item where the selected details permit. It does not change `channels_getChannel`, `channels_list`, or `playlist_items_list`.

## Discovery Metadata

| Property | Contract |
| --- | --- |
| Public name | `channels_getChannels` |
| Family | `channels` |
| Composition boundary | Normalized, batch retrieval with optional enrichment |
| Lower-level dependencies | One `channels.list` collection lookup; when enabled, at most one `playlistItems.list` one-item lookup for each available channel |
| Batch bound | 1–50 distinct channel IDs |
| Ordering | `results` exactly preserves `channelIds` order; source order is never exposed as a guarantee |
| Default details | `parts` defaults to `["snippet"]` |
| Default enrichment | `includeLatestUpload` defaults to `true` |
| Partial result policy | An unavailable ID or per-item enrichment failure does not discard other items; a bulk core dependency failure remains request-wide |
| Compatibility | Additive public tool; discovery must not advertise it as representative-only |
| Rollback | Remove only this descriptor, package export, and default registration; existing tools remain unchanged |

## Input Contract

```json
{
  "type": "object",
  "required": ["channelIds"],
  "additionalProperties": false,
  "properties": {
    "channelIds": {
      "type": "array",
      "minItems": 1,
      "maxItems": 50,
      "uniqueItems": true,
      "items": {
        "type": "string",
        "minLength": 1
      },
      "description": "One through 50 distinct YouTube channel identifiers."
    },
    "parts": {
      "type": "array",
      "minItems": 1,
      "uniqueItems": true,
      "items": {
        "type": "string",
        "enum": ["snippet", "contentDetails"]
      },
      "default": ["snippet"],
      "description": "Public source-detail groups to return."
    },
    "includeLatestUpload": {
      "type": "boolean",
      "default": true,
      "description": "Whether to obtain the latest publicly visible upload timestamp for each available channel."
    }
  }
}
```

The tool trims identifiers before validation, then rejects empty, duplicate-after-trimming, non-text, missing, or over-limit IDs; empty, duplicate, or unsupported `parts`; a non-Boolean enrichment preference; non-object arguments; and unknown fields as a request-wide `invalid_parameters` outcome before lookup.

## Detail Selection Contract

| Selected part | Returned fields when available | Provenance |
| --- | --- | --- |
| `snippet` | `title`, `description`, `thumbnails`, `normalizedMetadata`, and `heuristics` | Raw fields are `raw_upstream`; mapped metadata is `normalized`; contacts and heuristics are `heuristic_inferred`. |
| `contentDetails` | `contentDetails.uploadsPlaylistId` | `raw_upstream` |

Every available item always includes `channelId`, `outcome`, `enrichment`, and `fieldProvenance`. The service may retrieve other data solely to perform selected behavior, but it does not return unselected detail groups or infer facts from them.

## Successful Batch Result Contract

```json
{
  "requestedChannelIds": ["UC111", "UC222", "UC333"],
  "results": [
    {
      "channelId": "UC111",
      "outcome": {"status": "success"},
      "title": "Example Channel",
      "description": "Public profile description",
      "thumbnails": {"default": "https://example.invalid/channel.jpg"},
      "normalizedMetadata": {
        "country": "US",
        "defaultLanguage": "en",
        "joinedAt": "2020-01-01T00:00:00Z",
        "customUrl": "@example",
        "emailsFound": ["hello@example.com"],
        "contactLinks": ["https://example.invalid/contact"]
      },
      "heuristics": {
        "creatorClassification": "creator",
        "creatorSignals": ["public_creator_term"]
      },
      "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
      "enrichment": {"status": "complete"},
      "fieldProvenance": {
        "channelId": "raw_upstream",
        "title": "raw_upstream",
        "description": "raw_upstream",
        "thumbnails": "raw_upstream",
        "normalizedMetadata.country": "normalized",
        "normalizedMetadata.defaultLanguage": "normalized",
        "normalizedMetadata.joinedAt": "normalized",
        "normalizedMetadata.customUrl": "normalized",
        "normalizedMetadata.emailsFound": "heuristic_inferred",
        "normalizedMetadata.contactLinks": "heuristic_inferred",
        "heuristics.creatorClassification": "heuristic_inferred",
        "heuristics.creatorSignals": "heuristic_inferred",
        "latestVideoPublishedAt": "normalized",
        "enrichment": "normalized"
      }
    },
    {
      "channelId": "UC222",
      "outcome": {
        "status": "unavailable",
        "category": "unavailable_resource"
      }
    },
    {
      "channelId": "UC333",
      "outcome": {
        "status": "partial",
        "category": "partial_enrichment_failure",
        "causeCategory": "quota_exhaustion"
      },
      "enrichment": {
        "status": "partial",
        "category": "partial_enrichment_failure",
        "causeCategory": "quota_exhaustion"
      }
    }
  ],
  "summary": {
    "requested": 3,
    "successful": 1,
    "unavailable": 1,
    "partiallyEnriched": 1
  }
}
```

`results` contains exactly one item per validated requested ID in the same order. `summary` is a partition: `requested = successful + unavailable + partiallyEnriched`. A core-success item with enrichment `unavailable` or `not_requested` counts as `successful`; a core-success item with enrichment `partial` counts only as `partiallyEnriched`.

## Per-item Enrichment Contract

| Condition | Item outcome | Enrichment | Timestamp |
| --- | --- | --- | --- |
| Valid latest public upload timestamp | `success` | `complete` | Present as `latestVideoPublishedAt` |
| No public uploads playlist, item, or valid timestamp | `success` | `unavailable` | Omitted |
| Post-core authorization, capacity, or source failure | `partial` | `partial` plus sanitized cause category | Omitted |
| `includeLatestUpload=false` | `success` | `not_requested` | Omitted; no enrichment lookup occurs |

`latestVideoPublishedAt` is a normalized enrichment value, never a raw channel-profile field. The tool makes no more than one one-item latest-upload lookup per available item.

## Contact, Heuristic, and Provenance Contract

- `emailsFound` and `contactLinks` come only from returned public channel material. They are normalized and de-duplicated deterministically; malformed, unsupported, private, credential-bearing, or non-public values are omitted.
- `creatorClassification` is `creator`, `brand`, or `unknown`; a non-`unknown` value needs positive non-conflicting public signals. It and its safe signal identifiers are research context, not verified identity or canonical source truth.
- Available item fields are labeled only as `raw_upstream`, `normalized`, or `heuristic_inferred`. Batch container fields are documented separately and are never presented as channel source fields.

## Error Contract

| Boundary | Category | Trigger | Safe caller guidance |
| --- | --- | --- | --- |
| Request | `invalid_parameters` | Invalid argument shape or value | Correct the named input and retry. |
| Item | `unavailable_resource` | ID absent from a successful core result | Use a different accessible identifier; do not infer the reason. |
| Request | `authorization_sensitive_data` | Bulk core lookup requires unavailable authorization | Obtain appropriate authorization if applicable. |
| Request | `quota_exhaustion` | Bulk core lookup is capacity-limited | Retry after capacity is available. |
| Request | `upstream_failure` | Other bulk core source failure | Retry when the source is available. |
| Item | `partial_enrichment_failure` | Latest-upload lookup fails after core success | Use the returned core profile; retry enrichment later if appropriate. |

No error, item outcome, or partial result may include credentials, headers, tokens, authorization values, private owner context, raw source request/response data, stack traces, signed links, or non-public contact information.
