# Data Model: YT-241 Layer 2 Tool `subscriptions_list`

## Subscriptions List Tool

**Purpose**: Public Layer 2 MCP tool that exposes the low-level `subscriptions.list` operation.

**Fields**:
- `tool_name`: Stable public name, expected to be `subscriptions_list`
- `resource`: Upstream resource identity, expected to be `subscriptions`
- `method`: Upstream method identity, expected to be `list`
- `operation_key`: Caller-visible endpoint identity, expected to be `subscriptions.list`
- `quota_cost`: Official quota-unit cost, expected to be `1`
- `auth_mode`: Conditional access disclosure for public-compatible selectors and OAuth-backed user-context selectors
- `availability_state`: Caller-visible endpoint availability state and private subscriber caveats
- `input_contract`: Subscriptions List Request contract
- `response_convention`: Subscriptions List Result convention
- `examples`: Representative success and failure examples

**Validation Rules**:
- Must be discoverable as `subscriptions_list`
- Must identify `subscriptions.list` in discovery metadata, description, usage notes, and examples
- Must show quota cost `1` in metadata, description, usage notes, examples, and result context
- Must show conditional auth expectations before invocation
- Must not describe subscription creation, subscription deletion, partner delegation, channel enrichment, subscriber analytics, ranking, summarization, recommendation, or cross-endpoint aggregation as part of this tool

## Subscriptions List Request

**Purpose**: Caller-provided request for one supported subscription listing operation.

**Fields**:
- `part`: Required subscription response part selection supported by the endpoint
- `channelId`: Optional public-compatible selector for a channel's subscriptions
- `id`: Optional public-compatible selector for one or more subscription identifiers
- `mine`: Optional OAuth-backed selector for the authenticated user's subscriptions
- `myRecentSubscribers`: Optional OAuth-backed selector for recent subscribers of the authenticated user
- `mySubscribers`: Optional OAuth-backed selector for subscribers of the authenticated user
- `pageToken`: Optional continuation token for compatible collection traversal
- `maxResults`: Optional maximum result count within official limits
- `order`: Optional ordering mode for compatible collection traversal

**Validation Rules**:
- `part` is required and must include supported subscription resource parts
- Exactly one selector must be active: `channelId`, `id`, `mine`, `myRecentSubscribers`, or `mySubscribers`
- Boolean selectors only count as active when set to `true`
- Unsupported fields, partner-only delegation fields, channel enrichment instructions, subscriber analytics inputs, ranking instructions, summarization instructions, mutation requests, and higher-level workflow requests must be rejected before endpoint execution
- `mine`, `myRecentSubscribers`, and `mySubscribers` require eligible OAuth-backed access
- Pagination and ordering inputs must be valid and compatible with the selected list mode
- API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Subscription Part Selection

**Purpose**: Represents the requested subscription resource sections.

**Fields**:
- `contentDetails`: Optional subscription content details
- `id`: Optional subscription identifier section
- `snippet`: Optional subscription snippet section
- `subscriberSnippet`: Optional subscriber snippet section where available

**Validation Rules**:
- At least one supported part must be requested
- Unknown part names must be rejected before execution
- Returned optional fields depend on upstream availability and must not be fabricated

## Subscription Selector Mode

**Purpose**: Represents the mutually exclusive lookup path for one request.

**Fields**:
- `selector`: One of `channelId`, `id`, `mine`, `myRecentSubscribers`, or `mySubscribers`
- `value`: Selector value for string selectors or `true` for boolean selectors
- `auth_path`: Safe category such as `public` or `user_context`
- `collection_style`: Boolean indicating whether pagination and ordering can apply

**Validation Rules**:
- Must include exactly one supported selector
- Public-compatible selectors use public lookup access
- User-context selectors require OAuth-backed access
- Direct identifier lookup must not imply collection traversal

## Pagination and Ordering Context

**Purpose**: Represents caller-provided and returned page information for subscription list traversal.

**Fields**:
- `request_page_token`: Caller-provided `pageToken`, when present
- `request_max_results`: Caller-provided `maxResults`, when present
- `request_order`: Caller-provided `order`, when present
- `next_page_token`: Returned continuation token, when present
- `previous_page_token`: Returned previous-page token, when present
- `page_info`: Returned result-count context, when present

**Validation Rules**:
- `maxResults` must be within the official `0` to `50` range
- `pageToken` must be non-empty when provided
- `order` must be a supported ordering mode
- Returned pagination fields must not imply compatibility with different selector criteria

## Access Context

**Purpose**: Represents the caller access state used to execute public-compatible or user-context subscription listing without exposing credentials.

**Fields**:
- `mode`: Public lookup access or OAuth-backed user-context access
- `auth_path`: Safe category such as `public` or `user_context`
- `credential_present`: Safe boolean or category indicating whether required access material was available

**Validation Rules**:
- `channelId` and `id` use public-compatible access
- `mine`, `myRecentSubscribers`, and `mySubscribers` require eligible OAuth-backed access
- Missing, invalid, or insufficient access must be reported as access failure, not a validation failure or successful result
- Raw API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Subscription Result Record

**Purpose**: A returned subscription item visible for the selected criteria and parts.

**Fields**:
- `kind`: Returned item kind, when present
- `etag`: Returned item tag, when present
- `id`: Returned subscription identifier, when present
- `snippet`: Returned snippet fields, when requested and present
- `contentDetails`: Returned content details, when requested and present
- `subscriberSnippet`: Returned subscriber snippet fields, when requested and present

**Validation Rules**:
- Must preserve returned endpoint fields without fabricating hydrated channel or subscriber details
- Missing optional fields must remain absent rather than being invented from request context

## Subscriptions List Result

**Purpose**: Successful result for a `subscriptions_list` call.

**Fields**:
- `endpoint`: Expected to be `subscriptions.list`
- `quotaCost`: Expected to be `1`
- `items`: Subscription result records returned by the endpoint
- `empty`: Boolean marker for successful empty collections
- `selectorContext`: Safe submitted selector and part context
- `pagination`: Returned pagination context, when applicable
- `auth`: Safe access mode context

**Validation Rules**:
- Must distinguish successful populated results from successful empty results
- Must preserve returned fields, selector context, quota context, access context, and pagination context
- Must not expose credentials, raw upstream diagnostics, stack traces, unsafe request context, or fabricated channel/subscriber enrichment

## Subscriptions List Failure

**Purpose**: Caller-facing failure for invalid, ineligible, or unsuccessful subscription list requests.

**Fields**:
- `category`: Safe failure category such as invalid request, authentication failure, authorization failure, quota exhausted, not found, endpoint unavailable, deprecated behavior, or unexpected upstream failure
- `message`: Caller-actionable summary
- `details`: Sanitized field, selector, or access context

**Validation Rules**:
- Must distinguish local validation failures from access failures and upstream failures
- Must sanitize credential material, stack traces, raw upstream bodies, and unsafe diagnostics
- Must identify the invalid field or selector when doing so is safe

## State Transitions

1. Caller submits request.
2. Tool validates required `part`.
3. Tool rejects unsupported fields, partner-only delegation fields, mutation requests, enrichment instructions, analytics inputs, ranking instructions, summarization instructions, or higher-level workflow requests.
4. Tool validates exactly one supported selector.
5. Tool validates pagination and ordering compatibility with the selected selector.
6. Tool validates public-compatible or OAuth-backed access availability based on the selected selector.
7. Tool executes the existing Layer 1 `subscriptions.list` wrapper once for valid requests.
8. Successful upstream result maps to Subscriptions List Result, including empty successful results.
9. Local validation, access, quota, account-state, not-found, unavailable-service, deprecated, or unexpected upstream failures map to Subscriptions List Failure.
