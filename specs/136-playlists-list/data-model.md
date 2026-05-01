# Data Model: YT-136 Layer 1 Endpoint `playlists.list`

## Entity: Playlists List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `playlists.list` so maintainers can review endpoint identity, quota cost, selector-aware auth expectations, filter boundaries, paging rules, and result interpretation before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `playlists`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields, selector rules, and endpoint-specific validators for one playlist lookup
- `auth_mode`: Stable auth mode for this wrapper, expected to remain conditional auth for this slice
- `auth_condition_note`: Maintainer-facing explanation of which filter modes use API-key access and which use OAuth-backed access
- `quota_cost`: Official quota-unit cost of `1`
- `notes`: Maintainer-facing notes covering required `part`, filter rules, paging boundaries, unsupported modifiers, and empty-result interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as conditional auth with clear per-filter guidance
- Contract notes must keep filter rules, paging boundaries, and unsupported modifier guidance reviewable

**Relationships**:

- Uses one `Playlists List Request`
- Applies one `Playlist Filter Mode`
- Produces one `Playlists List Result`

## Entity: Playlists List Request

**Purpose**: Represents one supported `playlists.list` request.

**Fields**:

- `part`: Requested response sections for one retrieval attempt
- `channelId`: Channel-scoped selector for one playlist retrieval path
- `id`: Direct playlist identifier selector for one retrieval path
- `mine`: Owner-scoped selector for one user-owned playlist retrieval path
- `pageToken`: Optional continuation input when the selected filter mode supports paging
- `maxResults`: Optional page-size input when the selected filter mode supports paging

**Validation Rules**:

- Every supported request must include one non-empty `part` value
- Exactly one selector from `channelId`, `id`, or `mine` must be present
- `pageToken` and `maxResults` are allowed only when the selected filter mode supports paging
- No undocumented top-level request fields may be accepted for this slice

**Relationships**:

- Requires one `Playlist Filter Mode`
- Produces one `Playlists List Result`

## Entity: Playlist Filter Mode

**Purpose**: Captures the supported filter mode used to retrieve playlists and the rules attached to that mode.

**Fields**:

- `selector_name`: Expected to be one of `channelId`, `id`, or `mine`
- `selector_value`: The lookup value supplied for the chosen selector, or a stable owner-scoped marker for `mine`
- `paging_supported`: Boolean indicator showing whether `pageToken` and `maxResults` are allowed
- `required_auth_mode`: Required access path for the chosen selector
- `unsupported_modifier_policy`: Explicit statement that undocumented modifiers are unsupported in this slice

**Validation Rules**:

- `selector_name` must identify exactly one supported selector
- `channelId`, `id`, and `mine` modes must remain distinguishable in review surfaces
- Paging support must stay explicit rather than implicit
- Auth expectations must remain visible for all supported modes

**Relationships**:

- Applied to one `Playlists List Request`
- Interpreted alongside one `Playlists List Result`

## Entity: Playlist Resource

**Purpose**: Represents one returned playlist record that downstream layers can inspect to understand playlist identity and ownership context for one supported lookup.

**Fields**:

- `playlist_id`: Stable identifier for one playlist
- `channel_id`: Channel identity associated with the playlist when returned
- `title_summary`: Returned playlist title or display summary preserved from the upstream resource when requested
- `description_summary`: Returned playlist description summary when available
- `source_selector`: The filter mode used to retrieve the resource

**Validation Rules**:

- Returned playlist resources must remain tied to the selected lookup mode
- Resource interpretation must preserve the selector context of the endpoint
- Empty item sets must remain distinguishable from invalid request and access-related failures

**Relationships**:

- Returned within one `Playlists List Result`
- Interpreted alongside one `Playlist Filter Mode`

## Entity: Playlists List Result

**Purpose**: Represents normalized output for one valid `playlists.list` request.

**Fields**:

- `items`: Returned playlist records for the request
- `part`: Stable retrieval input echoed for review and downstream mapping
- `selector_name`: Stable selector identifier echoed for review and downstream mapping
- `selector_value`: Stable lookup value echoed for review and downstream mapping
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with one or more playlists or success with zero playlists

**Validation Rules**:

- Valid requests must produce a successful retrieval result even when `items` is empty
- Result handling must preserve source operation, quota visibility, auth guidance, and selector context needed by higher layers
- Invalid requests must remain distinct from access-related failures and valid success outcomes

**Relationships**:

- Produced by one `Playlists List Wrapper Contract`
- Contains zero or more `Playlist Resource` records
- Governed by one `Playlist Filter Mode`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but filter rules, auth guidance, or paging behavior are incomplete
2. `reviewable`: Quota, selector-aware auth expectations, filter rules, and paging boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm request and result behavior
4. `reusable`: Higher-layer authors can judge whether to reuse the wrapper without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one `playlists.list` request with required `part`
2. Wrapper validates that exactly one supported selector is present
3. Selector-specific paging rules and unsupported modifiers are evaluated before execution
4. Auth compatibility is evaluated for the selected filter mode before execution
5. Shared executor performs the retrieval for valid requests
6. Outcome ends as `successful retrieval with items`, `successful retrieval with no matches`, `normalized invalid_request`, or `normalized access_failure`
