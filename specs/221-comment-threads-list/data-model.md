# Data Model: Layer 2 Tool `commentThreads_list`

## Comment Threads List Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `commentThreads.list` retrieval operation.

**Fields**:

- `name`: fixed value `commentThreads_list`.
- `upstream.resource`: fixed value `commentThreads`.
- `upstream.method`: fixed value `list`.
- `upstream.operationKey`: fixed value `commentThreads.list`.
- `quotaCost`: fixed value `1`.
- `authMode`: API-key public retrieval with documented access-sensitive caveats for moderation-status usage and inaccessible resources.
- `availabilityState`: active unless official documentation or project inventory says otherwise.
- `inputSchema`: public request schema for one list request.
- `responseBoundary`: near-raw list result boundary.
- `usageNotes`: quota, auth, part, selector, pagination, ordering, search, moderation-status, text-format, no-body, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Comment Threads List Request` as input.
- Produces `Comment Threads List Result` on success.
- Depends on the Layer 1 `commentThreads.list` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 1 and auth/access expectations in metadata, description, usage notes, and examples.
- Must not claim to list replies through `comments.list`, create threads, mutate comments, perform moderation actions, recover content, recommend moderation decisions, or perform higher-level analysis.

## Comment Threads List Request

**Purpose**: Caller-provided request shape for one comment-thread retrieval attempt.

**Fields**:

- `part`: required non-empty comma-separated comment-thread resource parts.
- `videoId`: optional selector for retrieving threads associated with one video.
- `allThreadsRelatedToChannelId`: optional selector for retrieving threads associated with one channel.
- `id`: optional selector for direct retrieval of one or more comment-thread identifiers.
- `maxResults`: optional page size for supported non-`id` selectors; valid range 1 through 100.
- `moderationStatus`: optional access-sensitive moderation filter for supported non-`id` selectors; allowed values are `heldForReview`, `likelySpam`, and `published`.
- `order`: optional result ordering for supported non-`id` selectors; allowed values are `time` and `relevance`.
- `pageToken`: optional token for retrieving a result page for supported non-`id` selectors.
- `searchTerms`: optional text search terms for supported non-`id` selectors.
- `textFormat`: optional comment text representation; allowed values are `html` and `plainText`.

**Relationships**:

- Contains exactly one `Thread Retrieval Selector`.
- May include `Pagination Context` and `Supported Option Context` when valid for the selected selector.
- Requires `API-Key Auth Context` for the existing Layer 1 execution path.

**Validation Rules**:

- Reject missing, empty, unsupported, or conflicting `part`.
- Reject requests without exactly one selector from `videoId`, `allThreadsRelatedToChannelId`, or `id`.
- Reject `maxResults`, `moderationStatus`, `order`, `pageToken`, and `searchTerms` with the `id` selector.
- Reject unsupported request bodies, reply-listing fields, mutation fields, moderation-action fields, ranking instructions, summarization instructions, sentiment instructions, enrichment instructions, automated moderation advice, and unsupported optional parameters.

## Thread Retrieval Selector

**Purpose**: The single primary filter that determines how comment threads are retrieved.

**Fields**:

- `name`: one of `videoId`, `allThreadsRelatedToChannelId`, or `id`.
- `value`: non-empty selector value supplied by the caller.
- `accessState`: effective caller-facing state after validation or upstream response, such as retrievable, no matches, missing, comments disabled, inaccessible, or unsupported.

**Relationships**:

- Referenced by `Comment Threads List Request`.
- Determines which optional parameters are valid.
- Shapes the `selector` context in the result.

**Validation Rules**:

- Missing selector fails local validation.
- Multiple selectors fail local validation.
- Empty, malformed, duplicate, excessive, or unsupported selector values fail local validation or map to a safe upstream category.
- Missing videos, missing channels, missing thread identifiers, disabled comments, private or inaccessible resources, and unsupported ID behavior must be distinguishable from successful empty collections.

## Pagination Context

**Purpose**: Caller-provided and returned page information for supported comment-thread result traversal.

**Fields**:

- `maxResults`: requested maximum number of items for supported selectors.
- `pageToken`: requested page token for supported selectors.
- `nextPageToken`: returned token for the next page when present.
- `pageInfo`: returned page summary when present.

**Relationships**:

- Optional part of `Comment Threads List Request`.
- Preserved in `Comment Threads List Result`.

**Validation Rules**:

- `maxResults` must be within official limits.
- `pageToken` must be non-empty when supplied.
- Pagination fields are invalid with the `id` selector.

## Supported Option Context

**Purpose**: Endpoint-native options that shape valid list retrieval while preserving Layer 2 scope.

**Fields**:

- `moderationStatus`: requested moderation filter when valid and properly authorized.
- `order`: requested result order.
- `searchTerms`: requested search term filter.
- `textFormat`: requested text representation, defaulting to upstream `html` behavior when omitted.

**Relationships**:

- Optional part of `Comment Threads List Request`.
- Preserved in `Comment Threads List Result`.
- Constrained by `Thread Retrieval Selector` and `API-Key Auth Context`.

**Validation Rules**:

- `moderationStatus` must be one of `heldForReview`, `likelySpam`, or `published` and must disclose access-sensitive behavior.
- `order` must be one of `time` or `relevance`.
- `textFormat` must be one of `html` or `plainText`.
- `moderationStatus`, `order`, and `searchTerms` are invalid with the `id` selector.

## API-Key Auth Context

**Purpose**: Safe caller authorization context used for public comment-thread retrieval through the existing Layer 1 wrapper.

**Fields**:

- `mode`: fixed value `api_key` for supported public selectors in this slice.
- `eligible`: whether the caller has enough access for the selected retrieval context.
- `accessCaveat`: safe note for moderation-status or inaccessible-resource outcomes when relevant.

**Relationships**:

- Required by every `Comment Threads List Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing API-key access maps to an authentication-style failure.
- Ineligible access for moderation-status or private resources maps to an authorization-style failure.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, raw credential diagnostics, or sensitive owner credential details.

## Comment Threads List Result

**Purpose**: Successful comment-thread collection response for one list request.

**Fields**:

- `endpoint`: fixed value `commentThreads.list`.
- `quotaCost`: fixed value `1`.
- `requestedParts`: normalized requested part list.
- `selector`: selected retrieval mode and safe selector context.
- `textFormat`: effective text format.
- `options`: safe ordering, search, moderation-status, and pagination option context when supplied.
- `items`: returned comment-thread resources.
- `kind`: preserved upstream response kind when present.
- `etag`: preserved upstream response etag when present.
- `nextPageToken`: preserved upstream next-page token when present.
- `pageInfo`: preserved upstream page information when present.

**Relationships**:

- Produced by `Comment Threads List Tool`.
- Preserves allowed fields from the upstream comment-thread list response.

**Validation Rules**:

- Preserve requested selector, parts, options, page context, and returned thread resources without fabricating missing data.
- Empty `items` is a successful empty collection when upstream returns success.
- Do not include unrelated replies-only data, mutation data, moderation-action results, sentiment, ranking, summaries, enrichment, or cross-endpoint aggregation.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part, missing selector, conflicting selectors, unsupported id modifiers, body or unsupported shape)
  -> Awaiting API-Key Validation
  -> Authentication Failed (missing API-key access)
  -> Authorization Failed (ineligible moderation-status or inaccessible resource)
  -> Upstream Retrieval Attempted
  -> Comment Threads List Result (populated or empty success)
  -> Upstream Failure (quota, disabled comments, missing channel/video/thread, unavailable endpoint, unexpected failure)
```
