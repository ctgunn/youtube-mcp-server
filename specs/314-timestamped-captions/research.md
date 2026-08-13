# Research: YT-314 Timestamped Caption Retrieval

## Decision: Extend the Existing Concrete Transcript Family

Implement `transcripts_getTimestampedCaptions` in `src/mcp_server/tools/youtube_composed/transcripts.py`, export its public builders through `src/mcp_server/tools/youtube_composed/__init__.py`, and register its descriptor in `src/mcp_server/tools/dispatcher.py`.

**Rationale**: The transcript-family module already contains concrete Layer 3 transcript composition and has the injected caption-list/download, safe-error, metadata, export, and dispatcher-registration seams needed by this tool. The feature is a normalized two-operation composition, not a direct Layer 2 resource exposure.

**Alternatives considered**:

- Create a separate transcript or VTT service: rejected because the bounded one-track composition does not justify a new abstraction boundary.
- Implement the capability in Layer 2: rejected because Layer 2 exposes near-raw caption operations, while this tool selects a track and returns normalized segments.
- Leave a representative catalog entry only: rejected because the slice requires an executable public tool.

## Decision: Use the Existing Authorized Official Caption Flow

Call `captions.list` once with `part: snippet` and the requested video, select at most one usable returned track, then call `captions.download` once with `tfmt: vtt`. A normal successful flow uses 50 caption-list plus 200 caption-download quota units before retries. Both operations require eligible OAuth access, and downloading additionally requires permission for the associated video.

**Rationale**: Caption-list responses expose track metadata rather than caption content, while the download operation provides a timing-capable VTT representation. Reusing existing lower-layer handlers keeps authentication, observability, validation, and upstream-error normalization consistent. [Official caption list reference](https://developers.google.com/youtube/v3/docs/captions/list), [official caption download reference](https://developers.google.com/youtube/v3/docs/captions/download).

**Alternatives considered**:

- Call an integration wrapper or HTTP client directly: rejected because it bypasses established lower-layer contracts.
- Add a public or third-party transcript fallback: rejected because the feature contract requires an explicit access policy and does not authorize another source or provenance model.
- Download a non-timing caption representation: rejected because the public output requires cue timing.

## Decision: Parse VTT Into One Segment Per Source Cue

Decode downloaded VTT text or bytes as UTF-8; recognize cue identifiers and cue timing lines; convert `MM:SS.mmm` and `HH:MM:SS.mmm` start/end values into non-negative elapsed seconds; decode entities and remove cue markup from text; and return one segment for each source cue in source order. Preserve overlapping, adjacent, and blank-text cues. Treat undecodable, malformed, or incomplete cue timing as `upstream_failure` and return no partial result.

**Rationale**: VTT defines explicit cue timing and payloads. Preserving those boundaries fulfills the caller's need to relate content to the timeline without fabricating a new segmentation. [WebVTT specification](https://www.w3.org/TR/webvtt1/).

**Alternatives considered**:

- Reuse the complete-text parser: rejected because it deliberately removes timing and merges cue text.
- Return raw VTT: rejected because agents need stable text and numeric timing fields, not source-format parsing.
- Merge same-line, adjacent, or overlapping cues: rejected because it changes source segment granularity and may distort the timeline.

## Decision: Select One Usable Track Without Other-Language Fallback

For an explicit `language`, normalize and exact-match its language tag against usable source tracks; absence of an exact match returns `language_unavailable` without downloading a different language. With no explicit language, use a source-designated default usable track only when the source returns a documented default indicator; otherwise choose the first usable source track in completed source order. Exclude failed tracks and report the selected language and selection source.

**Rationale**: The feature specification requires deterministic selection and prohibits substituting another language. The official caption resource exposes BCP-47 language and track status but does not require a default-track field, so source order is the defined fallback when no documented indicator is present. [Official caption resource reference](https://developers.google.com/youtube/v3/docs/captions).

**Alternatives considered**:

- Use configured language then English fallback from `transcripts_getTranscript`: rejected because this feature's approved specification instead defines source-default/source-order behavior when the caller omits language.
- Base-language matching such as choosing `en-GB` for `en`: rejected because it can return a materially different language variant without caller consent.
- Translate during download: rejected because it obscures source-language provenance and violates the no-substitution contract.

## Decision: Distinguish Completed Absence, Access, and Source Failures Safely

Map malformed public input to `invalid_parameters`; a completed empty listing without an explicit language to successful `no_accessible_captions`; an explicit language without a usable exact match to `language_unavailable`; authentication or authorization failures to `authorization_sensitive_data`; quota exhaustion to `quota_exhaustion`; known endpoint unavailability to `source_unavailable`; and malformed VTT or other unexpected source failures to `upstream_failure`. Sanitize every exposed diagnostic detail.

**Rationale**: Callers need different recovery actions for absence, language mismatch, restricted access, capacity, and retryable failures. Existing transcript-family safe-error utilities prevent raw VTT, credentials, tokens, raw response bodies, protected track details, and traces from escaping.

**Alternatives considered**:

- Treat empty listings and access failures alike: rejected because that would falsely claim captions are absent.
- Forward lower-layer categories or messages: rejected because they expose implementation detail and may leak unsafe diagnostics.
- Return partial parsed segments after a malformed cue: rejected because clients could mistake incomplete content for a complete track.

## Decision: Use Deterministic Doubles and Finish With Full-Suite Evidence

Use injected recording caption-list and caption-download handlers to prove public validation, bounded calls, selection, cue parsing, timing, and safe failures. Complete with the repository pytest and Ruff commands; any credential-gated live check remains separate from deterministic feature coverage.

**Rationale**: Controlled results can exercise access-sensitive and malformed-content paths without credentials or source mutations. The constitution requires Red-Green-Refactor, integration coverage, reStructuredText docstrings, and a final full-repository test run.

**Alternatives considered**:

- Test only a live account: rejected because source contents and permissions are nondeterministic.
- Run only focused tests: rejected because the constitution requires final full-repository evidence.
