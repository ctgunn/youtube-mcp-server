# Data Model: YT-109 Layer 1 Endpoint `channelBanners.insert`

## Entity: Channel Banner Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `channelBanners.insert` in a way that exposes endpoint identity, quota cost, supported upload inputs, authorization expectations, image constraints, delegation guidance, and response-URL behavior before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `channelBanners`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes for image constraints, response-URL behavior, and optional delegation guidance

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if image constraints, response-URL guidance, or delegation notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Channel Banner Upload Request`
- References one `Banner Upload Access Expectation`
- Produces one `Channel Banner Upload Result`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Channel Banner Upload Request

**Purpose**: Represents one supported `channelBanners.insert` request shape that uploads banner artwork for later application to a managed channel.

**Fields**:

- `media`: Banner upload payload including the binary content and MIME type
- `delegation_context`: Optional content-owner delegation context when authorized use requires it
- `request_mode`: Maintainer-facing label that distinguishes a valid upload request from unsupported incomplete shapes

**Validation Rules**:

- A supported upload request must include one `media` payload
- The `media` payload must remain reviewable for accepted MIME types and file-size guidance
- Requests must not include a JSON resource body for this endpoint
- Unexpected request fields must be rejected or clearly flagged before execution
- Delegation context must remain optional and must not replace the base OAuth requirement

**Relationships**:

- Belongs to one `Channel Banner Insert Wrapper Contract`
- Requires one `Banner Upload Access Expectation`
- Produces one `Channel Banner Upload Result`

## Entity: Banner Upload Access Expectation

**Purpose**: Describes the credential, image-constraint, and delegation requirements for one `channelBanners.insert` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `upload_constraints`: Reviewable guidance for aspect ratio, minimum resolution, recommended resolution, file size, and supported MIME types
- `delegation_input`: Optional delegated content-owner field visible to maintainers
- `failure_boundary`: The expected distinction between `auth`, `invalid_request`, and `target_channel` failures

**Validation Rules**:

- Supported `channelBanners.insert` paths must require authorized access
- Upload constraints must stay visible even when the wrapper reuses generic media-upload helpers
- Delegation guidance must remain distinguishable from the base auth requirement
- Credential payloads and raw binary media content must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Channel Banner Insert Wrapper Contract`
- Referenced by upload-request semantics and implementation tests

## Entity: Channel Banner Upload Result

**Purpose**: Represents the successful outcome of a valid `channelBanners.insert` request.

**Fields**:

- `banner_url`: Reviewable URL returned by the endpoint for follow-on channel-branding updates
- `is_uploaded`: Whether the banner upload completed successfully
- `delegation_context_present`: Whether delegated content-owner context was supplied
- `source_operation`: Stable identifier of the wrapper operation that produced the result
- `metadata_visibility`: Whether quota, auth, upload, and response-URL guidance remain attached to the wrapper rather than being lost after execution

**Validation Rules**:

- A valid upload request must end as either a banner-upload success with a returned URL or a normalized upstream failure
- Successful upload handling must keep the returned URL visible for later `channels.update` planning
- Result handling must keep quota and source-operation visibility available to higher layers
- Successful upload handling must not blur access-related failures into invalid-upload or target-channel failures

**Relationships**:

- Returned by one `Channel Banner Insert Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but upload constraints, response-URL behavior, or delegation guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, supported upload inputs, response-URL behavior, and delegation notes are visible together
3. `validated`: Unit, contract, integration, and transport checks prove upload validation, OAuth-only guidance, response-URL handling, and failure-boundary visibility
4. `reusable`: Later channel-branding work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported banner-upload request shape
2. Wrapper validates the required `media` payload, optional delegation input, and unexpected-field rejection
3. Shared executor runs with authorized access for the validated upload request
4. Request ends as either `uploaded with banner URL`, `normalized auth failure`, `normalized invalid_request failure`, or `normalized target_channel failure`
