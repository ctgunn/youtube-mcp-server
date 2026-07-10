# Data Model: Layer 2 Tool `playlistItems_update`

## Playlist Items Update Tool

**Description**: Public Layer 2 MCP tool named `playlistItems_update`, representing the endpoint-backed `playlistItems.update` operation.

**Fields**:

- `tool_name`: Constant public name `playlistItems_update`.
- `upstream_resource`: `playlistItems`.
- `upstream_method`: `update`.
- `operation_key`: `playlistItems.update`.
- `quota_cost`: Official quota cost `50`.
- `auth_mode`: OAuth-backed authorization required.
- `availability_state`: Active unless official documentation or local endpoint metadata records a caveat.
- `input_contract`: Schema for required part selection, target playlist-item identity, and writable update body.
- `response_convention`: Mutation result convention for an updated playlist-item resource.
- `examples`: Caller-facing successful and failure examples.

**Relationships**:

- Uses one Playlist Items Update Request per invocation.
- Produces one Playlist Items Update Result on success.
- Depends on the Layer 1 `playlistItems.update` wrapper.

**Validation Rules**:

- Must be discoverable through the default public tool registry.
- Must advertise quota cost `50` in metadata, description, usage notes, and examples.
- Must advertise OAuth-backed access before invocation.
- Must not advertise playlist-item listing, insertion, deletion, enrichment, analytics, ranking, recommendation, summarization, or automated curation.

## Playlist Items Update Request

**Description**: Caller-provided request for updating one existing playlist item.

**Fields**:

- `part`: Required non-empty supported part selection. Determines which updated playlist-item fields are returned.
- `body`: Required object carrying target identity and writable playlist-item update data.
- `body.id`: Required existing playlist-item identifier for the target update.
- `body.snippet`: Required object carrying writable playlist/video context fields.
- `body.snippet.playlistId`: Required target playlist identifier preserved for the updated item.
- `body.snippet.resourceId`: Required referenced resource identity object.
- `body.snippet.resourceId.videoId`: Required referenced video identifier preserved for the updated item.
- `body.snippet.resourceId.kind`: Optional supported resource kind when accepted by the contract; if supplied, it must identify a video resource.

**Relationships**:

- Contains Part Selection.
- Contains Target Playlist Item Identity.
- Contains Writable Update Data.
- Requires Authorization Context.

**Validation Rules**:

- `part` must be present, non-empty, supported, and free of duplicates or conflicts.
- `body` must be present and must be an object.
- `body.id` must be present and non-empty.
- `body.snippet.playlistId` must be present and non-empty.
- `body.snippet.resourceId.videoId` must be present and non-empty.
- Read-only, unsupported, conflicting, or undocumented fields must be rejected with caller-facing validation feedback.
- Placement and content-detail fields must be accepted only when explicitly documented by the public contract.
- Requests must not be treated as successful updates without OAuth-backed access.

## Part Selection

**Description**: Caller-selected playlist item resource sections that determine which updated playlist-item properties are returned.

**Fields**:

- `parts`: Ordered set of supported part names.

**Relationships**:

- Belongs to Playlist Items Update Request.
- Reflected in Playlist Items Update Result.

**Validation Rules**:

- Must be supplied for every update.
- Must use supported playlist-item writable parts only.
- Empty, malformed, duplicated, unsupported, or conflicting values must fail validation.

## Target Playlist Item Identity

**Description**: The identifier and core context needed to select the existing playlist item being updated.

**Fields**:

- `playlist_item_id`: Existing playlist-item identifier from `body.id`.
- `playlist_id`: Target playlist identifier preserved in the writable snippet.
- `video_id`: Referenced video identifier preserved in the writable snippet.
- `resource_kind`: Optional supported resource kind, constrained to video resources when supplied.

**Relationships**:

- Derived from Playlist Items Update Request body.
- Preserved as safe target/update context in Playlist Items Update Result.

**Validation Rules**:

- Existing playlist-item identity is required.
- Target playlist identity is required.
- Referenced video identity is required.
- Missing, empty, malformed, unsupported, read-only, or conflicting identity fields must fail validation.

## Writable Update Data

**Description**: Mutation payload that describes supported playlist-item fields the caller wants to update while excluding read-only or unsupported fields.

**Fields**:

- `snippet`: Required writable update section for this slice.
- `playlist_id`: Target playlist identifier.
- `video_id`: Referenced video identifier.
- `resource_kind`: Optional supported resource kind.

**Relationships**:

- Belongs to Playlist Items Update Request.
- Reflected safely in Playlist Items Update Result.

**Validation Rules**:

- The writable update body must include the supported snippet section.
- Placement, content details, read-only fields, unsupported fields, and undocumented optional parameters must fail validation unless explicitly added to the public contract.
- The tool must not silently ignore unsupported update data.

## Authorization Context

**Description**: Caller access state required to update playlist item resources.

**Fields**:

- `mode`: OAuth-backed authorization.
- `status`: Present, missing, invalid, insufficient, or unavailable.

**Relationships**:

- Required by Playlist Items Update Tool.
- Passed safely to the Layer 1 wrapper.
- Reflected in success and error context without exposing credentials.

**Validation Rules**:

- API-key-only access is not sufficient.
- Missing, invalid, or insufficient authorization must be categorized as access failure.
- Credentials, tokens, and secret-bearing diagnostics must never appear in results, metadata, examples, or errors.

## Updated Playlist Item Resource

**Description**: Playlist item record returned after a successful update.

**Fields**:

- `id`: Updated playlist item identifier when returned.
- `snippet`: Returned snippet fields according to selected parts.
- `contentDetails`: Returned content details according to selected parts when upstream returns them.
- `status`: Returned status fields according to selected parts when upstream returns them.
- `kind`: Returned upstream resource kind when available.
- `etag`: Returned upstream entity tag when available.

**Relationships**:

- Produced by the upstream `playlistItems.update` operation.
- Included in Playlist Items Update Result.

**Validation Rules**:

- Returned fields must be preserved without fabricated playlist, video, channel, transcript, ranking, analytics, or recommendation data.
- Optional fields omitted by the upstream service must remain omitted.

## Playlist Items Update Result

**Description**: Public success result for one updated playlist item.

**Fields**:

- `endpoint`: `playlistItems.update`.
- `quota_cost`: `50`.
- `requested_parts`: Selected part context.
- `target`: Safe target playlist-item identity context.
- `update`: Safe writable update context.
- `auth`: Safe authorization mode context.
- `item`: Updated playlist item resource or equivalent updated-resource payload.
- `kind`: Returned upstream kind when available.
- `etag`: Returned upstream entity tag when available.

**Relationships**:

- Produced by Playlist Items Update Tool.
- Contains Updated Playlist Item Resource.

**Validation Rules**:

- Must distinguish successful update from validation failures, authorization failures, quota failures, invalid writable-field failures, missing-resource failures, endpoint unavailable responses, deprecated behavior, and unexpected upstream failures.
- Must not include credentials, raw upstream diagnostics, stack traces, or unsafe request context.

## Quota Disclosure

**Description**: Caller-facing statement that each invocation costs 50 official quota units.

**Fields**:

- `quota_cost`: `50`.
- `scope`: Per invocation.
- `visibility`: Metadata, description, usage notes, examples, result context, and review evidence.

**Validation Rules**:

- Must remain consistent across discovery, examples, quickstart, tests, and contracts.

## Unsupported Boundary Guidance

**Description**: Caller-facing explanation of behaviors excluded from this low-level endpoint tool.

**Fields**:

- `out_of_scope_behaviors`: Playlist-item listing, insertion, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, heuristic classification, and cross-endpoint aggregation.

**Validation Rules**:

- Unsupported workflow requests must be rejected or clearly flagged as outside the contract.
- The tool must not masquerade as a Layer 3 workflow.

## State Transitions

1. **Request received**: Caller submits candidate `playlistItems_update` arguments.
2. **Local validation**: Tool validates part selection, body shape, target identity, writable update data, unsupported fields, and access context.
3. **Rejected before execution**: Invalid request or missing access returns a safe categorized error without calling the Layer 1 wrapper.
4. **Endpoint execution**: Valid request calls the Layer 1 `playlistItems.update` wrapper once.
5. **Successful update**: Returned playlist-item resource is mapped to a near-raw updated-resource result with safe context.
6. **Upstream failure**: Normalized upstream failure is mapped to a safe Layer 2 error category.
