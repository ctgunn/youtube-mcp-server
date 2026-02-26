# Tool Specifications (v1)
## Project: YouTube MCP Server on Cloud Run

## 1. Conventions
- IDs: `videoId`, `channelId`, `playlistId`
- Search input name: `query` (mapped to YouTube `q`)
- Language: BCP-47 style `language` (for example, `en`, `en-US`, `es`)
- Search language param: `relevanceLanguage` (YouTube API term)
- Pagination: `pageToken`, `pageSize` (mapped to YouTube `maxResults`)
- Time values:
  - Durations: ISO 8601 duration (for example, `PT12M33S`)
  - Dates/times: ISO 8601 timestamp

## 2. Common Request Fields
- `pageSize` number, optional, default `10`, max `50`
- `pageToken` string, optional
- `order` string, optional (tool-specific allowed values)

## 2.1 YouTube API Mapping
- `query` -> `q`
- `pageSize` -> `maxResults`
- `language` (for transcript choice) is internal selection logic
- `relevanceLanguage` is passed to YouTube `search.list`

## 2.2 Endpoint Alignment Notes (Verified February 26, 2026)
- Video search and channel-content search use `search.list` with `type=video`.
- Channel videos can be implemented with:
  - `search.list` (`channelId`, `type=video`) for ranked/discoverability behavior.
  - or uploads playlist flow (`channels.list` -> `contentDetails.relatedPlaylists.uploads`, then `playlistItems.list`) for deterministic full listings.
- Playlist search is not a native YouTube endpoint and must be implemented by listing playlist items then filtering in server code.
- Transcript retrieval via YouTube Data API depends on `captions.list` and `captions.download`, which require OAuth authorization context for the target video/caption track.

## 3. Common Response Envelope
```json
{
  "success": true,
  "data": {},
  "meta": {
    "requestId": "req_123",
    "nextPageToken": "CAoQAA",
    "pageSize": 10,
    "totalResults": 123
  },
  "error": null
}
```

## 4. Common Error Shape
```json
{
  "success": false,
  "data": null,
  "meta": {
    "requestId": "req_123"
  },
  "error": {
    "code": "YOUTUBE_QUOTA_EXCEEDED",
    "message": "Daily quota limit exceeded.",
    "details": {
      "retryAfter": 3600
    }
  }
}
```

## 5. Tool Catalog

### 5.1 Video Information

#### 5.1.1 `youtube_get_video_details`
Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "properties": {
    "videoId": { "type": "string" },
    "include": {
      "type": "array",
      "items": { "type": "string", "enum": ["snippet", "contentDetails", "status"] }
    }
  }
}
```
Output `data`:
```json
{
  "videoId": "abc123",
  "title": "Video title",
  "description": "...",
  "publishedAt": "2025-12-01T10:00:00Z",
  "channelId": "UC...",
  "channelTitle": "Channel",
  "duration": "PT12M33S",
  "tags": ["tag1", "tag2"],
  "categoryId": "27",
  "thumbnails": {
    "default": "https://...",
    "medium": "https://...",
    "high": "https://..."
  },
  "status": {
    "privacyStatus": "public",
    "madeForKids": false
  }
}
```

#### 5.1.2 `youtube_list_channel_videos`
Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "properties": {
    "channelId": { "type": "string" },
    "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 },
    "pageToken": { "type": "string" },
    "order": { "type": "string", "enum": ["date", "relevance", "title", "viewCount"] },
    "publishedAfter": { "type": "string", "format": "date-time" },
    "publishedBefore": { "type": "string", "format": "date-time" }
  }
}
```
Output `data`:
```json
{
  "items": [
    {
      "videoId": "abc123",
      "title": "...",
      "publishedAt": "2025-12-01T10:00:00Z",
      "description": "...",
      "thumbnails": { "medium": "https://..." }
    }
  ]
}
```

#### 5.1.3 `youtube_get_video_statistics`
Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "properties": {
    "videoId": { "type": "string" }
  }
}
```
Output `data`:
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

#### 5.1.4 `youtube_search_videos`
Input schema:
```json
{
  "type": "object",
  "required": ["query"],
  "properties": {
    "query": { "type": "string", "minLength": 1 },
    "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 },
    "pageToken": { "type": "string" },
    "order": { "type": "string", "enum": ["date", "rating", "relevance", "title", "viewCount"] },
    "publishedAfter": { "type": "string", "format": "date-time" },
    "publishedBefore": { "type": "string", "format": "date-time" },
    "regionCode": { "type": "string", "minLength": 2, "maxLength": 2 },
    "relevanceLanguage": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "items": [
    {
      "videoId": "abc123",
      "title": "...",
      "channelId": "UC...",
      "channelTitle": "...",
      "publishedAt": "2025-12-01T10:00:00Z",
      "description": "...",
      "thumbnails": { "medium": "https://..." }
    }
  ]
}
```

### 5.2 Transcript Management

#### 5.2.1 `youtube_get_video_transcript`
Implementation note:
- Composite tool. Primary API flow is `captions.list(videoId)` -> choose caption track by `language` -> `captions.download(captionId)`.
- Requires authorized access to caption tracks for the target video.

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "properties": {
    "videoId": { "type": "string" },
    "captionTrackId": { "type": "string" },
    "language": { "type": "string" },
    "fallbackLanguages": {
      "type": "array",
      "items": { "type": "string" }
    },
    "includeTimestamps": { "type": "boolean", "default": true }
  }
}
```
Output `data`:
```json
{
  "videoId": "abc123",
  "captionTrackId": "Aeqx6m...",
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "duration": 4.2,
      "text": "Welcome to the video"
    }
  ],
  "fullText": "Welcome to the video ...",
  "requiresOwnerAuth": true
}
```

#### 5.2.2 `youtube_list_transcript_languages`
Implementation note:
- Mapped to `captions.list(videoId, part=snippet)`.

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "properties": {
    "videoId": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "videoId": "abc123",
  "languages": [
    { "language": "en", "captionTrackId": "Aeqx6m...", "trackKind": "standard", "isAutoSynced": false },
    { "language": "es", "captionTrackId": "Bfdp2c...", "trackKind": "ASR", "isAutoSynced": true }
  ]
}
```

#### 5.2.3 `youtube_get_timestamped_captions`
Implementation note:
- `captions.download` is keyed by caption track ID. If only `videoId` is provided, server must resolve a track first.

Input schema:
```json
{
  "type": "object",
  "required": ["videoId"],
  "properties": {
    "videoId": { "type": "string" },
    "captionTrackId": { "type": "string" },
    "language": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "videoId": "abc123",
  "captionTrackId": "Aeqx6m...",
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

#### 5.2.4 `youtube_search_transcript`
Implementation note:
- Composite tool. Not a native YouTube endpoint; it searches text after transcript retrieval.

Input schema:
```json
{
  "type": "object",
  "required": ["videoId", "query"],
  "properties": {
    "videoId": { "type": "string" },
    "query": { "type": "string", "minLength": 1 },
    "language": { "type": "string" },
    "maxMatches": { "type": "integer", "minimum": 1, "maximum": 100, "default": 20 }
  }
}
```
Output `data`:
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

### 5.3 Channel Management

#### 5.3.1 `youtube_get_channel_details`
Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "properties": {
    "channelId": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "channelId": "UC...",
  "title": "Channel name",
  "description": "...",
  "customUrl": "@channel",
  "publishedAt": "2020-01-01T00:00:00Z",
  "country": "US",
  "thumbnails": {
    "default": "https://...",
    "high": "https://..."
  }
}
```

#### 5.3.2 `youtube_list_channel_playlists`
Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "properties": {
    "channelId": { "type": "string" },
    "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 },
    "pageToken": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "items": [
    {
      "playlistId": "PL...",
      "title": "Playlist title",
      "description": "...",
      "publishedAt": "2025-01-01T00:00:00Z",
      "itemCount": 12
    }
  ]
}
```

#### 5.3.3 `youtube_get_channel_statistics`
Input schema:
```json
{
  "type": "object",
  "required": ["channelId"],
  "properties": {
    "channelId": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "channelId": "UC...",
  "statistics": {
    "viewCount": "100000",
    "subscriberCount": "5000",
    "videoCount": "124"
  }
}
```

#### 5.3.4 `youtube_search_channel_content`
Input schema:
```json
{
  "type": "object",
  "required": ["channelId", "query"],
  "properties": {
    "channelId": { "type": "string" },
    "query": { "type": "string", "minLength": 1 },
    "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 },
    "pageToken": { "type": "string" },
    "order": { "type": "string", "enum": ["date", "rating", "relevance", "title", "viewCount"] },
    "relevanceLanguage": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "items": [
    {
      "videoId": "abc123",
      "title": "...",
      "publishedAt": "2025-12-01T10:00:00Z",
      "description": "..."
    }
  ]
}
```

### 5.4 Playlist Management

#### 5.4.1 `youtube_list_playlist_items`
Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "properties": {
    "playlistId": { "type": "string" },
    "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 },
    "pageToken": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "playlistId": "PL...",
  "items": [
    {
      "playlistItemId": "UEx...",
      "videoId": "abc123",
      "title": "...",
      "position": 0,
      "publishedAt": "2025-12-01T10:00:00Z"
    }
  ]
}
```

#### 5.4.2 `youtube_get_playlist_details`
Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "properties": {
    "playlistId": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "playlistId": "PL...",
  "title": "Playlist title",
  "description": "...",
  "channelId": "UC...",
  "channelTitle": "...",
  "publishedAt": "2025-01-01T00:00:00Z",
  "itemCount": 42
}
```

#### 5.4.3 `youtube_search_playlist_items`
Implementation note:
- Composite tool. Use `playlistItems.list` then filter by query across title/description.

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId", "query"],
  "properties": {
    "playlistId": { "type": "string" },
    "query": { "type": "string", "minLength": 1 },
    "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 },
    "pageToken": { "type": "string" }
  }
}
```
Output `data`:
```json
{
  "playlistId": "PL...",
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

#### 5.4.4 `youtube_get_playlist_video_transcripts`
Implementation note:
- Composite tool. For each video from `playlistItems.list`, execute transcript flow described in 5.2.x.

Input schema:
```json
{
  "type": "object",
  "required": ["playlistId"],
  "properties": {
    "playlistId": { "type": "string" },
    "language": { "type": "string" },
    "pageSize": { "type": "integer", "minimum": 1, "maximum": 50 },
    "pageToken": { "type": "string" },
    "maxVideos": { "type": "integer", "minimum": 1, "maximum": 100, "default": 20 }
  }
}
```
Output `data`:
```json
{
  "playlistId": "PL...",
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

## 6. Error Codes (Recommended)
- `VALIDATION_ERROR`
- `RESOURCE_NOT_FOUND`
- `YOUTUBE_API_ERROR`
- `YOUTUBE_QUOTA_EXCEEDED`
- `TRANSCRIPT_UNAVAILABLE`
- `LANGUAGE_NOT_AVAILABLE`
- `TRANSCRIPT_REQUIRES_AUTHORIZED_CAPTION_ACCESS`
- `RATE_LIMITED`
- `INTERNAL_ERROR`

## 7. Acceptance Checks
- Every tool includes JSON-schema-validatable input.
- Every tool returns `success`, `data`, `meta`, `error`.
- Pagination fields appear where list/search endpoints are used.
- All transcript tools return timestamp-aware structures.
