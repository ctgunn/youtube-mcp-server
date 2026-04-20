# Data Model: YT-122 Layer 1 Endpoint `commentThreads.insert`

## Entity: Comment Threads Insert Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `commentThreads.insert` so maintainers can review endpoint identity, quota cost, top-level-thread rules, OAuth behavior, optional delegation guidance, and invalid-create boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `commentThreads`
- `operation_name`: Upstream operation name, expected to remain `insert`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for top-level thread creation
- `auth_mode`: Stable auth mode for this wrapper, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes covering top-level-thread boundaries, authorization requirements, unsupported reply-style shapes, optional delegation guidance, and target-eligibility handling

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain explicitly OAuth-required
- Contract notes must include top-level-thread expectations and clear unsupported-create guidance

**Relationships**:

- Uses one `Comment Thread Create Request`
- Applies one `Comment Thread Write Access Profile`
- Produces one `Created Comment Thread Result`

## Entity: Comment Thread Create Request

**Purpose**: Represents one supported `commentThreads.insert` request.

**Fields**:

- `part`: Requested response sections for one create attempt
- `body`: Video-targeted top-level thread-create payload supplied for comment-thread creation
- `delegation_context`: Optional owner-partner delegation inputs supported for this slice
- `write_scope`: Maintainer-facing label describing that the supported create boundary is top-level thread creation

**Validation Rules**:

- Every supported request must include `part` and one non-empty `body`
- The `body` must identify one supported discussion target for a new top-level thread
- The `body` must include non-empty top-level comment content
- Reply-style or mixed create shapes must be rejected or clearly flagged before execution
- Unexpected top-level request fields must be rejected before execution

**Relationships**:

- Requires one `Comment Thread Write Access Profile`
- Produces one `Created Comment Thread Result`

## Entity: Top-Level Thread Payload

**Purpose**: Defines the supported comment-thread body structure for top-level thread creation in this feature slice.

**Fields**:

- `discussion_target`: Video identifier of the supported discussion target for the new thread
- `comment_text`: Text content of the top-level comment to create
- `requested_parts`: Requested response sections associated with the created thread
- `unsupported_fields_present`: Indicator that reply-style or unrelated fields were supplied outside the supported top-level boundary
- `maintainer_note`: Reviewable explanation of the supported top-level create shape

**Validation Rules**:

- The payload must include one supported video target
- The payload must include one non-empty top-level comment text value after normalization
- The payload must not imply a reply create shape for this slice
- Review notes must stay specific enough for later Layer 2 and Layer 3 reuse decisions

**Relationships**:

- Embedded within one `Comment Thread Create Request`
- Interpreted alongside one `Comment Thread Write Access Profile`

## Entity: Comment Thread Write Access Profile

**Purpose**: Captures the authorization requirement and failure categorization expectations for one `commentThreads.insert` request path.

**Fields**:

- `auth_mode`: OAuth-required label for the wrapper
- `requires_authorized_access`: Whether the request needs authorized comment-thread write access
- `delegation_fields`: Optional owner-partner delegation fields supported in authorized requests
- `eligibility_note`: Maintainer-facing explanation of target eligibility and delegation limits
- `failure_boundary`: Expected distinction between `auth`, `invalid_request`, target-eligibility, and normalized upstream write failures

**Validation Rules**:

- Supported `commentThreads.insert` paths must require authorized access
- Auth mismatch behavior must remain distinguishable from invalid create-shape failures
- Target-eligibility behavior must remain distinguishable from malformed body or unsupported-shape failures
- Delegation guidance must stay explicit without exposing credential material
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Comment Threads Insert Wrapper Contract`
- Used to interpret `Created Comment Thread Result`

## Entity: Created Comment Thread Result

**Purpose**: Represents normalized output for one valid `commentThreads.insert` request.

**Fields**:

- `thread_id`: Returned identifier for the created top-level comment thread
- `discussion_target`: Stable target reference preserved for downstream review or mapping
- `top_level_comment_id`: Returned top-level comment identifier when available
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `delegated_owner`: Optional delegation indicator preserved from the request
- `result_state`: Success with created top-level thread or normalized failure outcome

**Validation Rules**:

- Valid requests must produce either a successful created-thread result or a normalized failure
- Result handling must preserve source operation and quota visibility needed by higher layers
- Successful results must preserve enough thread context for downstream callers to confirm the create target
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Comment Threads Insert Wrapper Contract`
- Interpreted alongside one `Comment Thread Write Access Profile`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but top-level-thread and OAuth rules are incomplete
2. `reviewable`: Quota, top-level-thread rules, auth requirements, delegation guidance, and failure boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm create-shape and auth behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one comment-thread create request with `part` and `body`
2. Wrapper validates required fields, top-level boundary, unsupported-field rules, and optional delegation-context boundaries
3. Auth compatibility is evaluated for the request
4. Target eligibility is evaluated for the selected discussion target
5. Shared executor performs the create for valid authorized requests
6. Outcome ends as `created top-level thread`, `normalized invalid_request`, `normalized auth failure`, `normalized target-eligibility failure`, or `normalized upstream write failure`
