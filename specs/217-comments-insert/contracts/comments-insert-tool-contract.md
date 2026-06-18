# Contract: YT-217 Layer 2 `comments_insert` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `comments_insert` tool. The tool exposes the upstream YouTube Data API `comments.insert` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, OAuth, response-boundary, mutation, validation, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `comments.insert` reply creation request
- Required OAuth access, response part selection, parent-comment reference, and reply text rules
- Near-raw successful created comment-resource result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define comment listing, top-level comment-thread creation, comment updating, moderation status changes, comment deletion, reply generation, sentiment analysis, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint composition.

## Tool Identity

The public tool must expose:

- `name`: `comments_insert`
- `upstream.resource`: `comments`
- `upstream.method`: `insert`
- `upstream.operationKey`: `comments.insert`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active write operation, with visible parent-comment, reply-content, and authorization caveats
- `resourceFamily`: `comments`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `comments.insert`, `Quota cost: 50`, OAuth-required access, required part selection, required parent-comment reference, and required reply text.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: comma-separated response part selection. The primary supported reply creation path uses `snippet`; `id` may be accepted where the shared contract supports requesting the created comment ID.
- `body`: comment resource body.
- `body.snippet.parentId`: identifier of the existing parent comment being answered.
- `body.snippet.textOriginal`: reply text to publish.

Optional request fields:

- `onBehalfOfContentOwner`: delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

Rules:

- `part` must be present and non-empty.
- `body.snippet.parentId` must be present and non-empty.
- `body.snippet.textOriginal` must be present and non-empty.
- OAuth authorization must be available for every supported request.
- Delegation context may be supplied only with eligible OAuth authorization.
- Unsupported fields must be rejected when the public schema disallows them.
- Request shapes for top-level comment-thread creation, comment update, moderation, deletion, search, automated reply generation, ranking, summarization, sentiment, or enrichment must be rejected or clearly flagged as out of scope.

## Successful Result Contract

Successful results must preserve the endpoint-backed created comment-resource shape:

- `endpoint`: `comments.insert`
- `quotaCost`: `50`
- `created`: `true`
- `requestedParts`: normalized requested response parts
- `item`: returned comment resource or equivalent created-resource payload
- `auth`: safe OAuth-required context summary
- `delegation`: safe delegation summary when delegation context is supplied

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not list comments, create top-level threads, update comments, moderate comments, delete comments, generate reply text, rank comments, summarize threads, enrich resources, aggregate across endpoints, or expose authorization secrets.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, or invalid part/body/parent/text inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot create the reply.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_not_found` when the selected parent comment is unavailable or missing.
- `endpoint_unavailable` when the upstream operation is temporarily unavailable.
- `deprecated_endpoint` when upstream deprecation signals apply.
- `upstream_failure` for unexpected upstream failures.

Specific upstream details such as `commentTextRequired`, `commentTextTooLong`, `invalidCustomEmoji`, `invalidCommentMetadata`, `operationNotSupported`, `parentCommentIsPrivate`, `parentIdMissing`, `processingFailure`, `forbidden`, `ineligibleAccount`, and `parentCommentNotFound` must be mapped to a safe shared category while preserving enough caller-facing guidance to correct the request.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw credential payloads, unsafe upstream diagnostics, or sensitive owner credential details.

## Usage Examples

### Authorized Reply Creation

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "parentId": "comment-parent-123",
      "textOriginal": "Thanks for the feedback."
    }
  }
}
```

Expected metadata: `comments.insert`, `Quota cost: 50`, eligible OAuth authorization required, creates a reply to an existing parent comment.

### Delegated Owner Context

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "parentId": "comment-parent-123",
      "textOriginal": "Thanks from the channel team."
    }
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `comments.insert`, `Quota cost: 50`, eligible OAuth authorization required, delegated content-owner context visible without exposing credentials.

### Missing OAuth Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "parentId": "comment-parent-123",
      "textOriginal": "Reply text"
    }
  }
}
```

Expected behavior when no eligible OAuth context is available: reject with safe `authentication_failed` guidance that `comments_insert` requires OAuth.

### Missing Part Failure

```json
{
  "body": {
    "snippet": {
      "parentId": "comment-parent-123",
      "textOriginal": "Reply text"
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `part` is required.

### Missing Parent Comment Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "textOriginal": "Reply text"
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `body.snippet.parentId` is required.

### Missing Reply Text Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "parentId": "comment-parent-123"
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `body.snippet.textOriginal` is required.

### Unsupported Top-Level Create Shape

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "videoId": "dQw4w9WgXcQ",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "This belongs to commentThreads.insert."
        }
      }
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that top-level comment-thread creation belongs to `commentThreads_insert`, not `comments_insert`.

### Parent Comment Not Found

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "parentId": "missing-parent-comment",
      "textOriginal": "Reply text"
    }
  }
}
```

Expected behavior: preserve a safe `resource_not_found` or closest shared parent-comment failure category.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `comments_insert` is listed as a callable tool.
- The input schema includes required `part`, required `body`, required `body.snippet.parentId`, required `body.snippet.textOriginal`, and optional delegation context when supported.
- The description and metadata expose quota cost `50`.
- The description and metadata expose OAuth-required auth.
- Usage notes include quota, OAuth, parent-comment, reply-content, examples, unsupported top-level creation, and safe failure guidance.
- The handler is executable and not merely a representative descriptor.

## Validation Expectations

Focused validation should include:

```bash
pytest tests/unit/test_youtube_comments.py tests/contract/test_youtube_comments_contract.py tests/integration/test_youtube_comments_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If Layer 1 wrapper behavior is touched, focused validation should also include:

```bash
pytest tests/contract/test_layer1_comments_contract.py tests/integration/test_layer1_foundation.py
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

Public metadata, examples, descriptions, usage notes, errors, logs, and tests must not expose:

- API keys
- OAuth tokens
- Secret values
- Signed URLs
- Raw credential payloads
- Stack traces
- Unsafe upstream diagnostics
- Sensitive channel-owner credential details

The tool may expose safe booleans or labels such as `oauthRequired`, `delegatedContextProvided`, `authentication_failed`, or `authorization_failed`.
