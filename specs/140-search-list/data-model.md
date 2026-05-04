# Data Model: YT-140 Layer 1 Endpoint `search.list`

## Entity: Search List Wrapper Contract

**Purpose**: Describes the internal Layer 1 wrapper contract for `search.list` so maintainers can review endpoint identity, quota cost, quota caveat, supported search inputs, conditional-auth behavior, and normalized search boundaries before implementation details are inspected.

**Fields**:

- `resource_name`: Upstream resource name, expected to remain `search`
- `operation_name`: Upstream operation name, expected to remain `list`
- `operation_key`: Stable combined identifier used in review and tests
- `http_method`: Upstream HTTP method for this wrapper
- `path_shape`: Upstream route pattern for this wrapper
- `request_shape`: Supported request fields and endpoint-specific validators for search execution
- `auth_mode`: Stable auth mode for this wrapper, expected to remain mixed or conditional
- `quota_cost`: Official quota-unit cost of `100`
- `lifecycle_state`: Reviewable lifecycle label for known documentation caveats
- `auth_condition_note`: Maintainer-facing explanation of when restricted filters require stronger authorization
- `caveat_note`: Maintainer-facing explanation of the known search quota-guidance inconsistency
- `notes`: Maintainer-facing notes covering supported search refinements, empty-result behavior, and unsupported-request guidance

**Validation Rules**:

- `resource_name`, `operation_name`, `operation_key`, `http_method`, `path_shape`, `request_shape`, `auth_mode`, and `quota_cost` are required
- `quota_cost` must equal the official endpoint cost captured for this slice
- `auth_mode` must remain conditional and must include a non-empty `auth_condition_note`
- `lifecycle_state` must remain reviewable when the quota caveat is present and must include a non-empty `caveat_note`
- Contract notes must include search-type, pagination, date-filtering, language and region refinement guidance plus unsupported-request boundaries

**Relationships**:

- Uses one `Search Request`
- Applies one `Search Access Profile`
- Applies one `Search Refinement Profile`
- Produces one `Search Result Set`

## Entity: Search Request

**Purpose**: Represents one supported `search.list` request.

**Fields**:

- `part`: Required upstream part selection for the search request
- `q`: Required search query string for the supported search boundary
- `channelId`: Optional channel-scoped search filter
- `forContentOwner`: Optional restricted filter for content-owner search paths
- `forDeveloper`: Optional restricted filter for developer search paths
- `forMine`: Optional restricted filter for owner-scoped search paths
- `publishedAfter`: Optional lower timestamp bound for search-result recency
- `publishedBefore`: Optional upper timestamp bound for search-result recency
- `regionCode`: Optional region-scoping input
- `relevanceLanguage`: Optional search-language preference input
- `safeSearch`: Optional safe-search preference
- `type`: Optional resource-type selector for search results
- `videoCaption`, `videoDefinition`, `videoDuration`, `videoEmbeddable`, `videoLicense`, `videoPaidProductPlacement`, `videoSyndicated`, `videoType`: Optional video-specific refinements
- `order`: Optional upstream ordering selector
- `pageToken`: Optional continuation token
- `maxResults`: Optional result-count limit
- `unsupported_fields_policy`: Explicit statement that undocumented top-level request fields are outside this feature's promised contract

**Validation Rules**:

- Every supported request must include non-empty `part` and `q`
- Unsupported top-level request fields must be rejected before execution
- Restricted filters must remain distinguishable from public search paths
- `publishedAfter` and `publishedBefore` must follow the repository's ISO 8601 timestamp convention
- Video-specific refinements must not be treated as compatible with unsupported non-video search-type combinations
- Pagination fields must preserve upstream-style semantics rather than being silently remapped

**Relationships**:

- Requires one `Search Access Profile`
- Uses one `Search Refinement Profile`
- Produces one `Search Result Set`

## Entity: Search Access Profile

**Purpose**: Captures the authorization expectations and failure categorization for one `search.list` request path.

**Fields**:

- `auth_mode`: Mixed or conditional auth label for the wrapper
- `public_search_path`: Maintainer-facing note describing the default API-key path for normal search requests
- `restricted_filter_path`: Maintainer-facing note describing the stronger-authorization path for restricted filters
- `conditional_reason`: Reviewable explanation attached when a request enters the restricted filter path
- `failure_boundary`: Expected distinction between `invalid_request`, restricted-auth failure, empty-result success, and normalized upstream search failure

**Validation Rules**:

- Public search requests must remain valid with API-key access
- Restricted filter paths must require stronger authorization and remain distinguishable from malformed requests
- Auth mismatch behavior must remain reviewable as a separate outcome from unsupported refinement combinations
- Secrets or credential material must never appear in review artifacts

**Relationships**:

- Applied by `Search List Wrapper Contract`
- Used to interpret `Search Result Set`

## Entity: Search Refinement Profile

**Purpose**: Defines the reviewable refinement categories supported by this `search.list` slice so downstream layers can understand which search combinations are valid.

**Fields**:

- `search_type_scope`: Supported `type` values and the behaviors they activate
- `pagination_scope`: Supported use of `pageToken` and `maxResults`
- `date_filter_scope`: Supported use of `publishedAfter` and `publishedBefore`
- `language_region_scope`: Supported use of `relevanceLanguage` and `regionCode`
- `video_filter_scope`: Supported use of video-only refinements and the conditions under which they are valid
- `order_scope`: Supported ordering inputs when explicitly documented
- `unsupported_combination_policy`: Maintainer-facing explanation of which refinement combinations fall outside the promised contract

**Validation Rules**:

- Search-type guidance must stay specific enough to explain when video-only refinements are valid
- Pagination guidance must remain distinct from higher-level public parameter remapping
- Date and language or region guidance must remain reviewable without external documentation
- Unsupported combination policy must remain deterministic and testable

**Relationships**:

- Interpreted alongside one `Search Request`
- Influences one `Search Result Set`

## Entity: Search Result Set

**Purpose**: Represents the normalized result of one valid `search.list` request.

**Fields**:

- `items`: Returned search-result items from the supported request
- `next_page_token`: Continuation token when the upstream search provides one
- `search_context`: Stable summary of the request context needed for downstream interpretation
- `source_operation`: Stable operation identifier for review and downstream mapping
- `quota_visibility`: Whether quota metadata remains visible in review surfaces
- `result_state`: Success with items, success with empty results, or normalized failure outcome
- `auth_path_used`: Reviewable label for whether the request used the public or restricted-auth path

**Validation Rules**:

- Valid requests must produce either a successful search result set or a normalized failure
- Empty result sets must remain successful outcomes rather than failure outcomes
- Result handling must preserve source operation and quota visibility needed by higher layers
- Failure outcomes must preserve distinctions required by downstream callers

**Relationships**:

- Produced by one `Search List Wrapper Contract`
- Interpreted alongside one `Search Access Profile` and one `Search Refinement Profile`

## State Transitions

### Wrapper Review Lifecycle

1. `draft`: Endpoint metadata exists but search refinement, auth, or quota-caveat notes are incomplete
2. `reviewable`: Quota, quota caveat, auth requirements, required search inputs, and refinement boundaries are visible together
3. `validated`: Unit, contract, integration, and transport checks confirm search-shape and auth behavior
4. `reusable`: Higher-layer authors can reuse wrapper behavior without additional endpoint research

### Request Outcome Lifecycle

1. Caller submits one search request with required `part` and `q`
2. Wrapper validates required fields, unsupported-field rejection, and refinement compatibility
3. Auth compatibility is evaluated for the request path
4. Shared executor performs the search for valid supported requests
5. Outcome ends as `search results returned`, `empty results returned`, `normalized invalid_request`, `normalized restricted-auth failure`, or `normalized upstream search failure`
