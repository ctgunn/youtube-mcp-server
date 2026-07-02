# Contract: `membershipsLevels_list`

## Public Tool Identity

- **Tool name**: `membershipsLevels_list`
- **Layer**: Layer 2 public MCP endpoint-backed tool
- **Upstream operation**: `membershipsLevels.list`
- **Resource family**: `memberships_levels`
- **Auth mode**: `oauth_required`
- **Official quota cost**: `1`
- **Availability**: Active, owner-only, channel-membership constrained

## Purpose

Expose YouTube channel membership-level listing for eligible channel owners while preserving low-level endpoint behavior. The tool is for direct retrieval, debugging, and downstream composition, not for channel member listing, subscriber lookup, membership administration, analytics, recommendation, ranking, summarization, enrichment, or delegated owner management.

## Input Contract

The public input schema must be object-shaped and must reject additional properties.

```json
{
  "type": "object",
  "required": ["part"],
  "properties": {
    "part": {
      "type": "string",
      "enum": ["snippet"]
    }
  },
  "additionalProperties": false
}
```

### Input Rules

- `part` is required and must be `snippet`.
- Filters, paging controls, page tokens, maximum result counts, delegated owner-context inputs, member-list selectors, subscriber lookup fields, request bodies, mutation fields, analytics fields, ranking fields, summarization fields, and enrichment fields are unsupported in this slice and must fail clearly.
- API-key-only access, missing OAuth access, non-owner OAuth access, and channel-membership ineligibility must not be treated as successful requests.

## Metadata Contract

Discovery metadata must expose:

- Public tool name `membershipsLevels_list`
- Upstream resource `membershipsLevels`
- Upstream method `list`
- Operation key `membershipsLevels.list`
- Quota cost `1`
- Auth mode `oauth_required`
- Active availability with owner-only and channel-membership eligibility caveats
- Supported request fields and rejected unsupported fields
- Response convention and safe error categories

Descriptions, usage notes, caveats, and examples must visibly state quota cost `1`.

## Result Contract

A successful result must preserve a near-raw list shape:

```json
{
  "endpoint": "membershipsLevels.list",
  "quotaCost": 1,
  "requestedParts": ["snippet"],
  "auth": {
    "mode": "oauth_required",
    "ownerScoped": true
  },
  "items": [],
  "kind": "youtube#membershipsLevelListResponse",
  "etag": "etag-value"
}
```

### Result Rules

- `items` may be empty for a valid successful request.
- Returned `kind`, `etag`, and item fields must be preserved when present.
- Missing optional upstream fields must not be fabricated.
- The requested parts must be preserved in the wrapper context.
- The result must not add channel member summaries, subscriber data, analytics, ranking, summarization, recommendation, enrichment, or heuristic classification.

## Error Contract

The tool must return or raise safe caller-facing errors using shared Layer 2 categories:

- `invalid_request`
- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `resource_not_found`
- `endpoint_unavailable`
- `upstream_failure`

### Error Rules

- Missing `part`, invalid `part`, empty `part`, unsupported fields, unsupported filters, unsupported paging controls, and unsupported actions must map to `invalid_request`.
- Missing OAuth credentials should map to `authentication_failed`.
- Non-owner access, channel-membership ineligibility, or inaccessible membership-level data should map to `authorization_failed` unless the upstream category provides a more specific safe shared category.
- Quota failures must map to `quota_exhausted`.
- Unavailable endpoint or service failures must map to `endpoint_unavailable` or `upstream_failure`.
- Errors must not expose OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.

## Required Examples

The contract must include caller-facing examples for:

- Owner-authorized membership-level retrieval with `part=snippet`
- Empty successful result
- Missing `part` validation failure
- Invalid `part` validation failure
- Unsupported field or unsupported modifier validation failure
- OAuth or membership eligibility failure
- Out-of-scope member-list or analytics request rejection
