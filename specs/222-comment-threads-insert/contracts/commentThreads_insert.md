# Contract: `commentThreads_insert`

## Public Identity

- **Tool name**: `commentThreads_insert`
- **Upstream resource**: `commentThreads`
- **Upstream method**: `insert`
- **Operation key**: `commentThreads.insert`
- **HTTP method/path**: `POST /youtube/v3/commentThreads`
- **Quota cost**: `50`
- **Auth mode**: `oauth_required`
- **Availability**: `active`
- **Layer 1 dependency**: `build_comment_threads_insert_wrapper()`

## Description Requirements

The public description and usage notes must state:

- The tool creates top-level YouTube comments through the upstream `commentThreads.insert` endpoint.
- The official quota cost is `50`.
- Eligible OAuth authorization is required; API-key-only access is unsupported.
- `part` is required.
- The request body must provide a comment-thread resource with `body.snippet.channelId`, `body.snippet.videoId`, and `body.snippet.topLevelComment.snippet.textOriginal`.
- `onBehalfOfContentOwner` may be supplied only as supported delegated owner context with eligible OAuth authorization.
- Reply creation belongs to `comments_insert`.
- The tool does not perform thread listing, reply creation, comment update, comment deletion, moderation actions, sentiment analysis, ranking, summarization, enrichment, analytics, generated responses, or cross-endpoint aggregation.
- Missing channels, missing videos, disabled comments, insufficient permissions, ineligible accounts, invalid metadata, and text validation failures are distinct from successful creation.

## Input Schema

```json
{
  "type": "object",
  "required": ["part", "body"],
  "properties": {
    "part": {
      "type": "string",
      "minLength": 1,
      "enum": ["id", "snippet", "replies"],
      "description": "Comma-separated commentThread resource parts to return, usually snippet for creation."
    },
    "body": {
      "type": "object",
      "required": ["snippet"],
      "properties": {
        "snippet": {
          "type": "object",
          "required": ["channelId", "videoId", "topLevelComment"],
          "properties": {
            "channelId": {
              "type": "string",
              "minLength": 1,
              "description": "Channel ID associated with the comment thread resource."
            },
            "videoId": {
              "type": "string",
              "minLength": 1,
              "description": "Video ID that receives the top-level comment."
            },
            "topLevelComment": {
              "type": "object",
              "required": ["snippet"],
              "properties": {
                "snippet": {
                  "type": "object",
                  "required": ["textOriginal"],
                  "properties": {
                    "textOriginal": {
                      "type": "string",
                      "minLength": 1,
                      "description": "Top-level comment text to publish."
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
    },
    "onBehalfOfContentOwner": {
      "type": "string",
      "minLength": 1,
      "description": "Optional delegated owner context when supported and authorized."
    }
  },
  "additionalProperties": false
}
```

## Validation Rules

| Request Shape | Outcome |
|---------------|---------|
| `part` + valid body + eligible OAuth | Valid top-level comment-thread creation |
| `part` + valid body + `onBehalfOfContentOwner` + eligible OAuth | Valid delegated top-level comment-thread creation |
| Missing `part` | `invalid_request` |
| Missing `body` | `invalid_request` |
| Missing `body.snippet.channelId` | `invalid_request` |
| Missing `body.snippet.videoId` | `invalid_request` |
| Missing `body.snippet.topLevelComment.snippet.textOriginal` | `invalid_request` |
| Empty top-level comment text | `invalid_request` |
| Reply-style `body.snippet.parentId` | `invalid_request` |
| Listing filters such as `videoId` or `allThreadsRelatedToChannelId` outside the body | `invalid_request` |
| Update, moderation, delete, search, ranking, summarization, or generated-response fields | `invalid_request` |
| Missing OAuth context | `authentication_failed` |
| Insufficient OAuth permissions or ineligible account | `authorization_failed` |
| Missing channel or video | `resource_not_found` |
| Disabled comments, invalid metadata, text too long, invalid emoji, or invalid request body | `invalid_request` |
| Quota exhausted | `quota_exhausted` |
| Endpoint unavailable | `endpoint_unavailable` |

## Successful Result Shape

```json
{
  "endpoint": "commentThreads.insert",
  "quotaCost": 50,
  "created": true,
  "requestedParts": ["snippet"],
  "auth": {
    "mode": "oauth_required"
  },
  "target": {
    "channelId": "channel-123",
    "videoId": "video-123"
  },
  "item": {
    "kind": "youtube#commentThread",
    "id": "thread-123",
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Great walkthrough."
        }
      }
    }
  }
}
```

Delegated owner context may add a safe delegation summary:

```json
{
  "endpoint": "commentThreads.insert",
  "quotaCost": 50,
  "created": true,
  "requestedParts": ["snippet"],
  "delegation": {
    "onBehalfOfContentOwner": true
  },
  "item": {
    "id": "thread-123"
  }
}
```

## Response Convention

- `resultKind`: `created_resource`
- `resourcePath`: `item`
- `authMode`: `oauth_required`
- `targetFields`: `body.snippet.channelId`, `body.snippet.videoId`
- `delegationFields`: `onBehalfOfContentOwner`
- `emptyResultPolicy`: not applicable; successful creation returns a created resource or equivalent upstream payload

## Response Boundary

- **Allowed wrapper fields**: `endpoint`, `quotaCost`, `created`, `requestedParts`, `auth`, `target`, `delegation`, `item`, `kind`, `etag`, `id`, `snippet`, `replies`
- **Preserved upstream fields**: `kind`, `etag`, `id`, `snippet`, `replies`
- **Disallowed behavior**: `thread_listing`, `reply_creation`, `comment_update`, `comment_delete`, `comment_moderation`, `sentiment_analysis`, `ranking`, `summarization`, `enrichment`, `analytics`, `generated_response`, `cross_endpoint_aggregation`

## Validation Failures

Missing OAuth:

```json
{
  "category": "authentication_failed",
  "details": {
    "authMode": "oauth_required"
  }
}
```

Missing part:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "part"
  }
}
```

Missing target video:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.snippet.videoId"
  }
}
```

Missing target channel:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.snippet.channelId"
  }
}
```

Missing top-level comment text:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.snippet.topLevelComment.snippet.textOriginal"
  }
}
```

Unsupported reply shape:

```json
{
  "category": "invalid_request",
  "details": {
    "field": "body.snippet.parentId",
    "toolBoundary": "reply creation belongs to comments_insert"
  }
}
```

## Usage Examples

### Authorized Top-Level Comment Creation

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Great walkthrough."
        }
      }
    }
  }
}
```

Expected metadata: `commentThreads.insert`, `Quota cost: 50`, eligible OAuth authorization required, creates a top-level comment thread.

### Delegated Owner Context

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Posting from the channel team."
        }
      }
    }
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `commentThreads.insert`, `Quota cost: 50`, eligible OAuth authorization required, delegated content-owner context visible without exposing credentials.

### Missing OAuth Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Top-level comment text"
        }
      }
    }
  }
}
```

Expected behavior when no eligible OAuth context is available: reject with safe `authentication_failed` guidance that `commentThreads_insert` requires OAuth.

### Missing Part Failure

```json
{
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Top-level comment text"
        }
      }
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `part` is required.

### Missing Target Channel Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Top-level comment text"
        }
      }
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `body.snippet.channelId` is required.

### Missing Target Video Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Top-level comment text"
        }
      }
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `body.snippet.videoId` is required.

### Missing Top-Level Comment Text Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {}
      }
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `body.snippet.topLevelComment.snippet.textOriginal` is required.

### Unsupported Reply Create Shape

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "parentId": "comment-parent-123",
      "textOriginal": "This belongs to comments.insert."
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that reply creation belongs to `comments_insert`, not `commentThreads_insert`.

### Missing Video Upstream Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "missing-video",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Top-level comment text"
        }
      }
    }
  }
}
```

Expected behavior: preserve a safe `resource_not_found` or closest shared video failure category.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `commentThreads_insert` is listed as a callable tool.
- The input schema includes required `part`, required `body`, required `body.snippet.channelId`, required `body.snippet.videoId`, required `body.snippet.topLevelComment.snippet.textOriginal`, and optional delegation context when supported.
- The description and metadata expose quota cost `50`.
- The description and metadata expose OAuth-required auth.
- Usage notes include quota, OAuth, channel/video target context, top-level comment content, examples, unsupported reply creation, and safe failure guidance.
- The handler is executable and not merely a representative descriptor.

## Validation Expectations

Focused validation should include:

```bash
pytest tests/unit/test_youtube_comment_threads.py tests/contract/test_youtube_comment_threads_contract.py tests/integration/test_youtube_comment_threads_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If Layer 1 wrapper behavior is touched, focused validation should also include:

```bash
pytest tests/contract/test_layer1_comment_threads_contract.py tests/integration/test_layer1_foundation.py
```

If default tool discovery or MCP routing changes, focused validation should also include:

```bash
pytest tests/integration/test_mcp_request_flow.py
```

Final validation after implementation code changes must include:

```bash
pytest
ruff check .
```

## Security and Safety Rules

- Do not expose API keys, OAuth tokens, signed URLs, secret values, raw credential payloads, stack traces, unsafe upstream diagnostics, or sensitive owner credential details.
- Do not include full authorization context in success results.
- Preserve only safe target and delegation summaries in public results.
- Keep generated examples clearly representative; do not include real channel IDs, video IDs, credentials, private comments, or publishable secrets.
