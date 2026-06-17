# Research: Layer 2 Tool `comments_list`

## Decision: Implement `comments_list` as an endpoint-backed Layer 2 tool in a comments resource-family module

**Rationale**: The PRD defines Layer 2 tools as one-to-one public MCP tools for documented YouTube Data API methods. No Layer 2 comments module currently exists, while the local codebase already groups endpoint-backed tools by resource family for captions, channels, and channel sections. A new `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py` module keeps this slice cohesive and leaves room for future `comments_insert`, `comments_update`, `comments_setModerationStatus`, and `comments_delete` tools.

**Alternatives considered**: Adding comments code to `examples.py`, `contracts.py`, or an unrelated resource-family module was rejected because it would blur ownership. A higher-level discussion or moderation module was rejected because YT-216 is explicitly low-level and endpoint-backed.

## Decision: Use public tool name `comments_list`

**Rationale**: YT-202 requires `resource_method` naming without a redundant `youtube_` prefix while preserving official resource and method identity. The PRD and seed list the public Layer 2 mapping as `comments_list`.

**Alternatives considered**: `comments.list`, `youtube_comments_list`, and `list_comments` were rejected because they drift from established Layer 2 naming and tool-discovery conventions.

## Decision: Require `part` plus exactly one selector, either `id` or `parentId`

**Rationale**: Official `comments.list` documentation requires `part`, supports the `id` filter for comma-separated comment IDs, supports the `parentId` filter for replies to a parent comment, and says callers must specify exactly one filter. The existing YT-116 Layer 1 wrapper already centers on ID-based and parent-comment-based retrieval modes.

**Alternatives considered**: Allowing missing selectors was rejected because the upstream endpoint requires a filter. Allowing both selectors was rejected because the official filter contract requires exactly one. Adding `videoId` or thread discovery was rejected because those belong to `commentThreads.list` or higher-level tools.

## Decision: Record quota cost as 1 everywhere the caller sees the tool

**Rationale**: Official `comments.list` documentation and the YouTube quota table both state that `comments.list` costs 1 quota unit. YT-202 and the feature spec require the quota cost in metadata, description, usage notes, and examples.

**Alternatives considered**: Omitting quota from examples was rejected because FR-004 and YT-202 require pre-invocation quota visibility. Treating invalid requests as quota-free was rejected because official quota guidance says invalid API requests still incur at least one quota point when sent upstream; local validation should avoid unnecessary upstream calls.

## Decision: Declare mixed or conditional auth and document access-sensitive limitations

**Rationale**: The project inventory describes `comments_list` auth as API key or mixed depending on filter mode, and the official endpoint documents insufficient-permission failures when requested comments cannot be retrieved. Public metadata should therefore avoid declaring the tool OAuth-only, while still making access-sensitive limitations clear.

**Alternatives considered**: `oauth_required` was rejected because the endpoint supports public read-style retrieval in common cases and the local Layer 1 wrapper uses API-key paths for representative selector tests. `api_key` only was rejected because some comments can be unavailable or permission-sensitive.

## Decision: Support pagination only where upstream allows it

**Rationale**: Official docs allow `maxResults` values from 1 to 100 and `pageToken`, but state that neither is supported with the `id` parameter. Pagination should therefore be accepted for parent-comment retrieval and rejected with ID-based retrieval.

**Alternatives considered**: Always allowing pagination was rejected because it would violate upstream behavior. Always rejecting pagination was rejected because parent-comment reply retrieval supports paginated result traversal.

## Decision: Support `textFormat` as `html` or `plainText`

**Rationale**: Official docs allow `html` and `plainText`, with `html` as the default. Layer 2 should expose that endpoint-native option and preserve the selected text-format context without doing additional text normalization.

**Alternatives considered**: Adding custom formats, Markdown conversion, plain-text normalization, or sanitization flags was rejected because they are higher-level transformations outside the endpoint-backed Layer 2 scope.

## Decision: Map success to a near-raw comment list result

**Rationale**: Official success returns a `youtube#commentListResponse` with `kind`, `etag`, optional `nextPageToken`, `pageInfo`, and `items[]`. The Layer 2 result should preserve returned items and pagination context while adding safe operation context such as `endpoint`, `quotaCost`, requested parts, selector, and text-format context.

**Alternatives considered**: Returning only comments was rejected because callers need pagination and operation context. Enriching comments with thread, video, channel, sentiment, moderation, or ranking data was rejected because it would no longer be a low-level endpoint-backed tool.

## Decision: Reuse shared Layer 2 safe error categories and sanitize credentials or diagnostics

**Rationale**: YT-201 requires consistent public error conventions. Official errors include unsupported operation, insufficient permissions, and not-found comments; these map to shared categories such as `invalid_request`, `authorization_failed`, `resource_not_found`, `quota_exhausted`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`.

**Alternatives considered**: Exposing raw Google error details was rejected because project safety rules prohibit leaking credentials, stack traces, or unsafe diagnostics.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**: Implementing first and adding tests afterward was rejected by the constitution. Running only focused tests was rejected because full-suite validation is required before completion.

## Official References Checked

- YouTube Data API `comments.list`: https://developers.google.com/youtube/v3/docs/comments/list
- YouTube Data API quota cost table: https://developers.google.com/youtube/v3/determine_quota_cost
