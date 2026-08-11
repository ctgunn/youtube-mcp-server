# Research: YT-303 Video Search with Channel Refinement

## Decision: Extend the Existing Concrete Videos Family

Implement `videos_searchVideos` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, alongside `videos_getVideo`. Export its public builder and support symbols through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and register its descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

**Rationale**: YT-302 already establishes this as the concrete Layer 3 videos-family seam, including injectable lower-layer handlers, safe error objects, discovery metadata, and registry integration. The existing family scaffolding already plans `videos_searchVideos`.

**Alternatives considered**:

- Create a new generic composed-search service: rejected because one videos-family workflow does not justify a new abstraction or project boundary.
- Add the behavior to Layer 2 `youtube_common`: rejected because this workflow normalizes, enriches, filters, and ranks across resource boundaries rather than exposing one near-raw endpoint.
- Leave a representative-only descriptor in the shared contract catalog: rejected because YT-303 requires an executable public tool.

## Decision: Use Layer 2 `search_list` for Base Video Retrieval

Build the base request with `part=snippet`, `q=query`, `type=video`, the validated final-limit value, and any selected base order, publication window, or channel ID. Normalize the returned video references and snippets into stable public video candidates while retaining base-search position only for internal deterministic ties.

**Rationale**: `search_list` already provides API-key public-search handling, safe errors, pagination information, and a Layer 2 contract. Restricting its request to videos satisfies the public tool's scope without duplicating lower-layer logic.

**Alternatives considered**:

- Call an integration wrapper or HTTP client directly: rejected because it bypasses the required Layer 2 interface, auth, observability, and error behavior.
- Use `videos_list` to perform the base query: rejected because it retrieves known video IDs and cannot perform the required query search.

## Decision: Batch Channel Metadata Enrichment and Treat Hidden Values as Unknown

When an active subscriber filter, `creatorOnly`, or metadata-dependent sort requires it, collect distinct candidate channel IDs and call `channels_list` with `part=snippet,statistics,contentDetails` and the public `id` selector. Read subscriber count only when present; a hidden or unavailable count is unknown, never zero or a fabricated value.

**Rationale**: `channels_list` is the existing public dependency for public channel metadata and supports a comma-separated ID selector, avoiding a per-candidate channel request. Unknown data cannot safely be used to pass a numeric filter or rank.

**Alternatives considered**:

- Enrich every base candidate unconditionally: rejected because query-only and `uniqueChannels` workflows do not need the additional cost or partial-result risk.
- Treat hidden subscriber counts as zero: rejected because it would create false filter and ranking results.
- Perform one channel request per candidate: rejected because batched IDs are simpler, cheaper, and still bounded.

## Decision: Derive Latest Public Upload Activity from the Conditional Uploads Playlist

For `channelLastUploadAfter`, `channelLastUploadBefore`, or `sortBy=recent_activity`, use the uploads-playlist ID exposed through the enriched channel's public `contentDetails.relatedPlaylists.uploads` metadata. Make one bounded `playlist_items_list` request per distinct candidate channel with `part=contentDetails` and `maxResults=1`, then normalize the first item's `videoPublishedAt` as `latestVideoPublishedAt`. Do not make these requests when no latest-upload rule is selected.

**Rationale**: `channels.list` does not supply a channel-wide latest-upload timestamp, but it supplies the public uploads-playlist ID needed for a bounded lookup. This avoids incorrectly treating query-dependent `search.list` results as a channel-wide activity source. The activity value is therefore derived from a public uploads playlist and must be marked normalized/enrichment-derived, not raw channel metadata.

**Alternatives considered**:

- Use only `channels.list`: rejected because it cannot provide the required latest-upload timestamp.
- Use a date-ordered `search.list` request: rejected because the existing Layer 2 search contract requires the public query input and a query-dependent result cannot reliably represent channel-wide activity.
- Use the newest base-query result as latest activity: rejected because query relevance does not establish channel-wide activity.

## Decision: Use a Conservative, Disclosed Creator Classification

Introduce a deterministic helper in the videos-family implementation that classifies a channel as `creator` only when available public channel metadata supplies positive, documented creator signals. Otherwise classify the candidate as `unknown`; `creatorOnly=true` admits only `creator`. Expose the classification and its public-metadata basis as `heuristic_inferred`, with an explicit limitation that it can be incomplete or incorrect.

**Rationale**: YT-301 provides the required disclosure model but deliberately does not provide concrete execution behavior. A conservative positive-only classification avoids inventing a brand identity or treating missing metadata as evidence.

**Alternatives considered**:

- Present creator classification as raw source metadata: rejected because it is an inference.
- Treat all channels as creators when metadata is incomplete: rejected because it defeats `creatorOnly`.
- Add a cross-family classifier immediately: rejected because reuse by another concrete tool has not yet been demonstrated; extract only when a second user exists.

## Decision: Apply Filter, Rank, De-duplicate, Then Cap in a Stable Order

Use this pipeline: validate input; retrieve base candidates; conditionally enrich; exclude candidates missing data required by an active filter or non-relevance rank; apply filters; rank; when `uniqueChannels=true`, retain the first ranked result for each channel; then cap results to `maxResults`. Every tie uses original base-search position.

**Rationale**: This order gives `uniqueChannels=true` the highest-ranked eligible video per channel, preserves relevance when requested, and produces deterministic output.

**Alternatives considered**:

- De-duplicate before ranking: rejected because it can discard the highest-ranked video from a channel.
- Cap before filtering/ranking: rejected because qualifying candidates later in the base result set would be missed.
- Use arbitrary map iteration as a tie-breaker: rejected because exposed tool behavior must be deterministic.

## Decision: Preserve Successful Base Search While Disclosing Partial Enrichment

When base search succeeds, retain a candidate with unavailable enrichment only if no selected filter or ranking requires the missing datum. Exclude candidates that cannot be evaluated for an active metadata-dependent rule and return safe aggregate partial-enrichment disclosure. If every candidate requiring enrichment is unavailable, produce a safe `partial_enrichment_failure` MCP error rather than returning unfiltered results.

**Rationale**: This preserves useful query-only results while preventing an unverified candidate from appearing to satisfy an active channel filter or ranking.

**Alternatives considered**:

- Fail the entire search on the first missing enrichment record: rejected because a remaining candidate set may still be valid and useful.
- Return unfiltered candidates after enrichment failure: rejected because it violates the selected filter/rank contract.
- Suppress partial status entirely: rejected because callers need to judge result completeness.

## Decision: Extend Protocol Error Mapping Additively

Add tests and additive mapping for Layer 3 safe categories used by this tool so protocol serialization produces an MCP numeric error and stable category data. Reuse safe upstream messages and sanitized details from existing conventions.

**Rationale**: Existing protocol mapping is incomplete for categories such as `invalid_parameters`, `partial_enrichment_failure`, and `unsupported_filter_or_sort`; an unmapped category currently risks an internal mapping failure instead of the caller-safe outcome promised by the feature.

**Alternatives considered**:

- Raise Layer 2 category names from the composed tool: rejected because it leaks lower-layer contract terms into the Layer 3 contract.
- Return arbitrary text errors: rejected because MCP clients need stable machine-readable categories.
- Leave categories unmapped until a later feature: rejected because this feature itself advertises them.

## Decision: Validate Through Red-Green-Refactor and the Full Suite

Write failing unit tests first for input normalization, mapping, filters, ranking, de-duplication, and partial results; contract tests for descriptor/metadata/provenance/error disclosure; integration tests for injected composition and default registration; and protocol regression tests for public error serialization. Final evidence is `python3 -m pytest` and `ruff check .` after all changes.

**Rationale**: This follows the constitution's non-negotiable Red-Green-Refactor, contract-first, integration, docstring, and full-suite obligations.

**Alternatives considered**:

- Test only direct handler behavior: rejected because registry and MCP error serialization are external contract boundaries.
- Test only against live YouTube data: rejected because deterministic controlled candidates are necessary to prove filters, ties, and partial states.
- Run only focused tests: rejected because the constitution requires full repository regression evidence.
