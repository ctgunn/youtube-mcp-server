# Contract: YT-219 Layer 2 `comments_setModerationStatus` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `comments_setModerationStatus` tool. The tool exposes the upstream YouTube Data API `comments.setModerationStatus` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, OAuth, response-boundary, mutation acknowledgment, validation, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `comments.setModerationStatus` moderation request
- Required OAuth access, target comment identifiers, moderation status values, optional `banAuthor` rule, no-body rule, and delegated owner context
- Near-raw successful moderation acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define comment listing, reply creation, comment editing, comment deletion, automated moderation recommendations, sentiment analysis, ranking, summarization, enrichment, hosted transport changes, persistence, or cross-endpoint composition.

## Tool Identity

The public tool must expose:

- `name`: `comments_setModerationStatus`
- `upstream.resource`: `comments`
- `upstream.method`: `setModerationStatus`
- `upstream.operationKey`: `comments.setModerationStatus`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active write operation, with visible target-comment, moderation-status, optional-flag, no-body, and authorization caveats
- `resourceFamily`: `comments`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `comments.setModerationStatus`, `Quota cost: 50`, OAuth-required access, required target comment identifiers, required moderation status, accepted statuses, `banAuthor` compatibility, and the no-body request boundary.

## Input Contract

The input schema must accept one object request.

Required fields:

- `id`: one comment identifier or a list/comma-separated representation of one or more comment identifiers, normalized according to the shared comments-family convention.
- `moderationStatus`: one of `heldForReview`, `published`, or `rejected`.

Optional request fields:

- `banAuthor`: boolean flag accepted only when `moderationStatus` is `rejected`.
- `onBehalfOfContentOwner`: delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

Rules:

- `id` must be present and include at least one non-empty target comment identifier.
- Duplicate target comment identifiers must be rejected.
- `moderationStatus` must be present and one of `heldForReview`, `published`, or `rejected`.
- `banAuthor` must be boolean when supplied.
- `banAuthor` may be supplied only when `moderationStatus` is `rejected`.
- OAuth authorization must be available for every supported request.
- Delegation context may be supplied only with eligible OAuth authorization.
- Request bodies must be rejected because the upstream operation supports query parameters only.
- Unsupported fields must be rejected when the public schema disallows them.
- Request shapes for comment listing, reply creation, comment editing, deletion, search, automated moderation advice, ranking, summarization, sentiment, or enrichment must be rejected or clearly flagged as out of scope.

## Successful Result Contract

Successful results must preserve the endpoint-backed moderation acknowledgment shape:

- `endpoint`: `comments.setModerationStatus`
- `quotaCost`: `50`
- `moderated`: `true`
- `targetIds`: normalized target comment identifiers
- `moderationStatus`: requested moderation status
- `banAuthor`: safe optional flag context when supplied
- `auth`: safe OAuth-required context summary
- `delegation`: safe delegation summary when delegation context is supplied
- `statusCode`: successful no-content acknowledgment represented without fabricated comment resource data

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not list comments, create replies, edit comments, delete comments, generate moderation advice, rank comments, summarize threads, enrich resources, aggregate across endpoints, or expose authorization secrets.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, duplicate, or invalid `id`, `moderationStatus`, `banAuthor`, body, or unsupported option inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot moderate the target comments.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_not_found` when one or more target comments are unavailable or missing.
- `endpoint_unavailable` when the upstream operation is temporarily unavailable.
- `deprecated_endpoint` when upstream deprecation signals apply.
- `upstream_failure` for unexpected upstream failures.

Specific upstream details such as `banWithoutReject`, `operationNotSupported`, `processingFailure`, `forbidden`, and `commentNotFound` must be mapped to a safe shared category while preserving enough caller-facing guidance to correct the request.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw credential payloads, unsafe upstream diagnostics, or sensitive owner credential details.

## Usage Examples

### Authorized Publish Moderation

```json
{
  "id": ["comment-123"],
  "moderationStatus": "published"
}
```

Expected metadata: `comments.setModerationStatus`, `Quota cost: 50`, eligible OAuth authorization required, clears the targeted comment for public display.

### Authorized Hold For Review

```json
{
  "id": ["comment-123", "comment-456"],
  "moderationStatus": "heldForReview"
}
```

Expected metadata: `comments.setModerationStatus`, `Quota cost: 50`, eligible OAuth authorization required, marks the targeted comments as awaiting moderator review.

### Authorized Rejection With Author Ban

```json
{
  "id": ["comment-123"],
  "moderationStatus": "rejected",
  "banAuthor": true
}
```

Expected metadata: `comments.setModerationStatus`, `Quota cost: 50`, eligible OAuth authorization required, rejects the target comment and requests compatible author-ban behavior.

### Delegated Owner Context

```json
{
  "id": ["comment-123"],
  "moderationStatus": "rejected",
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `comments.setModerationStatus`, `Quota cost: 50`, eligible OAuth authorization required, delegated content-owner context visible without exposing credentials.

### Missing OAuth Failure

```json
{
  "id": ["comment-123"],
  "moderationStatus": "published"
}
```

Expected behavior when no eligible OAuth context is available: reject with safe `authentication_failed` guidance that `comments_setModerationStatus` requires OAuth.

### Missing Target Failure

```json
{
  "moderationStatus": "published"
}
```

Expected behavior: reject with safe `invalid_request` guidance that `id` is required.

### Duplicate Target Failure

```json
{
  "id": ["comment-123", "comment-123"],
  "moderationStatus": "rejected"
}
```

Expected behavior: reject with safe `invalid_request` guidance that duplicate comment identifiers are unsupported.

### Missing Status Failure

```json
{
  "id": ["comment-123"]
}
```

Expected behavior: reject with safe `invalid_request` guidance that `moderationStatus` is required.

### Unsupported Status Failure

```json
{
  "id": ["comment-123"],
  "moderationStatus": "spam"
}
```

Expected behavior: reject with safe `invalid_request` guidance that supported statuses are `heldForReview`, `published`, and `rejected`.

### Incompatible Author Ban Failure

```json
{
  "id": ["comment-123"],
  "moderationStatus": "published",
  "banAuthor": true
}
```

Expected behavior: reject with safe `invalid_request` guidance that `banAuthor` is valid only with `rejected`.

### Unsupported Body Failure

```json
{
  "id": ["comment-123"],
  "moderationStatus": "rejected",
  "body": {
    "snippet": {
      "textOriginal": "Do not use body fields for moderation."
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `comments_setModerationStatus` does not accept a request body.

### Target Comment Not Found

```json
{
  "id": ["missing-comment"],
  "moderationStatus": "rejected"
}
```

Expected behavior: preserve a safe `resource_not_found` or closest shared target-comment failure category.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `comments_setModerationStatus` is listed as a callable tool.
- Its metadata includes `comments.setModerationStatus`, quota cost `50`, OAuth-required auth, and active availability.
- Its schema requires `id` and `moderationStatus`, allows compatible optional fields, disallows request bodies, and rejects unsupported properties.
- Its examples include at least authorized publish, authorized hold-for-review, authorized rejection with compatible `banAuthor`, delegated owner context, missing OAuth, missing target, duplicate target, missing status, unsupported status, incompatible `banAuthor`, unsupported body, and target-not-found failure.
- Its safe error surface follows shared Layer 2 error categories.

## Test Contract Expectations

The Red phase must add failing tests before implementation for:

- Public metadata, schema, usage notes, caveats, and examples.
- Default registry discovery and tool catalog inclusion.
- Successful moderation acknowledgment with 204/no-content upstream response.
- Optional delegated owner context.
- Missing OAuth, missing target IDs, duplicate target IDs, missing moderation status, unsupported status, invalid `banAuthor`, incompatible `banAuthor`, unsupported body, unsupported options, and upstream failure mapping.
- Safe error sanitization for tokens, stack traces, raw request diagnostics, and unsafe upstream detail.

The Green and Refactor phases must make these tests pass with the minimal endpoint-backed implementation and then run the focused suite, full `pytest`, and `ruff check .`.
