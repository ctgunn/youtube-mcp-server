# Contract: Layer 2 `channels_update` Tool

## Public Tool Identity

- **Tool name**: `channels_update`
- **Mapped upstream operation**: `channels.update`
- **Resource family**: `channels`
- **Layer**: Layer 2 endpoint-backed public MCP tool
- **Official quota cost**: `50` units per invocation
- **Auth mode**: `oauth_required`
- **Availability**: Active, with writable-part and authorization caveats

## Scope

`channels_update` updates supported YouTube channel metadata through the upstream channel update endpoint and returns the updated channel resource in a near-raw shape.

The tool does not:

- Retrieve or search channels.
- Upload channel banner images.
- Activate a banner unless the caller supplies the supported channel body field for a `brandingSettings` update.
- Rank, enrich, summarize, or analyze channels.
- Expand channels into videos, playlists, subscriptions, analytics, comments, captions, or related resources.
- Perform multi-step channel-management orchestration.
- Persist channel update state, OAuth credentials, request bodies, or banner URLs.

## Input Contract

The input is a JSON-compatible object.

```json
{
  "type": "object",
  "required": ["part", "body"],
  "properties": {
    "part": {
      "type": "string",
      "enum": ["brandingSettings", "localizations"]
    },
    "body": {
      "type": "object",
      "required": ["id"],
      "properties": {
        "id": {
          "type": "string",
          "minLength": 1
        },
        "brandingSettings": {
          "type": "object"
        },
        "localizations": {
          "type": "object"
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

### Input Rules

- `part` is required and must identify exactly one supported writable part.
- Supported writable parts for this slice are `brandingSettings` and `localizations`.
- `body` is required and must be a non-empty channel resource object.
- `body.id` is required and must be non-empty.
- The field matching the selected `part` is required in `body`.
- Unsupported parts, comma-separated multiple parts, empty parts, read-only fields, unrelated channel fields, unsupported channel lookup fields, banner upload fields, video expansion fields, playlist expansion fields, analytics fields, and orchestration instructions must be rejected or clearly flagged as outside this endpoint contract.
- `onBehalfOfContentOwner` is an official documentation caveat but is not part of this slice's public input contract unless YT-111 is intentionally expanded first.
- Callers must be warned that channel update behavior can overwrite mutable values within the selected part when omitted from the submitted body.

## Discovery Metadata Requirements

Tool discovery metadata must include:

- `name`: `channels_update`
- `upstream.resource`: `channels`
- `upstream.method`: `update`
- `upstream.operationKey`: `channels.update`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: active availability with writable-part caveat
- `resourceFamily`: `channels`
- `inputContract`: the public input contract
- `responseConvention`: mutation-result convention
- `responseBoundary`: near-raw boundary
- `usageNotes`: quota, OAuth, writable-part, part-to-body alignment, overwrite, official content-owner delegation caveat, banner-boundary, and out-of-scope notes
- `caveats`: supported writable parts, official-doc caveats for unsupported parts and delegation, read-only field exclusions, and no-composition boundary

Discovery descriptions and usage notes must visibly include `Quota cost: 50`.

## Response Contract

Successful responses must preserve the updated upstream channel resource or valid updated-resource outcome.

Representative successful shape:

```json
{
  "endpoint": "channels.update",
  "quotaCost": 50,
  "updatedPart": "brandingSettings",
  "requestedParts": ["brandingSettings"],
  "item": {
    "kind": "youtube#channel",
    "etag": "etag-value",
    "id": "UC123",
    "brandingSettings": {
      "channel": {
        "description": "Updated channel description"
      }
    }
  }
}
```

Response rules:

- Preserve returned channel resource fields when present.
- Include selected writable part and requested parts after safe normalization.
- Include safe operation context such as endpoint identity and quota cost.
- Do not echo OAuth tokens, API keys, or sensitive channel body values beyond the returned endpoint resource.
- Do not fabricate channel lookup results, analytics, search ranking, video lists, playlist lists, banner upload state, or enriched summaries.

## Error Contract

The tool must surface safe shared Layer 2 error categories:

- `invalid_request`
- `authentication_failed`
- `authorization_failed`
- `quota_exhausted`
- `resource_not_found`
- `endpoint_unavailable`
- `upstream_failure`

Endpoint-specific invalid request examples:

- Missing `part`.
- Empty `part`.
- Multiple writable parts in one request.
- Unsupported writable part.
- Missing `body`.
- Empty `body`.
- Missing `body.id`.
- Selected part missing from `body`.
- Read-only or unsupported channel fields in `body`.
- Unsupported top-level fields.
- Unsupported channel lookup, banner upload, analytics, video expansion, playlist expansion, or orchestration fields.
- Upstream branding or localization validation failure.

Security rules:

- Errors must not expose OAuth tokens, API keys, stack traces, private channel data, raw sensitive request bodies, or secret values.
- Authorization failures must be distinguishable from invalid update shapes.
- Missing OAuth must identify the OAuth requirement without exposing user credentials.
- Unsupported delegation fields must be rejected safely while this slice does not expose the official content-owner delegation parameter.

## Required Examples

The implementation must provide safe caller-facing examples for:

- `brandingSettings` update.
- `localizations` update.
- Banner URL activation through `brandingSettings.image.bannerExternalUrl`.
- Missing OAuth failure.
- Missing body or missing channel ID validation failure.
- Part-to-body mismatch validation failure.
- Read-only or unsupported field rejection.
- Unsupported writable part rejection.

## Verification Requirements

Before implementation is considered complete:

- Focused contract tests must prove discovery metadata includes endpoint identity, quota cost, OAuth requirement, supported writable parts, read-only exclusions, part-to-body alignment, overwrite warning, official-doc caveat, and banner upload boundary.
- Unit tests must prove writable-part, body, OAuth, and unsupported delegation validation reject unsupported inputs safely.
- Integration tests must prove default registration exposes executable `channels_update`.
- Handler tests must prove successful update result mapping preserves returned resource fields and safe operation context.
- Regression tests must preserve existing baseline, retrieval, activities, captions, channel banner, and `channels_list` tools.
- Final validation must include `python3 -m pytest` and `python3 -m ruff check .`.
- Every new or changed Python function must include a reStructuredText docstring.
