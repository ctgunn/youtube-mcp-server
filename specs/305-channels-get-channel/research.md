# Research: YT-305 Channel Details

## Decision: Implement the concrete tool in the composed channels family

**Decision**: Add the public descriptor, handler, validation, normalization, contact, heuristic, enrichment, and error-mapping behavior to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`; export it through the composed package and register it through the existing dispatcher.

**Rationale**: The shared Layer 3 catalog already assigns `channels_getChannel` to the channels family. This mirrors the established concrete video and transcript tool pattern and preserves the boundary between higher-level caller-ready tools and near-raw lower-layer tools.

**Alternatives considered**:

- Add the behavior to the lower-level channels wrapper: rejected because it would mix normalized, heuristic, and multi-resource behavior into a near-raw endpoint contract.
- Create a new service or source client: rejected because existing handlers supply all required source access.
- Add the behavior to the videos family: rejected because channel-specific public contracts and helpers belong to their declared family.

## Decision: Use one channel lookup for the core public profile

**Decision**: Retrieve the requested channel through the existing channel-list capability using the public profile and uploads-playlist detail groups needed for this tool: `snippet` and `contentDetails`.

**Rationale**: This provides the requested channel identity, public title, description, thumbnails, country, default language, joined date, custom URL, and the channel's public uploads-playlist identifier in one bounded lookup. The existing channel capability supports one identifier and already supplies authentication, quota, request execution, and safe lower-layer errors.

**Alternatives considered**:

- Hydrate multiple channel resources: rejected because the feature accepts exactly one identifier and needs one result.
- Expose the lower-level collection response unchanged: rejected because the feature requires normalized metadata, enrichment, and provenance.
- Use an owner-only channel lookup: rejected because the feature is a public research tool and must not require or expose owner context.

## Decision: Derive latest-video time through the public uploads playlist

**Decision**: When the core result includes a usable public uploads-playlist identifier, make at most one playlist-item lookup with `part=contentDetails` and `maxResults=1`, then use its available `videoPublishedAt` as `latestVideoPublishedAt`.

**Rationale**: The uploads playlist provides a deterministic, channel-wide, query-independent latest-video path. It bounds every request to one core lookup plus at most one enrichment lookup and reuses the existing lower-layer playlist-item capability.

**Alternatives considered**:

- Use a generic search operation: rejected because search requires a query and its output is query-dependent rather than a reliable channel-wide latest-video source.
- Fetch multiple videos and sort them: rejected because it adds unnecessary fan-out and latency.
- Return a cached or inferred timestamp: rejected because the feature must not present stale or guessed publication data.

## Decision: Separate no latest public video from failed enrichment

**Decision**: A missing uploads playlist, empty playlist result, or absent valid publication timestamp returns the core profile with `latestVideoPublishedAt` unavailable and `enrichment.status` set to `unavailable`. An access, capacity, or source failure after the core profile succeeds returns the profile with `enrichment.status` set to `partial`, `enrichment.category` set to `partial_enrichment_failure`, and a safe cause category.

**Rationale**: A usable channel profile remains valuable when optional enrichment cannot produce a timestamp. Distinguishing absence from failure lets clients retry only when appropriate and prevents an unavailable timestamp from being represented as a source failure.

**Alternatives considered**:

- Fail the entire request for any enrichment problem: rejected because it discards a successfully retrieved core profile.
- Treat a failed enrichment as no uploads: rejected because it hides actionable authorization, quota, or temporary source conditions.
- Return an older or guessed timestamp: rejected because it would misrepresent channel activity.

## Decision: Treat public contacts and channel type as cautious heuristics

**Decision**: Derive email addresses and HTTP(S) contact links only from public channel material returned for the request, normalize and de-duplicate them deterministically, and omit malformed or unsupported values. Classify channel type as `creator`, `brand`, or `unknown` only when positive public signals support one non-conflicting conclusion; otherwise return `unknown`.

**Rationale**: The required fields are useful research context, but neither a public contact string nor an observed branding signal verifies identity or ownership. Conservatively limiting both operations to available public material avoids scraping, private-data access, and false certainty.

**Alternatives considered**:

- Crawl external pages or use a contact-data provider: rejected because it expands scope, privacy risk, dependencies, and latency.
- Treat every unclassified channel as a brand: rejected because absence of evidence is not positive brand evidence.
- Omit all derived fields: rejected because the seed and PRD explicitly require normalized public contacts and creator-versus-brand heuristic fields.

## Decision: Reuse existing safe error and registration conventions

**Decision**: Map invalid public input to `invalid_parameters`; empty or unavailable core channels to `unavailable_resource`; authorization failures to `authorization_sensitive_data`; capacity failures to `quota_exhaustion`; and other core failures to `upstream_failure`. Use the existing dispatcher dependency injection and protocol error serialization; add regression coverage rather than a protocol change.

**Rationale**: Existing concrete Layer 3 tools already translate lower-layer categories through a sanitized public boundary. The project protocol already supports the required caller-facing categories, including partial enrichment failures.

**Alternatives considered**:

- Expose lower-layer categories and details directly: rejected because callers would receive inconsistent, potentially unsafe endpoint-specific information.
- Add a new protocol error format: rejected because existing serialization meets the feature's caller needs.
- Add bespoke runtime configuration: rejected because both lower-layer lookups already receive configured dependencies through the dispatcher.

## Decision: Keep new helpers local until a second user exists

**Decision**: Keep contact parsing, tri-state classification, and latest-enrichment result shaping private to the composed channels family unless another concrete tool establishes a genuine shared use case.

**Rationale**: The existing shared contract contains cross-family conventions while family modules own concrete behavior. Local helpers minimize coupling and avoid premature abstraction.

**Alternatives considered**:

- Move helpers immediately to shared conventions: rejected because no second consumer currently exists.
- Import private video-family helpers: rejected because they do not meet the required tri-state or partial-failure behavior and would create an inappropriate family dependency.
