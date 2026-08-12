# Feature Specification: Channel Search

**Feature Branch**: `307-channel-search`  
**Created**: 2026-08-11  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level channel search tool."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search for Relevant Channels (Priority: P1)

An MCP client searches public channels by handle, channel name, or a general topic query and receives a stable collection of distinct matching channels.

**Why this priority**: A query-only channel search is the core discovery workflow and provides immediate research value without any optional refinement.

**Independent Test**: Submit valid handle-like, name, and general-topic queries; verify that each successful result has no more than the requested number of distinct channels, has the documented core channel fields, and that a query with no matches produces an empty collection.

**Acceptance Scenarios**:

1. **Given** a non-empty handle, name, or general query, **When** the client searches without optional refinements, **Then** it receives up to 10 distinct matching channels in base relevance order.
2. **Given** a valid query and a supported base ordering or channel-type constraint, **When** the client searches, **Then** every returned channel satisfies the selected base-search constraint.
3. **Given** a valid query with no public channel matches, **When** the client searches, **Then** it receives a successful empty collection with the applied search context.

---

### User Story 2 - Refine Channels by Research Criteria (Priority: P2)

An MCP client narrows search results to channels in a subscriber range, channels active within a time period, or channels classified as creator-like, without treating unavailable data as a match.

**Why this priority**: Research workflows frequently need to identify active creators or channels of a particular scale rather than manually inspect every search result.

**Independent Test**: Search a controlled candidate set using each refinement independently and in combination; verify that every returned channel meets all selected criteria and that unavailable required data is disclosed rather than guessed.

**Acceptance Scenarios**:

1. **Given** a valid query and an inclusive subscriber range, **When** the client searches, **Then** every returned channel has an available public subscriber count within that range.
2. **Given** a valid query and an inclusive latest-upload window, **When** the client searches, **Then** every returned channel has an available public latest-upload timestamp within that window.
3. **Given** a valid query and `creatorOnly=true`, **When** the client searches, **Then** every returned channel is classified as creator-like and the response identifies that classification as a heuristic rather than a verified identity.

---

### User Story 3 - Rank Channels for a Research Goal (Priority: P3)

An MCP client chooses a documented ranking mode to prioritize matching channels by source relevance, audience size, creator-oriented independence, or recent public activity.

**Why this priority**: Explicit ranking lets the same discovery query answer different research questions without forcing clients to recreate channel comparisons.

**Independent Test**: Search a controlled eligible candidate set with each `sortBy` value and verify the documented ranking, stable ties, and treatment of candidates missing data required by a ranking mode.

**Acceptance Scenarios**:

1. **Given** eligible enriched channels and `sortBy=subscribers_asc` or `sortBy=subscribers_desc`, **When** the client searches, **Then** results are ordered by available subscriber count in the requested direction.
2. **Given** eligible enriched channels and `sortBy=indie_priority` or `sortBy=recent_activity`, **When** the client searches, **Then** results follow the documented creator-size or public-activity ranking rule.
3. **Given** `sortBy=relevance`, **When** the client searches, **Then** the result preserves base-search order after selected filters are applied.

### Edge Cases

- A missing query, a query blank after trimming, an unknown input field, a result limit outside 1–50, an unsupported enum value, or a value of the wrong type produces a safe validation error before search begins.
- A minimum subscriber value greater than the maximum, or an `After` timestamp later than its paired `Before` timestamp, produces a safe validation error before candidates are evaluated.
- Timestamp boundaries are inclusive and must be valid ISO 8601 timestamps with `Z` or an explicit numeric timezone offset.
- A candidate with hidden, unavailable, or failed enrichment is retained only when neither an active filter nor the selected ranking requires the unavailable value. Otherwise it is excluded and counted in safe partial-enrichment information.
- If no candidate can be evaluated for a requested refinement or non-relevance ranking because required enrichment is unavailable, the tool returns a safe partial-enrichment outcome rather than unfiltered substitute results.
- Duplicate base candidates for one channel are represented once in the final collection; the candidate with the earliest base-search position wins any otherwise equal choice.
- An empty result after base searching or applying filters is a successful empty collection, distinct from invalid input, authorization-sensitive data, quota exhaustion, and source failure.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing behavioral and contract tests for query validation, defaults, base search constraints, each refinement, all five ranking modes, deterministic ties, result provenance, empty collections, partial enrichment, and safe failures.
- **Green**: Add only the validation, public candidate discovery, conditional enrichment, filter-before-rank processing, bounded result shaping, and safe outcome mapping needed to satisfy those tests.
- **Refactor**: Consolidate channel search, enrichment, filtering, and ranking rules with shared Layer 3 conventions after focused tests pass. Run the complete repository test suite after refactoring.
- **Required test levels**: unit tests for validation, filter, ranking, de-duplication, and result shaping; contract tests for tool discovery and result/error shapes; integration tests for the composed channel-search workflow; and end-to-end invocation coverage where the hosted MCP verification path is available.
- Every new or changed Python function in scope must have a reStructuredText docstring that describes its behavior, inputs, returned values, and safe failure behavior.
- **Pull-request evidence**: Show focused tests moving from failing to passing, `python3 -m pytest`, and `python3 -m ruff check .` completing successfully. Include evidence for all ranking modes, all refinement types, an empty collection, unavailable required enrichment, and an invalid range.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `channels_searchChannels` for searching publicly discoverable channels by handle, channel name, or general query.
- **FR-002**: The tool MUST require `query` as non-empty text after trimming, reject unknown input fields, and accept only these optional inputs: `maxResults`, `order`, `channelType`, `minSubscribers`, `maxSubscribers`, `lastUploadAfter`, `lastUploadBefore`, `creatorOnly`, and `sortBy`.
- **FR-003**: The tool MUST default `maxResults` to 10, accept only whole-number values from 1 through 50 inclusive, and return no more than `maxResults` final channels.
- **FR-004**: The tool MUST accept `order` values `date`, `relevance`, `title`, and `videoCount` for base-search ordering. When omitted, base relevance ordering applies.
- **FR-005**: The tool MUST accept `channelType` values `any` and `show`. When omitted, it MUST not restrict matches by channel type.
- **FR-006**: The tool MUST derive a base candidate collection from the supplied query and selected base constraints, normalize each candidate to one distinct public channel, and preserve the candidate's base-search position for deterministic ordering.
- **FR-007**: The tool MUST apply `minSubscribers` and `maxSubscribers` as inclusive, non-negative whole-number bounds on available public subscriber counts. It MUST reject a supplied minimum greater than its paired maximum and MUST not invent a hidden or unavailable count.
- **FR-008**: The tool MUST apply `lastUploadAfter` and `lastUploadBefore` as inclusive bounds on an available public latest-upload timestamp. It MUST accept valid ISO 8601 timestamps with an explicit timezone and reject a supplied lower boundary later than its paired upper boundary.
- **FR-009**: When `creatorOnly=true`, the tool MUST retain only channels classified as creator-like by the shared documented public-signal heuristic. The response MUST identify the classification and supporting signals as inferred, potentially incomplete, and not a verified identity claim. The default is `false`.
- **FR-010**: The tool MUST support `sortBy` values `relevance`, `subscribers_asc`, `subscribers_desc`, `indie_priority`, and `recent_activity`, defaulting to `relevance`. `relevance` preserves base-search order after filtering; subscriber modes order eligible channels by available subscriber count in the selected direction; `indie_priority` places creator-like channels ahead of non-creator-like channels and then prefers smaller available subscriber counts; and `recent_activity` orders eligible channels by most recent available public latest-upload timestamp.
- **FR-011**: The tool MUST apply all selected refinements before final ranking and then cap the result at `maxResults`. For non-relevance rankings, candidates without the value required by the selected ranking rule MUST be excluded; every ranking tie MUST preserve base-search order.
- **FR-012**: The tool MUST conditionally enrich candidates when a selected filter or ranking needs subscriber count, latest-upload activity, or creator classification. It MUST evaluate enrichment only from available public channel information and must not use owner, credential, private, hidden, or inferred substitute data to satisfy a filter or ranking rule.
- **FR-013**: Each returned item MUST include its stable channel identifier, title, available public description and thumbnails, available normalized metadata, available public statistics, applicable heuristic information, and field-provenance information distinguishing source-preserved, normalized, and heuristic-inferred values.
- **FR-014**: A successful response MUST identify applied inputs, returned item count, any available continuation information, and a safe partial-enrichment summary whenever candidates were excluded because required enrichment was unavailable. The summary MUST state aggregate counts and safe reason categories without exposing credentials, internal traces, or raw source payloads.
- **FR-015**: Discovery metadata and caller documentation MUST state that this is a composite higher-level search tool, describe its candidate discovery, conditional enrichment, filtering, de-duplication, and ranking sequence, and disclose access, quota, and partial-result caveats.
- **FR-016**: A valid query with no matching or qualifying channels MUST return a successful empty collection. Invalid input, unavailable or authorization-sensitive data, quota exhaustion, source-service failure, and partial-enrichment failure MUST produce distinct safe structured outcomes without stack traces, credentials, private owner context, raw source payloads, or unfiltered substitute results.

### Key Entities

- **Channel Search Request**: The caller's query, optional base constraints, refinements, ranking choice, and result limit.
- **Channel Candidate**: One distinct publicly discoverable channel matched by the base search, including a stable identifier, source-preserved fields, and base-search position.
- **Channel Enrichment**: Available public subscriber, latest-upload, and creator-classification information used to evaluate active filters or rankings, with provenance and availability status.
- **Search Result Collection**: The ordered, bounded set of qualifying channel candidates together with applied inputs, continuation information, provenance, and optional partial-enrichment summary.
- **Partial Enrichment Summary**: A safe aggregate explanation of candidates excluded because data required for a selected refinement or ranking was unavailable.

## Assumptions

- YT-301 provides the shared Layer 3 conventions for parameter validation, field provenance, heuristic disclosure, composition, and safe structured errors.
- The feature is limited to public channel discovery. It does not provide private, deleted, hidden, region-restricted, owner-only, or otherwise authorization-sensitive channel information.
- `maxResults` caps final returned channels and does not guarantee that a restrictive query will return that many qualifying results.
- Public subscriber counts, latest-upload activity, and creator-classification signals can be absent or unavailable. The tool excludes a candidate when an active rule requires unavailable data rather than treating it as a match.
- `creatorOnly` and `indie_priority` use the shared creator-like public-signal heuristic; neither verifies a channel owner's identity, organizational status, or independence.
- This feature does not cover single-channel detail lookup, batch channel lookup, creator discovery from videos, channel video or playlist listing, or channel statistics; those workflows belong to separate feature slices.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid query-only requests return a structured collection containing no more than the requested number of distinct channels, or a documented safe structured outcome when public search data is unavailable.
- **SC-002**: Across representative candidate sets, 100% of returned channels satisfy every selected subscriber, latest-upload, and creator-only refinement; 100% of candidates missing data required by an active refinement or non-relevance ranking are excluded and disclosed safely.
- **SC-003**: Across representative candidate sets, all five `sortBy` modes produce the documented order, and repeated searches over the same source data preserve the same order for ties.
- **SC-004**: In automated contract testing, 100% of successful results identify applied inputs, result count, field provenance, and any applicable partial-enrichment information; 100% of safe failure outcomes exclude credentials, private owner information, internal traces, and raw source payloads.
- **SC-005**: Under normal public-source availability, at least 95% of representative searches return a complete, safely partial, or empty structured result within 5 seconds.
- **SC-006**: In a task-based review, at least 90% of participating agent developers can construct a valid query-only search, choose an appropriate refinement or ranking mode, and determine the provenance and limitations of returned values from the tool description and response alone.
