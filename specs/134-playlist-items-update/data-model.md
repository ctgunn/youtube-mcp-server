# Data Model: YT-134 Layer 1 Endpoint `playlistItems.update`

## Entity: Playlist Items Update Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `playlistItems.update` in a way that exposes endpoint identity, quota cost, supported update inputs, authorization expectations, writable-field boundaries, and normalized outcome rules before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `playlistItems`
- `operation_name`: Upstream operation name, expected to remain `update`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes for identifier requirements, supported writable fields, optional-field boundaries, and normalized outcome interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if required update inputs or writable-boundary notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Playlist Item Update Request`
- References one `Writable Playlist Item Field Set`
- Produces one `Updated Playlist Item Resource`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Playlist Item Update Request

**Purpose**: Represents one supported `playlistItems.update` request shape that combines reviewable identifying metadata with the writable playlist-item data needed to update an existing playlist item.

**Fields**:

- `part`: Requested writable part or return scope for the update call
- `body`: Playlist-item metadata payload that identifies what is being updated
- `body.id`: Existing playlist-item identifier for the target update
- `body.snippet`: Writable playlist-item metadata payload supported by this slice
- `body.snippet.playlistId`: Target playlist identifier preserved for the updated item
- `body.snippet.resourceId`: Referenced resource mapping used to identify the associated video
- `body.snippet.resourceId.videoId`: Referenced video identifier preserved for the update
- `body.snippet.position`: Optional placement field that is supported only when the wrapper explicitly documents it
- `request_mode`: Maintainer-facing label that distinguishes a valid update request from unsupported incomplete shapes
- `unsupported_fields_policy`: Explicit statement that undocumented top-level or nested request fields are outside this feature's promised contract

**Validation Rules**:

- A supported update request must include `part` and one stable `body` mapping with the required target identifier
- `body.id` is required
- `body.snippet` is required
- `body.snippet.playlistId` is required
- `body.snippet.resourceId.videoId` is required
- Requests missing the target playlist item, playlist context, or referenced video context are invalid
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- Optional placement or other writable fields must either be explicitly documented as supported or clearly treated as outside the guaranteed contract
- The request contract must remain deterministic and must not silently rewrite incomplete input into supported behavior

**Relationships**:

- Belongs to one `Playlist Items Update Wrapper Contract`
- Uses one `Writable Playlist Item Field Set`
- Produces one `Updated Playlist Item Resource`

## Entity: Writable Playlist Item Field Set

**Purpose**: Describes the writable update boundary for one `playlistItems.update` request so maintainers can tell which nested playlist-item fields are guaranteed for this slice and which are intentionally out of scope.

**Fields**:

- `required_part`: Maintainer-facing note identifying the supported writable part
- `required_identifier_field`: Maintainer-facing note identifying the required playlist-item identifier
- `required_playlist_field`: Maintainer-facing note identifying the required playlist context
- `required_resource_field`: Maintainer-facing note identifying the required referenced video context
- `supported_fields`: Explicit list of writable fields guaranteed by this slice
- `unsupported_fields_policy`: Explanation of how unsupported writable fields are treated
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `playlistItems.update` paths must require authorized access
- Required identifier and writable fields must remain distinguishable in review surfaces
- Unsupported writable fields must not appear supported implicitly
- Credentials and secret-backed values must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Playlist Items Update Wrapper Contract`
- Referenced by update-request semantics and implementation tests

## Entity: Updated Playlist Item Resource

**Purpose**: Represents the successful outcome of a valid `playlistItems.update` request.

**Fields**:

- `resource_id`: Stable identifier for the updated playlist item
- `resource_parts`: The updated playlist-item fields returned for the requested parts
- `update_state`: Successful update state visible to higher layers
- `request_mode`: The validated update-request mode used for the call
- `source_operation`: Stable source-operation identifier preserved for review and downstream mapping
- `playlist_id`: Preserved playlist context for the updated playlist item
- `video_id`: Preserved referenced-video context for the updated playlist item
- `metadata_visibility`: Whether quota, auth, and writable-boundary guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid update request must end as either an updated-resource success or a normalized upstream failure
- Successful update must not erase the wrapper's documented auth, quota, or writable-boundary context
- Result handling must keep source operation, playlist context, and request-mode visibility available to higher layers

**Relationships**:

- Returned by one `Playlist Items Update Wrapper Contract`
- Produced through the shared executor success path

## Entity: Update Failure Outcome

**Purpose**: Represents one normalized non-success outcome from a `playlistItems.update` request so downstream callers can distinguish what type of remediation is needed.

**Fields**:

- `category`: Stable failure category such as invalid request, access-related failure, or upstream update rejection
- `reason`: Maintainer-visible explanation of what failed
- `request_mode`: The update-request mode that triggered the failure, when known
- `source_operation`: Stable endpoint identifier preserved for diagnostics
- `retryability`: Whether the failure suggests caller correction, access correction, or upstream-side retry

**Validation Rules**:

- Local validation failures must remain distinct from access failures
- Access failures must remain distinct from upstream update rejections after execution begins
- The failure model must be reviewable enough that later layers can decide whether to fix input, change authorization, or surface the upstream rejection

**Relationships**:

- May be produced instead of one `Updated Playlist Item Resource`
- Shares wrapper metadata and request context with the `Playlist Items Update Wrapper Contract`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but writable-field or update-input guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, and required update inputs are visible together
3. `validated`: Unit, contract, integration, and transport checks prove identifier validation, writable-boundary guidance, OAuth-only guidance, and updated-resource handling
4. `reusable`: Later playlist-item work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported update-request shape
2. Wrapper validates required identifier and writable fields plus unexpected-field rejection
3. OAuth eligibility is evaluated before execution
4. Shared executor runs with authorized access for the validated update request
5. Request ends as either `updated resource`, `normalized invalid_request`, `normalized access_failure`, or `normalized upstream update failure`
