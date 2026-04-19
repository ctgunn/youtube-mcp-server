# Data Model: YT-121 Layer 1 Endpoint `commentThreads.list`

## Entity: Comment Threads List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `commentThreads.list` so maintainers can review endpoint identity, quota cost, selector rules, access behavior, optional modifiers, and result boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `commentThreads`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for comment-thread retrieval
- `auth_mode`: Stable auth mode for this wrapper, expected to remain API-key access for the seed-supported selectors
- `quota_cost`: Official quota-unit cost of `1`
- `notes`: Maintainer-facing notes covering selector exclusivity, optional modifiers, empty-result behavior, and failure boundaries

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- Contract notes must keep the supported selector set reviewable as public retrieval paths for this slice
- Contract notes must include video-based retrieval, channel-related retrieval, ID-based retrieval, and empty-result interpretation guidance
- Selector guidance must keep unsupported combinations and undocumented fields explicit

**Relationships**:

- Uses one `Comment Threads List Request`
- Applies one `Comment Thread Lookup Access Profile`
- Produces one `Comment Threads List Result`

## Entity: Comment Threads List Request

**Purpose**: Represents one supported `commentThreads.list` request.

**Fields**:

- `part`: Requested response sections for one retrieval attempt
- `videoId`: Optional video-scoped selector for thread lookup
- `allThreadsRelatedToChannelId`: Optional channel-related selector for thread lookup
- `id`: Optional direct thread selector for one or more thread identifiers
- `pageToken`: Optional cursor for continued retrieval
- `maxResults`: Optional item-count limit for one result page
- `order`: Optional ordering preference for returned threads
- `searchTerms`: Optional search phrase used within supported thread lookups
- `textFormat`: Optional text rendering preference for returned comment text

**Validation Rules**:

- Every supported request must include one non-empty `part` value
- Every supported request must include exactly one active selector from `videoId`, `allThreadsRelatedToChannelId`, or `id`
- Supported requests may include only the documented optional modifiers for this slice
- Unexpected top-level request fields must be rejected before execution

**Relationships**:

- Requires one `Comment Thread Lookup Access Profile`
- Produces one `Comment Threads List Result`

## Entity: Comment Thread Lookup Mode

**Purpose**: Captures the supported retrieval path selected for one `commentThreads.list` request.

**Fields**:

- `selector_name`: The selector field that activates the path, expected to be `videoId`, `allThreadsRelatedToChannelId`, or `id`
- `lookup_goal`: Whether the request fetches threads for one video, threads related to one channel, or one or more specific thread resources
- `selector_scope`: Whether the request targets a single video, a single channel-related discussion space, or one or more explicit thread identifiers
- `access_expectation`: The supported auth expectation for the path
- `review_note`: Maintainer-facing explanation of when to use the path

**Validation Rules**:

- Exactly one lookup mode may be active per supported request
- The lookup mode must remain deterministic and must not silently fall back to another path
- Review notes must stay specific enough for later Layer 2 and Layer 3 reuse decisions

**Relationships**:

- Activated by one `Comment Threads List Request`
- Informs one `Comment Thread Lookup Access Profile`

## Entity: Comment Thread Lookup Access Profile

**Purpose**: Captures the auth expectation and failure categorization for one `commentThreads.list` request path.

**Fields**:

- `auth_mode`: Supported access label for the wrapper
- `requires_api_key_access`: Whether the request depends on API-key-capable retrieval
- `selector_name`: The supported selector governed by the profile
- `failure_boundary`: Expected distinction between `invalid_request`, `auth`, and successful no-match outcomes
- `eligibility_note`: Maintainer-facing explanation of the path's supported access boundary

**Validation Rules**:

- The supported seed-required selector paths must remain reviewable as public retrieval paths for this slice
- Auth mismatch behavior must remain distinguishable from invalid selector-shape failures
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Comment Threads List Wrapper Contract`
- Used to interpret `Comment Threads List Result`

## Entity: Comment Threads List Result

**Purpose**: Represents normalized output for one valid `commentThreads.list` request.

**Fields**:

- `items`: Returned comment-thread resources for the request
- `nextPageToken`: Optional continuation token when another result page exists
- `selector_used`: Stable selector label used by the request
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with one or more items, success with zero items, or normalized failure outcome

**Validation Rules**:

- Valid requests must produce either a successful retrieval result or a normalized failure
- Empty item lists for valid requests must remain on the success path
- Result handling must preserve source operation and quota visibility needed by higher layers
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Comment Threads List Wrapper Contract`
- Interpreted alongside one `Comment Thread Lookup Mode`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but selector rules and access guidance are incomplete
2. `reviewable`: Quota, selector rules, optional modifiers, access expectations, and empty-result guidance are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm selector and retrieval behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one `commentThreads.list` request with `part` and one selector
2. Wrapper validates required fields, selector exclusivity, and optional modifier boundaries
3. Access compatibility is evaluated for the selected lookup mode
4. Shared executor performs the retrieval for valid requests
5. Outcome ends as `successful retrieval with items`, `successful retrieval with no matches`, `normalized invalid_request`, or `normalized auth failure`
