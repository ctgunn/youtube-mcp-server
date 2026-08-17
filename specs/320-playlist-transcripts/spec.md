# Feature Specification: Playlist Video Transcript Aggregation

**Feature Branch**: `320-playlist-transcripts`  
**Created**: 2026-08-17  
**Status**: Draft  
**Input**: User description: "Define and implement the Layer 3 `playlists_getVideoTranscripts` tool for retrieving transcript data for videos contained in a playlist."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve a Playlist's Available Transcripts (Priority: P1)

An MCP client requests the transcripts for the videos in a playlist so it can analyse the playlist's spoken content without manually looking up each video.

**Why this priority**: Retrieving the usable transcript data for a playlist is the feature's core value.

**Independent Test**: Request transcripts for a playlist containing videos with accessible captions and verify that the result identifies the playlist, identifies every video considered, and returns the available transcript content with its timestamps.

**Acceptance Scenarios**:

1. **Given** a valid playlist containing videos with accessible transcripts, **When** a client requests `playlists_getVideoTranscripts`, **Then** it receives a structured result with one outcome for every video considered and the available transcript content for each accessible video.
2. **Given** a playlist with more videos than the request's processing limit, **When** a client requests its transcripts, **Then** the result processes only the allowed number of videos and clearly states that additional videos were not attempted.

---

### User Story 2 - Request a Preferred Transcript Language (Priority: P2)

An MCP client requests playlist transcripts in a preferred language to keep downstream analysis consistent.

**Why this priority**: A predictable language-selection flow prevents an agent from analysing a transcript in an unintended language.

**Independent Test**: Request a playlist with a language preference and verify that each attempted video follows the documented preference order and reports the language actually returned.

**Acceptance Scenarios**:

1. **Given** an attempted video has an accessible transcript in the requested language, **When** the client supplies `language`, **Then** that video's returned transcript identifies and uses the requested language.
2. **Given** an attempted video has no accessible transcript in the requested language, **When** the client supplies `language`, **Then** that video has a transcript-unavailable outcome and the tool does not silently substitute another language.

---

### User Story 3 - Understand Incomplete Caption Access (Priority: P3)

An MCP client can distinguish videos with accessible transcripts from videos that are unavailable, restricted, or unable to be retrieved while preserving successful results for the other videos.

**Why this priority**: Playlist contents frequently have mixed caption availability; clear per-video outcomes let clients continue useful research and decide what follow-up is appropriate.

**Independent Test**: Request a playlist containing accessible, captionless, and access-restricted videos; verify that successful transcripts remain available and each other video has a safe, distinct status.

**Acceptance Scenarios**:

1. **Given** a valid playlist has a mixture of accessible and inaccessible video transcripts, **When** a client requests playlist transcripts, **Then** it receives available transcripts and a per-video status for each inaccessible video rather than losing the successful results.
2. **Given** caption access is restricted for an attempted video, **When** a client requests playlist transcripts, **Then** the result identifies the limitation without revealing credentials, protected caption content, or internal diagnostics.
3. **Given** a missing, blank, or invalid `playlistId`, **When** a client requests playlist transcripts, **Then** it receives a safe validation error before any playlist or transcript retrieval begins.

### Edge Cases

- A valid playlist has no video items; return a successful, explicitly empty result with no transcript attempts.
- A playlist is private, unavailable, or inaccessible to the caller; return a safe playlist-access outcome and do not imply that it has no transcripts.
- A playlist item does not resolve to a video that can be processed; report that item's safe unavailable status and continue with other eligible items.
- An attempted video has no transcript, captions are restricted, a requested language is unavailable, or the transcript source is temporarily unavailable; report the applicable per-video status without discarding other results.
- `maxResults` is missing, non-numeric, fractional, zero, negative, or greater than 50; apply the documented default only when omitted and otherwise reject invalid values before processing.
- Caption text, credentials, protected metadata, and internal diagnostic traces must never be exposed for inaccessible transcripts.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing unit and contract tests for required playlist validation; the default and bounds for `maxResults`; language selection; normalized transcript segments; bounded processing; empty playlists; and every documented partial, restricted, and unavailable outcome.
- **Green**: Add only the behavior necessary to enumerate the permitted playlist items, obtain each eligible transcript, return the documented normalized result, and preserve per-video outcomes when individual retrievals cannot succeed.
- **Refactor**: Consolidate shared playlist enumeration, language-selection, transcript result, and safe-error rules where appropriate. Add or update reStructuredText docstrings for every changed Python function, then run the complete repository quality suite.
- **Required test levels**: unit tests for validation, limits, language handling, result shaping, and failure mapping; contract tests for public inputs and result fields; integration tests for representative playlist and transcript access; and end-to-end invocation coverage where the hosted test environment is available.
- **Pull-request evidence**: Show focused tests moving from failing to passing and successful `python3 -m pytest` and `ruff check .` results. Include evidence for accessible transcripts, an empty playlist, a bounded playlist, a missing requested language, mixed access, and invalid input.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a public tool named `playlists_getVideoTranscripts` that returns transcript outcomes for videos contained in one playlist.
- **FR-002**: The tool MUST require `playlistId` as one non-empty text identifier and MUST reject a missing, blank, or non-text value with a safe validation error before processing begins.
- **FR-003**: The tool MUST accept an optional `language` preference. For each attempted video, it MUST use the requested language when an accessible matching transcript exists; when no matching transcript is accessible, it MUST report a transcript-unavailable outcome for that video and MUST NOT silently substitute another language.
- **FR-004**: When `language` is omitted, the tool MUST follow the shared transcript language-selection order: the configured transcript-language preference, then English. The result for every returned transcript MUST identify the language actually provided.
- **FR-005**: The tool MUST accept an optional integer `maxResults` from 1 through 50. When it is omitted, the tool MUST process at most 10 playlist items; when supplied, it MUST process at most the requested number of playlist items and make no more transcript attempts than that number.
- **FR-006**: The result MUST identify the requested playlist and include an outcome for every playlist item considered, including the video identifier when available, the transcript availability status, the returned language when applicable, and timestamped transcript segments when accessible.
- **FR-007**: The result MUST include a fan-out summary stating the item limit, number of playlist items considered, number of transcript attempts, counts by outcome, and whether any additional playlist items were not attempted because of the limit.
- **FR-008**: The tool MUST be documented as a composite playlist-enumeration and transcript-retrieval workflow, rather than as a direct single-resource lookup. Its public documentation MUST state its inputs, default and maximum processing bounds, per-video outcome meanings, language behavior, and fan-out summary.
- **FR-009**: If some attempted videos lack accessible transcripts or cannot be retrieved, the tool MUST preserve successful transcript results and return a safe per-video outcome for each unsuccessful attempt.
- **FR-010**: The tool MUST distinguish, in a safe caller-visible manner, invalid input, inaccessible or unavailable playlists, empty playlists, unavailable requested languages, unavailable transcripts, authorization-sensitive caption restrictions, source limits or temporary unavailability, and unexpected failures.
- **FR-011**: Authorization-sensitive and failure outcomes MUST NOT expose credentials, protected caption text, protected metadata, raw source payloads, or internal diagnostic traces.
- **FR-012**: The feature MUST limit its work to the bounded set of playlist items selected for a request. It MUST not continue through later playlist items after the limit is reached.

### Key Entities

- **Playlist Transcript Request**: A client's request to retrieve transcript outcomes for videos in one playlist, including an optional language preference and processing limit.
- **Playlist Video Outcome**: The result for one playlist item considered by the request, including its video identifier where available, transcript availability status, returned language, transcript segments when accessible, or a safe limitation reason.
- **Transcript Segment**: A timestamped portion of accessible transcript text, represented by its start time, duration, and text.
- **Fan-out Summary**: A request-level account of the processing bound, videos considered, transcript attempts, outcome counts, and any unattempted items.

## Scope

### In Scope

- Retrieving accessible transcript data for a bounded number of videos in one playlist.
- Applying an optional language preference and reporting the language actually returned.
- Returning per-video partial results and safe access limitations alongside a request-level fan-out summary.

### Out of Scope

- Generating, translating, editing, or publishing transcripts or captions.
- Processing an entire playlist beyond the configured per-request bound.
- Inferring or revealing the existence or content of inaccessible captions.
- Searching, ranking, or filtering playlist items by transcript text.

## Assumptions

- YT-301 provides shared Layer 3 conventions for tool naming, input validation, field provenance, safe error presentation, and common parameter meanings.
- YT-311 provides normalized playlist-item enumeration, and YT-304 provides the shared transcript retrieval and language-selection behavior used for each attempted video.
- `maxResults` limits both the number of playlist items considered and the maximum number of transcript retrieval attempts, with a default of 10 and a maximum of 50.
- A valid request may return mixed per-video outcomes; unavailable or restricted captions for one video do not invalidate accessible results for other attempted videos.
- Pagination beyond the request bound is intentionally excluded so callers can make an explicit follow-up request if more playlist items need processing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for playlists with accessible transcripts return a structured outcome for every item within the requested processing bound.
- **SC-002**: In automated acceptance testing, 100% of requests with an explicit language return only matching-language transcripts or the documented per-video unavailable-language outcome; no other language is substituted silently.
- **SC-003**: In automated acceptance testing, 100% of requests honor the selected `maxResults` bound, with no more than the allowed number of playlist items considered or transcript attempts made.
- **SC-004**: In automated mixed-access testing, 100% of accessible transcripts remain available when one or more other attempted videos have unavailable, restricted, or temporarily inaccessible transcripts.
- **SC-005**: Under normal source availability, at least 95% of representative requests processing 10 or fewer videos return their structured outcome within 15 seconds.
- **SC-006**: In a task-based review, at least 90% of participating agent developers can identify the processed limit, successful transcripts, and appropriate next action for each unavailable or restricted video from the response and tool documentation alone.
