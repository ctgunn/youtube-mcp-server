# Data Model: YT-119 Layer 1 Endpoint `comments.setModerationStatus`

## Entity: Comments Moderation Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `comments.setModerationStatus` so maintainers can review endpoint identity, quota cost, moderation-state rules, OAuth behavior, optional moderation-flag guidance, and invalid-moderation boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `comments`
- `operation_name`: Upstream operation name, expected to remain `setModerationStatus`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for moderation changes
- `auth_mode`: Stable auth mode for this wrapper, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes covering moderation-state rules, authorization requirements, optional moderation-flag boundaries, and unsupported moderation-shape guidance

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain explicitly OAuth-required
- Contract notes must include moderation-transition expectations and clear unsupported-moderation guidance

**Relationships**:

- Uses one `Comment Moderation Request`
- Applies one `Comment Moderation Access Profile`
- Produces one `Moderation Update Result`

## Entity: Comment Moderation Request

**Purpose**: Represents one supported `comments.setModerationStatus` request.

**Fields**:

- `id`: One or more target comment identifiers for one moderation attempt
- `moderation_status`: Requested moderation outcome for the targeted comments
- `ban_author`: Optional moderation flag indicating whether the author should also be banned when the selected moderation outcome supports it
- `delegation_context`: Optional owner-partner delegation inputs supported for this slice
- `moderation_scope`: Maintainer-facing label describing that the supported boundary is comment moderation-state change rather than comment editing

**Validation Rules**:

- Every supported request must include at least one non-empty target comment identifier
- The request must include one non-empty moderation outcome
- The request must remain query-only and must not require a request body
- Duplicate or unusable comment identifiers must be rejected or clearly flagged before execution
- Unsupported top-level request fields must be rejected before execution
- Optional moderation flags must only be accepted when compatible with the selected moderation outcome

**Relationships**:

- Requires one `Moderation Transition Policy`
- Requires one `Comment Moderation Access Profile`
- Produces one `Moderation Update Result`

## Entity: Moderation Transition Policy

**Purpose**: Defines the supported moderation-state and optional-flag combinations for this feature slice.

**Fields**:

- `allowed_statuses`: Representative supported moderation outcomes for this slice
- `default_transition_mode`: Reviewable statement that one moderation outcome applies to all comment IDs in a single request
- `ban_author_allowed_with`: The moderation outcome that may validly accompany the optional author-ban flag
- `unsupported_state_note`: Reviewable explanation of which moderation states or transition combinations are out of scope
- `maintainer_note`: Summary of how downstream layers should interpret supported moderation transitions

**Validation Rules**:

- Supported moderation outcomes must stay explicitly enumerated and reviewable
- The author-ban flag must not be accepted with unsupported moderation outcomes
- One request must not imply multiple conflicting moderation outcomes
- Review notes must stay specific enough for later Layer 2 and Layer 3 reuse decisions

**Relationships**:

- Applied to one `Comment Moderation Request`
- Interpreted alongside one `Comment Moderation Access Profile`

## Entity: Comment Moderation Access Profile

**Purpose**: Captures the authorization requirement and failure categorization expectations for one `comments.setModerationStatus` request path.

**Fields**:

- `auth_mode`: OAuth-required label for the wrapper
- `requires_authorized_access`: Whether the request needs authorized comment-moderation access
- `delegation_fields`: Optional owner-partner delegation fields supported in authorized requests
- `eligibility_note`: Maintainer-facing explanation of moderation eligibility and delegation limits
- `failure_boundary`: Expected distinction between `auth`, `invalid_request`, unsupported-transition, and normalized upstream moderation failures

**Validation Rules**:

- Supported `comments.setModerationStatus` paths must require authorized access
- Auth mismatch behavior must remain distinguishable from invalid moderation-shape or unsupported-transition failures
- Delegation guidance, if exposed, must stay explicit without exposing credential material
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Comments Moderation Wrapper Contract`
- Used to interpret `Moderation Update Result`

## Entity: Moderation Update Result

**Purpose**: Represents normalized acknowledgment output for one valid `comments.setModerationStatus` request.

**Fields**:

- `comment_ids`: Stable target comment identifiers preserved for downstream review or mapping
- `moderation_status`: Moderation outcome applied to the targeted comments
- `ban_author_applied`: Whether the optional author-ban flag was part of the accepted request
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `delegated_owner`: Optional delegation indicator preserved from the request
- `result_state`: Success with moderation acknowledgment or normalized failure outcome
- `upstream_body_state`: Reviewable note that successful upstream moderation may return no content body

**Validation Rules**:

- Valid requests must produce either a successful moderation acknowledgment or a normalized failure
- Result handling must preserve source operation and quota visibility needed by higher layers
- Successful results must preserve enough moderation context for downstream callers to confirm the targeted state change
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Comments Moderation Wrapper Contract`
- Interpreted alongside one `Comment Moderation Access Profile`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but moderation-state and OAuth rules are incomplete
2. `reviewable`: Quota, moderation-state rules, auth requirements, optional moderation-flag guidance, and failure boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm moderation-shape and auth behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one moderation request with target comment IDs and one moderation status
2. Wrapper validates required fields, moderation-state boundary, duplicate-target rules, optional moderation-flag compatibility, and optional delegation-context boundaries
3. Auth compatibility is evaluated for the request
4. Shared executor performs the moderation change for valid authorized requests
5. Outcome ends as `moderation acknowledged`, `normalized invalid_request`, `normalized auth failure`, `normalized unsupported-transition failure`, or `normalized upstream moderation failure`
