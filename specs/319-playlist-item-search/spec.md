# Feature Specification: Search Playlist Items

**Feature Branch**: `[319-playlist-item-search]`  
**Created**: 2026-08-16  
**Status**: Draft  
**Input**: User description: "Define and implement the YT-319 higher-level `playlists_searchItems` tool, enabling MCP clients to search within a playlist for matching videos or items."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search a Known Playlist (Priority: P1)

An MCP client supplies a playlist identifier and a research phrase, then receives the matching accessible playlist items in a concise, predictable form.

**Why this priority**: Finding relevant videos within a known collection is the feature's core research value.

**Independent Test**: Search a representative accessible playlist containing matching and non-matching items, then verify that every returned item matches the documented phrase rules and no non-matching item is returned.

**Acceptance Scenarios**:

1. **Given** an accessible playlist containing items whose available title, description, channel name, or video identifier matches a phrase, **When** a client supplies its `playlistId` and `query`, **Then** the client receives those matching items in their playlist order with the field or fields that matched.
2. **Given** an accessible playlist with no items matching the phrase, **When** a client searches it, **Then** the client receives a successful empty result that identifies the playlist and applied search phrase.

---

### User Story 2 - Bound a Search Result (Priority: P2)

An MCP client limits the number of matching items returned so it can keep a research response focused while knowing whether more matches exist.

**Why this priority**: A caller-controlled result size makes the primary search usable in both focused and broad research workflows.

**Independent Test**: Search a playlist with more matching items than the requested limit and confirm that the result contains no more than that limit and explicitly reports that it is limited.

**Acceptance Scenarios**:

1. **Given** a valid playlist and query, **When** the client omits `maxResults`, **Then** the tool returns up to the documented default of 25 matching items.
2. **Given** a valid playlist and query with more than the requested number of matches, **When** the client supplies a whole-number `maxResults` from 1 through 50, **Then** the result contains no more than that number and states that additional matches were not returned.

---

### User Story 3 - Understand Search Coverage and Failures (Priority: P3)

An MCP client can distinguish a complete no-match result from an incomplete search, unavailable playlist, invalid request, or item whose details cannot safely be searched.

**Why this priority**: Research workflows must not mistake an access problem or bounded search for proof that a playlist has no relevant content.

**Independent Test**: Exercise invalid input, an inaccessible playlist, a playlist exceeding the documented inspection bound, and entries with unavailable details; verify that each outcome is distinguishable and contains no private information.

**Acceptance Scenarios**:

1. **Given** a playlist with more than 500 accessible entries to inspect, **When** the search reaches that inspection bound, **Then** the result states that search coverage is incomplete and identifies the number of entries inspected.
2. **Given** a missing, malformed, unknown, or inaccessible playlist, **When** a client searches it, **Then** the client receives a clear, safe structured failure rather than a successful empty result.
3. **Given** a playlist entry with unavailable or private video details, **When** a client searches the playlist, **Then** the tool does not infer missing content; it only returns that entry if exposed searchable information matches and labels its availability state.

### Edge Cases

- A request with a missing, blank, non-text, or whitespace-only `playlistId` or `query` is rejected before the search begins.
- A `query` with repeated internal whitespace is searched as one space-separated phrase; matching is case-insensitive but otherwise literal, so it does not imply synonym, semantic, or transcript search.
- A `maxResults` value that is not a whole number from 1 through 50 is rejected with a clear corrective message.
- An accessible empty playlist and an accessible playlist with no matching items both return successful empty collections; an inaccessible playlist does not.
- If fewer matches exist than the applied limit, all matches in the inspected scope are returned and the result states whether that scope was complete.
- If the result reaches `maxResults`, the tool identifies that additional matching items exist when the inspected scope establishes this; it does not claim the returned set is exhaustive when coverage is incomplete.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and contract tests for discovery metadata; required identifiers and query validation; phrase normalization; case-insensitive literal matching; matching-field disclosure; source-order results; default and explicit limits; empty results; coverage reporting; unavailable items; and safe failure outcomes.
- **Green**: Implement only the behavior required to make those tests pass: validated composite playlist-item retrieval, bounded inspection, documented matching, normalized result shaping, and safe outcome mapping.
- **Refactor**: After the focused tests pass, consolidate only duplicated playlist-search validation, matching, and normalized-result rules through the shared Layer 3 contracts; run the full repository suite with `python3 -m pytest` and `python3 -m ruff check .` and retain passing output as pull-request evidence.
- **Required test levels**: Unit tests for input validation, text matching, coverage, and result shaping; contract tests for discovery metadata and callable input/output behavior; and integration-style tests using controlled upstream outcomes for populated, empty, unavailable, and incomplete-coverage playlists.
- **Documentation**: Add or update reStructuredText docstrings for every new or changed Python function in scope, including its purpose, inputs, matching and coverage behavior, result, and safe error behavior.
- **Review evidence**: The pull request must show focused tests moving from failing to passing and successful `python3 -m pytest` and `python3 -m ruff check .` results, including evidence for matching, no-match, limit, incomplete-coverage, unavailable-item, and unavailable-playlist cases.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a higher-level MCP tool named `playlists_searchItems` for finding matching items within one playlist.
- **FR-002**: The tool MUST require non-blank text values for `playlistId` and `query`, trim surrounding whitespace from both values, and reject missing, blank, non-text, or unsupported input fields with a safe validation outcome before searching.
- **FR-003**: The tool MUST accept an optional whole-number `maxResults` value from 1 through 50; when omitted, it MUST return up to 25 matching items and communicate the applied limit.
- **FR-004**: The tool MUST be documented and behave as a composite higher-level capability: it retrieves playlist items and applies the documented matching and result-shaping rules, rather than representing a single source operation unchanged.
- **FR-005**: The tool MUST normalize the query by trimming it, collapsing repeated whitespace to one space, and comparing it case-insensitively as a literal phrase against each available item title, description, channel name, and video identifier. It MUST NOT claim semantic, synonym, transcript, or fuzzy matching.
- **FR-006**: The tool MUST return matches in ascending playlist position, without ranking or reordering them, and MUST identify the available field or fields that caused each returned item to match.
- **FR-007**: Each returned item MUST provide its playlist position, playlist-item identifier when available, video identifier when available, title, description, channel identity, publication time, availability state, and matching fields; unavailable values MUST be represented as unavailable rather than invented.
- **FR-008**: The tool MUST inspect at most the first 500 accessible playlist entries in playlist order for one request. The result MUST report the number inspected and whether the search coverage is complete, so a client can distinguish a complete search from a bounded one.
- **FR-009**: The result MUST preserve the requested playlist identifier, normalized query, applied limit, returned-match count, coverage state, and whether additional matching items were omitted by the applied result limit.
- **FR-010**: An accessible empty playlist or accessible playlist with no matching items MUST return a successful empty collection. A missing, malformed, unknown, inaccessible, unauthorized, or otherwise unavailable playlist MUST return a clear, safe structured failure and MUST NOT be represented as a successful empty collection.
- **FR-011**: When an entry has unavailable, private, or deleted details, the tool MUST not infer missing text or identity. It MAY return the entry only when exposed searchable information satisfies the matching rule, and it MUST label the entry's availability state.
- **FR-012**: The tool's discovery metadata and returned results MUST describe its composite boundary, required and optional inputs, default and maximum result limits, 500-entry inspection bound, matching fields and semantics, source-order policy, normalized fields, and safe error categories.
- **FR-013**: The tool MUST return distinct, safe structured outcomes for invalid parameters, unavailable resources, authorization-sensitive data, capacity exhaustion, and source-service failures. These outcomes MUST exclude credentials, private content, internal traces, and raw source payloads.

### Key Entities

- **Playlist search request**: A client request containing a playlist identifier, literal query phrase, and optional maximum number of returned matches.
- **Searchable playlist item**: One playlist entry with its position, available public item and video details, availability state, and available fields that can satisfy a query.
- **Playlist search result**: The normalized response containing matching items, applied limit, returned count, search-coverage state, and any indication that additional matches were omitted.
- **Search coverage**: The number of playlist entries inspected and whether every accessible entry was searched within the feature's 500-entry bound.

### Assumptions

- YT-301 supplies the shared Layer 3 conventions for naming, input validation, normalized response and provenance fields, composition, and safe errors.
- YT-311 supplies normalized playlist-item retrieval that this feature composes with its own matching and search-result behavior.
- A default of 25 returned matches, a maximum of 50 returned matches, and inspection of no more than 500 entries balance focused research responses with predictable request scope.
- Search results preserve playlist order rather than applying a relevance heuristic, because a literal field match and source sequence give clients explainable, repeatable behavior.
- The feature searches available playlist-item metadata only. Transcript search, semantic search, synonym expansion, and changes to playlist content are outside this slice.

### Out of Scope

- Creating, editing, reordering, or deleting playlists or playlist entries.
- Searching video transcripts, comments, captions, channel-wide content, or YouTube content outside the requested playlist.
- Semantic, fuzzy, synonym, or relevance-ranked search.
- Returning more than 50 matches, inspecting more than 500 playlist entries, pagination controls, or continuation tokens.
- Enriching matching items with video statistics, comments, transcripts, or owner-only data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid searches against representative accessible playlists return only items satisfying the documented matching rule, in playlist order, with their matching fields identified.
- **SC-002**: In automated acceptance testing, 100% of requests with omitted, invalid, or out-of-range inputs receive a clear corrective failure and do not return a successful collection.
- **SC-003**: In automated acceptance testing, 100% of no-match, result-limited, incomplete-coverage, unavailable-item, and unavailable-playlist cases are distinguishable through the documented result or error state.
- **SC-004**: Under normal source availability, at least 95% of representative searches that inspect no more than 500 accessible playlist entries produce their structured outcome within 10 seconds.
- **SC-005**: In a task-based review with five representative MCP research tasks, at least four reviewers can construct a valid request, identify why each returned item matched, and tell whether the result is complete without consulting source-specific response data.
