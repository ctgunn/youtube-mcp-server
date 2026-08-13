# Research: YT-312 Video Statistics

## Decision: Extend the Existing Composed Videos Family

Implement the concrete public tool in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/videos.py`, using the catalog-reserved public name `videos_getStatistics` and videos-family conventions.

**Rationale**: YT-301 assigns the exact public name to the `videos` family. The existing module already owns executable normalized video detail and search tools, keeping the catalog coherent and avoiding another public-tool seam.

**Alternatives considered**:

- Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/videos.py`: rejected because it provides endpoint-near-raw Layer 2 behavior rather than a normalized Layer 3 workflow.
- Create a new public family or module: rejected because the existing composed videos family is the established ownership boundary.

## Decision: Use One `videos.list` Lookup with `part=statistics`

Validate one `videoId`, then adapt the existing `videos_list` handler with exactly `{"id": "<videoId>", "part": "statistics"}`. Map only the first returned item; do not expose the lower-layer collection envelope.

**Rationale**: The PRD identifies `videos.list` as YT-312's primary dependency. The official `videos.list` method requires `part`, supports `statistics`, and costs one quota unit. The existing lower layer already supplies configured credentials, source execution, and safe error handling. [Official method reference](https://developers.google.com/youtube/v3/docs/videos/list)

**Alternatives considered**:

- Reuse `videos_getVideo` with its optional `statistics` part: rejected because it retrieves unrelated core metadata and returns a different user-facing scope.
- Add a new source client or combine resources: rejected because a single `videos.list` statistics request provides the required data.

## Decision: Normalize Four Expected Metrics and Preserve Source Count Representation

Map only `viewCount`, `likeCount`, `commentCount`, and `favoriteCount` from the source `statistics` group. When source-provided, represent each count as a non-negative decimal value without conversion through floating-point or derived calculations. A source-provided `0` remains an available count.

**Rationale**: Google documents these values as unsigned-long statistics and represents them as decimal strings in JSON. Preserving their representation prevents loss of precision and makes a reported zero distinguishable from an absent value. [Official video resource reference](https://developers.google.com/youtube/v3/docs/videos#resource-representation)

**Alternatives considered**:

- Convert counts to floating-point numbers: rejected because it can lose precision for unsigned-long values.
- Compute additional ratios, rates, or trends: rejected because those are derived analytics outside the requested single-statistics lookup.

## Decision: Represent an Absent Expected Metric as `unavailable`, Not Zero or a Guessed Hidden State

For each expected metric absent from the source statistics object, return a normalized metric entry with `state: "unavailable"` and no `value`. For a source-present count, return `state: "available"`, its preserved value, and source-provided provenance. Do not infer why a standard metric is absent.

**Rationale**: The official resource contract does not provide a per-standard-metric hidden flag. Absence is therefore a no-value state, not evidence of zero or of a specific hidden reason. `status.publicStatsViewable=false` does not mean all standard view and rating counts are hidden. [Official status field reference](https://developers.google.com/youtube/v3/docs/videos#status.publicStatsViewable)

**Alternatives considered**:

- Treat absent values as zero: rejected because it misstates the source data.
- Label every absent value `hidden`: rejected because that asserts a source reason that is not supplied.
- Omit absent keys silently: rejected because clients need to distinguish no data from an incomplete response shape.

## Decision: Exclude Dislikes and Document the Favorite-Count Caveat

Do not include `dislikeCount` in normal results or discovery metadata. Include a source-provided `favoriteCount` when present, but document that the source marks it deprecated and always zero; do not position it as a meaningful engagement measure.

**Rationale**: Google makes `dislikeCount` available only to an authenticated video owner, making it inappropriate for this public normalized statistics contract. Google also documents `favoriteCount` as deprecated and always zero. [Official video resource reference](https://developers.google.com/youtube/v3/docs/videos#resource-representation)

**Alternatives considered**:

- Return dislike count when it happens to be available: rejected because it introduces owner-sensitive behavior into a public standard response.
- Suppress favorite count completely: rejected because the seed and PRD name it as an expected source statistic; retaining it with a clear caveat is more faithful.

## Decision: Reuse Existing Safe Error Mapping

Map an empty lower-layer result and lower `resource_not_found` or `removed` failures to `unavailable_resource`. Map invalid input to `invalid_parameters`, authentication and authorization failures to `authorization_sensitive_data`, quota exhaustion to `quota_exhaustion`, and other failures to `upstream_failure`. Sanitize all public details.

**Rationale**: A single-video tool must distinguish a failed or unavailable lookup from a successful statistics result with unavailable metrics. The existing normalized video-detail tool already uses this safe category mapping. Official errors include video-not-found, authorization, and quota cases; public output must not disclose underlying availability reasons or credentials. [Official error documentation](https://developers.google.com/youtube/v3/docs/errors#videos.list)

**Alternatives considered**:

- Return an empty result for no matching video: rejected because it is ambiguous with retrieved sparse statistics.
- Reveal private, deleted, restricted, or owner-only causes: rejected because those details can be sensitive and are unnecessary for recovery.

## Decision: Use Existing Descriptor, Registration, and Test Seams

Build a concrete descriptor with schema, handler, and safe discovery metadata; export it from the composed package and register it through the default dispatcher with an injected `videos_list` handler. Start with failing unit, contract, integration, and protocol tests, then implement the smallest passing behavior. Add reStructuredText docstrings to every changed or new Python function and test helper.

**Rationale**: This is the repository's established executable Layer 3 delivery pattern. It meets the constitution's contract-first, Red-Green-Refactor, full-suite, integration, safe-operation, and documentation requirements without changing transport or registry architecture.

**Alternatives considered**:

- Retain only a representative catalog descriptor: rejected because YT-312 requires an executable public tool.
- Add a separate registration or routing path: rejected because the dispatcher is already the production discovery and invocation boundary.
