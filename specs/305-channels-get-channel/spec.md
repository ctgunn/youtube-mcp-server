# Feature Specification: Channel Details

**Feature Branch**: `305-channels-get-channel`
**Created**: 2026-08-11
**Status**: Draft
**Input**: User description: "Define and implement the higher-level `channels_getChannel` tool, providing normalized and enriched information about a YouTube channel."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Retrieve One Channel's Details (Priority: P1)

An MCP client requests one channel by its identifier and receives a stable, normalized channel profile that it can use for research without interpreting source-specific field layouts.

**Why this priority**: A dependable single-channel result is the feature's core value and is the basis for channel research workflows.

**Independent Test**: Request an available channel with a valid `channelId` and verify that the result contains the channel identity, available public profile details, normalized metadata, provenance, and a latest-video publication value when one is available.

**Acceptance Scenarios**:

1. **Given** an available channel and a valid `channelId`, **When** a client requests channel details, **Then** it receives one normalized result containing the documented core profile, `normalizedMetadata`, `latestVideoPublishedAt` when available, and field-provenance information.
2. **Given** an available channel whose optional public profile values are absent, **When** a client requests channel details, **Then** the result represents those values as unavailable without inventing a value or failing the otherwise successful lookup.
3. **Given** an available channel with public contact information, **When** a client requests channel details, **Then** any returned email addresses and contact links are limited to information visibly published by the channel and are identified as derived rather than canonical channel facts.

---

### User Story 2 - Assess Channel Type With Appropriate Caution (Priority: P2)

An MCP client receives an explicitly non-canonical creator-versus-brand assessment and the public signals used to make that assessment, so it can use the assessment as research context rather than verified identity.

**Why this priority**: Channel discovery and research often need a quick indication of channel type, but presenting an inference as fact could mislead downstream decisions.

**Independent Test**: Request channels with creator-like, brand-like, and insufficient public signals; verify that each assessment uses the documented category, includes only applicable public signals, and identifies uncertainty.

**Acceptance Scenarios**:

1. **Given** a channel with sufficient public creator-like or brand-like signals, **When** a client requests channel details, **Then** the response includes a creator-versus-brand classification and the signals supporting it.
2. **Given** a channel with insufficient or conflicting public signals, **When** a client requests channel details, **Then** the response classifies it as `unknown` rather than asserting `creator` or `brand`.
3. **Given** a client receives a classification, **When** it inspects the response or discovery information, **Then** it can determine that the classification and its signals are heuristic, may be incomplete, and are not canonical source truth.

---

### User Story 3 - Handle Missing Channels and Incomplete Enrichment Safely (Priority: P3)

An MCP client receives clear, safe outcomes when the requested channel cannot be retrieved or the latest-video enrichment cannot be completed.

**Why this priority**: Research workflows need to distinguish a missing channel from a usable profile with incomplete enrichment, without receiving sensitive source details.

**Independent Test**: Exercise invalid input, an unavailable channel, a channel with no visible uploads, and a latest-video enrichment failure. Verify that each produces the documented safe outcome or partial result.

**Acceptance Scenarios**:

1. **Given** a missing, blank, or non-text `channelId`, **When** a client requests channel details, **Then** it receives a validation error before any lookup is attempted.
2. **Given** a syntactically valid identifier for a channel that cannot be returned, **When** a client requests channel details, **Then** it receives an unavailable-resource outcome that does not disclose whether the channel is deleted, hidden, restricted, or not found.
3. **Given** the core channel profile is available but latest-video enrichment is unavailable or fails, **When** a client requests channel details, **Then** it receives the usable channel profile with `latestVideoPublishedAt` marked unavailable and a safe partial-enrichment status.

### Edge Cases

- A `channelId` that becomes empty after trimming, is missing, or is not text is rejected before lookup.
- A channel with no publicly visible uploads returns a successful channel profile with `latestVideoPublishedAt` unavailable; it is not treated as a missing channel.
- A channel may have a profile but no country, default language, joined date, custom URL, public email address, or public contact link. Each absent value remains unavailable rather than being inferred.
- Duplicate, malformed, non-public, or unsupported contact values are omitted from `emailsFound` and `contactLinks`; the result must not expose private account or owner information.
- If latest-video enrichment cannot be completed because of authorization, quota, or a temporary source problem, the core profile remains usable and the response identifies a safe partial-enrichment category rather than presenting a stale or guessed timestamp.
- The creator-versus-brand assessment is `unknown` when available public signals are insufficient or conflict. It must not use private information, credentials, or owner context.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing behavioral and contract tests for required-channel validation, successful core normalization, every required normalized-metadata field, public-contact extraction safety, latest-video enrichment, provenance labeling, creator/brand/unknown heuristic outcomes, and safe unavailable and partial-enrichment outcomes.
- **Green**: Add only the behavior needed for those tests: one-channel lookup, bounded latest-video enrichment, stable response shaping, public-contact handling, cautious heuristic disclosure, and safe outcome mapping.
- **Refactor**: Consolidate repeated channel normalization, provenance, and heuristic-disclosure rules after focused tests pass; preserve the shared Layer 3 contract and run complete repository verification before review.
- **Required test levels**: unit tests for validation, normalization, contact-value handling, timestamp selection, and heuristic rules; contract tests for discovery metadata, response provenance, and safe result/error shapes; and integration-style tests for successful, unavailable, and partial-enrichment requests.
- Every new or changed Python function in scope must have a reStructuredText docstring describing its behavior, inputs, output, and safe failure behavior.
- **Pull-request evidence**: Show focused tests moving from failing to passing, `python3 -m pytest`, and `python3 -m ruff check .` with successful results. Include evidence for a channel with an available latest video, a channel without one, an unavailable channel, and a partial-enrichment failure.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public MCP tool named `channels_getChannel` that retrieves normalized and enriched details for exactly one YouTube channel.
- **FR-002**: The tool MUST require `channelId` as one non-empty text identifier and MUST reject a missing, blank, or non-text value with a safe validation error before lookup.
- **FR-003**: The tool MUST reject unknown input fields so callers can determine the complete supported request shape from discovery metadata.
- **FR-004**: For a successful lookup, the tool MUST return the requested `channelId`, available public channel title, description, and thumbnails, preserving their source meaning and identifying them as raw upstream values.
- **FR-005**: For a successful lookup, the tool MUST return `normalizedMetadata` and document it as a stable, normalized container. When available, it MUST contain `country`, `defaultLanguage`, `joinedAt`, and `customUrl`; unavailable values MUST be represented as unavailable rather than fabricated.
- **FR-006**: The tool MUST include `normalizedMetadata.emailsFound` and `normalizedMetadata.contactLinks` as normalized lists of valid, publicly published contact values when such values are available. It MUST omit values that are private, malformed, duplicated, or unsupported and MUST identify contact extraction as heuristic-inferred rather than canonical source truth.
- **FR-007**: The tool MUST include `latestVideoPublishedAt` when it can determine a channel's latest publicly visible video publication timestamp. The timestamp MUST be clearly identified as normalized enrichment rather than a raw channel-profile field.
- **FR-008**: When no latest publicly visible video exists or its publication timestamp is unavailable, the tool MUST return the usable channel profile with `latestVideoPublishedAt` marked unavailable and a documented enrichment status. It MUST not substitute an older, hidden, or guessed timestamp.
- **FR-009**: The tool MUST return a `heuristics` group containing `creatorClassification` and `creatorSignals`. `creatorClassification` MUST be one of `creator`, `brand`, or `unknown`; `unknown` MUST be used when public evidence is insufficient or conflicting.
- **FR-010**: The tool MUST disclose that `creatorClassification`, `creatorSignals`, `emailsFound`, and `contactLinks` are derived from available public information, identify the applicable basis and limitations, and state that they are not canonical source truth or verified identity claims.
- **FR-011**: The response MUST include field-provenance information that distinguishes raw upstream fields, normalized fields, and heuristic-inferred fields for every returned top-level field and every populated member of `normalizedMetadata` and `heuristics`.
- **FR-012**: The tool MUST use a bounded lookup flow for one requested channel and, at most, one latest-video enrichment result. Its discovery metadata and caller documentation MUST disclose that it is a higher-level normalized and enriched tool, the enrichment's potential for unavailable or partial results, and applicable access and quota caveats.
- **FR-013**: A syntactically valid identifier whose channel cannot be returned because it is missing, deleted, hidden, restricted, or otherwise unavailable MUST produce one unavailable-resource outcome without revealing the underlying availability reason.
- **FR-014**: The tool MUST return distinct, safe structured outcomes for invalid parameters, unavailable resources, authorization-sensitive data, quota exhaustion, source-service failures, and partial enrichment failures. These outcomes MUST exclude credentials, private owner context, internal traces, raw source payloads, and non-public contact information.
- **FR-015**: The tool's discovery metadata and caller documentation MUST state the required input, successful response fields and provenance, contact-value and heuristic limitations, latest-video enrichment behavior, boundedness, caller-visible failure categories, and recovery guidance.

### Key Entities *(include if feature involves data)*

- **Channel request**: A client request containing exactly one required channel identifier.
- **Channel detail**: The stable response for an available channel, combining source-preserved profile values with normalized metadata and bounded enrichment.
- **Normalized metadata**: A stable grouping of public country, default language, joined date, custom URL, and safely derived public contact values.
- **Latest-video enrichment**: The availability-aware timestamp for the channel's most recently published publicly visible video.
- **Channel heuristic**: A non-canonical creator-versus-brand assessment and its public supporting signals.
- **Lookup outcome**: A successful, partial, unavailable, or safe failure result for a channel request.

## Assumptions

- YT-301 provides the shared Layer 3 naming, parameter, field-provenance, heuristic-disclosure, composition, and safe-error conventions used by this feature.
- This feature is limited to a single channel. Batch lookup, channel search, creator discovery and ranking, channel video listing, playlist listing, and statistics are covered by separate slices.
- The latest-video value is based only on publicly visible channel content available to the service at request time; it does not infer publication dates from private, scheduled, unavailable, or stale content.
- Public contact values may be normalized only from public channel material. The feature neither seeks access to private contact information nor verifies that a published address or link belongs to the channel owner.
- Creator-versus-brand classification is a research aid, not a fact about a person or organization. It relies solely on documented public signals and defaults to `unknown` when certainty is not justified.
- An enrichment failure is partial only after the core channel profile has been retrieved successfully. If the core profile cannot be retrieved, the tool returns the applicable whole-request failure outcome.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated acceptance testing, 100% of valid requests for available channels return a structured channel detail containing every available required core, normalized-metadata, provenance, and heuristic field.
- **SC-002**: In automated enrichment testing, 100% of channels with a publicly visible latest video return its documented publication timestamp, and 100% of channels without an available timestamp return an explicit unavailable enrichment state without a guessed value.
- **SC-003**: In automated provenance testing, 100% of returned fields are labeled raw upstream, normalized, or heuristic-inferred consistently with the documented contract.
- **SC-004**: In automated failure-path testing, 100% of invalid-input, unavailable-resource, authorization-sensitive, quota, source-failure, and partial-enrichment cases use their documented safe outcome and expose no credentials, private owner context, internal traces, raw source payloads, or non-public contact data.
- **SC-005**: Under normal source availability, at least 95% of representative single-channel requests produce a complete or safely partial structured result within 5 seconds.
- **SC-006**: In a task-based review, at least 90% of participating agent developers can determine the required input, provenance of returned values, non-canonical status of contact and classification heuristics, and recovery action for an unavailable or partial result from discovery metadata and the response alone.
