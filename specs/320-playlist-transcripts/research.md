# Research: YT-320 Playlist Video Transcript Aggregation

## Decision: Extend the Concrete Playlists Family

**Decision**: Implement `playlists_getVideoTranscripts` in `src/mcp_server/tools/youtube_composed/playlists.py`, export it through `src/mcp_server/tools/youtube_composed/__init__.py`, and register its executable descriptor through `src/mcp_server/tools/dispatcher.py`.

**Rationale**: The planned catalog assigns the tool to the playlists family, and that family already owns bounded source-order playlist workflows. This gives the feature the established descriptor, injected dependency, safe error, and registration seams.

**Alternatives considered**:

- Implement in the transcripts family: rejected because this feature's public unit is a playlist and requires playlist enumeration and fan-out accounting.
- Build a generic fan-out service: rejected because one bounded workflow does not justify a new abstraction boundary.
- Keep the representative catalog entry only: rejected because YT-320 requires a callable public tool.

## Decision: Use One Bounded Playlist Listing and Timestamped Caption Retrieval

**Decision**: Invoke the existing playlist-item handler once with `part=snippet,contentDetails,status`, the validated `playlistId`, and applied `maxResults`. For every eligible item in the resulting source order, invoke the existing timestamped-caption handler at most once. Do not accept a continuation input or traverse later pages.

**Rationale**: The playlist-item handler already supplies public item identity, availability signals, source order, and a safe next-page indicator. The timestamped-caption handler supplies normalized VTT-derived segments without duplicating caption selection, authorized retrieval, or parsing.

**Alternatives considered**:

- Reuse `transcripts_getTranscript`: rejected because it returns aggregate plain text rather than timestamped segments.
- Call lower-level caption operations directly: rejected because it duplicates authorization, selection, parsing, observability, and safe-error behavior.
- Traverse additional playlist pages: rejected because it would violate the contract that the applied limit bounds both items considered and transcript attempts.

## Decision: Resolve Request Language at the Playlist Boundary

**Decision**: Resolve language once per request in this order: explicit `language`, injected configured `YOUTUBE_TRANSCRIPT_LANG`, then `en`. Validate and normalize the chosen language using the established language-tag behavior, then pass it explicitly to every timestamped-caption call. Return the selected language source at the request and successful-item levels.

**Rationale**: YT-320 requires the YT-304 configured-default-to-English policy and timestamped segments. The existing timestamped-caption tool provides segments but deliberately uses source-default/source-order selection when called without a language. Resolving language at the playlist boundary meets YT-320 without breaking that tool's existing public contract.

**Alternatives considered**:

- Change `transcripts_getTimestampedCaptions` to use the configured default: rejected because it changes an established public behavior for its own callers.
- Duplicate caption track selection and VTT parsing: rejected because it would diverge from the shared timestamped-caption workflow.
- Accept a different-language fallback: rejected because it violates the no-silent-substitution requirement.

## Decision: Make Fan-out Explicit and Preserve Partial Results

**Decision**: Define `maxResults` as both the maximum first-page playlist items considered and the maximum transcript attempts. Default it to 10 and accept whole numbers 1–50. Preserve item order and return one per-item outcome for every considered item. Do not invoke transcript retrieval for a playlist entry already marked unavailable. Include an aggregate fan-out summary with applied limit, considered count, attempt count, counts by status, and `additionalPlaylistItemsNotAttempted` only when the playlist listing safely indicates another page.

**Rationale**: This makes quota, latency, and completeness visible to agents without attempting unbounded work. A single failed or restricted caption retrieval should not erase successful transcripts from other videos.

**Alternatives considered**:

- Fail the whole request on the first unavailable transcript: rejected because playlists commonly have mixed caption availability and the specification requires partial results.
- Drop unavailable playlist entries: rejected because it hides gaps and changes source order.
- Infer additional unattempted items whenever the returned count equals the limit: rejected because only the source continuation signal proves that more items exist.

## Decision: Use a Narrow Safe Error Model at Two Boundaries

**Decision**: Invalid input and playlist enumeration failures are whole-request errors. Map lower playlist errors to `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, or `upstream_failure`. Catch every individual timestamped-caption error and convert it to a source-ordered per-video status: captionless and requested-language failures become `transcript_unavailable`; authorization, quota, source-unavailable, and upstream conditions retain their safe category. Successful no-caption results also become `transcript_unavailable`.

**Rationale**: Callers need both a clear failure when the playlist cannot be evaluated and usable results when only some video captions cannot be retrieved. Existing safe-detail utilities prevent error content from leaking secrets or protected data.

**Alternatives considered**:

- Forward lower-layer error messages and categories directly: rejected because they expose unstable implementation detail and may leak unsafe diagnostics.
- Collapse all per-video failures to unavailable: rejected because clients need to distinguish access, capacity, and retryable source conditions.

## Decision: Reuse Existing Credential, Observability, and Test Seams

**Decision**: Inject the existing API-key-capable playlist-item handler and OAuth-capable timestamped-caption handler through the dispatcher. Retain the registry's request correlation and tool-level observability. Use recording handler doubles for deterministic unit, contract, and registration coverage, then require a full suite and lint pass after implementation.

**Rationale**: The existing dependencies already centralize credentials, outbound request handling, error mapping, and logging. Recording doubles make exact bounds, ordering, partial outcomes, and language forwarding deterministic without exposing credentials or caption content.

**Alternatives considered**:

- Add a new credential or source-client flow: rejected as duplicate complexity.
- Verify only against live captions: rejected because authorization and caption availability are not deterministic.
- Run focused tests only: rejected by the constitution's full-suite requirement.
