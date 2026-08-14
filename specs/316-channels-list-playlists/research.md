# Research: YT-316 Channel Playlist Listing

## Decision: Extend the composed channels family and reuse playlist listing

**Decision**: Implement the public tool in the existing composed channels family and inject the existing lower-layer `playlists_list` handler.

**Rationale**: The channel-facing name belongs to that family, while the lower layer already owns public-read execution, authentication, quota behavior, request correlation, and safe source errors.

**Alternatives considered**:

- Create a new source client: rejected because it duplicates configured execution behavior.
- Expose the lower-layer result unchanged: rejected because it leaks near-raw response complexity.
- Place the tool in the playlist family: rejected because it breaks the public catalog's channel grouping.

## Decision: Verify the channel, then make one bounded channel-scoped listing read

**Decision**: Validate inputs, verify the channel once with the existing channel-listing capability, then call the playlist layer once with `part` set to `snippet,contentDetails,status`, the normalized `channelId`, and the applied limit.

**Rationale**: The verification distinguishes an unavailable channel from a valid channel with no accessible playlists, as the feature specification requires, while remaining a fixed two-read composition.

**Alternatives considered**:

- Traverse additional pages or enrich every playlist: rejected because pagination and enrichment are out of scope.
- Search or rank playlists: rejected because the feature is a listing, not discovery by relevance.

## Decision: Preserve source order and normalize only documented fields

**Decision**: Preserve returned source order; return `playlistId`, `title`, and available description, channel identity, publication time, thumbnails, item count, and visibility; omit unavailable optional values.

**Rationale**: The result remains predictable for agents without inventing metadata or applying an undisclosed ordering rule.

**Alternatives considered**:

- Sort chronologically or by popularity: rejected because no ranking behavior is promised.
- Substitute empty or inferred metadata: rejected because it obscures source availability.
- Return malformed records lacking stable identity or title: rejected because they cannot meet the public record contract.

## Decision: Default to 25 and bound to 1–50

**Decision**: `maxResults` defaults to 25 and accepts whole numbers from 1 through 50 only.

**Rationale**: This matches existing composed playlist-listing conventions and provides useful, readable bounded responses.

**Alternatives considered**:

- Allow zero or unbounded values: rejected because they make intent and response size ambiguous.
- Use a larger default: rejected because it increases typical agent response size without a stated need.

## Decision: Distinguish empty success from safe failures

**Decision**: A verified channel with a successful empty playlist collection becomes an empty successful result. A channel verification with no usable match is `unavailable_resource`. Lower-layer invalid, access-sensitive, quota, and other source failures map to `invalid_parameters`, `authorization_sensitive_data`, `quota_exhaustion`, and `upstream_failure` respectively, with sanitized details.

**Rationale**: Callers can distinguish no accessible playlists from a failed request without sensitive diagnostics.

**Alternatives considered**:

- Treat all empty results as unavailable channel: rejected because a channel may validly have no accessible playlists.
- Surface lower-layer categories and payloads directly: rejected because that weakens the stable Layer 3 boundary.

## Decision: Correct the lower-layer dependency reference in planning artifacts

**Decision**: Plan against YT-210 (`channels.list`) and YT-236 (`playlists.list`). The feature specification's YT-237 label refers to playlist creation and is not an executable dependency here; the seed's required dependency remains YT-301.

**Rationale**: The actual handler and required source fields are provided by playlist listing, not creation.

**Alternatives considered**:

- Use YT-237: rejected because it is a mutation and cannot produce a channel playlist list.
- Add a new wrapper: rejected because the suitable listing wrapper already exists.

## Decision: Use contract-first Red-Green-Refactor verification

**Decision**: Add failing unit, contract, integration, and routing tests before code; implement the smallest behavior; refactor shared local helpers; then run the full test suite and Ruff.

**Rationale**: This satisfies the constitution's mandatory TDD, contract, regression, documentation, security, and full-suite requirements.

**Alternatives considered**:

- Test only the handler: rejected because discovery and default registration are public boundaries.
- Run focused tests only: rejected because the constitution requires a final full-suite run.
