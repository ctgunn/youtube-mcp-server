# Contract: Layer 2 Tool `playlistItems_update`

## Purpose

Expose YouTube Data API `playlistItems.update` as a low-level public MCP tool named `playlistItems_update`. The contract stays close to the upstream update endpoint while making request validation, quota cost, OAuth-backed authorization, mutation semantics, result context, examples, and safe errors visible to MCP clients.

## Tool Identity

- **Public name**: `playlistItems_update`
- **Layer**: Layer 2 public endpoint-backed MCP tool
- **Mapped upstream operation**: `playlistItems.update`
- **Resource**: `playlistItems`
- **Method**: `update`
- **Official quota cost**: `50` units per call
- **Access mode**: OAuth-backed authorization required
- **Availability**: Available unless official documentation or local endpoint metadata records a caveat

## Scope

### In Scope

- Updating one existing playlist item through `playlistItems.update`
- Required part selection
- Required target playlist-item identity through `body.id`
- Required writable playlist/video context body
- Near-raw updated playlist-item results that preserve returned fields
- Safe validation, authorization, quota, invalid writable-field, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream errors

### Out of Scope

- Playlist item listing, insertion, or deletion
- Playlist search, playlist generation, playlist traversal, or playlist management beyond one update request
- Video, playlist, channel, transcript, analytics, recommendation, summarization, ranking, enrichment, or automated curation workflows
- Cross-endpoint fan-out or Layer 3 composition
- Persistent playlist-item storage

## Input Schema

The public input schema is an object with no additional properties.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `part` | Yes | string | Playlist item resource sections to return for the updated item. Must be non-empty and supported by the shared Layer 1 contract. |
| `body` | Yes | object | Playlist-item update payload. |
| `body.id` | Yes | string | Existing playlist-item identifier to update. |
| `body.snippet` | Yes | object | Writable snippet data for the playlist/video context. |
| `body.snippet.playlistId` | Yes | string | Target playlist identifier preserved for the updated item. |
| `body.snippet.resourceId` | Yes | object | Referenced resource identity. |
| `body.snippet.resourceId.videoId` | Yes | string | Referenced video identifier preserved for the target playlist item. |
| `body.snippet.resourceId.kind` | Conditional | string | Supported resource kind when supplied. Must represent a video resource if present. |

## Body Rules

- `body` must be an object.
- `body.id` is required and must be non-empty.
- `body.snippet` must be an object.
- `body.snippet.playlistId` is required and must be non-empty.
- `body.snippet.resourceId.videoId` is required and must be non-empty.
- Resource kind, when supplied, must not conflict with preserving a video resource.
- Read-only fields, unsupported fields, unsupported optional parameters, and conflicting update data must fail validation.
- Placement and content-detail update fields are accepted only when explicitly documented; unsupported or conflicting writable fields must fail validation.

## Metadata Requirements

Tool discovery metadata must include:

- Public tool name `playlistItems_update`
- Upstream identity `playlistItems.update`
- Resource `playlistItems`
- Method `update`
- Official quota cost `50`
- OAuth-backed access requirement
- Availability state
- Required part-selection guidance
- Required target playlist-item identity guidance
- Required writable update body guidance
- Mutation-result behavior
- Out-of-scope workflow boundaries
- Representative caller examples

## Successful Result Shape

A successful result must include safe, MCP-compatible structured data with:

- Endpoint identity `playlistItems.update`
- Source operation identity when included by shared conventions
- Quota cost `50`
- Selected part context
- Safe target playlist-item identity context
- Safe writable update context
- Safe authorization context
- Updated playlist item resource or equivalent updated-resource payload
- Returned upstream fields preserved according to selected parts

The result must not fabricate missing optional playlist item fields. It must not enrich the updated item with video, playlist, channel, transcript, ranking, analytics, recommendation, summarization, automated curation, or heuristic data.

## Error Contract

Errors must follow shared Layer 2 safe error conventions and must not expose credentials, API keys, OAuth tokens, raw upstream response bodies, stack traces, or unsafe request context.

| Scenario | Expected Category |
|----------|-------------------|
| Missing `part` | validation or invalid request |
| Unsupported or malformed `part` | validation or invalid request |
| Missing `body` | validation or invalid request |
| Non-object `body` | validation or invalid request |
| Missing `body.id` | validation or invalid request |
| Missing `body.snippet` | validation or invalid request |
| Missing playlist identifier | validation or invalid request |
| Missing referenced video identifier | validation or invalid request |
| Invalid resource identity | validation or invalid request |
| Unsupported body field or optional parameter | validation or invalid request |
| Unsupported placement or content-detail update field | validation or invalid request |
| Missing, invalid, or insufficient OAuth-backed access | authorization failure |
| Upstream quota limit | quota failure |
| Invalid writable-field update | invalid request or resource eligibility failure |
| Missing or unavailable playlist item, playlist, or video resource | missing-resource or upstream failure category |
| Upstream service unavailable | unavailable-service category |
| Deprecated or unavailable endpoint behavior | deprecated-behavior or availability category |
| Unexpected upstream failure | unexpected upstream failure category |

## Representative Examples

### Update a Playlist Item

```json
{
  "part": "snippet",
  "body": {
    "id": "playlist-item-123",
    "snippet": {
      "playlistId": "PL123",
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "video-123"
      }
    }
  }
}
```

Expected outcome: a successful `playlistItems.update` result with quota cost `50`, selected part context, safe target identity context, writable update context, OAuth-backed access context, and the updated playlist-item resource.

### Missing Target Identity

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "playlistId": "PL123",
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "video-123"
      }
    }
  }
}
```

Expected outcome: safe validation error explaining that `body.id` is required.

### Missing Part

```json
{
  "body": {
    "id": "playlist-item-123",
    "snippet": {
      "playlistId": "PL123",
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "video-123"
      }
    }
  }
}
```

Expected outcome: safe validation error explaining that part selection is required.

### Missing Video Reference

```json
{
  "part": "snippet",
  "body": {
    "id": "playlist-item-123",
    "snippet": {
      "playlistId": "PL123",
      "resourceId": {
        "kind": "youtube#video"
      }
    }
  }
}
```

Expected outcome: safe validation error explaining that the referenced video identifier is required.

### Unsupported Writable Field

```json
{
  "part": "snippet",
  "body": {
    "id": "playlist-item-123",
    "snippet": {
      "playlistId": "PL123",
      "position": 0,
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "video-123"
      }
    }
  }
}
```

Expected outcome: safe validation error unless placement update support has been explicitly added to the public contract.

### Unsupported Workflow Request

```json
{
  "part": "snippet",
  "body": {
    "id": "playlist-item-123",
    "snippet": {
      "playlistId": "PL123",
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "video-123"
      }
    }
  },
  "rankPlaylist": true
}
```

Expected outcome: safe validation error explaining that ranking and higher-level playlist workflows are outside this low-level endpoint tool.

## Acceptance Contract

An implementation satisfies this contract when:

- `playlistItems_update` appears in public tool discovery and default registry output.
- Discovery metadata, description, usage notes, caveats, and examples display `playlistItems.update`, quota cost `50`, and OAuth-backed access.
- Valid OAuth-backed update requests return near-raw updated playlist-item results.
- Invalid part, body, target identity, writable update data, unsupported field, authorization, quota, invalid writable-field, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are categorized safely and distinctly.
- All new or changed Python functions include reStructuredText docstrings that describe purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
