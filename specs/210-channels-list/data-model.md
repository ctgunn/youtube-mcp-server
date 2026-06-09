# Data Model: YT-210 Layer 2 Tool `channels_list`

## Channels List Tool

**Purpose**: Public Layer 2 MCP tool named `channels_list` that exposes the upstream `channels.list` channel retrieval operation.

**Fields**:

- `toolName`: Must be `channels_list`.
- `upstreamResource`: Must be `channels`.
- `upstreamMethod`: Must be `list`.
- `operationKey`: Must be `channels.list`.
- `quotaCost`: Must be `1`.
- `authMode`: Must be `mixed/conditional`.
- `availabilityState`: Should indicate active availability with documented selector caveats.
- `description`: Caller-facing description that includes endpoint identity, quota cost, mixed auth, and supported selector modes.
- `inputContract`: JSON-compatible schema for the channel lookup request.
- `responseConvention`: List-result convention preserving returned channel collection fields.
- `responseBoundary`: Near-raw endpoint boundary with allowed safe wrapper fields.
- `usageNotes`: Caller-facing notes that include quota, public selectors, owner-scoped OAuth selector, pagination, and empty-result behavior.
- `caveats`: Safe caveats for selector exclusivity, username-style lookup, and out-of-scope higher-level channel workflows.

**Validation Rules**:

- Tool name must derive from `channels.list` without adding a `youtube_` prefix.
- Quota cost must be visible in metadata, description, and usage notes.
- Auth mode must distinguish public selector paths from `mine` owner-scoped OAuth behavior.
- Public metadata must not include credentials, stack traces, private channel data, or secret values.
- The contract must remain scoped to channel retrieval and must not claim to perform search ranking, analytics, video expansion, playlist expansion, or channel updates.

**Relationships**:

- Uses the `Channels List Request` as input.
- Produces a `Channel Collection Result`.
- Depends on the YT-110 Layer 1 `channels.list` wrapper for endpoint execution.
- Follows YT-201 and YT-202 shared Layer 2 contract standards.

## Channels List Request

**Purpose**: Caller-provided arguments for one `channels_list` invocation.

**Fields**:

- `part` (required): Comma-separated channel resource parts requested from the endpoint.
- `id` (optional selector): Channel ID or comma-separated channel IDs.
- `mine` (optional selector): Boolean owner-scoped selector for the authenticated user's channel.
- `forHandle` (optional selector): YouTube handle selector; the value may include an `@` prefix.
- `forUsername` (optional selector): Legacy username-style selector.
- `pageToken` (optional): Pagination cursor for continuation.
- `maxResults` (optional): Page-size control.
- `hl` (optional): Localization language hint when supported by the endpoint contract.

**Validation Rules**:

- `part` is required and must be non-empty.
- Exactly one supported selector from `id`, `mine`, `forHandle`, or `forUsername` is required.
- Empty, malformed, unsupported, or conflicting selectors are invalid.
- `mine` requires eligible OAuth authorization.
- Public selectors `id`, `forHandle`, and `forUsername` use public API-key style access in the existing Layer 1 contract.
- `maxResults` must remain within the endpoint-supported page-size range.
- Unsupported fields, channel update fields, search query fields, analytics fields, video expansion fields, and playlist expansion fields are invalid for this tool.

**Relationships**:

- Contains one `Channel Lookup Filter`.
- Contains one `Part Selection`.
- May contain one `Pagination Cursor`.
- Is validated before calling the Layer 1 wrapper.

## Channel Lookup Filter

**Purpose**: The selector that determines how channel resources are retrieved.

**Fields**:

- `selectorName`: One of `id`, `mine`, `forHandle`, or `forUsername`.
- `selectorValue`: String value for `id`, `forHandle`, or `forUsername`; boolean `true` for `mine`.
- `accessRequirement`: Public API-key style access for `id`, `forHandle`, and `forUsername`; eligible user authorization for `mine`.

**Validation Rules**:

- Only one selector can be active.
- `id`, `forHandle`, and `forUsername` must be non-empty strings when present.
- `mine` must be `true` when used and must not be combined with public selectors.
- `forHandle` should preserve the caller-provided handle value after safe trimming.
- `forUsername` should be documented as username-style or legacy username lookup where supported.

**Relationships**:

- Belongs to one `Channels List Request`.
- Determines one `Auth Requirement`.
- Is echoed safely in the `Channel Collection Result`.

## Part Selection

**Purpose**: Caller-selected channel resource sections requested from the endpoint.

**Fields**:

- `rawPart`: Original comma-separated part string.
- `requestedParts`: Ordered normalized part names with surrounding whitespace removed.

**Validation Rules**:

- Must be non-empty.
- Must preserve requested part names for caller review.
- Must not imply validation of higher-level business semantics beyond the endpoint contract.

**Relationships**:

- Belongs to one `Channels List Request`.
- Is preserved in a `Channel Collection Result`.

## Pagination Cursor

**Purpose**: Optional continuation information for paginated channel result sets.

**Fields**:

- `pageToken`: Caller-provided continuation token.
- `maxResults`: Optional requested page size.
- `nextPageToken`: Continuation token returned by the upstream response when present.
- `prevPageToken`: Previous-page token returned by the upstream response when present.
- `pageInfo`: Upstream page summary when present.

**Validation Rules**:

- `pageToken` must be non-empty when present.
- `maxResults` must remain within the endpoint-supported page-size range.
- Returned pagination fields must be preserved when present.

**Relationships**:

- May be supplied by one `Channels List Request`.
- May be returned in one `Channel Collection Result`.

## Auth Requirement

**Purpose**: Caller-facing access expectation derived from the selected lookup mode.

**Fields**:

- `authMode`: `api_key` for public selectors or `oauth_required` for `mine`.
- `selectorName`: Selector that caused the access requirement.
- `guidance`: Safe caller-facing explanation of the required credential mode.

**Validation Rules**:

- Missing API-key style access for public selectors must surface a safe authentication failure.
- Missing OAuth for `mine` must surface a safe authentication failure.
- Authorization-sensitive failures must be distinguishable from no-match public lookups.
- Errors must not expose API keys, OAuth tokens, or private channel data.

**Relationships**:

- Determined by one `Channel Lookup Filter`.
- Used by the handler before calling the Layer 1 wrapper.

## Channel Collection Result

**Purpose**: Caller-facing result from a successful `channels_list` lookup.

**Fields**:

- `endpoint`: Safe operation identity such as `channels.list`.
- `quotaCost`: Official quota cost, `1`.
- `items`: Returned channel resource collection; may be empty.
- `requestedParts`: Ordered normalized part names.
- `selector`: Safe selected lookup mode context.
- `nextPageToken`: Returned continuation token when present.
- `prevPageToken`: Returned previous-page token when present.
- `pageInfo`: Returned page summary when present.

**Validation Rules**:

- Must preserve returned upstream channel items and pagination fields when present.
- Must treat valid no-match lookups as successful empty collections.
- Must not fabricate analytics, search ranking, video lists, playlist lists, branding update state, or enriched summaries.
- Must not expose credentials, private channel data beyond returned endpoint fields, stack traces, or secret values.

**Relationships**:

- Produced by `channels_list`.
- Contains one safe selector context.
- Contains one requested part summary.

## Error Outcome

**Purpose**: Safe caller-facing representation of validation and upstream failures.

**Fields**:

- `category`: Shared Layer 2 error category.
- `message`: Caller-facing correction guidance.
- `details`: Safe diagnostic context, such as invalid field name, selector name, or upstream status when safe.

**Validation Rules**:

- Missing `part`, missing selector, conflicting selectors, empty selector values, malformed `forHandle`, invalid `maxResults`, unsupported fields, and unsupported higher-level channel workflow fields map to safe invalid-request outcomes.
- Missing OAuth for `mine` maps to a safe authentication failure.
- Insufficient owner-scoped authorization maps to a safe authorization failure.
- Upstream invalid criteria, missing channel, quota, unavailable service, and unexpected upstream failures must follow shared Layer 2 error conventions.
- Errors must not expose stack traces, credentials, private channel data, or secret values.

## State Transitions

1. **Discovered**: `channels_list` appears in the public tool catalog with full metadata.
2. **Validated**: Caller arguments satisfy part, selector, pagination, and auth constraints.
3. **Lookup Attempted**: The request is routed to the Layer 1 `channels.list` wrapper.
4. **Succeeded**: The tool returns a near-raw `Channel Collection Result` with returned items, selected lookup mode, requested parts, pagination, and safe operation context.
5. **Rejected**: Invalid input or authorization-sensitive failures return a safe `Error Outcome`.
6. **Out of Scope**: Requests for analytics, search ranking, channel updates, video expansion, playlist expansion, branding updates, or enrichment are rejected or documented as separate behavior.
