# Data Model: YT-203 Layer 2 Tool `activities_list`

## Activities List Tool

**Purpose**: Represents the public Layer 2 MCP tool that exposes the upstream `activities.list` endpoint.

**Fields**:

- `tool_name`: Always `activities_list`
- `upstream_resource`: Always `activities`
- `upstream_method`: Always `list`
- `operation_key`: Stable identity `activities.list`
- `quota_cost`: Official quota-unit cost `1`
- `auth_mode`: `mixed/conditional`
- `availability_state`: Active with selector-specific caveat for deprecated `home`
- `description`: Caller-facing discovery description that includes upstream identity, quota cost, and auth summary
- `input_schema`: Public request schema for `part`, selector, pagination, and optional filters
- `handler`: Callable behavior that validates, invokes the Layer 1 wrapper, and maps the result
- `usage_notes`: Caller-facing examples and quota/auth/caveat notes
- `response_boundary`: Near-raw endpoint-backed activity collection result

**Validation Rules**:

- Must derive its name from `activities.list` using the shared `resource_method` naming rule
- Must include quota cost `1` in metadata, description, and examples
- Must expose mixed/conditional auth before invocation
- Must not include API keys, OAuth tokens, stack traces, signed URLs, raw media payloads, or secret values in metadata, examples, errors, or logs
- Must remain a single-endpoint Layer 2 tool and must not add cross-endpoint enrichment or ranking

**Relationships**:

- Owns one `Activities List Request`
- Produces one `Activity Collection Result` or one `Activities List Error Outcome`
- Uses one Layer 1 `activities.list` wrapper
- References one `Activities List Metadata Disclosure`

## Activities List Request

**Purpose**: Represents caller input for one `activities_list` invocation.

**Fields**:

- `part`: Required comma-separated activity resource parts; supported values include `contentDetails`, `id`, and `snippet`
- `channelId`: Public channel activity selector
- `mine`: Authorized-user activity selector
- `home`: Deprecated authorized-user home activity selector
- `maxResults`: Optional maximum number of items, bounded by the upstream range `0` through `50`
- `pageToken`: Optional pagination cursor
- `publishedAfter`: Optional lower datetime filter
- `publishedBefore`: Optional upper datetime filter
- `regionCode`: Optional region context used when relevant to authorized activity feeds

**Validation Rules**:

- Must include `part`
- Must include exactly one selector from `channelId`, `mine`, and `home`
- Must reject missing selector requests
- Must reject requests with more than one selector
- Must reject `mine` and `home` requests without eligible user authorization
- Must flag `home` as deprecated in caller-facing metadata or validation guidance
- Must reject unsupported fields when the public schema disallows them
- Must keep pagination and date filters optional and caller-controlled

**Relationships**:

- Selects one `Activity Selector`
- May include one `Pagination Cursor`
- May include zero or more optional date/region filters
- Is validated before Layer 1 wrapper invocation

## Activity Selector

**Purpose**: Identifies which activity feed the caller wants and what authorization is required.

**Fields**:

- `selector_name`: `channelId`, `mine`, or `home`
- `selector_value`: Channel identifier or boolean selector value
- `access_requirement`: Public channel access for `channelId`; eligible user authorization for `mine` and `home`
- `availability_note`: Deprecated caveat for `home` when selected

**Validation Rules**:

- Exactly one selector must be active
- `channelId` must identify the public channel activity path
- `mine` must identify the authenticated user's own activity path
- `home` must identify the deprecated authorized-user home activity path
- Selector validation must not silently rewrite one selector mode into another

**Relationships**:

- Belongs to one `Activities List Request`
- Determines one `Auth Requirement`

## Auth Requirement

**Purpose**: Describes the credential expectation for the selected request before invocation.

**Fields**:

- `auth_mode`: Public or authorized-user path derived from selector
- `condition_note`: Caller-facing explanation of why credentials are or are not required
- `safe_error_category`: Shared error category when eligible authorization is missing

**Validation Rules**:

- Must classify `channelId` as public channel access
- Must classify `mine` and `home` as authorized-user-only access
- Must not expose credential values, token names, or secret configuration details
- Must map missing eligible authorization to a stable caller-facing auth error

**Relationships**:

- Derived from one `Activity Selector`
- Appears in `Activities List Metadata Disclosure`
- May produce one `Activities List Error Outcome`

## Pagination Cursor

**Purpose**: Preserves caller-controlled continuation through upstream activity pages.

**Fields**:

- `pageToken`: Input token for a requested page
- `nextPageToken`: Returned token for the next page when present
- `prevPageToken`: Returned token for the previous page when present
- `pageInfo`: Returned page information when present
- `maxResults`: Optional caller-requested page size

**Validation Rules**:

- Must preserve upstream pagination tokens when present
- Must not auto-fetch additional pages as part of a single Layer 2 call
- Must keep `maxResults` within the supported endpoint range

**Relationships**:

- May be included in one `Activities List Request`
- May be returned in one `Activity Collection Result`

## Activity Collection Result

**Purpose**: Represents a successful near-raw activity list response.

**Fields**:

- `items`: Returned activity resources, possibly empty
- `requested_parts`: Parts requested by the caller
- `nextPageToken`: Optional continuation token
- `prevPageToken`: Optional previous-page token
- `pageInfo`: Optional page information
- `endpoint`: Upstream identity `activities.list`
- `quotaCost`: Official quota-unit cost `1`
- `selector`: Safe summary of the selected request mode

**Validation Rules**:

- Must preserve activity items from the endpoint-backed response
- Must allow an empty `items` collection as a successful result
- Must preserve pagination details when present
- Must preserve requested parts for review/debugging
- Must not add higher-level ranking, enrichment, transcript lookup, channel expansion, or heuristic interpretation

**Relationships**:

- Produced by one valid `Activities List Request`
- May include one `Pagination Cursor`
- References one `Activities List Metadata Disclosure`

## Activities List Error Outcome

**Purpose**: Represents a safe caller-facing failure for invalid requests, auth failures, quota failures, missing resources, unavailable upstream service, or unexpected upstream failures.

**Fields**:

- `category`: Shared safe error category
- `message`: Caller-facing remediation-oriented message
- `details`: Safe request context such as tool name, invalid field, selector mode, or upstream operation

**Validation Rules**:

- Must not include stack traces, API keys, OAuth tokens, secret values, signed URLs, or raw media payloads
- Must distinguish invalid selector input from missing authorization
- Must preserve shared Layer 2 error categories where applicable
- Must not present private authorization failures as ordinary public missing resources

**Relationships**:

- Produced by one invalid or failed `Activities List Request`
- Uses shared YT-201/YT-202 error and safety conventions

## Activities List Metadata Disclosure

**Purpose**: Captures the pre-invocation metadata clients and reviewers need to understand the tool.

**Fields**:

- `name`: `activities_list`
- `upstream`: `activities.list`
- `quotaCost`: `1`
- `authMode`: `mixed/conditional`
- `availabilityState`: Active with deprecated selector caveat for `home`
- `inputContract`: Required `part`, exactly-one selector, optional pagination and filters
- `responseBoundary`: Near-raw list response with light MCP clarity fields
- `usageNotes`: Examples for public channel activity, pagination, empty result handling, and authorization-sensitive selectors

**Validation Rules**:

- Must be visible before invocation
- Must include quota and auth details in both structured metadata and caller-facing text
- Must describe the `home` deprecation caveat
- Must stay aligned with YT-201/YT-202 shared metadata standards

**Relationships**:

- Belongs to the `Activities List Tool`
- References `Activities List Request`, `Auth Requirement`, and `Activity Collection Result`

## Verification Evidence

**Purpose**: Captures proof that the endpoint tool is ready for implementation review.

**Fields**:

- `red_phase_evidence`: Failing or characterization tests added before implementation
- `discovery_contract_checks`: Checks that `activities_list` appears with required metadata
- `request_validation_checks`: Checks for required `part`, exactly-one selector, and unsupported fields
- `auth_checks`: Checks for selector-specific public versus authorized-user behavior
- `result_checks`: Checks for activity items, empty collections, requested parts, and pagination preservation
- `error_checks`: Checks for safe error categories and sanitized details
- `full_suite_command`: `python3 -m pytest`
- `lint_command`: `python3 -m ruff check .`
- `docstring_review`: Confirmation that changed Python functions include reStructuredText docstrings

**Validation Rules**:

- Must include Red-Green-Refactor evidence
- Must include focused checks before full-suite validation
- Must include full repository validation after final code changes
- Must include lint validation after final code changes
- Must identify any official documentation caveats discovered during implementation
