# Data Model: YT-240 Layer 2 Tool `search_list`

## Search List Tool

**Purpose**: Public Layer 2 MCP tool that exposes the low-level `search.list` operation.

**Fields**:
- `tool_name`: Stable public name, expected to be `search_list`
- `resource`: Upstream resource identity, expected to be `search`
- `method`: Upstream method identity, expected to be `list`
- `operation_key`: Caller-visible endpoint identity, expected to be `search.list`
- `quota_cost`: Official quota-unit cost, expected to be `100`
- `auth_mode`: Conditional access disclosure for API-key public search and OAuth-backed restricted search
- `availability_state`: Caller-visible endpoint availability state and any quota documentation caveat
- `input_contract`: Search List Request contract
- `response_convention`: Search List Result convention
- `examples`: Representative success and failure examples

**Validation Rules**:
- Must be discoverable as `search_list`
- Must identify `search.list` in discovery metadata, description, usage notes, and examples
- Must show quota cost `100` in metadata, description, usage notes, examples, and result context
- Must show conditional auth expectations before invocation
- Must not describe video hydration, channel hydration, playlist hydration, transcript retrieval, analytics, ranking, summarization, recommendation, research synthesis, or cross-endpoint enrichment as part of this tool

## Search List Request

**Purpose**: Caller-provided request for one supported search operation.

**Fields**:
- `part`: Required search response part selection supported by the Layer 1 wrapper
- `q`: Required search query string for baseline supported searches
- `type`: Optional result type selection, including video-specific compatibility behavior
- `channelId`: Optional channel-scoped search refinement
- `publishedAfter`: Optional lower date bound
- `publishedBefore`: Optional upper date bound
- `regionCode`: Optional region refinement
- `relevanceLanguage`: Optional language refinement
- `safeSearch`: Optional safe-search refinement
- `order`: Optional ordering refinement
- `pageToken`: Optional continuation token for compatible searches
- `maxResults`: Optional maximum result count within official limits
- `forContentOwner`: Optional restricted OAuth-backed selector
- `forDeveloper`: Optional restricted OAuth-backed selector
- `forMine`: Optional restricted OAuth-backed selector
- `videoCaption`: Optional video-only refinement
- `videoDefinition`: Optional video-only refinement
- `videoDuration`: Optional video-only refinement
- `videoEmbeddable`: Optional video-only refinement
- `videoLicense`: Optional video-only refinement
- `videoPaidProductPlacement`: Optional video-only refinement
- `videoSyndicated`: Optional video-only refinement
- `videoType`: Optional video-only refinement

**Validation Rules**:
- `part` and `q` are required for the supported public baseline contract
- Unsupported fields, unsupported modifiers, resource hydration instructions, transcript inputs, analytics inputs, ranking instructions, summarization instructions, and higher-level workflow requests must be rejected before endpoint execution
- `forContentOwner`, `forDeveloper`, and `forMine` require eligible OAuth-backed access and are mutually exclusive
- Video-specific refinements require `type=video`
- Pagination inputs must be valid and compatible with the search context
- API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Search Criteria

**Purpose**: Represents the caller's intended search target.

**Fields**:
- `part`: Selected response parts
- `query`: Search query from `q`
- `selected_type`: Result type from `type`, when provided
- `channel_scope`: Channel context from `channelId`, when provided
- `date_window`: Published date bounds from `publishedAfter` and `publishedBefore`, when provided
- `locale_scope`: Language and region context from `relevanceLanguage` and `regionCode`, when provided
- `restricted_selector`: One of `forContentOwner`, `forDeveloper`, or `forMine`, when provided

**Validation Rules**:
- Must include the required supported baseline fields
- Must preserve only safe caller-provided context in results
- Missing, malformed, duplicated, conflicting, or unsupported search criteria must fail validation before endpoint execution

## Search Filter Mode

**Purpose**: Represents supported refinements that shape a search request.

**Fields**:
- `result_type`
- `channel_filter`
- `date_filter`
- `language_filter`
- `region_filter`
- `safe_search_filter`
- `order_filter`
- `restricted_filter`
- `video_only_filter`

**Validation Rules**:
- Restricted filters are mutually exclusive and require OAuth-backed access
- Video-only filters require `type=video`
- Unsupported or incompatible filter combinations must be rejected with caller-facing detail

## Pagination Context

**Purpose**: Represents caller-provided and returned page information for search result traversal.

**Fields**:
- `request_page_token`: Caller-provided `pageToken`, when present
- `request_max_results`: Caller-provided `maxResults`, when present
- `next_page_token`: Returned continuation token, when present
- `previous_page_token`: Returned previous-page token, when present

**Validation Rules**:
- `maxResults` must be within supported official limits
- `pageToken` must be non-empty when provided
- Returned pagination fields must not imply compatibility with different search criteria

## Access Context

**Purpose**: Represents the caller access state used to execute public or restricted search without exposing credentials.

**Fields**:
- `mode`: API-key public access or OAuth-backed restricted access
- `auth_path`: Safe category such as `public` or `restricted`
- `credential_present`: Safe boolean or category indicating whether required access material was available

**Validation Rules**:
- Baseline public search requests use API-key access
- Restricted search requests require eligible OAuth-backed access
- Missing, invalid, or insufficient access must be reported as access failure, not a validation failure or successful result
- Raw API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Search Result Record

**Purpose**: A returned search item visible for the selected criteria and filters.

**Fields**:
- `kind`: Returned item kind, when present
- `etag`: Returned item tag, when present
- `id`: Returned search result identifier object, when present
- `snippet`: Returned snippet fields, when requested and present

**Validation Rules**:
- Must preserve returned endpoint fields without fabricating hydrated resource details
- Missing optional fields must remain absent rather than being invented from request context

## Search List Result

**Purpose**: Successful result for a `search_list` call.

**Fields**:
- `endpoint`: Expected to be `search.list`
- `quotaCost`: Expected to be `100`
- `items`: Search result records returned by the endpoint
- `empty`: Boolean marker for successful empty collections
- `queryContext`: Safe submitted criteria and filter context
- `pagination`: Returned pagination context, when applicable
- `auth`: Safe access mode context

**Validation Rules**:
- Must distinguish successful populated results from successful empty results
- Must preserve returned fields, query context, quota context, access context, and pagination context
- Must not expose credentials, raw upstream diagnostics, stack traces, unsafe request context, or fabricated hydrated resource details

## Search List Failure

**Purpose**: Caller-facing failure for invalid, ineligible, or unsuccessful search requests.

**Fields**:
- `category`: Safe failure category such as invalid request, authentication failure, authorization failure, quota exhausted, endpoint unavailable, deprecated behavior, or unexpected upstream failure
- `message`: Caller-actionable summary
- `details`: Sanitized field or search context

**Validation Rules**:
- Must distinguish local validation failures from access failures and upstream failures
- Must sanitize credential material, stack traces, raw upstream bodies, and unsafe diagnostics
- Must identify the invalid field or search input when doing so is safe

## State Transitions

1. Caller submits request.
2. Tool validates required `part` and `q`.
3. Tool rejects unsupported fields, unsupported modifiers, hydration instructions, transcript inputs, analytics inputs, ranking instructions, summarization instructions, or higher-level workflow requests.
4. Tool validates restricted filter and video-only filter compatibility.
5. Tool validates API-key or OAuth-backed access availability based on the selected search path.
6. Tool executes the existing Layer 1 `search.list` wrapper once for valid requests.
7. Successful upstream result maps to Search List Result, including empty successful results.
8. Local validation, access, quota, unavailable-service, deprecated, or unexpected upstream failures map to Search List Failure.
