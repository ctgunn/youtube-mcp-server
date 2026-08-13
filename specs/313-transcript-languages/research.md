# Research: YT-313 Transcript Language Discovery

## Decision: Extend the Existing Concrete Transcript Family

Implement `transcripts_listLanguages` in `src/mcp_server/tools/youtube_composed/transcripts.py`, export its public builders through `src/mcp_server/tools/youtube_composed/__init__.py`, and register its descriptor in `src/mcp_server/tools/dispatcher.py`.

**Rationale**: The transcript-family module already provides the concrete Layer 3 seam and YT-304 establishes its descriptor, dependency injection, safe error, and registration patterns. This tool is a normalized composition, not a near-raw Layer 2 endpoint.

**Alternatives considered**:

- Create a separate transcript-language service: rejected because one bounded read does not justify another abstraction boundary.
- Expose only `captions_list`: rejected because clients need a stable, research-oriented language-discovery contract rather than a near-raw endpoint result.
- Add a new transcript provider: rejected because the PRD identifies `captions.list` as the primary dependency and an alternative would need a separate source and provenance policy.

## Decision: Use One Authorized Official Caption Listing

Call the existing `captions.list` handler once with `part: snippet` and the trimmed requested video identifier. The normal lookup uses 50 documented caption quota units and requires eligible OAuth access. No caption download is performed.

**Rationale**: The existing lower-layer handler supplies credential attachment, upstream error normalization, and request observability. One list operation is the simplest bounded composition that meets the slice scope.

**Alternatives considered**:

- Call a Layer 1 wrapper or HTTP client directly: rejected because it bypasses established validation, authentication, errors, and observability.
- Call `captions.download`: rejected because the feature is discovery-only and must not return caption content.
- Read a transcript-language configuration or apply English fallback: rejected because discovery must report source options, not select one.

## Decision: Preserve One Option per Returned Source Track

Map every returned caption item into one language option in source order. Preserve its source `language`, source identifier when supplied, and only allowed source metadata needed to distinguish or select a track, including name, status, track kind, draft state, or automatic-sync state when present. Do not deduplicate languages, rank tracks, infer a language, fabricate an identifier, or expose unapproved raw fields.

**Rationale**: Several tracks can use the same language and callers need an actionable selection record. Explicit provenance lets agents distinguish source facts from normalized presentation.

**Alternatives considered**:

- Return one distinct language only: rejected because it loses same-language track choice and metadata.
- Select the preferred track as YT-304 does: rejected because language discovery must expose options before a caller chooses one.
- Copy all source objects: rejected because it would leak upstream complexity and potentially unsafe or irrelevant fields.

## Decision: Treat a Completed Empty Listing as a Successful Discovery Result

When the authorized caption listing completes with no returned items, return `languageOptions: []` and `availability: no_accessible_languages`. A source resource-not-found, endpoint-unavailable, or other failed listing is not treated as a successful empty result.

**Rationale**: A client must distinguish no accessible language options from an inability to determine options. This satisfies the feature's no-accessible-languages behavior without misrepresenting a source failure as absence.

**Alternatives considered**:

- Treat every absent-looking result as empty success: rejected because permission and service failures would become indistinguishable.
- Return a failure for an empty completed list: rejected because no accessible tracks is a valid discovery outcome.

## Decision: Use Narrow Safe Failure Categories

Map public validation failures to `invalid_parameters`; caption authentication and authorization failures to `authorization_sensitive_data`; quota failures to `quota_exhaustion`; unavailable caption endpoint to `source_unavailable`; and other lower-layer failures, including source resource unavailability, to `upstream_failure`. Sanitize any error detail before exposing it.

**Rationale**: These categories give callers distinct recovery actions while retaining the safe, established Layer 3 error style. A new `source_unavailable` category makes endpoint availability distinguishable from an unexpected upstream failure as the feature requires.

**Alternatives considered**:

- Forward lower-layer categories and messages: rejected because they leak implementation detail and may reveal unsafe diagnostics.
- Report authorization or endpoint failure as no accessible languages: rejected because it is a misleading discovery result.
- Collapse all source issues into one error: rejected because quota, known endpoint availability, and unexpected failure have different recovery behavior.

## Decision: Validate With Deterministic Doubles, Then Full Repository Coverage

Use injected recording caption-list handlers to prove argument validation, exactly one composition call, ordering, source metadata, empty results, and safe errors. Complete with full repository pytest and Ruff checks; credential-gated live smoke behavior remains separate from deterministic feature tests.

**Rationale**: Controlled results accurately exercise permission-sensitive behavior without credentials or source mutations. The constitution requires Red-Green-Refactor, integration coverage, reStructuredText docstrings, and a final full-suite run.

**Alternatives considered**:

- Test only against a live account: rejected because authorization and source contents are nondeterministic and cannot cover safe failures reliably.
- Run focused tests only: rejected because the constitution requires final full-repository evidence.
