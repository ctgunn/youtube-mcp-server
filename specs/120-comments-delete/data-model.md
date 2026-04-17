# Data Model: YT-120 Layer 1 Endpoint `comments.delete`

## Entity: Comments Delete Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `comments.delete` so maintainers can review endpoint identity, quota cost, delete-target rules, OAuth behavior, optional delegation guidance, and delete-failure boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `comments`
- `operation_name`: Upstream operation name, expected to remain `delete`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for comment removal
- `auth_mode`: Stable auth mode for this wrapper, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes covering delete-target rules, authorization requirements, optional delegation behavior, and unavailable-target guidance

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain explicitly OAuth-required
- Contract notes must include delete preconditions, destructive-operation guidance, and clear unsupported-request guidance

**Relationships**:

- Uses one `Comment Delete Request`
- Applies one `Comment Delete Access Profile`
- Produces one `Comment Delete Result`

## Entity: Comment Delete Request

**Purpose**: Represents one supported `comments.delete` request.

**Fields**:

- `id`: Required target comment identifier for one delete attempt
- `delegation_context`: Optional owner-partner delegation inputs supported for this slice
- `delete_scope`: Maintainer-facing label describing that the supported boundary is one comment deletion rather than bulk removal

**Validation Rules**:

- Every supported request must include one non-empty target comment identifier
- The request must remain query-only and must not require a request body
- Unsupported top-level request fields must be rejected before execution
- Delegation inputs, if supported, must remain narrow and reviewable

**Relationships**:

- Requires one `Comment Delete Access Profile`
- Produces one `Comment Delete Result`

## Entity: Comment Delete Access Profile

**Purpose**: Captures the authorization requirement and failure categorization expectations for one `comments.delete` request path.

**Fields**:

- `auth_mode`: OAuth-required label for the wrapper
- `requires_authorized_access`: Whether the request needs authorized comment-delete access
- `delegation_fields`: Optional owner-partner delegation fields supported in authorized requests
- `eligibility_note`: Maintainer-facing explanation of delete eligibility and delegation limits
- `failure_boundary`: Expected distinction between `auth`, `invalid_request`, target-state, and normalized upstream delete failures

**Validation Rules**:

- Supported `comments.delete` paths must require authorized access
- Auth mismatch behavior must remain distinguishable from invalid delete-shape or unavailable-target failures
- Delegation guidance, if exposed, must stay explicit without exposing credential material
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Comments Delete Wrapper Contract`
- Used to interpret `Comment Delete Result`

## Entity: Delete Target State

**Purpose**: Defines the reviewable status of the targeted comment at delete time so downstream layers can interpret unavailable-resource outcomes clearly.

**Fields**:

- `target_id`: The comment identifier supplied for deletion
- `eligibility_state`: Whether the target is eligible for deletion, already removed, unavailable, or inaccessible in the current authorization context
- `state_note`: Maintainer-facing explanation of how the target state should be interpreted
- `source_boundary`: Whether the state is enforced locally before execution or reported as a normalized upstream outcome

**Validation Rules**:

- The target state must remain reviewable enough that maintainers can distinguish missing or malformed identifiers from unavailable comments
- Delete-target guidance must not imply silent retries or implicit recovery
- State notes must stay specific enough for later Layer 2 and Layer 3 reuse decisions

**Relationships**:

- Interpreted alongside one `Comment Delete Request`
- Influences one `Comment Delete Result`

## Entity: Comment Delete Result

**Purpose**: Represents normalized acknowledgment output for one valid `comments.delete` request.

**Fields**:

- `comment_id`: Stable target comment identifier preserved for downstream review or mapping
- `is_deleted`: Whether the delete request completed successfully
- `review_result_fields`: Maintainer-facing reminder that the normalized result exposes `commentId` and `isDeleted` review fields
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `delegated_owner`: Optional delegation indicator preserved from the request
- `result_state`: Success with deletion acknowledgment or normalized failure outcome
- `upstream_body_state`: Reviewable note that successful upstream delete may return no content body

**Validation Rules**:

- Valid requests must produce either a successful deletion acknowledgment or a normalized failure
- Result handling must preserve source operation and quota visibility needed by higher layers
- Successful results must preserve enough delete context for downstream callers to confirm which comment was removed
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Comments Delete Wrapper Contract`
- Interpreted alongside one `Comment Delete Access Profile`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but delete rules and OAuth notes are incomplete
2. `reviewable`: Quota, delete-target rules, auth requirements, optional delegation guidance, and failure boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm delete-shape and auth behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one delete request with a target comment identifier
2. Wrapper validates required fields, identifier shape, and optional delegation-context boundaries
3. Auth compatibility is evaluated for the request
4. Shared executor performs the delete for valid authorized requests
5. Outcome ends as `deletion acknowledged`, `normalized invalid_request`, `normalized auth failure`, `normalized target-state failure`, or `normalized upstream delete failure`
