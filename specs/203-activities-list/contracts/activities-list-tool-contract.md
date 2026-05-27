# Contract: YT-203 Layer 2 `activities_list` Tool

## Purpose

Define the public MCP-facing contract for the Layer 2 `activities_list` tool. The tool exposes the upstream YouTube Data API `activities.list` endpoint for low-level callers while preserving shared Layer 2 naming, metadata, quota, auth, response-boundary, and error conventions.

## Contract Scope

- Public MCP tool name, description, metadata, and usage notes
- Input schema for one `activities.list` request
- Selector and auth rules for public and authorized-user activity feeds
- Near-raw successful result shape
- Safe failure categories and validation behavior
- Registration and discovery expectations for MCP clients

This contract does not define Layer 3 enrichment, cross-endpoint composition, hosted transport changes, persistence, transcript lookup, ranking, channel expansion, or heuristic interpretation.

## Tool Identity

The public tool must expose:

- `name`: `activities_list`
- `upstream.resource`: `activities`
- `upstream.method`: `list`
- `upstream.operationKey`: `activities.list`
- `quotaCost`: `1`
- `authMode`: `mixed/conditional`
- `availabilityState`: active, with a visible caveat for deprecated `home`
- `resourceFamily`: `activities`
- `responseBoundary.boundaryKind`: `near_raw`

The tool description and usage notes must mention `activities.list` and `Quota cost: 1`.

## Input Contract

The input schema must accept one object request.

Required fields:

- `part`: comma-separated activity resource parts. Supported upstream parts include `contentDetails`, `id`, and `snippet`.

Selector fields:

- `channelId`: public channel activity selector
- `mine`: authorized-user own activity selector
- `home`: deprecated authorized-user home activity selector

Optional fields:

- `maxResults`: optional page size, bounded by the upstream range `0` through `50`
- `pageToken`: optional pagination cursor
- `publishedAfter`: optional lower datetime filter
- `publishedBefore`: optional upper datetime filter
- `regionCode`: optional region context

Rules:

- Exactly one selector field from `channelId`, `mine`, and `home` must be present.
- Requests with no selector must be rejected before invocation.
- Requests with multiple selector fields must be rejected before invocation.
- `mine` and `home` require eligible user authorization.
- `home` must be flagged as deprecated in caller-facing metadata or validation guidance.
- The request body must be empty; all supported inputs are request parameters.
- Unsupported fields must be rejected when the public schema disallows them.

## Successful Result Contract

Successful results must preserve the endpoint-backed activity collection shape:

- `items`: returned activity resources, including an empty list for valid no-item results
- `requestedParts`: requested resource parts
- `nextPageToken`: continuation token when present
- `prevPageToken`: previous-page token when present
- `pageInfo`: page information when present
- `endpoint`: `activities.list`
- `quotaCost`: `1`
- `selector`: safe selector-mode summary

The result may include light MCP clarity fields allowed by shared Layer 2 response-boundary rules. It must not add higher-level ranking, enrichment, transcript lookup, channel expansion, cross-endpoint aggregation, or heuristic interpretation.

## Error Contract

The tool must use shared safe error categories where applicable:

- `invalid_request` for missing, conflicting, unsupported, or malformed inputs
- `authentication_failed` when eligible credentials are missing or unusable
- `authorization_failed` when credentials exist but cannot access the selected activity view
- `quota_exhausted` when the upstream quota is exhausted
- `resource_not_found` when the selected public resource is unavailable or missing
- `deprecated_endpoint` when deprecated selector behavior blocks successful use
- `endpoint_unavailable` when the upstream operation is unavailable
- `upstream_failure` for unexpected upstream failures

Error details must never expose API keys, OAuth tokens, secret values, stack traces, signed URLs, raw media payloads, or sensitive channel-owner credential details.

## Usage Examples

### Public Channel Activity

```json
{
  "part": "snippet,contentDetails",
  "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "maxResults": 5
}
```

Expected metadata: `activities.list`, `Quota cost: 1`, public channel selector.

### Paginated Continuation

```json
{
  "part": "snippet",
  "channelId": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
  "pageToken": "NEXT_PAGE_TOKEN"
}
```

Expected behavior: return the requested page and preserve any next or previous pagination tokens.

### Authorized User Activity

```json
{
  "part": "snippet,contentDetails",
  "mine": true
}
```

Expected metadata: `activities.list`, `Quota cost: 1`, eligible user authorization required.

### Deprecated Home Selector

```json
{
  "part": "snippet",
  "home": true
}
```

Expected metadata: `activities.list`, `Quota cost: 1`, eligible user authorization required, deprecated selector caveat visible.

## Discovery and Registration Expectations

Reviewers must be able to verify through public discovery or registration artifacts that:

- `activities_list` is listed as a callable tool
- The input schema includes required `part`, exactly-one selector behavior, optional pagination, and optional filters
- The description and metadata expose quota cost `1`
- The description and metadata expose mixed/conditional auth
- Usage notes include quota, examples, selector guidance, and the `home` deprecation caveat
- The handler is executable and not merely a representative descriptor

## Validation Expectations

Focused validation should include:

```bash
python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If Layer 1 wrapper behavior is touched, focused validation should also include:

```bash
python3 -m pytest tests/contract/test_layer1_activities_contract.py tests/unit/test_layer1_foundation.py
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
- Sensitive channel-owner or delegated-owner credential details

Safe public details may include public tool name, upstream resource and method, quota cost, auth mode, selector mode, parameter names, deprecation caveats, and remediation hints.
