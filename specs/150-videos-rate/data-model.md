# Data Model: YT-150 Layer 1 Endpoint `videos.rate`

## Entity: Videos Rate Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `videos.rate` in a way that exposes endpoint identity, quota cost, supported rating semantics, authorization expectations, and normalized outcome rules before execution.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `videos`
- `operation_name`: Upstream operation name, expected to remain `rate`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `50`
- `notes`: Maintainer-facing notes for rating-action support, unsupported-input boundaries, and normalized acknowledgement-result interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if required rating inputs or action-boundary notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Video Rating Request`
- References one `Rating Action Set`
- Produces one `Video Rating Outcome`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Video Rating Request

**Purpose**: Represents one supported `videos.rate` request shape that combines the target video identity with the requested rating action.

**Fields**:

- `id`: Target video identifier for the rating mutation
- `rating`: Requested rating action for the target video
- `request_mode`: Maintainer-facing label that distinguishes a valid rating request from unsupported incomplete shapes
- `unsupported_fields_policy`: Explicit statement that undocumented request fields are outside this feature's promised contract

**Validation Rules**:

- A supported rating request must include `id` and `rating`
- `id` must remain visible as the target identifier field in review surfaces and contract artifacts
- `rating` must be one supported action from the documented `Rating Action Set`
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- The request contract must remain deterministic and must not silently rewrite incomplete input into supported behavior

**Relationships**:

- Belongs to one `Videos Rate Wrapper Contract`
- Uses one `Rating Action Set`
- Produces one `Video Rating Outcome`

## Entity: Rating Action Set

**Purpose**: Describes the supported action vocabulary for `videos.rate` so maintainers can tell which requested mutations are guaranteed by this slice and which are intentionally out of scope.

**Fields**:

- `apply_like_action`: Maintainer-facing note for the supported positive-rating action
- `apply_dislike_action`: Maintainer-facing note for the supported negative-rating action
- `clear_rating_action`: Maintainer-facing note for the supported rating-removal action
- `supported_actions`: Explicit list of rating values guaranteed by this slice
- `unsupported_actions_policy`: Explanation of how unsupported rating values are treated
- `maintainer_note`: Explanation shown in metadata and contract artifacts

**Validation Rules**:

- Supported `videos.rate` paths must require authorized access
- The supported action set must explicitly include the clear-rating path
- Unsupported rating values must not appear supported implicitly
- Credentials and secret-backed values must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Videos Rate Wrapper Contract`
- Referenced by request semantics and implementation tests

## Entity: Video Rating Outcome

**Purpose**: Represents the successful acknowledgement of a valid `videos.rate` request.

**Fields**:

- `resource_id`: Stable identifier for the rated video
- `requested_rating`: Supported rating action applied or cleared by the request
- `acknowledgement_state`: Successful mutation-acknowledgement state visible to higher layers
- `source_operation`: Stable source-operation identifier preserved for review and downstream mapping
- `metadata_visibility`: Whether quota, auth, and rating-semantics guidance remain attached to the wrapper rather than being lost in the result payload
- `upstream_body_state`: Whether the upstream acknowledgement body was empty or JSON-backed

**Validation Rules**:

- A valid rating request must end as either an acknowledgement success or a normalized upstream failure
- Successful acknowledgement must not erase the wrapper's documented auth, quota, or rating-semantics context
- Result handling must keep source operation, identifier, and requested action visibility available to higher layers
- The acknowledgement shape must preserve whether the request produced an applied or cleared rating state

**Relationships**:

- Returned by one `Videos Rate Wrapper Contract`
- Produced through the shared executor success path

## Entity: Rating Failure Outcome

**Purpose**: Represents one normalized non-success outcome from a `videos.rate` request so downstream callers can distinguish what type of remediation is needed.

**Fields**:

- `category`: Stable failure category such as invalid request, access-related failure, or upstream rating rejection
- `reason`: Maintainer-visible explanation of what failed
- `request_mode`: The rating-request mode that triggered the failure, when known
- `source_operation`: Stable endpoint identifier preserved for diagnostics
- `retryability`: Whether the failure suggests caller correction, access correction, or upstream-side retry
- `upstream_category_examples`: Representative normalized categories such as `invalid_request`, `auth`, `not_found`, and `policy_restricted`

**Validation Rules**:

- Local validation failures must remain distinct from access failures
- Access failures must remain distinct from upstream rating rejections after execution begins
- The failure model must be reviewable enough that later layers can decide whether to fix input, change authorization, or surface the upstream rejection
- Upstream refusal categories must remain distinguishable from local validation so higher layers do not misclassify remediation steps

**Relationships**:

- May be produced instead of one `Video Rating Outcome`
- Shares wrapper metadata and request context with the `Videos Rate Wrapper Contract`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but rating-action or required-input guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, and supported rating actions are visible together
3. `validated`: Unit, contract, integration, and transport checks prove identifier validation, rating-boundary guidance, OAuth-only guidance, and acknowledgement-result handling
4. `reusable`: Later video-rating work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported rating-request shape
2. Wrapper validates required identifier and requested action plus unexpected-field rejection
3. OAuth eligibility is evaluated before execution
4. Shared executor runs with authorized access for the validated rating request
5. Request ends as either `rating acknowledged`, `normalized invalid_request`, `normalized auth failure`, `normalized not_found`, or `normalized policy_restricted`
