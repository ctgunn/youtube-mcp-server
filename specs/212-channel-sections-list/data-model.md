# Data Model: YT-212 Layer 2 Tool `channelSections_list`

## Channel Sections List Tool

**Purpose**: Public Layer 2 MCP tool named `channelSections_list` that exposes the upstream `channelSections.list` channel-section retrieval operation.

**Fields**:

- `toolName`: Must be `channelSections_list`.
- `upstreamResource`: Must be `channelSections`.
- `upstreamMethod`: Must be `list`.
- `operationKey`: Must be `channelSections.list`.
- `quotaCost`: Must be `1`.
- `authMode`: Must be `mixed/conditional`.
- `availabilityState`: Should indicate active availability with documented deprecation and partner caveats.
- `description`: Caller-facing description that includes endpoint identity, quota cost, mixed auth, and supported selector modes.
- `inputContract`: JSON-compatible schema for the channel-section lookup request.
- `responseConvention`: List-result convention preserving returned channel-section collection fields.
- `responseBoundary`: Near-raw endpoint boundary with allowed safe wrapper fields.
- `usageNotes`: Caller-facing notes that include quota, public selectors, owner-scoped OAuth selector, empty-result behavior, optional returned continuation handling, `hl` deprecation, and content-owner caveats.
- `caveats`: Safe caveats for selector exclusivity, deprecated localization behavior, content-owner partner behavior, optional pagination discrepancy, and out-of-scope higher-level channel-section workflows.

**Validation Rules**:

- Tool name must derive from `channelSections.list` without adding a `youtube_` prefix.
- Quota cost must be visible in metadata, description, and usage notes.
- Auth mode must distinguish public selector paths from `mine` owner-scoped OAuth behavior.
- Public metadata must not include credentials, stack traces, private channel data, or secret values.
- The contract must remain scoped to channel-section retrieval and must not claim to perform playlist item expansion, video metadata expansion, analytics, ranking, layout recommendations, mutation, or enrichment.

**Relationships**:

- Uses the `Channel Sections List Request` as input.
- Produces a `Channel Section Collection Result`.
- Depends on the YT-112 Layer 1 `channelSections.list` wrapper for endpoint execution.
- Follows YT-201 and YT-202 shared Layer 2 contract standards.

## Channel Sections List Request

**Purpose**: Caller-provided arguments for one `channelSections_list` invocation.

**Fields**:

- `part` (required): Comma-separated channel-section resource parts requested from the endpoint.
- `channelId` (optional selector): YouTube channel ID whose channel sections should be listed.
- `id` (optional selector): Channel-section ID or comma-separated channel-section IDs.
- `mine` (optional selector): Boolean owner-scoped selector for the authenticated user's channel sections.
- `hl` (optional caveat field): Deprecated localization hint when exposed for compatibility.
- `onBehalfOfContentOwner` (optional caveat field): YouTube content-owner context intended exclusively for eligible content partners when supported by the dependency.
- `pageToken` (optional compatibility field): Continuation token only if the final dependency and endpoint contract support it.
- `maxResults` (optional compatibility field): Page-size control only if the final dependency and endpoint contract support it.

**Validation Rules**:

- `part` is required and must be non-empty.
- Exactly one supported selector from `channelId`, `id`, or `mine` is required.
- Empty, malformed, unsupported, or conflicting selectors are invalid.
- `mine` requires eligible OAuth authorization.
- Public selectors `channelId` and `id` use public API-key style access in the existing Layer 1 contract.
- `hl` must be documented as deprecated when exposed.
- `onBehalfOfContentOwner` must be documented as authorization-sensitive and partner-scoped when exposed.
- Pagination request fields must not be promised as core official endpoint behavior unless implementation verifies support against the current dependency and contract.
- Unsupported fields, channel update fields, channel search fields, analytics fields, video expansion fields, playlist expansion fields, and layout recommendation fields are invalid for this tool.

**Relationships**:

- Contains one `Channel-Section Lookup Filter`.
- Contains one `Part Selection`.
- May contain one `Official Caveat Context`.
- May contain one `Compatibility Pagination Cursor` when supported.
- Is validated before calling the Layer 1 wrapper.

## Channel-Section Lookup Filter

**Purpose**: The selector that determines how channel section resources are retrieved.

**Fields**:

- `selectorName`: One of `channelId`, `id`, or `mine`.
- `selectorValue`: String value for `channelId` or `id`; boolean `true` for `mine`.
- `accessRequirement`: Public API-key style access for `channelId` and `id`; eligible user authorization for `mine`.

**Validation Rules**:

- Only one selector can be active.
- `channelId` and `id` must be non-empty strings when present.
- `mine` must be `true` when used and must not be combined with public selectors.
- Unsupported selector aliases such as channel handles, usernames, search queries, or playlist IDs are invalid.

**Relationships**:

- Belongs to one `Channel Sections List Request`.
- Determines one `Auth Requirement`.
- Is echoed safely in the `Channel Section Collection Result`.

## Part Selection

**Purpose**: Caller-selected channel-section resource sections requested from the endpoint.

**Fields**:

- `rawPart`: Original comma-separated part string.
- `requestedParts`: Ordered normalized part names with surrounding whitespace removed.

**Validation Rules**:

- Must be non-empty.
- Officially documented values include `contentDetails`, `id`, and `snippet`.
- Must preserve requested part names for caller review.
- Must not imply validation of higher-level business semantics beyond the endpoint contract.

**Relationships**:

- Belongs to one `Channel Sections List Request`.
- Is preserved in a `Channel Section Collection Result`.

## Official Caveat Context

**Purpose**: Caller-facing context for official documentation caveats that affect `channelSections.list`.

**Fields**:

- `hlDeprecated`: Indicates that `hl` localization behavior is deprecated in current official documentation.
- `contentOwnerPartnerScoped`: Indicates that `onBehalfOfContentOwner` is intended exclusively for authorized YouTube content partners.
- `paginationSupportState`: Indicates whether pagination request fields are officially supported, dependency-supported only, or result-preserved only.

**Validation Rules**:

- Deprecated `hl` behavior must be visible before invocation when the field is exposed.
- Content-owner fields must not be presented as public or API-key-only behavior.
- Pagination fields must not be represented as official endpoint controls unless current documentation and dependency behavior support them.

**Relationships**:

- Belongs to the `Channel Sections List Tool`.
- Informs `Channel Sections List Request` validation and usage notes.

## Compatibility Pagination Cursor

**Purpose**: Optional continuation information that may be preserved for compatibility when present in dependency or upstream-compatible responses.

**Fields**:

- `pageToken`: Caller-provided continuation token when supported.
- `maxResults`: Optional requested page size when supported.
- `nextPageToken`: Continuation token returned by the upstream response when present.
- `prevPageToken`: Previous-page token returned by the upstream response when present.
- `pageInfo`: Upstream page summary when present.

**Validation Rules**:

- Request fields are accepted only if the final public contract intentionally supports them.
- Returned pagination fields must be preserved when present and safe.
- Absence of pagination fields must not be treated as an error.

**Relationships**:

- May be supplied by one `Channel Sections List Request`.
- May be returned in one `Channel Section Collection Result`.

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

- Determined by one `Channel-Section Lookup Filter`.
- Used by the handler before calling the Layer 1 wrapper.

## Channel Section Collection Result

**Purpose**: Caller-facing result from a successful `channelSections_list` lookup.

**Fields**:

- `endpoint`: Safe operation identity such as `channelSections.list`.
- `quotaCost`: Official quota cost, `1`.
- `items`: Returned channel-section resource collection; may be empty.
- `requestedParts`: Ordered normalized part names.
- `selector`: Safe selected lookup mode context.
- `caveats`: Safe caveats that applied to the request or tool contract.
- `nextPageToken`: Returned continuation token when present.
- `prevPageToken`: Returned previous-page token when present.
- `pageInfo`: Returned page summary when present.

**Validation Rules**:

- Must preserve returned upstream channel-section items and safe continuation fields when present.
- Must treat valid no-match lookups as successful empty collections.
- Must not fabricate channel analytics, section ranking, playlist item lists, video metadata, layout recommendations, update state, or enriched summaries.
- Must not expose credentials, private channel data beyond returned endpoint fields, stack traces, or secret values.

**Relationships**:

- Produced by `channelSections_list`.
- Contains one safe selector context.
- Contains one requested part summary.
- May contain caveat context.

## Error Outcome

**Purpose**: Safe caller-facing representation of validation and upstream failures.

**Fields**:

- `category`: Shared Layer 2 error category.
- `message`: Caller-facing correction guidance.
- `details`: Safe diagnostic context, such as invalid field name, selector name, caveat name, or upstream status when safe.

**Validation Rules**:

- Missing `part`, missing selector, conflicting selectors, empty selector values, invalid `mine`, unsupported fields, unsupported selector aliases, and unsupported higher-level channel-section workflow fields map to safe invalid-request outcomes.
- Missing OAuth for `mine` maps to a safe authentication failure.
- Insufficient owner-scoped authorization maps to a safe authorization failure.
- Upstream invalid criteria, invalid ID, missing channel, missing channel section, quota, unavailable service, deprecated behavior, and unexpected upstream failures must follow shared Layer 2 error conventions.
- Errors must not expose stack traces, credentials, private channel data, or secret values.

## State Transitions

1. **Discovered**: `channelSections_list` appears in the public tool catalog with full metadata.
2. **Validated**: Caller arguments satisfy part, selector, caveat, optional pagination, and auth constraints.
3. **Lookup Attempted**: The request is routed to the Layer 1 `channelSections.list` wrapper.
4. **Succeeded**: The tool returns a near-raw `Channel Section Collection Result` with returned items, selected lookup mode, requested parts, optional returned continuation fields, caveats, and safe operation context.
5. **Rejected**: Invalid input or authorization-sensitive failures return a safe `Error Outcome`.
6. **Out of Scope**: Requests for playlist item expansion, video metadata expansion, channel analytics, section ranking, layout recommendations, mutation behavior, or enrichment are rejected or documented as separate behavior.
