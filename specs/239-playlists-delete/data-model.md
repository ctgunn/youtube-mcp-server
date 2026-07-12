# Data Model: YT-239 Layer 2 Tool `playlists_delete`

## Playlists Delete Tool

**Purpose**: Public Layer 2 MCP tool that exposes the low-level `playlists.delete` operation.

**Fields**:
- `tool_name`: Stable public name, expected to be `playlists_delete`
- `resource`: Upstream resource identity, expected to be `playlists`
- `method`: Upstream method identity, expected to be `delete`
- `operation_key`: Caller-visible endpoint identity, expected to be `playlists.delete`
- `quota_cost`: Official quota-unit cost, expected to be `50`
- `auth_mode`: OAuth-required access disclosure
- `availability_state`: Caller-visible endpoint availability state
- `input_contract`: Playlists Delete Request contract
- `response_convention`: Playlists Delete Result convention
- `examples`: Representative success and failure examples

**Validation Rules**:
- Must be discoverable as `playlists_delete`
- Must identify `playlists.delete` in discovery metadata, description, usage notes, and examples
- Must show quota cost `50` in metadata, description, usage notes, examples, and result context
- Must show OAuth-required destructive behavior before invocation
- Must not describe playlist listing, creation, update, playlist item management, playlist image handling, video curation, transcript retrieval, analytics, ranking, summarization, recommendation, restore, rollback, idempotency guarantees, or cross-endpoint behavior as part of this tool

## Playlists Delete Request

**Purpose**: Caller-provided request for one supported playlist deletion operation.

**Fields**:
- `id`: Required identifier for the playlist being deleted

**Validation Rules**:
- `id` is required and must be present, non-empty, and valid as a target playlist identity
- The request targets exactly one playlist per invocation
- Unsupported fields, unsupported modifiers, bodies, part selections, list selectors, paging fields, playlist item inputs, playlist image inputs, video inputs, transcript inputs, analytics inputs, and out-of-scope workflow requests must be rejected before endpoint execution
- API-key-only access, missing OAuth access, or insufficient OAuth access must not be treated as a successful deletion

## Target Playlist Identity

**Purpose**: Identifies the existing playlist being deleted.

**Fields**:
- `playlist_id`: Playlist identifier from `id`

**Validation Rules**:
- Must be present and non-empty
- Must be preserved in safe target context
- Missing, malformed, duplicated, conflicting, or unsupported target identity fields must fail validation before endpoint execution
- Must not be broadened into channel, owner, or playlist collection selectors

## Authorization Context

**Purpose**: Represents the caller access state used to execute playlist deletion without exposing credentials.

**Fields**:
- `mode`: OAuth-backed access mode selected for the request
- `credential_present`: Safe boolean or category indicating whether required access material was available
- `authorized_account_context`: Safe account/channel context when available, without credentials

**Validation Rules**:
- All supported `playlists_delete` requests require eligible OAuth-backed access
- Missing, invalid, or insufficient access must be reported as access failure, not a validation failure or successful result
- Raw API keys, OAuth tokens, authorization headers, and secret-bearing diagnostics must never appear in caller-facing results or errors

## Deletion Acknowledgment

**Purpose**: Successful no-body-compatible outcome for a playlist deletion request.

**Fields**:
- `deleted`: Boolean marker for successful deletion
- `acknowledged`: Boolean marker that the endpoint accepted the delete operation
- `endpoint`: Expected to be `playlists.delete`
- `quotaCost`: Expected to be `50`
- `target`: Safe target playlist identity context
- `auth`: Safe OAuth access mode context

**Validation Rules**:
- Must acknowledge successful deletion without requiring a deleted playlist resource body
- Must not fabricate deleted playlist fields from request context
- Must preserve endpoint, quota, target, and auth context

## Playlists Delete Result

**Purpose**: Successful result for a `playlists_delete` call.

**Fields**:
- `endpoint`: Expected to be `playlists.delete`
- `quotaCost`: Expected to be `50`
- `deleted`: Boolean marker for successful deletion
- `acknowledged`: Boolean marker for accepted deletion
- `auth`: Safe OAuth access mode context
- `target`: Safe target context, including the playlist identifier without credentials

**Validation Rules**:
- Must distinguish successful playlist deletion from local validation failures, access failures, quota failures, missing-resource or already-deleted outcomes, unavailable-service responses, deprecated behavior, and unexpected upstream failures
- Must preserve target, quota, access, and endpoint context
- Must not expose credentials, raw upstream diagnostics, stack traces, unsafe request context, or fabricated deleted playlist details

## Playlists Delete Failure

**Purpose**: Caller-facing failure for invalid, ineligible, or unsuccessful playlist deletion requests.

**Fields**:
- `category`: Safe failure category such as invalid request, authentication failure, authorization failure, quota exhausted, resource not found, upstream unavailable, deprecated behavior, or unexpected upstream failure
- `message`: Caller-actionable summary
- `details`: Sanitized field or target context

**Validation Rules**:
- Must distinguish local validation failures from access failures and upstream failures
- Must sanitize credential material, stack traces, raw upstream bodies, and unsafe diagnostics
- Must identify the invalid field or target path when doing so is safe

## State Transitions

1. Caller submits request.
2. Tool validates required `id`.
3. Tool rejects unsupported fields, bodies, part selections, selectors, modifiers, or out-of-scope workflow requests.
4. Tool validates OAuth-backed access availability.
5. Tool executes the existing Layer 1 `playlists.delete` wrapper once for valid requests.
6. Successful upstream result maps to Playlists Delete Result.
7. Local validation, access, quota, missing-resource, unavailable-service, deprecated, or unexpected upstream failures map to Playlists Delete Failure.
