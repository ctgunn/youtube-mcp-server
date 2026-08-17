# Feature Specification: Channel Content Search

**Feature Branch**: `318-channels-search-content`  
**Created**: 2026-08-14  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level channel-content search tool."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search a Channel's Content (Priority: P1)

An MCP client searches the publicly searchable content of one known channel using a query and receives only matching content associated with that channel.

**Why this priority**: This is the core research task and provides useful channel-specific discovery without requiring a client to collect and filter a broader catalog.

**Independent Test**: Submit a known channel identifier and a query with known matches, then verify that the returned items match the query and identify the requested channel.

**Acceptance Scenarios**:

1. **Given** a valid channel with publicly searchable content, **When** a client supplies its identifier and a non-empty query, **Then** the client receives a normalized collection of matching content items from that channel.
2. **Given** a valid channel and a query with no matching content, **When** the client searches, **Then** the client receives a successful empty collection rather than an error.
3. **Given** a request missing a channel identifier or query, **When** a client searches, **Then** the client receives a clear validation error that identifies the missing or invalid input.

---

### User Story 2 - Control Search Results (Priority: P2)

An MCP client limits the number of returned content items and chooses a supported ordering so results fit the research task.

**Why this priority**: Researchers need concise result sets and predictable ordering to compare recent, popular, or most relevant channel content.

**Independent Test**: Run the same valid search with each supported ordering and a requested result limit, then verify the returned count does not exceed the limit and the documented ordering is applied.

**Acceptance Scenarios**:

1. **Given** a search with more matches than requested, **When** a client specifies `maxResults`, **Then** the collection contains no more than that number of items.
2. **Given** a valid search, **When** a client specifies a supported `order`, **Then** results follow the selected ordering and the response records that ordering.
3. **Given** an unsupported ordering or an out-of-range result limit, **When** a client searches, **Then** the client receives a validation error listing the accepted values or range.

---

### User Story 3 - Refine Search by Language (Priority: P3)

An MCP client supplies an optional language preference to improve the relevance of a channel-content search for a target audience.

**Why this priority**: Language refinement improves research quality for multilingual channels while leaving the basic search workflow simple.

**Independent Test**: Run a search with a valid language preference and verify that the response preserves the requested preference and uses it as a relevance refinement.

**Acceptance Scenarios**:

1. **Given** a valid channel and query, **When** a client supplies a valid language preference, **Then** the search applies it as a relevance refinement and reports it in the response context.
2. **Given** an invalid language preference, **When** a client searches, **Then** the client receives a clear validation error without a partial result set.

### Edge Cases

- A channel may exist but have no publicly searchable content; the result is an empty collection, and the response does not claim that the channel is unavailable.
- Private, deleted, restricted, or otherwise unavailable content is omitted from results without exposing restricted metadata.
- A query containing only whitespace is rejected as invalid rather than treated as a broad search.
- If upstream search data is temporarily unavailable, the client receives a safe, actionable failure and no partial collection is presented as complete.
- If a requested language preference cannot improve relevance for the available content, results may still be returned; the response retains the requested preference so the client can interpret the outcome.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start each story with failing unit and contract tests for required inputs, channel scoping, empty results, result limits, supported ordering, language refinement, and safe failure behavior.
- **Green**: Add only the behavior needed to make those tests pass, including normalized result and response-context shapes that let an MCP client verify the requested channel, refinements, and ordering.
- **Refactor**: Consolidate shared validation and result-shaping rules after the tests pass, retain behavior coverage, and run the full repository test suite before review.
- Required test levels are unit tests for validation and result shaping, integration tests for channel-constrained search behavior, and MCP contract tests for discoverability, inputs, normalized results, and failures.
- Every new or changed Python function in scope must have complete project-standard reStructuredText docstrings covering its purpose, inputs, result, and failure behavior.
- Pull-request evidence must include the focused feature test results, the full-suite command `pytest`, and a passing full-suite result.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a tool named `channels_searchContent` for searching publicly searchable content associated with one channel.
- **FR-002**: The tool MUST require a non-empty `channelId` and a non-empty `query`, and reject missing, malformed, or whitespace-only values with a clear validation error.
- **FR-003**: For a valid request, the tool MUST return a normalized collection whose items are associated with the requested channel and include, when available, a content identifier, content type, title, description or summary, publication time, channel identity, and available thumbnail references.
- **FR-004**: The tool MUST accept an optional `maxResults` whole number from 1 through 50, default to 10 when omitted, and return no more items than the effective limit.
- **FR-005**: The tool MUST accept an optional `order` with exactly these values: `relevance`, `date`, and `viewCount`; it MUST default to `relevance` and report the effective ordering in the response context.
- **FR-006**: The tool MUST accept an optional `language` preference expressed as a valid BCP 47 language tag, use it only to refine relevance, and report the effective preference in the response context when one was supplied.
- **FR-007**: The initial release MUST use channel-constrained search behavior as its matching source and apply only normalization and response-context shaping; it MUST NOT claim to enrich, filter, or re-rank results beyond that behavior.
- **FR-008**: The tool's public contract MUST state that its matching behavior is a direct channel-constrained search, while its returned collection is normalized for MCP-client consumption.
- **FR-009**: A valid search with no matching publicly searchable content MUST return a successful empty collection with the effective channel identifier, query, limit, ordering, and any language preference in its response context.
- **FR-010**: The tool MUST return a safe, actionable error for unavailable search data or invalid optional values and MUST NOT present incomplete results as a complete collection.
- **FR-011**: The tool MUST omit content and metadata that the requesting client is not permitted to discover and MUST not disclose access-control details in an error or empty result.

### Key Entities *(include if feature involves data)*

- **Channel Content Search Request**: A client's channel identifier, query, optional result limit, ordering preference, and optional language preference.
- **Content Search Result**: One publicly searchable content item associated with the requested channel, including its identity, type, descriptive metadata, publication time, channel identity, and available thumbnail references.
- **Search Response Context**: The effective channel identifier, query, limit, ordering, and optional language preference used to produce a collection, including an empty collection.

### Assumptions

- The initial scope is limited to publicly searchable channel content; it does not establish entitlement to private, deleted, restricted, or owner-only material.
- `maxResults` defaults to 10 and is capped at 50 to keep a single research request concise and predictable.
- The selected `order` values represent the initial audience needs: relevance by default, newest-first content, or most-viewed content.
- A language preference refines relevance but does not guarantee that all returned content is in that language.
- An empty result set means no matching publicly searchable content was found; it does not independently verify whether the channel exists or is accessible.

### Dependencies

- **YT-301**: Provides the shared Layer 3 tool foundation required to publish a consistent research-oriented tool contract.
- **YT-309**: Provides the channel search capability on which channel-constrained content search depends.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In contract testing, 100% of valid searches return only items associated with the requested channel.
- **SC-002**: In contract testing, 100% of valid no-match searches return a successful empty collection with complete response context.
- **SC-003**: In usability testing with representative MCP clients, at least 95% of participants can retrieve and interpret channel-specific results on their first valid request without manual post-filtering.
- **SC-004**: In a representative set of 100 valid searches, at least 95 complete with a result or safe actionable failure within 5 seconds.
- **SC-005**: In contract testing, 100% of invalid required inputs, result limits, order values, and language preferences receive an actionable validation error and no partial collection.
