# Data Model: Layer 2 Tool `comments_list`

## Entity: Comments List Tool

**Description**: Public Layer 2 MCP tool representing one direct YouTube Data API `comments.list` operation.

**Fields**

- `tool_name`: Constant string `comments_list`.
- `upstream_resource`: Constant string `comments`.
- `upstream_method`: Constant string `list`.
- `operation_key`: Constant string `comments.list`.
- `quota_cost`: Constant integer `1`.
- `auth_mode`: Mixed or conditional access mode with public-read and access-sensitive caveats documented.
- `availability_state`: Active unless official documentation changes.
- `input_contract`: JSON-compatible schema for the list request.
- `response_convention`: Metadata describing comment collection, pagination, selected parts, selector mode, and text-format context.
- `response_boundary`: Near-raw or lightly reshaped result boundary with explicit disallowed higher-level behaviors.
- `usage_notes` and `caveats`: Caller-facing text that includes quota, auth, selector, pagination, text-format, no-body, and out-of-scope behavior.

**Relationships**

- Uses the Layer 1 `comments.list` wrapper for endpoint execution.
- Is registered in the default MCP tool dispatcher.
- Is exported through `mcp_server.tools.youtube_common`.

**Validation Rules**

- Tool metadata must include quota cost `1` in description and usage notes.
- Tool metadata must not expose API keys, OAuth tokens, stack traces, raw diagnostics, or unsafe request context.
- Tool must remain close to the upstream endpoint and not add thread discovery, mutation, moderation, enrichment, sentiment, ranking, or summarization workflows.

## Entity: Comments List Request

**Description**: Caller-provided arguments for one comment retrieval operation.

**Fields**

- `part` (required string): Comma-separated comment resource parts requested by the caller.
- `id` (optional string): Comma-separated comment IDs for direct comment retrieval.
- `parentId` (optional string): Parent comment ID used to retrieve reply comments.
- `maxResults` (optional integer): Page size for supported paginated retrieval.
- `pageToken` (optional string): Page token for supported paginated retrieval.
- `textFormat` (optional string): Comment text format, either `html` or `plainText`.

**Relationships**

- Produces exactly one Layer 1 `comments.list` call when validation and access checks pass.
- Produces a `Comments List Result` on success or a shared Layer 2 error on failure.

**Validation Rules**

- `part` must be present, a string, and non-empty after trimming.
- Exactly one of `id` or `parentId` must be present.
- `id`, when present, must be a non-empty string and must not be combined with `parentId`, `maxResults`, or `pageToken`.
- `parentId`, when present, must be a non-empty string and may be combined with supported `maxResults`, `pageToken`, and `textFormat`.
- `maxResults`, when present, must be an integer from 1 through 100.
- `pageToken`, when present, must be a non-empty string and must not be combined with `id`.
- `textFormat`, when present, must be `html` or `plainText`.
- No request body is accepted.
- Unsupported fields such as `videoId`, `channelId`, `threadId`, `body`, `order`, `searchTerms`, `moderationStatus`, `sentiment`, `rank`, `summarize`, `insert`, `update`, or `delete` must be rejected before Layer 1 execution.

## Entity: Retrieval Selector

**Description**: The caller-selected upstream filter mode.

**Fields**

- `name`: Either `id` or `parentId`.
- `value`: Non-empty selector string supplied by the caller.

**Validation Rules**

- Missing selectors return caller-facing `invalid_request` feedback.
- Multiple selectors return caller-facing `invalid_request` feedback.
- Empty, non-string, malformed, duplicate, or excessive selector values return caller-facing `invalid_request` feedback.
- Upstream not-found responses map to `resource_not_found`.

## Entity: Pagination Context

**Description**: Caller-provided and returned paging information for parent-comment retrieval.

**Fields**

- `maxResults`: Optional requested page size.
- `pageToken`: Optional requested page token.
- `nextPageToken`: Optional returned token for the next result page.
- `pageInfo`: Optional returned result count information.

**Validation Rules**

- Pagination inputs are rejected with the `id` selector.
- `maxResults` must be between 1 and 100 when provided.
- Empty or non-string `pageToken` values are rejected.
- Returned page fields are preserved without fabricating missing tokens.

## Entity: Text Format Selection

**Description**: Caller-selected comment text representation for upstream-supported text fields.

**Fields**

- `textFormat`: Optional value `html` or `plainText`.

**Validation Rules**

- Unsupported text-format values are rejected as `invalid_request`.
- The result records the selected or default text format as context but does not transform, sanitize, summarize, or enrich comment text beyond the upstream response.

## Entity: Comments List Result

**Description**: Public result returned after successful retrieval.

**Fields**

- `endpoint`: Constant string `comments.list`.
- `quotaCost`: Constant integer `1`.
- `items`: Returned comment resources, defaulting to an empty list only when the upstream response is an empty successful collection.
- `requestedParts`: Normalized list of requested parts.
- `selector`: Safe object naming the selected retrieval mode.
- `textFormat`: Returned or requested text-format context.
- `nextPageToken`: Optional returned next page token.
- `pageInfo`: Optional returned paging information.
- `kind` and `etag`: Optional upstream response metadata when returned.

**Validation Rules**

- Must preserve empty successful collections as successful results.
- Must preserve safe upstream fields when returned.
- Must not fabricate comment fields, thread fields, channel fields, moderation state, sentiment, rankings, summaries, or enrichment fields.
- Must not expose API keys, OAuth tokens, stack traces, or unsafe raw diagnostics.

## State Transitions

1. `Unvalidated Request` -> `Rejected` when required part, selector, pagination, text-format, access, or unsupported-field validation fails.
2. `Unvalidated Request` -> `Validated Request` when argument checks pass.
3. `Validated Request` -> `Layer 1 Executed` after exactly one `comments.list` wrapper call.
4. `Layer 1 Executed` -> `Comments Returned` when upstream retrieval succeeds with one or more items.
5. `Layer 1 Executed` -> `Empty Collection Returned` when upstream retrieval succeeds with no matching reply comments or an empty result page.
6. `Layer 1 Executed` -> `Mapped Error` when upstream returns quota, auth, invalid, not-found, unavailable, deprecated, or unexpected failure.
