# Contract: Layer 2 `channelSections_update` Tool

## Public Tool Identity

- **Tool name**: `channelSections_update`
- **Mapped upstream operation**: `channelSections.update`
- **Resource family**: `channel_sections`
- **Layer**: Layer 2 endpoint-backed public MCP tool
- **Official quota cost**: `50` units per invocation
- **Auth mode**: `oauth_required`
- **Availability**: Active, with OAuth, partner-context, writable-field, overwrite, and content-structure caveats

## Scope

`channelSections_update` updates one existing YouTube channel section through the upstream channel-section update endpoint and returns the updated resource in a near-raw shape.

The tool does not:

- Sort, reorder, patch, replace multiple sections, insert, or delete channel sections.
- Create playlists, channels, videos, captions, comments, analytics records, or channel branding assets.
- Expand supplied playlist or channel references into full resources.
- Rank, enrich, summarize, analyze, or recommend channel sections.
- Call `channelSections.list`, `channelSections.insert`, `channelSections.delete`, `playlistItems.list`, `playlists.insert`, `videos.list`, `channels.update`, `search.list`, or analytics endpoints.
- Persist updated-resource state or layout history.

## Input Contract

The input is a JSON-compatible object.

```json
{
  "type": "object",
  "required": ["part", "body"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "enum": ["contentDetails", "id", "snippet"]
    },
    "body": {
      "type": "object",
      "required": ["id", "snippet"],
      "properties": {
        "id": { "type": "string", "minLength": 1 },
        "snippet": {
          "type": "object",
          "required": ["type"],
          "properties": {
            "type": { "type": "string", "minLength": 1 },
            "title": { "type": "string", "minLength": 1 },
            "position": { "type": "integer", "minimum": 0 }
          },
          "additionalProperties": false
        },
        "contentDetails": {
          "type": "object",
          "properties": {
            "playlists": {
              "type": "array",
              "items": { "type": "string", "minLength": 1 }
            },
            "channels": {
              "type": "array",
              "items": { "type": "string", "minLength": 1 }
            }
          },
          "additionalProperties": false
        }
      },
      "additionalProperties": false
    },
    "onBehalfOfContentOwner": {
      "type": "string",
      "minLength": 1
    }
  },
  "additionalProperties": false
}
```

If the implementation supports comma-separated `part` values, the same allowed values apply to each selected part: `contentDetails`, `id`, and `snippet`.

### Input Rules

- `part` is required and must be non-empty.
- Officially documented update part values include `contentDetails`, `id`, and `snippet`.
- `body` is required and must be an object.
- `body.id` is required and identifies the existing channel section being updated.
- `body.snippet.type` is required.
- Supported writable body fields are `body.id`, `body.snippet.type`, `body.snippet.title`, `body.snippet.position`, `body.contentDetails.playlists[]`, and `body.contentDetails.channels[]`.
- `singlePlaylist` requires exactly one playlist reference.
- `multiplePlaylists` requires playlist references and a title.
- `multipleChannels` requires channel references and a title.
- Playlist references must not be supplied for section types that do not expect playlists.
- Channel references must not be supplied for section types that do not expect channels.
- Duplicate playlist or channel references are invalid.
- `onBehalfOfContentOwner` is authorization-sensitive, intended exclusively for eligible YouTube content partners, and must not be presented as public API-key behavior.
- Update semantics are overwrite-sensitive: omitted existing properties can be deleted by the upstream update behavior, so callers must submit the intended full writable state for selected fields.
- Unsupported fields, query-search fields, channel update fields, analytics fields, video expansion fields, playlist creation fields, layout recommendation fields, sorting instructions, patch instructions, multi-section replacement instructions, and enrichment instructions must be rejected or clearly flagged as outside this endpoint contract.

## Discovery Metadata Requirements

Tool discovery metadata must include:

- `name`: `channelSections_update`
- `upstream.resource`: `channelSections`
- `upstream.method`: `update`
- `upstream.operationKey`: `channelSections.update`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active availability with OAuth, partner-context, body-shape, writable-field, overwrite, and content-rule caveats
- `resourceFamily`: `channel_sections`
- `inputContract`: the public input contract
- `responseConvention`: updated-resource convention
- `responseBoundary`: near-raw boundary
- `usageNotes`: quota, OAuth, part-selection, target section identity, body, `snippet.type`, writable fields, overwrite behavior, content-rule, partner-context, and out-of-scope notes
- `caveats`: owner-scoped write behavior, content partner context, section-type-specific content behavior, overwrite-sensitive update behavior, and out-of-scope higher-level workflow caveats

Discovery descriptions and usage notes must visibly include `Quota cost: 50`.

## Response Contract

Successful responses must preserve the upstream-updated channel-section resource.

Representative successful shape:

```json
{
  "endpoint": "channelSections.update",
  "quotaCost": 50,
  "updated": true,
  "requestedParts": ["snippet", "contentDetails"],
  "item": {
    "kind": "youtube#channelSection",
    "etag": "etag-value",
    "id": "section-123",
    "snippet": {
      "type": "singlePlaylist",
      "channelId": "UC123",
      "position": 3
    },
    "contentDetails": {
      "playlists": ["PL123"]
    }
  }
}
```

Representative partner-context result shape:

```json
{
  "endpoint": "channelSections.update",
  "quotaCost": 50,
  "updated": true,
  "requestedParts": ["snippet"],
  "partnerContext": {
    "contentOwnerDelegation": true
  },
  "item": {
    "kind": "youtube#channelSection",
    "id": "section-123",
    "snippet": {
      "type": "multipleChannels"
    }
  }
}
```

Response rules:

- Preserve returned channel-section resource fields in `item`.
- Include requested part names after safe normalization.
- Include safe operation context such as endpoint identity, quota cost, and `updated`.
- Include safe partner-context flags where relevant.
- Do not fabricate optional fields that the endpoint did not return.
- Do not fabricate playlist item lists, video metadata, channel analytics, search ranking, layout recommendations, patch state, deletion state, or enriched summaries.

## Error Contract

The tool must surface safe shared Layer 2 error categories:

- `invalid_request`
- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `resource_not_found`
- `endpoint_unavailable`
- `upstream_failure`

Endpoint-specific invalid request examples:

- Missing `part`.
- Unsupported part name.
- Missing `body`.
- Body is not an object.
- Missing `body.id`.
- Invalid `body.id`.
- Missing `body.snippet`.
- Missing `body.snippet.type`.
- Missing `contentDetails` when the selected section type requires referenced playlists or channels.
- Playlist references provided for section types that do not accept playlists.
- Channel references provided for section types that do not accept channels.
- Duplicate playlist or channel references.
- Missing title when required for `multiplePlaylists` or `multipleChannels`.
- Invalid position.
- Too many playlist or channel references.
- Unsupported body fields.
- Unsupported optional parameters.
- Unsupported higher-level workflow fields such as sorting, patching, multi-section replacement, playlist creation, video expansion, analytics, ranking, recommendations, branding, or bulk editing.

Endpoint-specific upstream failure examples:

- Target channel section cannot be edited.
- Target channel section cannot be found.
- Referenced channel is inactive or cannot be found.
- Referenced playlist is private or cannot be found.
- Authenticated caller lacks access to the target section or partner context.

Security rules:

- Errors must not expose OAuth tokens, API keys, stack traces, private channel data, CMS account identifiers, owner identifiers, or secret values.
- Authorization failures must be distinguishable from invalid content-structure failures.
- Partner-context failures must identify partner-scoped authorization requirements without exposing CMS account details.
- Referenced-resource failures must identify safe resource categories without exposing private data beyond caller-provided identifiers when avoidable.

## Required Examples

The implementation must provide safe caller-facing examples for:

- Authorized title or position update.
- Authorized playlist-backed section update.
- Authorized channel-backed section update.
- Supported partner-context update.
- Missing OAuth authorization failure.
- Missing `part` validation failure.
- Missing `body.id` validation failure.
- Missing `body.snippet.type` validation failure.
- Invalid writable field failure.
- Invalid playlist/channel content-structure failure.
- Duplicate playlist or channel reference failure.
- Missing target section failure.
- Unsupported higher-level workflow rejection.
- Overwrite-sensitive update caveat.

## Verification Requirements

Before implementation is considered complete:

- Focused contract tests must prove discovery metadata includes endpoint identity, quota cost, OAuth requirement, supported parts, target section ID requirement, body requirement, `snippet.type` requirement, writable-field expectations, overwrite behavior, content-structure requirements, partner-context caveats, and out-of-scope boundaries.
- Unit tests must prove part, body, target ID, OAuth, content-rule, duplicate-reference, partner-context, unsupported-field, and overwrite-guidance validation rejects unsupported inputs safely.
- Integration tests must prove default registration exposes executable `channelSections_update`.
- Handler tests must prove successful result mapping preserves returned updated resource fields, requested parts, safe partner context, endpoint identity, and quota cost.
- Regression tests must preserve existing baseline, retrieval, activities, captions, channel banner, channels, `channelSections_list`, and `channelSections_insert` tools.
- Final validation must include `python3 -m pytest` and `python3 -m ruff check .`.
- Every new or changed Python function must include a reStructuredText docstring.
