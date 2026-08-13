# Feature Specification: Retrieve Playlist Items

**Feature Branch**: `[311-playlist-items]`

**Created**: 2026-08-12

**Status**: Draft

**Input**: User description: "Define and implement the higher-level playlist items tool."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Videos in a Playlist (Priority: P1)

An MCP client requests the videos in a known playlist and receives a concise, ordered collection that can be used directly in a research workflow.

**Why this priority**: Listing a playlist's videos is the feature's primary value and enables playlist-based research.

**Independent Test**: Invoke `playlists_getPlaylistItems` with a valid playlist identifier and confirm that the returned collection represents the videos in that playlist in playlist order.

**Acceptance Scenarios**:

1. **Given** a playlist containing available videos, **When** a client supplies its `playlistId`, **Then** the client receives normalized information for each returned video in playlist order.
2. **Given** a playlist with more videos than the requested limit, **When** a client supplies `maxResults`, **Then** the response contains no more than that number of videos and reports that the result is limited.

---

### User Story 2 - Bound Playlist Research (Priority: P2)

An MCP client limits a playlist request to the number of videos relevant to its current task, avoiding unnecessarily large results.

**Why this priority**: A caller-controlled limit makes the primary flow useful for both focused questions and larger playlists.

**Independent Test**: Invoke the tool with a valid playlist identifier and a valid `maxResults` value, then verify that the returned item count does not exceed that value.

**Acceptance Scenarios**:

1. **Given** a valid playlist identifier, **When** the client omits `maxResults`, **Then** the tool returns up to the documented default limit of 25 videos.
2. **Given** a valid playlist identifier, **When** the client supplies a limit from 1 through 50, **Then** the tool honors that limit.

---

### User Story 3 - Understand Unavailable Results (Priority: P3)

An MCP client receives a clear, actionable outcome when the playlist cannot be found, cannot be accessed, or contains unavailable items.

**Why this priority**: Clear outcomes prevent a research workflow from mistaking missing or inaccessible content for a successful empty result.

**Independent Test**: Invoke the tool with an unknown or inaccessible playlist identifier and verify that it returns an understandable failure rather than a misleading empty collection.

**Acceptance Scenarios**:

1. **Given** an unknown, inaccessible, or unauthorized playlist, **When** a client requests its videos, **Then** the client receives a clear failure that distinguishes the request from a successful empty playlist.
2. **Given** a playlist that includes unavailable, private, or deleted entries, **When** a client retrieves the playlist, **Then** the response preserves the playlist order and identifies any returned entry whose video details are unavailable without fabricating those details.

### Edge Cases

- A missing, blank, or malformed `playlistId` is rejected before a playlist lookup is attempted.
- A `maxResults` value that is not a whole number from 1 through 50 is rejected with a clear corrective message.
- An empty accessible playlist returns a successful collection with zero items.
- If fewer videos exist than the requested limit, all available items are returned.
- If item metadata is partially unavailable, the result identifies the unavailable item rather than omitting it silently or inventing missing values.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and contract tests for tool discovery metadata, required identifier validation, default and explicit limits, ordered normalized results, empty playlists, unavailable items, and inaccessible playlists.
- **Green**: Implement only the behavior needed for those tests: request validation, bounded retrieval, normalized collection shaping, and clear result states.
- **Refactor**: Consolidate shared playlist-result behavior only after the tests pass; run the full repository suite with `pytest` and retain the passing output as pull-request evidence.
- **Required test levels**: Unit tests for validation and result shaping, contract tests for the callable tool's input and output, and integration tests using the project’s controlled upstream boundary for retrieval outcomes.
- **Documentation**: Add or update reStructuredText docstrings for every new or changed Python function in scope, including its purpose, inputs, normalized result, and error behavior.
- **Review evidence**: The pull request must include the focused test command(s), `pytest`, and confirmation that each completed command exits successfully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a higher-level MCP tool named `playlists_getPlaylistItems` for retrieving the videos contained in one playlist.
- **FR-002**: The tool MUST require one non-blank `playlistId` that identifies the playlist to retrieve.
- **FR-003**: The tool MUST accept an optional whole-number `maxResults` value from 1 through 50 and return no more items than the requested limit.
- **FR-004**: When `maxResults` is omitted, the tool MUST return up to 25 items and communicate the applied limit in the result.
- **FR-005**: For every returned playlist entry, the tool MUST provide a normalized item containing the playlist position, video identifier when available, video title when available, channel identity when available, publication time when available, and availability state.
- **FR-006**: The tool MUST preserve the playlist's item order in the normalized collection.
- **FR-007**: The tool MUST report the number of returned items and whether the result is limited by the applied maximum, so a client can distinguish a complete collection from a partial one.
- **FR-008**: The tool MUST return a successful empty collection for an accessible playlist with no items.
- **FR-009**: The tool MUST return a clear, structured failure for a missing, malformed, unknown, inaccessible, or unauthorized playlist identifier and MUST NOT represent those conditions as a successful empty playlist.
- **FR-010**: When a playlist entry refers to unavailable, private, or deleted video content, the tool MUST retain the entry in its ordered result when the playlist exposes it, label its availability state, and omit unavailable details rather than inventing them.
- **FR-011**: The tool's description and returned result MUST identify it as a higher-level playlist-retrieval capability and present a stable, concise collection rather than exposing raw upstream response structure.
- **FR-012**: The tool MUST preserve the source playlist identifier in the result so clients can associate the collection with the request that produced it.

### Key Entities

- **Playlist request**: A client request identified by `playlistId` and an optional maximum number of returned items.
- **Playlist item**: One ordered entry in a playlist, with its position, available video and channel details, publication time, and availability state.
- **Playlist item collection**: The normalized ordered response for one playlist, including its source identifier, applied limit, returned count, and completeness signal.

### Assumptions

- A default limit of 25 and a maximum accepted limit of 50 provide a predictable, bounded result size for research workflows.
- The feature retrieves only the first requested set of playlist entries; it does not provide continuation or pagination controls in this slice.
- Availability depends on the access and metadata exposed for the requester; absent details are represented as unavailable rather than inferred.
- This slice depends on the shared Layer 3 contracts defined by YT-301.

### Out of Scope

- Creating, editing, reordering, or deleting playlist entries.
- Retrieving video transcripts, statistics, comments, or other video enrichments beyond the normalized playlist item details.
- Fetching additional pages beyond the applied result limit.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In acceptance testing, 100% of valid requests for representative accessible playlists return an ordered normalized collection containing no more than the applied limit.
- **SC-002**: In acceptance testing, 100% of requests with a missing, malformed, or out-of-range input receive a clear corrective failure and do not return a successful collection.
- **SC-003**: In acceptance testing, 100% of representative empty, inaccessible, and unavailable-item cases are distinguishable from one another by the result state and availability information.
- **SC-004**: In a usability review of five representative MCP research tasks, at least four reviewers can identify the requested playlist, item order, returned-item count, and whether the result is limited without consulting raw source data.
