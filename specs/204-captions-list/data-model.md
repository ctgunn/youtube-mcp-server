# Data Model: YT-204 Layer 2 Tool `captions_list`

## Captions List Tool

**Purpose**: Represents the public Layer 2 MCP tool that exposes the upstream `captions.list` endpoint.

**Fields**:

- `tool_name`: Always `captions_list`
- `upstream_resource`: Always `captions`
- `upstream_method`: Always `list`
- `operation_key`: Stable identity `captions.list`
- `quota_cost`: Official quota-unit cost `50`
- `auth_mode`: `oauth_required`
- `availability_state`: Active, with caption access and delegated-owner caveats visible
- `description`: Caller-facing discovery description that includes upstream identity, quota cost, and auth summary
- `input_schema`: Public request schema for `part`, `videoId`, optional `id`, pagination, and delegation context
- `handler`: Callable behavior that validates, invokes the Layer 1 wrapper, and maps the result
- `usage_notes`: Caller-facing examples and quota/auth/delegation notes
- `response_boundary`: Near-raw endpoint-backed caption-track collection result

**Validation Rules**:

- Must derive its name from `captions.list` using the shared `resource_method` naming rule
- Must include quota cost `50` in metadata, description, and examples
- Must expose OAuth-required auth before invocation
- Must not include API keys, OAuth tokens, stack traces, signed URLs, raw media payloads, caption file contents, or secret values in metadata, examples, errors, or logs
- Must remain a single-endpoint Layer 2 tool and must not add transcript download, language ranking, enrichment, or cross-endpoint composition

**Relationships**:

- Owns one `Captions List Request`
- Produces one `Caption Track Collection Result` or one `Captions List Error Outcome`
- Uses one Layer 1 `captions.list` wrapper
- References one `Captions List Metadata Disclosure`

## Captions List Request

**Purpose**: Represents caller input for one `captions_list` invocation.

**Fields**:

- `part`: Required comma-separated caption resource parts; supported values include `id` and `snippet`
- `videoId`: Required video identifier whose caption tracks are listed
- `id`: Optional comma-separated caption track identifiers used to narrow the lookup
- `maxResults`: Optional maximum number of items, bounded by the upstream range `0` through `50`
- `pageToken`: Optional pagination cursor
- `onBehalfOfContentOwner`: Optional delegated content-owner context for authorized callers

**Validation Rules**:

- Must include `part`
- Must include `videoId`
- Must require eligible OAuth authorization
- Must reject missing OAuth authorization before endpoint execution
- Must reject unsupported fields when the public schema disallows them
- Must keep pagination caller-controlled and must not auto-fetch additional pages
- Must preserve `id` as an optional narrowing input, not as a replacement for `videoId`
- Must validate delegated content-owner context without exposing credential details

**Relationships**:

- Uses one `OAuth Requirement`
- May include one `Caption Track Identifier Filter`
- May include one `Pagination Cursor`
- May include one `Delegation Context`
- Is validated before Layer 1 wrapper invocation

## Caption Track Identifier Filter

**Purpose**: Narrows a caption listing request to one or more known caption track identifiers.

**Fields**:

- `id`: One or more caption track identifiers
- `videoId`: Required video context that scopes the identifier lookup

**Validation Rules**:

- Must not replace the required `videoId`
- Must be treated as an optional lookup filter
- Must not trigger caption download or content retrieval

**Relationships**:

- Belongs to one `Captions List Request`
- Affects the returned `Caption Track Collection Result`

## OAuth Requirement

**Purpose**: Describes the credential expectation for caption listing before invocation.

**Fields**:

- `auth_mode`: Always `oauth_required`
- `condition_note`: Caller-facing explanation that caption listing requires eligible access to the target video's captions
- `safe_error_category`: Shared error category when eligible authorization is missing or insufficient

**Validation Rules**:

- Must not present `captions_list` as API-key-compatible
- Must not expose credential values, token names, or secret configuration details
- Must map missing eligible authorization to a stable caller-facing auth error
- Must distinguish insufficient caption access from true empty caption-track results

**Relationships**:

- Applies to every `Captions List Request`
- Appears in `Captions List Metadata Disclosure`
- May produce one `Captions List Error Outcome`

## Delegation Context

**Purpose**: Represents optional content-owner delegation supplied by authorized callers.

**Fields**:

- `onBehalfOfContentOwner`: Optional content-owner identifier
- `authorization_note`: Caller-facing explanation that delegation still requires eligible OAuth authorization

**Validation Rules**:

- Must be optional
- Must not be accepted as a substitute for OAuth authorization
- Must not expose delegated-owner secrets or credential details
- Must be preserved only as safe request context or metadata when useful

**Relationships**:

- May belong to one `Captions List Request`
- May appear as safe context in one `Caption Track Collection Result`
- May produce one `Captions List Error Outcome` if authorization is missing or insufficient

## Pagination Cursor

**Purpose**: Preserves caller-controlled continuation through upstream caption-track pages.

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

- May be included in one `Captions List Request`
- May be returned in one `Caption Track Collection Result`

## Caption Track Collection Result

**Purpose**: Represents a successful near-raw caption-track list response.

**Fields**:

- `items`: Returned caption-track resources, possibly empty
- `requested_parts`: Parts requested by the caller
- `nextPageToken`: Optional continuation token
- `prevPageToken`: Optional previous-page token
- `pageInfo`: Optional page information
- `endpoint`: Upstream identity `captions.list`
- `quotaCost`: Official quota-unit cost `50`
- `lookup`: Safe summary of the request lookup context
- `delegation`: Safe indication of whether delegation context was supplied when useful

**Validation Rules**:

- Must preserve caption-track items from the endpoint-backed response
- Must allow an empty `items` collection as a successful result
- Must preserve pagination details when present
- Must preserve requested parts for review/debugging
- Must not download caption content
- Must not add higher-level language ranking, transcript lookup, enrichment, or heuristic interpretation

**Relationships**:

- Produced by one valid `Captions List Request`
- May include one `Pagination Cursor`
- References one `Captions List Metadata Disclosure`

## Captions List Error Outcome

**Purpose**: Represents a safe caller-facing failure for invalid requests, auth failures, quota failures, inaccessible captions, unavailable upstream service, or unexpected upstream failures.

**Fields**:

- `category`: Shared safe error category
- `message`: Caller-facing remediation-oriented message
- `details`: Safe request context such as tool name, invalid field, lookup mode, delegation presence, or upstream operation

**Validation Rules**:

- Must not include stack traces, API keys, OAuth tokens, secret values, signed URLs, raw media payloads, caption file contents, or sensitive owner credential details
- Must distinguish invalid input from missing authorization
- Must distinguish access-restricted captions from valid empty caption-track collections
- Must preserve shared Layer 2 error categories where applicable

**Relationships**:

- Produced by one invalid or failed `Captions List Request`
- Uses shared YT-201/YT-202 error and safety conventions

## Captions List Metadata Disclosure

**Purpose**: Captures the pre-invocation metadata clients and reviewers need to understand the tool.

**Fields**:

- `name`: `captions_list`
- `upstream`: `captions.list`
- `quotaCost`: `50`
- `authMode`: `oauth_required`
- `availabilityState`: Active with caption-access and delegation caveats
- `inputContract`: Required `part` and `videoId`, optional `id`, pagination, and delegation context
- `responseBoundary`: Near-raw list response with light MCP clarity fields
- `usageNotes`: Examples for authorized video caption lookup, paginated continuation, empty result handling, and delegated content-owner context

**Validation Rules**:

- Must be visible before invocation
- Must include quota and auth details in both structured metadata and caller-facing text
- Must describe delegated content-owner context
- Must stay aligned with YT-201/YT-202 shared metadata standards

**Relationships**:

- Belongs to the `Captions List Tool`
- References `Captions List Request`, `OAuth Requirement`, `Delegation Context`, and `Caption Track Collection Result`

## Verification Evidence

**Purpose**: Captures proof that the endpoint tool is ready for implementation review.

**Fields**:

- `red_phase_evidence`: Failing or characterization tests added before implementation
- `discovery_contract_checks`: Checks that `captions_list` appears with required metadata
- `request_validation_checks`: Checks for required `part`, required `videoId`, optional `id`, pagination, and delegation rules
- `auth_checks`: Checks for OAuth-required behavior and delegated-owner guidance
- `result_checks`: Checks for caption-track items, empty collections, requested parts, and pagination preservation
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
