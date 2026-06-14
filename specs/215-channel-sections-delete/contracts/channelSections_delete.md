# Contract: `channelSections_delete`

## Public Identity

- **Tool name**: `channelSections_delete`
- **Upstream resource**: `channelSections`
- **Upstream method**: `delete`
- **Operation key**: `channelSections.delete`
- **HTTP method/path**: `DELETE /youtube/v3/channelSections`
- **Quota cost**: `50`
- **Auth mode**: `oauth_required`
- **Availability**: `active`
- **Layer 1 dependency**: `build_channel_sections_delete_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool deletes one YouTube channel section.
- The endpoint is `channelSections.delete`.
- The official quota cost is `50`.
- Eligible OAuth authorization is required.
- `id` is required.
- `onBehalfOfContentOwner` is partner-only delegated context.
- The operation is destructive and does not provide undo, recovery, playlist cleanup, layout repair, section lookup, sorting, creation, update, or bulk deletion.

## Input Schema

```json
{
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "The channel-section ID to delete."
    },
    "onBehalfOfContentOwner": {
      "type": "string",
      "minLength": 1,
      "description": "Partner-only content-owner context for properly authorized requests."
    }
  },
  "additionalProperties": false
}
```

## Successful Result Shape

No-body success:

```json
{
  "endpoint": "channelSections.delete",
  "quotaCost": 50,
  "deleted": true,
  "delete": {
    "id": "section-123"
  },
  "bodyPolicy": "no_upstream_body"
}
```

Success with upstream body preserved:

```json
{
  "endpoint": "channelSections.delete",
  "quotaCost": 50,
  "deleted": true,
  "delete": {
    "id": "section-123"
  },
  "upstream": {
    "kind": "youtube#channelSection",
    "etag": "etag-123",
    "id": "section-123"
  }
}
```

Partner-context success:

```json
{
  "endpoint": "channelSections.delete",
  "quotaCost": 50,
  "deleted": true,
  "delete": {
    "id": "section-123"
  },
  "partnerContext": {
    "onBehalfOfContentOwner": true
  },
  "bodyPolicy": "no_upstream_body"
}
```

## Response Convention

- `resultKind`: `deletion_acknowledgment`
- `successStatus`: `204_or_upstream_body`
- `bodyPolicy`: `preserve_returned_body_or_acknowledge_no_body`
- `targetField`: `id`
- `mutation`: `destructive_delete`

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `deleted`, `delete`, `partnerContext`, `bodyPolicy`, `upstream`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `contentDetails`
- **Disallowed behavior**: `channel_section_lookup`, `channel_section_creation`, `channel_section_update`, `bulk_delete`, `layout_repair`, `playlist_deletion`, `playlist_item_cleanup`, `undo`, `recovery`, `enrichment`, `cross_endpoint_aggregation`

## Validation Failures

Missing OAuth:

```json
{
  "category": "authentication_failed",
  "details": {
    "field": "auth"
  }
}
```

Missing or invalid ID:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "id"
  }
}
```

Unsupported field:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body"
  }
}
```

Empty partner context:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "onBehalfOfContentOwner",
    "partnerScoped": true
  }
}
```

## Upstream Error Mapping

| Upstream Signal | Public Category | Notes |
|-----------------|-----------------|-------|
| `idRequired`, missing `id` | `invalid_request` | Reject locally when possible |
| `idInvalid` | `invalid_request` | Preserve safe status/reason only |
| `notEditable` | `authorization_failed` or `invalid_request` | Prefer authorization when tied to caller rights |
| `channelSectionForbidden` | `authorization_failed` | Do not leak credential details |
| `channelNotFound` | `resource_not_found` | Safe missing-resource category |
| `channelSectionNotFound` | `resource_not_found` | Covers repeated delete or missing target |
| quota/rate limit | `quota_exhausted` | Preserve safe upstream status |
| transient/unavailable | `endpoint_unavailable` | Retry behavior remains Layer 1 concern |
| deprecated endpoint | `deprecated_endpoint` | Surface shared category when Layer 1 reports it |
| unknown upstream failure | `upstream_failure` | Safe fallback |

## Required Caller Examples

- `authorized_delete`: Valid OAuth delete with `id`.
- `partner_context_delete`: Valid OAuth delete with `id` and `onBehalfOfContentOwner`.
- `missing_id`: Rejects absent `id`.
- `invalid_id`: Rejects empty or malformed `id`.
- `unsupported_option`: Rejects request body, bulk, recovery, playlist cleanup, or layout repair option.
- `missing_target_section`: Maps repeated deletion or missing upstream section to `resource_not_found`.
- `missing_oauth`: Rejects calls without eligible OAuth.

Every example must include `quotaCost: 50` or text stating `Quota cost: 50`.
