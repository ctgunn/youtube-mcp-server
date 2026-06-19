# Data Model: Layer 2 Tool `comments_delete`

## Comments Delete Tool

**Purpose**: Public Layer 2 MCP tool that exposes one endpoint-backed YouTube `comments.delete` deletion operation.

**Fields**:

- `name`: fixed value `comments_delete`.
- `upstream.resource`: fixed value `comments`.
- `upstream.method`: fixed value `delete`.
- `upstream.operationKey`: fixed value `comments.delete`.
- `quotaCost`: fixed value `50`.
- `authMode`: fixed value `oauth_required`.
- `availabilityState`: active unless official documentation or project inventory says otherwise.
- `inputSchema`: public request schema for one deletion request.
- `responseBoundary`: near-raw destructive mutation acknowledgment boundary.
- `usageNotes`: quota, OAuth, target ID, delegation, no-body, destructive behavior, and out-of-scope guidance.
- `examples`: representative success and failure examples.

**Relationships**:

- Uses `Comment Delete Request` as input.
- Produces `Deletion Mutation Result` on success.
- Depends on the Layer 1 `comments.delete` wrapper for endpoint behavior.

**Validation Rules**:

- Must be discoverable through the default MCP tool registry.
- Must expose quota cost 50 and OAuth-required auth in metadata, description, usage notes, and examples.
- Must not claim to list comments, create replies, edit comment text, change moderation status, recover deleted comments, recommend moderation decisions, or perform higher-level comment workflows.

## Comment Delete Request

**Purpose**: Caller-provided request shape for one deletion attempt.

**Fields**:

- `id`: required non-empty comment identifier for the comment resource being deleted.
- `onBehalfOfContentOwner`: optional delegated content-owner context when supported by Layer 1 and eligible OAuth authorization.

**Relationships**:

- Contains one `Target Comment Identifier`.
- Requires `Write Authorization Context`.
- Is governed by `Deletion Boundary Policy`.

**Validation Rules**:

- Reject missing, empty, malformed, duplicate, conflicting, or multi-target `id` shapes.
- Reject request bodies, listing fields, insertion fields, update-body fields, moderation fields, recovery instructions, search instructions, ranking instructions, summarization instructions, sentiment instructions, enrichment instructions, automated moderation advice, and unsupported optional parameters.
- Reject or map unavailable comments, already deleted comments, and insufficient permissions to safe caller-facing categories.

## Target Comment Identifier

**Purpose**: Identifier of the existing comment that will be deleted.

**Fields**:

- `id`: one non-empty comment identifier.
- `accessState`: effective caller-facing state after validation or upstream response, such as deletion eligible, missing, already deleted, private, inaccessible, ineligible, or unsupported.

**Relationships**:

- Referenced by `Comment Delete Request`.
- Determines whether `comments_delete` can delete the selected comment.

**Validation Rules**:

- Missing or empty target comment ID fails local validation.
- Duplicate, conflicting, list-style, or multi-target target shapes fail local validation unless a shared contract explicitly adds a supported multi-target pattern later.
- Missing, already deleted, private, inaccessible, ineligible, or unsupported target comments must be surfaced distinctly from successful deletion.

## Deletion Boundary Policy

**Purpose**: Caller-facing rules that distinguish supported destructive deletion from unsupported request shapes and unrelated workflows.

**Fields**:

- `supportedOperation`: fixed value `delete one existing comment`.
- `noBodyRule`: no request body is supported for this operation.
- `destructiveBehavior`: successful calls remove the targeted comment when the caller is authorized.
- `unsupportedOperationBoundary`: listing, insertion, update, moderation status change, recovery, recommendation, ranking, summarization, sentiment, enrichment, and cross-endpoint behaviors are outside scope.

**Relationships**:

- Applies to every `Comment Delete Request`.
- Shapes public validation, usage notes, caveats, and examples.

**Validation Rules**:

- Reject body-bearing or unrelated workflow requests.
- Public surfaces must clearly disclose destructive behavior and no returned deleted-comment resource.

## Write Authorization Context

**Purpose**: OAuth-backed caller authorization used for the destructive write operation.

**Fields**:

- `mode`: fixed value `oauth_required`.
- `eligible`: whether the caller has sufficient authorization for the target comment context.
- `delegatedContext`: safe presence indicator for delegated owner context when supplied.

**Relationships**:

- Required by every `Comment Delete Request`.
- Passed to the Layer 1 wrapper without exposing credential values in public metadata, results, or errors.

**Validation Rules**:

- Missing OAuth credentials map to `authentication_failed`.
- Present but insufficient OAuth authorization maps to `authorization_failed`.
- Public surfaces must never expose API keys, OAuth tokens, signed URLs, stack traces, raw credential diagnostics, or sensitive owner credential details.

## Deletion Mutation Result

**Purpose**: Successful acknowledgment for one deletion request.

**Fields**:

- `endpoint`: fixed value `comments.delete`.
- `quotaCost`: fixed value `50`.
- `deleted`: true for successful deletion mutation.
- `targetId`: normalized target comment identifier.
- `auth`: safe OAuth-required context summary.
- `delegation`: safe delegated context summary when supplied.
- `statusCode`: successful no-content acknowledgment, represented without fabricating comment resource data.

**Relationships**:

- Produced by `Comments Delete Tool`.
- Represents a successful upstream 204/no-content mutation response.

**Validation Rules**:

- Preserve requested target and operation context without fabricating missing comment data.
- Do not include unrelated parent thread, channel, video, edit, moderation, recovery, sentiment, ranking, summary, enrichment, or recommendation data.
- Do not expose secret-bearing request or authorization details.

## State Transitions

```text
Draft Request
  -> Locally Invalid (missing/empty target ID, duplicate/conflicting target shape, body or unsupported shape)
  -> Awaiting OAuth Validation
  -> Authentication Failed (missing OAuth)
  -> Authorization Failed (insufficient OAuth or inaccessible target)
  -> Upstream Deletion Attempted
  -> Deletion Mutation Result (204/no-content acknowledgment)
  -> Upstream Failure (quota, missing target, already deleted target, unavailable endpoint, unexpected failure)
```
