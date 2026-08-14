# Research: YT-315 Transcript Search

## Decision: Compose Timestamped Caption Retrieval Rather Than Plain Transcript Retrieval

`transcripts_searchTranscript` will inject and call the existing concrete `transcripts_getTimestampedCaptions` handler, then search its normalized `segments` locally.

**Rationale**: The YT-304 `transcripts_getTranscript` result deliberately contains only complete plain text, while YT-315 must return per-match start and end timestamps. The YT-314 handler already authorizes and bounds caption discovery/download, chooses a language, normalizes VTT cues, and exposes timed segments. Composition preserves those behaviors without duplicating them or calling the public dispatcher recursively.

**Alternatives considered**:

- Compose `transcripts_getTranscript`: rejected because it cannot provide the required timestamp values.
- Repeat caption-list, caption-download, and VTT parsing logic: rejected because it would duplicate authorization, quota, language, parsing, observability, and error behavior.
- Call the public MCP tool through a nested dispatcher: rejected because it creates an unnecessary protocol recursion and weaker dependency control in tests.

## Decision: Use Case-Insensitive Literal Segment-Local Matching

Normalize the query and segment text with Unicode case folding, then match the literal query only within each normalized segment. Return at most one result for a segment, even when the query appears more than once there. Never combine text from different segments.

**Rationale**: This is predictable, satisfies the accepted specification, and avoids an unbounded relevance or semantic-ranking policy. It gives every returned timestamp a direct source segment.

**Alternatives considered**:

- Semantic, fuzzy, synonym, or token search: rejected because it changes user expectations and is explicitly out of scope.
- One result per occurrence: rejected because the feature specifies matching transcript segments and would duplicate the same time interval.
- Cross-segment phrase matching: rejected because it would need synthesized timing and snippets, which are out of scope.

## Decision: Rank Chronologically and Apply the Limit Last

Sort matches by ascending `startTimeSeconds`; for equal timestamps retain the selected transcript's original segment order. Apply `maxMatches` only after ordering. `maxMatches` defaults to 10 and accepts integers from 1 through 50.

**Rationale**: Chronological results allow reliable navigation through a video and implement the feature's stated ranking rule. A bounded final limit prevents an ordinary common-term query from producing an oversized agent response.

**Alternatives considered**:

- Relevance scoring or the representative catalog's `matchScore`: rejected because the accepted specification requires chronological ranking and does not define a relevance heuristic.
- Source-order-only results: rejected because source order may not be chronological in malformed or unusual input.
- Limiting before ordering: rejected because it could discard earlier matching moments.

## Decision: Return Deterministic, Segment-Only Contextual Snippets

For the first match within a matching normalized segment, return a source-text snippet of up to 160 characters centered on that match where surrounding text is available. Prefix and suffix ellipses indicate omitted text; at a segment boundary, include all available text without an ellipsis on that boundary. The result also returns the source-preserving first matching substring and the complete segment timestamps.

**Rationale**: The snippet is concise enough for agent consumption, useful to a researcher, and deterministically testable. It never implies text or timing that the source segment did not provide.

**Alternatives considered**:

- Return the full segment only: rejected because very long caption segments can obscure the matching phrase.
- Return a fixed leading excerpt: rejected because it may omit a late match.
- Build context from adjacent segments: rejected because it would violate the no-cross-segment requirement.

## Decision: Preserve Existing Authorized Retrieval and Safe Error Taxonomy

The search handler validates its own public input before calling the timestamped dependency. It converts that dependency's completed `no_accessible_captions` result to `transcript_unavailable`; preserves `language_unavailable`, authorization, quota, source, and upstream failure categories; and returns an ordinary success with `availability: no_matches` only after a selected transcript is searched successfully.

**Rationale**: Clients need to distinguish “the phrase is absent” from “captions could not be searched.” Existing category serialization and detail sanitization already support the required safe outcomes.

**Alternatives considered**:

- Return no accessible captions as an empty match collection: rejected because it masks a retrievability or permission problem.
- Add a `no_matching_results` error: rejected because no match is an expected successful search outcome.
- Forward lower-layer raw errors or details: rejected because it risks disclosing protected caption and authorization information.

## Decision: Keep the Change Additive and Local

Implement the concrete handler, metadata, descriptor, export, and registration in the established transcript-family paths. Reuse existing protocol category mappings and change them only if contract tests reveal a genuine gap.

**Rationale**: Existing `invalid_parameters`, `language_unavailable`, `authorization_sensitive_data`, `quota_exhaustion`, `source_unavailable`, and `upstream_failure` categories already serialize safely. No new runtime component is needed.

**Alternatives considered**:

- Introduce a new service or generic text-search framework: rejected because a single bounded transcript workflow does not justify it.
- Add storage or caching: rejected because the feature is single-request and has no persistence requirement.

## Dependency Reconciliation

The seed names YT-301 and YT-304. YT-304 provides the transcript-family retrieval foundation, but its concrete result does not carry timestamps. YT-314 is therefore an additional implementation dependency for this feature's timestamp requirement. The dependency is satisfied by the existing concrete timestamped-caption handler; no change to the seed is required.
