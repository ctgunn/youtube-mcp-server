# Data Model: YT-236 Layer 2 Tool `playlists_list`

## Playlists List Tool

**Purpose**: Public Layer 2 MCP tool that exposes the low-level `playlists.list` operation.

**Fields**:
- `tool_name`: Stable public name, expected to be `playlists_list`
- `resource`: Upstream resource identity, expected to be `playlists`
- `method`: Upstream method identity, expected to be `list`
- `operation_key`: Caller-visible endpoint identity, expected to be `playlists.list`
- `quota_cost`: Official quota-unit cost, expected to be `1`
- `auth_mode`: Conditional access disclosure for public and owner-scoped selector paths
- `availability_state`: Caller-visible endpoint availability state
- `input_contract`: Playlists List Request contract
- `response_convention`: Playlists List Result convention
- `examples`: Representative success and failure examples

**Validation Rules**:
- Must be discoverable as `playlists_list`
- Must identify `playlists.list` in discovery metadata, description, usage notes, and examples
- Must show quota cost `1` in metadata, description, usage notes, examples, and result context
- Must not describe playlist mutation, playlist item traversal, playlist image handling, search, enrichment, analytics, ranking, summarization, recommendation, or cross-endpoint behavior as part of this tool

## Playlists List Request

**Purpose**: Caller-provided request for one supported playlist retrieval mode.

**Fields**:
- `part`: Required part selection that determines which playlist properties are returned
- `channelId`: Optional channel-scoped selector for retrieving playlists associated with one channel
- `id`: Optional direct selector for retrieving one or more playlists by playlist identifier
- `mine`: Optional owner-scoped selector for retrieving the authorized user's playlists
- `pageToken`: Optional continuation token for selector modes that support paging
- `maxResults`: Optional maximum result count for selector modes that support paging

**Validation Rules**:
- `part` is required and must be non-empty and supported by the public contract
- Exactly one selector from `channelId`, `id`, and `mine` must be present
- `channelId` must be a non-empty channel identifier when used
- `id` must contain one or more non-empty playlist identifiers within supported limits when used
- `mine` must be a valid owner-scoped selector value and requires eligible user authorization
- `pageToken` must be non-empty when present
- `maxResults` must be within the documented playlist listing limits when present
- Paging inputs are valid only for selector modes documented as pageable
- Unsupported fields, unsupported modifiers, empty identifiers, malformed identifiers, conflicting selectors, and out-of-scope workflow requests must be rejected before endpoint execution

## Part Selection

**Purpose**: Determines the playlist resource sections returned to the caller.

**Fields**:
- `requested_parts`: Caller-selected playlist sections
- `supported_parts`: Publicly supported playlist sections for this tool

**Validation Rules**:
- Must be explicitly supplied by the caller
- Must not contain empty, duplicate, unsupported, or conflicting values
- Returned playlist resources must preserve upstream fields for selected parts without fabricating missing optional fields

## Playlist Lookup Selector

**Purpose**: Represents the active retrieval mode for one `playlists_list` request.

**Fields**:
- `name`: One of `channelId`, `id`, or `mine`
- `value`: Caller-provided channel identifier, playlist identifier set, or owner-scoped marker
- `access_requirement`: Public API-key path for `channelId` and `id`, OAuth-backed path for `mine`
- `paging_allowed`: Whether the selector supports `pageToken` and `maxResults`

**Validation Rules**:
- Exactly one lookup selector must be active
- Missing selector input must fail as invalid request input
- Multiple active selectors must fail as conflicting selector input
- Selector-specific access and paging rules must be visible before invocation

## Pagination Context

**Purpose**: Captures caller-supplied and returned page state for collection-style playlist retrieval.

**Fields**:
- `request_page_token`: Optional incoming continuation token
- `request_max_results`: Optional incoming page-size request
- `next_page_token`: Optional continuation token returned by the endpoint
- `previous_page_token`: Optional previous-page token returned by the endpoint
- `result_count`: Number of playlist resources returned in the current result

**Validation Rules**:
- Pagination must be preserved for valid collection-style retrieval through `channelId` and `mine`
- Pagination for direct `id` lookup must be rejected unless the shared contract explicitly permits it
- Empty successful pages must remain distinguishable from validation, access, missing-resource, quota, and upstream failures

## Access Context

**Purpose**: Represents the caller access state used to execute a supported selector path without exposing credentials.

**Fields**:
- `mode`: Public or OAuth-backed access mode selected for the request
- `selector`: Selector that determined the access mode
- `credential_present`: Safe boolean or category indicating whether required access material was available

**Validation Rules**:
- `channelId` and `id` retrieval must use the public lookup path documented for this tool
- `mine` retrieval must require eligible OAuth-backed access
- Missing, invalid, or insufficient owner-scoped access must be reported as access failure, not successful empty results
- Raw API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Playlist Resource

**Purpose**: One playlist returned by the upstream endpoint for the selected parts.

**Fields**:
- `id`: Playlist identifier when returned
- `snippet`: Playlist snippet fields when requested and returned
- `contentDetails`: Playlist content details when requested and returned
- `status`: Playlist status fields when requested and returned
- `player`: Playlist player fields when requested and returned
- `localizations`: Playlist localization fields when requested and returned
- `other_returned_fields`: Any additional upstream fields returned for selected parts and supported by the shared result convention

**Validation Rules**:
- Returned fields depend on selected parts and upstream availability
- Missing optional fields must not be fabricated
- Playlist item, playlist image, video, channel, transcript, analytics, recommendation, ranking, summarization, and enrichment data must not be invented by this tool

## Playlists List Result

**Purpose**: Successful result for a `playlists_list` call.

**Fields**:
- `endpoint`: Expected to be `playlists.list`
- `quotaCost`: Expected to be `1`
- `requestedParts`: Parsed part-selection context
- `selector`: Active selector name and safe value context
- `auth`: Safe access mode context
- `pagination`: Pagination Context when applicable
- `items`: Returned playlist resources, possibly empty
- `empty`: Whether the result is a successful empty collection

**Validation Rules**:
- Must distinguish successful populated collections from successful empty collections
- Must preserve selected part, selector, pagination, quota, access, and endpoint context
- Must not expose credentials, raw upstream diagnostics, stack traces, or unsafe request context

## Playlists List Failure

**Purpose**: Caller-facing failure for invalid, ineligible, or unsuccessful playlist list requests.

**Fields**:
- `category`: Safe failure category such as invalid request, authentication failure, authorization failure, quota exhausted, resource not found, upstream unavailable, deprecated behavior, or unexpected upstream failure
- `message`: Caller-actionable summary
- `details`: Sanitized field or selector context

**Validation Rules**:
- Must distinguish local validation failures from access failures and upstream failures
- Must sanitize credential material, stack traces, raw upstream bodies, and unsafe diagnostics
- Must identify the invalid field or selector when doing so is safe
- Must preserve empty successful collections as success rather than failure

## State Transitions

1. Caller submits request.
2. Tool validates required `part` and exactly one selector.
3. Tool validates selector-specific paging and access requirements.
4. Tool executes the existing Layer 1 `playlists.list` wrapper once for valid requests.
5. Successful upstream result maps to Playlists List Result.
6. Empty successful upstream result maps to Playlists List Result with empty collection context.
7. Local validation, access, quota, missing-resource, unavailable-service, deprecated, or unexpected upstream failures map to Playlists List Failure.
