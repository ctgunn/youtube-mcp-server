# Data Model: Layer 2 Tool `comments_setModerationStatus`

## Comments Moderation Status Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `comments.setModerationStatus` moderation operation.

**Fields**:

- `name`: fixed value `comments_setModerationStatus`.
- `upstream.resource`: fixed value `comments`.
- `upstream.method`: fixed value `setModerationStatus`.
- `upstream.operationKey`: fixed value `comments.setModerationStatus`.
- `quotaCost`: fixed value `50`.
- `authMode`: fixed value `oauth_required`.
- `availabilityState`: active unless official documentation or project inventory says otherwise.
- `inputSchema`: public request schema for one moderation status request.
- `responseBoundary`: near-raw mutation acknowledgment boundary.
- `usageNotes`: quota, OAuth, target IDs, moderation status, optional flag, delegation, no-body, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Comment Moderation Request` as input.
- Produces `Moderation Mutation Result` on success.
- Depends on the Layer 1 `comments.setModerationStatus` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 50 and OAuth-required auth in metadata, description, usage notes, and examples.
- Must not claim to list comments, create replies, edit comment text, delete comments, recommend moderation decisions, or perform higher-level comment workflows.

## Comment Moderation Request

**Purpose**: Caller-provided request shape for one moderation attempt.

**Fields**:

- `id`: required non-empty comment identifier or list of comment identifiers.
- `moderationStatus`: required moderation outcome. Supported values are `heldForReview`, `published`, and `rejected`.
- `banAuthor`: optional boolean flag accepted only when `moderationStatus` is `rejected`.
- `onBehalfOfContentOwner`: optional delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

**Relationships**:

- Contains `Target Comment Identifiers`.
- Contains `Moderation Status`.
- May contain `Optional Moderation Flag`.
- Requires `Write Authorization Context`.

**Validation Rules**:

- Reject missing, empty, malformed, or duplicate `id` values.
- Reject missing, empty, or unsupported `moderationStatus` values.
- Reject `banAuthor` values that are not boolean.
- Reject `banAuthor` when `moderationStatus` is not `rejected`.
- Reject request bodies, listing fields, insertion fields, update-body fields, deletion instructions, search instructions, ranking instructions, summarization instructions, sentiment instructions, enrichment instructions, automated moderation advice, and unsupported optional parameters.
- Reject or map malformed target IDs, unavailable comments, limited moderation functionality, and insufficient permissions to safe caller-facing categories.

## Target Comment Identifiers

**Purpose**: Identifiers of the existing comments whose moderation status will change.

**Fields**:

- `ids`: one or more non-empty comment identifiers supplied through `id`.
- `accessState`: effective caller-facing state after validation or upstream response, such as moderation eligible, missing, private, inaccessible, ineligible, or unsupported.

**Relationships**:

- Referenced by `Comment Moderation Request`.
- Determines whether `comments_setModerationStatus` can moderate the selected comments.

**Validation Rules**:

- Missing or empty target comment IDs fail local validation.
- Duplicate target comment IDs fail local validation.
- Missing, private, inaccessible, ineligible, or unsupported target comments must be surfaced distinctly from successful moderation.

## Moderation Status

**Purpose**: The requested moderation outcome to apply to the target comments.

**Fields**:

- `value`: one of `heldForReview`, `published`, or `rejected`.
- `effect`: caller-facing meaning of the selected outcome.

**Relationships**:

- Belongs to `Comment Moderation Request`.
- Is governed by `Moderation Transition Policy`.

**Validation Rules**:

- Moderation status is required.
- Unsupported status values fail local validation.
- Accepted statuses must be visible in metadata, usage notes, caveats, and examples.

## Moderation Transition Policy

**Purpose**: Caller-facing rules that distinguish supported moderation outcomes and optional flag combinations from unsupported moderation transitions or request shapes.

**Fields**:

- `supportedStatuses`: fixed values `heldForReview`, `published`, and `rejected`.
- `compatibleOptionalFlags`: `banAuthor` is compatible only with `rejected`.
- `noBodyRule`: no request body is supported for this operation.
- `unsupportedOperationBoundary`: listing, insertion, update, deletion, recommendation, ranking, summarization, sentiment, enrichment, and cross-endpoint behaviors are outside scope.

**Relationships**:

- Applies to every `Comment Moderation Request`.
- Shapes public validation and usage examples.

**Validation Rules**:

- Reject unsupported status values.
- Reject incompatible optional flags.
- Reject body-bearing or unrelated workflow requests.

## Optional Moderation Flag

**Purpose**: Additional moderation instruction that can accompany a compatible moderation request.

**Fields**:

- `banAuthor`: optional boolean indicating whether future comments from the target comment author should be rejected.

**Relationships**:

- Belongs to `Comment Moderation Request`.
- Depends on `Moderation Status`.

**Validation Rules**:

- `banAuthor` must be boolean when supplied.
- `banAuthor` is accepted only when `moderationStatus` is `rejected`.
- Public surfaces must explain the compatibility rule before invocation.

## Write Authorization Context

**Purpose**: OAuth-backed caller authorization used for the write operation.

**Fields**:

- `mode`: fixed value `oauth_required`.
- `eligible`: whether the caller has sufficient authorization for the target comment context.
- `delegatedContext`: safe presence indicator for delegated owner context when supplied.

**Relationships**:

- Required by every `Comment Moderation Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing OAuth credentials map to `authentication_failed`.
- Present but insufficient OAuth authorization maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, raw credential diagnostics, or sensitive owner credential details.

## Moderation Mutation Result

**Purpose**: Successful acknowledgment for one moderation request.

**Fields**:

- `endpoint`: fixed value `comments.setModerationStatus`.
- `quotaCost`: fixed value `50`.
- `moderated`: true for successful moderation mutation.
- `targetIds`: normalized target comment identifiers.
- `moderationStatus`: requested supported moderation status.
- `banAuthor`: safe optional flag context when supplied.
- `auth`: safe OAuth-required context summary.
- `delegation`: safe delegated context summary when supplied.
- `statusCode`: successful no-content acknowledgment, represented without fabricating comment resource data.

**Relationships**:

- Produced by `Comments Moderation Status Tool`.
- Represents a successful upstream 204/no-content mutation response.

**Validation Rules**:

- Preserve requested target, status, optional flag, and operation context without fabricating missing comment data.
- Do not include unrelated parent thread, channel, video, edit, deletion, sentiment, ranking, summary, enrichment, or recommendation data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing/duplicate target IDs, missing/unsupported status, invalid optional flag, body or unsupported shape)
  -> Awaiting OAuth Validation
  -> Authentication Failed (missing OAuth)
  -> Authorization Failed (insufficient OAuth or inaccessible target)
  -> Upstream Moderation Attempted
  -> Moderation Mutation Result (204/no-content acknowledgment)
  -> Upstream Failure (quota, missing target, limited moderation functionality, unavailable endpoint, unexpected failure)
```
