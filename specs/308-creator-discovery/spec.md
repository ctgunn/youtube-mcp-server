# Feature Specification: Creator Discovery

**Feature Branch**: `308-creator-discovery`

**Created**: 2026-08-12

**Status**: Draft

**Input**: User description: "Define and implement the higher-level creator-discovery tool `channels_findCreators`."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover Creators from Relevant Videos (Priority: P1)

An MCP client searches for a topic and receives a stable, distinct collection of public channels derived from videos that match the topic.

**Why this priority**: Finding the channels behind relevant videos is the core creator-research workflow and provides value without any optional refinement.

**Independent Test**: Submit a valid topic query against a controlled set of matching videos; verify that each successful result represents one distinct channel, identifies the matched-video basis for its inclusion, and that no-match queries return an empty collection.

**Acceptance Scenarios**:

1. **Given** a non-empty topic query and matching public videos from more than one channel, **When** the client invokes creator discovery without optional refinements, **Then** it receives up to 10 distinct candidate channels in base video-search relevance order.
2. **Given** a valid query and a supported video ordering or publication window, **When** the client invokes creator discovery, **Then** every returned candidate derives from a video that satisfies the selected base-search constraints.
3. **Given** a valid query with no matching public videos, **When** the client invokes creator discovery, **Then** it receives a successful empty collection with the applied search context.

---

### User Story 2 - Refine Creators by Audience and Activity (Priority: P2)

An MCP client narrows creator candidates by public subscriber count, most recent public upload, or creator-like classification without treating unavailable data as a match.

**Why this priority**: Research workflows need to identify creators at an appropriate audience scale and with recent activity without manually joining channel data.

**Independent Test**: Run discovery against controlled candidates using each refinement independently and in combination; verify that every returned channel meets all selected criteria and that candidates missing required data are disclosed rather than guessed.

**Acceptance Scenarios**:

1. **Given** a valid query and an inclusive subscriber range, **When** the client invokes creator discovery, **Then** every returned channel has an available public subscriber count within that range.
2. **Given** a valid query and an inclusive latest-upload window, **When** the client invokes creator discovery, **Then** every returned channel has an available public latest-upload timestamp within that window.
3. **Given** a valid query and `creatorOnly=true`, **When** the client invokes creator discovery, **Then** every returned channel is classified as creator-like and the response identifies that classification as a heuristic rather than a verified identity.

---

### User Story 3 - Prioritize and Inspect Creator Candidates (Priority: P3)

An MCP client selects a documented ranking mode and requests a bounded number of matching-video samples per returned channel to judge candidate relevance.

**Why this priority**: Ranking and samples let the same discovery query support different research goals while giving the client evidence for each channel's topical fit.

**Independent Test**: Run discovery against controlled eligible candidates for each ranking mode and sample limit; verify the documented order, stable ties, sample count, and sample relevance to the base query.

**Acceptance Scenarios**:

1. **Given** eligible creator candidates and `sortBy=subscribers_asc` or `sortBy=subscribers_desc`, **When** the client invokes discovery, **Then** results are ordered by available public subscriber count in the requested direction.
2. **Given** eligible creator candidates and `sortBy=indie_priority` or `sortBy=recent_activity`, **When** the client invokes discovery, **Then** results follow the documented creator-size or public-activity ranking rule.
3. **Given** a request for two sample videos per channel, **When** a returned channel has three or more matching videos, **Then** its result includes exactly the first two matching videos in base video-search order.

### Edge Cases

- A missing query, a query blank after trimming, an unknown input field, a result limit outside 1–50, a sample limit outside 0–10, an unsupported ordering or ranking value, or a value of the wrong type produces a safe validation error before candidate discovery begins.
- A minimum subscriber value greater than the maximum, a video publication start later than its end, or a latest-upload start later than its end produces a safe validation error before candidates are evaluated.
- Timestamp boundaries are inclusive and must be valid ISO 8601 timestamps with `Z` or an explicit numeric timezone offset.
- Duplicate matching videos from one channel yield one candidate channel. The earliest matching video in base-search order establishes that channel's base position and is the first possible sample.
- A candidate with hidden, unavailable, or failed enrichment is retained only when neither an active filter nor the selected ranking requires that value. Otherwise it is excluded and counted in safe partial-enrichment information.
- If no candidate can be evaluated for a requested refinement or non-relevance ranking because required enrichment is unavailable, the tool returns a safe partial-enrichment outcome rather than unfiltered substitute results.
- A valid query that yields no qualifying candidates after filtering is a successful empty collection, distinct from invalid input, authorization-sensitive data, quota exhaustion, and source failure.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing behavioral and contract tests for query validation, defaults, video publication constraints, candidate derivation and de-duplication, each refinement, all five ranking modes, deterministic ties, sample limits and ordering, result provenance, empty collections, partial enrichment, and safe failures.
- **Green**: Add only the validation, matched-video discovery, distinct-channel derivation, conditional enrichment, filter-before-rank processing, bounded sample selection, result shaping, and safe outcome mapping needed to satisfy those tests.
- **Refactor**: Consolidate reusable creator classification, channel filtering, ranking, and provenance rules with the shared Layer 3 conventions after focused tests pass. Keep creator-discovery responsibilities cohesive and run the complete repository test suite after refactoring.
- **Required test levels**: unit tests for validation, candidate derivation, filtering, ranking, sampling, and result shaping; contract tests for tool discovery and result/error shapes; integration tests for the composed video-discovery and channel-enrichment workflow; and end-to-end invocation coverage where the hosted MCP verification path is available.
- Every new or changed Python function in scope must have a reStructuredText docstring that describes its behavior, inputs, returned values, and safe failure behavior.
- **Pull-request evidence**: Show focused tests moving from failing to passing, `python3 -m pytest`, and `python3 -m ruff check .` completing successfully. Include evidence for all ranking modes, every refinement, distinct-channel derivation, zero and nonzero sample limits, an empty collection, unavailable required enrichment, and invalid ranges.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `channels_findCreators` that discovers publicly visible creator candidates from videos matching a required `query` text value.
- **FR-002**: The tool MUST require `query` to be non-empty text after trimming, reject unknown input fields, and accept only these optional inputs: `maxResults`, `order`, `videoPublishedAfter`, `videoPublishedBefore`, `channelMinSubscribers`, `channelMaxSubscribers`, `channelLastUploadAfter`, `channelLastUploadBefore`, `creatorOnly`, `sortBy`, and `sampleVideosPerChannel`.
- **FR-003**: The tool MUST default `maxResults` to 10, accept only whole-number values from 1 through 50 inclusive, and return no more than `maxResults` final channel candidates after all selected refinement rules are applied.
- **FR-004**: The tool MUST accept `order` values `date`, `rating`, `relevance`, `title`, and `viewCount` for base video-search ordering. When omitted, base relevance ordering applies.
- **FR-005**: The tool MUST apply `videoPublishedAfter` and `videoPublishedBefore` as inclusive base video-search constraints, accept only valid ISO 8601 timestamps with an explicit timezone, and reject a supplied start boundary later than its end boundary.
- **FR-006**: The tool MUST derive candidate channels from the public owning-channel identity attached to videos matching the query and selected base constraints. It MUST normalize the result to one distinct public channel per stable identifier and preserve each channel's earliest base video-search position for deterministic ordering.
- **FR-007**: The tool MUST apply `channelMinSubscribers` and `channelMaxSubscribers` as inclusive, non-negative whole-number bounds on available public subscriber counts. It MUST reject a supplied minimum greater than its paired maximum and MUST not invent a hidden or unavailable count.
- **FR-008**: The tool MUST apply `channelLastUploadAfter` and `channelLastUploadBefore` as inclusive bounds on an available public latest-upload timestamp. It MUST reject a supplied start boundary later than its end boundary and MUST not use a matched video as a substitute for unavailable latest-upload information.
- **FR-009**: When `creatorOnly=true`, the tool MUST retain only channels classified as creator-like by the shared documented public-signal heuristic. The response MUST identify the classification and supporting signals as inferred, potentially incomplete, and not a verified claim about the channel owner, organizational status, or independence. The default is `false`.
- **FR-010**: The tool MUST support `sortBy` values `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, and `recent_activity`, defaulting to `relevance`. `relevance` preserves base video-search order after filtering; subscriber modes order eligible channels by available subscriber count in the selected direction; `indie_priority` places creator-like channels ahead of non-creator-like channels and then prefers smaller available subscriber counts; and `recent_activity` orders eligible channels by most recent available public latest-upload timestamp.
- **FR-011**: The tool MUST apply all selected refinements before final ranking and cap the final collection at `maxResults`. For non-relevance rankings, candidates without the value required by the selected ranking rule MUST be excluded; every ranking tie MUST preserve base video-search order.
- **FR-012**: The tool MUST default `sampleVideosPerChannel` to 0, accept only whole-number values from 0 through 10 inclusive, and include no samples when the value is 0. For each returned channel, a positive value MUST include up to that number of its query-matching videos in base video-search order, with each sample identifying its stable video identifier, title, publication timestamp when available, and the channel association.
- **FR-013**: The tool MUST conditionally obtain public channel information when a selected filter or ranking needs subscriber count, latest-upload activity, or creator classification. It MUST use available public information only and MUST not use owner, credential, private, hidden, or inferred substitute data to satisfy a filter or ranking rule.
- **FR-014**: Each returned candidate MUST include its stable channel identifier, title, available public description and thumbnails, available normalized metadata, available public statistics, the matched-video basis for candidate derivation, applicable heuristic information, and field-provenance information distinguishing source-preserved, normalized, and heuristic-inferred values.
- **FR-015**: A successful response MUST identify applied inputs, returned candidate count, any available continuation information, and a safe partial-enrichment summary whenever candidates were excluded because information required by a selected filter or ranking was unavailable. The summary MUST state aggregate counts and safe reason categories without exposing credentials, internal traces, or raw source payloads.
- **FR-016**: Tool discovery metadata and caller documentation MUST state that `channels_findCreators` is a composite higher-level workflow rather than a single-resource passthrough, and describe its matched-video discovery, candidate derivation, conditional enrichment, filtering, de-duplication, ranking, sample inclusion, access, quota, and partial-result semantics.
- **FR-017**: A valid query with no matching or qualifying candidates MUST return a successful empty collection. Invalid input, unavailable or authorization-sensitive data, quota exhaustion, source-service failure, and partial-enrichment failure MUST produce distinct safe structured outcomes without stack traces, credentials, private owner context, raw source payloads, or unfiltered substitute results.

### Key Entities

- **Creator Discovery Request**: The caller's topic query, optional base video constraints, channel refinements, ranking choice, result limit, and per-channel sample limit.
- **Matched Video**: A public video satisfying the topic query and selected base constraints, carrying the public owning-channel identity and base-search position used for candidate derivation.
- **Creator Candidate**: One distinct publicly discoverable channel derived from one or more matched videos, including its stable identifier, matched-video basis, base position, and available enrichment.
- **Channel Enrichment**: Available public subscriber, latest-upload, and creator-classification information used to evaluate active filters or rankings, with provenance and availability status.
- **Video Sample**: A bounded, query-matching video associated with a returned candidate and presented in base video-search order as evidence of topical relevance.
- **Creator Discovery Result Collection**: The ordered, bounded set of qualifying candidates together with applied inputs, continuation information, provenance, sample videos, and optional partial-enrichment summary.
- **Partial Enrichment Summary**: A safe aggregate explanation of candidates excluded because information required for a selected refinement or ranking was unavailable.

## Assumptions

- YT-301 provides shared Layer 3 conventions for parameter validation, field provenance, creator-like heuristic disclosure, composition, and safe structured errors; YT-305 and YT-307 provide the normalized public channel and channel-search behavior this workflow builds on.
- The feature is limited to public creator discovery. It does not provide private, deleted, hidden, region-restricted, owner-only, or otherwise authorization-sensitive information.
- `maxResults` caps final returned candidates and `sampleVideosPerChannel` caps per-candidate evidence; neither guarantees that a restrictive query will produce that many items.
- Public subscriber counts, latest-upload activity, and creator-classification signals can be absent or unavailable. The tool excludes a candidate when an active rule requires unavailable information rather than treating it as a match.
- `creatorOnly` and `indie_priority` use the shared creator-like public-signal heuristic; neither verifies a channel owner's identity, organizational status, or independence.
- This feature discovers channels through matching videos. Direct channel search, single- or batch-channel detail lookup, channel video or playlist listing, and channel statistics are separate feature slices.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid query-only requests return a structured collection containing no more than the requested number of distinct candidate channels, or a documented safe structured outcome when public search data is unavailable.
- **SC-002**: Across representative candidate sets, 100% of returned candidates derive from at least one matching video and satisfy every selected video-publication, subscriber, latest-upload, and creator-only refinement; 100% of candidates missing information required by an active refinement or non-relevance ranking are excluded and disclosed safely.
- **SC-003**: Across representative candidate sets, all five `sortBy` modes produce their specified order, repeated discovery over the same source data preserves the same tie order, and every returned candidate includes no more than its requested number of query-matching video samples in base order.
- **SC-004**: In automated contract testing, 100% of successful results identify applied inputs, candidate count, candidate derivation basis, field provenance, sample inclusion, and any applicable partial-enrichment information; 100% of safe failure outcomes exclude credentials, private owner information, internal traces, and raw source payloads.
- **SC-005**: Under normal public-source availability, at least 95% of representative creator-discovery requests return a complete, safely partial, or empty structured result within 5 seconds.
- **SC-006**: In a task-based review, at least 90% of participating agent developers can construct a valid query-only creator-discovery request, choose an appropriate refinement, ranking, or sample limit, and determine the basis and limitations of a returned candidate from the tool description and response alone.
