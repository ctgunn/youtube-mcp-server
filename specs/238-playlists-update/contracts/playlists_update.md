# Contract: `playlists_update`

## Public Identity

- **Tool name**: `playlists_update`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped operation**: YouTube resource `playlists`, method `update`
- **Operation key**: `playlists.update`
- **Quota cost**: `50` official quota units per invocation
- **Availability**: Active unless implementation discovers an official documentation caveat that must be recorded
- **Auth mode**: OAuth-required user authorization
- **Scope**: Low-level playlist update only

## Discovery Metadata Requirements

Discovery metadata, descriptions, usage notes, caveats, and examples must make the following visible before invocation:

- Public tool name `playlists_update`
- Upstream operation `playlists.update`
- Quota cost `50`
- OAuth-backed user authorization requirement
- Required `part` selection
- Required target playlist identity through `body.id`
- Required writable playlist body, including `body.snippet.title`
- Successful calls mutate user-visible playlist details
- Returned result represents the updated playlist resource
- Repeat-request caveat
- Safe failure categories
- Out-of-scope workflows, including playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, rollback, conflict detection, and cross-endpoint enrichment

## Input Contract

```json
{
  "type": "object",
  "required": ["part", "body"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1
    },
    "body": {
      "type": "object",
      "required": ["id", "snippet"],
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1
        },
        "snippet": {
          "type": "object",
          "required": ["title"],
          "properties": {
            "title": {
              "type": "string",
              "minLength": 1
            }
          },
          "additionalProperties": false
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

## Input Validation Rules

- `part` is required and must contain supported writable playlist part selection.
- The supported minimum part-selection path is `snippet`.
- `body` is required and must be an object.
- `body.id` is required and must identify the target playlist.
- `body.snippet` is required and must be an object.
- `body.snippet.title` is required and must be non-empty.
- Optional write fields such as `body.snippet.description`, `body.status`, or `body.localizations` are rejected unless the implementation deliberately expands the public contract.
- Unsupported fields, unsupported modifiers, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, and higher-level workflow instructions are rejected before endpoint execution.
- Eligible OAuth-backed user authorization is required for execution.

## Success Result Contract

Successful calls return a near-raw updated playlist resource with safe context:

```json
{
  "endpoint": "playlists.update",
  "quotaCost": 50,
  "requestedParts": ["snippet"],
  "updated": true,
  "auth": {
    "mode": "oauth_required"
  },
  "target": {
    "playlistId": "PL123"
  },
  "update": {
    "writableFields": ["body.snippet.title"]
  },
  "playlist": {
    "id": "PL123",
    "snippet": {
      "title": "Updated research playlist"
    }
  }
}
```

Result rules:
- `endpoint` must be `playlists.update`.
- `quotaCost` must be `50`.
- `requestedParts` must reflect caller-selected supported parts.
- `updated` must identify the result as a successful update outcome.
- `auth` must identify the safe access mode, not credentials.
- `target` must identify the target playlist without exposing credentials or unsafe diagnostics.
- `update` must identify safe writable-field context without exposing credentials or unsafe request diagnostics.
- `playlist` must contain the returned updated playlist resource.
- Returned playlist fields must preserve upstream data for selected parts without fabricated playlist item, video, channel, image, transcript, analytics, ranking, recommendation, rollback, conflict, or enrichment fields.

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing part, invalid part, missing body, malformed body, missing target playlist identity, missing snippet, missing title, unsupported write field, unsupported field, unsupported modifier, or out-of-scope workflow request
- `authentication_failed`: Required OAuth credential material missing or invalid
- `authorization_failed`: Caller lacks access to update the target playlist for the authorized account or channel
- `quota_exhausted`: Upstream quota failure
- `forbidden_update`: Upstream refuses the update operation for policy, permission, account, playlist ownership, or playlist-rule reasons
- `resource_not_found`: Target playlist is missing or unavailable to the authorized caller
- `endpoint_unavailable`: Upstream service unavailable or timeout category
- `deprecated_endpoint`: Official endpoint behavior is deprecated or unavailable
- `upstream_failure`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Successful Playlist Update

```json
{
  "part": "snippet",
  "body": {
    "id": "PL123",
    "snippet": {
      "title": "Updated research playlist"
    }
  }
}
```

Expected context:
- Endpoint `playlists.update`
- Quota cost `50`
- OAuth-backed access mode
- Updated playlist result
- Mutation warning visible before invocation

### Missing Part Failure

```json
{
  "body": {
    "id": "PL123",
    "snippet": {
      "title": "Updated research playlist"
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `part`

### Invalid Part Failure

```json
{
  "part": "status",
  "body": {
    "id": "PL123",
    "snippet": {
      "title": "Updated research playlist"
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `part`

### Missing Target Playlist Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Updated research playlist"
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `body.id`

### Missing Title Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "PL123",
    "snippet": {}
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `body.snippet.title`

### Unsupported Write Field Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "PL123",
    "snippet": {
      "title": "Updated research playlist",
      "description": "Optional write field not supported by this slice"
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying the unsupported writable field

### Missing Authorization Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "PL123",
    "snippet": {
      "title": "Updated research playlist"
    }
  }
}
```

Expected error when no eligible OAuth access is available:
- Category `authentication_failed`
- Safe detail identifying OAuth-required access

### Upstream Update Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "PL_NO_ACCESS",
    "snippet": {
      "title": "Policy rejected playlist"
    }
  }
}
```

Expected error when upstream rejects update:
- Safe category such as `authorization_failed`, `forbidden_update`, `resource_not_found`, `quota_exhausted`, `endpoint_unavailable`, or `upstream_failure`
- Sanitized details only

### Out-of-Scope Playlist Management Request

```json
{
  "part": "snippet",
  "body": {
    "id": "PL123",
    "snippet": {
      "title": "Updated research playlist"
    }
  },
  "insertPlaylistItems": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying the unsupported workflow field
