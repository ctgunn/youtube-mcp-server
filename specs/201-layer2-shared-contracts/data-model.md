# Data Model: YT-201 Shared YouTube Scaffolding and Contracts

## YouTube Tool Contract

**Purpose**: Represents the public MCP-facing contract for one endpoint-backed YouTube Data API tool.

**Fields**:

- `tool_name`: Public MCP tool name derived from the resource-method pair
- `upstream_resource`: YouTube Data API resource name
- `upstream_method`: YouTube Data API method name
- `operation_key`: Stable internal identity used to connect the public tool to Layer 1 behavior
- `description`: Caller-facing tool description including endpoint identity, quota cost, auth mode, and caveats
- `input_contract`: JSON-compatible input schema and validation expectations
- `response_convention`: Expected successful result shape
- `auth_mode`: Declared access mode, such as API-key, OAuth-required, or mixed/conditional
- `quota_cost`: Official quota-unit cost for one upstream call
- `caveats`: Deprecation, availability, high-cost, media-handling, or documentation notes
- `error_categories`: Stable MCP-safe failure categories supported by the tool
- `resource_family`: Family that owns the endpoint-backed tool

**Validation Rules**:

- Must use the shared `resource_method` naming pattern without a redundant `youtube_` prefix
- Must identify upstream resource and method
- Must expose auth mode and official quota cost in caller-facing metadata
- Must include caveats for deprecated, availability-constrained, mixed-auth, media-handling, or high-quota tools when applicable
- Must stay near-raw and must not claim composed, enriched, ranked, or heuristic behavior
- Must exclude secrets, stack traces, OAuth tokens, API keys, and raw media payloads from examples, logs, errors, and safe result metadata
- Must include reStructuredText docstrings for any new or changed Python functions that create, validate, or register the contract

**Relationships**:

- Derived from one `Resource-Method Name`
- Owns one `Input Contract`, one `Response Convention`, and one or more `Error Category` entries
- Belongs to one `YouTube Resource Family`
- References one Layer 1 endpoint capability through upstream identity and operation key

## Resource-Method Name

**Purpose**: Represents the upstream resource and method pair used to derive the public YouTube tool name.

**Fields**:

- `resource`: Upstream YouTube resource name, such as `videos`, `comments`, or `channelBanners`
- `method`: Upstream YouTube method name, such as `list`, `insert`, `setModerationStatus`, or `getRating`
- `tool_name`: Derived public MCP tool name
- `case_policy`: Rule for preserving camelCase method suffixes after the resource-method separator

**Validation Rules**:

- Must derive names as `resource_method`
- Must not add `youtube_`
- Must preserve meaningful camelCase suffixes such as `setModerationStatus` and `getRating`
- Must be deterministic for repeated derivation and collision checks

**Relationships**:

- Derives one `YouTube Tool Contract`
- Maps to one upstream endpoint identity

## Input Contract

**Purpose**: Defines how MCP-facing arguments map to upstream YouTube Data API request parameters, request bodies, media inputs, and mutation options.

**Fields**:

- `required_fields`: Required caller inputs
- `optional_fields`: Optional caller inputs
- `selector_groups`: Mutually exclusive or conditional selectors
- `part_fields`: Upstream `part` selection rules when applicable
- `pagination_fields`: Page token and result-limit inputs when applicable
- `request_body_fields`: Body fields for create, update, moderation, abuse-report, or mutation operations
- `media_fields`: Media or upload-related inputs when applicable
- `delegation_fields`: Content-owner or delegated-channel fields when applicable
- `validation_messages`: Safe caller-facing validation failures

**Validation Rules**:

- Must stay close to upstream parameter names unless an MCP-safe wrapper name is required
- Must identify required fields and mutually exclusive selector rules
- Must preserve upstream pagination and `part` concepts when present
- Must distinguish request parameters from request body or media-related inputs
- Must reject unsupported combinations deterministically with safe error messages

**Relationships**:

- Belongs to one `YouTube Tool Contract`
- Produces request inputs for one Layer 1 endpoint capability

## Response Convention

**Purpose**: Defines the successful result shape for a YouTube tool while preserving near-raw upstream semantics.

**Fields**:

- `result_kind`: Read, list, mutation acknowledgment, upload result, download result, or lookup result
- `items_path`: Where returned resource items appear for list-style responses
- `paging_fields`: Returned paging tokens and paging metadata when applicable
- `requested_parts`: Requested resource parts echoed or preserved when useful
- `raw_payload_policy`: Rule for preserving upstream fields
- `wrapper_fields`: Light MCP clarity fields allowed around upstream data
- `content_policy`: Safe handling rule for media or downloaded content

**Validation Rules**:

- Must preserve upstream-visible items, paging tokens, requested parts, mutation acknowledgments, and resource fields when those concepts exist
- May include light wrapper fields only for MCP clarity, endpoint identity, safe metadata, or content delivery
- Must not transform results into Layer 3-style composed, ranked, enriched, or heuristic outputs
- Must not include secrets, raw credentials, stack traces, or unsafe raw media payloads

**Relationships**:

- Belongs to one `YouTube Tool Contract`
- Is validated by representative examples and contract tests

## Error Category

**Purpose**: Provides stable MCP-safe failure categories for YouTube endpoint-backed tools.

**Fields**:

- `category`: Stable caller-facing category
- `source`: Upstream, validation, auth, quota, availability, or unexpected failure source
- `safe_message`: Non-secret caller-facing message
- `details_policy`: Allowed safe diagnostic fields
- `retryability`: Whether the caller may retry after changing inputs, credentials, quota state, or waiting

**Validation Rules**:

- Must cover authentication failure, authorization failure, quota exhaustion, missing resource, invalid request, deprecated endpoint, unavailable endpoint, and unexpected upstream failure
- Must not expose stack traces, credentials, tokens, secret values, raw signed URLs, or raw upstream internals
- Must preserve enough category and safe context for callers to understand the failed request

**Relationships**:

- Belongs to one or more `YouTube Tool Contract` records
- Uses shared error conventions rather than endpoint-local categories

## Auth and Quota Declaration

**Purpose**: Makes access and cost expectations visible before invocation.

**Fields**:

- `auth_mode`: API-key, OAuth-required, or mixed/conditional
- `condition`: Selector, caller context, or operation detail that changes auth expectations
- `quota_cost`: Official quota-unit cost
- `quota_caveat`: High-cost or documentation caveat when applicable
- `visibility_target`: Tool description, metadata record, contract doc, or representative example

**Validation Rules**:

- Must be present for every representative YouTube tool contract
- Must distinguish mixed/conditional auth from single-mode auth
- Must call out high-cost tools such as expensive upload or search operations
- Must record caveats discovered from official or project documentation

**Relationships**:

- Belongs to one `YouTube Tool Contract`
- Is checked by shared contract tests and endpoint-slice review

## YouTube Resource Family

**Purpose**: Groups endpoint-backed public tools by YouTube capability family while keeping shared rules centralized.

**Fields**:

- `family_name`: Stable family label, such as `captions`, `channels`, `comments`, `playlist_items`, `search`, `subscriptions`, `videos`, or `watermarks`
- `tool_contracts`: Tool contracts owned by the family
- `tool_definitions`: Public tool definitions for the family
- `handlers`: Endpoint-backed public tool handlers for the family
- `tests`: Unit, contract, and integration tests for the family
- `examples`: Representative usage and caveat examples
- `caveat_notes`: Documentation inconsistency, deprecation, or availability notes

**Validation Rules**:

- Must keep endpoint-backed public tools cohesive by family
- Must depend on shared YouTube scaffolding for naming, metadata, auth, quota, response, and error rules
- Must not duplicate shared cross-cutting rules in each family
- Must not place every endpoint-backed tool in one monolithic file

**Relationships**:

- Owns one or more `YouTube Tool Contract` records
- Depends on Layer 1 resource-family capabilities for execution

## Scaffolding Contract

**Purpose**: Maintainer-facing agreement for where future YouTube endpoint slices place definitions, handlers, tests, contracts, and caveat notes.

**Fields**:

- `definition_location`: Expected location for public tool definitions
- `handler_location`: Expected location for endpoint-backed handlers
- `schema_location`: Expected location for input contracts or schema builders
- `test_locations`: Expected contract, unit, and integration test locations
- `documentation_location`: Expected location for caveats and examples
- `shared_helper_boundary`: Which behavior belongs in shared YouTube helpers versus endpoint-family modules

**Validation Rules**:

- Must let a future endpoint author identify placement obligations in under 3 minutes
- Must keep shared rules centralized and endpoint-specific behavior localized by family
- Must include reStructuredText docstring expectations for any new or changed Python function

**Relationships**:

- Guides each `YouTube Resource Family`
- Is validated by quickstart and contract checks

## Verification Evidence

**Purpose**: Captures the checks required to prove YT-201 and later endpoint slices honor the shared contracts.

**Fields**:

- `red_phase_evidence`: Failing or characterization tests added before implementation
- `focused_contract_checks`: shared YouTube contract tests for naming, metadata, auth, quota, response, and errors
- `unit_checks`: Focused helper and validation tests
- `integration_checks`: Registration or discovery checks against the MCP tool registry
- `full_suite_command`: Expected to be `python3 -m pytest`
- `lint_command`: Expected to be `python3 -m ruff check .`
- `docstring_review`: Confirmation that changed Python functions include reStructuredText docstrings

**Validation Rules**:

- Must include Red-Green-Refactor evidence
- Must include targeted checks before full-suite validation
- Must include full repository validation after final code changes
- Must include lint validation after final code changes
