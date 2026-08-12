# Research: YT-308 Creator Discovery

## Decision: Compose public video search, channel lookup, and uploads-playlist activity lookup

**Rationale**: Creator discovery begins with videos that match the caller's topic, then groups those videos by their public channel identity. Existing `search_list`, `channels_list`, and `playlist_items_list` handlers already provide the necessary boundaries, safe error mapping, injected-test seams, and request observability. The composed channels family already implements conservative public creator classification, latest-activity derivation, ranking, and partial-enrichment conventions.

**Alternatives considered**:

- Call `videos_searchVideos`: rejected because creator discovery must group raw topic-matching videos by channel and retain their per-channel sample order.
- Add a direct YouTube client in the composed tool: rejected because it would bypass established authentication, quota, error, and observability boundaries.
- Persist candidate state: rejected because one request's bounded candidate set needs no durable state.

## Decision: Fetch up to 50 base videos independently of the final channel limit

**Rationale**: `maxResults` caps final returned channels, not source evidence. A request for one channel and two samples still requires collecting multiple matching videos. A fixed maximum of 50 aligns with existing public result limits and bounds all grouping and enrichment fan-out.

**Alternatives considered**:

- Fetch only `maxResults` videos: rejected because repeated videos from one channel could hide later channels and cannot satisfy per-channel sample requests.
- Fetch until enough distinct channels or samples are found: rejected because dynamic fan-out obscures quota behavior and is harder to bound deterministically.
- Fetch an unbounded result set: rejected because it violates the feature's boundedness and latency constraints.

## Decision: Reuse existing public-only enrichment and ranking semantics

**Rationale**: `channels_searchChannels` already establishes public subscriber, latest-upload, creator-only, `sortBy`, tie-break, and partial-enrichment behavior. Reusing those rules keeps the public catalog consistent: filters run before ranking; `relevance` retains base-search order; ties use earliest base position; unavailable required data excludes rather than qualifies a candidate.

**Alternatives considered**:

- Treat a matched video as latest channel activity: rejected because it does not prove the channel has no newer upload and conflicts with the specified latest-upload semantics.
- Treat missing subscriber counts as zero: rejected because hidden or unavailable data must not satisfy a filter or rank.
- Use a different creator classifier: rejected because inconsistent creator/brand labels would make sibling Layer 3 tools disagree.

## Decision: Include samples only for final candidates and preserve base-video order

**Rationale**: Samples are topical evidence, not another ranking input. Grouping preserves every channel's matched videos in base-video order; after filtering/ranking/final capping, each final channel exposes at most `sampleVideosPerChannel` samples from that ordered group. The default of zero keeps ordinary results compact.

**Alternatives considered**:

- Select latest or highest-view samples: rejected because it would conflict with the documented relevance/order basis and needs extra source data or rules.
- Include samples before final filtering and ranking: rejected because it wastes work and could expose evidence for channels that are not returned.
- Return all matching videos: rejected because it exceeds a bounded creator-discovery result and duplicates the channel-video listing workflow.

## Decision: Preserve safe aggregate partial-enrichment outcomes

**Rationale**: If a selected filter or non-relevance ranking needs unavailable public data, excluding that candidate prevents misleading results. The response gives only aggregate counts, safe reason categories, and active rules; if every candidate is unevaluable, it returns `partial_enrichment_failure` rather than unfiltered substitutes.

**Alternatives considered**:

- Return unfiltered candidates with a warning: rejected because clients could mistake them for qualifying results.
- Return raw lower-layer errors: rejected because they can disclose unsafe diagnostics and violate the MCP-safe error contract.
- Fail every request on one unavailable candidate: rejected because safely partial results retain useful qualifying public data.
