# Data Model: YT-132 Layer 1 Endpoint `playlistItems.list`

## Entity: Playlist Items List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `playlistItems.list` so maintainers can review endpoint identity, quota cost, API-key access expectations, selector boundaries, paging rules, and result interpretation before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `playlistItems`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields, selector rules, and endpoint-specific validators for one playlist-item lookup
- `auth_mode`: Stable auth mode for this wrapper, expected to remain API-key access for this slice
- `quota_cost`: Official quota-unit cost of `1`
- `notes`: Maintainer-facing notes covering required `part`, selector rules, paging boundaries, unsupported modifiers, and empty-result interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as API-key access for this feature scope
- Contract notes must keep selector rules, paging boundaries, and unsupported modifier guidance reviewable

**Relationships**:

- Uses one `Playlist Items List Request`
- Applies one `Playlist Item Selector Mode`
- Produces one `Playlist Items List Result`

## Entity: Playlist Items List Request

**Purpose**: Represents one supported `playlistItems.list` request.

**Fields**:

- `part`: Requested response sections for one retrieval attempt
- `playlistId`: Playlist-scoped selector for one playlist-item retrieval path
- `id`: Direct playlist-item identifier selector for one retrieval path
- `pageToken`: Optional continuation input when the selected selector mode supports paging
- `maxResults`: Optional page-size input when the selected selector mode supports paging

**Validation Rules**:

- Every supported request must include one non-empty `part` value
- Exactly one selector from `playlistId` or `id` must be present
- `pageToken` and `maxResults` are allowed only when the selected selector mode supports paging
- No undocumented top-level request fields may be accepted for this slice

**Relationships**:

- Requires one `Playlist Item Selector Mode`
- Produces one `Playlist Items List Result`

## Entity: Playlist Item Selector Mode

**Purpose**: Captures the supported selector mode used to retrieve playlist items and the rules attached to that mode.

**Fields**:

- `selector_name`: Expected to be either `playlistId` or `id`
- `selector_value`: The lookup value supplied for the chosen selector
- `paging_supported`: Boolean indicator showing whether `pageToken` and `maxResults` are allowed
- `api_key_required`: Boolean indicator that supported requests use API-key access in this slice
- `unsupported_modifier_policy`: Explicit statement that undocumented modifiers are unsupported in this slice

**Validation Rules**:

- `selector_name` must identify exactly one supported selector
- `playlistId` mode must remain distinguishable from `id` mode in review surfaces
- Paging support must stay explicit rather than implicit
- API-key expectations must remain visible for all supported modes

**Relationships**:

- Applied to one `Playlist Items List Request`
- Interpreted alongside one `Playlist Items List Result`

## Entity: Playlist Item Resource

**Purpose**: Represents one returned playlist-item record that downstream layers can inspect to understand playlist membership data for one supported lookup.

**Fields**:

- `playlist_item_id`: Stable identifier for one playlist item
- `playlist_id`: Playlist identity associated with the item
- `position`: Returned ordering information for one playlist membership entry
- `snippet_summary`: Returned title, description, or channel details preserved from the upstream resource when requested
- `source_selector`: The selector mode used to retrieve the resource

**Validation Rules**:

- Returned playlist-item resources must remain tied to the selected lookup mode
- Resource interpretation must preserve the selector context of the endpoint
- Empty item sets must remain distinguishable from invalid request and access-related failures

**Relationships**:

- Returned within one `Playlist Items List Result`
- Interpreted alongside one `Playlist Item Selector Mode`

## Entity: Playlist Items List Result

**Purpose**: Represents normalized output for one valid `playlistItems.list` request.

**Fields**:

- `items`: Returned playlist-item records for the request
- `part`: Stable retrieval input echoed for review and downstream mapping
- `selector_name`: Stable selector identifier echoed for review and downstream mapping
- `selector_value`: Stable lookup value echoed for review and downstream mapping
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with one or more items or success with zero items

**Validation Rules**:

- Valid requests must produce a successful retrieval result even when `items` is empty
- Result handling must preserve source operation, quota visibility, and selector context needed by higher layers
- Invalid requests must remain distinct from access-related failures and valid success outcomes

**Relationships**:

- Produced by one `Playlist Items List Wrapper Contract`
- Contains zero or more `Playlist Item Resource` records
- Governed by one `Playlist Item Selector Mode`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but selector rules or paging guidance are incomplete
2. `reviewable`: Quota, API-key expectations, selector rules, and paging boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm request and result behavior
4. `reusable`: Higher-layer authors can judge whether to reuse the wrapper without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one `playlistItems.list` request with required `part`
2. Wrapper validates that exactly one supported selector is present
3. Selector-specific paging rules and unsupported modifiers are evaluated before execution
4. API-key compatibility is evaluated before execution
5. Shared executor performs the retrieval for valid requests
6. Outcome ends as `successful retrieval with items`, `successful retrieval with no matches`, `normalized invalid_request`, or `normalized access_failure`
