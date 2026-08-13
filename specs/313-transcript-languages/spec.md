# Feature Specification: Transcript Language Discovery

**Feature Branch**: `313-transcript-languages`
**Created**: 2026-08-13
**Status**: Draft
**Input**: User description: "Enable MCP clients to discover the available transcript and caption languages for a YouTube video before requesting a transcript."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover Available Transcript Languages (Priority: P1)

An MCP client identifies the transcript and caption languages it can request for one video before beginning transcript analysis.

**Why this priority**: Language discovery is the core value of the feature. It prevents a client from requesting a transcript blindly or analysing content in an unintended language.

**Independent Test**: Request language availability for a video with accessible caption tracks and verify that the response identifies the video and every accessible language with its availability information.

**Acceptance Scenarios**:

1. **Given** a video with one or more accessible caption tracks, **When** a client requests its available transcript languages using a valid `videoId`, **Then** it receives a structured result that identifies the video and each accessible language.
2. **Given** a video with multiple accessible tracks in the same language, **When** a client requests its available transcript languages, **Then** it receives each track as a distinct available option rather than an ambiguous language-only result.

---

### User Story 2 - Select a Suitable Transcript Track (Priority: P2)

An MCP client uses the discovery result to choose a language and, where supplied, a track identifier for a later transcript request.

**Why this priority**: Track-level context makes the discovery result actionable when a video has variants such as manually created and automatically generated captions.

**Independent Test**: Request language availability for a video with track metadata and verify that every source-provided identifier and caller-relevant track attribute is clearly associated with its language.

**Acceptance Scenarios**:

1. **Given** a caption source exposes a track identifier or track attributes, **When** a client requests available languages, **Then** the result includes those source-provided values with the corresponding language.
2. **Given** a caption source does not expose a track identifier, **When** a client requests available languages, **Then** the result remains usable and explicitly indicates that no identifier is available rather than inventing one.

---

### User Story 3 - Understand Restricted or Missing Access (Priority: P3)

An MCP client can distinguish a video with no accessible transcript languages from one whose caption information is limited by authorization or source availability.

**Why this priority**: Clear access outcomes let clients choose an appropriate recovery action without treating permission restrictions as an absence of captions.

**Independent Test**: Exercise videos with no accessible tracks, restricted access, and unavailable source information; verify that the result or error identifies the applicable safe outcome without exposing sensitive details.

**Acceptance Scenarios**:

1. **Given** a valid video with no accessible caption tracks, **When** a client requests available languages, **Then** it receives a successful empty result that is explicitly identified as having no accessible languages.
2. **Given** caption information is restricted for the caller, **When** a client requests available languages, **Then** it receives an authorization-sensitive outcome that explains the limitation without exposing credentials or protected caption content.
3. **Given** a missing, blank, or invalid `videoId`, **When** a client requests available languages, **Then** it receives a safe validation error before language discovery begins.

### Edge Cases

- A video may have no accessible caption tracks; this is a successful empty discovery result, not a failure.
- Multiple tracks may share one language and must remain individually distinguishable when source metadata permits it.
- A language label may be unavailable or incomplete from the caption source; the result must preserve the available information and must not infer a more specific language.
- Authorization restrictions, unavailable video captions, source unavailability, and invalid input must remain distinguishable caller-visible outcomes.
- Results must not expose caption text, credentials, internal diagnostic traces, or protected details about inaccessible tracks.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing unit and contract tests for required-video validation, accessible-language discovery, distinct same-language tracks, metadata presentation, empty results, and each safe restricted or unavailable outcome.
- **Green**: Add only the behavior required to validate the input, identify accessible tracks, present caller-relevant language and metadata information, and map failure categories safely.
- **Refactor**: Consolidate duplicate language and track-presentation rules into shared behavior where appropriate. Update the project's required function documentation for every changed function, then run the complete repository quality suite.
- **Required test levels**: unit tests for validation and result shaping; contract tests for the public tool inputs and outcomes; integration tests for discovery across representative caption sources; and end-to-end invocation coverage where the hosted test environment is available.
- **Pull-request evidence**: Show the focused tests moving from failing to passing and provide successful complete repository quality-suite results. Include evidence for a video with several languages, duplicate-language tracks, no accessible tracks, restricted access, and invalid input.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a public tool named `transcripts_listLanguages` that reports the accessible transcript and caption language options for exactly one video.
- **FR-002**: The tool MUST require `videoId` as one non-empty text identifier and MUST reject a missing, blank, or non-text value with a safe validation error before discovery begins.
- **FR-003**: For every accessible caption track discovered for the video, the result MUST include its language and a caller-visible availability state.
- **FR-004**: The result MUST preserve each discovered track as a distinct option, including when multiple tracks use the same language.
- **FR-005**: When the caption source provides a track identifier or caller-relevant track metadata, the result MUST include those values with the matching track and identify them as source-provided. When such a value is unavailable, the result MUST not invent a substitute.
- **FR-006**: When no caption tracks are accessible for a valid video, the tool MUST return a successful structured result with an empty language-options collection and a clear no-accessible-languages state.
- **FR-007**: The tool MUST return distinct, safe caller-visible outcomes for invalid input, no accessible languages, authorization-sensitive restrictions, source quota or availability limitations, and unexpected source failures.
- **FR-008**: Authorization-sensitive and source-failure outcomes MUST not expose caption text, credentials, internal traces, raw source payloads, or protected metadata about inaccessible tracks.
- **FR-009**: The tool's discovery information and caller documentation MUST state the required input, the language-option and track-metadata fields, the no-accessible-languages result, and all caller-visible limitation categories.
- **FR-010**: The feature MUST remain limited to language and track discovery; retrieving transcript text or timestamped caption segments is outside its scope.

### Key Entities

- **Language Discovery Request**: A client's request to identify accessible caption language options for one video, identified by `videoId`.
- **Language Option**: One accessible caption track's language, availability state, and source-provided identifier or metadata when available.
- **Language Discovery Result**: The identified video and its language options, or a safe outcome explaining why options could not be presented.

## Assumptions

- YT-301 supplies the shared Layer 3 conventions for tool naming, input validation, field provenance, and safe error presentation.
- Only caption tracks accessible to the caller are reported; the feature does not attempt to infer the existence, language, or metadata of inaccessible tracks.
- Caller-relevant track metadata includes only attributes supplied by the caption source that help distinguish or select a track; it does not add caption text.
- Transcript retrieval and timestamped-caption retrieval are separate feature slices and consume, but are not implemented by, this discovery capability.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for videos with accessible tracks return a structured result that identifies the video and every accessible language option.
- **SC-002**: In automated acceptance testing, 100% of videos with multiple accessible tracks in the same language return separate, distinguishable options for those tracks when source metadata permits distinction.
- **SC-003**: In automated failure-path testing, 100% of invalid-input, no-accessible-languages, authorization-sensitive, source-limitation, and source-failure cases return their documented distinct safe outcome without exposing protected information.
- **SC-004**: Under normal source availability, at least 95% of representative language-discovery requests return their structured outcome within 5 seconds.
- **SC-005**: In a task-based review, at least 90% of participating agent developers can choose an available language option or identify the appropriate next action for a no-accessible-languages or restricted-access result from the tool information and response alone.
