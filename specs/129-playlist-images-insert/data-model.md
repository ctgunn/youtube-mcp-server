# Data Model: YT-129 Layer 1 Endpoint `playlistImages.insert`

## Entity: Playlist Images Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `playlistImages.insert` in a way that exposes endpoint identity, quota cost, supported creation inputs, authorization expectations, upload guidance, and normalized outcome boundaries before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `playlistImages`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes for create-input guidance, upload behavior, quota visibility, and normalized outcome interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if required create inputs or upload-boundary notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Playlist Image Creation Request`
- References one `Upload Access Expectation`
- Produces one `Created Playlist Image Resource`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Playlist Image Creation Request

**Purpose**: Represents one supported `playlistImages.insert` request shape that combines reviewable metadata with upload content for playlist-image creation.

**Fields**:

- `part`: Requested resource parts or write scope for the creation call
- `body`: Playlist-image metadata payload that identifies what is being created
- `media`: Playlist-image content payload submitted for the creation request
- `request_mode`: Maintainer-facing label that distinguishes a valid create request from unsupported incomplete shapes
- `unsupported_fields_policy`: Explicit statement that undocumented top-level request fields are outside this feature's promised contract

**Validation Rules**:

- A supported creation request must include `part`, one stable `body` metadata field, and one stable `media` upload field
- Metadata-only requests are invalid
- Upload-only requests are invalid
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- The request contract must remain deterministic and must not silently rewrite incomplete input into supported behavior

**Relationships**:

- Belongs to one `Playlist Images Insert Wrapper Contract`
- Requires one `Upload Access Expectation`
- Produces one `Created Playlist Image Resource`

## Entity: Upload Access Expectation

**Purpose**: Describes the credential and upload-boundary requirement for one `playlistImages.insert` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `required_metadata_input`: Maintainer-facing note identifying the required metadata field
- `required_upload_input`: Maintainer-facing note identifying the required media-upload field
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `playlistImages.insert` paths must require authorized access
- Required metadata and upload inputs must remain distinguishable in review surfaces
- Credential payloads and media content must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Playlist Images Insert Wrapper Contract`
- Referenced by creation-request semantics and implementation tests

## Entity: Created Playlist Image Resource

**Purpose**: Represents the successful outcome of a valid `playlistImages.insert` request.

**Fields**:

- `resource_id`: Stable identifier for the created playlist image
- `resource_parts`: The created playlist-image fields returned for the requested parts
- `creation_state`: Successful creation state visible to higher layers
- `request_mode`: The validated creation-request mode used for the call
- `source_operation`: Stable source-operation identifier preserved for review and downstream mapping
- `metadata_visibility`: Whether quota, auth, and upload guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid create request must end as either a created-resource success or a normalized upstream failure
- Successful creation must not erase the wrapper's documented auth, quota, or upload context
- Result handling must keep source operation and request-mode visibility available to higher layers

**Relationships**:

- Returned by one `Playlist Images Insert Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but create-input or upload guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, and required create inputs are visible together
3. `validated`: Unit, contract, integration, and transport checks prove metadata-plus-upload validation, OAuth-only guidance, and created-resource handling
4. `reusable`: Later playlist-image work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported create-request shape
2. Wrapper validates required metadata, required upload input, and unexpected-field rejection
3. OAuth eligibility is evaluated before execution
4. Shared executor runs with authorized access for the validated creation request
5. Request ends as either `created resource`, `normalized invalid_request`, `normalized access_failure`, or `normalized upstream create failure`
