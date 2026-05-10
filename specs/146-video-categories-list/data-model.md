# Data Model: YT-146 Layer 1 Endpoint `videoCategories.list`

## Entity: Video Categories List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `videoCategories.list` so maintainers can review endpoint identity, quota cost, API-key access behavior, selector rules, region guidance, optional display-language usage, and result interpretation before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `videoCategories`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields, mutually exclusive selectors, and endpoint-specific validators
- `auth_mode`: Stable auth mode for this wrapper, expected to remain API-key access
- `quota_cost`: Official quota-unit cost of `1`
- `notes`: Maintainer-facing notes covering selector choice, region behavior, optional `hl` usage, and empty-result interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as API-key access for this feature scope
- Contract notes must keep `part`, selector rules, optional `hl` behavior, and empty-result interpretation reviewable

**Relationships**:

- Uses one `Video Categories List Request`
- Applies one `Video Category Selector Context`
- Produces one `Video Category Retrieval Result`

## Entity: Video Categories List Request

**Purpose**: Represents one supported `videoCategories.list` request.

**Fields**:

- `part`: Requested response sections for one retrieval attempt
- `id`: Optional category identifier selector for direct category lookup
- `regionCode`: Optional region selector for browsing category availability in one region
- `hl`: Optional display-language hint used to request more readable category metadata where supported

**Validation Rules**:

- Every supported request must include one non-empty `part` value
- Every supported request must include exactly one non-empty selector from `id` or `regionCode`
- `hl` may be present only as an optional hint and must not replace the required selector
- No undocumented top-level request fields may be accepted for this slice
- The request must remain deterministic and must not be silently expanded to undocumented lookup behavior

**Relationships**:

- Requires one `Video Category Selector Context`
- Produces one `Video Category Retrieval Result`

## Entity: Video Category Selector Context

**Purpose**: Captures how one `videoCategories.list` request should be interpreted for review and downstream reuse.

**Fields**:

- `selector_type`: Whether the request is a direct category-id lookup or a region-scoped category browse
- `selector_value`: The specific `id` or `regionCode` value chosen for the request
- `display_language`: Optional `hl` value when the caller asks for display-language guidance
- `lookup_goal`: Category review, video categorization support, or region-aware category discovery for downstream layers
- `review_note`: Maintainer-facing explanation of when the selected lookup path should be used
- `empty_result_interpretation`: Guidance for how to treat valid requests that return zero categories

**Validation Rules**:

- The selector context must remain tied to exactly one selector value
- Review notes must keep the difference between direct category lookup and region browsing explicit
- Optional `hl` behavior must remain distinguishable from the primary selector
- Empty-result interpretation must remain distinguishable from invalid request handling

**Relationships**:

- Activated by one `Video Categories List Request`
- Interpreted alongside one `Video Category Retrieval Result`

## Entity: Video Category Retrieval Result

**Purpose**: Represents normalized output for one valid `videoCategories.list` request.

**Fields**:

- `items`: Returned video-category resources for the request
- `selected_selector`: Stable indicator of whether the request used `id` or `regionCode`
- `id`: Echoed category identifier when the direct-lookup selector is used
- `regionCode`: Echoed region selector when the region-browse selector is used
- `hl`: Echoed display-language hint when provided
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with one or more items or success with zero items

**Validation Rules**:

- Valid requests must produce a successful retrieval result even when `items` is empty
- Result handling must preserve source operation, quota visibility, selector context, and any provided display-language hint needed by higher layers
- Invalid requests must remain distinct from valid success outcomes

**Relationships**:

- Produced by one `Video Categories List Wrapper Contract`
- Interpreted alongside one `Video Category Selector Context`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but selector rules or region guidance are incomplete
2. `reviewable`: Quota, API-key access, `part` plus selector rules, and region notes are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm request and result behavior
4. `reusable`: Higher-layer authors can judge whether to reuse the wrapper without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one `videoCategories.list` request with `part`, exactly one selector, and optional `hl`
2. Wrapper validates required fields, selector exclusivity, and rejects undocumented inputs
3. Selector context and optional display-language hint are preserved for execution and review surfaces
4. Shared executor performs the retrieval for valid requests
5. Outcome ends as `successful retrieval with items`, `successful retrieval with no matches`, or `normalized invalid_request`
