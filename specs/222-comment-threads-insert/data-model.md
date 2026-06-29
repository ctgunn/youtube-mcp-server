# Data Model: Layer 2 Tool `commentThreads_insert`

## Comment Threads Insert Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `commentThreads.insert` top-level comment creation operation.

**Fields**:

- `name`: fixed value `commentThreads_insert`.
- `upstream.resource`: fixed value `commentThreads`.
- `upstream.method`: fixed value `insert`.
- `upstream.operationKey`: fixed value `commentThreads.insert`.
- `quotaCost`: fixed value `50`.
- `authMode`: fixed value `oauth_required`.
- `availabilityState`: active unless official documentation or project inventory says otherwise.
- `inputSchema`: public request schema for one top-level comment-thread creation request.
- `responseBoundary`: near-raw mutation result boundary.
- `usageNotes`: quota, OAuth, part, top-level body, channel/video target context, delegation, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Comment Thread Create Request` as input.
- Produces `Created Comment Thread Result` on success.
- Depends on the Layer 1 `commentThreads.insert` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 50 and OAuth-required auth in metadata, description, usage notes, and examples.
- Must not claim to list threads, create replies through `comments.insert`, update comments, delete comments, perform moderation actions, or perform higher-level analysis.

## Comment Thread Create Request

**Purpose**: Caller-provided request shape for one top-level comment-thread creation attempt.

**Fields**:

- `part`: required non-empty response part selection. The primary supported creation path uses `snippet`; `id` and `replies` may be accepted only where the shared contract and upstream endpoint support requesting those returned parts.
- `body`: required comment-thread resource body.
- `body.snippet`: required snippet object.
- `body.snippet.channelId`: required non-empty target channel identifier for the comment thread resource.
- `body.snippet.videoId`: required non-empty target video identifier where the top-level comment appears.
- `body.snippet.topLevelComment`: required top-level comment resource.
- `body.snippet.topLevelComment.snippet`: required top-level comment snippet object.
- `body.snippet.topLevelComment.snippet.textOriginal`: required non-empty top-level comment text to publish.
- `onBehalfOfContentOwner`: optional delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

**Relationships**:

- Contains `Top-Level Comment Body`.
- References `Target Channel Context` and `Target Video Context`.
- Requires `Write Authorization Context`.

**Validation Rules**:

- Reject missing or empty `part`.
- Reject missing `body`, missing `body.snippet`, missing or empty `body.snippet.channelId`, missing or empty `body.snippet.videoId`, missing `body.snippet.topLevelComment`, missing nested top-level comment snippet, and missing or empty `body.snippet.topLevelComment.snippet.textOriginal`.
- Reject unsupported request fields, read-only fields, reply-style fields such as `parentId`, listing filters, update fields, moderation fields, deletion fields, search instructions, and automated response instructions.
- Reject or map malformed target IDs, too-long comment text, invalid custom emoji, unavailable channel or video targets, disabled comments, and invalid metadata to safe caller-facing categories.

## Top-Level Comment Body

**Purpose**: The comment-thread resource content to publish as a new top-level comment.

**Fields**:

- `snippet.channelId`: channel associated with the top-level comment thread.
- `snippet.videoId`: video that receives the top-level comment.
- `snippet.topLevelComment.snippet.textOriginal`: comment text to publish.

**Relationships**:

- Belongs to `Comment Thread Create Request`.
- Identifies `Target Channel Context` and `Target Video Context`.

**Validation Rules**:

- Channel ID, video ID, and top-level comment text are all required.
- Top-level comment text must be publishable and non-empty after validation.
- The body must not include fields that imply reply creation, thread listing, comment update, moderation, deletion, or enrichment behavior.

## Target Channel Context

**Purpose**: Channel identifier required by the upstream comment-thread resource body.

**Fields**:

- `channelId`: non-empty channel identifier supplied as `body.snippet.channelId`.
- `accessState`: effective caller-facing state after validation or upstream response, such as available, missing, inaccessible, or not eligible for the caller's authorization.

**Relationships**:

- Referenced by `Top-Level Comment Body`.
- Combined with `Target Video Context` to define where the top-level comment thread is created.

**Validation Rules**:

- Missing or empty channel IDs fail local validation.
- Missing, private, inaccessible, or ineligible channels must be surfaced distinctly from successful creation.

## Target Video Context

**Purpose**: Video identifier where the top-level comment thread will be created.

**Fields**:

- `videoId`: non-empty video identifier supplied as `body.snippet.videoId`.
- `accessState`: effective caller-facing state after validation or upstream response, such as available, missing, private, inaccessible, comments disabled, or not accepting top-level comments.

**Relationships**:

- Referenced by `Top-Level Comment Body`.
- Determines whether `commentThreads_insert` can create the top-level thread.

**Validation Rules**:

- Missing or empty video IDs fail local validation.
- Missing, private, inaccessible, comments-disabled, restricted, or non-commentable videos must be surfaced distinctly from successful creation.

## Write Authorization Context

**Purpose**: OAuth-backed caller authorization used for the write operation.

**Fields**:

- `mode`: fixed value `oauth_required`.
- `eligible`: whether the caller has sufficient authorization for the channel/video target context.
- `delegatedContext`: safe presence indicator for delegated owner context when supplied.

**Relationships**:

- Required by every `Comment Thread Create Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing OAuth credentials map to `authentication_failed`.
- Present but insufficient OAuth authorization maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, or raw credential diagnostics.

## Created Comment Thread Result

**Purpose**: Successful result for one created top-level comment thread.

**Fields**:

- `endpoint`: fixed value `commentThreads.insert`.
- `quotaCost`: fixed value `50`.
- `created`: true for successful creation.
- `requestedParts`: normalized part selection.
- `item`: created comment-thread resource returned by Layer 1 or upstream.
- `auth`: safe OAuth-required context summary.
- `target`: safe channel/video target context.
- `delegation`: safe delegated context summary when supplied.
- `kind`, `etag`, `id`, `snippet`, `replies`: preserved upstream comment-thread fields when present.

**Relationships**:

- Produced by `Comment Threads Insert Tool`.
- Contains or wraps the upstream returned comment-thread resource.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing comment-thread data.
- Do not include unrelated thread listing, reply insertion, comment editing, moderation, deletion, sentiment, ranking, summary, enrichment, analytics, or generated response data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part/body/channel/video/top-level comment text or unsupported shape)
  -> Awaiting OAuth Validation
  -> Authentication Failed (missing OAuth)
  -> Authorization Failed (insufficient OAuth or inaccessible target context)
  -> Upstream Create Attempted
  -> Created Comment Thread Result
  -> Upstream Failure (quota, missing channel, missing video, disabled comments, invalid metadata, unavailable endpoint, unexpected failure)
```
