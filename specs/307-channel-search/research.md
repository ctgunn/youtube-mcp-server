# Research: YT-307 Channel Search

## Decision: Extend the Existing Concrete Channels Family

Implement `channels_searchChannels` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, export its public builder and support symbols through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`, and register its descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

**Rationale**: The existing channels family already owns normalized public channel profiles, provenance, creator classification, safe errors, injected lower-layer handlers, and concrete descriptor patterns. This keeps the public tool coherent with `channels_getChannel` and `channels_getChannels`.

**Alternatives considered**:

- Create a generic cross-family composed-search service: rejected because this one channels-family workflow does not justify a new abstraction or project boundary.
- Add the behavior to the lower-level public search tool: rejected because this workflow normalizes, enriches, filters, and ranks across resource boundaries.
- Retain a representative-only descriptor: rejected because YT-307 requires an executable public MCP tool.

## Decision: Add Narrow `channelType` Support Through Existing Search Contracts

Add `channelType` as an optional `search.list` field in the Layer 1 search request shape, Layer 2 search schema and validation, and associated lower-layer metadata/tests. Accept only `any` and `show`, preserve it in the public request, and use it only with channel search from this composed tool.

**Rationale**: `channelType` is a required YT-307 public input, but the existing lower-level search boundary currently rejects it. Passing it through the established contract preserves request execution, credential injection, safe errors, and observability without a direct integration bypass.

**Alternatives considered**:

- Ignore `channelType`: rejected because it violates the published feature contract.
- Call the upstream integration directly from the composed tool: rejected because it duplicates or bypasses existing validation, auth, observability, and error behavior.
- Add a broad new generic filter mechanism: rejected because one optional field only needs an additive, backward-compatible extension.

## Decision: Retrieve Base Channel Candidates Through the Lower-Level Search Tool

Build the base request from `part=snippet`, the normalized `query`, `type=channel`, the selected `maxResults`, optional `order`, and optional `channelType`. Normalize only results with a non-empty `id.channelId`, retain the original base-search position internally, and retain the earliest position when de-duplicating a repeated channel.

**Rationale**: The existing search tool provides the supported public-search path, safe error behavior, and source continuation information. Restricting it to channels fulfills the feature scope without duplicating lower-layer request logic.

**Alternatives considered**:

- Use channel details to perform the query search: rejected because it retrieves known identifiers rather than searching a query.
- Fetch multiple source pages or over-fetch beyond the public limit: rejected because the published contract bounds candidates and does not define result-level pagination after composite ranking.

## Decision: Conditionally Enrich with Batched Public Channel Metadata

When a subscriber filter, `creatorOnly`, or non-relevance ranking needs channel metadata, request the distinct candidate identifiers together with public profile, statistics, and uploads-playlist information. Treat hidden or unavailable subscriber counts as unknown, never as zero or a fabricated value.

**Rationale**: One bounded batch lookup avoids per-candidate channel requests while providing the public data needed to evaluate active rules. Unknown data cannot safely satisfy a numeric filter or ranking rule.

**Alternatives considered**:

- Enrich every candidate unconditionally: rejected because a query-only search does not need the added quota cost or partial-result risk.
- Treat hidden subscriber counts as zero: rejected because it creates false filtering and ranking outcomes.
- Make one channel request per candidate: rejected because a single bounded batch is simpler and less costly.

## Decision: Derive Latest Public Activity Only When an Activity Rule Requires It

For `lastUploadAfter`, `lastUploadBefore`, or `sortBy=recent_activity`, read at most one public item from each enriched candidate channel's uploads playlist and normalize its publication time as `latestVideoPublishedAt`. Do not make these reads when no activity rule is active.

**Rationale**: A channel profile does not itself supply one definitive latest-upload timestamp. Its public uploads playlist supports a bounded, channel-wide activity lookup and avoids mistaking a query-specific search result for channel-wide activity.

**Alternatives considered**:

- Use only channel profile data: rejected because it cannot provide the required activity timestamp.
- Use the newest base-query result: rejected because query relevance does not establish channel-wide recent activity.
- Always read uploads playlists: rejected because it needlessly increases quota consumption and partial-result risk.

## Decision: Reuse Conservative Channel-Family Creator Classification

Use the existing channel-family public-signal classifier: classify a channel as `creator` only with positive creator signals and no conflicting brand signal; classify conflicting or insufficient public information as `unknown`. `creatorOnly=true` accepts only `creator`.

**Rationale**: The helper already gives the channels family consistent `creator`, `brand`, and `unknown` behavior. Its conservative positive-only rule avoids presenting an inference as verified identity, ownership, or independence.

**Alternatives considered**:

- Treat classification as raw source data: rejected because it is a heuristic.
- Treat incomplete data as creator evidence: rejected because it makes `creatorOnly` misleading.
- Introduce a new shared classifier now: rejected because the existing channels-family helper already meets this feature and no additional shared consumer is required.

## Decision: Filter, Rank, Then Cap with Stable Ties

Use this pipeline: validate and normalize; retrieve and de-duplicate base candidates; conditionally enrich; exclude candidates missing data required by an active rule; apply all selected filters; apply final ranking; cap at `maxResults`. Each ranking tie preserves original base-search position.

**Rationale**: This prevents unavailable data from silently satisfying a request, maintains documented relevance behavior, and gives clients deterministic results.

**Alternatives considered**:

- Cap before filtering or ranking: rejected because qualifying later candidates could be omitted.
- Use arbitrary mapping order as a tie-breaker: rejected because public tool behavior must be deterministic.
- Return unfiltered candidates after enrichment failure: rejected because that would violate active refinement or ranking rules.

## Decision: Preserve Base Search Context While Disclosing Composite Limits

Return source continuation information only as base-search continuation context, not as a guarantee of pagination over the final ranked collection. A base-search result with no matches or no qualifying candidates is a successful empty collection. When some candidates cannot be evaluated for an active data-dependent rule, expose a safe aggregate partial-enrichment summary; when none can be evaluated, return `partial_enrichment_failure`.

**Rationale**: Composite filtering and ranking alter the base collection, so a source continuation token cannot promise final-result pagination. Aggregate partial disclosure maintains usefulness while accurately describing completeness.

**Alternatives considered**:

- Present the source token as a final-result page token: rejected because it would misrepresent pagination semantics.
- Fail the entire request on the first unavailable candidate: rejected because other valid candidates may remain.
- Suppress partial status: rejected because callers need to judge whether active rules were fully evaluated.

## Decision: Reuse Existing Safe Error and Observability Boundaries

Map lower-layer failures to the existing Layer 3 safe categories, sanitize diagnostic details, and reuse configured lower-layer execution and dispatcher instrumentation. Existing protocol mapping already covers the feature's public categories; add regression coverage rather than duplicate protocol mappings unless new evidence exposes a gap.

**Rationale**: The public contract requires stable machine-readable categories without credentials, tokens, stack traces, raw payloads, signed URLs, or private owner data. Existing lower-layer execution retains request correlation and safe operational signals.

**Alternatives considered**:

- Expose lower-layer error text or categories directly: rejected because it leaks implementation contracts and potentially unsafe detail.
- Add a separate telemetry system: rejected because existing lifecycle instrumentation already provides the required observability.

## Decision: Validate Through Red-Green-Refactor and the Full Suite

Write failing tests first for the supporting search field, public input normalization, candidate behavior, enrichment, filtering, ranking, partial results, metadata, registration, and error serialization. Complete with the full repository test suite and lint after all feature changes.

**Rationale**: This meets the constitution's non-negotiable contract-first, Red-Green-Refactor, integration, regression, docstring, security, and full-suite requirements.

**Alternatives considered**:

- Test handler behavior only: rejected because discovery, registration, lower-layer contract, and protocol serialization are external boundaries.
- Test only against live data: rejected because controlled candidates are needed to prove filters, ties, and safe partial states.
- Run focused tests only: rejected because the constitution requires full repository regression evidence.
