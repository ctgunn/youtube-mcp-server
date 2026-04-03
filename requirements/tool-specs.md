# Tool Specifications (v1)
## Project: YouTube MCP Server on Cloud Run

## 1. Purpose
This document defines the public MCP tool contracts for the YouTube MCP Server.

It covers the two public tool layers:

- Layer 1: internal integrations and wrappers
- Layer 2: lower-level MCP tools that expose one documented YouTube Data API
  endpoint per tool with near-raw request/response semantics
- Layer 3: higher-level public MCP tools

This file does not define Layer 1 implementation details beyond the public
context needed to understand how Layers 2 and 3 are derived.

## 2. Design Principles
- Tool names are grouped by domain:
  - Layer 2 uses `resource_method` names such as `videos_list` or
    `comments_setModerationStatus`
  - Layer 3 uses domain-grouped names such as `videos_*`, `channels_*`,
    `playlists_*`, and `transcripts_*`
- Tool names do not include a redundant `youtube_` prefix.
- MCP transport, JSON-RPC framing, and top-level result/error envelopes are
  governed by the foundation contracts.
- This file defines the logical request schema and logical payload returned in
  MCP tool results.
- Layer 2 tools stay close to upstream YouTube request/response semantics while
  still using MCP-friendly descriptions and validation.
- Layer 3 public tool contracts use MCP-facing parameter names, not raw YouTube
  API parameter names.
- Tools may combine multiple upstream YouTube endpoints and local enrichment
  logic before producing a final result.
- Public contracts must distinguish:
  - raw upstream fields
  - normalized fields
  - heuristic or inferred fields

## 3. Common Conventions

### 3.1 Identifiers
- `videoId`: YouTube video ID
- `channelId`: YouTube channel ID
- `playlistId`: YouTube playlist ID
- `channelIds`: array of YouTube channel IDs

### 3.2 Time and Date Formats
- Date/time values use ISO 8601 timestamps.
- Duration values use ISO 8601 duration strings.
- Filter inputs such as `publishedAfter`, `publishedBefore`,
  `lastUploadAfter`, and `lastUploadBefore` MUST accept ISO 8601 timestamps.

### 3.3 Pagination and Limits
- Layer 2 preserves upstream pagination and limit concepts where practical,
  including `maxResults`, `pageToken`, and resource-specific filters.
- The public Layer 3 catalog prefers `maxResults` over `pageSize`.
- Unless a tool defines otherwise:
  - default `maxResults` = `10`
  - maximum `maxResults` = `50`
- Batch input arrays SHOULD be validated explicitly.
- If implementation needs a lower bound than the contract default for safety or
  quota reasons, that lower bound must be documented before rollout.

### 3.4 Search and Ordering Semantics
- `query` is the canonical public search field.
- `order` maps to upstream ordering where supported.
- `sortBy` is a Layer 3 ranking field and may be implemented partly or fully in
  server-side logic after upstream retrieval.

Supported Layer 3 `sortBy` values where applicable:
- `relevance`
- `subscribers_asc`
- `subscribers_desc`
- `indie_priority`
- `recent_activity`

Semantics:
- `relevance`: preserve the base upstream or composite relevance order
- `subscribers_asc`: smallest qualifying channels first
- `subscribers_desc`: largest qualifying channels first
- `indie_priority`: prefer smaller creator-like channels over large brands when
  enough metadata exists to support that distinction
- `recent_activity`: prefer channels whose latest upload activity is more recent

### 3.5 Transcript Language Semantics
- `language` uses BCP-47-style strings such as `en`, `en-US`, or `es`.
- For transcript tools, language resolution order is:
  1. explicit `language` parameter
  2. `YOUTUBE_TRANSCRIPT_LANG`
  3. `en`

### 3.6 `parts` Semantics
`parts` is a public field that controls optional response expansion for tools
that can expose additional upstream resource parts.

The contract permits `parts` only on:
- `videos_getVideo`
- `channels_getChannels`

If `parts` is omitted:
- the tool returns its default normalized response shape
- the server MAY still fetch extra upstream data needed to populate normalized
  fields

If `parts` is present:
- only supported public part names may be requested
- unsupported part names MUST fail validation

### 3.7 Quota Visibility
- Every Layer 2 tool MUST document its official YouTube Data API quota-unit
  cost in the tool description or adjacent public contract notes.
- Layer 3 tools SHOULD document when they are likely to fan out into multiple
  upstream calls or expensive endpoints.
- Especially expensive upstream methods such as `search.list`,
  `captions.insert`, `captions.update`, `captions.download`, and
  `videos.insert` must remain highly visible in both implementation and public
  contract documentation.

## 4. Common Output Rules

### 4.1 Logical Payload Model
Each tool returns a logical payload object that will be embedded inside the
MCP-native tool result content.

This file does not redefine the transport envelope. It defines the
`structuredContent` payload shape that agents should expect for each tool.

Layer-specific intent:
- Layer 2 returns near-raw upstream resource payloads or lightly normalized
  wrappers that remain obviously traceable to a single endpoint call.
- Layer 3 returns higher-level normalized or composite payloads optimized for
  agent workflows.

### 4.2 List Result Shape
Tools returning multiple items SHOULD follow this shape when applicable:

```json
{
  "items": [],
  "nextPageToken": "token-or-null",
  "maxResults": 10,
  "totalResults": 123
}
```

Rules:
- `nextPageToken` is present when continuation is meaningful and available.
- `totalResults` is present when the server can provide it reliably.
- For composite tools, `totalResults` MAY be omitted if it would be misleading
  or disproportionately expensive to compute.

### 4.3 Raw vs Normalized vs Heuristic Fields
- Raw fields:
  - values taken directly from upstream resources with no semantic expansion
- Normalized fields:
  - values renamed or reshaped for consistency across tools
- Heuristic fields:
  - values inferred by server-side rules rather than guaranteed by YouTube

Heuristic fields MUST be documented clearly and must not masquerade as raw
YouTube guarantees.

## 5. Common Error Categories
The exact transport error envelope is governed by the MCP foundation, but Layer
3 tools should map failures into stable logical categories such as:

- `invalid_argument`
- `resource_not_found`
- `quota_exceeded`
- `upstream_unavailable`
- `transcript_unavailable`
- `language_not_available`
- `transcript_access_not_permitted`
- `partial_data_unavailable`
- `internal_execution_failure`

## 6. Upstream Endpoint Dependencies
Layer 2 exposes the currently documented YouTube Data API v3 surface through one
public MCP tool per endpoint/resource method.

Current Layer 2 inventory:
- `activities.list`
- `captions.list`, `captions.insert`, `captions.update`,
  `captions.download`, `captions.delete`
- `channelBanners.insert`
- `channels.list`, `channels.update`
- `channelSections.list`, `channelSections.insert`,
  `channelSections.update`, `channelSections.delete`
- `comments.list`, `comments.insert`, `comments.update`,
  `comments.setModerationStatus`, `comments.delete`
- `commentThreads.list`, `commentThreads.insert`
- `guideCategories.list`
- `i18nLanguages.list`, `i18nRegions.list`
- `members.list`, `membershipsLevels.list`
- `playlistImages.list`, `playlistImages.insert`,
  `playlistImages.update`, `playlistImages.delete`
- `playlistItems.list`, `playlistItems.insert`,
  `playlistItems.update`, `playlistItems.delete`
- `playlists.list`, `playlists.insert`, `playlists.update`,
  `playlists.delete`
- `search.list`
- `subscriptions.list`, `subscriptions.insert`, `subscriptions.delete`
- `thumbnails.set`
- `videoAbuseReportReasons.list`
- `videoCategories.list`
- `videos.list`, `videos.insert`, `videos.update`, `videos.rate`,
  `videos.getRating`, `videos.reportAbuse`, `videos.delete`
- `watermarks.set`, `watermarks.unset`

Initial Layer 3 tools may depend on this subset of upstream YouTube Data API
endpoints:

- `videos.list`
- `search.list`
- `channels.list`
- `playlists.list`
- `playlistItems.list`
- `captions.list`
- `captions.download`

Composite tools must document where they depend on more than one endpoint.

## 7. Layer 2 Tool Catalog

### 7.1 Shared Layer 2 Rules
- Layer 2 tools expose one documented YouTube Data API endpoint/resource method
  per MCP tool.
- Tool names follow `resource_method`, preserving camelCase method suffixes
  where needed, such as `comments_setModerationStatus` and `videos_getRating`.
- Input contracts should stay close to upstream request parameters.
- Output contracts should stay near-raw to the upstream resource shape, with
  only light normalization when needed for MCP clarity.
- OAuth-only endpoints MUST say so explicitly in the tool description and
  validation/error behavior.
- Deprecated or availability-constrained endpoints MUST say so explicitly in the
  tool description.

### 7.2 Layer 2 Resource Catalog

#### 7.2.1 Activities
- `activities_list`
  Endpoint: `activities.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: near-raw upstream filters such as `part`, `channelId`, `home`,
  `mine`, `publishedAfter`, `pageToken`, `maxResults`
  Output: near-raw activity list payload with items, paging, and requested
  parts

#### 7.2.2 Captions
- `captions_list`
  Endpoint: `captions.list`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: near-raw upstream filters such as `part`, `videoId`, `id`,
  `onBehalfOfContentOwner`
  Output: near-raw caption track list payload
- `captions_insert`
  Endpoint: `captions.insert`
  Quota: `400`
  Auth: `oauth_required`
  Inputs: metadata plus media-upload inputs required by the upstream endpoint
  Output: created caption resource payload
- `captions_update`
  Endpoint: `captions.update`
  Quota: `450`
  Auth: `oauth_required`
  Inputs: caption resource update body plus media-upload inputs when required
  Output: updated caption resource payload
- `captions_download`
  Endpoint: `captions.download`
  Quota: `200`
  Auth: `oauth_required`
  Inputs: caption track identifier plus optional `tfmt`, `tlang`, and
  delegation flags where supported
  Output: downloaded caption content plus any light metadata wrapper needed for
  MCP-safe delivery
- `captions_delete`
  Endpoint: `captions.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: caption identifier plus delegation flags where supported
  Output: deletion acknowledgment payload

#### 7.2.3 Channel Banners
- `channelBanners_insert`
  Endpoint: `channelBanners.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: media-upload inputs and optional channel/delegation context
  Output: banner update result payload

#### 7.2.4 Channels
- `channels_list`
  Endpoint: `channels.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: near-raw upstream filters such as `part`, `id`, `mine`,
  `forHandle`, `managedByMe`, `pageToken`, `maxResults`
  Output: near-raw channel list payload
- `channels_update`
  Endpoint: `channels.update`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: writable channel resource body plus `part`
  Output: updated channel resource payload

#### 7.2.5 Channel Sections
- `channelSections_list`
  Endpoint: `channelSections.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part` plus upstream filters such as `channelId`, `id`, `mine`
  Output: near-raw channel section list payload
- `channelSections_insert`
  Endpoint: `channelSections.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus channel section resource body
  Output: created channel section payload
- `channelSections_update`
  Endpoint: `channelSections.update`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus channel section resource body
  Output: updated channel section payload
- `channelSections_delete`
  Endpoint: `channelSections.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: section identifier
  Output: deletion acknowledgment payload

#### 7.2.6 Comments
- `comments_list`
  Endpoint: `comments.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part` plus `id`, `parentId`, `pageToken`, `maxResults`, `textFormat`
  Output: near-raw comment list payload
- `comments_insert`
  Endpoint: `comments.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus reply-creation body
  Output: created comment resource payload
- `comments_update`
  Endpoint: `comments.update`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus writable comment resource body
  Output: updated comment resource payload
- `comments_setModerationStatus`
  Endpoint: `comments.setModerationStatus`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: comment identifiers plus moderation status flags
  Output: moderation-update acknowledgment payload
- `comments_delete`
  Endpoint: `comments.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: comment identifier
  Output: deletion acknowledgment payload

#### 7.2.7 Comment Threads
- `commentThreads_list`
  Endpoint: `commentThreads.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part` plus filters such as `videoId`, `allThreadsRelatedToChannelId`,
  `id`, `pageToken`, `maxResults`, `order`, `searchTerms`, `textFormat`
  Output: near-raw comment-thread list payload
- `commentThreads_insert`
  Endpoint: `commentThreads.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus top-level comment thread body
  Output: created comment thread payload

#### 7.2.8 Guide Categories
- `guideCategories_list`
  Endpoint: `guideCategories.list`
  Quota: `1`
  Auth: `api_key`
  Inputs: `part`, `regionCode`
  Output: near-raw guide-category payload
  Notes: must explicitly document deprecated or unavailable platform behavior

#### 7.2.9 Localization
- `i18nLanguages_list`
  Endpoint: `i18nLanguages.list`
  Quota: `1`
  Auth: `api_key`
  Inputs: `part`, `hl`
  Output: near-raw language lookup payload
- `i18nRegions_list`
  Endpoint: `i18nRegions.list`
  Quota: `1`
  Auth: `api_key`
  Inputs: `part`, `hl`
  Output: near-raw region lookup payload

#### 7.2.10 Memberships
- `members_list`
  Endpoint: `members.list`
  Quota: `1`
  Auth: `oauth_required`
  Inputs: `part`, `mode`, `pageToken`, `maxResults`, delegation flags if
  supported
  Output: near-raw membership list payload
- `membershipsLevels_list`
  Endpoint: `membershipsLevels.list`
  Quota: `1`
  Auth: `oauth_required`
  Inputs: `part`
  Output: near-raw membership-level payload

#### 7.2.11 Playlist Images
- `playlistImages_list`
  Endpoint: `playlistImages.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part`, `playlistId`, `id`, paging flags where supported
  Output: near-raw playlist-image payload
- `playlistImages_insert`
  Endpoint: `playlistImages.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: metadata plus media-upload inputs
  Output: created playlist-image payload
- `playlistImages_update`
  Endpoint: `playlistImages.update`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: update body plus media-upload inputs when required
  Output: updated playlist-image payload
- `playlistImages_delete`
  Endpoint: `playlistImages.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: image identifier
  Output: deletion acknowledgment payload

#### 7.2.12 Playlist Items
- `playlistItems_list`
  Endpoint: `playlistItems.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part`, `playlistId`, `id`, `pageToken`, `maxResults`,
  `videoId`, delegation flags where supported
  Output: near-raw playlist item list payload
- `playlistItems_insert`
  Endpoint: `playlistItems.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus playlist item resource body
  Output: created playlist item payload
- `playlistItems_update`
  Endpoint: `playlistItems.update`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus playlist item resource body
  Output: updated playlist item payload
- `playlistItems_delete`
  Endpoint: `playlistItems.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: playlist item identifier
  Output: deletion acknowledgment payload

#### 7.2.13 Playlists
- `playlists_list`
  Endpoint: `playlists.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part`, `channelId`, `id`, `mine`, `pageToken`, `maxResults`
  Output: near-raw playlist list payload
- `playlists_insert`
  Endpoint: `playlists.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus playlist resource body
  Output: created playlist payload
- `playlists_update`
  Endpoint: `playlists.update`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus playlist resource body
  Output: updated playlist payload
- `playlists_delete`
  Endpoint: `playlists.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: playlist identifier
  Output: deletion acknowledgment payload

#### 7.2.14 Search
- `search_list`
  Endpoint: `search.list`
  Quota: `100`
  Auth: `api_key`
  Inputs: near-raw upstream filters such as `part`, `q`, `channelId`,
  `forContentOwner`, `forDeveloper`, `forMine`, `publishedAfter`,
  `publishedBefore`, `regionCode`, `relevanceLanguage`, `safeSearch`, `type`,
  `videoCaption`, `videoDefinition`, `videoDuration`, `videoEmbeddable`,
  `videoLicense`, `videoPaidProductPlacement`, `videoSyndicated`,
  `videoType`, `order`, `pageToken`, `maxResults`
  Output: near-raw search result payload
  Notes: must explicitly warn about the high quota cost

#### 7.2.15 Subscriptions
- `subscriptions_list`
  Endpoint: `subscriptions.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part`, `channelId`, `id`, `mine`, `myRecentSubscribers`,
  `mySubscribers`, `pageToken`, `maxResults`, `order`
  Output: near-raw subscription list payload
- `subscriptions_insert`
  Endpoint: `subscriptions.insert`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus subscription resource body
  Output: created subscription payload
- `subscriptions_delete`
  Endpoint: `subscriptions.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: subscription identifier
  Output: deletion acknowledgment payload

#### 7.2.16 Thumbnails
- `thumbnails_set`
  Endpoint: `thumbnails.set`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `videoId` plus media-upload inputs
  Output: thumbnail update result payload

#### 7.2.17 Video Lookup Utilities
- `videoAbuseReportReasons_list`
  Endpoint: `videoAbuseReportReasons.list`
  Quota: `1`
  Auth: `api_key`
  Inputs: `part`, `hl`
  Output: near-raw abuse-reason lookup payload
- `videoCategories_list`
  Endpoint: `videoCategories.list`
  Quota: `1`
  Auth: `api_key`
  Inputs: `part`, `id`, `regionCode`, `hl`
  Output: near-raw category lookup payload

#### 7.2.18 Videos
- `videos_list`
  Endpoint: `videos.list`
  Quota: `1`
  Auth: `api_key` or mixed, depending on filter mode
  Inputs: `part`, `id`, `chart`, `myRating`, `pageToken`, `maxResults`,
  `regionCode`, `videoCategoryId`
  Output: near-raw video list payload
- `videos_insert`
  Endpoint: `videos.insert`
  Quota: `1600`
  Auth: `oauth_required`
  Inputs: `part` plus metadata and media-upload inputs
  Output: created video resource payload
  Notes: must be called out as one of the highest-cost tools in the system
- `videos_update`
  Endpoint: `videos.update`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `part` plus writable video resource body
  Output: updated video resource payload
- `videos_rate`
  Endpoint: `videos.rate`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: `id`, `rating`
  Output: rating-update acknowledgment payload
- `videos_getRating`
  Endpoint: `videos.getRating`
  Quota: `1`
  Auth: `oauth_required`
  Inputs: `id`
  Output: near-raw video rating payload
- `videos_reportAbuse`
  Endpoint: `videos.reportAbuse`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: abuse-report request body
  Output: abuse-report acknowledgment payload
- `videos_delete`
  Endpoint: `videos.delete`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: video identifier
  Output: deletion acknowledgment payload

#### 7.2.19 Watermarks
- `watermarks_set`
  Endpoint: `watermarks.set`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: channel/watermark placement metadata plus media-upload inputs
  Output: watermark update result payload
- `watermarks_unset`
  Endpoint: `watermarks.unset`
  Quota: `50`
  Auth: `oauth_required`
  Inputs: channel context where required
  Output: watermark removal acknowledgment payload

## 8. Layer 3 Tool Catalog

### 8.1 Video Tools

#### 8.1.1 `videos_getVideo`
Purpose:
- Return detailed information about a single YouTube video in a normalized
  shape.

Primary upstream dependency:
- `videos.list`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "parts": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["snippet", "contentDetails", "statistics", "status", "topicDetails"]
      },
      "uniqueItems": true
    }
  }
}
```

Behavior notes:
- The tool MUST always return the default normalized video shape.
- `parts` expands the response contract to include supported optional groups.
- Unsupported parts MUST fail validation.

Logical payload:
```json
{
  "videoId": "abc123",
  "title": "Video title",
  "description": "...",
  "publishedAt": "2025-12-01T10:00:00Z",
  "channelId": "UC123",
  "channelTitle": "Channel title",
  "duration": "PT12M33S",
  "categoryId": "27",
  "tags": ["tag1", "tag2"],
  "thumbnails": {
    "default": "https://...",
    "medium": "https://...",
    "high": "https://..."
  },
  "statistics": {
    "viewCount": "1000",
    "likeCount": "45",
    "commentCount": "8"
  },
  "status": {
    "privacyStatus": "public",
    "madeForKids": false
  }
}
```

#### 8.1.2 `videos_searchVideos`
Purpose:
- Search for videos and optionally refine results using channel- and
  creator-aware filters.

Primary upstream dependencies:
- `search.list`
- optional enrichment via `channels.list`

Input schema:
```json
{
  "type": "object",
  "required": ["query"],
  "additionalProperties": false,
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "rating", "relevance", "title", "viewCount"] },
    "publishedAfter": { "type": "string", "format": "date-time" },
    "publishedBefore": { "type": "string", "format": "date-time" },
    "channelId": { "type": "string", "minLength": 1 },
    "uniqueChannels": { "type": "boolean", "default": false },
    "channelMinSubscribers": { "type": "integer", "minimum": 0 },
    "channelMaxSubscribers": { "type": "integer", "minimum": 0 },
    "channelLastUploadAfter": { "type": "string", "format": "date-time" },
    "channelLastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": false },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    }
  }
}
```

Behavior notes:
- Base retrieval comes from video search.
- Channel-level filters may require enrichment of matched videos through
  channel lookups.
- `uniqueChannels=true` means at most one returned result per distinct channel.
- `creatorOnly` applies heuristic creator-vs-brand classification where enough
  metadata exists.
- `sortBy` may reorder the candidate set after enrichment.

Logical payload:
```json
{
  "items": [
    {
      "videoId": "abc123",
      "title": "Video title",
      "description": "...",
      "publishedAt": "2025-12-01T10:00:00Z",
      "channelId": "UC123",
      "channelTitle": "Channel title",
      "thumbnails": { "medium": "https://..." },
      "channel": {
        "subscriberCount": "5000",
        "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
        "creatorClassification": "creator"
      }
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 8.1.3 `videos_getStatistics`
Purpose:
- Return statistics for a single video.

Primary upstream dependency:
- `videos.list`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "videoId": "abc123",
  "statistics": {
    "viewCount": "1000",
    "likeCount": "45",
    "commentCount": "8",
    "favoriteCount": "0"
  }
}
```

Behavior notes:
- Hidden or unavailable counts SHOULD be omitted or returned as null-like
  values consistently; the final implementation must not invent counts.

### 8.2 Transcript Tools

#### 8.2.1 `transcripts_getTranscript`
Purpose:
- Retrieve the transcript of a video using the supported transcript strategy.

Primary upstream dependencies:
- `captions.list`
- `captions.download`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 }
  }
}
```

Behavior notes:
- Language resolution order is explicit `language`, then
  `YOUTUBE_TRANSCRIPT_LANG`, then `en`.
- If official caption access is required and not permitted, the tool MUST fail
  with a transcript-access-specific error rather than pretending the transcript
  does not exist.

Logical payload:
```json
{
  "videoId": "abc123",
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "duration": 4.2,
      "text": "Welcome to the video"
    }
  ],
  "fullText": "Welcome to the video ..."
}
```

#### 8.2.2 `transcripts_listLanguages`
Purpose:
- List available transcript or caption languages for a video.

Primary upstream dependency:
- `captions.list`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "videoId": "abc123",
  "languages": [
    {
      "language": "en",
      "captionTrackId": "Aeqx6m",
      "trackKind": "standard",
      "isAutoSynced": false
    },
    {
      "language": "es",
      "captionTrackId": "Bfdp2c",
      "trackKind": "ASR",
      "isAutoSynced": true
    }
  ]
}
```

#### 8.2.3 `transcripts_getTimestampedCaptions`
Purpose:
- Return transcript or caption data with explicit segment timing.

Primary upstream dependencies:
- `captions.list`
- `captions.download`

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 }
  }
}
```

Logical payload:
```json
{
  "videoId": "abc123",
  "language": "en",
  "captions": [
    {
      "start": 0.0,
      "end": 4.2,
      "text": "Welcome to the video"
    }
  ]
}
```

#### 8.2.4 `transcripts_searchTranscript`
Purpose:
- Search transcript text and return matching snippets with timing.

Primary dependencies:
- transcript retrieval flow
- in-server text search

Input schema:
```json
{
  "type": "object",
  "required": ["videoId", "query"],
  "additionalProperties": false,
  "properties": {
    "videoId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 },
    "maxMatches": { "type": "integer", "minimum": 1, "maximum": 100, "default": 20 }
  }
}
```

Behavior notes:
- This is a composite tool, not a direct YouTube endpoint.
- Match order SHOULD be deterministic.
- Returned snippets SHOULD include enough surrounding text to be interpretable.

Logical payload:
```json
{
  "videoId": "abc123",
  "query": "api key",
  "matches": [
    {
      "start": 125.1,
      "duration": 3.8,
      "text": "Set your API key in Secret Manager"
    }
  ]
}
```

### 8.3 Channel Tools

#### 8.3.1 `channels_getChannel`
Purpose:
- Return information about a single channel in a normalized and enriched shape.

Primary upstream dependencies:
- `channels.list`
- optional latest-upload enrichment via `search.list` or uploads-playlist path

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "title": "Channel name",
  "description": "...",
  "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
  "normalizedMetadata": {
    "country": "US",
    "defaultLanguage": "en",
    "joinedAt": "2020-01-01T00:00:00Z",
    "customUrl": "@channel",
    "emailsFound": ["contact@example.com"],
    "contactLinks": ["https://example.com"]
  },
  "heuristics": {
    "creatorClassification": "creator",
    "creatorSignals": ["has-face-forward-branding", "recent-upload-activity"]
  },
  "thumbnails": {
    "default": "https://...",
    "high": "https://..."
  }
}
```

Behavior notes:
- `normalizedMetadata` contains public normalized fields.
- `heuristics` contains inferred fields and must not be treated as canonical
  upstream truth.

#### 8.3.2 `channels_getChannels`
Purpose:
- Return information about multiple channels in one request.

Primary upstream dependency:
- `channels.list`

Input schema:
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
      "items": { "type": "string", "minLength": 1 }
    },
    "parts": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["snippet", "statistics", "brandingSettings", "contentDetails", "status", "topicDetails"]
      },
      "uniqueItems": true
    },
    "includeLatestUpload": { "type": "boolean", "default": true }
  }
}
```

Logical payload:
```json
{
  "items": [
    {
      "channelId": "UC123",
      "title": "Channel name",
      "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
      "normalizedMetadata": {
        "country": "US",
        "defaultLanguage": "en",
        "joinedAt": "2020-01-01T00:00:00Z",
        "customUrl": "@channel"
      }
    }
  ]
}
```

#### 8.3.3 `channels_searchChannels`
Purpose:
- Search for channels by handle, name, or general query.

Primary upstream dependencies:
- `search.list`
- optional enrichment via `channels.list`

Input schema:
```json
{
  "type": "object",
  "required": ["query"],
  "additionalProperties": false,
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "relevance", "title", "videoCount"] },
    "channelType": { "type": "string", "enum": ["any", "show"] },
    "minSubscribers": { "type": "integer", "minimum": 0 },
    "maxSubscribers": { "type": "integer", "minimum": 0 },
    "lastUploadAfter": { "type": "string", "format": "date-time" },
    "lastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": false },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    }
  }
}
```

Logical payload:
```json
{
  "items": [
    {
      "channelId": "UC123",
      "title": "Channel name",
      "normalizedMetadata": {
        "customUrl": "@channel",
        "joinedAt": "2020-01-01T00:00:00Z"
      },
      "statistics": {
        "subscriberCount": "5000"
      },
      "heuristics": {
        "creatorClassification": "creator"
      }
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 8.3.4 `channels_findCreators`
Purpose:
- Discover creator channels from matched or mentioning videos and then filter
  and rank them.

Primary upstream dependencies:
- `search.list`
- `channels.list`
- optional latest-activity or sample-video enrichment

Input schema:
```json
{
  "type": "object",
  "required": ["query"],
  "additionalProperties": false,
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "relevance", "title", "viewCount"] },
    "videoPublishedAfter": { "type": "string", "format": "date-time" },
    "videoPublishedBefore": { "type": "string", "format": "date-time" },
    "channelMinSubscribers": { "type": "integer", "minimum": 0 },
    "channelMaxSubscribers": { "type": "integer", "minimum": 0 },
    "channelLastUploadAfter": { "type": "string", "format": "date-time" },
    "channelLastUploadBefore": { "type": "string", "format": "date-time" },
    "creatorOnly": { "type": "boolean", "default": true },
    "sortBy": {
      "type": "string",
      "enum": ["relevance", "subscribers_asc", "subscribers_desc", "indie_priority", "recent_activity"],
      "default": "relevance"
    },
    "sampleVideosPerChannel": { "type": "integer", "minimum": 1, "maximum": 10, "default": 3 }
  }
}
```

Behavior notes:
- This is explicitly a composite higher-level tool.
- Candidate channels may be discovered from matched videos before final
  channel-level filtering.
- Returned sample videos are illustrative support data, not exhaustive channel
  inventories.

Logical payload:
```json
{
  "items": [
    {
      "channelId": "UC123",
      "title": "Creator channel",
      "statistics": { "subscriberCount": "12000" },
      "latestVideoPublishedAt": "2026-03-01T12:00:00Z",
      "heuristics": { "creatorClassification": "creator" },
      "sampleVideos": [
        {
          "videoId": "abc123",
          "title": "Mentioned video",
          "publishedAt": "2026-02-01T12:00:00Z"
        }
      ]
    }
  ]
}
```

#### 8.3.5 `channels_listVideos`
Purpose:
- List videos for a specific channel.

Primary upstream dependencies:
- `search.list` or uploads-playlist path

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Behavior notes:
- Final implementation must document whether it uses:
  - ranked search behavior
  - uploads-playlist behavior
  - or a documented combination of both

Logical payload:
```json
{
  "channelId": "UC123",
  "items": [
    {
      "videoId": "abc123",
      "title": "Channel video",
      "publishedAt": "2025-12-01T10:00:00Z",
      "description": "...",
      "thumbnails": { "medium": "https://..." }
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 8.3.6 `channels_listPlaylists`
Purpose:
- List playlists associated with a channel.

Primary upstream dependency:
- `playlists.list`

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "items": [
    {
      "playlistId": "PL123",
      "title": "Playlist title",
      "description": "...",
      "publishedAt": "2025-01-01T00:00:00Z",
      "itemCount": 12
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 8.3.7 `channels_getStatistics`
Purpose:
- Return statistics for a single channel.

Primary upstream dependency:
- `channels.list`

Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "statistics": {
    "viewCount": "100000",
    "subscriberCount": "5000",
    "videoCount": "124"
  }
}
```

#### 8.3.8 `channels_searchContent`
Purpose:
- Search within the content of a specific channel.

Primary upstream dependency:
- `search.list`

Input schema:
```json
{
  "type": "object",
  "required": ["channelId", "query"],
  "additionalProperties": false,
  "properties": {
    "channelId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 },
    "order": { "type": "string", "enum": ["date", "rating", "relevance", "title", "viewCount"] }
  }
}
```

Logical payload:
```json
{
  "channelId": "UC123",
  "query": "deployment",
  "items": [
    {
      "videoId": "abc123",
      "title": "Cloud Run deployment guide",
      "publishedAt": "2025-12-01T10:00:00Z",
      "description": "..."
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

### 8.4 Playlist Tools

#### 8.4.1 `playlists_getPlaylist`
Purpose:
- Return information about a playlist.

Primary upstream dependency:
- `playlists.list`

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 }
  }
}
```

Logical payload:
```json
{
  "playlistId": "PL123",
  "title": "Playlist title",
  "description": "...",
  "channelId": "UC123",
  "channelTitle": "Channel title",
  "publishedAt": "2025-01-01T00:00:00Z",
  "itemCount": 42
}
```

#### 8.4.2 `playlists_getPlaylistItems`
Purpose:
- Return the videos contained in a playlist.

Primary upstream dependency:
- `playlistItems.list`

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Logical payload:
```json
{
  "playlistId": "PL123",
  "items": [
    {
      "playlistItemId": "UEx123",
      "videoId": "abc123",
      "title": "Video title",
      "position": 0,
      "publishedAt": "2025-12-01T10:00:00Z"
    }
  ],
  "maxResults": 10,
  "nextPageToken": "token-or-null"
}
```

#### 8.4.3 `playlists_searchItems`
Purpose:
- Search within a playlist for matching items.

Primary dependencies:
- `playlistItems.list`
- in-server filtering and ranking

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId", "query"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "query": { "type": "string", "minLength": 1 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Behavior notes:
- This is a composite higher-level tool.
- Matching may inspect title and description fields from playlist items.

Logical payload:
```json
{
  "playlistId": "PL123",
  "query": "deployment",
  "items": [
    {
      "videoId": "abc123",
      "title": "Cloud Run deployment guide",
      "position": 3,
      "snippet": "..."
    }
  ]
}
```

#### 8.4.4 `playlists_getVideoTranscripts`
Purpose:
- Retrieve transcript data for videos in a playlist.

Primary dependencies:
- `playlistItems.list`
- transcript retrieval flow

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "additionalProperties": false,
  "properties": {
    "playlistId": { "type": "string", "minLength": 1 },
    "language": { "type": "string", "minLength": 2 },
    "maxResults": { "type": "integer", "minimum": 1, "maximum": 50, "default": 10 }
  }
}
```

Behavior notes:
- This is a bounded fan-out composite tool.
- The implementation MUST document whether `maxResults` limits:
  - playlist items fetched
  - transcripts attempted
  - or both

Logical payload:
```json
{
  "playlistId": "PL123",
  "items": [
    {
      "videoId": "abc123",
      "language": "en",
      "segments": [
        {
          "start": 0.0,
          "duration": 4.2,
          "text": "Welcome"
        }
      ],
      "transcriptAvailable": true
    }
  ]
}
```

## 9. Implementation Notes for Future Agents
- Do not expose raw YouTube API response shapes directly unless the public
  contract explicitly calls for them.
- Prefer one normalized shape per tool and keep optional expansions controlled.
- When adding heuristic fields, document:
  - what the field means
  - whether it is inferred
  - what upstream data influenced it
- When a tool is composite:
  - document the upstream call flow
  - document the ranking/filtering stage
  - document any bounded fan-out rules
- When a tool exposes `maxResults`, ensure the implementation does not silently
  exceed upstream quota expectations without documentation.

## 10. Acceptance Checks
- Every public Layer 3 tool has JSON-schema-validatable input.
- Every tool has a documented logical payload for MCP `structuredContent`.
- Composite tools are explicitly labeled as composite.
- Transcript tools document language fallback and auth-sensitive behavior.
- Channel enrichment tools document normalized and heuristic fields.
- Search tools document ranking and filtering semantics where implemented
  partly in-server.
