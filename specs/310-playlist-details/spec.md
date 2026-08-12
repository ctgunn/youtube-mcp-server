# Feature Specification: Playlist Details

**Feature Branch**: `310-playlist-details`  
**Created**: 2026-08-12  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level playlist detail tool for MCP clients."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Playlist Details (Priority: P1)

An MCP client provides a playlist identifier and receives a predictable, normalized summary of that publicly available playlist, without having to interpret provider-specific resource layouts.

**Why this priority**: Retrieving details for one known playlist is the feature's core research workflow.

**Independent Test**: Request an accessible playlist with a valid identifier and verify that the result contains the playlist identity plus every available documented public detail in the normalized shape.

**Acceptance Scenarios**:

1. **Given** an accessible public playlist and a valid `playlistId`, **When** a client calls `playlists_getPlaylist`, **Then** it receives a normalized playlist detail result containing the playlist identifier and all available documented public details.
2. **Given** an accessible playlist with no description, thumbnails, or other optional public values, **When** a client requests its details, **Then** it receives a successful result that represents those values as unavailable and does not invent replacements.

---

### User Story 2 - Interpret Playlist Details for Research (Priority: P2)

An MCP client can tell which returned values came from the playlist, which values express the public contract, and whether the result describes the playlist itself rather than the videos it contains.

**Why this priority**: Research agents need enough context to cite and compare playlists accurately without confusing playlist metadata with a playlist-item listing.

**Independent Test**: Inspect discovery metadata and a successful result, and verify that they describe the available playlist identity, ownership attribution, publication context, visual references, item count, provenance, public-content boundary, and the fact that videos are not included.

**Acceptance Scenarios**:

1. **Given** a successful playlist lookup, **When** a client inspects the result, **Then** it can identify the playlist and all available documented public title, description, creator attribution, publication time, thumbnails, privacy visibility, and item count.
2. **Given** a client needs the videos contained in a playlist, **When** it inspects this tool's contract, **Then** it is directed to a playlist-items tool rather than assuming this detail result includes video entries.
3. **Given** public playlist metadata changes after an earlier request, **When** a client makes a later request, **Then** the later result reflects the public playlist state available at that time without claiming that the earlier result remains current.

---

### User Story 3 - Receive Safe Outcomes for Unavailable Playlists (Priority: P3)

An MCP client receives a clear, safe outcome when its request is invalid, the playlist cannot be accessed publicly, access is insufficient, capacity is exhausted, or the source cannot complete the lookup.

**Why this priority**: A research workflow must distinguish a retrievable playlist from a problem it can safely recover from, without exposing non-public playlist information or service diagnostics.

**Independent Test**: Exercise invalid input, an unavailable playlist, authorization-sensitive content, exhausted capacity, and a source failure; verify the documented outcome category and that no private context, credentials, internal traces, or raw source payloads are exposed.

**Acceptance Scenarios**:

1. **Given** a missing, blank, or non-text `playlistId`, **When** a client invokes the tool, **Then** it receives a validation outcome before any lookup is attempted.
2. **Given** a syntactically valid identifier for a playlist that cannot be publicly retrieved, **When** a client invokes the tool, **Then** it receives one unavailable-resource outcome that does not disclose whether the playlist is deleted, private, restricted, or absent.
3. **Given** a lookup cannot complete because of authorization-sensitive access, capacity exhaustion, or a source-service failure, **When** a client invokes the tool, **Then** it receives the matching safe structured outcome and, where useful, recovery guidance without sensitive diagnostics.

### Edge Cases

- A `playlistId` that is missing, non-text, or empty after trimming is rejected before any lookup.
- An accessible playlist with sparse public metadata remains a successful result; unavailable optional values are not fabricated or substituted.
- A playlist whose public metadata changes, including its item count, between requests can produce a different later result; each response represents the public state observed for that request.
- A playlist that is deleted, private, hidden, region-restricted, or otherwise unavailable produces one safe unavailable-resource outcome and reveals no underlying availability reason.
- The detail result describes one playlist only. It does not include playlist items, video details, comments, private creator information, or a historical snapshot.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing validation, handler, and contract tests for the required `playlistId`, successful normalized detail result, sparse metadata, provenance, scope disclosure, and every safe failure outcome.
- **Green**: Implement only the public tool behavior needed to satisfy those tests: single-playlist retrieval, normalized public detail shaping, required metadata, scope guidance, and safe outcome mapping.
- **Refactor**: Consolidate repeated playlist normalization, provenance, validation, and safe-error rules with the shared Layer 3 contracts after focused tests pass; then run the full repository verification suite before review.
- **Required test levels**: unit tests for validation and result normalization; contract tests for discovery metadata, input and result shapes, provenance, and safe errors; and integration-style tests for accessible, sparse, unavailable, authorization-sensitive, capacity, and source-failure flows.
- Every new or changed Python function in scope must have a reStructuredText docstring describing its behavior, inputs, output, public-content boundary, and safe failure behavior.
- **Pull-request evidence**: Show focused tests moving from failing to passing, `python3 -m pytest`, and `python3 -m ruff check .` with successful results. Include evidence for a populated accessible playlist, sparse metadata, an unavailable playlist, and every documented failure category.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `playlists_getPlaylist` that returns normalized details for exactly one playlist.
- **FR-002**: The tool MUST require `playlistId` as one non-empty text identifier, trim surrounding whitespace, and reject missing, blank, or non-text values with a safe validation outcome before lookup begins.
- **FR-003**: The tool MUST accept only the required `playlistId` input and MUST reject unknown input fields so callers can determine the complete supported request shape from discovery metadata.
- **FR-004**: For a successfully retrieved playlist, the tool MUST return `playlistId` and every available documented public value among title, description, creator identifier, creator name, publication time, thumbnails, privacy visibility, and item count.
- **FR-005**: The successful response MUST include a normalized playlist-detail object, the requested `playlistId`, and provenance context that distinguishes source-preserved playlist values from normalized contract values.
- **FR-006**: The tool MUST represent unavailable optional public values as unavailable and MUST NOT fabricate, infer, or substitute playlist metadata.
- **FR-007**: The tool's discovery metadata and caller documentation MUST state the required identifier, result fields, public-content boundary, provenance, possible changes between requests, applicable access and capacity caveats, and caller-visible recovery guidance.
- **FR-008**: The tool's discovery metadata and successful response MUST state that the result describes playlist details only and does not include the playlist's video entries; clients requiring entries MUST be directed to the playlist-items tool.
- **FR-009**: A syntactically valid playlist identifier whose details cannot be retrieved because the playlist is missing, deleted, hidden, private, restricted, or otherwise unavailable MUST produce one unavailable-resource outcome without disclosing the underlying reason.
- **FR-010**: The tool MUST return distinct, safe structured outcomes for invalid parameters, unavailable resources, authorization-sensitive data, capacity exhaustion, and source-service failures. These outcomes MUST exclude credentials, private creator context, internal traces, raw source payloads, and non-public playlist data.
- **FR-011**: The tool MUST preserve each available public playlist value as observed for the request and MUST NOT claim that a result remains current after the request completes.

### Key Entities *(include if feature involves data)*

- **Playlist detail request**: A client request containing one required playlist identifier.
- **Playlist detail**: The normalized public summary of one playlist, including its identity and available descriptive, attribution, timing, visual, visibility, and count information.
- **Provenance context**: Information that tells a client which result values preserve available playlist data and which values describe the normalized public contract.
- **Lookup outcome**: The successful detail result or safe structured outcome returned for a request, including validation, unavailability, authorization-sensitive, capacity, and source-service cases.

## Assumptions

- YT-301 supplies the shared Layer 3 naming, input, response-provenance, composition, and safe-error conventions used by this feature.
- The default detail result is limited to broadly useful public playlist metadata: identity, title, description, creator attribution, publication time, thumbnails, privacy visibility, and item count when available.
- For privacy and security, an unavailable result does not distinguish deleted, private, hidden, restricted, and not-found playlists.
- Playlist-item retrieval, video enrichment, ranking, filtering, historical comparison, and private or owner-only data are outside this slice; playlist-item retrieval belongs to YT-311.
- Changes in publicly available playlist metadata between requests are expected; the tool does not infer omitted values or promise a historical snapshot.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for accessible playlists return a structured result containing the requested playlist identifier and every available documented public detail without fabricated values.
- **SC-002**: In automated contract testing, 100% of successful results and discovery records identify provenance, the public-content boundary, and that playlist video entries are outside this tool's result.
- **SC-003**: In automated outcome testing, 100% of invalid-input, unavailable-resource, authorization-sensitive, capacity-exhaustion, and source-failure cases use their documented safe outcome and expose no private data, credentials, internal traces, or raw source payloads.
- **SC-004**: Under normal source availability, at least 95% of representative single-playlist requests produce their structured outcome within 5 seconds.
- **SC-005**: In a task-based review, at least 90% of participating agent developers can construct a valid request, interpret a returned playlist detail, and identify the separate tool needed for playlist video entries using discovery metadata and one response alone.
