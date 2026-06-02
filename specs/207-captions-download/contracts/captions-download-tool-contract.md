# Contract: YT-207 Layer 2 `captions_download` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `captions_download` tool. The tool exposes the upstream YouTube Data API `captions.download` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, downloaded-content, conversion-option, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `captions.download` request
- Caption track identifier, output format, target language, OAuth, delegated content-owner, and permission rules
- Near-raw successful downloaded-content result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define Layer 3 transcript discovery, transcript summarization, caption listing, caption creation, caption update, caption deletion, language ranking, cross-endpoint composition, hosted transport changes, persistence, local translation, or heuristic interpretation.

## Tool Identity

The public tool must expose:

- `name`: `captions_download`
- `upstream.resource`: `captions`
- `upstream.method`: `download`
- `upstream.operationKey`: `captions.download`
- `quotaCost`: `200`
- `authMode`: `oauth_required`
- `availabilityState`: active permission-sensitive download operation, with visible caption-access, delegation, and conversion caveats
- `resourceFamily`: `captions`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `captions.download`, `Quota cost: 200`, OAuth-required access, required caption track `id`, permission-to-edit caveat, supported `tfmt` values, and `tlang` guidance.

## Input Contract

The input schema must accept one object request.

Required fields:

- `id`: caption track identifier for the caption content being downloaded.

Optional request fields:

- `tfmt`: output format. Supported values are `sbv`, `scc`, `srt`, `ttml`, and `vtt`.
- `tlang`: target language conversion value, represented as an ISO 639-1 two-letter language code.
- `onBehalfOfContentOwner`: delegated content-owner context for eligible authorized callers.

Rules:

- `id` must be present and non-empty.
- OAuth authorization must be available for every supported request.
- The authorized user must have permission to edit the video associated with the caption track.
- `tfmt`, when supplied, must use one documented supported value.
- `tlang`, when supplied, must use a two-letter language-code shape.
- Delegation context may be supplied only with eligible OAuth authorization.
- The request body must be empty; all supported inputs are request parameters.
- Unsupported fields must be rejected when the public schema disallows them.

## Successful Result Contract

Successful results must preserve the endpoint-backed downloaded-content shape:

- `content`: downloaded caption content or supported safe content representation.
- `contentType`: response content type when available, expected to reflect `application/octet-stream` upstream response context.
- `contentForm`: indicator that distinguishes text, binary, encoded, or descriptor-shaped content representation.
- `sizeBytes`: optional safe size descriptor when available.
- `requestedFormat`: requested `tfmt` value when supplied.
- `requestedLanguage`: requested `tlang` value when supplied.
- `endpoint`: `captions.download`.
- `quotaCost`: `200`.
- `download`: safe download summary, including caption track identity and conversion options.
- `delegation`: safe delegation summary when delegation context is supplied.

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not list caption tracks, create caption tracks, update caption tracks, delete caption tracks, rank languages, enrich transcript metadata, aggregate across endpoints, translate locally, summarize captions, or apply heuristic interpretation.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, unsupported, malformed, or invalid identifier or conversion inputs.
- `authentication_failed` when eligible OAuth credentials are missing or unusable.
- `authorization_failed` when credentials exist but cannot download the selected caption track or use the delegated content-owner context.
- `quota_exhausted` when the upstream quota is exhausted.
- `resource_not_found` when the selected caption track is unavailable or missing.
- `endpoint_unavailable` when the upstream operation is unavailable.
- `upstream_failure` for unexpected upstream failures.

Endpoint-specific upstream errors should map safely:

- Upstream `couldNotConvert` should become `invalid_request` with safe conversion guidance.
- Upstream `forbidden` should become `authorization_failed`.
- Upstream `captionNotFound` should become `resource_not_found`.

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw private caption content, binary payloads, or sensitive channel-owner credential details.

## Usage Examples

### Authorized Default Caption Download

```json
{
  "id": "caption-track-123"
}
```

Expected metadata: `captions.download`, `Quota cost: 200`, eligible OAuth authorization required, permission to edit the video required.

### Authorized Format-Specific Caption Download

```json
{
  "id": "caption-track-123",
  "tfmt": "srt"
}
```

Expected metadata: `captions.download`, `Quota cost: 200`, eligible OAuth authorization required, caption content requested in supported `srt` output format.

### Authorized Target-Language Conversion

```json
{
  "id": "caption-track-123",
  "tlang": "es"
}
```

Expected metadata: `captions.download`, `Quota cost: 200`, eligible OAuth authorization required, machine-generated target-language conversion requested through upstream `tlang`.

### Format and Target-Language Conversion

```json
{
  "id": "caption-track-123",
  "tfmt": "vtt",
  "tlang": "fr"
}
```

Expected behavior: request a supported output format and target language; if upstream cannot convert, map the failure to safe conversion guidance.

### Delegated Content Owner

```json
{
  "id": "caption-track-123",
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Expected metadata: `captions.download`, `Quota cost: 200`, eligible OAuth authorization required, delegated content-owner context visible.

### Missing-Identifier Failure

```json
{
  "tfmt": "srt"
}
```

Expected behavior: reject with safe `invalid_request` guidance that a caption track `id` is required.

### Unsupported Format Failure

```json
{
  "id": "caption-track-123",
  "tfmt": "unsupported-format"
}
```

Expected behavior: reject with safe `invalid_request` guidance listing the supported output format values.

### Malformed Language Failure

```json
{
  "id": "caption-track-123",
  "tlang": "spanish"
}
```

Expected behavior: reject with safe `invalid_request` guidance that `tlang` must use an ISO 639-1-style two-letter language code.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `captions_download` is listed as a callable tool.
- The input schema includes required `id`, optional `tfmt`, optional `tlang`, and optional delegation context.
- The description and metadata expose quota cost `200`.
- The description and metadata expose OAuth-required auth.
- The description and usage notes expose permission-to-edit and delegated content-owner caveats.
- The description and usage notes expose supported `tfmt` values and `tlang` language-code guidance.
- Usage notes include quota, examples, conversion guidance, binary response context, and error guidance.
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
- Sensitive video-owner or delegated-owner credential details

Safe public details may include public tool name, upstream resource and method, quota cost, auth mode, request field names, supported `tfmt` values, `tlang` code-shape guidance, delegation caveats, binary response context, and remediation hints.
