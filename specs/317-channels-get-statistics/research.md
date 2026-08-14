# Research: YT-317 Channel Statistics

## Decision: Extend the Existing Composed Channels Family

Implement the concrete public tool in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`, using the catalog-reserved public name `channels_getStatistics` and channels-family conventions.

**Rationale**: YT-301 assigns the exact public name to the `channels` family. The existing module already owns executable normalized channel detail, batch detail, listing, search, and discovery tools, preserving the public catalog's ownership boundary.

**Alternatives considered**:

- Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`: rejected because it provides endpoint-near-raw Layer 2 behavior rather than a normalized Layer 3 workflow.
- Create a new public family or module: rejected because the existing composed channels family is the established ownership boundary.

## Decision: Use One `channels.list` Lookup with `part=statistics`

Validate one `channelId`, then adapt the existing `channels_list` handler with exactly `{"id": "<channelId>", "part": "statistics"}`. Map only the first returned item; do not expose the lower-layer collection envelope.

**Rationale**: The PRD identifies `channels.list` as YT-317's primary dependency. The existing lower layer accepts this public ID selector and statistics part, applies the configured public credential path, preserves the source item, and records the one-unit source cost. [Official method reference](https://developers.google.com/youtube/v3/docs/channels/list)

**Alternatives considered**:

- Reuse `channels_getChannel`: rejected because it retrieves profile and enrichment data outside this focused statistics scope.
- Add a new source client or combine resources: rejected because a single channel statistics lookup supplies the required data.

## Decision: Normalize Three Expected Metrics and Preserve Source Count Representation

Map only `subscriberCount`, `videoCount`, and `viewCount` from the source `statistics` group. When source-provided, represent each count as a non-negative decimal value without floating-point conversion or derived calculations. A source-provided `0` remains an available count.

**Rationale**: The channel resource documents these values as unsigned-long statistics. Preserving their representation avoids precision loss and keeps a reported zero distinguishable from hidden or unavailable data. The source documents `subscriberCount` as rounded down to three significant figures, `videoCount` as public videos only, and `viewCount` as including Shorts starts and replays from March 31, 2025. [Official channel resource reference](https://developers.google.com/youtube/v3/docs/channels#statistics)

**Alternatives considered**:

- Convert counts to floating-point numbers: rejected because it can lose precision for unsigned-long values.
- Compute additional ratios, rates, trends, or unrounded estimates: rejected because they are derived analytics outside the requested single-statistics lookup.

## Decision: Use `hidden` Only for a Source-Flagged Subscriber Count

When `hiddenSubscriberCount` is `true`, represent `subscriberCount` as `state: "hidden"` with no `value`, even if an inconsistent payload also contains a count. When it is not true and the subscriber count is a valid source value, represent the metric as available. For missing or malformed subscriber data and for missing or malformed video or view data, use `state: "unavailable"` with no `value`. Do not expose the raw flag.

**Rationale**: The channel resource explicitly defines `hiddenSubscriberCount` as whether the subscriber count is publicly visible. It supplies no equivalent hiddenness indicator for view or video counts. Giving the explicit subscriber flag precedence protects callers from an inconsistent source payload while avoiding invented reasons for missing data. [Official channel resource reference](https://developers.google.com/youtube/v3/docs/channels#statistics)

**Alternatives considered**:

- Treat all absent metrics as hidden: rejected because the source supplies no hiddenness reason for video or view metrics.
- Return a source count whenever it is present despite `hiddenSubscriberCount=true`: rejected because it conflicts with the source's public-visibility declaration.
- Omit hidden or unavailable keys silently: rejected because clients must distinguish non-reported metrics from an incomplete result shape.

## Decision: Reuse Existing Safe Error Mapping

Map an empty lower-layer result and lower `resource_not_found` or `removed` failures to `unavailable_resource`. Map invalid input to `invalid_parameters`, authentication and authorization failures to `authorization_sensitive_data`, quota exhaustion to `quota_exhaustion`, and other failures to `upstream_failure`. Sanitize all public details.

**Rationale**: A single-channel tool must distinguish a failed or unavailable lookup from a successful channel result with hidden or unavailable metrics. The existing composed channels family already maps lower-layer categories through this safe public taxonomy and shared sanitization.

**Alternatives considered**:

- Return an empty result for no matching channel: rejected because it is ambiguous with a retrieved channel whose counts are unavailable.
- Reveal deleted, suspended, restricted, or owner-only causes: rejected because those details can be sensitive and are unnecessary for recovery.

## Decision: Use Existing Descriptor, Registration, and Test Seams

Build a concrete descriptor with schema, handler, and safe discovery metadata; export it from the composed package and register it through the default dispatcher with an injected `channels_list` handler. Start with failing unit, contract, integration, and protocol tests, then implement the smallest passing behavior. Add reStructuredText docstrings to every changed or new Python function and test helper.

**Rationale**: This is the repository's established executable Layer 3 delivery pattern. It meets the constitution's contract-first, Red-Green-Refactor, full-suite, integration, safe-operation, and documentation requirements without changing transport or registry architecture.

**Alternatives considered**:

- Retain only a representative catalog descriptor: rejected because YT-317 requires an executable public tool.
- Add a separate registration or routing path: rejected because the dispatcher is already the production discovery and invocation boundary.
