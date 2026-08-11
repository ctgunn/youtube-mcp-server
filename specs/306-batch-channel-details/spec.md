# Feature Specification: Batch Channel Details

**Feature Branch**: `306-batch-channel-details`  
**Created**: 2026-08-11  
**Status**: Draft  
**Input**: User description: "Define and implement the higher-level `channels_getChannels` tool so MCP clients can retrieve normalized, optionally latest-upload-enriched information about multiple YouTube channels in one request."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve Multiple Channel Details (Priority: P1)

An MCP client submits several channel identifiers and receives one stable, normalized channel-detail result for each requested channel that is available, without having to make a separate request per channel.

**Why this priority**: Batch retrieval is the feature's central value: it lets research and enrichment workflows obtain comparable channel information efficiently.

**Independent Test**: Request two or more available channel identifiers and verify that the response contains a result for each identifier in request order, with the documented core profile, normalized metadata, field provenance, and heuristic disclosures.

**Acceptance Scenarios**:

1. **Given** two or more available channel identifiers, **When** a client requests their details, **Then** it receives one successful channel-detail result per requested identifier in the same order as the request.
2. **Given** an available channel that lacks optional public profile values, **When** it appears in a batch request, **Then** its result represents those values as unavailable without fabricating a value or failing the other results.
3. **Given** a request with the maximum supported number of distinct channel identifiers, **When** all identifiers are valid, **Then** the batch is accepted and returns one independently interpretable result for every identifier.

---

### User Story 2 - Control Returned Detail and Latest-Upload Enrichment (Priority: P2)

An MCP client can limit the public channel-detail sections it needs and can choose whether to include latest-upload enrichment, while receiving an unambiguous result that distinguishes unavailable enrichment from enrichment that was not requested.

**Why this priority**: Callers often need only selected channel facts and can avoid unnecessary enrichment when it provides no value to their task.

**Independent Test**: Request a batch with selected detail sections and with latest-upload enrichment both enabled and disabled; verify that every item follows the requested detail selection and accurately reports its enrichment state.

**Acceptance Scenarios**:

1. **Given** a request without `includeLatestUpload`, **When** a client requests batch details, **Then** latest-upload enrichment is requested by default and every available item reports either its latest public upload timestamp or a documented unavailable or partial state.
2. **Given** a request with `includeLatestUpload` set to `false`, **When** a client requests batch details, **Then** no latest-upload timestamp is presented as a lookup result and each available item identifies that the enrichment was not requested.
3. **Given** a request with supported `parts`, **When** a client requests batch details, **Then** each successful item contains only the selected source-detail sections plus the always-present identity, outcome, and provenance information.

---

### User Story 3 - Continue Through Individual Unavailable Channels (Priority: P3)

An MCP client receives usable details for available channels even when another requested channel cannot be returned or has incomplete latest-upload enrichment.

**Why this priority**: Research batches frequently include outdated or inaccessible identifiers; a single such identifier should not discard the usable work in the batch.

**Independent Test**: Request a batch containing available, unavailable, no-upload, and partial-enrichment channels; verify that available items remain usable and every other item has the documented safe per-channel outcome.

**Acceptance Scenarios**:

1. **Given** a batch containing available and unavailable channel identifiers, **When** a client requests details, **Then** available identifiers return channel details and each unavailable identifier returns a safe unavailable-resource item without revealing why it is unavailable.
2. **Given** a channel whose core profile is available but whose latest-upload enrichment cannot be completed, **When** latest-upload enrichment is requested, **Then** that item returns the usable core profile with a safe partial-enrichment state while unaffected batch items retain their own outcomes.
3. **Given** a malformed batch request, **When** the client submits it, **Then** the entire request is rejected before any channel lookup and the validation response explains the supported request shape safely.

### Edge Cases

- A missing, non-list, empty, over-limit, duplicate, blank, or non-text `channelIds` entry rejects the entire request before lookup.
- The batch supports from 1 through 50 distinct channel identifiers; a request above that limit is rejected with guidance to split it into smaller batches.
- A channel with no publicly visible uploads returns a successful core detail with latest-upload enrichment marked unavailable, not an unavailable-channel outcome.
- If `includeLatestUpload` is `false`, `latestVideoPublishedAt` is not populated and the item's enrichment status is `not_requested`; this is distinct from an unavailable timestamp.
- Unsupported, duplicate, or empty `parts` selections reject the entire request; omitted `parts` select the documented standard public channel-detail set.
- If a requested source-detail section is absent for one channel, that channel reports that section as unavailable without changing the selected detail sections or outcome for other items.
- A partial batch response must never expose credentials, private owner context, raw internal failures, or non-public contact information.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Begin with failing behavioral and contract tests for batch-size and identifier validation; ordered per-item results; default and suppressed latest-upload enrichment; selected detail sections; normalization and provenance; and mixed available, unavailable, no-upload, and partial-enrichment batches.
- **Green**: Add only the batch validation, per-channel outcome handling, stable item shaping, detail selection, and bounded enrichment behavior needed to satisfy those tests.
- **Refactor**: Consolidate repeated one-channel normalization, provenance, and enrichment-state rules with the shared channel-detail contract after focused tests pass. Run complete repository verification before review.
- **Required test levels**: unit tests for validation, ordering, selection, and enrichment-state rules; contract tests for discovery metadata and response/error shapes; and integration-style tests for representative mixed-outcome batches.
- Every new or changed Python function in scope must have a reStructuredText docstring covering its behavior, inputs, outputs, and safe failure behavior.
- **Pull-request evidence**: Show focused tests moving from failing to passing, `python3 -m pytest`, and `python3 -m ruff check .` with successful results. Include evidence for the maximum supported batch size, default and disabled enrichment, an unavailable channel alongside an available one, a no-upload channel, and a partial-enrichment item.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `channels_getChannels` that retrieves normalized details for multiple YouTube channels in one request.
- **FR-002**: The tool MUST require `channelIds` as a list of 1 through 50 distinct, non-empty text identifiers and MUST reject a missing, non-list, empty, over-limit, duplicate, blank, or non-text value before any lookup.
- **FR-003**: The tool MUST accept an optional `parts` list that selects supported public source-detail sections. Omitted `parts` MUST select the documented standard public channel-detail set; supplied selections MUST be non-empty, distinct, and supported.
- **FR-004**: The tool MUST accept an optional Boolean `includeLatestUpload` whose default is `true`. Discovery metadata and caller documentation MUST state this default and its effect.
- **FR-005**: The tool MUST reject unknown input fields so callers can determine the complete supported request shape from discovery metadata.
- **FR-006**: For each available requested channel, the result MUST contain the channel identifier, an item outcome, the requested available public detail sections, and field-provenance information. Successful items MUST appear in the same order as their corresponding identifiers in `channelIds`.
- **FR-007**: Each successful item MUST apply the same channel-detail normalization rules as `channels_getChannel` where the selected data permits, including a `normalizedMetadata` grouping for available `country`, `defaultLanguage`, `joinedAt`, `customUrl`, `emailsFound`, and `contactLinks`. It MUST represent unavailable values as unavailable rather than invented.
- **FR-008**: Each successful item that includes normalized contact values or creator-versus-brand information MUST identify those values as public-information-derived, disclose their basis and limitations, and state that they are not canonical source truth or verified identity claims.
- **FR-009**: Field-provenance information for each successful item MUST distinguish raw source values, normalized values, and heuristic-inferred values for all returned fields. The batch container MUST separately identify batch-level metadata from item-level channel data.
- **FR-010**: When `includeLatestUpload` is `true`, each available item MUST include `latestVideoPublishedAt` when its latest publicly visible upload timestamp can be determined. The timestamp MUST be identified as normalized enrichment, not as a raw channel-profile field.
- **FR-011**: When `includeLatestUpload` is `true` and an available channel has no latest publicly visible upload or no available timestamp, the item MUST retain the usable core detail, mark `latestVideoPublishedAt` unavailable, and report the documented enrichment state without substituting an older, hidden, stale, or guessed timestamp.
- **FR-012**: When `includeLatestUpload` is `false`, the tool MUST not obtain or present a latest-upload timestamp as a result of the request. Each successful item MUST report its enrichment status as `not_requested`.
- **FR-013**: The response MUST include batch-level counts for requested, successful, unavailable, and partially enriched items so a caller can assess the batch without inferring counts from item contents.
- **FR-014**: A syntactically valid identifier whose channel cannot be returned MUST produce a safe unavailable-resource item without revealing whether the channel is deleted, hidden, restricted, or not found. That item's outcome MUST NOT prevent other valid identifiers in the same batch from returning their independent results.
- **FR-015**: The tool MUST return distinct, safe structured outcomes for invalid batch parameters, per-channel unavailability, authorization-sensitive data, quota exhaustion, source-service failures, and partial enrichment failures. These outcomes MUST exclude credentials, private owner context, internal traces, raw source payloads, and non-public contact information.
- **FR-016**: The tool's discovery metadata and caller documentation MUST describe the input limits, default `parts`, default `includeLatestUpload` behavior, result ordering, per-item and batch-level outcomes, field provenance, normalization and heuristic limits, boundedness, failure categories, and recovery guidance.

### Key Entities *(include if feature involves data)*

- **Batch channel request**: A client request containing 1 through 50 distinct channel identifiers, optional selected detail sections, and a latest-upload enrichment preference.
- **Batch channel result**: An ordered collection of independently interpretable per-channel results with summary counts.
- **Channel detail item**: One available channel's public source details, normalized metadata, provenance information, and optional latest-upload enrichment outcome.
- **Item outcome**: The safe per-channel status of a successful, unavailable, partially enriched, or failed lookup.
- **Detail selection**: The client-requested set of supported public source-detail sections returned for each available channel.
- **Latest-upload enrichment**: The availability-aware latest public upload timestamp or an explicit `unavailable`, `partial`, or `not_requested` state.

## Assumptions

- YT-301 provides the shared Layer 3 naming, parameter, field-provenance, heuristic-disclosure, composition, and safe-error conventions used by this feature.
- `channels_getChannel` remains the canonical single-channel detail contract. This batch feature applies its normalization and disclosure rules per item where the selected data permits; it does not expand the single-channel feature's public-data scope.
- A batch limit of 50 distinct identifiers is the documented initial boundary, providing a predictable request size and clear client batching behavior.
- `parts` controls selectable public source-detail sections, while identity, outcome, requested-result order, provenance, and enrichment status remain available for every item so results are interpretable.
- Latest-upload enrichment considers only content publicly visible to the service at request time and does not use private, scheduled, unavailable, or stale content.
- A channel's core detail can succeed even when its optional latest-upload enrichment is unavailable or fails. Malformed batch input, by contrast, prevents all lookups.
- Search, discovery, ranking, creator filtering, channel video listing, playlist listing, and statistics remain outside this feature's scope.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid batches containing 1 through 50 available channel identifiers return one ordered, independently interpretable successful item per identifier.
- **SC-002**: In automated contract testing, 100% of omitted `includeLatestUpload` requests use the documented enabled default, and 100% of requests that set it to `false` report `not_requested` without a populated latest-upload timestamp.
- **SC-003**: In automated mixed-batch testing, 100% of available items remain usable when the same request includes unavailable or partially enriched items, and every item and summary count matches its documented outcome.
- **SC-004**: In automated provenance and privacy testing, 100% of returned channel fields are labeled consistently as raw source, normalized, or heuristic-inferred, and no test response contains credentials, private owner context, internal traces, raw source payloads, or non-public contact values.
- **SC-005**: Under normal source availability, at least 95% of representative batches of up to 50 identifiers produce complete or safely partial structured results within 15 seconds.
- **SC-006**: In a task-based review, at least 90% of participating agent developers can determine input limits, default enrichment behavior, per-item status, batch completeness, provenance, and recovery action from discovery metadata and a response alone.
