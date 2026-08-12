# Contract: `playlists_getPlaylist`

## Purpose

Return normalized, caller-ready public details for exactly one YouTube playlist. This additive Layer 3 contract does not alter the existing near-raw `playlists_list` contract and does not return the videos contained in the playlist.

## Discovery Metadata

| Property | Contract |
| --- | --- |
| Public name | `playlists_getPlaylist` |
| Family | `playlists` |
| Retrieval boundary | Normalized retrieval of one playlist through `playlists.list` |
| Lower-level dependency | `playlists.list` |
| Result bound | Exactly one normalized playlist on success; one lookup; no pagination, fan-out, ranking, filtering, or enrichment |
| Access and capacity | Surface safe public-read access and capacity caveats in metadata and errors; do not expose secrets or internal diagnostics |
| Playlist entries | Not returned; callers use `playlists_getPlaylistItems` for entry retrieval |

## Input Contract

```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": {
      "type": "string",
      "minLength": 1,
      "description": "One YouTube playlist identifier."
    }
  }
}
```

The tool trims surrounding whitespace. It rejects missing, blank, non-text, and unknown inputs as `invalid_parameters` before lookup.

## Result Contract

### Available normalized fields

Every successful result includes `playlistId` plus every available field from this set:

| Field | Provenance | Source meaning |
| --- | --- | --- |
| `playlistId` | `raw_upstream` | Playlist identifier. |
| `title`, `description`, `publishedAt`, `thumbnails` | `normalized` | Descriptive playlist metadata. |
| `channelId`, `channelTitle` | `normalized` | Playlist creator attribution. |
| `privacyStatus` | `normalized` | Available public playlist visibility state. |
| `itemCount` | `normalized` | Number of playlist entries observed for this request. |
| `fieldProvenance`, `contentScope` | `normalized` | Contract interpretation and scope guidance. |

Unavailable optional values are omitted; the tool never substitutes empty strings, zeros, or inferred values. `contentScope` identifies `playlists_getPlaylistItems` as the separate entry-retrieval tool and confirms that no video entries are included here.

### Successful example

```json
{
  "playlistId": "PL123",
  "title": "Example research playlist",
  "description": "Public collection of example videos",
  "channelId": "UC123",
  "channelTitle": "Example Channel",
  "publishedAt": "2026-01-15T12:00:00Z",
  "thumbnails": {"default": {"url": "https://example.invalid/thumbnail.jpg"}},
  "privacyStatus": "public",
  "itemCount": 12,
  "fieldProvenance": {
    "playlistId": "raw_upstream",
    "title": "normalized",
    "contentScope": "normalized"
  },
  "contentScope": {
    "playlistItemsIncluded": false,
    "playlistItemsTool": "playlists_getPlaylistItems",
    "stateObservedAtRequest": true
  }
}
```

## Error Contract

The tool returns safe MCP-compatible errors with a stable category and sanitized details. It never exposes API keys, authorization values, credentials, tokens, headers, stack traces, signed links, raw request or response bodies, private creator context, or non-public playlist data.

| Category | Trigger | Safe response rule |
| --- | --- | --- |
| `invalid_parameters` | Invalid `playlistId` or unknown input field | Identify the invalid field and instruct the caller to correct it before retrying. |
| `unavailable_resource` | Empty or malformed lookup result, or source not-found/removed outcome | Use a different accessible identifier; do not reveal whether the playlist is private, deleted, restricted, or nonexistent. |
| `authorization_sensitive_data` | Access is denied or requires authorization | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | Capacity or rate limit blocks lookup | Retry after capacity is available. |
| `upstream_failure` | Other source-service failure | Retry when the source service is available. |

## Compatibility and Rollback

- This is an additive public tool; it does not change `playlists_list` inputs or results.
- Discovery metadata must not include a representative-only marker and must not contain unsafe metadata keys.
- Rolling back removes this tool's export and default registration only; the lower-level playlist lookup remains intact.
