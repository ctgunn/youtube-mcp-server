# Contract: YT-206 Layer 2 `captions_update` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `captions_update` tool. The tool exposes the upstream YouTube Data API `captions.update` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, mutation, media-update, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `captions.update` request
- Caption update body, optional media-replacement, OAuth, delegated content-owner, and deprecated `sync` rules
- Near-raw successful updated caption-resource result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define Layer 3 transcript discovery, caption creation, caption download, language ranking, cross-endpoint composition, hosted transport changes, persistence, translation, or heuristic interpretation.

## Tool Identity

The public tool must expose:

- `name`: `captions_update`
- `upstream.resource`: `captions`
- `upstream.method`: `update`
- `upstream.operationKey`: `captions.update`
- `quotaCost`: `450`
- `authMode`: `oauth_required`
- `availabilityState`: active media-capable mutation operation, with visible caption-access, delegation, and deprecated-option caveats
- `resourceFamily`: `captions`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `captions.update`, `Quota cost: 450`, OAuth-required access, required caption update body, and optional replacement caption media.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: comma-separated caption resource parts. The update endpoint supports `id` and `snippet`; `snippet` is used when updating draft status, while `id` applies when not updating draft status.
- `body`: caption resource update body.

Required body fields:

- `body.id`: caption track identifier for the caption resource being updated.

Optional body fields:

- `body.snippet.isDraft`: draft-state flag.

Optional request fields:

- `media`: replacement caption media input or safe media descriptor accepted by the implementation contract.
- `onBehalfOfContentOwner`: delegated content-owner context for eligible authorized callers.
- `sync`: deprecated upstream synchronization flag when supported by the public schema. If accepted, metadata must note that upstream processing requires an updated caption file.

Rules:

- `part` must be present and non-empty.
- `body.id` must be present and non-empty.
- OAuth authorization must be available for every supported request.
- `media`, when supplied, must be paired with a valid update body and must not be represented as public raw caption content in examples, logs, metadata, or errors.
- Delegation context may be supplied only with eligible OAuth authorization.
- `sync`, if accepted, must be marked deprecated in metadata and usage notes and must not be promoted as the normal path.
- Unsupported fields must be rejected when the public schema disallows them.

## Successful Result Contract

Successful results must preserve the endpoint-backed updated caption-resource shape:

- `item`: returned caption resource or equivalent updated-resource payload.
- `requestedParts`: requested resource parts.
- `endpoint`: `captions.update`.
- `quotaCost`: `450`.
- `update`: safe update-body summary, including caption track identity and requested writable fields.
- `media`: safe media summary when media is supplied, with no raw caption file contents.
- `delegation`: safe delegation summary when delegation context is supplied.

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not download caption content, create caption tracks, rank languages, enrich transcript metadata, aggregate across endpoints, expose uploaded file contents, or apply heuristic interpretation.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, or invalid body/media inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot update the selected caption track or delegated content-owner context.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_not_found` when the selected caption track is unavailable or missing.
- `endpoint_unavailable` when the upstream operation is unavailable.
- `upstream_failure` for unexpected upstream failures.

Endpoint-specific upstream errors should map safely:

- Upstream `contentRequired` should become `invalid_request` when `sync` or a supported media-related request requires caption file contents.
- Upstream `forbidden` should become `authorization_failed`.
- Upstream `captionNotFound` should become `resource_not_found`.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw media payloads, caption file contents, or sensitive channel-owner credential details.

## Usage Examples

### Authorized Body-Only Caption Update

```json
{
  "part": "snippet",
  "body": {
    "id": "caption-track-123",
    "snippet": {
      "isDraft": false
    }
  }
}
```

Expected metadata: `captions.update`, `Quota cost: 450`, eligible OAuth authorization required, caption update body required.

### Authorized Body-Plus-Media Caption Update

```json
{
  "part": "id",
  "body": {
    "id": "caption-track-123"
  },
  "media": {
    "mimeType": "text/xml",
    "contentRef": "test-safe-caption-media"
  }
}
```

Expected metadata: `captions.update`, `Quota cost: 450`, eligible OAuth authorization required, replacement caption media handled as part of a valid update request.

### Delegated Content Owner

```json
{
  "part": "snippet",
  "body": {
    "id": "caption-track-123",
    "snippet": {
      "isDraft": true
    }
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `captions.update`, `Quota cost: 450`, eligible OAuth authorization required, delegated content-owner context visible.

### Missing-Body Failure

```json
{
  "part": "snippet"
}
```

Expected behavior: reject with safe `invalid_request` guidance that a caption update body with `id` is required.

### Media-Without-Body Failure

```json
{
  "part": "id",
  "media": {
    "mimeType": "text/xml",
    "contentRef": "test-safe-caption-media"
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that replacement media must be paired with a valid caption update body.

### Deprecated Sync Caveat

```json
{
  "part": "id",
  "body": {
    "id": "caption-track-123"
  },
  "media": {
    "mimeType": "text/xml",
    "contentRef": "test-safe-caption-media"
  },
  "sync": true
}
```

Expected metadata: `sync` is deprecated, is not presented as the recommended path, and requires updated caption file contents when processed upstream.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `captions_update` is listed as a callable tool.
- The input schema includes required `part`, required `body.id`, optional `body.snippet.isDraft`, optional media input, optional delegation context, and deprecated `sync` caveat if supported.
- The description and metadata expose quota cost `450`.
- The description and metadata expose OAuth-required auth.
- Usage notes include quota, examples, update-body guidance, optional media-replacement guidance, delegation guidance, and deprecated-option caveats.
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
- Raw media payloads
- Caption file contents
- Sensitive video-owner or delegated-owner credential details

Safe public details may include public tool name, upstream resource and method, quota cost, auth mode, update field names, safe media descriptor field names, delegation caveats, deprecated-option caveats, and remediation hints.
