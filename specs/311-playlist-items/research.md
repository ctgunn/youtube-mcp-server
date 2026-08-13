# Research: YT-311 Playlist Items

## Decision: Build a concrete composed playlists-family descriptor

**Decision**: Add `playlists_getPlaylistItems` to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/playlists.py`, export it through the composed package, and default-register it through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

**Rationale**: The Layer 3 catalog already reserves this name in the playlists family, YT-310 establishes the concrete family pattern, and the feature requires a callable normalized tool rather than a representative contract or a near-raw endpoint surface.

**Alternatives considered**:

- Keep an inert representative descriptor: rejected because YT-311 requires invocation.
- Add behavior to `youtube_common/playlist_items.py`: rejected because that changes the Layer 2 near-raw boundary instead of adding the Layer 3 contract.
- Create a new source client or service: rejected because established handlers already provide execution, configuration, observability, and safe errors.

## Decision: Use exactly one playlist-scoped lower-layer listing

**Decision**: Invoke the existing playlist-item listing handler once with `part=snippet,contentDetails,status`, the validated `playlistId`, and the applied limit. Do not pass or accept a continuation token.

**Rationale**: The existing handler supports playlist-scoped public reads, the required fields, configured public-read access, and a limit of up to 50. One request preserves observed source order and satisfies the first-page-only bounded scope.

**Alternatives considered**:

- Direct item lookup: rejected because it cannot list a playlist.
- Multi-page traversal: rejected because continuation is out of scope.
- Per-video enrichment: rejected because it expands latency, quota use, and scope beyond playlist-item retrieval.

## Decision: Validate a Layer 3 request limit of 1 through 50 with default 25

**Decision**: Require trimmed nonblank `playlistId`; accept no unknown fields; accept optional whole-number `maxResults` from 1 through 50; apply 25 when it is absent.

**Rationale**: The feature specification defines this caller-facing contract. The lower layer allows a broader zero value, so the composed tool must validate the stricter Layer 3 minimum before it invokes the lower layer.

**Alternatives considered**:

- Expose raw `part`, `id`, or `pageToken` inputs: rejected because they leak endpoint-level choices and conflict with the constrained higher-level workflow.
- Accept zero: rejected because it contradicts the feature contract and does not retrieve videos.

## Decision: Normalize every exposed source item in observed order

**Decision**: Return an ordered collection with the source playlist identifier, applied limit, returned count, limited indicator, collection context, provenance, and item summaries. Each item retains available playlist position, playlist item identifier, video identifier, title, channel identity, publication time, and an availability state. Entries that the source exposes without usable public video details remain in their source position with an unavailable state; missing optional values are omitted rather than inferred.

**Rationale**: This satisfies the requirement to provide a concise agent-ready collection without losing the playlist sequence or silently concealing unavailable entries. The `status`, `snippet`, and `contentDetails` groups supply the available identity and availability signals needed without additional reads.

**Alternatives considered**:

- Return the lower-level `items` envelope: rejected because it leaks raw response complexity.
- Drop unavailable entries: rejected because it changes observed order and hides availability gaps.
- Fill absent details with empty values or guesses: rejected because it misrepresents source data.

## Decision: Treat successful empty collections separately from lower-layer failures

**Decision**: A successfully returned empty `items` collection is a successful empty result. Lower-layer resource-not-found, unavailable, authorization, quota, and source failures map to the documented safe Layer 3 failure categories. The contract does not infer why a source has produced an empty successful collection.

**Rationale**: The lower-level list contract explicitly defines empty item collections as successful. One bounded `playlistItems.list` response alone cannot safely distinguish an accessible empty playlist from all possible provider causes of an empty result; revealing or guessing a cause would violate the public-content and safety boundaries. Where the source reports a failure, the tool clearly distinguishes it from a successful empty collection.

**Alternatives considered**:

- Treat every empty list as unavailable: rejected because it violates the required successful-empty behavior.
- Add a playlist detail lookup to distinguish causes: rejected because it breaks the one-read scope and adds quota/latency.
- Expose provider-specific cause information: rejected because it leaks sensitive availability information and creates an unstable client contract.

## Decision: Reuse the shared Layer 3 safe error taxonomy and existing seams

**Decision**: Translate `PlaylistItemsListToolError` using the existing sanitizer and public taxonomy: `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure`. Register the descriptor beside `playlists_getPlaylist` with an injected `playlistItems_list` handler.

**Rationale**: The dispatcher already injects this lower-layer dependency, preserves request context and observability, and serializes error categories safely. The existing playlist-detail tool provides the exact local mapping and registration precedent.

**Alternatives considered**:

- Pass lower-layer categories directly to clients: rejected because it exposes endpoint-specific behavior.
- Build another registration or observability subsystem: rejected as unnecessary complexity.

## Decision: Require TDD and reStructuredText docstrings

**Decision**: Add failing unit, contract, integration, and routing tests before implementation; then add the minimum behavior; then refactor and run the full suite. Add or update reStructuredText docstrings on every new or changed Python function and test helper.

**Rationale**: This is required by the project constitution and aligns with existing composed-tool test conventions.

**Alternatives considered**:

- Use focused tests only: rejected by the full-suite constitution gate.
- Omit helper documentation: rejected by the constitution's docstring requirement.
