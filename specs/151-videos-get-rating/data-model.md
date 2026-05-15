# Data Model: YT-151 Layer 1 Endpoint `videos.getRating`

## Entity: Videos Get Rating Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper for `videos.getRating` in a way that exposes endpoint identity, quota cost, supported identifier boundaries, authorization expectations, and normalized rating-state outcome rules before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `videos`
- `operation_name`: Upstream operation name, expected to remain `getRating`
- `operation_key`: Stable combined identifier used in tests and review surfaces
- `http_method`: Upstream HTTP method for the wrapper
- `path_shape`: Upstream path or route pattern for the wrapper
- `request_shape`: Allowed request fields for the wrapper contract
- `auth_mode`: Stable auth mode for this endpoint, expected to remain OAuth-required
- `quota_cost`: Official quota-unit cost of `1`
- `notes`: Maintainer-facing notes for identifier boundaries, returned rating-state support, unsupported-input boundaries, and normalized outcome interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as OAuth-required rather than hiding access expectations in runtime-only behavior
- The wrapper contract is incomplete if required identifier guidance or returned rating-state notes are not visible in maintainer-facing artifacts

**Relationships**:

- Uses one `Video Rating Lookup Request`
- References one `Returned Rating State Set`
- Produces one `Video Rating Lookup Result`
- Is exercised through the shared executor and representative wrapper flow under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`

## Entity: Video Rating Lookup Request

**Purpose**: Represents one supported `videos.getRating` request shape that identifies the video or videos whose current viewer rating state should be retrieved.

**Fields**:

- `id`: Required video identifier field for the lookup request
- `identifier_mode`: Maintainer-facing label that distinguishes one-video and bounded multi-video use within the same field
- `identifier_limit`: Maximum supported identifier count for one request, expected to remain `50`
- `unsupported_fields_policy`: Explicit statement that undocumented request fields are outside this feature's promised contract
- `request_mode`: Maintainer-facing label that distinguishes a valid lookup request from unsupported incomplete shapes

**Validation Rules**:

- A supported lookup request must include `id`
- `id` must remain visible as the request field in review surfaces and contract artifacts
- The accepted `id` form must be documented clearly enough that maintainers can tell whether the request covers one video, multiple videos, or both
- The accepted `id` form must document that one request supports at most 50 comma-delimited video identifiers
- Unsupported or unexpected fields must be rejected or clearly flagged before execution
- The request contract must remain deterministic and must not silently rewrite incomplete or broader list-style input into supported behavior

**Relationships**:

- Belongs to one `Videos Get Rating Wrapper Contract`
- Produces one `Video Rating Lookup Result`

## Entity: Returned Rating State Set

**Purpose**: Describes the supported viewer-rating outcomes returned by `videos.getRating` so maintainers can tell which successful states are guaranteed and which outcomes are not failures.

**Fields**:

- `liked_state`: Maintainer-facing note for the successful positive-rating outcome
- `disliked_state`: Maintainer-facing note for the successful negative-rating outcome
- `unrated_state`: Maintainer-facing note for the successful no-rating outcome
- `supported_states`: Explicit list of successful viewer-rating states guaranteed by this slice
- `state_boundary_note`: Explanation shown in metadata and contract artifacts
- `failure_separation_note`: Explanation of how successful unrated states remain distinct from lookup failures

**Validation Rules**:

- Supported `videos.getRating` paths must require authorized access
- The supported rating-state set must explicitly include the unrated success path
- Returned state guidance must remain reviewable without reading transport code
- Credentials and secret-backed values must never be exposed in contract artifacts or documentation

**Relationships**:

- Applied to one `Videos Get Rating Wrapper Contract`
- Referenced by request semantics, result interpretation, and implementation tests

## Entity: Video Rating Lookup Result

**Purpose**: Represents the normalized successful outcome of a valid `videos.getRating` request.

**Fields**:

- `items`: Per-video rating-state entries returned by the lookup
- `requested_id`: Stable echo of the incoming identifier field used for the request
- `source_operation`: Stable source-operation identifier preserved for review and downstream mapping
- `auth_path`: Maintainer-facing label showing the OAuth-required path used by this wrapper
- `rating_state_summary`: Stable summary of whether the result includes rated items, unrated items, or both
- `metadata_visibility`: Whether quota, auth, and returned-state guidance remain attached to the wrapper rather than being lost in the result payload

**Validation Rules**:

- A valid lookup request must end as either a successful rating-state result or a normalized upstream failure
- Successful lookup results must preserve whether returned items are rated or unrated rather than treating unrated items as empty failure cases
- Result handling must keep source operation, identifier visibility, and viewer-rating meaning available to higher layers
- The result shape must preserve enough per-video context that downstream layers can match returned states back to requested videos

**Relationships**:

- Returned by one `Videos Get Rating Wrapper Contract`
- Produces one or more `Per-Video Rating Entry` records

## Entity: Per-Video Rating Entry

**Purpose**: Represents one requested video's returned viewer-rating state in a successful `videos.getRating` lookup.

**Fields**:

- `video_id`: Stable video identifier for the returned entry
- `rating`: Returned viewer-rating state for that video
- `is_rated`: Boolean-style indicator that the viewer currently has a rating on the video
- `is_unrated`: Boolean-style indicator that the viewer has no current rating on the video
- `source_request_id`: Link back to the originating request identifier set

**Validation Rules**:

- Each successful entry must identify the target video
- Each successful entry must preserve a supported returned rating state
- `is_rated` and `is_unrated` must remain logically consistent
- Successful unrated entries must remain distinct from omitted or failed entries

**Relationships**:

- Belongs to one `Video Rating Lookup Result`

## Entity: Rating Lookup Failure Outcome

**Purpose**: Represents one normalized non-success outcome from a `videos.getRating` request so downstream callers can distinguish what kind of remediation is needed.

**Fields**:

- `category`: Stable failure category such as invalid request, access-related failure, or upstream lookup failure
- `reason`: Maintainer-visible explanation of what failed
- `request_mode`: The lookup-request mode that triggered the failure, when known
- `source_operation`: Stable endpoint identifier preserved for diagnostics
- `retryability`: Whether the failure suggests caller correction, access correction, or upstream-side retry
- `upstream_category_examples`: Representative normalized categories such as `invalid_request`, `auth`, `not_found`, and `upstream_unavailable`

**Validation Rules**:

- Local validation failures must remain distinct from access failures
- Access failures must remain distinct from upstream lookup failures after execution begins
- Successful unrated results must not be represented through this failure entity
- The failure model must be reviewable enough that later layers can decide whether to fix input, change authorization, or surface the upstream problem

**Relationships**:

- May be produced instead of one `Video Rating Lookup Result`
- Shares wrapper metadata and request context with the `Videos Get Rating Wrapper Contract`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but identifier-boundary or returned-state guidance may still be implicit
2. `reviewable`: Endpoint identity, quota cost, OAuth requirement, and supported returned rating states are visible together
3. `validated`: Unit, contract, integration, and transport checks prove identifier validation, returned-state guidance, OAuth-only guidance, and normalized lookup-result handling
4. `reusable`: Later video-rating and viewer-state work can consume the wrapper contract without extra endpoint research

### Request Outcome Lifecycle

1. Caller supplies one supported rating-lookup request shape
2. Wrapper validates required identifier input plus unexpected-field rejection
3. OAuth eligibility is evaluated before execution
4. Shared executor runs with authorized access for the validated lookup request
5. Request ends as either `successful rated result`, `successful unrated result`, `normalized invalid_request`, `normalized auth failure`, `normalized not_found`, or `normalized upstream_unavailable`
