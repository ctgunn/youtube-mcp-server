# Data Model: YT-202 Layer 2 Tool Metadata, Naming, and Quota Standards

## Layer 2 Metadata Standard

**Purpose**: Represents the required public metadata every endpoint-backed Layer 2 MCP tool must expose before invocation.

**Fields**:

- `tool_name`: Public MCP tool name derived from the upstream resource-method pair
- `upstream_resource`: YouTube Data API resource name
- `upstream_method`: YouTube Data API method name
- `operation_key`: Stable internal identity used to connect the public tool to Layer 1 behavior
- `quota_cost`: Official quota-unit cost for one upstream call
- `auth_mode`: Declared access mode: API-key, OAuth-required, or mixed/conditional
- `availability_state`: Active, deprecated, unavailable, region-constrained, owner-only, media-constrained, or documentation-caveat state
- `description`: Caller-facing discovery description
- `usage_notes`: Caller-facing example or usage notes that include quota and caveats
- `caveats`: High-cost, auth-condition, media-handling, deprecation, availability, or documentation notes
- `response_boundary`: Classification of the successful result shape as near-raw or lightly reshaped for MCP clarity

**Validation Rules**:

- Must include all required fields for every Layer 2 endpoint-backed tool definition
- Must expose official quota cost in structured metadata, description, and usage notes
- Must expose auth mode and availability state before invocation
- Must identify the upstream resource and method unambiguously
- Must not include credentials, tokens, signed URLs, stack traces, secret values, or unsafe raw media payloads
- Must remain additive to YT-201 shared scaffolding and avoid redefining broad input, layout, or error conventions

**Relationships**:

- Derived from one `Resource-Method Name`
- Owns one `Quota Disclosure`, one `Auth Declaration`, one `Availability Declaration`, and one `Response Boundary`
- Is validated through one or more `Representative Metadata Example` records
- References one Layer 1 endpoint capability through `operation_key`

## Resource-Method Name

**Purpose**: Represents the official upstream endpoint identity used to derive the public Layer 2 tool name.

**Fields**:

- `resource`: Upstream resource name, such as `videos`, `playlists`, `comments`, or `channelBanners`
- `method`: Upstream method name, such as `list`, `insert`, `setModerationStatus`, or `getRating`
- `tool_name`: Derived public name
- `case_policy`: Rule for preserving meaningful upstream camelCase method suffixes

**Validation Rules**:

- Must derive names as `resource_method`
- Must not include a redundant `youtube_` prefix
- Must preserve official camelCase suffixes when lowercasing would obscure the method identity
- Must be deterministic across docs, tests, examples, and registration metadata

**Relationships**:

- Derives one `Layer 2 Metadata Standard`
- Maps to one upstream endpoint identity

## Quota Disclosure

**Purpose**: Makes endpoint cost visible to callers and future composing tools before invocation.

**Fields**:

- `quota_cost`: Official YouTube quota-unit cost
- `visibility_targets`: Metadata, description, usage notes, and representative examples where cost appears
- `high_quota_warning`: Explicit warning for especially expensive endpoints
- `source_note`: Official documentation reference or caveat note when the quota source is inconsistent

**Validation Rules**:

- Must use a positive integer quota-unit cost
- Must be visible in structured metadata
- Must be visible in the tool description
- Must be visible in usage notes or example text
- Must call out high-cost endpoints before invocation

**Relationships**:

- Belongs to one `Layer 2 Metadata Standard`
- Is used by future Layer 3 authors to estimate composition cost

## Auth Declaration

**Purpose**: Describes credential requirements in a stable caller-facing form.

**Fields**:

- `auth_mode`: API-key, OAuth-required, or mixed/conditional
- `condition_note`: Selector, caller context, or operation mode that changes credential requirements
- `caller_message`: Safe description shown to callers before invocation

**Validation Rules**:

- Must use one of the shared auth-mode values
- Must distinguish mixed/conditional auth from single-mode auth
- Must not expose credentials, token values, or secret configuration details
- Must align with Layer 1 endpoint metadata where applicable

**Relationships**:

- Belongs to one `Layer 2 Metadata Standard`
- May reference one or more caveats for private filters, owner-only operations, or mutation behavior

## Availability Declaration

**Purpose**: Describes whether the endpoint is active or constrained before callers attempt invocation.

**Fields**:

- `availability_state`: Active, deprecated, unavailable, region-constrained, owner-only, media-constrained, or documentation-caveat state
- `availability_note`: Caller-facing explanation of the caveat or constraint
- `review_source`: Official or project documentation source used to justify the state

**Validation Rules**:

- Must be present for every representative Layer 2 metadata example
- Must use active for ordinary available endpoints
- Must use constrained states when endpoint behavior is deprecated, unavailable, owner-only, region-specific, media-specific, or otherwise caveated
- Must not hide deprecation or availability constraints in implementation-only comments

**Relationships**:

- Belongs to one `Layer 2 Metadata Standard`
- Contributes to usage notes and caveat text

## Usage Note

**Purpose**: Provides short caller-facing example or review text that reinforces cost, auth, caveats, and response expectations.

**Fields**:

- `text`: Human-readable usage note
- `quota_cost`: Official quota-unit cost repeated for visibility
- `auth_summary`: Short auth-mode summary
- `caveat_summary`: Optional high-cost, media, owner-only, deprecation, or availability warning
- `response_summary`: Short response-boundary summary

**Validation Rules**:

- Must mention quota cost or a high-quota warning
- Must not imply a concrete endpoint implementation when used as a representative example only
- Must not include secrets, tokens, stack traces, signed URLs, or raw media payloads

**Relationships**:

- Belongs to one `Layer 2 Metadata Standard`
- Appears in representative examples and review evidence

## Response Boundary

**Purpose**: Classifies how a successful Layer 2 result relates to the upstream endpoint response.

**Fields**:

- `boundary_kind`: Near-raw, lightly reshaped for MCP clarity, or out of Layer 2 scope
- `allowed_wrapper_fields`: Endpoint identity, safe metadata, requested parts, quota cost, pagination, mutation acknowledgment, or safe content wrapper fields
- `preserved_upstream_fields`: Items, paging tokens, requested parts, resource fields, mutation acknowledgments, upload result identity, or download metadata
- `disallowed_behavior`: Composition, enrichment, ranking, heuristics, or cross-endpoint aggregation

**Validation Rules**:

- Must preserve upstream-visible concepts when present
- May allow light wrapper fields only for MCP clarity, endpoint identity, safe metadata, or safe content delivery
- Must reject Layer 3-style composition, ranking, enrichment, or heuristic behavior
- Must not expose unsafe raw media payloads or sensitive details

**Relationships**:

- Belongs to one `Layer 2 Metadata Standard`
- Reuses YT-201 response convention concepts

## Representative Metadata Example

**Purpose**: Demonstrates that the standard covers the endpoint shapes future slices will implement.

**Fields**:

- `tool_name`: Derived public tool name
- `resource_method`: Official upstream resource-method pair
- `shape_category`: Simple read, paginated read, camelCase method, OAuth-only, mixed-auth, mutation, media, high-quota, constrained, lookup, download, or acknowledgment
- `metadata`: Complete `Layer 2 Metadata Standard` record
- `expected_validation`: Contract checks the example must satisfy

**Validation Rules**:

- Must include at least 10 representative examples
- Must cover simple reads, paginated reads, camelCase names, OAuth-only operations, mixed-auth operations, mutations, media operations, high-quota operations, availability constraints, and non-list response shapes
- Must remain non-executing unless the corresponding endpoint slice implements behavior later

**Relationships**:

- Validates one or more `Layer 2 Metadata Standard` rules
- Feeds contract, unit, and integration-style checks

## Verification Evidence

**Purpose**: Captures the checks needed to prove the metadata standards are ready for later endpoint slices.

**Fields**:

- `red_phase_evidence`: Failing or characterization tests added before metadata changes
- `metadata_contract_checks`: Contract tests for required fields and visibility targets
- `naming_checks`: Unit or contract tests for deterministic public names
- `quota_visibility_checks`: Tests proving quota appears in metadata, descriptions, and usage notes
- `response_boundary_checks`: Tests proving examples remain near-raw or lightly reshaped
- `integration_checks`: Registration or discovery checks where applicable
- `full_suite_command`: Expected to be `python3 -m pytest`
- `lint_command`: Expected to be `python3 -m ruff check .`
- `docstring_review`: Confirmation that changed Python functions include reStructuredText docstrings

**Validation Rules**:

- Must include Red-Green-Refactor evidence
- Must include focused checks before full-suite validation
- Must include full repository validation after final code changes
- Must include lint validation after final code changes
- Must identify any official documentation caveats discovered during implementation
