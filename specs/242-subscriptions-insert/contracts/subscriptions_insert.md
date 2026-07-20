# Contract: `subscriptions_insert`

## Public Identity

- **Tool name**: `subscriptions_insert`
- **Layer**: Layer 2 public MCP endpoint tool
- **Mapped operation**: YouTube resource `subscriptions`, method `insert`
- **Operation key**: `subscriptions.insert`
- **Quota cost**: `50` official quota units per invocation
- **Availability**: Active unless implementation discovers an official documentation caveat that must be recorded
- **Auth mode**: OAuth-required user authorization
- **Scope**: Low-level subscription creation only

## Discovery Metadata Requirements

Discovery metadata, descriptions, usage notes, caveats, and examples must make the following visible before invocation:

- Public tool name `subscriptions_insert`
- Upstream operation `subscriptions.insert`
- Quota cost `50`
- OAuth-backed user authorization requirement
- Required `part=snippet`
- Required writable subscription body, including `body.snippet.resourceId.channelId`
- Optional `body.snippet.resourceId.kind` is accepted only as `youtube#channel`
- Successful calls create subscription relationships for the authorized account
- Returned result represents the created subscription resource
- Duplicate or ineligible target caveats
- Safe failure categories
- Out-of-scope workflows, including subscription listing, subscription deletion, channel search, recommendation, notification management, subscriber analytics, ranking, summarization, enrichment, idempotency, duplicate prevention, and cross-endpoint behavior

## Input Contract

```json
{
  "type": "object",
  "required": ["part", "body"],
  "properties": {
    "part": {
      "type": "string",
      "enum": ["snippet"]
    },
    "body": {
      "type": "object",
      "required": ["snippet"],
      "properties": {
        "snippet": {
          "type": "object",
          "required": ["resourceId"],
          "properties": {
            "resourceId": {
              "type": "object",
              "required": ["channelId"],
              "properties": {
                "kind": {
                  "type": "string",
                  "enum": ["youtube#channel"]
                },
                "channelId": {
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
  },
  "additionalProperties": false
}
```

## Input Validation Rules

- `part` is required and must be `snippet`.
- `body` is required and must be an object.
- `body.snippet` is required and must be an object.
- `body.snippet.resourceId` is required and must be an object.
- `body.snippet.resourceId.channelId` is required and must be non-empty.
- `body.snippet.resourceId.kind` may be omitted or set to `youtube#channel`.
- Unsupported fields such as `body.title`, `body.status`, extra `body.snippet` mappings, extra `body.snippet.resourceId` mappings, subscription listing inputs, subscription deletion inputs, channel search inputs, notification inputs, analytics inputs, and higher-level workflow instructions are rejected before endpoint execution.
- Eligible OAuth-backed user authorization is required for execution.

## Success Result Contract

Successful calls return a near-raw created subscription resource with safe context:

```json
{
  "endpoint": "subscriptions.insert",
  "quotaCost": 50,
  "requestedParts": ["snippet"],
  "created": true,
  "auth": {
    "mode": "oauth_required"
  },
  "creation": {
    "targetChannelId": "UC123",
    "targetResourceKind": "youtube#channel",
    "writableFields": ["body.snippet.resourceId.channelId"]
  },
  "subscription": {
    "id": "subscription-123",
    "snippet": {
      "resourceId": {
        "kind": "youtube#channel",
        "channelId": "UC123"
      }
    }
  }
}
```

Result rules:
- `endpoint` must be `subscriptions.insert`.
- `quotaCost` must be `50`.
- `requestedParts` must reflect caller-selected supported parts.
- `created` must identify the result as a successful creation outcome.
- `auth` must identify the safe access mode, not credentials.
- `creation` must identify safe target-channel and writable-field context without exposing credentials or unsafe request diagnostics.
- `subscription` must contain the returned created subscription resource.
- Returned subscription fields must preserve upstream data for selected parts without fabricated channel details, notification settings, subscriber profiles, analytics, ranking, recommendation, or enrichment fields.

## Error Contract

Failures must use safe caller-facing categories and sanitized details:

- `invalid_request`: Missing part, invalid part, missing body, malformed body, missing snippet, missing resourceId, missing channelId, invalid resource kind, unsupported write field, unsupported field, unsupported modifier, or out-of-scope workflow request
- `authentication_failed`: Required OAuth credential material missing or invalid
- `authorization_failed`: Caller lacks access to create subscriptions for the authorized account or target channel
- `quota_exhausted`: Upstream quota failure
- `duplicate_target`: Upstream indicates the authorized account is already subscribed to the target channel
- `ineligible_target`: Upstream indicates the target cannot be subscribed to, such as self-subscription, blocked channel, policy restriction, or account-state limitation
- `not_found`: Target channel cannot be found or is unavailable
- `endpoint_unavailable`: Upstream service unavailable or timeout category
- `deprecated_endpoint`: Official endpoint behavior is deprecated or unavailable
- `upstream_failure`: Unexpected upstream failure after sanitization

Error details must not include API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, raw request context, or secret-bearing diagnostics.

## Representative Examples

### Successful Subscription Creation

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      }
    }
  }
}
```

Expected context:
- Endpoint `subscriptions.insert`
- Quota cost `50`
- OAuth-backed access mode
- Created subscription result
- Target channel context visible in safe result fields
- Mutation warning visible before invocation

### Successful Subscription Creation With Explicit Kind

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "kind": "youtube#channel",
        "channelId": "UC123"
      }
    }
  }
}
```

Expected context:
- Endpoint `subscriptions.insert`
- Quota cost `50`
- Target resource kind preserved as `youtube#channel`

### Missing Part Failure

```json
{
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      }
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
  "part": "contentDetails",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      }
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `part`

### Missing Target Channel Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {}
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `body.snippet.resourceId.channelId`

### Invalid Resource Kind Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "kind": "youtube#playlist",
        "channelId": "UC123"
      }
    }
  }
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `body.snippet.resourceId.kind`

### Unsupported Write Field Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      },
      "title": "Unsupported by this slice"
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
      "resourceId": {
        "channelId": "UC123"
      }
    }
  }
}
```

Expected error when no eligible OAuth access is available:
- Category `authentication_failed`
- Safe detail identifying OAuth-required access

### Duplicate or Ineligible Target Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC_ALREADY_SUBSCRIBED"
      }
    }
  }
}
```

Expected error when upstream rejects the target:
- Safe category such as `duplicate_target`, `ineligible_target`, `authorization_failed`, `not_found`, or `upstream_failure`
- Sanitized details only

### Out-of-Scope Subscription Management Request

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      }
    }
  },
  "deleteExistingSubscription": true
}
```

Expected error:
- Category `invalid_request`
- Safe detail identifying `deleteExistingSubscription`

## Duplicate and Ineligible Target Caveat

The tool does not promise idempotent creation or preflight eligibility checks. If a caller retries after a timeout or unclear upstream outcome, the request may receive a duplicate relationship failure or another account-state-dependent response. Duplicate detection, idempotency keys, target lookup, self-subscription prevention beyond available validation, and cleanup workflows are out of scope for this low-level endpoint tool.
