# Data Model: YT-107 Layer 1 Endpoint `captions.download`

## Entity: Caption Download Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `captions.download` in a way that exposes endpoint identity, quota cost, supported download inputs, permission expectations, format and translation guidance, and delegation notes before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `captions`
- `operation_name`: Upstream operation name, expected to remain `download`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `200`
- `notes`: Maintainer-facing notes for permission expectations, translation options, format-conversion guidance, and delegation behavior

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if permission, translation, format-conversion, or delegation notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Caption Download Request`
- References one `Download Access Expectation`
- Produces one `Caption Download Result`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Caption Download Request

**Purpose**: Represents one supported `captions.download` request shape that identifies a caption track and optionally asks for a translated or reformatted download.

**Fields**:

- `caption_track_id`: Stable identifier for the caption track being downloaded
- `download_format`: Optional requested output format
- `translation_language`: Optional requested output language
- `delegation_context`: Optional content-owner delegation context when authorized use requires it
- `request_mode`: Maintainer-facing label that distinguishes a base download from a formatted or translated download

**Validation Rules**:

- A supported download request must include one caption track identifier
- `download_format` is optional and must remain within the supported download contract
- `translation_language` is optional and must remain within the supported download contract
- Unexpected request fields must be rejected or clearly flagged before execution
- Delegation context must remain optional and must not replace the base OAuth requirement

**Relationships**:

- Belongs to one `Caption Download Wrapper Contract`
- Requires one `Download Access Expectation`
- Produces one `Caption Download Result`

## Entity: Download Access Expectation

**Purpose**: Describes the credential, permission, and delegation requirements for one `captions.download` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `permission_note`: Maintainer-facing explanation of edit-permission-sensitive behavior
- `delegation_input`: Optional delegated content-owner field visible to maintainers
- `failure_boundary`: The expected distinction between inaccessible and nonexistent caption tracks

**Validation Rules**:

- Supported `captions.download` paths must require authorized access
- Permission guidance must stay visible even when OAuth access is already present
- Delegation guidance must remain distinguishable from the base auth requirement
- Credential payloads must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Caption Download Wrapper Contract`
- Referenced by download-request semantics and implementation tests

## Entity: Caption Download Result

**Purpose**: Represents the successful outcome of a valid `captions.download` request.

**Fields**:

- `caption_content`: Downloaded caption body returned for the requested track
- `content_format`: The effective output format of the returned content
- `content_language`: The effective language of the returned content
- `caption_track_id`: Stable identifier for the downloaded caption track
- `delegation_context_present`: Whether delegated content-owner context was supplied
- `metadata_visibility`: Whether quota, auth, and option guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid download request must end as either downloaded caption content or a normalized upstream failure
- Result handling must keep quota and source-operation visibility available to higher layers
- Successful download handling must not blur inaccessible-track failures into missing-track outcomes

**Relationships**:

- Returned by one `Caption Download Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but permission or output-option guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, supported download inputs, and delegation notes are visible together
3. `validated`: Unit, contract, integration, and transport checks prove identifier validation, OAuth-only guidance, option visibility, and result handling
4. `reusable`: Later transcript and caption-delivery work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported download-request shape
2. Wrapper validates the required caption track identifier, optional translation and format inputs, allowed delegation input, and unexpected-field rejection
3. Shared executor runs with authorized access for the validated download request
4. Request ends as either `downloaded caption content`, `normalized access-denied failure`, or `normalized not-found failure`
