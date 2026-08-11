# Feature Specification: Transcript Retrieval

**Feature Branch**: `304-transcripts-get-transcript`  
**Created**: 2026-08-11  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level transcript retrieval tool."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve a Video Transcript (Priority: P1)

An MCP client requests the accessible transcript for one YouTube video and receives the transcript text in a stable, agent-friendly result.

**Why this priority**: Retrieving a transcript is the feature's core research value; it lets a client analyze a video without processing the video itself.

**Independent Test**: Request an accessible video with a valid identifier and verify that the result identifies the video and resolved language and contains its available transcript text.

**Acceptance Scenarios**:

1. **Given** a video with an accessible transcript and a valid `videoId`, **When** the client requests a transcript without a language, **Then** it receives the transcript text in the resolved default language and the response identifies that language.
2. **Given** a video with an accessible transcript in the requested language, **When** the client supplies that `language`, **Then** it receives the transcript text for that language and the response identifies the selected caption track when one is available.
3. **Given** a valid video whose accessible transcript has no text, **When** the client requests it, **Then** it receives a successful empty-text result that identifies the transcript as empty rather than unavailable.

---

### User Story 2 - Control Transcript Language (Priority: P2)

An MCP client can request a transcript in a specific language and can predict which language the tool will use when no language is supplied.

**Why this priority**: Research workflows need reproducible language selection and must not silently analyze a different language than intended.

**Independent Test**: Exercise requests with an explicit language, without one when a configured default exists, and without either; verify that the resolved language follows the documented priority in every case.

**Acceptance Scenarios**:

1. **Given** an explicit valid `language` and an accessible matching track, **When** the client requests a transcript, **Then** the explicit language takes precedence over every default.
2. **Given** no explicit `language` and a configured `YOUTUBE_TRANSCRIPT_LANG` default with an accessible matching track, **When** the client requests a transcript, **Then** the configured default is selected.
3. **Given** no explicit `language` and no configured transcript-language default, **When** the client requests a transcript for a video with an accessible English track, **Then** English (`en`) is selected.

---

### User Story 3 - Understand Unavailable Caption Access (Priority: P3)

An MCP client receives a clear, safe outcome when the requested transcript cannot be obtained because no matching track exists, caption access is not authorized, or the source cannot complete the request.

**Why this priority**: Caption access is permission-sensitive. Clear failure categories prevent clients from mistaking a permission failure for a video with no transcript.

**Independent Test**: Exercise invalid input, missing matching language, no accessible tracks, denied caption access, quota exhaustion, and source-service failure; verify that each produces its documented safe outcome with no transcript substitute.

**Acceptance Scenarios**:

1. **Given** a valid video with no accessible transcript in the resolved language, **When** the client requests it, **Then** it receives a transcript-unavailable outcome that identifies the resolved language and does not return another-language content.
2. **Given** a valid video with a transcript that the caller is not authorized to access, **When** the client requests it, **Then** it receives an authorization-sensitive outcome without credentials, internal traces, or caption content.
3. **Given** an invalid, missing, blank, or non-text `videoId` or `language`, **When** the client requests a transcript, **Then** it receives a safe validation error before transcript retrieval is attempted.

### Edge Cases

- A language value is normalized only for harmless casing and surrounding whitespace; an empty value after trimming, malformed language tag, or unsupported input type is rejected.
- The tool selects exactly one language using this priority: explicit `language`, then `YOUTUBE_TRANSCRIPT_LANG`, then `en`. It does not silently try other languages after the resolved language has no accessible track.
- A video can have caption tracks but none accessible to the caller. That is an authorization-sensitive outcome, distinct from no track in the resolved language.
- Multiple accessible tracks for the resolved language are selected deterministically; the result identifies the chosen track where the source makes that identity available.
- A transcript with no textual content is a successful empty-text result, distinct from an unavailable transcript.
- Quota exhaustion, temporary source failure, and authorization-sensitive access are distinct safe outcomes. None may expose caption content, credentials, internal traces, or raw source payloads.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and contract tests for required-video validation, accepted language values, the complete language-selection order, successful text shaping, empty-text results, deterministic same-language track selection, and every safe failure category. Add integration tests using controlled caption-discovery and transcript-retrieval results to prove the complete composed flow.
- **Green**: Implement only the validation, language resolution, authorized caption selection, transcript retrieval, result shaping, and safe error mapping needed for the focused tests to pass.
- **Refactor**: Consolidate shared transcript language-selection and safe caption-access behavior where future transcript tools can reuse it. Update reStructuredText docstrings for every new or changed Python function, covering parameters, returned values, errors, and caller-visible behavior. Run the full repository test suite after refactoring.
- **Required test levels**: unit tests for validation, language resolution, track selection, response shaping, and error mapping; contract tests for MCP-facing discovery and result/error contracts; integration tests for the composed caption workflow; end-to-end invocation coverage where the hosted MCP test harness is available.
- **Pull-request evidence**: Show focused tests moving from failing to passing, `python3 -m pytest`, and `python3 -m ruff check .` with successful results. Include evidence for all three language-selection sources and for unavailable, authorization-sensitive, quota, and source-failure outcomes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `transcripts_getTranscript` that retrieves the accessible transcript for exactly one YouTube video.
- **FR-002**: The tool MUST require `videoId` as one non-empty text identifier and MUST reject a missing, blank, or non-text value with a safe validation error before retrieval is attempted.
- **FR-003**: The tool MUST accept `language` only as an optional, non-empty language tag. It MUST reject malformed or non-text language values with a safe validation error that identifies `language`.
- **FR-004**: The tool MUST resolve transcript language in this order: the explicit `language` request value, then the `YOUTUBE_TRANSCRIPT_LANG` configured default, then `en`. The response MUST identify both the resolved language and which of these three sources selected it.
- **FR-005**: When an accessible track exists in the resolved language, the tool MUST retrieve and return its transcript text. It MUST not substitute text from another language unless that language was itself the resolved language.
- **FR-006**: A successful response MUST include `videoId`, `language`, `languageSource`, `text`, and an availability status. When available from the authorized caption source, it MUST also include `captionTrackId`; all values must be identified as source-provided or normalized according to the shared Layer 3 field-provenance convention.
- **FR-007**: When multiple accessible tracks match the resolved language, the tool MUST use a documented deterministic selection rule and identify the selected track when its identity is available. It MUST not combine separate tracks into one result.
- **FR-008**: The tool MUST return a successful empty-text result when the selected accessible transcript contains no text. The result MUST remain distinguishable from a transcript-unavailable outcome.
- **FR-009**: The tool MUST return a transcript-unavailable outcome when no accessible track exists in the resolved language. That outcome MUST identify the resolved language and MUST not return a transcript in a different language.
- **FR-010**: The tool MUST use the official caption-access path and MUST document that access requires eligible authorization for the target caption track. It MUST return an authorization-sensitive outcome when that authorization is absent or insufficient; it MUST not present public transcript fallback content as an official caption result.
- **FR-011**: The tool MUST return distinct, safe structured outcomes for validation failure, transcript unavailability, authorization-sensitive access, quota exhaustion, and source-service failure. These outcomes MUST exclude caption text where it was not retrieved, credentials, internal traces, raw source payloads, and any sensitive authorization details.
- **FR-012**: The tool's discovery metadata and caller documentation MUST state the required and optional inputs, language-selection order, response fields and provenance, official-caption access limitation, and caller-visible failure categories.

### Key Entities

- **Transcript Request**: A client's video identifier and optional requested language.
- **Resolved Language**: The single language selected from the explicit request, configured default, or English fallback, together with the source of that selection.
- **Caption Track**: An accessible, language-matching transcript source for the requested video, with an identifier when available.
- **Transcript Result**: The successful transcript text or a safe structured outcome that identifies availability and any applicable failure category.

## Assumptions

- YT-301 provides the shared Layer 3 naming, parameter, field-provenance, and safe-error conventions referenced by this tool.
- This feature covers only the official authorized-caption route. It does not introduce a public or third-party transcript fallback; any future fallback must be separately specified and clearly identified as non-official.
- The configured `YOUTUBE_TRANSCRIPT_LANG` value, when present, is a valid language tag. Invalid configuration is treated as a safe configuration outcome rather than silently using a different configured language.
- Timestamped segment retrieval is intentionally outside this feature's primary output; it is covered by the separate timestamped-captions tool slice. This tool returns complete transcript text and does not invent timing data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests with an accessible matching track return a structured transcript result containing the required identity, resolved-language, language-source, availability, and text fields.
- **SC-002**: In automated language-selection testing, 100% of requests use the explicit language when supplied; otherwise use the configured default when present; otherwise use `en`, with the selected source correctly reported.
- **SC-003**: In automated failure-path testing, 100% of invalid-input, unavailable-transcript, authorization-sensitive, quota, and source-failure cases return their documented distinct safe outcome and expose no caption content, credentials, internal traces, or raw source payloads when retrieval fails.
- **SC-004**: Under normal authorized source availability, at least 95% of representative transcript requests produce their structured outcome within 8 seconds.
- **SC-005**: In a task-based review, at least 90% of participating agent developers can determine the required input, language-selection order, response fields, and recovery action for an unavailable or authorization-sensitive result from the tool description and response alone.
