# Research: YT-309 Channel Video Listing

## Decision: Extend the existing concrete channels family

**Decision**: Add the public descriptor, handler, validation, item normalization, and error-mapping behavior to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`; export it through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`; and register it through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

**Rationale**: The shared Layer 3 catalog assigns `channels_listVideos` to the channels family, which already owns executable channel tools, lower-layer dependency injection, normalized result shaping, provenance, and safe public errors.

**Alternatives considered**:

- Add the behavior to the near-raw `playlist_items_list` tool: rejected because callers provide a channel identifier and need a stable higher-level channel-video contract.
- Create a new service or source client: rejected because existing handlers provide required request execution, configuration, observability, and error behavior.
- Place the tool in the videos family: rejected because the public operation starts with channel identity and belongs to its declared catalog family.

## Decision: Use the public uploads collection rather than ranked search

**Decision**: Resolve the requested channel's public uploads collection, then list its items. The public contract states that results use the collection's observed order at request time and do not apply query matching, relevance ranking, or another reordering heuristic.

**Rationale**: The PRD explicitly permits this path for deterministic exhaustive channel listing. It is channel-wide and query-independent, unlike search results whose order and coverage are driven by discovery ranking.

**Alternatives considered**:

- Use channel-scoped search: rejected because its ranked/discoverability behavior conflicts with the selected source-ordered listing contract.
- Combine search and uploads collection: rejected because it adds quota, ambiguity, and scope without improving this known-channel listing workflow.
- Directly list playlist items using the channel identifier: rejected because a channel identifier is not an uploads-collection identifier.

## Decision: Bound each request to one channel lookup and one collection listing

**Decision**: First request the one channel's public collection reference, then make at most one playlist-item list request with `part=snippet,contentDetails`, that uploads-collection identifier, and the validated `maxResults`. Public `maxResults` defaults to 10 and accepts only whole numbers 1 through 50.

**Rationale**: The lower-layer channel lookup provides the collection reference, and the playlist-item handler supplies the public collection in source order. The fixed two-read upper bound keeps latency, quota, and failure behavior predictable.

**Alternatives considered**:

- Over-fetch multiple source pages: rejected because the feature accepts no continuation input and explicitly limits the current response.
- Fetch individual video details after listing: rejected because item enrichment is outside this slice and would add fan-out.
- Pass through zero as a list limit: rejected because the feature contract requires a useful 1–50 public range.

## Decision: Preserve order, de-duplicate before final cap, and expose only available public fields

**Decision**: Iterate lower-layer playlist items in returned order without sorting; extract a nonblank video identifier; retain the first occurrence of each identifier; then apply the final cap. Return the video identifier plus any available title, description, publication time, and thumbnails, without fabricating absent values.

**Rationale**: This meets the source-order and distinct-item requirements while giving deterministic handling if a source collection contains repeated usable video references.

**Alternatives considered**:

- Sort by publication timestamp: rejected because timestamps may be absent and the tool must preserve collection order rather than claim a chronological guarantee.
- Cap before de-duplication: rejected because it could return fewer distinct usable videos than the requested bound despite later unique items.
- Infer values from missing fields: rejected because it would corrupt source meaning and provenance.

## Decision: Separate empty, unavailable, and failed collection outcomes

**Decision**: An accessible channel with no uploads collection reference, or a successful uploads listing with no usable public items, returns an empty successful collection. An empty/malformed core channel result maps to `unavailable_resource`. A core or required collection-read error maps to a safe whole-request category: `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, or `upstream_failure` as applicable.

**Rationale**: Empty publicly listable content is meaningfully different from an inaccessible channel or an unsuccessful collection read. Because the collection read is the primary requested operation, a failure cannot truthfully preserve a successful listing result.

**Alternatives considered**:

- Treat absent uploads as an unavailable channel: rejected because the channel can remain accessible while having no publicly listable uploads.
- Treat a collection-read failure as a successful empty list: rejected because it hides a retriable authorization, capacity, or source issue.
- Fail the request when one source item is unusable: rejected because the remaining public collection can still be useful.

## Decision: Limit partial availability to known item-level omissions

**Decision**: If a successful collection response establishes that individual items cannot be returned, omit them and include only a safe aggregate partial-availability status when such an omission is known. No private identity, source diagnostic, or substitute item is returned.

**Rationale**: This preserves usable public results while accurately communicating a known completeness limitation. It does not relabel a failed required collection read as partial success.

**Alternatives considered**:

- Return placeholders for inaccessible items: rejected because placeholders may reveal non-public content existence or identity.
- Invent substitute videos: rejected because it violates channel collection semantics.
- Suppress a known omission: rejected because callers need to assess collection completeness.

## Decision: Reuse existing safe error, metadata, registration, and observability boundaries

**Decision**: Translate existing channel and playlist-item safe errors through a local composed-tool error boundary with sanitized details, describe the composition boundary and caller guidance in executable discovery metadata, and inject existing configured handlers through the default dispatcher.

**Rationale**: Existing lower-layer handlers retain credential attachment, quota behavior, request correlation, and safe logging. Existing composed tools and protocol mapping already establish the public descriptor, error, and registration seams.

**Alternatives considered**:

- Expose lower-layer error categories or payloads directly: rejected because it would weaken the stable public contract and could expose unsafe implementation details.
- Add separate telemetry or configuration: rejected because existing request lifecycle instrumentation and configured dependencies meet the feature need.
- Retain a representative-only descriptor: rejected because YT-309 requires an executable public MCP tool.

## Decision: Verify through contract-first Red-Green-Refactor and full-suite regression coverage

**Decision**: Add failing tests before implementation for validation, exact dependency calls, ordering, de-duplication, cap, empty and failure outcomes, provenance, metadata, registration, and protocol serialization; implement the smallest behavior required; refactor local duplication; then run the focused tests and full repository suite with Ruff.

**Rationale**: This satisfies the constitution's contract-first, mandatory Red-Green-Refactor, integration/regression, documentation, security, and full-suite requirements.

**Alternatives considered**:

- Test only the handler: rejected because MCP discovery, default registration, and serialized safe errors are public boundaries.
- Test only with live data: rejected because controlled injected results are required to prove order, duplicates, and failure categories deterministically.
- Run focused tests only: rejected because the constitution requires post-change full-suite verification.
