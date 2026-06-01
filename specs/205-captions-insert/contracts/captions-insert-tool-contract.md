# Contract: YT-205 Layer 2 `captions_insert` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `captions_insert` tool. The tool exposes the upstream YouTube Data API `captions.insert` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, mutation, media-upload, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `captions.insert` request
- Caption metadata, media-upload, OAuth, delegated content-owner, and deprecated `sync` rules
- Near-raw successful created caption-resource result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define Layer 3 transcript discovery, caption download, language ranking, cross-endpoint composition, hosted transport changes, persistence, translation, or heuristic interpretation.

## Tool Identity

The public tool must expose:

- `name`: `captions_insert`
- `upstream.resource`: `captions`
- `upstream.method`: `insert`
- `upstream.operationKey`: `captions.insert`
- `quotaCost`: `400`
- `authMode`: `oauth_required`
- `availabilityState`: active media-upload operation, with visible caption-access, delegation, and deprecated-option caveats
- `resourceFamily`: `captions`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `captions.insert`, `Quota cost: 400`, OAuth-required access, and required caption media input.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: comma-separated caption resource parts. The insert endpoint requires `snippet` for the primary supported path.
- `body`: caption resource metadata body.
- `media`: caption media input or safe media descriptor accepted by the implementation contract.

Required body fields:

- `body.snippet.videoId`: video identifier for the caption track.
- `body.snippet.language`: caption language.
- `body.snippet.name`: caption track name.

Optional body fields:

- `body.snippet.isDraft`: draft-state flag.

Optional request fields:

- `onBehalfOfContentOwner`: delegated content-owner context for eligible authorized callers.
- `sync`: deprecated upstream synchronization flag when supported by the public schema.

Rules:

- `part` must be present and non-empty.
- `body.snippet.videoId`, `body.snippet.language`, and `body.snippet.name` must be present and non-empty.
- `media` must be present and must not be represented as public raw caption content in examples, logs, metadata, or errors.
- OAuth authorization must be available for every supported request.
- Delegation context may be supplied only with eligible OAuth authorization.
- `sync`, if accepted, must be marked deprecated in metadata and usage notes.
- Unsupported fields must be rejected when the public schema disallows them.

## Successful Result Contract

Successful results must preserve the endpoint-backed created caption-resource shape:

- `item`: returned caption resource or equivalent created-resource payload.
- `requestedParts`: requested resource parts.
- `endpoint`: `captions.insert`.
- `quotaCost`: `400`.
- `metadata`: safe metadata summary.
- `media`: safe media summary with no raw caption file contents.
- `delegation`: safe delegation summary when delegation context is supplied.

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not download caption content, rank languages, enrich transcript metadata, aggregate across endpoints, expose uploaded file contents, or apply heuristic interpretation.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, or invalid metadata/media inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot create captions for the selected video or delegated content-owner context.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_conflict` or the closest shared equivalent when the upstream reports a duplicate caption conflict.
- `resource_not_found` when the selected video is unavailable or missing.
- `endpoint_unavailable` when the upstream operation is unavailable.
- `upstream_failure` for unexpected upstream failures.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw media payloads, caption file contents, or sensitive channel-owner credential details.

## Usage Examples

### Authorized Caption Creation

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "videoId": "dQw4w9WgXcQ",
      "language": "en",
      "name": "English captions",
      "isDraft": false
    }
  },
  "media": {
    "mimeType": "text/xml",
    "contentRef": "test-safe-caption-media"
  }
}
```

Expected metadata: `captions.insert`, `Quota cost: 400`, eligible OAuth authorization required, caption media input required.

### Delegated Content Owner

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "videoId": "dQw4w9WgXcQ",
      "language": "en",
      "name": "Partner captions"
    }
  },
  "media": {
    "mimeType": "text/xml",
    "contentRef": "test-safe-caption-media"
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `captions.insert`, `Quota cost: 400`, eligible OAuth authorization required, delegated content-owner context visible.

### Metadata-Only Failure

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "videoId": "dQw4w9WgXcQ",
      "language": "en",
      "name": "Missing media"
    }
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that caption media input is required.

### Media-Only Failure

```json
{
  "part": "snippet",
  "media": {
    "mimeType": "text/xml",
    "contentRef": "test-safe-caption-media"
  }
}
```

Expected behavior: reject with safe `invalid_request` guidance that caption metadata body fields are required.

### Deprecated Sync Caveat

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "videoId": "dQw4w9WgXcQ",
      "language": "en",
      "name": "Timed captions"
    }
  },
  "media": {
    "mimeType": "text/xml",
    "contentRef": "test-safe-caption-media"
  },
  "sync": true
}
```

Expected metadata: `sync` is deprecated and must not be presented as the recommended path.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `captions_insert` is listed as a callable tool.
- The input schema includes required `part`, required `body`, required `media`, optional delegation context, and deprecated `sync` caveat if supported.
- The description and metadata expose quota cost `400`.
- The description and metadata expose OAuth-required auth.
- Usage notes include quota, examples, metadata guidance, media-upload guidance, delegation guidance, and deprecated-option caveats.
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

Safe public details may include public tool name, upstream resource and method, quota cost, auth mode, metadata field names, safe media descriptor field names, delegation caveats, deprecated-option caveats, and remediation hints.
