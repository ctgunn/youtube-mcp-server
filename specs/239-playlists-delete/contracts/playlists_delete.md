# Contract: `playlists_delete`

## Public Identity

- **Tool name**: `playlists_delete`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped operation**: YouTube resource `playlists`, method `delete`
- **Operation key**: `playlists.delete`
- **Quota cost**: `50` official quota units per invocation
- **Availability**: Active unless implementation discovers an official documentation caveat that must be recorded
- **Auth mode**: OAuth-required user authorization
- **Scope**: Low-level playlist deletion only

## Discovery Metadata Requirements

Discovery metadata, descriptions, usage notes, caveats, and examples must make the following visible before invocation:

- Public tool name `playlists_delete`
- Upstream operation `playlists.delete`
- Quota cost `50`
- OAuth-backed user authorization requirement
- Required target playlist identity through `id`
- Successful calls delete user-visible playlists
- Successful deletion returns an acknowledgment, not a fabricated playlist resource
- Repeat-delete caveat
- Safe failure categories
- Out-of-scope workflows, including playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, restore, rollback, idempotency guarantees, and cross-endpoint enrichment

## Input Contract

```json
{
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1
    }
  },
  "additionalProperties": false
}
```

## Input Validation Rules

- `id` is required and must identify the target playlist.
- `id` must be a non-empty string after normalization.
- The request targets exactly one playlist per invocation.
- `part`, `body`, list selectors, paging fields, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, restore or rollback instructions, and higher-level workflow instructions are rejected before endpoint execution.
- Eligible OAuth-backed user authorization is required for execution.

## Success Result Contract

Successful calls return a deletion acknowledgment with safe context:

```json
{
  "endpoint": "playlists.delete",
  "quotaCost": 50,
  "deleted": true,
  "acknowledged": true,
  "auth": {
    "mode": "oauth_required"
  },
  "target": {
    "playlistId": "PL123"
  }
}
```

Result rules:
- `endpoint` must be `playlists.delete`.
- `quotaCost` must be `50`.
- `deleted` and `acknowledged` must identify the result as a successful destructive deletion outcome.
- `auth` must identify the safe access mode, not credentials.
- `target` must identify the target playlist without exposing credentials or unsafe diagnostics.
- The result must not fabricate deleted playlist fields or include playlist items, videos, playlist images, transcripts, analytics, ranking, recommendation, restore, rollback, or enrichment fields.

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing `id`, blank `id`, non-string `id`, unsupported field, unsupported request body, unsupported part selection, unsupported selector, unsupported modifier, or out-of-scope workflow request
- `authentication_failed`: Required OAuth credential material missing or invalid
- `authorization_failed`: Caller lacks access to delete the target playlist for the authorized account or channel
- `quota_exhausted`: Upstream quota failure
- `resource_not_found`: Target playlist is missing, already deleted, or unavailable to the authorized caller
- `endpoint_unavailable`: Upstream service unavailable or timeout category
- `deprecated_endpoint`: Official endpoint behavior is deprecated or unavailable
- `upstream_failure`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Successful Playlist Deletion

```json
{
  "id": "PL123"
}
```

Expected context:
- Endpoint `playlists.delete`
- Quota cost `50`
- OAuth-backed access mode
- Deletion acknowledgment
- Destructive mutation warning visible before invocation

### Missing Target Identity Failure

```json
{}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `id`

### Malformed Target Identity Failure

```json
{
  "id": ""
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `id`

### Unsupported Field Failure

```json
{
  "id": "PL123",
  "part": "snippet"
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `part`

### OAuth Failure

```json
{
  "id": "PL123"
}
```

Expected error when OAuth-backed access is missing or invalid:
- Category `authentication_failed`
- Safe auth mode detail only

### Insufficient Authorization Failure

```json
{
  "id": "PL_NOT_OWNED"
}
```

Expected error:
- Category `authorization_failed`
- Safe target context only

### Missing Resource or Already Deleted Failure

```json
{
  "id": "PL_ALREADY_DELETED"
}
```

Expected error:
- Category `resource_not_found`
- Safe target context only

### Quota or Upstream Failure

```json
{
  "id": "PL123"
}
```

Expected error:
- Category `quota_exhausted`, `endpoint_unavailable`, `deprecated_endpoint`, or `upstream_failure`
- Sanitized details only

### Repeat-Delete Caveat

If a caller retries after an unclear outcome, the second request may return `resource_not_found` if the first deletion succeeded. The tool must not promise restore, rollback, or idempotent success.

### Out-of-Scope Playlist Management Request

```json
{
  "id": "PL123",
  "restore": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `restore`
