# MCP Contract: `channels_getChannel`

## Purpose

Return one caller-ready YouTube channel profile with stable public metadata, cautious public-contact and creator-versus-brand context, and a bounded latest-video publication enrichment. This is additive to the public MCP catalog and does not change the existing `channels_list` or `playlist_items_list` contracts.

## Discovery Metadata

| Property | Contract |
| --- | --- |
| Public name | `channels_getChannel` |
| Family | `channels` |
| Composition boundary | Normalized and enriched retrieval |
| Lower-level dependencies | `channels.list` and, when a public uploads playlist is available, `playlistItems.list` |
| Result bound | One channel, one core lookup, and at most one one-item uploads-playlist lookup |
| Access and quota | Surface safe access and capacity caveats. A normal enriched request uses the documented cost of one channel lookup and one playlist-item lookup before retries. |
| Partial result policy | Preserve a successful core profile when latest-video enrichment is unavailable or fails safely. |
| Compatibility | Executable and additive; discovery metadata must not contain `representativeOnly`. |

## Input Contract

```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": {
      "type": "string",
      "minLength": 1,
      "description": "One YouTube channel identifier."
    }
  }
}
```

The tool rejects a missing, blank, non-text `channelId`, non-object arguments, and unknown input fields as `invalid_parameters` before lookup.

## Composition and Enrichment Contract

1. Retrieve the one requested channel's public profile and public uploads-playlist identifier.
2. If a usable uploads-playlist identifier is available, retrieve at most its first item and use its available publication timestamp.
3. Do not perform generic search, multi-item scanning, video hydration, ranking, scraping, or external contact discovery.

The core profile is the whole-request boundary. A core lookup failure produces a whole-request error. A latest-video issue after a successful core lookup produces a successful profile with an explicit enrichment state.

## Successful Result Contract

Every successful result contains a `fieldProvenance` object that labels every returned field path as `raw_upstream`, `normalized`, or `heuristic_inferred`.

| Field | Provenance | Meaning |
| --- | --- | --- |
| `channelId` | `raw_upstream` | Source-provided canonical channel identifier. |
| `title`, `description`, `thumbnails` | `raw_upstream` | Available public profile values. |
| `normalizedMetadata.country`, `defaultLanguage`, `joinedAt`, `customUrl` | `normalized` | Stable public metadata mappings. |
| `normalizedMetadata.emailsFound`, `contactLinks` | `heuristic_inferred` | Valid, public-only values derived from returned channel material; not verified identity or canonical source truth. |
| `latestVideoPublishedAt` | `normalized` | Timestamp derived from the bounded public uploads-playlist enrichment. |
| `heuristics.creatorClassification`, `creatorSignals` | `heuristic_inferred` | Non-canonical channel-type assessment and public signal identifiers. |
| `enrichment` | `normalized` | Availability and partial-failure state for latest-video enrichment. |

### Complete enrichment example

```json
{
  "channelId": "UC123",
  "title": "Example Channel",
  "description": "Official creator channel. Contact: hello@example.com",
  "thumbnails": {
    "default": "https://example.invalid/channel.jpg"
  },
  "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
  "enrichment": {
    "status": "complete"
  },
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
  "fieldProvenance": {
    "channelId": "raw_upstream",
    "title": "raw_upstream",
    "description": "raw_upstream",
    "thumbnails": "raw_upstream",
    "latestVideoPublishedAt": "normalized",
    "enrichment": "normalized",
    "normalizedMetadata.country": "normalized",
    "normalizedMetadata.defaultLanguage": "normalized",
    "normalizedMetadata.joinedAt": "normalized",
    "normalizedMetadata.customUrl": "normalized",
    "normalizedMetadata.emailsFound": "heuristic_inferred",
    "normalizedMetadata.contactLinks": "heuristic_inferred",
    "heuristics.creatorClassification": "heuristic_inferred",
    "heuristics.creatorSignals": "heuristic_inferred"
  }
}
```

### Unavailable and partial enrichment

If no public uploads playlist, video item, or valid timestamp is available, the result omits `latestVideoPublishedAt` and returns:

```json
{
  "enrichment": {
    "status": "unavailable"
  }
}
```

If a safe dependency failure occurs after core profile success, the result omits `latestVideoPublishedAt` and returns:

```json
{
  "enrichment": {
    "status": "partial",
    "category": "partial_enrichment_failure",
    "causeCategory": "quota_exhaustion"
  }
}
```

`causeCategory` may instead be `authorization_sensitive_data` or `upstream_failure`; it contains no raw lower-layer details. A partial result is still a successful channel-detail response.

## Contact and Heuristic Disclosure

- `emailsFound` and `contactLinks` are extracted only from public channel material already returned for this request. The tool does not crawl links, access owner accounts, or use a contact-data provider.
- Contact values are normalized and de-duplicated deterministically. Malformed, unsupported, private, and non-public values are omitted.
- A public contact value does not establish ownership, affiliation, deliverability, or permission to contact its holder.
- `creatorClassification` is `creator`, `brand`, or `unknown`. A non-`unknown` classification requires positive, non-conflicting public signals. Missing or conflicting signals return `unknown`.
- `creatorSignals` use safe signal identifiers rather than copied free-form profile content. The heuristic may be incomplete or incorrect and must be used only as research context.

## Error Contract

| Category | Trigger | Safe response rule |
| --- | --- | --- |
| `invalid_parameters` | Invalid `channelId`, arguments, or unknown input field | Identify the invalid field and instruct the caller to correct it before retrying. |
| `unavailable_resource` | Empty core result or source not-found/unavailable outcome | Use a different accessible identifier; do not reveal whether the channel is hidden, deleted, restricted, or nonexistent. |
| `authorization_sensitive_data` | Core profile access is denied or requires authorization | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Capacity blocks the core profile lookup | Retry after capacity is available. |
| `upstream_failure` | Another core source-service failure | Retry when the source service is available. |
| `partial_enrichment_failure` | Latest-video enrichment fails after a successful core profile | Use the returned profile; retry enrichment later if its safe cause category is actionable. |

All errors and partial-enrichment details omit API keys, credentials, authorization values, headers, tokens, private owner context, stack traces, raw request and response bodies, signed links, media, and non-public contact information.

## Compatibility and Rollback

- This is an additive public tool and does not change existing lower-level inputs or results.
- Rollback removes only this tool's composed-package export and default registration.
- Existing channel and playlist-item capabilities continue unchanged.
