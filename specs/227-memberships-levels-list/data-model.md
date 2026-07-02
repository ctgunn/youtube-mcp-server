# Data Model: YT-227 Layer 2 Tool `membershipsLevels_list`

## Memberships Levels List Tool

**Purpose**: Public Layer 2 MCP tool for owner-scoped channel membership-level retrieval through `membershipsLevels.list`.

**Fields**:
- `toolName`: Must be `membershipsLevels_list`.
- `upstreamResource`: Must be `membershipsLevels`.
- `upstreamMethod`: Must be `list`.
- `operationKey`: Must be `membershipsLevels.list`.
- `quotaCost`: Must be `1`.
- `authMode`: Must be `oauth_required`.
- `availabilityState`: Active with owner-only and channel-membership eligibility caveats.

**Relationships**:
- Uses one Memberships Levels List Request.
- Produces one Memberships Levels List Result or one safe Memberships Levels List Error.
- Depends on the YT-127 Layer 1 `membershipsLevels.list` wrapper.

**Validation Rules**:
- Discovery metadata, descriptions, usage notes, and examples must expose endpoint identity, quota cost, auth mode, owner-only access, channel-membership constraints, supported inputs, and unsupported boundaries.
- Public metadata must not include OAuth tokens, raw request context, stack traces, or unsafe diagnostics.

## Memberships Levels List Request

**Purpose**: Caller-supplied input for one owner-scoped membership-level list operation.

**Fields**:
- `part`: Required string. Supported value is `snippet`.

**Relationships**:
- Part Selection determines returned membership-level fields.
- Owner Access Context is required before the request can succeed.

**Validation Rules**:
- Reject missing, blank, malformed, duplicate, unsupported, or conflicting part selections.
- Reject unsupported fields, including filters, paging controls, page tokens, maximum result counts, delegation-related inputs, member-list selectors, subscriber lookup fields, management actions, analytics fields, ranking, summarization, and enrichment.
- Reject API-key-only or missing OAuth access before treating the request as a supported membership-level list call.

## Part Selection

**Purpose**: Defines which membership-level resource sections are requested.

**Fields**:
- `requestedParts`: Ordered list derived from `part`; must contain only `snippet` for this slice.

**Validation Rules**:
- Must be present.
- Must not contain unsupported part names.
- Must be preserved in successful results for caller review.

## Owner Access Context

**Purpose**: Represents the OAuth-backed eligibility needed to retrieve membership-level data.

**Fields**:
- `authMode`: Must be `oauth_required`.
- `ownerVisibility`: Indicates that the authorizing user must be the channel owner.
- `membershipEligibility`: Indicates that the channel must be eligible for channel-membership level access.

**Validation Rules**:
- API-key-only access is invalid for this tool.
- Missing OAuth, non-owner OAuth, and channel-membership ineligibility must be distinguishable from malformed requests and successful empty results.
- Public results and errors must not expose secrets or sensitive membership configuration details beyond returned successful membership-level resources.

## Membership Level Resource

**Purpose**: Represents one returned membership-level definition visible to the authorized owner context.

**Fields**:
- `kind`: Returned resource kind, when present.
- `etag`: Returned resource etag, when present.
- `id`: Membership-level identifier, when present.
- `snippet`: Membership-level descriptive fields, when requested and returned.

**Validation Rules**:
- Returned fields must be preserved as received.
- Missing optional fields must not be fabricated.
- No member details, subscriber data, analytics, ranking, summaries, or enrichment should be added to the resource.

## Memberships Levels List Result

**Purpose**: Successful near-raw response wrapper for membership-level collections.

**Fields**:
- `endpoint`: `membershipsLevels.list`.
- `quotaCost`: `1`.
- `requestedParts`: Normalized part selection.
- `auth`: Safe auth-mode summary.
- `items`: Returned membership-level resources, possibly empty.
- `kind`: Upstream response kind, when returned.
- `etag`: Upstream etag, when returned.

**Validation Rules**:
- Empty `items` is a successful result when request shape and access are valid.
- Returned fields must be preserved without adding member listing, subscriber lookup, analytics, ranking, summarization, enrichment, recommendation, or heuristic classification.
- Missing optional upstream fields must not be fabricated.

## Memberships Levels List Error

**Purpose**: Safe caller-facing failure for invalid, ineligible, quota, unavailable, or unexpected membership-level list outcomes.

**Fields**:
- `category`: One of the shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, or `upstream_failure`.
- `message`: Caller-facing correction or failure summary.
- `details`: Sanitized diagnostic fields such as invalid field name or supported values.

**Validation Rules**:
- Must not include OAuth tokens, API keys, stack traces, raw upstream bodies, raw request context, or unsafe diagnostics.
- Must distinguish malformed input, auth failure, owner-visibility failure, channel-membership eligibility failure, empty successful results, and upstream failures.

## Quota Disclosure

**Purpose**: Public statement that each invocation costs 1 official quota unit.

**Fields**:
- `quotaCost`: `1`.
- `visibleLocations`: Discovery metadata, description, usage notes, examples, and successful result context.

**Validation Rules**:
- Every caller-facing contract surface for this tool must consistently report quota cost `1`.

## Unsupported Boundary Guidance

**Purpose**: Caller-facing explanation of what the low-level membership-level listing tool does not do.

**Fields**:
- `unsupportedBehaviors`: Channel member listing, subscriber lookup, delegation inputs, filters, paging controls, membership administration, analytics, ranking, summarization, enrichment, recommendation, and cross-endpoint aggregation.

**Validation Rules**:
- Unsupported behaviors must fail clearly or be documented as separate endpoint or higher-level workflow concerns.
- Unsupported behavior guidance must be visible before invocation.
