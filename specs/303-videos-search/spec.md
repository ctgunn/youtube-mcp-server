# Feature Specification: Video Search with Channel Refinement

**Feature Branch**: `[303-videos-search]`  
**Created**: 2026-08-09  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level video search tool with channel-aware enrichment and ranking/filtering behavior."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search for Relevant Videos (Priority: P1)

An MCP client searches for publicly discoverable videos using a text query and, when useful, narrows the search by publication period, channel, base ordering, or result count. The client receives a stable, agent-friendly collection of matching videos.

**Why this priority**: A reliable query-only search is the minimum useful research workflow and remains valuable without any channel refinement.

**Independent Test**: Invoke `videos_searchVideos` with a valid query and verify that the returned collection contains no more than the requested result count, each item has the documented core video identity and metadata, and an unmatched query returns an empty collection rather than an error.

**Acceptance Scenarios**:

1. **Given** a valid non-empty query, **When** the client searches without optional filters, **Then** it receives up to the default number of video results in base relevance order.
2. **Given** a valid query and a valid publication window or channel identifier, **When** the client searches, **Then** every returned video satisfies the supplied base-search constraint.
3. **Given** a valid query that has no matches, **When** the client searches, **Then** it receives a successful empty result collection with the applied search context.

---

### User Story 2 - Find Videos from Suitable Channels (Priority: P2)

An MCP client refines video search results using the matched channel's subscriber range, most-recent upload date, or creator classification, and can request one result per channel.

**Why this priority**: Channel-aware filtering lets research workflows distinguish independent creators, active channels, and channels of a suitable scale without manually joining separate search results.

**Independent Test**: Invoke the tool against representative candidates with known channel metadata and verify that every result meets each selected channel-level filter and that `uniqueChannels=true` returns no repeated channel identifier.

**Acceptance Scenarios**:

1. **Given** a valid query and an inclusive subscriber range, **When** the client searches, **Then** every returned result's enriched channel has a subscriber count within that range.
2. **Given** a valid query and an inclusive latest-upload date window, **When** the client searches, **Then** every returned result's enriched channel has a latest upload date within that window.
3. **Given** a valid query and `creatorOnly=true`, **When** the client searches, **Then** every returned result is classified as creator-like and that classification is identified as inferred rather than raw source data.
4. **Given** a valid query and `uniqueChannels=true`, **When** several eligible videos belong to the same channel, **Then** the response contains at most one video for that channel.

---

### User Story 3 - Rank Results for a Research Goal (Priority: P3)

An MCP client selects a documented ranking mode to prioritize relevant videos, smaller or larger channels, independent creators, or recently active channels.

**Why this priority**: Ranking makes the same search useful for different research questions without requiring the client to reconstruct channel comparisons itself.

**Independent Test**: Invoke the tool with a controlled set of eligible candidates for each `sortBy` value and verify the documented order, including deterministic tie handling.

**Acceptance Scenarios**:

1. **Given** eligible enriched results and `sortBy=subscribers_asc` or `sortBy=subscribers_desc`, **When** the client searches, **Then** results are ordered by qualifying channel subscriber count in the requested direction.
2. **Given** eligible enriched results and `sortBy=indie_priority` or `sortBy=recent_activity`, **When** the client searches, **Then** results follow the documented creator-size or latest-activity ranking rule.
3. **Given** `sortBy=relevance`, **When** the client searches, **Then** the tool preserves the base-search order after applying filters and any requested one-result-per-channel rule.

### Edge Cases

- A query that is blank after trimming, a result count outside 1–50, an unsupported `order` or `sortBy`, a negative subscriber limit, or an unknown input field produces a safe validation error that identifies the invalid field without exposing internal details.
- A supplied lower subscriber bound greater than its upper bound, or an "after" timestamp later than its paired "before" timestamp, produces a safe validation error before any search is performed.
- Publication and latest-upload boundary timestamps are inclusive. Date/time inputs must be valid ISO 8601 timestamps with an explicit offset or `Z` timezone designator.
- A channel with hidden, unavailable, or failed-to-retrieve metadata is retained only when no selected filter or ranking requires that unavailable metadata; such a result identifies channel enrichment as unavailable. If a selected filter or ranking requires the unavailable metadata, that candidate is excluded and the response discloses partial enrichment.
- If base search succeeds but every candidate requiring enrichment cannot be evaluated, the response reports a safe partial-enrichment outcome rather than returning unfiltered candidates as if they satisfied the request.
- If `uniqueChannels=true`, the tool filters and ranks eligible candidates before retaining the first candidate per channel; ties preserve base-search order. Results from candidates without a channel identifier are not returned because they cannot satisfy the requested uniqueness rule.
- Empty results after filtering are a successful empty collection, distinct from invalid input, authorization-sensitive data, quota exhaustion, and upstream failure.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing unit and contract tests for the public input boundary, default values, valid and invalid date/range combinations, each filter, each ranking mode, one-result-per-channel behavior, field provenance, empty results, and safe error/partial-enrichment outcomes. Add integration tests with controlled base-search and channel-metadata responses to prove the composed workflow.
- **Green**: Implement only the validation, candidate enrichment, filtering, ordering, result shaping, and error mapping needed for those tests to pass; preserve the bounded result count and documented response fields.
- **Refactor**: Consolidate reusable channel-filtering and ranking behavior into the shared Layer 3 conventions where it is used by more than this tool. Keep video-family responsibilities cohesive, update reStructuredText docstrings for every new or changed Python function (including parameters, returned values, errors, and externally visible behavior), and run the full repository suite after refactoring.
- **Required test levels**: unit tests for validation, filter, ranking, de-duplication, and response shaping; contract tests for the MCP-facing tool descriptor and result/error contract; integration tests for the composed video-search and channel-enrichment flow; end-to-end invocation coverage where the hosted MCP test harness is available.
- **Pull-request evidence**: show the failing-to-passing focused tests, `pytest`, and `ruff check .` with successful results; include representative evidence for all five `sortBy` values, partial enrichment, and `uniqueChannels=true`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `videos_searchVideos` that accepts a required `query` text value and rejects blank queries after trimming.
- **FR-002**: The tool MUST accept only the following optional inputs: `maxResults`, `order`, `publishedAfter`, `publishedBefore`, `channelId`, `uniqueChannels`, `channelMinSubscribers`, `channelMaxSubscribers`, `channelLastUploadAfter`, `channelLastUploadBefore`, `creatorOnly`, and `sortBy`.
- **FR-003**: The tool MUST default `maxResults` to 10 and accept integer values from 1 through 50 inclusive. It MUST return no more than `maxResults` items after all selected refinement rules are applied.
- **FR-004**: The tool MUST accept `order` values `date`, `rating`, `relevance`, `title`, and `viewCount` and use the selected value for base-search ordering. When omitted, base-search relevance ordering applies.
- **FR-005**: The tool MUST apply `publishedAfter`, `publishedBefore`, and `channelId` as base video-search constraints. It MUST apply publication-date boundaries inclusively and validate that a supplied start boundary is not later than its end boundary.
- **FR-006**: When a subscriber filter is supplied, the tool MUST enrich each candidate with its channel metadata and retain only candidates whose available subscriber count is within the inclusive selected bounds. It MUST reject a minimum subscriber value greater than the maximum.
- **FR-007**: When a latest-upload filter is supplied, the tool MUST enrich each candidate with its channel metadata and retain only candidates whose available latest upload timestamp is within the inclusive selected bounds. It MUST reject an "after" value later than its paired "before" value.
- **FR-008**: When `creatorOnly=true`, the tool MUST retain only candidates whose enriched channel is classified as creator-like by the shared documented creator-classification rule. The response MUST identify that classification as heuristic or inferred and state that it can be incomplete or inaccurate.
- **FR-009**: When `uniqueChannels=true`, the tool MUST return at most one eligible video per distinct channel. It MUST retain the highest-ranked eligible video for each channel, using base-search order as the deterministic tie-breaker. The default is `false`.
- **FR-010**: The tool MUST support `sortBy` values `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, and `recent_activity`, with `relevance` as the default. `relevance` preserves base-search order; subscriber modes order qualifying channels by subscriber count in the requested direction; `indie_priority` prioritizes creator-like channels with smaller available subscriber counts ahead of larger brands; and `recent_activity` prioritizes channels with more recent available latest-upload timestamps.
- **FR-011**: The tool MUST apply channel-level filtering before final ranking. For non-relevance ranking modes, candidates lacking metadata required by the selected ranking rule MUST be excluded and disclosed as partial enrichment; ties in every ranking mode MUST preserve base-search order.
- **FR-012**: Each returned item MUST include stable video identity and core metadata: `videoId`, `title`, `description` when available, `publishedAt`, `channelId`, `channelTitle`, and available thumbnails. When channel enrichment is available, it MUST include channel subscriber count, latest upload timestamp, and creator classification where applicable.
- **FR-013**: The response MUST identify the applied inputs, returned item count, continuation information when more base-search results are available, and the provenance of returned fields: raw source data, normalized data, or heuristic/inferred data.
- **FR-014**: The tool MUST disclose that it is a composed video-search workflow with optional channel enrichment, post-search filtering, ranking, and bounded one-result-per-channel behavior. It MUST disclose that channel-aware operations can have additional authorization sensitivity, quota impact, and partial-result risk.
- **FR-015**: For a successful base search with no matching or no qualifying candidates, the tool MUST return a successful empty collection. For invalid input, unavailable or hidden data, authorization-sensitive data, quota exhaustion, upstream failure, an unsupported filter or sort, or partial enrichment failure, it MUST return the corresponding safe, structured MCP-compatible outcome without stack traces, credentials, or unfiltered substitute results.

### Key Entities

- **Video Search Request**: The caller's query, base-search constraints, channel refinements, ranking choice, and result limit.
- **Video Candidate**: A video found by the base search, including its identity, core metadata, source channel, and base-search position.
- **Channel Enrichment**: Available channel metadata associated with a candidate, including subscriber count, latest upload timestamp, and creator classification with provenance and availability status.
- **Search Result Collection**: The bounded, ordered set of qualifying video candidates together with applied inputs, continuation information, field provenance, and any partial-enrichment disclosure.

### Assumptions

- YT-301 supplies the shared Layer 3 parameter, field-provenance, creator-classification, and safe error conventions referenced by this tool.
- This feature searches publicly discoverable video results only; it does not promise access to private, deleted, region-restricted, or authorization-sensitive content.
- A channel's subscriber count or other metadata may be hidden or unavailable. The tool will not infer a value simply to satisfy a numeric filter or ranking.
- `maxResults` is a limit on final returned results, not a guarantee that a highly restrictive request will produce that many qualifying results.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In the automated acceptance suite, 100% of valid invocations return a structured collection or a documented safe structured outcome, and 100% of invalid invocations are rejected before a search result is returned.
- **SC-002**: Across representative candidate sets, 100% of returned items satisfy every selected date, channel, subscriber, latest-upload, and creator filter; every `uniqueChannels=true` result set contains zero duplicate channel identifiers.
- **SC-003**: Across representative candidate sets, all five documented `sortBy` modes produce their specified order, and repeated invocations with the same source data produce the same tie order.
- **SC-004**: Under normal upstream availability, at least 95% of representative searches produce their structured outcome within 5 seconds.
- **SC-005**: In a task-based review, at least 90% of participating agent developers can construct a valid query-only search and correctly identify the effect of one channel-oriented refinement from the tool description and response alone.

