# Contract: YT-204 Layer 2 `captions_list` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `captions_list` tool. The tool exposes the upstream YouTube Data API `captions.list` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `captions.list` request
- Lookup, OAuth, pagination, and delegated content-owner rules
- Near-raw successful result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define Layer 3 transcript discovery, caption download, language ranking, cross-endpoint composition, hosted transport changes, persistence, media upload, or heuristic interpretation.

## Tool Identity

The public tool must expose:

- `name`: `captions_list`
- `upstream.resource`: `captions`
- `upstream.method`: `list`
- `upstream.operationKey`: `captions.list`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active, with visible caption-access and delegation caveats
- `resourceFamily`: `captions`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `captions.list` and `Quota cost: 50`.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: comma-separated caption resource parts. Supported upstream parts include `id` and `snippet`.
- `videoId`: video identifier whose caption tracks are listed.

Optional fields:

- `id`: optional caption track identifier filter
- `maxResults`: optional page size, bounded by the upstream range `0` through `50`
- `pageToken`: optional pagination cursor
- `onBehalfOfContentOwner`: optional delegated content-owner context for eligible authorized callers

Rules:

- `part` must be present and non-empty.
- `videoId` must be present and non-empty.
- OAuth authorization must be available for every supported request.
- `id` may narrow the lookup but must not replace `videoId`.
- Delegation context may be supplied only with eligible OAuth authorization.
- The request body must be empty; all supported inputs are request parameters.
- Unsupported fields must be rejected when the public schema disallows them.

## Successful Result Contract

Successful results must preserve the endpoint-backed caption-track collection shape:

- `items`: returned caption-track resources, including an empty list for valid no-item results
- `requestedParts`: requested resource parts
- `nextPageToken`: continuation token when present
- `prevPageToken`: previous-page token when present
- `pageInfo`: page information when present
- `endpoint`: `captions.list`
- `quotaCost`: `50`
- `lookup`: safe lookup summary
- `delegation`: safe delegation summary when delegation context is supplied

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not download caption content, rank languages, enrich transcript metadata, aggregate across endpoints, or apply heuristic interpretation.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, or malformed inputs
- `authentication_failed` when eligible OAuth credentials are missing or unusable
- `authorization_failed` when credentials exist but cannot access the selected video's captions or delegated content-owner context
- `quota_exhausted` when the upstream quota is exhausted
- `resource_not_found` when the selected video or caption track is unavailable or missing
- `endpoint_unavailable` when the upstream operation is unavailable
- `upstream_failure` for unexpected upstream failures

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw media payloads, caption file contents, or sensitive channel-owner credential details.

## Usage Examples

### Authorized Video Caption Lookup

```json
{
  "part": "snippet",
  "videoId": "dQw4w9WgXcQ",
  "maxResults": 5
}
```

Expected metadata: `captions.list`, `Quota cost: 50`, eligible OAuth authorization required.

### Caption Track Identifier Filter

```json
{
  "part": "id,snippet",
  "videoId": "dQw4w9WgXcQ",
  "id": "CAPTION_TRACK_ID"
}
```

Expected behavior: list caption tracks for the video narrowed to the supplied caption track identifier when accessible.

### Paginated Continuation

```json
{
  "part": "snippet",
  "videoId": "dQw4w9WgXcQ",
  "pageToken": "NEXT_PAGE_TOKEN"
}
```

Expected behavior: return the requested page and preserve any next or previous pagination tokens.

### Delegated Content Owner

```json
{
  "part": "snippet",
  "videoId": "dQw4w9WgXcQ",
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `captions.list`, `Quota cost: 50`, eligible OAuth authorization required, delegated content-owner context visible.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `captions_list` is listed as a callable tool
- The input schema includes required `part`, required `videoId`, optional `id`, optional pagination, and optional delegation context
- The description and metadata expose quota cost `50`
- The description and metadata expose OAuth-required auth
- Usage notes include quota, examples, lookup guidance, and delegation guidance
- The handler is executable and not merely a representative descriptor

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

Safe public details may include public tool name, upstream resource and method, quota cost, auth mode, lookup field names, delegation caveats, and remediation hints.
