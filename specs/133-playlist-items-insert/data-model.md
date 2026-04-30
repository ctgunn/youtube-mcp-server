# Data Model: YT-133 Layer 1 Endpoint `playlistItems.insert`

## Entity: Playlist Items Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `playlistItems.insert` in a way that exposes endpoint identity, quota cost, supported writable inputs, authorization expectations, optional-field boundaries, and normalized outcome rules before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `playlistItems`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes for writable-part guidance, playlist/video assignment requirements, optional-field boundaries, and normalized outcome interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if required create inputs or writable-boundary notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Playlist Item Creation Request`
- References one `Writable Access Expectation`
- Produces one `Created Playlist Item Resource`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Playlist Item Creation Request

**Purpose**: Represents one supported `playlistItems.insert` request shape that combines reviewable writable metadata with the playlist/video assignment needed to create a playlist item.

**Fields**:

- `part`: Requested writable part or return scope for the creation call
- `body`: Playlist-item metadata payload that identifies what is being created
- `body.snippet.playlistId`: Target playlist identifier for the inserted item
- `body.snippet.resourceId`: Referenced resource mapping used to identify the video to add
- `body.snippet.position`: Optional placement field that is supported only when the wrapper explicitly documents it
- `body.contentDetails`: Optional content-details mapping that is supported only when the wrapper explicitly documents it
- `request_mode`: Maintainer-facing label that distinguishes a valid create request from unsupported incomplete shapes
- `unsupported_fields_policy`: Explicit statement that undocumented top-level or nested request fields are outside this feature's promised contract

**Validation Rules**:

- A supported creation request must include `part` and one stable `body` mapping with the required writable `snippet`
- `body.snippet.playlistId` is required
- `body.snippet.resourceId` is required
- Requests missing the target playlist or referenced resource are invalid
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- Optional placement or content-details fields must either be explicitly documented as supported or clearly treated as outside the guaranteed contract
- The request contract must remain deterministic and must not silently rewrite incomplete input into supported behavior

**Relationships**:

- Belongs to one `Playlist Items Insert Wrapper Contract`
- Requires one `Writable Access Expectation`
- Produces one `Created Playlist Item Resource`

## Entity: Writable Access Expectation

**Purpose**: Describes the credential and writable-boundary requirement for one `playlistItems.insert` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `required_writable_part`: Maintainer-facing note identifying the supported writable part
- `required_playlist_input`: Maintainer-facing note identifying the required target playlist input
- `required_resource_input`: Maintainer-facing note identifying the required referenced resource input
- `optional_fields_policy`: Explanation of how placement and content-details inputs are treated
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `playlistItems.insert` paths must require authorized access
- Required writable inputs must remain distinguishable in review surfaces
- Credential payloads must never be exposed in contract artifacts or documentation
- Optional writable inputs must not appear supported implicitly

**Relationships**:

- Applied to one `Playlist Items Insert Wrapper Contract`
- Referenced by creation-request semantics and implementation tests

## Entity: Created Playlist Item Resource

**Purpose**: Represents the successful outcome of a valid `playlistItems.insert` request.

**Fields**:

- `resource_id`: Stable identifier for the created playlist item
- `resource_parts`: The created playlist-item fields returned for the requested parts
- `creation_state`: Successful creation state visible to higher layers
- `request_mode`: The validated creation-request mode used for the call
- `source_operation`: Stable source-operation identifier preserved for review and downstream mapping
- `metadata_visibility`: Whether quota, auth, and writable-boundary guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid create request must end as either a created-resource success or a normalized upstream failure
- Successful creation must not erase the wrapper's documented auth, quota, or writable-boundary context
- Result handling must keep source operation and request-mode visibility available to higher layers

**Relationships**:

- Returned by one `Playlist Items Insert Wrapper Contract`
- Produced through the shared executor success path

## Entity: Insert Failure Outcome

**Purpose**: Represents one normalized non-success outcome from a `playlistItems.insert` request so downstream callers can distinguish what type of remediation is needed.

**Fields**:

- `category`: Stable failure category such as invalid request, access-related failure, or upstream create rejection
- `reason`: Maintainer-visible explanation of what failed
- `request_mode`: The create-request mode that triggered the failure, when known
- `source_operation`: Stable endpoint identifier preserved for diagnostics
- `retryability`: Whether the failure suggests caller correction, access correction, or upstream-side retry

**Validation Rules**:

- Local validation failures must remain distinct from access failures
- Access failures must remain distinct from upstream create rejections after execution begins
- The failure model must be reviewable enough that later layers can decide whether to fix input, change authorization, or surface the upstream rejection

**Relationships**:

- May be produced instead of one `Created Playlist Item Resource`
- Shares wrapper metadata and request context with the `Playlist Items Insert Wrapper Contract`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but writable-part or create-input guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, and required create inputs are visible together
3. `validated`: Unit, contract, integration, and transport checks prove writable-input validation, OAuth-only guidance, and created-resource handling
4. `reusable`: Later playlist-item work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported create-request shape
2. Wrapper validates required writable fields and unexpected-field rejection
3. OAuth eligibility is evaluated before execution
4. Shared executor runs with authorized access for the validated creation request
5. Request ends as either `created resource`, `normalized invalid_request`, `normalized access_failure`, or `normalized upstream create failure`
