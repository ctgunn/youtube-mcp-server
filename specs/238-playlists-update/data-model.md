# Data Model: YT-238 Layer 2 Tool `playlists_update`

## Playlists Update Tool

**Purpose**: Public Layer 2 MCP tool that exposes the low-level `playlists.update` operation.

**Fields**:
- `tool_name`: Stable public name, expected to be `playlists_update`
- `resource`: Upstream resource identity, expected to be `playlists`
- `method`: Upstream method identity, expected to be `update`
- `operation_key`: Caller-visible endpoint identity, expected to be `playlists.update`
- `quota_cost`: Official quota-unit cost, expected to be `50`
- `auth_mode`: OAuth-required access disclosure
- `availability_state`: Caller-visible endpoint availability state
- `input_contract`: Playlists Update Request contract
- `response_convention`: Playlists Update Result convention
- `examples`: Representative success and failure examples

**Validation Rules**:
- Must be discoverable as `playlists_update`
- Must identify `playlists.update` in discovery metadata, description, usage notes, and examples
- Must show quota cost `50` in metadata, description, usage notes, examples, and result context
- Must show OAuth-required mutation behavior before invocation
- Must not describe playlist listing, creation, deletion, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, rollback, conflict detection, or cross-endpoint behavior as part of this tool

## Playlists Update Request

**Purpose**: Caller-provided request for one supported playlist update operation.

**Fields**:
- `part`: Required writable part selection that determines which playlist properties are accepted and returned
- `body`: Required playlist update payload
- `body.id`: Required existing playlist identifier for the target update
- `body.snippet`: Required writable playlist snippet payload
- `body.snippet.title`: Required playlist title for the minimum supported update path
- `body.snippet.description`: Optional only if the implementation deliberately expands beyond the current Layer 1 minimum write boundary
- `body.status`: Optional only if the implementation deliberately expands beyond the current Layer 1 minimum write boundary
- `body.localizations`: Optional only if the implementation deliberately expands beyond the current Layer 1 minimum write boundary

**Validation Rules**:
- `part` is required and must be supported by the public contract
- Current supported `part` value is expected to center on `snippet`
- `body` must be an object
- `body.id` must be present and non-empty
- `body.snippet` must be an object
- `body.snippet.title` must be present, non-empty, and valid for playlist update
- Unsupported fields, unsupported modifiers, unsupported optional write fields, and out-of-scope workflow requests must be rejected before endpoint execution

## Part Selection

**Purpose**: Determines the writable playlist resource sections accepted and returned to the caller.

**Fields**:
- `requested_parts`: Caller-selected playlist sections
- `supported_parts`: Publicly supported writable playlist sections for this tool

**Validation Rules**:
- Must be explicitly supplied by the caller
- Must not contain empty, duplicate, unsupported, or conflicting values
- Returned playlist resources must preserve upstream fields for selected parts without fabricating missing optional fields

## Target Playlist Identity

**Purpose**: Identifies the existing playlist being updated.

**Fields**:
- `playlist_id`: Existing playlist identifier from `body.id`

**Validation Rules**:
- Must be present and non-empty
- Must be preserved in safe target context
- Missing, malformed, conflicting, or unsupported target identity fields must fail validation before endpoint execution

## Writable Playlist Details

**Purpose**: Caller-provided playlist metadata used to update the playlist.

**Fields**:
- `title`: Required playlist title for the supported update path
- `description`: Supported only if deliberately included by the implementation contract
- `privacy_or_status`: Supported only if deliberately included by the implementation contract
- `localization_details`: Supported only if deliberately included by the implementation contract

**Validation Rules**:
- Required title must be present and non-empty
- Malformed, conflicting, excessively long, or unsupported writable details must fail as invalid request input
- Unsupported optional write fields must be rejected unless the contract intentionally expands to support them

## Authorization Context

**Purpose**: Represents the caller access state used to execute playlist update without exposing credentials.

**Fields**:
- `mode`: OAuth-backed access mode selected for the request
- `credential_present`: Safe boolean or category indicating whether required access material was available
- `authorized_account_context`: Safe account/channel context when available, without credentials

**Validation Rules**:
- All supported `playlists_update` requests require eligible OAuth-backed access
- Missing, invalid, or insufficient access must be reported as access failure, not a validation failure or successful result
- Raw API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Updated Playlist Resource

**Purpose**: The playlist resource returned after successful update for the selected parts.

**Fields**:
- `id`: Playlist identifier when returned
- `snippet`: Playlist snippet fields when requested and returned
- `status`: Playlist status fields when requested and returned by an explicitly supported contract
- `localizations`: Playlist localization fields when requested and returned by an explicitly supported contract
- `other_returned_fields`: Any additional upstream fields returned for selected parts and supported by the shared result convention

**Validation Rules**:
- Returned fields depend on selected parts and upstream availability
- Missing optional fields must not be fabricated
- Playlist item, playlist image, video, channel, transcript, analytics, recommendation, ranking, summarization, rollback, conflict, or enrichment data must not be invented by this tool

## Playlists Update Result

**Purpose**: Successful result for a `playlists_update` call.

**Fields**:
- `endpoint`: Expected to be `playlists.update`
- `quotaCost`: Expected to be `50`
- `requestedParts`: Parsed part-selection context
- `updated`: Boolean marker for successful update
- `auth`: Safe OAuth access mode context
- `target`: Safe target context, including the playlist identifier without credentials
- `update`: Safe update context, including supported requested write fields without credentials
- `playlist`: Updated Playlist Resource

**Validation Rules**:
- Must distinguish successful playlist update from local validation failures, access failures, quota failures, forbidden update failures, missing-resource failures, and unexpected upstream failures
- Must preserve selected part, target, update, quota, access, and endpoint context
- Must not expose credentials, raw upstream diagnostics, stack traces, or unsafe request context

## Playlists Update Failure

**Purpose**: Caller-facing failure for invalid, ineligible, or unsuccessful playlist update requests.

**Fields**:
- `category`: Safe failure category such as invalid request, authentication failure, authorization failure, quota exhausted, forbidden update, resource not found, upstream unavailable, deprecated behavior, or unexpected upstream failure
- `message`: Caller-actionable summary
- `details`: Sanitized field, target, or update context

**Validation Rules**:
- Must distinguish local validation failures from access failures and upstream failures
- Must sanitize credential material, stack traces, raw upstream bodies, and unsafe diagnostics
- Must identify the invalid field or writable body path when doing so is safe

## State Transitions

1. Caller submits request.
2. Tool validates required `part`.
3. Tool validates required `body.id`.
4. Tool validates required `body.snippet.title` and rejects unsupported write fields or modifiers.
5. Tool validates OAuth-backed access availability.
6. Tool executes the existing Layer 1 `playlists.update` wrapper once for valid requests.
7. Successful upstream result maps to Playlists Update Result.
8. Local validation, access, quota, forbidden update, missing-resource, unavailable-service, deprecated, or unexpected upstream failures map to Playlists Update Failure.
