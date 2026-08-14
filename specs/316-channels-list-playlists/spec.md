# Feature Specification: Layer 3 Channel Playlist Listing

**Feature Branch**: `316-channels-list-playlists`  
**Created**: 2026-08-14  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level channel playlist listing tool. As an MCP client, I can retrieve the playlists associated with a channel. The tool must require channelId, accept optional maxResults, and return playlist listings normalized for agent consumption and consistent with the playlist tool family."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List a Channel's Playlists (Priority: P1)

An MCP client retrieves the playlists associated with one channel and receives a stable, agent-readable list that identifies each playlist and its useful available metadata.

**Why this priority**: This is the feature's core research action: it lets an agent discover the collections of videos available from a known channel.

**Independent Test**: Request playlists for a channel with known public playlists and verify that the result identifies the requested channel and returns the expected normalized playlist records in source order.

**Acceptance Scenarios**:

1. **Given** a channel with publicly available playlists, **When** a client supplies its `channelId`, **Then** it receives a successful structured result identifying that channel and an ordered collection of normalized playlist records.
2. **Given** a returned playlist has available title, description, publication time, item count, or visibility metadata, **When** a client retrieves the channel's playlists, **Then** the corresponding normalized record includes that available metadata without inventing a value for unavailable metadata.
3. **Given** a channel has no playlists available to the caller, **When** a client supplies its `channelId`, **Then** it receives a successful result with an empty playlist collection rather than a failure.

---

### User Story 2 - Bound a Playlist Listing (Priority: P2)

An MCP client requests only the number of playlists it can use in its current workflow and can tell how many records were returned.

**Why this priority**: A bounded result keeps research responses usable when a channel has a large collection of playlists.

**Independent Test**: Request a channel with more available playlists than the requested limit and verify that the collection contains no more records than the limit, retains source order, and reports the returned count.

**Acceptance Scenarios**:

1. **Given** a channel has more available playlists than the client requests, **When** the client supplies a valid `maxResults`, **Then** the result contains no more than that number of playlist records in source order.
2. **Given** a client omits `maxResults`, **When** it requests a channel's playlists, **Then** the result applies the documented default limit and reports the number of records returned.
3. **Given** a client supplies a non-integer, zero, negative, or greater-than-50 `maxResults`, **When** it requests a listing, **Then** it receives a safe validation outcome before the listing is attempted.

---

### User Story 3 - Receive Actionable Unavailable Outcomes (Priority: P3)

An MCP client receives a clear, safe outcome when the requested channel cannot be used for playlist retrieval, rather than confusing that condition with an empty playlist list.

**Why this priority**: Agents need to distinguish a channel with no available playlists from an invalid identifier, unavailable channel, access restriction, or temporary source limitation before choosing a next step.

**Independent Test**: Exercise missing and invalid identifiers, an unavailable channel, an access-restricted listing, and a source failure; verify each produces its documented safe outcome and none is represented as an empty successful list.

**Acceptance Scenarios**:

1. **Given** `channelId` is missing, blank, or not text, **When** a client calls the tool, **Then** it receives a safe validation outcome before playlist retrieval begins.
2. **Given** a requested channel is unavailable or its playlists are not accessible to the caller, **When** a client requests the listing, **Then** it receives a safe availability or access outcome distinct from an empty playlist collection.
3. **Given** the playlist source is temporarily unavailable or limited, **When** a client requests the listing, **Then** it receives a safe source-limitation outcome without internal diagnostics or sensitive information.

### Edge Cases

- A valid channel may have no playlists visible to the caller; this is a successful empty collection, not an unavailable-channel or source-failure outcome.
- Some playlists or metadata fields may be unavailable to the caller; the result includes only accessible playlist records and represents unavailable optional metadata as absent rather than fabricated.
- A client may request a limit larger than the number of available playlists; the result returns all available records up to the requested limit and reports the actual count.
- Playlist titles or descriptions may be empty; the result preserves the available source value and does not substitute a generated title or summary.
- Invalid identifiers, unavailable channels, access restrictions, source limitations, and unexpected failures are distinct from one another and do not expose credentials, internal traces, or raw source diagnostics.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing unit and contract tests for required-channel validation, optional-result-limit validation, default and bounded result counts, source ordering, normalized playlist fields, empty successful results, and every documented unavailable outcome.
- **Green**: Add only the behavior needed to validate the request, retrieve playlists associated with one channel, shape the documented stable records, preserve source order, apply the result limit, and present safe outcomes.
- **Refactor**: Consolidate shared channel-listing validation and playlist-result shaping where appropriate without changing the public contract. Add or update reStructuredText docstrings for every new or changed Python function in scope, then run the complete repository quality suite.
- **Required test levels**: unit tests for validation, limiting, ordering, field normalization, and outcome mapping; contract tests for public inputs and structured results; integration tests using representative playlist listings; and end-to-end invocation coverage where the hosted test environment is available.
- **Pull-request evidence**: Show focused tests moving from failing to passing, then show successful `pytest` and `ruff check .` results for the complete repository. Include evidence for a default-limit request, an explicit limit, an empty successful listing, invalid input, unavailable channel, restricted access, and source-limitation outcomes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a public higher-level tool named `channels_listPlaylists` that lists playlists associated with exactly one channel.
- **FR-002**: The tool MUST require `channelId` as one non-empty text identifier and MUST reject a missing, blank, or non-text value with a safe validation outcome before attempting playlist retrieval.
- **FR-003**: The tool MUST accept an optional `maxResults` as an integer from 1 through 50, defaulting to 25 when omitted, and MUST reject a value outside that range or a non-integer value with a safe validation outcome.
- **FR-004**: For a successful non-empty listing, the result MUST identify the requested channel, include an ordered collection of playlist records, and state the number of records returned.
- **FR-005**: Each playlist record MUST include a stable `playlistId` and `title`; when available to the caller, it MUST also include the source-provided description, publication time, item count, visibility, and owning channel identifier.
- **FR-006**: The tool MUST preserve the source ordering of returned playlists and apply `maxResults` without re-ranking, filtering, or generating playlists.
- **FR-007**: When the requested channel has no playlists available to the caller, the tool MUST return a successful structured result with an empty playlist collection and a returned-record count of zero.
- **FR-008**: The tool MUST distinguish normalized playlist fields from any source-provided fields in its discovery information and caller documentation. This tool does not return heuristic or inferred playlist fields.
- **FR-009**: The tool MUST return distinct, safe caller-visible outcomes for invalid input, unavailable channel, access restriction, source quota or availability limitation, and unexpected source failure; none of these outcomes may be represented as a successful empty playlist list.
- **FR-010**: Validation, access-restriction, source-limitation, and unexpected-failure outcomes MUST NOT expose credentials, internal traces, raw source payloads, or other sensitive diagnostics.
- **FR-011**: The tool's discovery information and caller documentation MUST state the required and optional inputs, default and permitted `maxResults` values, result ordering, normalized record fields, empty-list meaning, and all caller-visible limitation categories.
- **FR-012**: The feature MUST remain limited to listing playlists for one channel. Retrieving playlist items, searching playlist contents, modifying playlists, listing across multiple channels, pagination beyond the single bounded result, ranking, and recommendation are out of scope.

### Key Entities

- **Channel Playlist Request**: A request identifying one channel and an optional maximum number of playlist records to return.
- **Normalized Playlist Record**: A stable, agent-readable representation of an accessible playlist, including its identifier, title, and available metadata.
- **Channel Playlist Listing**: The requested channel, ordered playlist collection, and returned-record count for a successful request.
- **Playlist Listing Outcome**: Either a successful listing or a safe, caller-visible explanation of why a listing could not be produced.

## Scope

### In Scope

- Listing the accessible playlists associated with one channel.
- Required channel identification and optional bounded result count.
- Stable playlist records, source-order preservation, and clear empty-list semantics.
- Safe, distinct outcomes for validation, availability, access, source limitation, and unexpected failure conditions.

### Out of Scope

- Fetching playlist details beyond the fields in the returned list records or retrieving playlist items.
- Searching, ranking, recommending, creating, updating, or deleting playlists.
- Combining playlists from multiple channels in one request.
- Multi-page traversal or continuation requests.

## Assumptions

- YT-301 supplies the shared Layer 3 conventions for tool naming, input validation, field provenance, response structure, and safe error presentation.
- A default of 25 records and a maximum of 50 records balance useful channel coverage with readable agent responses.
- The source's supplied ordering is the most transparent default because this feature does not promise a ranking or recommendation rule.
- Only playlists visible to the caller are eligible for return; inaccessible playlists are not inferred or represented as unavailable records.
- A playlist with unavailable optional metadata remains a valid listing result when its stable identifier and title are available.

## Dependencies

- **YT-301**: Provides the shared Layer 3 contract conventions used by this tool.
- **YT-237**: Provides the lower-level playlist-listing capability used to obtain channel-associated playlists.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for channels with accessible playlists return a structured result that identifies the requested channel and includes the expected playlist identifiers and titles in source order.
- **SC-002**: In automated limit testing, 100% of results contain no more than the requested valid limit, and omitted-limit requests contain no more than 25 records.
- **SC-003**: In automated outcome testing, 100% of empty-channel, invalid-input, unavailable-channel, access-restricted, source-limited, and unexpected-failure cases produce their documented distinct result or outcome without sensitive diagnostics.
- **SC-004**: Under normal playlist-source availability, at least 95% of representative valid requests return a structured outcome within 5 seconds.
- **SC-005**: In a task-based review of 10 representative research requests, at least 9 reviewers can identify a playlist to inspect next, or correctly recognize that the channel has no accessible playlists, from one returned result.
