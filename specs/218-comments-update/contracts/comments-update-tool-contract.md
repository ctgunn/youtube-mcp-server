# Contract: YT-218 Layer 2 `comments_update` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `comments_update` tool. The tool exposes the upstream YouTube Data API `comments.update` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, OAuth, response-boundary, mutation, validation, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `comments.update` comment edit request
- Required OAuth access, response part selection, target comment identifier, writable text, and read-only field rules
- Near-raw successful updated comment-resource result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define comment listing, reply creation, top-level comment-thread creation, moderation status changes, comment deletion, automated rewriting, sentiment analysis, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint composition.

## Tool Identity

The public tool must expose:

- `name`: `comments_update`
- `upstream.resource`: `comments`
- `upstream.method`: `update`
- `upstream.operationKey`: `comments.update`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active write operation, with visible target-comment, writable-field, read-only-field, and authorization caveats
- `resourceFamily`: `comments`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `comments.update`, `Quota cost: 50`, OAuth-required access, required part selection, required target comment identifier, and required revised comment text.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: comma-separated response part selection. `snippet` is required because it contains all updateable properties; `id` may be accepted where the shared contract supports requesting the returned comment ID.
- `body`: comment resource body.
- `body.id`: identifier of the existing comment being edited.
- `body.snippet.textOriginal`: revised comment text to apply.

Optional request fields:

- `onBehalfOfContentOwner`: delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

Rules:

- `part` must be present, non-empty, and include `snippet`.
- `body.id` must be present and non-empty.
- `body.snippet.textOriginal` must be present and non-empty.
- OAuth authorization must be available for every supported request.
- Delegation context may be supplied only with eligible OAuth authorization.
- Unsupported fields must be rejected when the public schema disallows them.
- Request shapes for comment listing, reply creation, top-level comment-thread creation, moderation status changes, deletion, search, automated rewriting, ranking, summarization, sentiment, or enrichment must be rejected or clearly flagged as out of scope.
- Read-only or unrelated comment fields must be rejected instead of silently ignored.

## Successful Result Contract

Successful results must preserve the endpoint-backed updated comment-resource shape:

- `endpoint`: `comments.update`
- `quotaCost`: `50`
- `updated`: `true`
- `requestedParts`: normalized requested response parts
- `writableFields`: safe summary of fields updated, including `body.snippet.textOriginal`
- `item`: returned comment resource or equivalent updated-resource payload
- `auth`: safe OAuth-required context summary
- `delegation`: safe delegation summary when delegation context is supplied

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not list comments, create replies, create top-level threads, moderate comments, delete comments, generate rewritten text, rank comments, summarize threads, enrich resources, aggregate across endpoints, or expose authorization secrets.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, or invalid part/body/id/text inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot update the target comment.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_not_found` when the selected target comment is unavailable or missing.
- `endpoint_unavailable` when the upstream operation is temporarily unavailable.
- `deprecated_endpoint` when upstream deprecation signals apply.
- `upstream_failure` for unexpected upstream failures.

Specific upstream details such as `commentTextTooLong`, `invalidCommentMetadata`, `operationNotSupported`, `processingFailure`, `forbidden`, `ineligibleAccount`, and `commentNotFound` must be mapped to a safe shared category while preserving enough caller-facing guidance to correct the request.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw credential payloads, unsafe upstream diagnostics, or sensitive owner credential details.

## Usage Examples

### Authorized Comment Update

```json
{
  "part": "snippet",
  "body": {
    "id": "comment-123",
    "snippet": {
      "textOriginal": "Updated comment text."
    }
  }
}
```

Expected metadata: `comments.update`, `Quota cost: 50`, eligible OAuth authorization required, updates the writable text field on an existing comment.

### Delegated Owner Context

```json
{
  "part": "snippet",
  "body": {
    "id": "comment-123",
    "snippet": {
      "textOriginal": "Updated by the channel team."
    }
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `comments.update`, `Quota cost: 50`, eligible OAuth authorization required, delegated content-owner context visible without exposing credentials.

### Missing OAuth Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "comment-123",
    "snippet": {
      "textOriginal": "Updated comment text."
    }
  }
}
```

Expected behavior when no eligible OAuth context is available: reject with safe `authentication_failed` guidance that `comments_update` requires OAuth.

### Missing Part Failure

```json
{
  "body": {
    "id": "comment-123",
    "snippet": {
      "textOriginal": "Updated comment text."
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `part` is required.

### Unsupported Writable Part Failure

```json
{
  "part": "statistics",
  "body": {
    "id": "comment-123",
    "snippet": {
      "textOriginal": "Updated comment text."
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `snippet` is the supported writable part for this tool.

### Missing Target Comment Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "textOriginal": "Updated comment text."
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `body.id` is required.

### Missing Updated Text Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "comment-123",
    "snippet": {}
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `body.snippet.textOriginal` is required.

### Read-Only Field Failure

```json
{
  "part": "snippet",
  "body": {
    "id": "comment-123",
    "snippet": {
      "textOriginal": "Updated comment text.",
      "parentId": "another-parent"
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that parent relationships and read-only fields cannot be updated through `comments_update`.

### Target Comment Not Found

```json
{
  "part": "snippet",
  "body": {
    "id": "missing-comment",
    "snippet": {
      "textOriginal": "Updated comment text."
    }
  }
}
```

Expected behavior: preserve a safe `resource_not_found` or closest shared target-comment failure category.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `comments_update` is listed as a callable tool.
- The input schema includes required `part`, required `body`, required `body.id`, required `body.snippet.textOriginal`, and optional delegation context when supported.
- The description and metadata expose quota cost `50`.
- The description and metadata expose OAuth-required auth.
- Usage notes include quota, OAuth, target-comment, writable-text, read-only-field, examples, unsupported update shapes, and safe failure guidance.
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

- Do not expose API keys, OAuth tokens, raw credential payloads, stack traces, signed URLs, or unsafe upstream diagnostics.
- Public result metadata may identify OAuth-required mode and safe delegation presence, but not credential values.
- Local validation should reject unsupported request shapes before endpoint execution where possible.
- The tool must not add generated comment text, rewrite suggestions, moderation decisions, ranking, sentiment, summary, or enrichment behavior.
