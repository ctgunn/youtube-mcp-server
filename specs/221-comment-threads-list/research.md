# Research: Layer 2 Tool `commentThreads_list`

## Decision: Implement `commentThreads_list` as an endpoint-backed Layer 2 tool in a `comment_threads` resource-family module

**Rationale**: The PRD defines Layer 2 tools as one-to-one public MCP tools for documented YouTube Data API methods. YT-221 requires the public tool name `commentThreads_list`, and the existing Layer 1 dependency is already organized under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`. A new `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py` module keeps this slice aligned to the upstream resource family and leaves room for the neighboring `commentThreads_insert` Layer 2 tool.

**Alternatives considered**:

- Add the tool to `comments.py`: rejected because `comments_*` tools map to the `comments` resource, while this feature maps to `commentThreads`.
- Add code to generic shared contracts or examples modules: rejected because endpoint-specific selectors, examples, and result mapping belong in a concrete resource family.
- Build a higher-level discussion or moderation workflow: rejected because YT-221 is explicitly low-level and endpoint-backed.

## Decision: Use public tool name `commentThreads_list`

**Rationale**: YT-202 requires `resource_method` naming without a redundant `youtube_` prefix while preserving official resource and method identity. The seed and PRD list the public Layer 2 mapping as `commentThreads_list`.

**Alternatives considered**:

- `comment_threads_list`: rejected because it changes the official resource casing used by the seed and existing endpoint naming examples.
- `commentThreads.list`: rejected because Layer 2 public tools use underscore-separated resource-method names.
- `youtube_commentThreads_list`: rejected because Layer 2 naming omits the redundant `youtube_` prefix.

## Decision: Require `part` plus exactly one selector: `videoId`, `allThreadsRelatedToChannelId`, or `id`

**Rationale**: The official `commentThreads.list` reference requires `part` and says callers must specify exactly one filter from `videoId`, `allThreadsRelatedToChannelId`, or `id`. The existing YT-121 Layer 1 wrapper already centers on the same three selectors.

**Alternatives considered**:

- Allow missing selectors: rejected because the upstream endpoint requires one filter.
- Allow multiple selectors: rejected because the official filter contract requires exactly one.
- Add `parentId`: rejected because parent-comment reply retrieval belongs to `comments.list`, not `commentThreads.list`.

## Decision: Record quota cost as 1 everywhere the caller sees the tool

**Rationale**: The official YouTube Data API `commentThreads.list` reference states that the method costs 1 quota unit. YT-202 and the feature spec require quota cost visibility in metadata, description, usage notes, and examples.

**Alternatives considered**:

- Hide quota in implementation-only metadata: rejected because client developers need pre-invocation cost visibility.
- Treat examples for invalid requests as quota-free: rejected because official quota guidance is endpoint-level; local validation should avoid unnecessary upstream calls while public docs still show the official cost.

## Decision: Use API-key auth for public selector retrieval and document access-sensitive moderation behavior

**Rationale**: The existing Layer 1 `build_comment_threads_list_wrapper()` marks the endpoint as API-key auth for `videoId`, `allThreadsRelatedToChannelId`, and `id` selectors. Official documentation states `moderationStatus` can only be used in a properly authorized request, so the Layer 2 public contract must document that access-sensitive filter and reject or safely categorize ineligible usage.

**Alternatives considered**:

- Declare the tool OAuth-only: rejected because the local Layer 1 wrapper and common public retrieval path use API-key auth.
- Declare the tool purely unrestricted API-key access: rejected because moderation-status filtering and some inaccessible resources can fail with authorization-related outcomes.
- Add a new OAuth execution path in this slice: rejected because Layer 2 should reuse YT-121 behavior and avoid expanding auth semantics beyond the existing wrapper without a separate dependency change.

## Decision: Support endpoint-native optional parameters only where upstream allows them

**Rationale**: Official docs allow `maxResults` from 1 to 100, `moderationStatus` values `heldForReview`, `likelySpam`, and `published`, `order` values `time` and `relevance`, `pageToken`, `searchTerms`, and `textFormat` values `html` and `plainText`. Official docs also say `maxResults`, `moderationStatus`, `order`, `pageToken`, and `searchTerms` are not supported with `id`.

**Alternatives considered**:

- Always allow optional parameters with every selector: rejected because the `id` selector has documented restrictions.
- Reject all optional modifiers: rejected because video and channel-related retrieval support endpoint-native pagination, ordering, search-term, moderation-status, and text-format behavior.
- Add custom formats, sorting modes, text normalization, or search semantics: rejected because those are higher-level transformations outside Layer 2 scope.

## Decision: Map success to a near-raw comment-thread list result

**Rationale**: Official success returns a `youtube#commentThreadListResponse` with `kind`, `etag`, optional `nextPageToken`, `pageInfo`, and `items[]` containing comment-thread resources. The Layer 2 result should preserve returned items and pagination context while adding safe operation context such as `endpoint`, `quotaCost`, requested parts, selector, option context, and text-format context.

**Alternatives considered**:

- Return only top-level comments: rejected because the endpoint returns comment-thread resources.
- Enrich threads with reply listing, channel, video, sentiment, moderation, or ranking data: rejected because that would cross endpoint boundaries and violate Layer 2 scope.
- Collapse empty upstream results into not-found errors: rejected because empty successful collections must remain distinguishable from missing channel/video/thread errors.

## Decision: Reuse shared Layer 2 safe error categories and sanitize credentials or diagnostics

**Rationale**: YT-201 requires consistent public error conventions. Official errors include `operationNotSupported`, `processingFailure`, `commentsDisabled`, `forbidden`, `channelNotFound`, `commentThreadNotFound`, and `videoNotFound`; these map to shared categories such as `invalid_request`, `authorization_failed`, `resource_not_found`, `quota_exhausted`, `endpoint_unavailable`, `deprecated_endpoint`, and `upstream_failure`, with provider-specific reasons like `commentsDisabled` preserved only as safe details.

**Alternatives considered**:

- Expose raw Google error payloads: rejected because public MCP clients need stable categories and safe diagnostics.
- Collapse every upstream failure into `upstream_failure`: rejected because callers need to distinguish invalid requests, authorization, disabled comments, and missing resources.
- Add a new custom error taxonomy for comment threads: rejected because YT-201 requires shared conventions across Layer 2 tools.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**:

- Implement first and add tests afterward: rejected by the constitution.
- Run only focused tests: rejected because full-suite validation is required before completion.
- Omit docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, existing YT-121 wrapper, existing Layer 2 list tools, and official documentation resolve the endpoint identity, quota, auth mode, required field, selector set, optional parameters, response shape, dependencies, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-221 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/spec.md`
- Local Layer 1 wrapper planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/spec.md`
- Local Layer 2 comments list planning: `/Users/ctgunn/Projects/youtube-mcp-server/specs/216-comments-list/research.md`
- Existing Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`
- Official YouTube Data API `commentThreads.list`: https://developers.google.com/youtube/v3/docs/commentThreads/list
