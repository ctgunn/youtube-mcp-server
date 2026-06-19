# Contract: YT-220 Layer 2 `comments_delete` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `comments_delete` tool. The tool exposes the upstream YouTube Data API `comments.delete` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, OAuth, response-boundary, destructive mutation acknowledgment, validation, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `comments.delete` deletion request
- Required OAuth access, target comment identifier, no-body rule, destructive deletion caveat, and delegated owner context
- Near-raw successful deletion acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define comment listing, reply creation, comment editing, moderation status changes, deletion recovery, automated moderation recommendations, sentiment analysis, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint composition.

## Tool Identity

The public tool must expose:

- `name`: `comments_delete`
- `upstream.resource`: `comments`
- `upstream.method`: `delete`
- `upstream.operationKey`: `comments.delete`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active destructive write operation, with visible target-comment, no-body, acknowledgment, and authorization caveats
- `resourceFamily`: `comments`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `comments.delete`, `Quota cost: 50`, OAuth-required access, required target comment identifier, destructive deletion behavior, no returned deleted-comment resource, and the no-body request boundary.

## Input Contract

The input schema must accept one object request.

Required fields:

- `id`: one comment identifier for the comment resource being deleted.

Optional request fields:

- `onBehalfOfContentOwner`: delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

Rules:

- `id` must be present and include exactly one non-empty target comment identifier.
- Empty, duplicate, conflicting, list-style, comma-separated multi-target, or malformed target shapes must be rejected unless a later shared Layer 2 convention explicitly adds a supported multi-target pattern for this endpoint.
- OAuth authorization must be available for every supported request.
- Delegation context may be supplied only with eligible OAuth authorization.
- Request bodies must be rejected because the upstream operation supports query parameters only.
- Unsupported fields must be rejected when the public schema disallows them.
- Request shapes for comment listing, reply creation, comment editing, moderation status change, deletion recovery, search, automated moderation advice, ranking, summarization, sentiment, or enrichment must be rejected or clearly flagged as out of scope.

## Successful Result Contract

Successful results must preserve the endpoint-backed deletion acknowledgment shape:

- `endpoint`: `comments.delete`
- `quotaCost`: `50`
- `deleted`: `true`
- `targetId`: normalized target comment identifier
- `auth`: safe OAuth-required context summary
- `delegation`: safe delegation summary when delegation context is supplied
- `statusCode`: successful no-content acknowledgment represented without fabricated deleted comment resource data

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not list comments, create replies, edit comments, change moderation status, recover comments, generate moderation advice, rank comments, summarize threads, enrich resources, aggregate across endpoints, or expose authorization secrets.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, duplicate, conflicting, body-bearing, or unsupported option inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot delete the target comment.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_not_found` when the target comment is unavailable, already deleted, or missing.
- `endpoint_unavailable` when the upstream operation is temporarily unavailable.
- `deprecated_endpoint` when upstream deprecation signals apply.
- `upstream_failure` for unexpected upstream failures.

Specific upstream details such as `processingFailure`, `forbidden`, and `commentNotFound` must be mapped to a safe shared category while preserving enough caller-facing guidance to correct the request.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw credential payloads, unsafe upstream diagnostics, or sensitive owner credential details.

## Usage Examples

### Authorized Comment Deletion

```json
{
  "id": "comment-123"
}
```

Expected metadata: `comments.delete`, `Quota cost: 50`, eligible OAuth authorization required, deletes the targeted comment and returns a safe deletion acknowledgment.

### Delegated Owner Context

```json
{
  "id": "comment-123",
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `comments.delete`, `Quota cost: 50`, eligible OAuth authorization required, delegated content-owner context visible without exposing credentials.

### Missing OAuth Failure

```json
{
  "id": "comment-123"
}
```

Expected behavior when no eligible OAuth context is available: reject with safe `authentication_failed` guidance that `comments_delete` requires OAuth.

### Missing Target Failure

```json
{}
```

Expected behavior: reject with safe `invalid_request` guidance that `id` is required.

### Empty Target Failure

```json
{
  "id": ""
}
```

Expected behavior: reject with safe `invalid_request` guidance that `id` must be a non-empty comment identifier.

### Conflicting Target Shape Failure

```json
{
  "id": ["comment-123", "comment-456"]
}
```

Expected behavior: reject with safe `invalid_request` guidance that this tool accepts one target comment per deletion request.

### Unsupported Body Failure

```json
{
  "id": "comment-123",
  "body": {
    "snippet": {
      "textOriginal": "Do not use body fields for deletion."
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `comments.delete` does not accept a request body.

### Unsupported Operation Failure

```json
{
  "id": "comment-123",
  "moderationStatus": "rejected"
}
```

Expected behavior: reject with safe `invalid_request` guidance that moderation belongs to `comments_setModerationStatus`, not `comments_delete`.

### Inaccessible Target Failure

```json
{
  "id": "private-comment-123"
}
```

Expected behavior: map inaccessible target behavior to safe `authorization_failed` or `resource_not_found` guidance according to the shared Layer 2 error convention.

### Already Deleted Target Failure

```json
{
  "id": "already-deleted-comment-123"
}
```

Expected behavior: map missing or already deleted target behavior to safe `resource_not_found` guidance.

## Discovery and Registration Expectations

- `comments_delete` must appear in default MCP tool discovery with complete metadata.
- The descriptor must expose the same public name, quota, auth, availability, input schema, examples, and response boundary documented here.
- `comments_delete` must be exported through the shared YouTube common module surface used by adjacent Layer 2 tools.
- Registry and dispatcher integration must allow representative invocation without custom manual registration by the caller.

## Review Checklist

- Tool identity matches `comments_delete` and upstream `comments.delete`.
- Quota cost 50 appears in metadata, description, usage notes, and examples.
- OAuth-required access is visible before invocation.
- Input schema accepts one target `id` and rejects body-bearing or unrelated request shapes.
- Successful 204/no-content deletion maps to a safe deletion acknowledgment.
- Errors use shared safe categories and do not leak secrets or unsafe upstream diagnostics.
- Scope excludes listing, insertion, update, moderation, recovery, search, ranking, summarization, sentiment, enrichment, and cross-endpoint composition.
