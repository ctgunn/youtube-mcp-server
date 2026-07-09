# Contract: Layer 2 Tool `playlistItems_insert`

## Purpose

Expose YouTube Data API `playlistItems.insert` as a low-level public MCP tool named `playlistItems_insert`. The contract stays close to the upstream insert endpoint while making request validation, quota cost, OAuth-backed authorization, mutation semantics, result context, examples, and safe errors visible to MCP clients.

## Tool Identity

- **Public name**: `playlistItems_insert`
- **Layer**: Layer 2 public endpoint-backed MCP tool
- **Mapped upstream operation**: `playlistItems.insert`
- **Resource**: `playlistItems`
- **Method**: `insert`
- **Official quota cost**: `50` units per call
- **Access mode**: OAuth-backed authorization required
- **Availability**: Available unless official documentation or local endpoint metadata records a caveat

## Scope

### In Scope

- Adding a video to a playlist through `playlistItems.insert`
- Required part selection
- Required writable playlist/video assignment body
- Supported placement behavior only when explicitly documented
- Near-raw created playlist-item results that preserve returned fields
- Safe validation, authorization, quota, duplicate or ineligible resource, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream errors

### Out of Scope

- Playlist item listing, update, or deletion
- Playlist search, playlist generation, playlist traversal, or playlist management beyond one insert request
- Video, playlist, channel, transcript, analytics, recommendation, summarization, ranking, enrichment, or automated curation workflows
- Cross-endpoint fan-out or Layer 3 composition
- Persistent playlist-item storage

## Input Schema

The public input schema is an object with no additional properties.

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `part` | Yes | string | Playlist item resource sections to return for the created item. Must be non-empty and supported by the shared Layer 1 contract. |
| `body` | Yes | object | Writable playlist-item creation payload. |
| `body.snippet` | Yes | object | Writable snippet data for the playlist/video assignment. |
| `body.snippet.playlistId` | Yes | string | Target playlist identifier. |
| `body.snippet.resourceId` | Yes | object | Referenced resource identity. |
| `body.snippet.resourceId.videoId` | Yes | string | Referenced video identifier to add to the target playlist. |
| `body.snippet.resourceId.kind` | Conditional | string | Supported resource kind when supplied. Must represent a video resource if present. |
| `body.snippet.position` | No | integer | Supported insertion position only if the implementation contract explicitly accepts placement. |

## Body Rules

- `body` must be an object.
- `body.snippet` must be an object.
- `body.snippet.playlistId` is required and must be non-empty.
- `body.snippet.resourceId.videoId` is required and must be non-empty.
- Resource kind, when supplied, must not conflict with adding a video resource.
- Read-only fields, unsupported fields, unsupported optional parameters, and conflicting assignment data must fail validation.
- Placement details are accepted only when explicitly documented; unsupported or conflicting placement details must fail validation.

## Metadata Requirements

Tool discovery metadata must include:

- Public tool name `playlistItems_insert`
- Upstream identity `playlistItems.insert`
- Resource `playlistItems`
- Method `insert`
- Official quota cost `50`
- OAuth-backed access requirement
- Availability state
- Required part-selection guidance
- Required playlist/video assignment guidance
- Supported placement guidance
- Mutation-result behavior
- Out-of-scope workflow boundaries
- Representative caller examples

## Successful Result Shape

A successful result must include safe, MCP-compatible structured data with:

- Endpoint identity `playlistItems.insert`
- Source operation identity when included by shared conventions
- Quota cost `50`
- Selected part context
- Safe playlist/video assignment context
- Safe placement context when supplied and accepted
- Safe authorization context
- Created playlist item resource or equivalent created-resource payload
- Returned upstream fields preserved according to selected parts

The result must not fabricate missing optional playlist item fields. It must not enrich the created item with video, playlist, channel, transcript, ranking, analytics, recommendation, summarization, automated curation, or heuristic data.

## Error Contract

Errors must follow shared Layer 2 safe error conventions and must not expose credentials, API keys, OAuth tokens, raw upstream response bodies, stack traces, or unsafe request context.

| Scenario | Expected Category |
|----------|-------------------|
| Missing `part` | validation or invalid request |
| Unsupported or malformed `part` | validation or invalid request |
| Missing `body` | validation or invalid request |
| Non-object `body` | validation or invalid request |
| Missing `body.snippet` | validation or invalid request |
| Missing playlist identifier | validation or invalid request |
| Missing referenced video identifier | validation or invalid request |
| Invalid resource identity | validation or invalid request |
| Unsupported body field or optional parameter | validation or invalid request |
| Unsupported or conflicting placement detail | validation or invalid request |
| Missing, invalid, or insufficient OAuth-backed access | authorization failure |
| Upstream quota limit | quota failure |
| Duplicate or ineligible video/resource | invalid request or resource eligibility failure |
| Missing or unavailable playlist/video resource | missing-resource or upstream failure category |
| Upstream service unavailable | unavailable-service category |
| Deprecated or unavailable endpoint behavior | deprecated-behavior or availability category |
| Unexpected upstream failure | unexpected upstream failure category |

## Representative Examples

### Add a Video to a Playlist

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

Expected outcome: a successful `playlistItems.insert` result with quota cost `50`, selected part context, safe playlist/video assignment context, OAuth-backed access context, and the created playlist-item resource.

### Add a Video with Supported Placement

```json
{
  "part": "snippet",
  "body": {
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

Expected outcome: a successful insertion only if placement is explicitly supported by the implementation contract; otherwise safe validation feedback identifying unsupported placement.

### Missing Part

```json
{
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

Expected outcome: safe validation error explaining that part selection is required.

### Missing Video Reference

```json
{
  "part": "snippet",
  "body": {
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

### Unsupported Workflow Request

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
  },
  "generatePlaylist": true
}
```

Expected outcome: safe validation error explaining that playlist generation and unsupported fields are outside this low-level endpoint tool.

## Acceptance Contract

An implementation satisfies this contract when:

- `playlistItems_insert` appears in public tool discovery and default registry output.
- Discovery metadata, description, usage notes, caveats, and examples display `playlistItems.insert`, quota cost `50`, and OAuth-backed access.
- Valid OAuth-backed insertion requests return near-raw created playlist-item results.
- Invalid part, body, assignment, placement, unsupported field, authorization, quota, duplicate or ineligible resource, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are categorized safely and distinctly.
- All new or changed Python functions include reStructuredText docstrings that describe purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
