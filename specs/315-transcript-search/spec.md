# Feature Specification: Layer 3 Transcript Search

**Feature Branch**: `315-transcript-search`  
**Created**: 2026-08-13  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level transcript text search tool."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Find Relevant Transcript Moments (Priority: P1)

An MCP client searches a video's available transcript for a phrase and receives the matching moments with enough surrounding text and timing information to assess their relevance and navigate to them.

**Why this priority**: Finding evidence within a long video is the feature's core research value.

**Independent Test**: Provide a video with a known transcript and a query that occurs in several segments; verify that the returned matches contain the expected snippets and timestamps in chronological order.

**Acceptance Scenarios**:

1. **Given** a video has an available transcript containing the requested phrase, **When** a client supplies its `videoId` and `query`, **Then** it receives one result for every matching transcript segment up to the requested limit, with a contextual snippet and start and end timestamps.
2. **Given** a phrase occurs in multiple transcript segments, **When** a client searches for it, **Then** the results are ordered from the earliest matching moment to the latest.
3. **Given** a query differs from transcript text only by letter case, **When** a client searches for it, **Then** the same matches are returned as for the equivalent casing in the transcript.

---

### User Story 2 - Search a Requested Language (Priority: P2)

An MCP client restricts the search to a requested transcript language so that research results match the language needed by the workflow.

**Why this priority**: Multilingual videos may have materially different captions, and a client needs control when a language is known.

**Independent Test**: Provide a video with transcripts in two languages, search with an explicit language, and verify that only the selected language's transcript supplies results.

**Acceptance Scenarios**:

1. **Given** a requested transcript language is available for the video, **When** a client supplies `language`, **Then** all returned snippets and timestamps come from that language's transcript.
2. **Given** the requested transcript language is unavailable, **When** a client searches the video, **Then** it receives a clear failure that identifies transcript availability as the reason and does not substitute a different language.

---

### User Story 3 - Handle Empty and Bounded Searches (Priority: P3)

An MCP client receives a clear, structured outcome when a search yields no text matches and can limit a broad query to the number of results it can use.

**Why this priority**: Predictable empty results and limits let agents continue a research workflow without treating ordinary conditions as failures.

**Independent Test**: Search a known transcript with an absent phrase and with a common phrase plus a result limit; verify the empty outcome and result count respectively.

**Acceptance Scenarios**:

1. **Given** a transcript is available but contains no matching segment, **When** a client searches it, **Then** it receives a successful response with an empty match collection and the searched video and language context.
2. **Given** more segments match than the client requests, **When** it supplies `maxMatches`, **Then** the response contains no more matches than that limit while retaining chronological order.
3. **Given** a client supplies a blank or invalid query, **When** it starts a search, **Then** it receives a clear validation failure before any transcript search is performed.

### Edge Cases

- A video has no accessible transcript, captions are restricted, or transcript retrieval fails: the client receives a clear, safe failure that distinguishes unavailable transcript content from an empty search result.
- A requested `language` is unavailable: the search does not silently fall back to another language.
- The query spans two separate transcript segments: it produces no match unless the phrase occurs wholly within one segment; no synthetic cross-segment snippet is created.
- A matching segment begins at the start or ends at the end of a transcript: its snippet includes all available surrounding text without requiring unavailable context.
- A common query produces more matches than `maxMatches`: only the earliest matches through the requested limit are returned.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and contract tests for required inputs, optional language and `maxMatches`, case-insensitive matching, chronological ordering, timestamped snippets, empty results, and each unavailable or invalid-input outcome. Add an integration test using controlled transcript retrieval to prove the complete composite journey.
- **Green**: Implement only the search behavior and result contract needed for those tests, using the existing transcript-retrieval capability as its source of transcript content.
- **Refactor**: Consolidate shared transcript-search validation and result-shaping behavior without changing the documented contract; run the full repository test suite after the focused tests pass.
- Required test levels: unit tests for query, matching, ranking, and result-limit rules; contract tests for the public request and result shape; integration tests for retrieval followed by search; and an end-to-end invocation test where the project test environment supports it.
- Every new or changed Python function in scope will receive or update a reStructuredText docstring that states its behavior, inputs, return value, and relevant failure conditions.
- Pull-request evidence must include the focused test results, the applicable contract and integration results, and a passing full-suite run using the repository's documented test command.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide `transcripts_searchTranscript`, a higher-level tool that retrieves an accessible transcript for a specified video and searches its text within the same request.
- **FR-002**: The tool MUST require a non-empty `videoId` and a non-empty `query`, and it MUST reject requests that omit either value or provide a query consisting only of whitespace.
- **FR-003**: The tool MUST accept optional `language` and `maxMatches` inputs. `language` selects only that transcript language; `maxMatches` limits the returned matches to an integer from 1 through 50, defaulting to 10 when omitted.
- **FR-004**: When `language` is omitted, the tool MUST search the video's default accessible transcript and identify the selected language in the response.
- **FR-005**: The system MUST perform a case-insensitive literal text search within each transcript segment. A phrase that crosses segment boundaries MUST not be reported as a match.
- **FR-006**: For each match, the system MUST return the matching text, a human-readable contextual snippet from the matching segment, and the segment's start and end timestamps in seconds.
- **FR-007**: The system MUST rank results chronologically by segment start timestamp, with earlier matches returned before later matches; it MUST apply `maxMatches` after that ordering.
- **FR-008**: When no segment matches a valid query in an accessible transcript, the system MUST return a successful response with an empty match collection and the searched video and language context.
- **FR-009**: When no accessible transcript exists, the requested language is unavailable, or transcript access is denied, the system MUST return a clear, safe failure describing the availability or access condition and MUST NOT present it as an empty match collection.
- **FR-010**: The response MUST make clear that match snippets and timestamps are derived from retrieved transcript segments and may reflect the timing and text available in the source captions.

### Key Entities *(include if feature involves data)*

- **Transcript Search Request**: A request identifying one video, the required search phrase, and optional language and result-limit preferences.
- **Transcript Segment**: A time-bounded portion of an accessible transcript, with text, start timestamp, end timestamp, and language context.
- **Transcript Match**: A matching transcript segment returned to the client, including matched text, a contextual snippet, and segment timestamps.
- **Search Result Collection**: The ordered matches and the video and selected-language context for a completed search.

## Scope

### In Scope

- Searching one accessible video's transcript text by phrase.
- Optional language selection and bounded match results.
- Timestamped, contextual snippets and documented chronological ordering.
- Clear differentiation between no matches and unavailable or inaccessible transcripts.

### Out of Scope

- Searching across multiple videos, channels, or playlists in one request.
- Creating, editing, translating, or publishing transcripts or captions.
- Semantic, fuzzy, synonym, or relevance-based search.
- Combining text across transcript segment boundaries.

## Assumptions

- The existing transcript-retrieval capability can provide accessible, time-bounded transcript segments for a video.
- Case-insensitive literal phrase matching and chronological ordering are the most predictable defaults for research workflows.
- When no language is supplied, the transcript source's default accessible language is suitable; callers that require a particular language will supply it explicitly.
- A default of 10 matches and an upper limit of 50 balance useful coverage with readable agent responses.

## Dependencies

- **YT-301**: Provides the shared Layer 3 transcript capability on which this composite search experience depends.
- **YT-304**: Provides transcript retrieval needed to obtain the searchable caption content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a representative set of 20 videos with accessible transcripts and known phrases, clients receive the expected matching transcript moments, snippets, and timestamps for at least 19 videos.
- **SC-002**: For representative transcripts containing up to 10,000 segments, 95% of valid searches return their ordered results within 3 seconds after the transcript is available for searching.
- **SC-003**: In contract testing, 100% of responses distinguish an empty match collection from a transcript-unavailable, language-unavailable, or access-denied outcome.
- **SC-004**: In a usability review of 10 representative research queries, at least 9 reviewers can identify the relevant video moment from the returned snippet and timestamps without opening unrelated transcript text.
