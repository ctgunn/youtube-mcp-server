# Data Model: YT-310 Playlist Details

## Playlist Detail Request

Represents one client request for normalized details about one playlist.

**Fields**:

- `playlistId`: required, nonblank text identifier for exactly one playlist.

**Validation Rules**:

- Only `playlistId` is accepted.
- `playlistId` must be nonblank text after trimming.
- Missing, blank, non-text, and unknown inputs are reported as `invalid_parameters` before lookup occurs.

**Relationships**:

- Produces either one Normalized Playlist Detail or one Lookup Outcome error.

## Normalized Playlist Detail

Represents the successful, bounded result for exactly one publicly retrievable playlist.

**Available Fields**:

- `playlistId`: source playlist identifier.
- `title`, `description`, `publishedAt`, `thumbnails`: available descriptive metadata.
- `channelId`, `channelTitle`: available creator attribution.
- `privacyStatus`: available public visibility metadata.
- `itemCount`: available number of playlist entries observed for the request.
- `fieldProvenance`: classification of source-preserved and normalized fields.
- `contentScope`: normalized declaration that video entries are not included, with the separate playlist-items tool name.

**Rules**:

- The result copies only available public source values and never fabricates missing metadata.
- The result contains exactly one playlist and no entries, pagination, ranking, filtering, enrichment, or historical snapshot.
- `contentScope` and field provenance are normalized contract information, not source playlist fields.
- The result represents the public state observed for the lookup; it makes no claim about later state.

**Relationships**:

- Is derived from one lower-level `playlists.list` item.
- Points clients needing entries to `playlists_getPlaylistItems` without invoking it.

## Provenance Context

Represents caller-visible information about how a result field should be interpreted.

| Field group | Provenance | Rule |
| --- | --- | --- |
| `playlistId` | `raw_upstream` | Preserve the available source identifier. |
| Available playlist metadata | `normalized` | Preserve source meaning while presenting stable caller field names. |
| `fieldProvenance`, `contentScope` | `normalized` | Describe the public contract and scope; do not claim to be source data. |

## Lookup Outcome

Represents a safe result state for a request that cannot return a normalized playlist detail.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | The request did not meet input rules. | Correct `playlistId` and retry. |
| `unavailable_resource` | The requested playlist cannot be returned. | Use a different accessible identifier; do not infer why. |
| `authorization_sensitive_data` | Public access cannot retrieve the required source data. | Obtain appropriate access if applicable. |
| `quota_exhaustion` | The lookup cannot proceed because capacity is exhausted. | Retry after capacity is available. |
| `upstream_failure` | The source service could not complete the lookup for another reason. | Retry when appropriate. |

**Safety Rules**:

- Unavailable outcomes do not distinguish private, deleted, hidden, restricted, and not-found playlists.
- Error details exclude credentials, private creator context, headers, tokens, stack traces, signed links, raw request or response bodies, and non-public playlist data.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> validated
       -> unavailable_resource
       -> authorization_sensitive_data
       -> quota_exhaustion
       -> upstream_failure
       -> normalized_playlist_detail
```
