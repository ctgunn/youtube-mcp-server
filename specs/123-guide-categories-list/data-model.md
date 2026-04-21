# Data Model: YT-123 Layer 1 Endpoint `guideCategories.list`

## Entity: Guide Categories List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `guideCategories.list` so maintainers can review endpoint identity, quota cost, API-key access behavior, request boundaries, lifecycle caveat handling, and result interpretation before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `guideCategories`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for one guide-category lookup
- `auth_mode`: Stable auth mode for this wrapper, expected to remain API-key access
- `quota_cost`: Official quota-unit cost of `1`
- `lifecycle_state`: Reviewable lifecycle label for the wrapper, expected to remain `deprecated` for this slice
- `caveat_note`: Maintainer-facing note describing deprecated or unavailable endpoint behavior
- `notes`: Additional maintainer-facing notes covering request boundaries, empty-result behavior, and failure interpretation

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, `quota_cost`, and `lifecycle_state` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain reviewable as API-key access for this feature scope
- `lifecycle_state` must require a visible `caveat_note`
- Contract notes must keep `part` plus `regionCode` guidance and lifecycle-aware failure handling reviewable

**Relationships**:

- Uses one `Guide Categories List Request`
- Applies one `Guide Categories Lifecycle Profile`
- Produces one `Guide Categories List Result`

## Entity: Guide Categories List Request

**Purpose**: Represents one supported `guideCategories.list` request.

**Fields**:

- `part`: Requested response sections for one retrieval attempt
- `regionCode`: Region identifier used to scope guide-category lookup

**Validation Rules**:

- Every supported request must include one non-empty `part` value
- Every supported request must include one non-empty `regionCode` value
- No undocumented top-level request fields may be accepted for this slice
- The request must remain deterministic and must not be silently expanded to undocumented lookup behavior

**Relationships**:

- Requires one `Guide Category Region Profile`
- Interpreted with one `Guide Categories Lifecycle Profile`
- Produces one `Guide Categories List Result`

## Entity: Guide Category Region Profile

**Purpose**: Captures the requested region scope for one `guideCategories.list` lookup.

**Fields**:

- `region_code`: The requested region identifier
- `lookup_goal`: Region-scoped guide-category discovery
- `review_note`: Maintainer-facing explanation of when the region lookup path should be used
- `empty_result_interpretation`: Guidance for how to treat valid requests that return zero categories

**Validation Rules**:

- The region profile must remain tied to exactly one `regionCode` value
- Review notes must stay specific enough for later Layer 2 and Layer 3 reuse decisions
- Empty-result interpretation must remain distinguishable from lifecycle-aware unavailable endpoint behavior

**Relationships**:

- Activated by one `Guide Categories List Request`
- Interpreted alongside one `Guide Categories Lifecycle Profile`

## Entity: Guide Categories Lifecycle Profile

**Purpose**: Captures the deprecated-or-unavailable caveat and failure interpretation for `guideCategories.list`.

**Fields**:

- `lifecycle_state`: Reviewable lifecycle label, expected to remain `deprecated`
- `caveat_note`: Maintainer-facing explanation of deprecated or unavailable platform behavior
- `recommended_reuse_boundary`: Guidance explaining when downstream layers should avoid relying on this endpoint
- `failure_boundary`: Expected distinction between `invalid_request`, lifecycle-aware unavailable outcomes, and successful retrieval results

**Validation Rules**:

- The lifecycle profile must remain visible in maintainer-facing metadata and contract artifacts
- The caveat note must explain why the endpoint should not be treated as a normal always-available lookup surface
- Failure guidance must keep lifecycle-aware unavailable behavior distinct from malformed requests and successful empty results
- Lifecycle notes must not expose secrets or implementation-only transport details

**Relationships**:

- Applied by `Guide Categories List Wrapper Contract`
- Used to interpret `Guide Categories List Result`

## Entity: Guide Categories List Result

**Purpose**: Represents normalized output for one valid `guideCategories.list` request.

**Fields**:

- `items`: Returned guide-category resources for the request
- `regionCode`: Stable region identifier echoed for review and downstream mapping
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `lifecycle_visibility`: Whether lifecycle caveat metadata remains visible in review surfaces
- `result_state`: Success with one or more items, success with zero items, or normalized lifecycle-aware failure outcome

**Validation Rules**:

- Valid requests must produce either a successful retrieval result or a normalized failure
- Empty item lists for valid requests must remain on the success path
- Result handling must preserve source operation, quota visibility, and lifecycle visibility needed by higher layers
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Guide Categories List Wrapper Contract`
- Interpreted alongside one `Guide Category Region Profile`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but request boundaries or lifecycle caveat guidance are incomplete
2. `reviewable`: Quota, API-key access, `part` plus `regionCode` rules, and deprecated-or-unavailable caveat are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm request and lifecycle behavior
4. `reusable-with-caution`: Higher-layer authors can judge whether to reuse or avoid the wrapper without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one `guideCategories.list` request with `part` and `regionCode`
2. Wrapper validates required fields and rejects undocumented inputs
3. Lifecycle caveat context is preserved for the execution and review surfaces
4. Shared executor performs the retrieval for valid requests
5. Outcome ends as `successful retrieval with items`, `successful retrieval with no matches`, `normalized invalid_request`, or `normalized lifecycle-aware unavailable`
