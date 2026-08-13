# Feature Specification: Video Statistics

**Feature Branch**: `312-video-statistics`  
**Created**: 2026-08-13  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level video statistics tool."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Available Video Statistics (Priority: P1)

An MCP client requests statistics for one known video and receives a concise, normalized result containing its available public counts, without needing to interpret source-specific response layouts.

**Why this priority**: A focused view of a video's engagement and view counts is the feature's core research value.

**Independent Test**: Invoke `videos_getStatistics` with the identifier of a video that exposes public statistics and verify that the response identifies the video and returns every available documented metric with a consistent availability state.

**Acceptance Scenarios**:

1. **Given** an available video with public statistics, **When** a client supplies its `videoId`, **Then** the client receives a normalized statistics result for that same video containing its available view, like, comment, and favorite counts.
2. **Given** an available video whose source provides an additional documented public count, **When** a client requests its statistics, **Then** the result includes that count only when it can identify the metric, source value, and availability state consistently with the documented contract.

---

### User Story 2 - Understand Hidden or Unavailable Counts (Priority: P2)

An MCP client can distinguish an absent, hidden, or unavailable statistic from a reported count, so it does not mistake missing information for zero engagement.

**Why this priority**: Research and reporting workflows can make incorrect conclusions if omitted counts are silently converted to zero or otherwise guessed.

**Independent Test**: Invoke the tool against representative videos with one or more missing, hidden, or unavailable counts and verify that the result identifies the state for each expected metric and contains no fabricated numeric value.

**Acceptance Scenarios**:

1. **Given** a retrievable video for which a documented count is not exposed, **When** a client requests statistics, **Then** the result marks that metric as hidden or unavailable and does not return zero, an estimate, or a substitute value.
2. **Given** a retrievable video with a count of zero, **When** a client requests statistics, **Then** the result reports zero as an available count rather than treating it as missing.

---

### User Story 3 - Receive Actionable Lookup Outcomes (Priority: P3)

An MCP client receives a clear, safe outcome when its video identifier is invalid, the video cannot be retrieved, or the statistics lookup cannot be completed.

**Why this priority**: Distinguishing input, availability, permission, quota, and source failures lets a client recover without mistaking a failed request for an empty statistics result.

**Independent Test**: Exercise invalid identifiers, unavailable videos, and representative access, quota, and source-service failures; verify that each outcome is categorized safely and exposes no sensitive details.

**Acceptance Scenarios**:

1. **Given** a missing, blank, or non-text `videoId`, **When** a client requests statistics, **Then** it receives a corrective validation failure before a lookup is attempted.
2. **Given** a syntactically valid identifier for a video that is unavailable to the requester, **When** a client requests statistics, **Then** it receives an unavailable-resource outcome rather than a successful result with empty or zero counts.
3. **Given** a lookup cannot complete because of authorization, quota, or a source-service failure, **When** a client requests statistics, **Then** it receives the matching safe outcome and, where useful, recovery guidance without credentials, internal traces, or raw source payloads.

### Edge Cases

- A `videoId` that is missing, blank after trimming, or not text is rejected before statistics are requested.
- A requested video with an available count of zero preserves zero as a reported value.
- A requested video with sparse or hidden public statistics returns a successful result for the video, with each unavailable metric explicitly identified instead of silently omitted or inferred.
- A video that is deleted, private, restricted, or not found produces one safe unavailable-resource outcome without disclosing the underlying availability reason.
- A failure to retrieve the video is distinct from a retrieved video that has no available statistics.
- The result does not claim that metrics not exposed by the source, including dislike counts, are available.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and contract tests for discovery metadata, required identifier validation, normalized available-count results, zero-count handling, hidden or unavailable metric states, unavailable-video handling, and authorization, quota, and source-service failures.
- **Green**: Implement only the validation, single-video statistics retrieval, metric normalization, availability-state representation, and safe outcome mapping needed for those tests to pass.
- **Refactor**: Consolidate repeated video-statistics validation and normalization rules only after focused tests pass, preserve the shared Layer 3 public contract, and run the full repository suite after changes.
- **Required test levels**: Unit tests for validation, count and availability-state shaping, and failure classification; contract tests for MCP-facing discovery metadata and result/error shapes; and integration tests using the controlled lower-layer boundary for successful, hidden, unavailable, and failed retrieval outcomes.
- **Documentation**: Add or update reStructuredText docstrings for every new or changed Python function in scope, covering its purpose, inputs, normalized outcome, availability semantics, and safe error behavior.
- **Review evidence**: The pull request must include focused test command results, `python3 -m pytest`, and `python3 -m ruff check .`, with each command completing successfully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a higher-level MCP tool named `videos_getStatistics` for retrieving statistics for exactly one YouTube video.
- **FR-002**: The tool MUST require one non-blank text `videoId` and reject a missing, blank, or non-text identifier with a safe validation failure before attempting retrieval.
- **FR-003**: For a retrievable video, the tool MUST return a normalized result that preserves the requested `videoId` and identifies the result as video statistics.
- **FR-004**: The result contract MUST define the expected public count metrics as view count, like count, comment count, and favorite count, and MUST return each metric when it is available for the requested video.
- **FR-005**: For each expected metric, the result MUST distinguish an available reported count from a hidden or unavailable count. An available count of zero MUST remain distinguishable from a hidden or unavailable count.
- **FR-006**: The tool MUST omit the numeric value for a hidden or unavailable metric and MUST NOT replace it with zero, an estimate, a derived value, or a value from another video.
- **FR-007**: When the source makes another public count available, the tool MAY include it only when its metric name, value, availability state, and caller-facing meaning are documented in the public contract; undocumented source fields MUST NOT be exposed as raw result structure.
- **FR-008**: The tool MUST use stable, concise, agent-oriented field names and structure, and MUST identify the provenance of reported counts as source-provided values and of availability states as normalized result information.
- **FR-009**: The tool MUST return a safe unavailable-resource outcome for a syntactically valid `videoId` whose video is missing, deleted, private, restricted, or otherwise unavailable, without disclosing the underlying reason.
- **FR-010**: The tool MUST return distinct safe outcomes for invalid input, unavailable resources, authorization-sensitive access, quota exhaustion, and source-service failures; those outcomes MUST exclude credentials, internal traces, signed links, raw source payloads, and raw media content.
- **FR-011**: The tool's discovery metadata and caller documentation MUST state the required input, expected metrics, representation of available, zero, hidden, and unavailable counts, and caller-visible failure categories.
- **FR-012**: The tool MUST provide a normalized single-resource retrieval result and MUST NOT combine statistics from multiple videos or derive engagement metrics that are not supplied by the source.

### Key Entities

- **Video statistics request**: A client request containing the required `videoId` for exactly one video.
- **Video statistics result**: The normalized response tied to the requested video, including the expected metrics and their availability states.
- **Statistic metric**: A named public count, such as views, likes, comments, or favorites, represented either as an available reported count or as hidden or unavailable without a numeric value.
- **Lookup outcome**: The successful statistics result or a safe failure category for validation, unavailable resources, authorization-sensitive access, quota exhaustion, or source-service failure.

### Assumptions

- This slice depends on YT-301 for shared Layer 3 naming, `videoId`, field-provenance, and safe error conventions.
- The tool retrieves source-provided statistics for one video only; it does not calculate rates, trends, comparisons, or other derived analytics.
- Publicly available source counts are preserved as reported so clients do not mistake formatting or conversion for a newly measured value.
- Hidden, absent, and unavailable counts are treated consistently as non-reported metrics for caller interpretation; the tool does not attempt to determine why a specific metric was not exposed.

### Out of Scope

- Retrieving video metadata beyond the identity needed to associate the statistics with the requested video.
- Retrieving comments, comment content, audience demographics, watch time, revenue, retention, or private creator analytics.
- Calculating engagement rates, historical changes, rankings, comparisons, forecasts, or estimates.
- Updating video statistics or other video data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for representative retrievable videos return a normalized result associated with the requested video and include every available expected metric.
- **SC-002**: In automated acceptance testing, 100% of representative zero, hidden, and unavailable metric cases are distinguishable from one another, and no hidden or unavailable metric is represented with a fabricated numeric value.
- **SC-003**: In validation and failure-path testing, 100% of missing, blank, non-text, unavailable-resource, authorization-sensitive, quota, and source-service cases return their documented safe outcome and do not return a successful statistics result.
- **SC-004**: Under normal source availability, at least 95% of representative valid requests produce their structured statistics outcome within 3 seconds.
- **SC-005**: In a task-based review with five representative MCP research tasks, at least four reviewers can identify the requested video, determine which counts are reported versus unavailable, and avoid treating unavailable counts as zero using the tool description and result alone.
