# Data Model: Layer 2 Subscriptions Delete Tool

## Subscriptions Delete Tool

Represents the public Layer 2 MCP tool named `subscriptions_delete`.

**Fields**
- `name`: Constant public tool name, always `subscriptions_delete`.
- `upstreamResource`: YouTube resource name, always `subscriptions`.
- `upstreamMethod`: YouTube method name, always `delete`.
- `quotaCost`: Official per-call quota cost, always `50`.
- `authMode`: Public auth disclosure, always `oauth_required`.
- `availabilityState`: Caller-facing endpoint availability state.
- `inputContract`: The schema for one deletion request.
- `responseConvention`: The success result shape for a deletion acknowledgment.
- `examples`: Caller-facing examples for success, validation failure, access failure, target-state failure, quota/upstream failure, and out-of-scope requests.

**Relationships**
- Uses one Subscriptions Delete Request.
- Produces one Subscriptions Delete Result or one Subscriptions Delete Failure.
- Depends on the Layer 1 `subscriptions.delete` wrapper for endpoint behavior.

**Validation Rules**
- Must expose quota cost `50` in metadata, description, usage notes, examples, and result context.
- Must disclose OAuth-required access before invocation.
- Must not advertise listing, creation, discovery, recommendation, notification management, analytics, enrichment, or bulk behavior.

## Subscriptions Delete Request

Represents the caller's request to remove one subscription relationship.

**Fields**
- `id`: Required non-empty subscription relationship identifier.

**Relationships**
- Supplies the Subscription Relationship Identifier.
- Is passed to the Layer 1 `subscriptions.delete` wrapper after validation.
- Is summarized in the Subscriptions Delete Result as safe deletion context.

**Validation Rules**
- `id` is required.
- `id` must be non-empty text after trimming.
- No additional public fields are accepted.
- Channel IDs, bodies, selectors, creation fields, notification modifiers, analytics flags, ranking flags, summarization flags, and enrichment flags are invalid for this tool.
- The request represents one deletion attempt only; no bulk deletion or preflight lookup is implied.

## Subscription Relationship Identifier

Represents the subscription relationship the authorized account is attempting to remove.

**Fields**
- `id`: The identifier supplied by the caller.

**Relationships**
- Appears in the request.
- Appears in safe result context when deletion succeeds.
- May appear in safe error details when validation or target-state failures occur.

**Validation Rules**
- Must be provided by the caller.
- Must not be inferred from channel URL, channel ID, search terms, or subscription list selectors.
- Must not expose OAuth credentials, authorization headers, or raw upstream diagnostics.

## Access Context

Represents the safe caller-facing access mode used for deletion.

**Fields**
- `mode`: Always `oauth_required` for supported deletion requests.

**Relationships**
- Required before the Layer 1 wrapper is called.
- Included in success results and safe access failures.

**Validation Rules**
- Missing, invalid, expired, or insufficient OAuth access is categorized as an access failure.
- API-key-only access is not accepted.
- Tokens, authorization headers, and credential material are never returned in results, errors, logs, metadata, or examples.

## Deletion Acknowledgment

Represents a successful deletion outcome.

**Fields**
- `deleted`: Boolean success marker, expected `true`.
- `id`: The requested subscription relationship identifier.
- `endpoint`: Always `subscriptions.delete`.
- `quotaCost`: Always `50`.
- `auth`: Safe Access Context.
- `upstream`: Optional safe upstream acknowledgment fields when present.

**Relationships**
- Forms the core of the Subscriptions Delete Result.
- Carries safe request context rather than a fabricated deleted resource.

**Validation Rules**
- Must preserve enough context for callers to identify the targeted deletion.
- Must not fabricate subscription resource details, channel details, analytics, notification settings, recommendation, ranking, summarization, or enrichment.

## Subscriptions Delete Result

Represents the complete successful public result for `subscriptions_delete`.

**Fields**
- `endpoint`: `subscriptions.delete`.
- `quotaCost`: `50`.
- `deleted`: `true`.
- `deletion`: Object containing safe deletion context, including `id`.
- `auth`: Safe Access Context.
- `upstream`: Optional safe upstream acknowledgment context.

**Relationships**
- Produced by a valid authorized Subscriptions Delete Request.
- Consumed by MCP clients and higher-layer workflows that need direct endpoint deletion behavior.

**Validation Rules**
- Must remain near-raw and endpoint-backed.
- Must distinguish acknowledgment-style success from empty list results or created-resource results.
- Must not include secret-bearing request or auth data.

## Subscriptions Delete Failure

Represents a safe caller-facing failure instead of a successful deletion result.

**Fields**
- `category`: Stable failure category such as `invalid_request`, `authentication_failed`, `authorization_failed`, `not_found`, `non_removable_target`, `quota_exhausted`, `endpoint_unavailable`, `deprecated_endpoint`, or `upstream_failure`.
- `message`: Human-readable safe summary.
- `details`: Optional sanitized structured details, such as `field`, `id`, `reason`, or `authMode`.

**Relationships**
- Produced by validation, missing OAuth, target-state, quota, availability, deprecation, or unexpected upstream failure.

**Validation Rules**
- Must distinguish local validation failures from access failures and upstream target-state failures.
- Must sanitize API keys, OAuth tokens, authorization headers, raw upstream bodies, stack traces, and unsafe request context.
- Already-removed or missing subscriptions should be distinguishable from successful deletion acknowledgments.

## State Transitions

- `candidate_request` -> `validation_failed`: Missing, empty, malformed, unsupported, or extra fields.
- `validated_request` -> `access_failed`: OAuth access is missing, invalid, expired, or insufficient.
- `validated_request` -> `target_state_failed`: The target subscription is missing, already removed, not owned, blocked, or otherwise non-removable.
- `validated_request` -> `upstream_failed`: Quota, invalid request, unavailable service, deprecated behavior, or unexpected upstream failure occurs.
- `validated_request` -> `deleted`: The subscription deletion succeeds and returns a deletion acknowledgment.
