# Data Model: Layer 2 Tool `comments_update`

## Comments Update Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `comments.update` edit operation.

**Fields**:

- `name`: fixed value `comments_update`.
- `upstream.resource`: fixed value `comments`.
- `upstream.method`: fixed value `update`.
- `upstream.operationKey`: fixed value `comments.update`.
- `quotaCost`: fixed value `50`.
- `authMode`: fixed value `oauth_required`.
- `availabilityState`: active unless official documentation or project inventory says otherwise.
- `inputSchema`: public request schema for one comment update request.
- `responseBoundary`: near-raw mutation result boundary.
- `usageNotes`: quota, OAuth, part, target comment, writable text, delegation, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Comment Update Request` as input.
- Produces `Updated Comment Result` on success.
- Depends on the Layer 1 `comments.update` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 50 and OAuth-required auth in metadata, description, usage notes, and examples.
- Must not claim to list comments, create replies, moderate comments, delete comments, rewrite content, or perform higher-level comment workflows.

## Comment Update Request

**Purpose**: Caller-provided request shape for one comment edit attempt.

**Fields**:

- `part`: required non-empty response part selection. Supported values must follow the upstream endpoint and local contract, with `snippet` required because it contains updateable properties and `id` allowed when supported for the response.
- `body`: required comment resource body.
- `body.id`: required non-empty target comment identifier.
- `body.snippet`: required snippet object.
- `body.snippet.textOriginal`: required non-empty revised comment text.
- `onBehalfOfContentOwner`: optional delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

**Relationships**:

- Contains `Updated Comment Text`.
- References `Target Comment Identifier`.
- Requires `Write Authorization Context`.

**Validation Rules**:

- Reject missing or empty `part`.
- Reject `part` values that omit `snippet` or request unsupported writable parts.
- Reject missing `body`, missing or empty `body.id`, missing `body.snippet`, and missing or empty `body.snippet.textOriginal`.
- Reject unsupported request fields, read-only fields, immutable parent relationships, insert-only fields, moderation fields, deletion fields, listing/search instructions, generated rewrite instructions, and enrichment instructions.
- Reject or map malformed target IDs, too-long updated text, invalid metadata, ineligible accounts, unavailable comments, and insufficient permissions to safe caller-facing categories.

## Target Comment Identifier

**Purpose**: Identifier of the existing comment to edit.

**Fields**:

- `id`: non-empty comment identifier supplied as `body.id`.
- `accessState`: effective caller-facing state after validation or upstream response, such as editable, missing, private, inaccessible, ineligible, or not editable.

**Relationships**:

- Referenced by `Comment Update Request`.
- Determines whether `comments_update` can modify the target comment.

**Validation Rules**:

- Missing or empty target comment IDs fail local validation.
- Missing, private, inaccessible, ineligible, or non-editable target comments must be surfaced distinctly from successful updates.

## Updated Comment Text

**Purpose**: The revised comment content to apply to the target comment.

**Fields**:

- `snippet.textOriginal`: revised original comment text.

**Relationships**:

- Belongs to `Comment Update Request`.
- Is governed by `Writable Field Policy`.

**Validation Rules**:

- Updated text is required.
- Updated text must be non-empty after validation and publishable by upstream rules.
- The body must not include fields that imply parent changes, moderation changes, deletion, insertion, search, analytics, or enrichment behavior.

## Writable Field Policy

**Purpose**: Caller-facing rules that distinguish fields that may be changed from read-only fields and unrelated operations.

**Fields**:

- `supportedWritablePart`: fixed value `snippet` for this slice.
- `supportedWritableBodyField`: fixed value `body.snippet.textOriginal`.
- `requiredIdentityField`: fixed value `body.id`.
- `readOnlyFieldBoundary`: any other comment metadata or relationship fields are not writable through this tool.

**Relationships**:

- Applies to every `Comment Update Request`.
- Shapes public validation and usage examples.

**Validation Rules**:

- Reject unsupported writable parts.
- Reject read-only fields such as author, channel, parent relationship, ratings, counts, published time, updated time, moderation state, and derived display fields when supplied as update targets.
- Reject patch-style or generated-rewrite instructions because this tool accepts endpoint-backed update bodies only.

## Write Authorization Context

**Purpose**: OAuth-backed caller authorization used for the write operation.

**Fields**:

- `mode`: fixed value `oauth_required`.
- `eligible`: whether the caller has sufficient authorization for the target comment context.
- `delegatedContext`: safe presence indicator for delegated owner context when supplied.

**Relationships**:

- Required by every `Comment Update Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing OAuth credentials map to `authentication_failed`.
- Present but insufficient OAuth authorization maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, or raw credential diagnostics.

## Updated Comment Result

**Purpose**: Successful result for one updated comment.

**Fields**:

- `endpoint`: fixed value `comments.update`.
- `quotaCost`: fixed value `50`.
- `updated`: true for successful update.
- `requestedParts`: normalized part selection.
- `writableFields`: safe summary of the writable field applied.
- `item`: updated comment resource returned by Layer 1 or upstream.
- `auth`: safe OAuth-required context summary.
- `delegation`: safe delegated context summary when supplied.
- `kind`, `etag`, `id`, `snippet`: preserved upstream comment fields when present.

**Relationships**:

- Produced by `Comments Update Tool`.
- Contains or wraps the upstream returned comment resource.

**Validation Rules**:

- Preserve returned upstream fields without fabricating missing comment data.
- Do not include unrelated parent thread, channel, video, moderation, deletion, sentiment, ranking, summary, enrichment, or generated rewrite data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing part/body/id/text or unsupported shape)
  -> Awaiting OAuth Validation
  -> Authentication Failed (missing OAuth)
  -> Authorization Failed (insufficient OAuth or inaccessible target)
  -> Upstream Update Attempted
  -> Updated Comment Result
  -> Upstream Failure (quota, missing target, ineligible account, unavailable endpoint, unexpected failure)
```
