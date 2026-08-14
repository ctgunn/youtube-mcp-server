# Feature Specification: Channel Statistics

**Feature Branch**: `317-channels-get-statistics`  
**Created**: 2026-08-14  
**Status**: Draft  
**Input**: User description: "Define and implement the Layer 3 channels_getStatistics tool so MCP clients can retrieve available subscriber, video, and view counts for a channel in a normalized agent-ready result, with clear treatment of hidden or unavailable counts."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Available Channel Statistics (Priority: P1)

An MCP client requests statistics for one known channel and receives a concise, normalized result containing its available public subscriber, video, and view counts without interpreting source-specific layouts.

**Why this priority**: A focused statistics view lets research agents assess a channel's reach and publishing activity in one reliable lookup.

**Independent Test**: Invoke `channels_getStatistics` with a channel that exposes public statistics and verify that the result identifies that channel and includes every available documented metric with a consistent availability state.

**Acceptance Scenarios**:

1. **Given** an available channel with public statistics, **When** a client supplies its `channelId`, **Then** it receives a normalized statistics result for that same channel containing its available subscriber, video, and view counts.
2. **Given** a channel whose source provides an additional documented public count, **When** a client requests its statistics, **Then** the result includes that count only when its metric name, source value, availability state, and caller-facing meaning are documented.

---

### User Story 2 - Understand Hidden or Unavailable Counts (Priority: P2)

An MCP client can distinguish a hidden or unavailable statistic from a reported count, so it does not mistake missing information for zero activity or audience size.

**Why this priority**: Channel research and reporting can be misleading if hidden subscriber counts or missing statistics are silently converted to zero or estimated.

**Independent Test**: Invoke the tool against representative channels with one or more hidden or unavailable counts and verify that the result identifies the state for each expected metric and contains no fabricated numeric value.

**Acceptance Scenarios**:

1. **Given** a retrievable channel for which a documented count is not exposed, **When** a client requests its statistics, **Then** the result marks that metric as hidden or unavailable and does not return zero, an estimate, or a substitute value.
2. **Given** a retrievable channel with a count of zero, **When** a client requests its statistics, **Then** the result reports zero as an available count rather than treating it as missing.

---

### User Story 3 - Receive Actionable Lookup Outcomes (Priority: P3)

An MCP client receives a clear, safe outcome when its channel identifier is invalid, the channel cannot be retrieved, or the statistics lookup cannot be completed.

**Why this priority**: Agents need to distinguish invalid input, unavailable channels, access conditions, and temporary source limitations before deciding how to continue.

**Independent Test**: Exercise invalid identifiers, unavailable channels, and representative access, quota, and source-service failures; verify that each outcome is categorized safely and exposes no sensitive details.

**Acceptance Scenarios**:

1. **Given** a missing, blank, or non-text `channelId`, **When** a client requests statistics, **Then** it receives a corrective validation failure before a lookup is attempted.
2. **Given** a syntactically valid identifier for a channel that is unavailable to the requester, **When** a client requests statistics, **Then** it receives an unavailable-resource outcome rather than a successful result with empty or zero counts.
3. **Given** a lookup cannot complete because of authorization, quota, or a source-service failure, **When** a client requests statistics, **Then** it receives the matching safe outcome and, where useful, recovery guidance without credentials, internal traces, or raw source payloads.

### Edge Cases

- A `channelId` that is missing, blank after trimming, or not text is rejected before statistics are requested.
- A requested channel with an available count of zero preserves zero as a reported value.
- A requested channel with a hidden subscriber count or sparse public statistics returns a successful result with each non-reported metric explicitly identified rather than silently omitted or inferred.
- A channel that is deleted, suspended, restricted, or not found produces one safe unavailable-resource outcome without disclosing the underlying availability reason.
- A failure to retrieve the channel is distinct from a retrieved channel that has hidden or unavailable statistics.
- The result does not claim that metrics not exposed by the source are available.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and contract tests for discovery metadata, required identifier validation, normalized available-count results, zero-count handling, hidden or unavailable metric states, unavailable-channel handling, and authorization, quota, and source-service failures.
- **Green**: Implement only the validation, single-channel statistics retrieval, metric normalization, availability-state representation, and safe outcome mapping needed for those tests to pass.
- **Refactor**: Consolidate repeated channel-statistics validation and normalization rules only after focused tests pass, preserve the shared Layer 3 public contract, and run the full repository suite after changes.
- **Required test levels**: Unit tests for validation, count and availability-state shaping, and failure classification; contract tests for MCP-facing discovery metadata and result/error shapes; and integration tests using the controlled lower-layer boundary for successful, hidden, unavailable, and failed retrieval outcomes.
- **Documentation**: Add or update reStructuredText docstrings for every new or changed Python function in scope, covering its purpose, inputs, normalized outcome, availability semantics, and safe error behavior.
- **Review evidence**: The pull request must include focused test command results, `python3 -m pytest`, and `python3 -m ruff check .`, with each command completing successfully.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a higher-level MCP tool named `channels_getStatistics` for retrieving statistics for exactly one YouTube channel.
- **FR-002**: The tool MUST require one non-blank text `channelId` and reject a missing, blank, or non-text identifier with a safe validation failure before attempting retrieval.
- **FR-003**: For a retrievable channel, the tool MUST return a normalized result that preserves the requested `channelId` and identifies the result as channel statistics.
- **FR-004**: The result contract MUST define the expected public count metrics as subscriber count, video count, and view count, and MUST return each metric when it is available for the requested channel.
- **FR-005**: For each expected metric, the result MUST distinguish an available reported count from a hidden or unavailable count. An available count of zero MUST remain distinguishable from a hidden or unavailable count.
- **FR-006**: The tool MUST omit the numeric value for a hidden or unavailable metric and MUST NOT replace it with zero, an estimate, a derived value, or a value from another channel.
- **FR-007**: When the source makes another public count available, the tool MAY include it only when its metric name, value, availability state, and caller-facing meaning are documented in the public contract; undocumented source fields MUST NOT be exposed as raw result structure.
- **FR-008**: The tool MUST use stable, concise, agent-oriented field names and structure, and MUST identify reported counts as source-provided values and availability states as normalized result information. This tool does not return heuristic or inferred statistics.
- **FR-009**: The tool MUST return a safe unavailable-resource outcome for a syntactically valid `channelId` whose channel is missing, suspended, restricted, or otherwise unavailable, without disclosing the underlying reason.
- **FR-010**: The tool MUST return distinct safe outcomes for invalid input, unavailable resources, authorization-sensitive access, quota exhaustion, and source-service failures; those outcomes MUST exclude credentials, internal traces, signed links, raw source payloads, and raw media content.
- **FR-011**: The tool's discovery metadata and caller documentation MUST state the required input, expected metrics, representation of available, zero, hidden, and unavailable counts, and caller-visible failure categories.
- **FR-012**: The tool MUST provide a normalized single-resource retrieval result and MUST NOT combine statistics from multiple channels or derive audience, engagement, trend, comparison, or forecast metrics that are not supplied by the source.

### Key Entities

- **Channel Statistics Request**: A client request containing the required `channelId` for exactly one channel.
- **Channel Statistics Result**: The normalized response tied to the requested channel, including the expected metrics and their availability states.
- **Statistic Metric**: A named public count, such as subscribers, videos, or views, represented either as an available reported count or as hidden or unavailable without a numeric value.
- **Lookup Outcome**: The successful statistics result or a safe failure category for validation, unavailable resources, authorization-sensitive access, quota exhaustion, or source-service failure.

## Scope

### In Scope

- Retrieving source-provided public subscriber, video, and view counts for one channel.
- Normalizing those metrics for agent consumption while preserving zero and making hidden or unavailable values explicit.
- Required channel identification, safe caller-visible outcomes, and clear discovery documentation.

### Out of Scope

- Retrieving channel metadata beyond the identity needed to associate the statistics with the requested channel.
- Retrieving audience demographics, watch time, revenue, retention, private creator analytics, or data for multiple channels in one request.
- Calculating engagement rates, historical changes, rankings, comparisons, forecasts, or estimates.
- Updating channel statistics or other channel data.

## Assumptions

- YT-301 supplies the shared Layer 3 conventions for tool naming, `channelId`, field provenance, response structure, and safe error presentation.
- The tool retrieves source-provided statistics for one channel only; it does not calculate derived analytics.
- Publicly available source counts are preserved as reported so clients do not mistake formatting or conversion for a newly measured value.
- Hidden, absent, and unavailable counts are treated consistently as non-reported metrics for caller interpretation; the tool does not attempt to determine why a specific metric was not exposed.

## Dependencies

- **YT-301**: Provides the shared Layer 3 contract conventions used by this tool.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for representative retrievable channels return a normalized result associated with the requested channel and include every available expected metric.
- **SC-002**: In automated acceptance testing, 100% of representative zero, hidden, and unavailable metric cases are distinguishable from one another, and no hidden or unavailable metric is represented with a fabricated numeric value.
- **SC-003**: In validation and failure-path testing, 100% of missing, blank, non-text, unavailable-resource, authorization-sensitive, quota, and source-service cases return their documented safe outcome and do not return a successful statistics result.
- **SC-004**: Under normal source availability, at least 95% of representative valid requests produce their structured statistics outcome within 3 seconds.
- **SC-005**: In a task-based review with five representative MCP research tasks, at least four reviewers can identify the requested channel, determine which counts are reported versus unavailable, and avoid treating unavailable counts as zero using the tool description and result alone.
