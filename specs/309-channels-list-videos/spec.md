# Feature Specification: Channel Video Listing

**Feature Branch**: `309-channels-list-videos`  
**Created**: 2026-08-12  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level channel video listing tool."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List a Channel's Videos (Priority: P1)

An MCP client provides a channel identifier and receives a stable, bounded collection of that channel's publicly available videos, ready for research without interpreting provider-specific resource layouts.

**Why this priority**: Retrieving videos for one known channel is the feature's essential research workflow.

**Independent Test**: Request a channel with known publicly available uploads and verify that the result contains no more than the requested number of distinct videos, in the documented source-collection order, with the documented identity and public metadata for each available video.

**Acceptance Scenarios**:

1. **Given** an accessible channel with publicly available uploads, **When** a client calls `channels_listVideos` with its `channelId`, **Then** it receives up to the default result limit in the channel uploads collection's order as observed for the request.
2. **Given** an accessible channel and a valid `maxResults` value, **When** a client requests its videos, **Then** it receives no more than that number of distinct available videos and the response identifies the applied limit.
3. **Given** an accessible channel with no publicly available uploads, **When** a client requests its videos, **Then** it receives a successful empty collection rather than an unavailable-channel error.

---

### User Story 2 - Understand Result Meaning and Ordering (Priority: P2)

An MCP client can determine from discovery metadata and the response which values preserve source information, which values are normalized for the public contract, and why the returned sequence is not a relevance-ranked search.

**Why this priority**: Research agents need to use the result collection confidently and must not mistake a deterministic channel-upload sequence for a ranked discovery result.

**Independent Test**: Inspect discovery metadata and a successful response; verify that both describe the uploads-collection listing approach, applied limit, source ordering, field provenance, public-content boundary, and the fact that the tool does not perform relevance ranking.

**Acceptance Scenarios**:

1. **Given** a successful listing, **When** a client inspects each returned item, **Then** it can identify the video identity and available public title, description, publication time, thumbnails, and their provenance.
2. **Given** a channel's uploads collection changes after an earlier request, **When** a client makes a later request, **Then** the later result reflects the collection available at that time without claiming that the earlier sequence remains unchanged.
3. **Given** a client needs ranked or keyword-based discovery, **When** it inspects this tool's contract, **Then** it is directed to use a search-oriented tool rather than assuming `channels_listVideos` ranks results by relevance.

---

### User Story 3 - Receive Safe Outcomes for Unavailable Content (Priority: P3)

An MCP client receives a clear, safe outcome when its request is malformed, the channel is unavailable, public listing access is insufficient, capacity is exhausted, or the source cannot complete the listing.

**Why this priority**: A research workflow must distinguish an empty accessible collection from an unavailable channel or a temporary failure without receiving sensitive account or source diagnostics.

**Independent Test**: Exercise invalid input, an unavailable channel, authorization-sensitive content, exhausted capacity, and a source failure; verify the documented category and that no private channel context, credentials, internal traces, or raw source payloads are exposed.

**Acceptance Scenarios**:

1. **Given** a missing, blank, or non-text `channelId`, **When** a client invokes the tool, **Then** it receives a validation outcome before any listing is attempted.
2. **Given** a syntactically valid identifier for a channel that cannot be publicly listed, **When** a client invokes the tool, **Then** it receives one safe unavailable-resource outcome that does not disclose whether the channel is deleted, hidden, restricted, or absent.
3. **Given** one or more items are not publicly accessible while the channel listing otherwise succeeds, **When** the client invokes the tool, **Then** the response omits inaccessible items, does not substitute or invent content, and discloses a safe partial-availability status when applicable.

### Edge Cases

- A `channelId` that is missing, non-text, or empty after trimming is rejected before any lookup.
- `maxResults` must be a whole number from 1 through 50; omitted values default to 10, and booleans, fractions, zero, negative values, and values above 50 are rejected.
- A channel may exist but have no publicly available uploads. This is a successful empty collection, distinct from an unavailable channel.
- Hidden, deleted, private, region-restricted, or otherwise inaccessible videos are not represented as placeholders and never expose non-public metadata.
- Repeated video entries in the source collection are de-duplicated by video identity, preserving the first available occurrence and source order.
- A newly published, removed, or re-ordered upload can change a later request's result; each result represents the public collection available at the time of that request.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing validation, handler, and contract tests for the required `channelId`, `maxResults` default and boundaries, successful ordered listing, empty accessible listing, item de-duplication, provenance, collection-path disclosure, and every safe failure or partial-availability outcome.
- **Green**: Implement only the public tool behavior needed to satisfy those tests: bounded public upload collection retrieval, source-order preservation, stable result shaping, required metadata, and safe outcome mapping.
- **Refactor**: Consolidate repeated channel/video normalization, source-order, provenance, and safe-error rules with the shared Layer 3 contracts after focused tests pass; then run the full repository verification suite before review.
- **Required test levels**: unit tests for validation, result normalization, de-duplication, and ordering; contract tests for discovery metadata, input and result shapes, provenance, and safe errors; and integration-style tests for available, empty, unavailable, partial-availability, capacity, and source-failure flows.
- Every new or changed Python function in scope must have a reStructuredText docstring describing its behavior, inputs, output, ordering guarantees, and safe failure behavior.
- **Pull-request evidence**: Show focused tests moving from failing to passing, `python3 -m pytest`, and `python3 -m ruff check .` with successful results. Include evidence for a populated channel, an empty accessible channel, an unavailable channel, an inaccessible item, and every `maxResults` boundary.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `channels_listVideos` that returns a bounded collection of publicly available videos for exactly one channel.
- **FR-002**: The tool MUST require `channelId` as one non-empty text identifier, trim surrounding whitespace, and reject missing, blank, or non-text values with a safe validation outcome before listing begins.
- **FR-003**: The tool MUST accept only the required `channelId` and optional `maxResults` inputs, and MUST reject unknown input fields so callers can determine the complete supported request shape from discovery metadata.
- **FR-004**: When omitted, `maxResults` MUST default to 10. It MUST accept only whole-number values from 1 through 50 and MUST reject all other values with a safe validation outcome.
- **FR-005**: The tool MUST use the channel's public uploads collection as its listing source, preserve that collection's available order at request time, and MUST NOT apply relevance ranking, keyword matching, or another reordering heuristic.
- **FR-006**: The tool MUST return no more than the applied `maxResults` number of distinct, publicly available video items. Each item MUST contain the video identifier and every available documented public value among title, description, publication time, and thumbnails.
- **FR-007**: The tool MUST de-duplicate returned items by video identifier while preserving the first available source-collection occurrence and its order.
- **FR-008**: The successful response MUST include `items`, `channelId`, `returnedCount`, and `maxResults`. It MUST represent absent optional public video values as unavailable rather than fabricating values.
- **FR-009**: The tool's response and discovery metadata MUST identify video identifiers and available public video metadata as source-preserved values, and result counts, applied inputs, and collection-order context as normalized contract values.
- **FR-010**: The tool's discovery metadata and caller documentation MUST state that this is a composed higher-level listing tool using the channel uploads collection rather than ranked search behavior; it MUST state the 1–50 bound, default, public-content boundary, ordering behavior, possible changes between requests, applicable access and capacity caveats, and caller-visible recovery guidance.
- **FR-011**: A channel with no publicly available uploads MUST return a successful response with an empty `items` collection and `returnedCount` of zero; it MUST not be reported as unavailable.
- **FR-012**: When individual videos cannot be publicly returned but the listing otherwise succeeds, the tool MUST omit those items, MUST NOT return substitute or inferred content, and MUST provide a safe partial-availability disclosure when an omission is known.
- **FR-013**: A syntactically valid channel identifier whose public listing cannot be retrieved because the channel is missing, deleted, hidden, restricted, or otherwise unavailable MUST produce one unavailable-resource outcome without disclosing the underlying reason.
- **FR-014**: The tool MUST return distinct, safe structured outcomes for invalid parameters, unavailable resources, authorization-sensitive data, capacity exhaustion, source-service failures, and partial availability. These outcomes MUST exclude credentials, private owner context, internal traces, raw source payloads, and non-public video data.

### Key Entities *(include if feature involves data)*

- **Channel video listing request**: A client request containing one channel identifier and an optional result limit.
- **Channel uploads collection**: The publicly available video sequence associated with a channel, observed at request time and preserved without relevance ranking.
- **Channel video item**: One distinct publicly available video with its identifier and available public metadata.
- **Listing result**: The bounded, ordered set of channel video items, its applied inputs, counts, provenance, and any safe partial-availability context.
- **Listing outcome**: A successful collection, successful empty collection, partial-availability result, or safe structured error.

## Assumptions

- YT-301 supplies the shared Layer 3 naming, input, response-provenance, composition, and safe-error conventions used by this feature.
- The uploads-collection approach is the selected behavior for this tool because it provides a source-ordered channel listing. Ranked or keyword-based video discovery remains outside this feature and belongs to a search-oriented tool.
- This feature lists only publicly available videos exposed to the service at request time; it does not seek access to private, scheduled, deleted, hidden, region-restricted, or owner-only content.
- `maxResults` limits the current response. Continuation traversal, filtering, ranking, video-detail enrichment, and channel statistics are not part of this slice.
- Changes in public channel content between requests are expected; the tool does not cache, infer, or promise a historical snapshot.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for populated accessible channels return a structured result containing no more than the applied limit, with no duplicate video identifiers and in the documented source-collection order.
- **SC-002**: In automated boundary testing, 100% of omitted, minimum, maximum, and invalid `maxResults` cases use the documented default, limit, or safe validation outcome.
- **SC-003**: In automated outcome testing, 100% of empty-accessible, unavailable-resource, authorization-sensitive, capacity-exhaustion, source-failure, and partial-availability cases use their documented safe outcome and expose no private data, credentials, internal traces, or raw source payloads.
- **SC-004**: Under normal source availability, at least 95% of representative requests for up to 50 videos produce their structured outcome within 5 seconds.
- **SC-005**: In a task-based review, at least 90% of participating agent developers can construct a valid request and correctly distinguish source-ordered channel listing from relevance-ranked search using discovery metadata and one response alone.
