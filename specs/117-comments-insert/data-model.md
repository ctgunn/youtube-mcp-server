# Data Model: YT-117 Layer 1 Endpoint `comments.insert`

## Entity: Comments Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `comments.insert` so maintainers can review endpoint identity, quota cost, reply-body rules, OAuth behavior, optional delegation guidance, and invalid-create boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `comments`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for reply creation
- `auth_mode`: Stable auth mode for this wrapper, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes covering reply boundaries, authorization requirements, unsupported create shapes, and optional delegation guidance

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain explicitly OAuth-required
- Contract notes must include reply-creation expectations and clear unsupported-create guidance

**Relationships**:

- Uses one `Comment Insert Request`
- Applies one `Comment Write Access Profile`
- Produces one `Created Comment Result`

## Entity: Comment Insert Request

**Purpose**: Represents one supported `comments.insert` request.

**Fields**:

- `part`: Requested response sections for one create attempt
- `body`: Reply-create payload supplied for comment creation
- `delegation_context`: Optional owner-partner delegation inputs supported for this slice
- `write_scope`: Maintainer-facing label describing that the supported create boundary is reply creation

**Validation Rules**:

- Every supported request must include `part` and one non-empty `body`
- The `body` must identify the parent comment being answered
- The `body` must include non-empty reply content
- Unsupported or read-only fields must be rejected or clearly flagged before execution
- Unexpected top-level request fields must be rejected before execution

**Relationships**:

- Requires one `Comment Write Access Profile`
- Produces one `Created Comment Result`

## Entity: Reply Payload

**Purpose**: Defines the supported comment body structure for reply creation in this feature slice.

**Fields**:

- `parent_comment_id`: Identifier of the parent comment being answered
- `reply_text`: Text content of the reply to create
- `requested_parts`: Requested response sections associated with the created comment
- `unsupported_fields_present`: Indicator that top-level-comment or unrelated fields were supplied outside the supported reply boundary
- `maintainer_note`: Reviewable explanation of the supported reply-create shape

**Validation Rules**:

- The payload must include one parent-comment reference
- The payload must include one non-empty reply text value after normalization
- The payload must not imply a top-level comment create shape for this slice
- Review notes must stay specific enough for later Layer 2 and Layer 3 reuse decisions

**Relationships**:

- Embedded within one `Comment Insert Request`
- Interpreted alongside one `Comment Write Access Profile`

## Entity: Comment Write Access Profile

**Purpose**: Captures the authorization requirement and failure categorization expectations for one `comments.insert` request path.

**Fields**:

- `auth_mode`: OAuth-required label for the wrapper
- `requires_authorized_access`: Whether the request needs authorized comment-write access
- `delegation_fields`: Optional owner-partner delegation fields supported in authorized requests
- `eligibility_note`: Maintainer-facing explanation of create eligibility and delegation limits
- `failure_boundary`: Expected distinction between `auth`, `invalid_request`, and normalized upstream write failures

**Validation Rules**:

- Supported `comments.insert` paths must require authorized access
- Auth mismatch behavior must remain distinguishable from invalid reply-body or unsupported-create failures
- Delegation guidance must stay explicit without exposing credential material
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Comments Insert Wrapper Contract`
- Used to interpret `Created Comment Result`

## Entity: Created Comment Result

**Purpose**: Represents normalized output for one valid `comments.insert` request.

**Fields**:

- `comment_id`: Returned identifier for the created reply comment
- `parent_comment_id`: Stable parent-comment reference preserved for downstream review or mapping
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `delegated_owner`: Optional delegation indicator preserved from the request
- `result_state`: Success with created reply or normalized failure outcome

**Validation Rules**:

- Valid requests must produce either a successful created-comment result or a normalized failure
- Result handling must preserve source operation and quota visibility needed by higher layers
- Successful results must preserve enough reply context for downstream callers to confirm the create target
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Comments Insert Wrapper Contract`
- Interpreted alongside one `Comment Write Access Profile`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but reply and OAuth rules are incomplete
2. `reviewable`: Quota, reply-body rules, auth requirements, delegation guidance, and failure boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm create-shape and auth behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one comment-create request with `part` and `body`
2. Wrapper validates required fields, reply boundary, unsupported-field rules, and optional delegation-context boundaries
3. Auth compatibility is evaluated for the request
4. Shared executor performs the create for valid authorized requests
5. Outcome ends as `created reply`, `normalized invalid_request`, `normalized auth failure`, or `normalized upstream write failure`
