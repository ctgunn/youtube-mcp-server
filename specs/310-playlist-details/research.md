# Research: YT-310 Playlist Details

## Decision: Build a concrete composed playlists-family descriptor

**Rationale**: YT-301 already reserves `playlists_getPlaylist` in the public playlists family, while `src/mcp_server/tools/youtube_composed/playlists.py` currently contains only family scaffolding. Existing concrete composed tools use a descriptor, metadata builder, validator, normalizer, safe error type, handler, package export, and default-dispatcher registration.

**Alternatives considered**:

- Keep an inert representative descriptor: rejected because YT-310 requires a callable higher-level tool.
- Add the behavior to the Layer 2 `playlists_list` tool: rejected because that would change a near-raw endpoint contract rather than add the normalized Layer 3 contract.

## Decision: Use exactly one direct `playlists.list` lookup

**Rationale**: The existing lower-level handler supports public direct lookup by identifier. One request with `id` and the `snippet,contentDetails,status` detail groups supplies the required available public fields: playlist identity, descriptive metadata, channel attribution, publication time, thumbnails, item count, and privacy visibility. It satisfies the one-playlist boundedness requirement without pagination or fan-out.

**Alternatives considered**:

- Multiple lookups for metadata groups: rejected because one request can return the required groups and has lower quota, latency, and failure exposure.
- Playlist-item retrieval: rejected because YT-310 explicitly returns playlist details only; entries belong to YT-311.
- Owner-scoped `mine` lookup: rejected because this feature requires a caller-provided playlist identifier and must remain public-read focused.

## Decision: Normalize only available public fields and include explicit provenance

**Rationale**: The public result will copy only available values from the lower-level item: `playlistId`, `title`, `description`, `channelId`, `channelTitle`, `publishedAt`, `thumbnails`, `privacyStatus`, and `itemCount`. A `fieldProvenance` mapping distinguishes `playlistId` as source-preserved from public field mappings and result context as normalized. A normalized scope context declares that item entries are absent and points callers to `playlists_getPlaylistItems`.

**Alternatives considered**:

- Return the lower-level `items` envelope unchanged: rejected because it leaves provider-specific structure for agents to interpret.
- Fill missing fields with empty strings, zeros, or guessed values: rejected because it misrepresents sparse source data.
- Include item summaries: rejected because it expands the scope to the YT-311 workflow.

## Decision: Map failures to the shared five-category Layer 3 taxonomy

**Rationale**: `PlaylistsListToolError` already exposes safe lower-layer categories, and the shared conventions sanitize error details. Empty or malformed lookup results become a generic `unavailable_resource`; lower access, quota, and source-service failures map to `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure`. No error reveals whether a playlist is private, deleted, restricted, or absent.

**Alternatives considered**:

- Surface lower-layer categories unchanged: rejected because it leaks endpoint-specific behavior and violates the Layer 3 contract.
- Distinguish unavailable reasons: rejected because the specification requires one safe unavailable outcome.
- Return partial details after a required lookup failure: rejected because the tool has one required lookup and no usable detail result exists when it fails.

## Decision: Reuse existing dispatcher, observability, and test seams

**Rationale**: The default dispatcher already injects configured dependencies into concrete composed tools and carries request context through the existing MCP path. The plan adds the playlist lookup handler at that same seam, retaining existing logs and safe protocol serialization. Existing video and channel composed-tool tests provide the unit, contract, integration, and routing patterns.

**Alternatives considered**:

- Add a new client or registration subsystem: rejected because the existing lower-layer handler and dispatcher already supply the required behavior.
- Add feature-specific persistence or metrics: rejected because the feature has no state and existing request-level observability is sufficient.

## Decision: Require TDD and reStructuredText docstrings

**Rationale**: The project constitution requires Red-Green-Refactor execution, integration coverage, a final full-suite run, and reStructuredText docstrings for every new or modified Python function. New validator, normalizer, mapper, handler, descriptor, and test-double functions must document parameters, returns, raised errors where relevant, and public/safe behavior.

**Alternatives considered**:

- Focused tests only: rejected by the constitution's mandatory full-suite gate.
- Undocumented helpers: rejected by the constitution's documentation requirement.
