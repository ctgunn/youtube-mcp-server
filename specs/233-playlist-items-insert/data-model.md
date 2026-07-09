# Data Model: Layer 2 Tool `playlistItems_insert`

## Playlist Items Insert Tool

**Description**: Public Layer 2 MCP tool named `playlistItems_insert`, representing the endpoint-backed `playlistItems.insert` operation.

**Fields**:

- `tool_name`: Constant public name `playlistItems_insert`.
- `upstream_resource`: `playlistItems`.
- `upstream_method`: `insert`.
- `operation_key`: `playlistItems.insert`.
- `quota_cost`: Official quota cost `50`.
- `auth_mode`: OAuth-backed authorization required.
- `availability_state`: Active unless official documentation or local endpoint metadata records a caveat.
- `input_contract`: Schema for required part selection and playlist-item creation body.
- `response_convention`: Mutation result convention for a created playlist-item resource.
- `examples`: Caller-facing successful and failure examples.

**Relationships**:

- Uses one Playlist Items Insert Request per invocation.
- Produces one Playlist Items Insert Result on success.
- Depends on the Layer 1 `playlistItems.insert` wrapper.

**Validation Rules**:

- Must be discoverable through the default public tool registry.
- Must advertise quota cost `50` in metadata, description, usage notes, and examples.
- Must advertise OAuth-backed access before invocation.
- Must not advertise playlist-item listing, update, deletion, enrichment, analytics, ranking, recommendation, summarization, or automated curation.

## Playlist Items Insert Request

**Description**: Caller-provided request for creating one playlist item.

**Fields**:

- `part`: Required non-empty supported part selection. Determines which created playlist-item fields are returned.
- `body`: Required object carrying writable playlist-item creation data.
- `body.snippet`: Required object carrying playlist/video assignment fields.
- `body.snippet.playlistId`: Required target playlist identifier.
- `body.snippet.resourceId`: Required referenced resource identity object.
- `body.snippet.resourceId.videoId`: Required referenced video identifier.
- `body.snippet.resourceId.kind`: Optional supported resource kind when accepted by the contract; if supplied, it must identify a video resource.
- `body.snippet.position`: Optional placement context only when explicitly supported.

**Relationships**:

- Contains Part Selection.
- Contains Playlist/Video Assignment Data.
- May contain Placement Context.
- Requires Authorization Context.

**Validation Rules**:

- `part` must be present, non-empty, supported, and free of duplicates or conflicts.
- `body` must be present and must be an object.
- `body.snippet.playlistId` must be present and non-empty.
- `body.snippet.resourceId.videoId` must be present and non-empty.
- Read-only, unsupported, conflicting, or undocumented fields must be rejected with caller-facing validation feedback.
- Placement fields must be accepted only when documented by the public contract.
- Requests must not be treated as successful insertions without OAuth-backed access.

## Part Selection

**Description**: Caller-selected playlist item resource sections that determine which created playlist-item properties are returned.

**Fields**:

- `parts`: Ordered set of supported part names.

**Relationships**:

- Belongs to Playlist Items Insert Request.
- Reflected in Playlist Items Insert Result.

**Validation Rules**:

- Must be supplied for every insertion.
- Must use supported playlist-item parts only.
- Empty, malformed, duplicated, unsupported, or conflicting values must fail validation.

## Playlist/Video Assignment Data

**Description**: Writable creation payload that identifies the target playlist and the video to add.

**Fields**:

- `playlist_id`: Target playlist identifier.
- `video_id`: Referenced video identifier.
- `resource_kind`: Optional supported resource kind, constrained to video resources when supplied.

**Relationships**:

- Derived from Playlist Items Insert Request body.
- Preserved as safe assignment context in Playlist Items Insert Result.

**Validation Rules**:

- Target playlist identity is required.
- Referenced video identity is required.
- Missing, empty, malformed, unsupported, read-only, or conflicting assignment fields must fail validation.

## Placement Context

**Description**: Optional supported caller intent for where the new playlist item should appear.

**Fields**:

- `position`: Optional supported insertion position when accepted by the contract.

**Relationships**:

- Belongs to Playlist Items Insert Request.
- Reflected in Playlist Items Insert Result when supplied and accepted.

**Validation Rules**:

- Must be omitted unless explicitly supported by the contract.
- Empty, malformed, duplicate, conflicting, unsupported, or out-of-bound placement fields must fail validation.

## Authorization Context

**Description**: Caller access state required to insert playlist item resources.

**Fields**:

- `mode`: OAuth-backed authorization.
- `status`: Present, missing, invalid, insufficient, or unavailable.

**Relationships**:

- Required by Playlist Items Insert Tool.
- Passed safely to the Layer 1 wrapper.
- Reflected in success and error context without exposing credentials.

**Validation Rules**:

- API-key-only access is not sufficient.
- Missing, invalid, or insufficient authorization must be categorized as access failure.
- Credentials, tokens, and secret-bearing diagnostics must never appear in results, metadata, examples, or errors.

## Created Playlist Item Resource

**Description**: Playlist item record returned after a successful insertion.

**Fields**:

- `id`: Created playlist item identifier when returned.
- `snippet`: Returned snippet fields according to selected parts.
- `contentDetails`: Returned content details according to selected parts.
- `status`: Returned status fields according to selected parts.
- `kind`: Returned upstream resource kind when available.
- `etag`: Returned upstream entity tag when available.

**Relationships**:

- Produced by the upstream `playlistItems.insert` operation.
- Included in Playlist Items Insert Result.

**Validation Rules**:

- Returned fields must be preserved without fabricated playlist, video, channel, transcript, ranking, analytics, or recommendation data.
- Optional fields omitted by the upstream service must remain omitted.

## Playlist Items Insert Result

**Description**: Public success result for one created playlist item.

**Fields**:

- `endpoint`: `playlistItems.insert`.
- `quota_cost`: `50`.
- `requested_parts`: Selected part context.
- `assignment`: Safe playlist/video assignment context.
- `placement`: Safe placement context when supplied and accepted.
- `auth`: Safe authorization mode context.
- `item`: Created playlist item resource or equivalent created-resource payload.
- `kind`: Returned upstream kind when available.
- `etag`: Returned upstream entity tag when available.

**Relationships**:

- Produced by Playlist Items Insert Tool.
- Contains Created Playlist Item Resource.

**Validation Rules**:

- Must distinguish successful insertion from validation failures, authorization failures, quota failures, duplicate or ineligible video failures, missing-resource failures, endpoint unavailable responses, deprecated behavior, and unexpected upstream failures.
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

- `out_of_scope_behaviors`: Playlist-item listing, update, deletion, playlist search, playlist generation, video enrichment, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated curation, heuristic classification, and cross-endpoint aggregation.

**Validation Rules**:

- Unsupported workflow requests must be rejected or clearly flagged as outside the contract.
- The tool must not masquerade as a Layer 3 workflow.

## State Transitions

1. **Request received**: Caller submits candidate `playlistItems_insert` arguments.
2. **Local validation**: Tool validates part selection, body shape, assignment fields, placement boundaries, unsupported fields, and access context.
3. **Rejected before execution**: Invalid request or missing access returns a safe categorized error without calling the Layer 1 wrapper.
4. **Endpoint execution**: Valid request calls the Layer 1 `playlistItems.insert` wrapper once.
5. **Successful insertion**: Returned playlist-item resource is mapped to a near-raw created-resource result with safe context.
6. **Upstream failure**: Normalized upstream failure is mapped to a safe Layer 2 error category.
