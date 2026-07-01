# Data Model: YT-226 Layer 2 Tool `members_list`

## Members List Tool

**Purpose**: Public Layer 2 MCP tool for owner-scoped channel membership retrieval through `members.list`.

**Fields**:
- `toolName`: Must be `members_list`.
- `upstreamResource`: Must be `members`.
- `upstreamMethod`: Must be `list`.
- `operationKey`: Must be `members.list`.
- `quotaCost`: Must be `2`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Active with owner-only and channel-membership eligibility caveats.

**Relationships**:
- Uses one Members List Request.
- Produces one Members List Result or one safe Members List Error.
- Depends on the YT-126 Layer 1 `members.list` wrapper.

**Validation Rules**:
- Discovery metadata, descriptions, usage notes, and examples must expose endpoint identity, quota cost, auth mode, owner-only access, channel-membership constraints, supported inputs, and unsupported boundaries.
- Public metadata must not include OAuth tokens, raw request context, stack traces, or unsafe diagnostics.

## Members List Request

**Purpose**: Caller-supplied input for one owner-scoped membership list operation.

**Fields**:
- `part`: Required string. Supported value is `snippet`.
- `mode`: Required string. Supported values are `all_current` and `updates`.
- `pageToken`: Optional non-empty string for a page in the same mode stream.
- `maxResults`: Optional integer within the documented member-list bound.

**Relationships**:
- Part Selection determines returned member fields.
- Membership Retrieval Mode determines the member stream being requested.
- Pagination Context is supplied by `pageToken` and `maxResults`.
- Owner Access Context is required before the request can succeed.

**Validation Rules**:
- Reject missing, blank, malformed, duplicate, unsupported, or conflicting part selections.
- Reject missing, blank, malformed, multiple, or unsupported mode values.
- Reject empty page tokens.
- Reject maximum result counts outside the documented member-list range.
- Reject unsupported fields, including delegation-related inputs, membership-level lookup fields, management actions, analytics fields, ranking, summarization, enrichment, `hasAccessToLevel`, and `filterByMemberChannelId` until a Layer 1 contract revision explicitly supports them.
- Reject API-key-only or missing OAuth access before treating the request as a supported member-list call.

## Part Selection

**Purpose**: Defines which member resource sections are requested.

**Fields**:
- `requestedParts`: Ordered list derived from `part`; must contain only `snippet` for this slice.

**Validation Rules**:
- Must be present.
- Must not contain unsupported part names.
- Must be preserved in successful results for caller review.

## Membership Retrieval Mode

**Purpose**: Defines which member stream is retrieved.

**Fields**:
- `mode`: Either `all_current` for current members or `updates` for membership changes.

**Validation Rules**:
- Must be present even though the upstream endpoint has a default, because the Layer 1 and Layer 2 contracts require deterministic request context.
- Page tokens are mode-specific; incompatible tokens must surface as invalid-request or upstream failure according to shared error conventions.
- Must be preserved in successful results.

## Pagination Context

**Purpose**: Represents caller-supplied and returned pagination information.

**Fields**:
- `pageToken`: Caller-supplied page token, when present.
- `maxResults`: Caller-supplied maximum result count, when present.
- `nextPageToken`: Returned upstream page token, when present.
- `pageInfo`: Returned upstream page metadata, when present.

**Validation Rules**:
- Empty page tokens are invalid.
- `maxResults` must be inside the documented member-list range and must not silently exceed quota or endpoint expectations.
- Returned pagination fields must be preserved without fabricating missing tokens.

## Owner Access Context

**Purpose**: Represents the OAuth-backed eligibility needed to retrieve membership data.

**Fields**:
- `authMode`: Must be `oauth_required`.
- `ownerVisibility`: Indicates that the authorizing user must be the channel owner.
- `membershipEligibility`: Indicates that the channel must be eligible for channel-memberships member access.

**Validation Rules**:
- API-key-only access is invalid for this tool.
- Missing OAuth, non-owner OAuth, and channel-membership ineligibility must be distinguishable from malformed requests and successful empty results.
- Public results and errors must not expose secrets or sensitive member details beyond returned successful member resources.

## Members List Result

**Purpose**: Successful near-raw response wrapper for member collections.

**Fields**:
- `endpoint`: `members.list`.
- `quotaCost`: `2`.
- `requestedParts`: Normalized part selection.
- `mode`: Selected membership retrieval mode.
- `auth`: Safe auth-mode summary.
- `items`: Returned member resources, possibly empty.
- `kind`: Upstream response kind, when returned.
- `etag`: Upstream etag, when returned.
- `nextPageToken`: Upstream next page token, when returned.
- `pageInfo`: Upstream page info, when returned.

**Validation Rules**:
- Empty `items` is a successful result when request shape and access are valid.
- Returned fields must be preserved without adding analytics, ranking, summarization, enrichment, subscriber lookup, or membership-level details.
- Missing optional upstream fields must not be fabricated.

## Members List Error

**Purpose**: Safe caller-facing failure for invalid, ineligible, quota, unavailable, or unexpected member-list outcomes.

**Fields**:
- `category`: One of the shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, or `upstream_failure`.
- `message`: Caller-facing correction or failure summary.
- `details`: Sanitized diagnostic fields such as invalid field name, selected mode, or supported values.

**Validation Rules**:
- Must not include OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.
- Must distinguish malformed input, auth failure, owner-visibility failure, channel-membership eligibility failure, empty successful results, and upstream failures.
