# Contract: YT-208 Layer 2 `captions_delete` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `captions_delete` tool. The tool exposes the upstream YouTube Data API `captions.delete` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, mutation-acknowledgment, delegation, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `captions.delete` request
- Caption track identifier, OAuth, delegated content-owner, no-body, and destructive deletion rules
- Near-raw successful deletion acknowledgment result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define Layer 3 transcript discovery, transcript summarization, caption listing, caption creation, caption update, caption download, deletion undo, deletion recovery, language ranking, cross-endpoint composition, hosted transport changes, persistence, local translation, or heuristic interpretation.

## Tool Identity

The public tool must expose:

- `name`: `captions_delete`
- `upstream.resource`: `captions`
- `upstream.method`: `delete`
- `upstream.operationKey`: `captions.delete`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active destructive caption-management operation, with visible OAuth and delegation caveats
- `resourceFamily`: `captions`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `captions.delete`, `Quota cost: 50`, OAuth-required access, required caption track `id`, optional `onBehalfOfContentOwner`, no request body, destructive deletion behavior, and successful no-content acknowledgment behavior.

## Input Contract

The input schema must accept one object request.

Required fields:

- `id`: caption track identifier for the caption track being deleted.

Optional request fields:

- `onBehalfOfContentOwner`: delegated content-owner context for eligible authorized callers.

Rules:

- `id` must be present and non-empty.
- OAuth authorization must be available for every supported request.
- Delegation context may be supplied only with eligible OAuth authorization.
- The request body must be empty; all supported inputs are query parameters.
- Unsupported fields must be rejected when the public schema disallows them.
- Each request targets exactly one caption track.

## Successful Result Contract

Successful results must preserve the endpoint-backed no-content deletion shape:

- `endpoint`: `captions.delete`.
- `quotaCost`: `50`.
- `delete`: safe deletion summary, including caption track identity and deletion outcome.
- `status`: deletion acknowledgment state such as `deleted`.
- `responseStatus`: upstream success status context, expected to reflect HTTP `204 No Content`.
- `hasResponseBody`: false for the upstream success response.
- `delegation`: safe delegation summary when delegation context is supplied.

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not list caption tracks, create caption tracks, update caption tracks, download caption tracks, return deleted caption resources, provide deletion undo, rank languages, enrich transcript metadata, aggregate across endpoints, translate locally, summarize captions, or apply heuristic interpretation.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, or invalid identifier or request-shape inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot delete the selected caption track or use the delegated content-owner context.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_not_found` when the selected caption track is unavailable or missing.
- `endpoint_unavailable` when the upstream operation is unavailable.
- `upstream_failure` for unexpected upstream failures.

Endpoint-specific upstream errors should map safely:

- Upstream `forbidden` should become `authorization_failed`.
- Upstream `captionNotFound` should become `resource_not_found`.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw private caption content, binary payloads, deleted-resource internals, or sensitive channel-owner credential details.

## Usage Examples

### Authorized Caption Deletion

```json
{
  "id": "caption-track-123"
}
```

Expected metadata: `captions.delete`, `Quota cost: 50`, eligible OAuth authorization required, destructive deletion of the target caption track.

### Delegated Content Owner Deletion

```json
{
  "id": "caption-track-123",
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `captions.delete`, `Quota cost: 50`, eligible OAuth authorization required, delegated content-owner context visible.

### Missing-Identifier Failure

```json
{
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected behavior: reject with safe `invalid_request` guidance that a caption track `id` is required.

### Empty-Identifier Failure

```json
{
  "id": " "
}
```

Expected behavior: reject with safe `invalid_request` guidance that `id` must be non-empty.

### Unsupported Option Failure

```json
{
  "id": "caption-track-123",
  "body": {
    "reason": "cleanup"
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that `captions.delete` does not accept a request body or unsupported deletion options.

### Repeated Deletion or Missing Resource

```json
{
  "id": "caption-track-already-deleted"
}
```

Expected behavior: if upstream reports `captionNotFound`, map the failure to safe `resource_not_found` guidance rather than fabricating successful idempotency.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `captions_delete` is listed as a callable tool.
- The input schema includes required `id` and optional delegation context.
- The description and metadata expose quota cost `50`.
- The description and metadata expose OAuth-required auth.
- The description and usage notes expose destructive deletion behavior.
- The description and usage notes expose delegated content-owner caveats.
- The description and usage notes state that the upstream request has no request body.
- Usage notes include quota, examples, no-content acknowledgment context, and error guidance.
- The handler is executable and not merely a representative descriptor.

## Validation Expectations

Focused validation should include:

```bash
python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If Layer 1 wrapper behavior is touched, focused validation should also include:

```bash
python3 -m pytest tests/contract/test_layer1_captions_contract.py tests/unit/test_layer1_foundation.py
```

If default tool discovery or MCP routing changes, focused validation should also include:

```bash
python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py
```

Final validation after implementation code changes must include:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Security and Safety Rules

Public metadata, examples, descriptions, usage notes, errors, logs, and tests must not expose:

- API keys
- OAuth tokens
- Secret values
- Stack traces
- Signed URLs
- Raw private caption content
- Binary payloads
- Deleted-resource internals
- Sensitive video-owner or delegated-owner credential details

Safe public details may include public tool name, upstream resource and method, quota cost, auth mode, request field names, delegation caveats, no-body request rule, no-content response context, destructive mutation warning, and remediation hints.
