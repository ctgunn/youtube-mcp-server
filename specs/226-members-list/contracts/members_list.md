# Contract: `members_list`

## Public Tool Identity

- **Tool name**: `members_list`
- **Layer**: Layer 2 public MCP endpoint-backed tool
- **Upstream operation**: `members.list`
- **Resource family**: `members`
- **Auth mode**: `oauth_required`
- **Official quota cost**: `2`
- **Availability**: Active, owner-only, channel-membership constrained

## Purpose

Expose YouTube channel membership member listing for eligible channel owners while preserving low-level endpoint behavior. The tool is for direct retrieval, debugging, and downstream composition, not for subscriber lookup, membership-level listing, member administration, analytics, recommendation, ranking, summarization, enrichment, or delegated owner management.

## Input Contract

The public input schema must be object-shaped and must reject additional properties.

```json
{
  "type": "object",
  "required": ["part", "mode"],
  "properties": {
    "part": {
      "type": "string",
      "enum": ["snippet"]
    },
    "mode": {
      "type": "string",
      "enum": ["all_current", "updates"]
    },
    "pageToken": {
      "type": "string",
      "minLength": 1
    },
    "maxResults": {
      "type": "integer",
      "minimum": 0,
      "maximum": 1000
    }
  },
  "additionalProperties": false
}
```

### Input Rules

- `part` is required and must be `snippet`.
- `mode` is required and must be `all_current` or `updates`.
- `pageToken` is optional, non-empty, and tied to the mode stream that produced it.
- `maxResults` is optional and must be within the documented member-list range.
- `hasAccessToLevel`, `filterByMemberChannelId`, delegated owner-context inputs, subscriber lookup fields, membership-level selectors, request bodies, mutation fields, analytics fields, ranking fields, summarization fields, and enrichment fields are unsupported in this slice and must fail clearly.
- API-key-only access, missing OAuth access, non-owner OAuth access, and channel-membership ineligibility must not be treated as successful requests.

## Metadata Contract

Discovery metadata must expose:

- Public tool name `members_list`
- Upstream resource `members`
- Upstream method `list`
- Operation key `members.list`
- Quota cost `2`
- Auth mode `oauth_required`
- Active availability with owner-only and channel-membership eligibility caveats
- Supported request fields and rejected unsupported fields
- Response convention and safe error categories

Descriptions, usage notes, caveats, and examples must visibly state quota cost `2`.

## Result Contract

A successful result must preserve a near-raw list shape:

```json
{
  "endpoint": "members.list",
  "quotaCost": 2,
  "requestedParts": ["snippet"],
  "mode": "all_current",
  "auth": {
    "mode": "oauth_required",
    "ownerScoped": true
  },
  "items": [],
  "kind": "youtube#memberListResponse",
  "etag": "etag-value",
  "nextPageToken": "NEXT_PAGE",
  "pageInfo": {
    "totalResults": 0,
    "resultsPerPage": 0
  }
}
```

### Result Rules

- `items` may be empty for a valid successful request.
- Returned `kind`, `etag`, `nextPageToken`, and `pageInfo` must be preserved when present.
- Missing optional upstream fields must not be fabricated.
- The selected mode and requested parts must be preserved in the wrapper context.
- The result must not add subscriber summaries, membership-level enrichment, analytics, ranking, summarization, recommendation, or heuristic classification.

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

- Missing `part`, invalid `part`, missing `mode`, invalid `mode`, invalid `maxResults`, empty `pageToken`, unsupported fields, and unsupported filters/actions must map to `invalid_request`.
- Missing OAuth credentials should map to `authentication_failed`.
- Non-owner access, channel-membership ineligibility, or inaccessible member data should map to `authorization_failed` unless the upstream category provides a more specific safe shared category.
- Quota failures must map to `quota_exhausted`.
- Unavailable endpoint or service failures must map to `endpoint_unavailable` or `upstream_failure`.
- Errors must not expose OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.

## Required Examples

The contract must include caller-facing examples for:

- Owner-authorized current-member retrieval with `mode=all_current`
- Owner-authorized update-stream retrieval with `mode=updates`
- Paged retrieval with `pageToken` and `maxResults`
- Empty successful result
- Missing `part` validation failure
- Missing `mode` validation failure
- Unsupported `mode` validation failure
- Invalid `maxResults` validation failure
- Unsupported field or unsupported filter validation failure
- OAuth or membership eligibility failure
- Out-of-scope subscriber lookup or analytics request rejection
