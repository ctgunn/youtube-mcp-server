# Data Model: YT-113 Layer 1 Endpoint `channelSections.insert`

## Entity: Channel Sections Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `channelSections.insert` so maintainers can review endpoint identity, quota cost, section-type rules, OAuth behavior, delegation guidance, and invalid-create boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `channelSections`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for channel-section creation
- `auth_mode`: Stable auth mode for this wrapper, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes covering section-type boundaries, title rules, and optional delegation guidance

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain explicitly OAuth-required
- Contract notes must include section-type expectations and clear unsupported-create guidance

**Relationships**:

- Uses one `Channel Section Insert Request`
- References one `Channel Section Type Profile`
- Applies one `Channel Section Access Expectation`
- Produces one `Created Channel Section Resource`

## Entity: Channel Section Insert Request

**Purpose**: Represents one supported `channelSections.insert` request.

**Fields**:

- `part`: Requested resource parts to set and return for the created section
- `body`: New channel-section resource payload supplied for creation
- `delegation_context`: Optional owner-partner delegation inputs supported for this slice
- `write_scope`: Maintainer-facing label that describes the selected section-type create boundary

**Validation Rules**:

- Every supported request must include `part` and one non-empty `body`
- The `body` must include `snippet.type`
- The selected section type must align with the fields present in `body`
- Unsupported or read-only fields must be rejected or clearly flagged before execution
- Unexpected top-level request fields must be rejected before execution

**Relationships**:

- Conforms to one `Channel Section Type Profile`
- Requires one `Channel Section Access Expectation`
- Produces one `Created Channel Section Resource`

## Entity: Channel Section Type Profile

**Purpose**: Defines how one channel-section type is represented and reviewed in the wrapper contract.

**Fields**:

- `type_name`: One channel-section type identifier such as `singlePlaylist`, `multiplePlaylists`, or `multipleChannels`
- `support_state`: Supported or unsupported for this feature scope
- `required_content_fields`: Body fields that must be present for this type
- `forbidden_content_fields`: Body fields that must not be present for this type
- `title_rule`: Whether `snippet.title` is required, optional, or ignored for this type
- `item_count_rule`: Whether the type expects exactly one item, one or more items, or no explicit item list
- `maintainer_note`: Reviewable explanation of the type boundary

**Validation Rules**:

- Supported types must map to at least one reviewable body-shape rule
- Playlist-backed types must remain distinguishable from channel-backed types
- Title requirements must be explicit for types that require custom titles
- Duplicate item references must remain invalid when the selected type expects distinct items

**Relationships**:

- Referenced by `Channel Section Insert Request`
- Summarized by `Channel Sections Insert Wrapper Contract`
- Interpreted alongside `Channel Section Access Expectation`

## Entity: Channel Section Access Expectation

**Purpose**: Captures the authorization requirement and failure categorization expectations for one `channelSections.insert` request path.

**Fields**:

- `auth_mode`: OAuth-required label for the wrapper
- `requires_authorized_access`: Whether the request needs authorized channel-management access
- `delegation_fields`: Optional owner-partner delegation fields supported in authorized requests
- `eligibility_note`: Maintainer-facing explanation of create eligibility and partner delegation limits
- `failure_boundary`: Expected distinction between `auth`, `invalid_request`, and normalized upstream create failures

**Validation Rules**:

- Supported `channelSections.insert` paths must require authorized access
- Auth mismatch behavior must remain distinguishable from invalid create-body or unsupported-content failures
- Delegation guidance must stay explicit without exposing credential material
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Channel Sections Insert Wrapper Contract`
- Referenced by `Channel Section Type Profile`
- Used to interpret `Created Channel Section Resource`

## Entity: Created Channel Section Resource

**Purpose**: Represents normalized output for one valid `channelSections.insert` request.

**Fields**:

- `items`: Returned created channel-section resource content
- `source_operation`: Stable operation identifier for review and downstream mapping
- `created_type`: Section type reflected in the successful response
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with created resource or normalized failure outcome

**Validation Rules**:

- Valid requests must produce either a successful created-resource result or a normalized failure
- Result handling must preserve the source operation and quota visibility needed by higher layers
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Channel Sections Insert Wrapper Contract`
- Interpreted alongside `Channel Section Access Expectation`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but section-type and OAuth rules are incomplete
2. `reviewable`: Quota, section-type rules, auth requirements, delegation guidance, and failure boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm create-shape and auth behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one channel-section create request with `part` and `body`
2. Wrapper validates required fields, section-type alignment, duplicate-item boundaries, and unsupported-field rules
3. Auth compatibility and optional delegation context are evaluated for the request
4. Shared executor performs the create for valid authorized requests
5. Outcome ends as `created resource`, `normalized invalid_request`, `normalized auth failure`, or `normalized upstream create failure`
