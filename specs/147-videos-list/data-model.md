# Data Model: YT-147 Layer 1 Endpoint `videos.list`

## Entity: Videos List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `videos.list` so maintainers can review endpoint identity, quota cost, mixed-auth behavior, selector rules, collection-refinement limits, and result interpretation before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `videos`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields, mutually exclusive selectors, and endpoint-specific validators
- `auth_mode`: Stable auth mode for this wrapper, expected to remain mixed or conditional
- `auth_condition_note`: Maintainer-facing explanation of which selectors use public access versus OAuth-required access
- `quota_cost`: Official quota-unit cost of `1`
- `notes`: Maintainer-facing notes covering selector choice, paging limits, chart refinements, and empty-result interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as mixed or conditional access for this feature scope
- `auth_condition_note` must explain the selector-specific auth split
- Contract notes must keep `part`, selector rules, chart refinements, and empty-result interpretation reviewable

**Relationships**:

- Uses one `Videos List Request`
- Applies one `Video Selector Context`
- Produces one `Video Retrieval Result`

## Entity: Videos List Request

**Purpose**: Represents one supported `videos.list` request.

**Fields**:

- `part`: Requested response sections for one retrieval attempt
- `id`: Optional direct-video selector for exact video lookup
- `chart`: Optional collection selector for chart-oriented video retrieval
- `myRating`: Optional personal-rating selector for caller-specific video retrieval
- `pageToken`: Optional continuation token for collection-style retrieval
- `maxResults`: Optional page-size hint for collection-style retrieval
- `regionCode`: Optional regional refinement for chart-based retrieval
- `videoCategoryId`: Optional category refinement for chart-based retrieval

**Validation Rules**:

- Every supported request must include one non-empty `part` value
- Every supported request must include exactly one non-empty selector from `id`, `chart`, or `myRating`
- `pageToken` and `maxResults` may be present only for collection-style selectors
- `regionCode` and `videoCategoryId` must remain constrained to the chart-oriented retrieval path for this slice
- No undocumented top-level request fields may be accepted for this slice
- The request must remain deterministic and must not be silently expanded to another lookup profile

**Relationships**:

- Requires one `Video Selector Context`
- Produces one `Video Retrieval Result`

## Entity: Video Selector Context

**Purpose**: Captures how one `videos.list` request should be interpreted for review and downstream reuse.

**Fields**:

- `selector_type`: Whether the request is direct `id` lookup, chart retrieval, or personal-rating retrieval
- `selector_value`: The specific `id`, `chart`, or `myRating` value chosen for the request
- `auth_path`: Whether the request follows the public-compatible access path or the OAuth-required path
- `collection_mode`: Whether paging and volume-oriented interpretation are expected
- `region_refinement`: Optional region context when chart retrieval is refined geographically
- `category_refinement`: Optional category context when chart retrieval is refined by video category
- `review_note`: Maintainer-facing explanation of when the selected lookup path should be used
- `empty_result_interpretation`: Guidance for how to treat valid requests that return zero videos

**Validation Rules**:

- The selector context must remain tied to exactly one selector value
- Review notes must keep the difference between direct lookup, chart retrieval, and personal-rating retrieval explicit
- Auth-path guidance must remain visible whenever the selected path changes access expectations
- Optional chart refinements must remain distinguishable from the primary selector
- Empty-result interpretation must remain distinguishable from invalid request handling

**Relationships**:

- Activated by one `Videos List Request`
- Interpreted alongside one `Video Retrieval Result`

## Entity: Video Retrieval Result

**Purpose**: Represents normalized output for one valid `videos.list` request.

**Fields**:

- `items`: Returned video resources for the request
- `selected_selector`: Stable indicator of whether the request used `id`, `chart`, or `myRating`
- `id`: Echoed direct-video selector when the exact-lookup path is used
- `chart`: Echoed chart selector when the chart path is used
- `myRating`: Echoed rating selector when the personal path is used
- `regionCode`: Echoed regional refinement when provided for chart retrieval
- `videoCategoryId`: Echoed category refinement when provided for chart retrieval
- `pageToken`: Echoed paging cursor when provided
- `nextPageToken`: Returned continuation token for collection-style retrieval when available
- `auth_path`: Stable indicator of the access path used for the request
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with one or more items or success with zero items

**Validation Rules**:

- Valid requests must produce a successful retrieval result even when `items` is empty
- Result handling must preserve source operation, quota visibility, selector context, auth-path context, and any supported optional refinements needed by higher layers
- Invalid requests must remain distinct from valid success outcomes

**Relationships**:

- Produced by one `Videos List Wrapper Contract`
- Interpreted alongside one `Video Selector Context`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but selector rules or mixed-auth guidance are incomplete
2. `reviewable`: Quota, mixed-auth access expectations, `part` plus selector rules, and collection-refinement notes are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm request and result behavior
4. `reusable`: Higher-layer authors can judge whether to reuse the wrapper without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one `videos.list` request with `part`, exactly one selector, and any compatible optional refinements
2. Wrapper validates required fields, selector exclusivity, auth-path expectations, and rejects undocumented or incompatible inputs
3. Selector context, auth path, and any supported refinements are preserved for execution and review surfaces
4. Shared executor performs the retrieval for valid requests
5. Outcome ends as `successful retrieval with items`, `successful retrieval with no matches`, or `normalized invalid_request`
