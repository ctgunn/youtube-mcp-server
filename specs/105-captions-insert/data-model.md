# Data Model: YT-105 Layer 1 Endpoint `captions.insert`

## Entity: Caption Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `captions.insert` in a way that exposes endpoint identity, quota cost, supported creation inputs, authorization expectations, upload guidance, and delegation notes before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `captions`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `400`
- `notes`: Optional maintainer-facing notes for upload behavior, delegation guidance, or creation-result interpretation
- `delegation_note`: Maintainer-facing explanation of when `onBehalfOfContentOwner` is supported

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if upload requirements, minimum creation inputs, or delegation notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Caption Creation Request`
- References one `Authorization Expectation`
- Produces one `Created Caption Resource`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Caption Creation Request

**Purpose**: Represents one supported `captions.insert` request shape that combines reviewable metadata with upload content for caption creation.

**Fields**:

- `part`: Requested resource parts or write scope for the creation call
- `body`: Caption metadata payload that identifies what is being created
- `media`: Caption content payload submitted for the creation request
- `delegation_context`: Optional content-owner delegation context when authorized use requires it
- `request_mode`: Maintainer-facing label that distinguishes a valid create request from unsupported incomplete shapes

**Validation Rules**:

- A supported creation request must include `part`, one stable `body` metadata field, and one stable `media` upload field
- Metadata-only requests are invalid
- Upload-only requests are invalid
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- Delegation context must remain optional and must not replace the base OAuth requirement

**Relationships**:

- Belongs to one `Caption Insert Wrapper Contract`
- Requires one `Authorization Expectation`
- Produces one `Created Caption Resource`

## Entity: Authorization Expectation

**Purpose**: Describes the credential and delegation requirement for one `captions.insert` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `delegation_input`: Optional delegated content-owner field visible to maintainers
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `captions.insert` paths must require authorized access
- Delegation guidance must remain distinguishable from the base auth requirement
- Credential payloads must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Caption Insert Wrapper Contract`
- Referenced by creation-request semantics and implementation tests

## Entity: Created Caption Resource

**Purpose**: Represents the successful outcome of a valid `captions.insert` request.

**Fields**:

- `resource_id`: Stable identifier for the created caption track
- `resource_parts`: The created caption fields returned for the requested parts
- `creation_state`: Successful creation state visible to higher layers
- `request_mode`: The validated creation-request mode used for the call
- `delegation_context_present`: Whether delegated content-owner context was supplied
- `metadata_visibility`: Whether quota, auth, and upload guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid create request must end as either a created-resource success or a normalized upstream failure
- Successful creation must not erase the wrapper's documented auth, upload, or delegation context
- Result handling must keep quota and source-operation visibility available to higher layers

**Relationships**:

- Returned by one `Caption Insert Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but upload guidance or delegation notes may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, supported creation inputs, and delegation notes are visible together
3. `validated`: Unit, contract, integration, and transport checks prove metadata-plus-upload validation, OAuth-only guidance, delegation visibility, and created-resource handling
4. `reusable`: Later caption-management work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported create-request shape
2. Wrapper validates required metadata, required upload input, allowed delegation input, and unexpected-field rejection
3. Shared executor runs with authorized access for the validated creation request
4. Request ends as either `created resource` or `normalized upstream failure`
