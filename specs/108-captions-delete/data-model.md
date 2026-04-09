# Data Model: YT-108 Layer 1 Endpoint `captions.delete`

## Entity: Caption Delete Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `captions.delete` in a way that exposes endpoint identity, quota cost, supported delete inputs, ownership expectations, delegation guidance, and delete-failure boundaries before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `captions`
- `operation_name`: Upstream operation name, expected to remain `delete`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes for ownership expectations and delegation behavior

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if ownership or delegation notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Caption Delete Request`
- References one `Delete Access Expectation`
- Produces one `Caption Delete Result`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Caption Delete Request

**Purpose**: Represents one supported `captions.delete` request shape that targets a single caption track for deletion.

**Fields**:

- `caption_track_id`: Stable identifier for the caption track being deleted
- `delegation_context`: Optional content-owner delegation context when authorized use requires it
- `request_mode`: Maintainer-facing label that distinguishes a direct delete from a delegated delete

**Validation Rules**:

- A supported delete request must include one caption track identifier
- Unexpected request fields must be rejected or clearly flagged before execution
- Delegation context must remain optional and must not replace the base OAuth requirement
- Bulk deletion and selector-style list inputs are outside the promised wrapper contract

**Relationships**:

- Belongs to one `Caption Delete Wrapper Contract`
- Requires one `Delete Access Expectation`
- Produces one `Caption Delete Result`

## Entity: Delete Access Expectation

**Purpose**: Describes the credential, ownership, and delegation requirements for one `captions.delete` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `ownership_note`: Maintainer-facing explanation of delete-sensitive ownership behavior
- `delegation_input`: Optional delegated content-owner field visible to maintainers
- `failure_boundary`: The expected distinction between inaccessible and nonexistent caption tracks

**Validation Rules**:

- Supported `captions.delete` paths must require authorized access
- Ownership guidance must stay visible even when OAuth access is already present
- Delegation guidance must remain distinguishable from the base auth requirement
- Credential payloads must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Caption Delete Wrapper Contract`
- Referenced by delete-request semantics and implementation tests

## Entity: Caption Delete Result

**Purpose**: Represents the successful outcome of a valid `captions.delete` request.

**Fields**:

- `caption_track_id`: Stable identifier for the caption track the caller attempted to delete
- `is_deleted`: Whether the delete operation completed successfully
- `delegation_context_present`: Whether delegated content-owner context was supplied
- `metadata_visibility`: Whether quota, auth, and ownership guidance remain attached to the wrapper rather than being lost after execution

**Validation Rules**:

- A valid delete request must end as either a confirmed delete outcome or a normalized upstream failure
- Result handling must keep quota and source-operation visibility available to higher layers
- Successful delete handling must not blur access-related failures into missing-target outcomes

**Relationships**:

- Returned by one `Caption Delete Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but ownership or delegation guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, delete input boundary, and delegation notes are visible together
3. `validated`: Unit, contract, integration, and transport checks prove identifier validation, OAuth-only guidance, ownership visibility, and delete-result handling
4. `reusable`: Later caption-management work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported delete-request shape
2. Wrapper validates the required caption track identifier, optional delegation input, and unexpected-field rejection
3. Shared executor runs with authorized access for the validated delete request
4. Request ends as either `deleted`, `normalized access-denied failure`, or `normalized not-found failure`
