# Research: Search Playlist Items

## Decision 1: Traverse the existing lower-layer playlist-item listing privately

**Decision**: Implement a private composed-tool traversal that requests up to ten pages of 50 playlist entries through the existing `playlistItems_list` Layer 2 boundary. Stop when there is no next page or after 500 inspected entries. Keep continuation tokens entirely internal.

**Rationale**: The adjacent public `playlists_getPlaylistItems` contract makes exactly one 1-50-item request, declares `paginationTraversed: false`, and omits item descriptions. It therefore cannot meet the specified 500-entry coverage rule or search descriptions. The lower-layer listing already accepts a playlist-scoped continuation value and preserves the next-page indication, so a family-local traversal is sufficient and introduces no new integration.

**Alternatives considered**:

- Call `playlists_getPlaylistItems` once: rejected because it has a one-page public contract and cannot inspect more than 50 entries.
- Expose continuation input/output: rejected because the feature explicitly bounds one request and requires coverage reporting rather than caller-managed pagination.
- Fetch all playlist items without a cap: rejected because it makes the composite request unbounded and prevents predictable performance.

## Decision 2: Confirm playlist availability before accepting an empty item collection

**Decision**: Perform one existing direct playlist lookup before traversal. Treat a successful lookup with zero playlist items as a successful empty/no-match result; map unavailable or inaccessible lookup results to one safe unavailable-resource outcome.

**Rationale**: An empty item listing alone cannot prove whether a playlist is accessible and empty or unavailable. The feature requires these outcomes to be distinguishable while preserving the existing privacy-safe unavailable-resource behavior.

**Alternatives considered**:

- Infer availability from an empty item listing: rejected because it conflates accessible empty playlists with unavailable resources.
- Reveal detailed unavailability reasons: rejected because it could disclose private, restricted, deleted, or authorization-sensitive state.

## Decision 3: Use explainable literal matching and source order

**Decision**: Normalize a query by trimming it and collapsing whitespace. Compare the normalized phrase case-insensitively using Unicode case folding against available item title, description, channel title, and video identifier. Return matching entries in playlist position order and list matching fields in the fixed order title, description, channel title, video identifier.

**Rationale**: This provides repeatable, auditable search behavior for research clients without claiming relevance ranking, semantic understanding, transcript search, fuzzy search, or synonym support.

**Alternatives considered**:

- Relevance ranking: rejected because it adds an undocumented heuristic and breaks stable playlist order.
- Semantic or fuzzy matching: rejected because it would require an additional contract and creates unclear result explanations.
- Search only title: rejected because the feature explicitly supports matching playlist videos or items and the exposed description, channel title, and video identifier are useful public item fields.

## Decision 4: Make limits and incomplete coverage unambiguous

**Decision**: Return `appliedLimit`, `returnedCount`, `searchCoverage`, and `additionalMatchesOmitted`. `additionalMatchesOmitted` is `true` when a further match is observed, `false` when complete coverage proves no returned match was omitted, and `null` when the search cap prevents a definitive answer. Continue traversal after reaching the returned-match limit until the terminal page or 500-entry cap.

**Rationale**: Stopping as soon as enough matches are found could not prove whether the result is complete or whether coverage ended early. The tri-state signal avoids falsely claiming no omitted matches when the 500-entry cap is reached.

**Alternatives considered**:

- Boolean-only omission flag: rejected because `false` would be misleading for incomplete coverage.
- Return raw continuation tokens: rejected because they leak upstream state and shift a bounded search responsibility to callers.

## Decision 5: Reuse the established safe public error taxonomy and registration pattern

**Decision**: Map direct playlist and paged item-list failures to `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, or `upstream_failure`; sanitize all details. Export one concrete family descriptor and register it in the default dispatcher with existing injected handlers.

**Rationale**: Adjacent composed tools already provide the MCP-safe error boundary, dependency injection, descriptor shape, and registration convention. Reusing those conventions preserves machine-readable behavior and avoids a parallel error model.

**Alternatives considered**:

- Return raw lower-layer errors: rejected because they can expose internal diagnostics and are incompatible with the established public taxonomy.
- Register a separate standalone service: rejected because the current playlist family and dispatcher already provide the required composition boundary.
