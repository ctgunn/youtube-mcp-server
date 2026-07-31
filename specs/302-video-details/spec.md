# Feature Specification: Video Details

**Feature Branch**: `302-video-details`  
**Created**: 2026-07-30  
**Status**: Draft  
**Input**: User description: "Define the higher-level video detail tool that lets MCP clients retrieve normalized information for one YouTube video using a required video identifier and optional requested parts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve a Video's Core Details (Priority: P1)

An MCP client requests one video by its identifier and receives a predictable, normalized set of core details that it can use without interpreting source-specific field layouts.

**Why this priority**: A dependable single-video result is the primary value of the feature and supports research workflows even when no optional detail groups are requested.

**Independent Test**: Submit a valid identifier for an available video without optional parts and verify that the normalized core video shape is returned.

**Acceptance Scenarios**:

1. **Given** an available video and a valid `videoId`, **When** a client requests video details without `parts`, **Then** it receives the default normalized video fields defined in this specification.
2. **Given** a client requests a video, **When** the video has no value for an optional core field such as description, tags, or a thumbnail size, **Then** the response represents that field as unavailable without inventing a value or failing the complete request.

---

### User Story 2 - Request Additional Detail Groups (Priority: P2)

An MCP client asks for one or more supported detail groups when its workflow needs statistics, publication status, topic information, or the underlying metadata groups beyond the default shape.

**Why this priority**: Part selection lets clients obtain relevant extra context while keeping the default response predictable and focused.

**Independent Test**: Request an available video with each supported `parts` value individually and with multiple unique values, then verify that the corresponding documented fields are present in addition to the default shape.

**Acceptance Scenarios**:

1. **Given** an available video, **When** a client requests `parts` containing `statistics`, **Then** the response includes the normalized statistics group and the default normalized video fields.
2. **Given** an available video, **When** a client requests multiple supported, unique parts, **Then** the response includes the mapped fields for every requested part and no unrelated optional group is implied.
3. **Given** a client provides an unsupported, duplicated, or non-text `parts` value, **When** it requests video details, **Then** the request is rejected with a safe validation error that identifies the invalid parameter.

---

### User Story 3 - Understand Unavailable and Failed Lookups (Priority: P3)

An MCP client receives clear, safe outcomes when the supplied identifier is invalid, the video cannot be retrieved, or the service cannot complete a lookup because of access, quota, or source-service failure.

**Why this priority**: Predictable failures let clients recover or inform their users without revealing sensitive information about unavailable videos.

**Independent Test**: Exercise missing, blank, and wrongly typed identifiers; identifiers for unavailable videos; quota/access failures; and source-service failures. Verify that each outcome has the documented category and safe remediation guidance.

**Acceptance Scenarios**:

1. **Given** a missing, blank, or non-text `videoId`, **When** a client requests video details, **Then** it receives a validation error and no lookup is attempted.
2. **Given** a syntactically valid identifier whose video is deleted, private, restricted, or not found, **When** a client requests video details, **Then** it receives one unavailable-resource outcome that does not disclose which condition applies.
3. **Given** a lookup cannot be completed because of quota, authorization, or a source-service failure, **When** a client requests video details, **Then** it receives the matching safe failure category and, where useful, retry or authorization guidance without credentials, internal traces, or raw source payloads.

### Edge Cases

- A request with a valid identifier for a video that has sparse metadata returns the default shape with only genuinely available values; it does not fabricate missing details.
- A requested optional group may be unavailable for an otherwise retrievable video; the result identifies that group's unavailable fields without converting it into a successful value.
- An empty `parts` list is treated the same as omitting `parts` and returns only the default normalized shape.
- A request that includes a valid identifier plus any unsupported or repeated part is rejected as invalid rather than silently ignoring the problematic value.
- Source-service access limits and quota exhaustion remain distinguishable from an unavailable video, while their details remain safe for callers.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing behavioral and contract tests for a valid default response, each supported part mapping, invalid part selection, unavailable-video handling, and quota, access, and source-service failure categories.
- **Green**: Add only the behavior needed for those tests: single-video lookup, default normalization, documented optional-group selection, and safe error mapping.
- **Refactor**: Consolidate repeated normalization and validation rules after the focused tests pass; preserve the shared public-tool contract and run the complete repository verification before review.
- Required test levels are unit tests for validation and field mapping, contract tests for caller-visible metadata and result shape, and integration-style tests for successful and failed lookup outcomes.
- Every new or changed Python function in scope must have a reStructuredText docstring describing its behavior, inputs, output, and safe failure behavior.
- Pull-request evidence must include the focused test results plus `python3 -m pytest` and `python3 -m ruff check .`, both completing successfully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose the public tool name `videos_getVideo` for retrieving normalized details for exactly one YouTube video.
- **FR-002**: The tool MUST require `videoId` as one non-empty text identifier for the requested video and MUST reject a missing, blank, or non-text identifier with a safe validation error.
- **FR-003**: The tool MUST return the default normalized video shape for every successful request, whether or not `parts` is supplied.
- **FR-004**: The default normalized video shape MUST document and, when available, return `videoId`, `title`, `description`, `publishedAt`, `channelId`, `channelTitle`, `duration`, `categoryId`, `tags`, and `thumbnails`.
- **FR-005**: The tool MUST accept `parts` only as an optional list of unique values from `snippet`, `contentDetails`, `statistics`, `status`, and `topicDetails`; an omitted or empty list MUST select no optional group.
- **FR-006**: The response contract MUST map each supported requested part to its returned fields: `snippet` adds `liveBroadcastContent`, `defaultLanguage`, and `defaultAudioLanguage`; `contentDetails` adds `dimension`, `definition`, `caption`, `licensedContent`, `regionRestriction`, and `projection`; `statistics` adds `viewCount`, `likeCount`, `favoriteCount`, and `commentCount`; `status` adds `uploadStatus`, `privacyStatus`, `license`, `embeddable`, `publicStatsViewable`, `madeForKids`, and `selfDeclaredMadeForKids`; and `topicDetails` adds `topicCategories`.
- **FR-007**: When a client requests one or more valid parts, the tool MUST include the documented fields for each requested group in addition to the default normalized shape, and MUST not claim unavailable data as present.
- **FR-008**: The tool MUST reject unsupported, duplicate, or incorrectly typed `parts` values with a safe validation error that names `parts` and states the accepted values.
- **FR-009**: The tool MUST classify a syntactically valid identifier that cannot be returned because the video is missing, deleted, private, restricted, or otherwise unavailable as an unavailable-resource outcome without revealing the underlying availability reason.
- **FR-010**: The tool MUST return distinct safe outcomes for validation failures, unavailable resources, authorization-required access, quota exhaustion, and source-service failures; those outcomes MUST exclude credentials, internal traces, signed links, and raw media content.
- **FR-011**: The tool's discovery metadata and caller documentation MUST state the required identifier, allowed `parts` values, default result fields, optional-group mappings, and the caller-visible error categories.
- **FR-012**: The tool MUST preserve source values where available and identify a missing requested field or optional group as unavailable rather than deriving or guessing a substitute.

### Key Entities *(include if feature involves data)*

- **Video request**: A client request containing one required video identifier and, optionally, a unique selection of supported detail groups.
- **Normalized video detail**: The stable core video result returned for a successful request, with available metadata reshaped for consistent client use.
- **Optional detail group**: A caller-selected group of additional video details: `snippet`, `contentDetails`, `statistics`, `status`, or `topicDetails`.
- **Lookup outcome**: The successful result or safe failure category returned for a video request, including validation, unavailability, access, quota, and source-service outcomes.

## Assumptions

- The feature relies on the existing shared public-tool conventions and the existing single-video retrieval capability established by YT-301.
- The default result is intentionally limited to common research metadata; optional detail groups are additive and do not remove default fields.
- For privacy and security, an unavailable result does not distinguish deleted, private, restricted, and not-found videos.
- Counts and other source-provided values retain their supplied representation so clients do not mistake formatting changes for new measurements.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In contract testing, 100% of successful requests without `parts` return every available default normalized field and no optional detail group.
- **SC-002**: In contract testing, 100% of successful requests for each supported part return the documented mapping for that part while retaining the default normalized shape.
- **SC-003**: In validation testing, 100% of requests with missing, blank, non-text, unsupported, duplicated, or wrongly typed inputs are rejected before a video result is returned.
- **SC-004**: In failure-path testing, 100% of unavailable, access, quota, and source-service cases use their documented safe outcome category and expose no credentials, internal traces, signed links, or raw media content.
- **SC-005**: A client developer can determine the required input, default response fields, optional-part mappings, and recovery action for every documented failure category from discovery metadata and tool documentation alone.
