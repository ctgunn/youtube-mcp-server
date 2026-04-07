# Data Model: YT-106 Layer 1 Endpoint `captions.update`

## Entity: Caption Update Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `captions.update` in a way that exposes endpoint identity, quota cost, supported update inputs, authorization expectations, media-update guidance, and delegation notes before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `captions`
- `operation_name`: Upstream operation name, expected to remain `update`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `450`
- `notes`: Optional maintainer-facing notes for media-update behavior, delegation guidance, or update-result interpretation
- `delegation_note`: Maintainer-facing explanation of when `onBehalfOfContentOwner` is supported

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if update-body requirements, media-update expectations, or delegation notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Caption Update Request`
- References one `Authorization Expectation`
- Produces one `Updated Caption Resource`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Caption Update Request

**Purpose**: Represents one supported `captions.update` request shape that combines reviewable caption resource updates with either a body-only update mode or an optional body-plus-media replacement mode.

**Fields**:

- `part`: Requested resource parts or write scope for the update call
- `body`: Caption resource payload that identifies what is being updated
- `media`: Optional caption content payload submitted when the update replaces caption content
- `delegation_context`: Optional content-owner delegation context when authorized use requires it
- `request_mode`: Maintainer-facing label that distinguishes a body-only update from a body-plus-media replacement update

**Validation Rules**:

- A supported update request must include `part` and one stable `body` payload
- `media` is optional and must only appear on otherwise valid update requests
- `media` without `body` is invalid
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- Delegation context must remain optional and must not replace the base OAuth requirement

**Relationships**:

- Belongs to one `Caption Update Wrapper Contract`
- Requires one `Authorization Expectation`
- Produces one `Updated Caption Resource`

## Entity: Authorization Expectation

**Purpose**: Describes the credential and delegation requirement for one `captions.update` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `delegation_input`: Optional delegated content-owner field visible to maintainers
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `captions.update` paths must require authorized access
- Delegation guidance must remain distinguishable from the base auth requirement
- Credential payloads must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Caption Update Wrapper Contract`
- Referenced by update-request semantics and implementation tests

## Entity: Updated Caption Resource

**Purpose**: Represents the successful outcome of a valid `captions.update` request.

**Fields**:

- `resource_id`: Stable identifier for the updated caption track
- `resource_parts`: The updated caption fields returned for the requested parts
- `update_state`: Successful update state visible to higher layers
- `request_mode`: The validated update-request mode used for the call
- `delegation_context_present`: Whether delegated content-owner context was supplied
- `metadata_visibility`: Whether quota, auth, and media-update guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid update request must end as either an updated-resource success or a normalized upstream failure
- Successful update must not erase the wrapper's documented auth, media, or delegation context
- Result handling must keep quota and source-operation visibility available to higher layers

**Relationships**:

- Returned by one `Caption Update Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but media-update guidance or delegation notes may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, supported update inputs, and delegation notes are visible together
3. `validated`: Unit, contract, integration, and transport checks prove body-required validation, OAuth-only guidance, delegation visibility, and updated-resource handling
4. `reusable`: Later caption-management work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported update-request shape
2. Wrapper validates required body input, optional media input, allowed delegation input, and unexpected-field rejection
3. Shared executor runs with authorized access for the validated update request
4. Request ends as either `updated resource` or `normalized upstream failure`
