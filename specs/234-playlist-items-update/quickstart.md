# Quickstart: Layer 2 Tool `playlistItems_update`

## Goal

Verify that `playlistItems_update` is planned, implemented, and reviewed as a low-level public Layer 2 MCP tool for `playlistItems.update`.

## Prerequisites

- Branch: `234-playlist-items-update`
- Feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/plan.md`
- Contract: `/Users/ctgunn/Projects/youtube-mcp-server/specs/234-playlist-items-update/contracts/playlistItems_update.md`
- Layer 1 dependency: `build_playlist_items_update_wrapper()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py`

## Expected Public Tool Behavior

`playlistItems_update` must:

- Map to `playlistItems.update`.
- Cost 50 official quota units per invocation.
- Require OAuth-backed access.
- Require supported `part` selection.
- Require a writable body that identifies the existing playlist item and preserves playlist/video context.
- Return a near-raw updated playlist-item result.
- Reject unsupported playlist-management, placement, content-detail, enrichment, analytics, recommendation, ranking, summarization, or automated curation workflows unless support is explicitly added to this public contract.

## Representative Successful Request

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

Expected review outcome:

- Tool metadata shows `playlistItems.update`.
- Tool metadata and examples show quota cost `50`.
- Tool metadata and examples show OAuth-backed access.
- Result contains endpoint context, selected part context, safe target identity context, safe writable update context, safe authorization context, and updated playlist-item fields.
- No credentials, raw upstream diagnostics, or fabricated enrichment fields appear in the result.

## Representative Validation Failures

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

Expected: safe validation feedback explaining that `part` is required.

### Missing Target Playlist Item Identifier

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

Expected: safe validation feedback explaining that `body.id` is required.

### Missing Playlist Identifier

```json
{
  "part": "snippet",
  "body": {
    "id": "playlist-item-123",
    "snippet": {
      "resourceId": {
        "kind": "youtube#video",
        "videoId": "video-123"
      }
    }
  }
}
```

Expected: safe validation feedback explaining that `body.snippet.playlistId` is required.

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

Expected: safe validation feedback explaining that `body.snippet.resourceId.videoId` is required.

### Unsupported Workflow

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

Expected: safe validation feedback explaining that ranking or higher-level playlist workflows are outside this endpoint tool.

## Red-Green-Refactor Verification

1. Red: Add failing focused checks before implementing behavior.

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py
```

Expected during Red: checks fail because `playlistItems_update` metadata, validation, handler, exports, or registration are absent.

2. Green: Implement the smallest endpoint-backed contract, validation, handler, result mapping, exports, and registry integration.

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py
```

Expected during Green: focused checks pass for discovery, validation, successful update mapping, safe errors, examples, and registration.

3. Refactor: Remove duplication, verify docstrings, and run full checks.

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
pytest
ruff check .
```

Expected final result: all focused tests pass, the full repository test suite passes, and Ruff reports no issues.

## Review Checklist

- Public discovery includes `playlistItems_update`.
- Metadata identifies `playlistItems.update`, OAuth-backed access, quota cost `50`, availability, mutation result shape, and examples.
- Valid request examples include target playlist-item identity, playlist/video context, and safe OAuth context.
- Failure examples include missing part, invalid part, missing target identity, missing playlist identifier, missing video reference, invalid body, unsupported writable field, missing OAuth, quota or upstream failure, and unsupported workflow request.
- All new or changed Python functions use reStructuredText docstrings with purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
