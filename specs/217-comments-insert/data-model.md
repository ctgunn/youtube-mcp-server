# Data Model: Layer 2 Tool `comments_insert`

## Comments Insert Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `comments.insert` reply creation operation.

**Fields**:

- `name`: fixed value `comments_insert`.
- `upstream.resource`: fixed value `comments`.
- `upstream.method`: fixed value `insert`.
- `upstream.operationKey`: fixed value `comments.insert`.
- `quotaCost`: fixed value `50`.
- `authMode`: fixed value `oauth_required`.
- `availabilityState`: active unless official documentation or project inventory says otherwise.
- `inputSchema`: public request schema for one reply creation request.
- `responseBoundary`: near-raw mutation result boundary.
- `usageNotes`: quota, OAuth, part, reply-body, parent-comment, delegation, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Comment Reply Create Request` as input.
- Produces `Created Comment Result` on success.
- Depends on the Layer 1 `comments.insert` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 50 and OAuth-required auth in metadata, description, usage notes, and examples.
- Must not claim to create top-level comment threads or perform higher-level comment workflows.

## Comment Reply Create Request

**Purpose**: Caller-provided request shape for one reply creation attempt.

**Fields**:

- `part`: required non-empty response part selection. Supported values must follow the upstream endpoint and local contract, with `snippet` as the primary required reply creation path and `id` allowed when supported for the response.
- `body`: required comment resource body.
- `body.snippet`: required snippet object.
- `body.snippet.parentId`: required non-empty parent comment identifier.
- `body.snippet.textOriginal`: required non-empty reply text.
- `onBehalfOfContentOwner`: optional delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

**Relationships**:

- Contains `Reply Body`.
- References `Parent Comment Reference`.
- Requires `Write Authorization Context`.

**Validation Rules**:

- Reject missing or empty `part`.
- Reject missing `body`, missing `body.snippet`, missing or empty `body.snippet.parentId`, and missing or empty `body.snippet.textOriginal`.
- Reject unsupported request fields, read-only fields, top-level thread creation fields, update fields, moderation fields, deletion fields, search instructions, and automated response instructions.
- Reject or map malformed parent IDs, too-long reply text, invalid custom emoji, private parent comments, unavailable parent comments, and disabled reply behavior to safe caller-facing categories.

## Reply Body

**Purpose**: The comment resource content to publish as a reply.

**Fields**:

- `snippet.parentId`: parent comment being answered.
- `snippet.textOriginal`: reply text to publish.

**Relationships**:

- Belongs to `Comment Reply Create Request`.
- Identifies `Parent Comment Reference`.

**Validation Rules**:

- Parent ID and reply text are both required.
- Reply text must be publishable and non-empty after validation.
- The body must not include fields that imply top-level comment-thread creation, comment update, moderation, deletion, or enrichment behavior.

## Parent Comment Reference

**Purpose**: Identifier of the existing parent comment that receives the reply.

**Fields**:

- `id`: non-empty parent comment identifier supplied as `body.snippet.parentId`.
- `accessState`: effective caller-facing state after validation or upstream response, such as available, missing, private, inaccessible, or not accepting replies.

**Relationships**:

- Referenced by `Reply Body`.
- Determines whether `comments_insert` can create a reply.

**Validation Rules**:

- Missing or empty parent IDs fail local validation.
- Missing, private, inaccessible, or non-replyable parent comments must be surfaced distinctly from successful creation.

## Write Authorization Context

**Purpose**: OAuth-backed caller authorization used for the write operation.

**Fields**:

- `mode`: fixed value `oauth_required`.
- `eligible`: whether the caller has sufficient authorization for the target parent-comment context.
- `delegatedContext`: safe presence indicator for delegated owner context when supplied.

**Relationships**:

- Required by every `Comment Reply Create Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing OAuth credentials map to `authentication_failed`.
- Present but insufficient OAuth authorization maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, or raw credential diagnostics.

## Created Comment Result

**Purpose**: Successful result for one created reply comment.

**Fields**:

- `endpoint`: fixed value `comments.insert`.
- `quotaCost`: fixed value `50`.
- `created`: true for successful creation.
- `requestedParts`: normalized part selection.
- `item`: created comment resource returned by Layer 1 or upstream.
- `auth`: safe OAuth-required context summary.
- `delegation`: safe delegated context summary when supplied.
- `kind`, `etag`, `id`, `snippet`: preserved upstream comment fields when present.

**Relationships**:

- Produced by `Comments Insert Tool`.
- Contains or wraps the upstream returned comment resource.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing comment data.
- Do not include unrelated parent thread, channel, video, moderation, sentiment, ranking, summary, enrichment, or generated response data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part/body/parent/text or unsupported shape)
  -> Awaiting OAuth Validation
  -> Authentication Failed (missing OAuth)
  -> Authorization Failed (insufficient OAuth or inaccessible context)
  -> Upstream Create Attempted
  -> Created Comment Result
  -> Upstream Failure (quota, missing parent, private parent, disabled replies, unavailable endpoint, unexpected failure)
```
