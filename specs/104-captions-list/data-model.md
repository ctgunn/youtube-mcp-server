# Data Model: YT-104 Layer 1 Endpoint `captions.list`

## Entity: Caption List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `captions.list` in a way that exposes endpoint identity, quota cost, supported selectors, authorization expectations, and delegation guidance before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `captions`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Optional maintainer-facing notes for selector or response interpretation
- `delegation_note`: Maintainer-facing explanation of when `onBehalfOfContentOwner` is supported

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if selector scope or delegation notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Caption Selector Mode Set`
- References one `Authorization Expectation`
- Produces one `Caption Track Collection Result`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Caption Selector Mode

**Purpose**: Represents one supported request-selection path for `captions.list`.

**Fields**:

- `mode_name`: Human-readable label for the selector path
- `request_fields`: Fields used to select that path
- `description`: Maintainer-facing explanation of when to use the mode
- `supported`: Whether the selector mode is in scope for YT-104
- `delegation_allowed`: Whether `onBehalfOfContentOwner` may accompany the selector mode

**Validation Rules**:

- Each supported mode must map to one clear request intent
- Supported modes must be mutually exclusive for a single request
- Unsupported or ambiguous combinations must be rejected or clearly flagged before execution
- The initial supported selector profiles for this slice are `videoId` and `id`

**Relationships**:

- Belongs to one `Caption List Wrapper Contract`
- Informs one `Authorization Expectation`

## Entity: Authorization Expectation

**Purpose**: Describes the credential and delegation requirement for one `captions.list` request path.

**Fields**:

- `auth_mode`: The runtime auth selection compatible with the endpoint
- `requires_authorized_access`: Whether the request needs authorized access
- `delegation_input`: Optional delegated content-owner field visible to maintainers
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `captions.list` paths must require authorized access
- Delegation guidance must remain distinguishable from the base auth requirement
- Credential payloads must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Caption List Wrapper Contract`
- Referenced by selector semantics and implementation tests

## Entity: Caption Track Collection Result

**Purpose**: Represents the successful outcome of a valid `captions.list` request, including the case where no caption tracks are returned.

**Fields**:

- `items`: Returned caption-track records, which may be empty
- `result_state`: Non-empty or empty-success
- `request_mode`: Selector mode used for the request
- `delegation_context_present`: Whether delegated content-owner context was supplied
- `metadata_visibility`: Whether quota and auth guidance remain attached to the wrapper rather than the result payload

**Validation Rules**:

- An empty `items` collection is valid when the request itself is valid
- Empty-success must not be normalized into an upstream error
- Result handling must not erase the wrapper's documented auth, selector, or delegation context

**Relationships**:

- Returned by one `Caption List Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but selector scope or delegation guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, supported selector paths, and delegation notes are visible together
3. `validated`: Unit, contract, integration, and transport checks prove selector exclusivity, OAuth-only guidance, delegation visibility, and empty-success handling
4. `reusable`: Later transcript and caption-management work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller selects one supported selector mode
2. Wrapper validates required fields, selector exclusivity, and allowed delegation input
3. Shared executor runs with authorized access for the selected request
4. Request ends as either `success with items`, `success with empty items`, or `normalized upstream failure`
