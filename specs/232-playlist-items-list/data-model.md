# Data Model: Layer 2 Tool `playlistItems_list`

## Overview

`playlistItems_list` is a public Layer 2 MCP tool that exposes one endpoint-backed playlist-item listing operation. It does not introduce persistent storage. The data model below describes caller-visible request, result, metadata, validation, and error concepts that must be represented by the public contract and implementation tests.

## Entities

### Playlist Items List Tool

Represents the public MCP tool named `playlistItems_list`.

**Fields**

- `name`: Stable public tool name, always `playlistItems_list`.
- `description`: Caller-facing summary that identifies the upstream operation, quota cost, access expectation, and list-only scope.
- `inputSchema`: Public object schema for supported arguments.
- `metadata`: Public discovery metadata containing upstream identity, quota, access mode, availability, usage notes, caveats, and examples.
- `handler`: Callable behavior that validates arguments, invokes the Layer 1 wrapper, and maps the result into a public Layer 2 result or safe error.

**Relationships**

- Uses one `Playlist Items List Request`.
- Produces one `Playlist Items List Result` on success.
- Produces one safe error outcome when validation, access, quota, missing-resource, unavailable-service, deprecated-behavior, or unexpected upstream failure occurs.
- Depends on the YT-132 Layer 1 `playlistItems.list` wrapper.

**Validation Rules**

- Must expose mapped operation identity `playlistItems.list`.
- Must expose official quota cost `1`.
- Must expose the documented API-key access expectation for the supported selector set.
- Must remain scoped to playlist item listing only.

### Playlist Items List Request

Represents caller-supplied arguments for one list operation.

**Fields**

- `part`: Required string selecting playlist item resource sections to return.
- `playlistId`: Optional string selector for playlist-scoped retrieval.
- `id`: Optional string or supported identifier value for direct playlist-item lookup.
- `pageToken`: Optional string for supported playlist-scoped pagination.
- `maxResults`: Optional integer page-size request within supported limits.

**Relationships**

- Contains one `Part Selection`.
- Contains exactly one `Playlist Item Lookup Selector`.
- May contain one `Pagination Context` when the selected lookup mode supports pagination.

**Validation Rules**

- `part` is required and must be non-empty.
- Part values must belong to the supported Layer 1 contract.
- Exactly one supported selector is required.
- `playlistId` and `id` are mutually exclusive in a single request.
- Selector values must be non-empty and well-formed enough for the shared contract.
- Paging inputs must be accepted only with selector modes that support paging.
- Unsupported properties must be rejected before execution.

### Part Selection

Represents the caller-selected playlist item fields returned by the endpoint-backed list operation.

**Fields**

- `rawValue`: Caller-provided part selection string.
- `selectedParts`: Normalized list of selected part names.

**Relationships**

- Belongs to one `Playlist Items List Request`.
- Determines which fields may appear on each `Playlist Item Resource`.

**Validation Rules**

- Must be present.
- Must not be empty, malformed, duplicated in unsupported ways, or outside the supported part set.
- Must be preserved in successful result context.

### Playlist Item Lookup Selector

Represents the lookup mode for the request.

**Fields**

- `mode`: Either `playlistId` or `id`.
- `value`: Caller-supplied selector value.

**Relationships**

- Belongs to one `Playlist Items List Request`.
- Controls whether pagination inputs are accepted.
- Is preserved in successful result context.

**Validation Rules**

- Exactly one selector mode must be present.
- `playlistId` selects playlist-scoped retrieval and supports playlist traversal.
- `id` selects direct playlist-item lookup.
- Missing, conflicting, empty, malformed, duplicate, excessive, or unsupported selector values must fail with caller-facing validation feedback.

### Pagination Context

Represents caller-provided and returned page information.

**Fields**

- `pageToken`: Optional caller-provided page token.
- `maxResults`: Optional caller-provided page size.
- `nextPageToken`: Optional returned token for subsequent page retrieval.
- `pageInfo`: Optional returned page summary, including total or page-size information when available.

**Relationships**

- Belongs to a playlist-scoped `Playlist Items List Request` when supplied.
- Appears in `Playlist Items List Result` when applicable or returned upstream.

**Validation Rules**

- `pageToken` must be non-empty when present.
- `maxResults` must be within the supported official limit.
- Paging must be rejected for selector modes where the contract does not support it.
- Returned paging context must be preserved without inventing unavailable values.

### Access Context

Represents the caller access expectations for the supported selector set.

**Fields**

- `mode`: Public access mode, documented as API-key access for the supported selector set.
- `eligible`: Whether the request has the access context required by the selected lookup mode.
- `safeFailureCategory`: Optional safe category when access is missing, invalid, or insufficient.

**Relationships**

- Applies to one request.
- Is included in success context when safe and useful.
- Can produce an access failure before or during endpoint execution.

**Validation Rules**

- Public metadata and examples must disclose the access expectation before invocation.
- Missing, invalid, or insufficient access must not be reported as a successful list result.
- Credential material must never appear in public results, examples, logs, or safe errors.

### Playlist Item Resource

Represents one returned playlist entry from the endpoint-backed list operation.

**Fields**

- `id`: Playlist item identifier when returned.
- `snippet`: Playlist item snippet fields when selected and returned.
- `contentDetails`: Playlist item content details when selected and returned.
- `status`: Playlist item status fields when selected and returned.
- `rawFields`: Any returned upstream fields allowed by the selected parts and shared result contract.

**Relationships**

- Appears zero or more times in a `Playlist Items List Result`.
- Field presence depends on `Part Selection`.

**Validation Rules**

- Returned fields must be preserved when supplied by the Layer 1 result.
- Missing optional fields must not be fabricated.
- Video, playlist, channel, transcript, ranking, analytics, or recommendation enrichment must not be added by this tool.

### Playlist Items List Result

Represents the successful public result for one `playlistItems_list` call.

**Fields**

- `endpoint`: Mapped endpoint identity, `playlistItems.list`.
- `sourceOperation`: Source operation identity when included by shared conventions.
- `quotaCost`: Official quota-unit cost, `1`.
- `items`: Zero or more returned playlist item resources.
- `partContext`: Selected parts used for the request.
- `selectorContext`: Lookup mode and safe selector context.
- `paginationContext`: Returned and requested page information when applicable.
- `accessContext`: Safe access-mode context.
- `upstreamContext`: Safe returned upstream context when available.

**Relationships**

- Produced by one successful request.
- Contains zero or more `Playlist Item Resource` records.
- May include one `Pagination Context`.

**Validation Rules**

- Must distinguish populated success from empty success.
- Must preserve selected part, selector, pagination, quota, and endpoint context.
- Must not expose secrets, raw unsafe diagnostics, stack traces, or fabricated enrichment fields.

### Safe Error Outcome

Represents caller-facing failure information.

**Fields**

- `category`: Safe error category such as validation, access, quota, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure.
- `message`: Caller-facing explanation.
- `details`: Safe structured details identifying invalid fields or failure context.
- `endpoint`: `playlistItems.list` when applicable.
- `quotaCost`: `1` when useful for caller context.

**Relationships**

- Produced when a `Playlist Items List Request` cannot complete successfully.
- May originate from local validation, access checks, or normalized upstream failure.

**Validation Rules**

- Validation failures must identify missing or invalid fields.
- Access failures must be distinct from malformed input and empty successful results.
- Quota, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream failures must follow shared Layer 2 error conventions.
- Raw upstream bodies, credentials, tokens, stack traces, and unsafe request context must not appear in public errors.

## State Transitions

1. **Discovered**: Client reads `playlistItems_list` metadata, schema, usage notes, caveats, and examples.
2. **Submitted**: Client submits arguments for one request.
3. **Validated**: Local validation confirms `part`, exactly one selector, supported paging, supported fields, and eligible access context.
4. **Rejected**: Invalid requests fail before endpoint execution with a safe error outcome.
5. **Executed**: Valid requests invoke the YT-132 Layer 1 wrapper once.
6. **Mapped Success**: Layer 1 success is mapped to a public list result, including populated or empty collections.
7. **Mapped Failure**: Layer 1 failure is mapped to a safe public error category.

## Non-Persistent Data

All request, result, metadata, validation, and error state is request-scoped or file-documented. This slice introduces no database tables, durable queues, external storage, or retained playlist-item data.
