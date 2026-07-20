# Contract: `subscriptions_delete`

## Public Tool Identity

- **Tool name**: `subscriptions_delete`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped upstream operation**: `subscriptions.delete`
- **Resource family**: `subscriptions`
- **Official quota cost**: `50` units per invocation
- **Auth mode**: `oauth_required`
- **Availability**: Active unless official endpoint caveats recorded during implementation say otherwise
- **Response boundary**: Near-raw endpoint-backed deletion acknowledgment

## Purpose

Remove one YouTube subscription relationship for the authorized account using the low-level `subscriptions.delete` endpoint behavior. This tool is for direct endpoint access, debugging, power-user workflows, and later composition by higher layers.

## Out Of Scope

`subscriptions_delete` does not list subscriptions, create subscriptions, search channels, infer subscription identifiers from channel IDs, perform bulk deletion, preflight lookup existing relationships, manage notifications, provide subscriber analytics, rank results, summarize results, recommend channels, enrich channel data, or compose multiple endpoint calls.

## Input Schema

```json
{
  "type": "object",
  "required": ["id"],
  "properties": {
    "id": {
      "type": "string",
      "minLength": 1,
      "description": "Identifier for the subscription relationship to delete."
    }
  },
  "additionalProperties": false
}
```

## Input Rules

- `id` is required and must be non-empty text after trimming.
- Exactly one subscription relationship is targeted per call.
- OAuth-backed user authorization is required before execution.
- API-key-only access is invalid for deletion.
- Additional fields are rejected before endpoint execution.
- Channel IDs, request bodies, selectors, creation fields, notification options, analytics flags, ranking flags, summarization flags, and enrichment flags are invalid.

## Success Result Shape

```json
{
  "endpoint": "subscriptions.delete",
  "quotaCost": 50,
  "deleted": true,
  "deletion": {
    "id": "subscription-123"
  },
  "auth": {
    "mode": "oauth_required"
  },
  "upstream": {}
}
```

## Success Result Rules

- `endpoint` is always `subscriptions.delete`.
- `quotaCost` is always `50`.
- `deleted` is `true` only when deletion succeeds.
- `deletion.id` preserves the caller's validated target subscription identifier.
- `auth.mode` discloses the safe authorization mode and never includes credentials.
- `upstream` may include safe acknowledgment fields when returned; it must not include raw diagnostics or secrets.
- The result must not fabricate a deleted subscription resource, channel details, analytics, notification settings, recommendations, rankings, summaries, or enrichment.

## Failure Categories

| Category | Trigger | Required Detail |
|----------|---------|-----------------|
| `invalid_request` | Missing, empty, malformed, unsupported, or extra input fields | Include `field` when one field caused the failure |
| `authentication_failed` | OAuth access is missing, expired, invalid, or unavailable | Include `authMode: oauth_required` |
| `authorization_failed` | Caller has OAuth but cannot delete the target relationship | Include safe reason when available |
| `not_found` | Target subscription does not exist or is already removed | Include safe target context when available |
| `non_removable_target` | Target relationship exists but cannot be removed because of account, ownership, policy, or state | Include safe reason when available |
| `quota_exhausted` | Quota prevents deletion | Include safe quota context when available |
| `endpoint_unavailable` | Upstream deletion endpoint is unavailable | Include safe availability context when available |
| `deprecated_endpoint` | Upstream deletion endpoint is deprecated or disabled | Include safe caveat when available |
| `upstream_failure` | Unexpected upstream failure | Include only sanitized diagnostic details |

## Required Caller Examples

### Successful Deletion

```json
{
  "name": "oauth_subscription_deletion",
  "description": "Quota cost: 50. Delete one subscription relationship with OAuth authorization.",
  "arguments": {
    "id": "subscription-123"
  },
  "result": {
    "endpoint": "subscriptions.delete",
    "quotaCost": 50,
    "deleted": true,
    "deletion": {
      "id": "subscription-123"
    }
  },
  "quotaCost": 50
}
```

### Missing Identifier

```json
{
  "name": "missing_id",
  "description": "Quota cost: 50. Reject deletion requests missing the required subscription id.",
  "arguments": {},
  "error": {
    "category": "invalid_request",
    "field": "id"
  }
}
```

### Empty Identifier

```json
{
  "name": "empty_id",
  "description": "Quota cost: 50. Reject deletion requests with an empty subscription id.",
  "arguments": {
    "id": ""
  },
  "error": {
    "category": "invalid_request",
    "field": "id"
  }
}
```

### Missing OAuth

```json
{
  "name": "access_failure",
  "description": "Quota cost: 50. Map missing or invalid OAuth access to safe authentication errors.",
  "arguments": {
    "id": "subscription-123"
  },
  "error": {
    "category": "authentication_failed",
    "authMode": "oauth_required"
  }
}
```

### Already Removed Or Missing Target

```json
{
  "name": "already_removed_or_missing_target",
  "description": "Quota cost: 50. Map missing or already-removed subscriptions to safe target-state errors.",
  "arguments": {
    "id": "subscription-missing"
  },
  "error": {
    "category": "not_found"
  }
}
```

### Non-Removable Target

```json
{
  "name": "non_removable_target",
  "description": "Quota cost: 50. Map ownership, policy, or account-state deletion failures safely.",
  "arguments": {
    "id": "subscription-blocked"
  },
  "error": {
    "category": "non_removable_target"
  }
}
```

### Quota Or Upstream Failure

```json
{
  "name": "quota_or_upstream_delete_failure",
  "description": "Quota cost: 50. Map quota and upstream delete failures to safe categories.",
  "arguments": {
    "id": "subscription-123"
  },
  "error": {
    "category": "quota_exhausted"
  }
}
```

### Out-Of-Scope Workflow Request

```json
{
  "name": "out_of_scope_subscription_management_request",
  "description": "Quota cost: 50. Listing, creation, notification management, analytics, and enrichment are out of scope.",
  "arguments": {
    "id": "subscription-123",
    "includeChannelStatistics": true
  },
  "error": {
    "category": "invalid_request",
    "field": "includeChannelStatistics"
  }
}
```

## Discovery Metadata Requirements

- Metadata includes `name: subscriptions_delete`.
- Metadata includes upstream `resource: subscriptions`, `method: delete`, and `operationKey: subscriptions.delete`.
- Metadata includes `quotaCost: 50`.
- Metadata includes `authMode: oauth_required`.
- Metadata includes the input schema above.
- Metadata response convention identifies an acknowledgment-style mutation result.
- Description, usage notes, caveats, and examples all mention quota cost `50`.
- Description, usage notes, caveats, and examples all make OAuth-required access visible.

## Security Requirements

- Results and errors must not expose API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, or unsafe request context.
- Error details must be sanitized before returning to MCP callers.
- Examples must not contain real credentials or real account identifiers.
