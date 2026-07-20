# Data Model: YT-242 Layer 2 Tool `subscriptions_insert`

## Subscriptions Insert Tool

**Purpose**: Public Layer 2 MCP tool that exposes the low-level `subscriptions.insert` operation.

**Fields**:
- `tool_name`: Stable public name, expected to be `subscriptions_insert`
- `resource`: Upstream resource identity, expected to be `subscriptions`
- `method`: Upstream method identity, expected to be `insert`
- `operation_key`: Caller-visible endpoint identity, expected to be `subscriptions.insert`
- `quota_cost`: Official quota-unit cost, expected to be `50`
- `auth_mode`: OAuth-required access disclosure
- `availability_state`: Caller-visible endpoint availability state
- `input_contract`: Subscriptions Insert Request contract
- `response_convention`: Subscriptions Insert Result convention
- `examples`: Representative success and failure examples

**Validation Rules**:
- Must be discoverable as `subscriptions_insert`
- Must identify `subscriptions.insert` in discovery metadata, description, usage notes, and examples
- Must show quota cost `50` in metadata, description, usage notes, examples, and result context
- Must show OAuth-required mutation behavior before invocation
- Must not describe subscription listing, deletion, channel search, recommendation, notification management, analytics, ranking, summarization, enrichment, idempotency, duplicate prevention, or cross-endpoint behavior as part of this tool

## Subscriptions Insert Request

**Purpose**: Caller-provided request for one supported subscription creation operation.

**Fields**:
- `part`: Required writable part selection; the supported value for this slice is `snippet`
- `body`: Required subscription creation payload
- `body.snippet`: Required writable subscription snippet payload
- `body.snippet.resourceId`: Required target resource payload
- `body.snippet.resourceId.channelId`: Required target channel identifier to subscribe to
- `body.snippet.resourceId.kind`: Optional target resource kind, allowed only as `youtube#channel` when provided

**Validation Rules**:
- `part` is required and must be exactly `snippet`
- `body` must be an object
- `body.snippet` must be an object
- `body.snippet.resourceId` must be an object
- `body.snippet.resourceId.channelId` must be present and non-empty
- `body.snippet.resourceId.kind` must be absent, empty, or `youtube#channel`
- Unsupported top-level body fields, snippet fields, resource-id fields, modifiers, and out-of-scope workflow requests must be rejected before endpoint execution

## Part Selection

**Purpose**: Determines the writable subscription resource section accepted and returned to the caller.

**Fields**:
- `requested_parts`: Caller-selected subscription sections
- `supported_parts`: Publicly supported writable subscription sections for this tool

**Validation Rules**:
- Must be explicitly supplied by the caller
- Must be `snippet` for the supported create path
- Returned subscription resources must preserve upstream fields for selected parts without fabricating missing optional fields

## Target Channel Relationship

**Purpose**: Represents the subscription relationship the authorized account is attempting to create.

**Fields**:
- `target_channel_id`: The channel identifier from `body.snippet.resourceId.channelId`
- `target_resource_kind`: The resource kind, defaulting to or preserving `youtube#channel`
- `relationship_state`: Safe outcome category such as created, duplicate, ineligible, rejected, or unknown

**Validation Rules**:
- Target channel id must be non-empty
- Target resource kind must represent a YouTube channel when supplied
- Duplicate, self-targeted, blocked, missing, or otherwise ineligible relationships must be reported distinctly when determinable from validation or normalized upstream feedback

## Access Context

**Purpose**: Represents the caller access state used to execute subscription creation without exposing credentials.

**Fields**:
- `mode`: OAuth-backed access mode selected for the request
- `credential_present`: Safe boolean or category indicating whether required access material was available
- `authorized_account_context`: Safe account/channel context when available, without credentials

**Validation Rules**:
- All supported `subscriptions_insert` requests require eligible OAuth-backed access
- Missing, invalid, or insufficient access must be reported as access failure, not a validation failure or successful result
- Raw API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Created Subscription Resource

**Purpose**: The subscription resource returned after successful creation for the selected part.

**Fields**:
- `id`: Subscription identifier when returned
- `snippet`: Subscription snippet fields when requested and returned
- `targetChannelId`: Stable target channel id when returned or derived safely from request/response context
- `targetResourceKind`: Stable target resource kind when returned or derived safely from request/response context
- `other_returned_fields`: Any additional upstream fields returned for selected parts and supported by the shared result convention

**Validation Rules**:
- Returned fields depend on selected parts and upstream availability
- Missing optional fields must not be fabricated
- Channel search, notification settings, subscriber profile, analytics, recommendation, ranking, summarization, and enrichment data must not be invented by this tool

## Subscriptions Insert Result

**Purpose**: Successful result for a `subscriptions_insert` call.

**Fields**:
- `endpoint`: Expected to be `subscriptions.insert`
- `quotaCost`: Expected to be `50`
- `requestedParts`: Parsed part-selection context
- `created`: Boolean marker for successful creation
- `auth`: Safe OAuth access mode context
- `creation`: Safe creation context, including target channel context without credentials
- `subscription`: Created Subscription Resource

**Validation Rules**:
- Must distinguish successful subscription creation from local validation failures, access failures, duplicate/ineligible target failures, quota failures, forbidden create failures, and unexpected upstream failures
- Must preserve selected part, target channel, quota, access, and endpoint context
- Must not expose credentials, raw upstream diagnostics, stack traces, or unsafe request context

## Subscriptions Insert Failure

**Purpose**: Caller-facing failure for invalid, ineligible, or unsuccessful subscription creation requests.

**Fields**:
- `category`: Safe failure category such as invalid request, authentication failure, authorization failure, quota exhausted, duplicate target, ineligible target, resource not found, upstream unavailable, deprecated behavior, or unexpected upstream failure
- `message`: Caller-actionable summary
- `details`: Sanitized field or creation context

**Validation Rules**:
- Must distinguish local validation failures from access failures and upstream failures
- Must sanitize credential material, stack traces, raw upstream bodies, and unsafe diagnostics
- Must identify the invalid field or writable body path when doing so is safe

## State Transitions

1. Caller submits request.
2. Tool validates required `part=snippet`.
3. Tool validates required `body.snippet.resourceId.channelId` and rejects unsupported write fields or modifiers.
4. Tool validates OAuth-backed access availability.
5. Tool executes the existing Layer 1 `subscriptions.insert` wrapper once for valid requests.
6. Successful upstream result maps to Subscriptions Insert Result.
7. Local validation, access, duplicate target, ineligible target, quota, forbidden create, unavailable-service, deprecated, or unexpected upstream failures map to Subscriptions Insert Failure.
