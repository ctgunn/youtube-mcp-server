# Data Model: YT-302 Video Details

## Video Details Request

Represents one client request for normalized details about one video.

**Fields**:

- `videoId`: required, nonblank text identifier for exactly one video.
- `parts`: optional list of unique detail-group names.

**Validation Rules**:

- Only `videoId` and `parts` are accepted.
- `videoId` must be nonblank text.
- `parts`, when supplied, must be an array of unique text values.
- Allowed part values are `snippet`, `contentDetails`, `statistics`, `status`, and `topicDetails`.
- An omitted or empty `parts` selection requests no optional group.
- Invalid input is reported as `invalid_parameters` before a lookup occurs.

**Relationships**:

- Selects zero or more Optional Detail Groups.
- Produces either one Normalized Video Detail or one Lookup Outcome error.

## Normalized Video Detail

Represents the successful, bounded result for exactly one video.

**Default Fields**:

- `videoId`: source video identifier.
- `title`, `description`, `publishedAt`: normalized descriptive metadata.
- `channelId`, `channelTitle`: normalized publisher metadata.
- `duration`, `categoryId`: normalized content metadata.
- `tags`, `thumbnails`: available descriptive collections.

**Rules**:

- Default fields are returned whenever available, regardless of the `parts` selection.
- Values retain their source meaning; the result must not invent a missing value.
- A field can be unavailable when the source does not provide it.
- The result contains one video, never a collection, pagination, ranking, or enrichment output.

**Relationships**:

- Has zero or more selected Optional Detail Groups.
- Is derived from one lower-level `videos.list` item.

## Optional Detail Group

Represents an additive field group selected by a client.

| Group | Returned fields | Selection rule |
| --- | --- | --- |
| `snippet` | `liveBroadcastContent`, `defaultLanguage`, `defaultAudioLanguage` | Add only when requested; core descriptive fields remain default fields. |
| `contentDetails` | `dimension`, `definition`, `caption`, `licensedContent`, `regionRestriction`, `projection` | Add only when requested; `duration` and `categoryId` remain default fields. |
| `statistics` | `viewCount`, `likeCount`, `favoriteCount`, `commentCount` | Add only when requested and available. |
| `status` | `uploadStatus`, `privacyStatus`, `license`, `embeddable`, `publicStatsViewable`, `madeForKids`, `selfDeclaredMadeForKids` | Add only when requested and available. |
| `topicDetails` | `topicCategories` | Add only when requested and available. |

**Validation Rules**:

- A group may occur at most once per request.
- Unsupported groups cause request rejection; they are never ignored.
- Requested unavailable fields remain unavailable and are never synthesized.

## Lookup Outcome

Represents the safe result state for a request that cannot return a normalized video detail.

| Category | Meaning | Caller guidance |
| --- | --- | --- |
| `invalid_parameters` | The request did not meet input rules. | Correct `videoId` or `parts` and retry. |
| `unavailable_resource` | The requested video cannot be returned. | Use a different accessible identifier; do not infer the reason. |
| `authorization_sensitive_data` | Access to requested source data is not permitted. | Obtain appropriate authorization if applicable. |
| `quota_exhaustion` | The lookup cannot proceed because usage capacity is exhausted. | Retry after capacity is available. |
| `upstream_failure` | The source service could not complete the lookup for another reason. | Retry when appropriate. |

**Safety Rules**:

- Unavailable outcomes do not distinguish private, deleted, restricted, and not-found videos.
- Error details exclude credentials, headers, tokens, stack traces, signed links, raw request or response bodies, and media content.

## Request State Transitions

```text
received
  -> invalid_parameters
  -> validated
       -> unavailable_resource
       -> authorization_sensitive_data
       -> quota_exhaustion
       -> upstream_failure
       -> normalized_video_detail
```
