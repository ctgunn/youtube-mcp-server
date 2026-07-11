# Contract: `playlists_insert`

## Public Identity

- **Tool name**: `playlists_insert`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped operation**: YouTube resource `playlists`, method `insert`
- **Operation key**: `playlists.insert`
- **Quota cost**: `50` official quota units per invocation
- **Availability**: Active unless implementation discovers an official documentation caveat that must be recorded
- **Auth mode**: OAuth-required user authorization
- **Scope**: Low-level playlist creation only

## Discovery Metadata Requirements

Discovery metadata, descriptions, usage notes, caveats, and examples must make the following visible before invocation:

- Public tool name `playlists_insert`
- Upstream operation `playlists.insert`
- Quota cost `50`
- OAuth-backed user authorization requirement
- Required `part` selection
- Required writable playlist body, including `body.snippet.title`
- Successful calls create user-visible playlists
- Returned result represents the created playlist resource
- Retry or duplicate-create caveat
- Safe failure categories
- Out-of-scope workflows, including playlist update, deletion, playlist item insertion, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, duplicate-prevention, and cross-endpoint enrichment

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
      "required": ["snippet"],
      "properties": {
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
- `body.snippet` is required and must be an object.
- `body.snippet.title` is required and must be non-empty.
- Optional write fields such as `body.snippet.description`, `body.status`, or `body.localizations` are rejected unless the implementation deliberately expands the public contract.
- Unsupported fields, unsupported modifiers, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, and higher-level workflow instructions are rejected before endpoint execution.
- Eligible OAuth-backed user authorization is required for execution.

## Success Result Contract

Successful calls return a near-raw created playlist resource with safe context:

```json
{
  "endpoint": "playlists.insert",
  "quotaCost": 50,
  "requestedParts": ["snippet"],
  "created": true,
  "auth": {
    "mode": "oauth_required"
  },
  "creation": {
    "writableFields": ["body.snippet.title"]
  },
  "playlist": {
    "id": "PL123",
    "snippet": {
      "title": "Example playlist"
    }
  }
}
```

Result rules:
- `endpoint` must be `playlists.insert`.
- `quotaCost` must be `50`.
- `requestedParts` must reflect caller-selected supported parts.
- `created` must identify the result as a successful creation outcome.
- `auth` must identify the safe access mode, not credentials.
- `creation` must identify safe writable-field context without exposing credentials or unsafe request diagnostics.
- `playlist` must contain the returned created playlist resource.
- Returned playlist fields must preserve upstream data for selected parts without fabricated playlist item, video, channel, image, transcript, analytics, ranking, recommendation, or enrichment fields.

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing part, invalid part, missing body, malformed body, missing snippet, missing title, unsupported write field, unsupported field, unsupported modifier, or out-of-scope workflow request
- `authentication_failed`: Required OAuth credential material missing or invalid
- `authorization_failed`: Caller lacks access to create playlists for the authorized account or channel
- `quota_exhausted`: Upstream quota failure
- `forbidden_create`: Upstream refuses the create operation for policy, permission, account, or playlist-rule reasons
- `resource_not_found`: Upstream missing-resource or unavailable selected resource category
- `endpoint_unavailable`: Upstream service unavailable or timeout category
- `deprecated_endpoint`: Official endpoint behavior is deprecated or unavailable
- `upstream_failure`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Successful Playlist Creation

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Research playlist"
    }
  }
}
```

Expected context:
- Endpoint `playlists.insert`
- Quota cost `50`
- OAuth-backed access mode
- Created playlist result
- Mutation warning visible before invocation

### Missing Part Failure

```json
{
  "body": {
    "snippet": {
      "title": "Research playlist"
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
    "snippet": {
      "title": "Research playlist"
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `part`

### Missing Title Failure

```json
{
  "part": "snippet",
  "body": {
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
    "snippet": {
      "title": "Research playlist",
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
    "snippet": {
      "title": "Research playlist"
    }
  }
}
```

Expected error when no eligible OAuth access is available:
- Category `authentication_failed`
- Safe detail identifying OAuth-required access

### Upstream Create Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Policy rejected playlist"
    }
  }
}
```

Expected error when upstream rejects creation:
- Safe category such as `authorization_failed`, `forbidden_create`, `quota_exhausted`, `endpoint_unavailable`, or `upstream_failure`
- Sanitized details only

### Out-of-Scope Playlist Management Request

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Research playlist"
    }
  },
  "insertPlaylistItems": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `insertPlaylistItems`

## Duplicate-Create Caveat

The tool does not promise idempotent creation. If a caller retries after a timeout or unclear upstream outcome, another playlist may be created. Duplicate detection, idempotency keys, playlist lookup, and cleanup workflows are out of scope for this low-level endpoint tool.
