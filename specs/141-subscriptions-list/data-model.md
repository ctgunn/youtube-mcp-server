# Data Model: YT-141 Layer 1 Endpoint `subscriptions.list`

## Entity: Subscriptions List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `subscriptions.list` so maintainers can review endpoint identity, quota cost, selector modes, OAuth behavior, paging and ordering boundaries, and normalized retrieval boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `subscriptions`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and selector exclusivity rules
- `auth_mode`: Stable auth mode for this wrapper, expected to remain mixed or conditional
- `quota_cost`: Official quota-unit cost of `1`
- `auth_condition_note`: Maintainer-facing explanation of which selector modes remain public-compatible and which require OAuth-backed access
- `notes`: Maintainer-facing notes covering selector semantics, collection-versus-direct lookup behavior, paging and ordering boundaries, empty-result behavior, and unsupported-request guidance

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain mixed or conditional and must include a non-empty `auth_condition_note`
- Contract notes must include selector exclusivity, paging and ordering guidance, and under-authorized request interpretation

**Relationships**:

- Uses one `Subscription List Request`
- Applies one `Subscription Selector Profile`
- Applies one `Subscription Access Profile`
- Produces one `Subscription List Result Set`

## Entity: Subscription List Request

**Purpose**: Represents one supported `subscriptions.list` request.

**Fields**:

- `part`: Required upstream part selection for the subscription-list request
- `channelId`: Optional public-compatible channel-scoped selector
- `id`: Optional public-compatible direct subscription identifier selector
- `mine`: Optional owner-scoped selector
- `myRecentSubscribers`: Optional OAuth-backed subscriber-management selector
- `mySubscribers`: Optional OAuth-backed subscriber-management selector
- `pageToken`: Optional continuation token for supported collection-style selectors
- `maxResults`: Optional result-count limit for supported collection-style selectors
- `order`: Optional upstream ordering selector for supported collection-style selectors
- `unsupported_fields_policy`: Explicit statement that undocumented top-level request fields are outside this feature's promised contract

**Validation Rules**:

- Every supported request must include non-empty `part`
- Exactly one selector from `channelId`, `id`, `mine`, `myRecentSubscribers`, or `mySubscribers` must be active
- Unsupported top-level request fields must be rejected before execution
- `pageToken` and `maxResults` must remain tied to supported collection-style retrieval modes
- `order` must remain disallowed or clearly flagged for direct `id` lookup

**Relationships**:

- Requires one `Subscription Selector Profile`
- Requires one `Subscription Access Profile`
- Produces one `Subscription List Result Set`

## Entity: Subscription Selector Profile

**Purpose**: Defines the selector semantics supported by this `subscriptions.list` slice so downstream layers can understand which lookup path is active.

**Fields**:

- `selector_name`: One selector identifier (`channelId`, `id`, `mine`, `myRecentSubscribers`, or `mySubscribers`)
- `selector_type`: Public-compatible, owner-scoped, or subscriber-management retrieval path
- `auth_requirement`: Required auth mode for the selector path
- `paging_support`: Whether `pageToken` and `maxResults` are supported for the path
- `ordering_support`: Whether `order` is supported for the path
- `combination_rule`: Declares selector exclusivity for this feature

**Validation Rules**:

- Public-compatible selectors must map to public retrieval expectations
- Owner-scoped and subscriber-management selectors must map to OAuth-backed expectations
- Selector combinations must remain mutually exclusive
- Collection-style selectors must keep paging and ordering support explicit and reviewable

**Relationships**:

- Referenced by `Subscription List Request`
- Referenced by `Subscription Access Profile`
- Summarized by `Subscriptions List Wrapper Contract`

## Entity: Subscription Access Profile

**Purpose**: Captures the authorization expectations and failure categorization for one `subscriptions.list` request path.

**Fields**:

- `auth_mode`: Mixed or conditional auth label for the wrapper
- `public_selector_paths`: Maintainer-facing note describing the public-compatible selector modes
- `oauth_selector_paths`: Maintainer-facing note describing the owner-scoped and subscriber-management selector modes
- `conditional_reason`: Reviewable explanation attached when a request enters an OAuth-backed path
- `failure_boundary`: Expected distinction between `invalid_request`, access-related failure, empty-result success, and normalized upstream subscription failure

**Validation Rules**:

- Public-compatible selector paths must remain distinguishable from OAuth-backed paths
- Auth mismatch behavior must remain reviewable as a separate outcome from unsupported selector, paging, or ordering combinations
- Empty result sets must remain successful outcomes rather than failure outcomes
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Subscriptions List Wrapper Contract`
- Used to interpret `Subscription List Result Set`

## Entity: Subscription List Result Set

**Purpose**: Represents the normalized result of one valid `subscriptions.list` request.

**Fields**:

- `items`: Returned subscription items from the supported request
- `next_page_token`: Continuation token when the upstream response provides one
- `selector_used`: Stable label for the selector mode that produced the returned items
- `request_context`: Stable summary of the request context needed for downstream interpretation
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with items, success with empty results, or normalized failure outcome
- `auth_path_used`: Reviewable label for whether the request used a public-compatible or OAuth-backed path

**Validation Rules**:

- Valid requests must produce either a successful subscription result set or a normalized failure
- Empty result sets must remain successful outcomes rather than failure outcomes
- Result handling must preserve source operation, selector context, and quota visibility needed by higher layers
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Subscriptions List Wrapper Contract`
- Interpreted alongside one `Subscription Selector Profile` and one `Subscription Access Profile`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but selector, OAuth, or paging guidance is incomplete
2. `reviewable`: Quota, selector set, selector-auth mapping, and paging or ordering boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm selector and access behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one subscription-list request with required `part` and one selector profile
2. Wrapper validates required fields, selector exclusivity, and paging or ordering compatibility
3. Auth compatibility is evaluated for the selected path
4. Shared executor performs retrieval for valid supported requests
5. Outcome ends as `subscription results returned`, `empty results returned`, `normalized invalid_request`, `normalized access-related failure`, or `normalized upstream subscription failure`
