# Data Model: YT-103 Layer 1 Endpoint `activities.list`

## Entity: Activity List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `activities.list` in a way that exposes endpoint identity, quota cost, supported filters, and authorization expectations before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `activities`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Mixed or conditional auth mode for this endpoint
- `quota_cost`: Official quota-unit cost of `1`
- `auth_condition_note`: Maintainer-facing explanation of when public versus authorized-user access applies
- `notes`: Optional maintainer-facing notes for wrapper interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must expose mixed or conditional semantics rather than hiding the access split in runtime-only behavior
- `auth_condition_note` is required because this endpoint has filter-dependent auth expectations
- The wrapper contract is incomplete if filter scope is not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Activity Filter Mode Set`
- Produces one `Activity Collection Result`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Activity Filter Mode

**Purpose**: Represents one supported request-selection path for `activities.list`.

**Fields**:

- `mode_name`: Human-readable label for the filter path
- `request_fields`: Fields used to select that path
- `access_type`: Public-channel or authorized-user
- `description`: Maintainer-facing explanation of when to use the mode
- `supported`: Whether the filter mode is in scope for YT-103

**Validation Rules**:

- Each supported mode must map to one clear access type
- Supported modes must be mutually exclusive for a single request
- Unsupported or ambiguous combinations must be rejected or clearly flagged before execution

**Relationships**:

- Belongs to one `Activity List Wrapper Contract`
- Informs one `Authorization Expectation`

## Entity: Authorization Expectation

**Purpose**: Describes the credential requirement for one `activities.list` request path.

**Fields**:

- `access_type`: Public-channel or authorized-user
- `auth_mode`: The runtime auth selection compatible with that path
- `maintainer_note`: Explanation shown in metadata and contract artifacts
- `conditional_reason`: Execution-time explanation when conditional auth is selected

**Validation Rules**:

- Public-channel paths must remain distinguishable from authorized-user paths
- Authorized-user paths must require a clear maintainer-facing explanation and compatible execution context
- Credential payloads must never be exposed in contract artifacts or documentation

**Relationships**:

- Derived from one `Activity Filter Mode`
- Referenced by the wrapper metadata review surface and implementation tests

## Entity: Activity Collection Result

**Purpose**: Represents the successful outcome of a valid `activities.list` request, including the case where no activity items are returned.

**Fields**:

- `items`: Returned activity items, which may be empty
- `result_state`: Non-empty or empty-success
- `request_mode`: Filter mode used for the request
- `metadata_visibility`: Whether quota and auth guidance remain attached to the wrapper rather than the result payload

**Validation Rules**:

- An empty `items` collection is valid when the request itself is valid
- Empty-success must not be normalized into an upstream error
- Result handling must not erase the wrapper's documented auth or filter context

**Relationships**:

- Returned by one `Activity List Wrapper Contract`
- Produced through the shared executor success path

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but filter scope or auth guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, supported filter paths, and auth expectations are visible together
3. `validated`: Unit, contract, and integration checks prove filter exclusivity, mixed-auth explanation, and empty-success handling
4. `reusable`: Later Layer 2 and Layer 3 work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller selects one supported filter mode
2. Wrapper validates field presence and exclusivity
3. Shared executor runs with the auth context appropriate to that mode
4. Request ends as either `success with items`, `success with empty items`, or `normalized upstream failure`
