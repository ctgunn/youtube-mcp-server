# Research: YT-306 Batch Channel Details

## Decision: Extend the existing composed channels family

**Decision**: Implement the public descriptor, handler, batch validation, result shaping, and safe-error mapping in `src/mcp_server/tools/youtube_composed/channels.py`; export it through `src/mcp_server/tools/youtube_composed/__init__.py` and register it with the existing dispatcher.

**Rationale**: The single-channel `channels_getChannel` tool and the Layer 3 family conventions already own normalization, provenance, public-contact heuristics, latest-upload enrichment, injected dependency handling, and public-tool registration. Extending that family is the smallest additive change and avoids duplicating or bypassing the lower-level channel handlers.

**Alternatives considered**:

- Add batch normalization to the near-raw Layer 2 channel tool: rejected because it would mix composed public behavior with an endpoint-aligned contract.
- Create a new service or source client: rejected because existing channel and playlist-item tools provide the required source access and safe errors.
- Issue one single-channel request per identifier: rejected because it creates avoidable fan-out and fails the bounded-batch objective.

## Decision: Use one bounded bulk core lookup and restore caller order

**Decision**: Validate 1–50 distinct IDs, send them in one comma-separated core channel lookup, index returned source items by canonical channel ID, then emit results in the caller's original order.

**Rationale**: The existing channel-list capability supports a bounded identifier collection but does not promise source result order. Indexing and reconstruction preserve the public ordering contract, make absent IDs explicit, and limit the core dependency work to one request.

**Alternatives considered**:

- Depend on source response order: rejected because it is not a reliable contract for callers.
- Reject a batch when any one ID is absent: rejected because it would discard usable results for other IDs.
- Perform a follow-up lookup for each missing ID: rejected because a source omission is sufficient for the safe unavailable outcome and extra calls add cost and latency.

## Decision: Reuse the single-channel item contract where selected data permits

**Decision**: Every available batch item uses the `channels_getChannel` value semantics: raw public profile fields, normalized metadata, cautious public-contact and creator-type heuristics, enrichment state, and path-level provenance. Unavailable source values remain absent or explicitly unavailable; no value is invented.

**Rationale**: Consistent item semantics let a caller reuse existing single-channel interpretation logic while receiving the efficiency and resilience of batch lookup.

**Alternatives considered**:

- Return the lower-level collection envelope directly: rejected because it lacks normalized, heuristic, enrichment, provenance, and per-ID outcome semantics.
- Create a second unrelated batch-item schema: rejected because it would increase caller complexity and risk inconsistent privacy behavior.

## Decision: Make response detail selections explicit and safe

**Decision**: Support `parts` values `snippet` and `contentDetails`; default omitted `parts` to `snippet`. `snippet` permits public profile values, normalized metadata, and public-data heuristics. `contentDetails` permits only its documented public uploads-playlist identifier. Identity, item outcome, enrichment state, and provenance remain available regardless of selection. Internal data needed to perform selected behavior is not exposed merely because it was fetched.

**Rationale**: An explicit, small selection vocabulary makes discovery deterministic, prevents accidental exposure of unrelated source fields, and lets callers limit the raw detail they receive. The default remains compatible with the normalized public profile expected from the single-channel tool.

**Alternatives considered**:

- Forward arbitrary `parts` directly: rejected because unsupported values would create an unstable public contract and might omit data needed for safe normalization.
- Ignore `parts`: rejected because the seed explicitly requires a caller-controlled detail selection.
- Expose all internally read source fields: rejected because internal enrichment needs do not constitute public output requirements.

## Decision: Keep latest-upload enrichment optional, bounded, and item-local

**Decision**: `includeLatestUpload` defaults to `true`. When enabled, each available channel may make at most one one-item uploads-playlist lookup. A valid timestamp produces `complete`; no usable playlist, item, or timestamp produces `unavailable`; a safe post-core failure produces `partial` and a sanitized cause category. When disabled, no enrichment lookup occurs and the item state is `not_requested`.

**Rationale**: The public uploads playlist provides deterministic, channel-wide latest-video behavior. Item-local states preserve useful core profiles and distinguish an absent timestamp, a disabled feature, and a retryable failure.

**Alternatives considered**:

- Use generic search to locate the latest upload: rejected because it is query-dependent and adds high-cost, less deterministic behavior.
- Fail the entire batch after one enrichment failure: rejected because it discards independently successful items.
- Treat an enrichment failure as no uploads: rejected because it hides a potentially actionable access, capacity, or source-service condition.

## Decision: Separate item-local outcomes from request-wide failures

**Decision**: An ID omitted from an otherwise successful core lookup is an item-level `unavailable_resource` outcome. A post-core enrichment problem is an item-level partial outcome. A failure of the single bulk core lookup before any item can be resolved remains a safe request-wide `authorization_sensitive_data`, `quota_exhaustion`, or `upstream_failure` error.

**Rationale**: The contract can safely determine absence only after a successful bulk response. It cannot truthfully attribute a request-wide dependency failure to a particular channel.

**Alternatives considered**:

- Mark every ID unavailable after a core request failure: rejected because it misstates the failure and hides retry guidance.
- Return raw lower-level errors per item: rejected because it leaks inconsistent and potentially sensitive source detail.

## Decision: Preserve the existing public-data and heuristic safeguards

**Decision**: Derive email addresses and HTTP(S) links only from public returned channel material; normalize and deterministically de-duplicate them; reject malformed, private, unsupported, or credential-bearing links. Classify channel type as `creator`, `brand`, or `unknown` using safe public signal identifiers, with missing or conflicting signals yielding `unknown`.

**Rationale**: These fields are useful research context but do not establish ownership or identity. Reusing YT-305's safeguards prevents scope expansion into crawling, account access, or external contact-data enrichment.

**Alternatives considered**:

- Crawl public links or use third-party contact sources: rejected because it expands privacy risk, scope, and latency.
- Present public contact strings or classifications as verified facts: rejected because neither proves affiliation, ownership, or deliverability.

## Decision: Use existing test and documentation conventions

**Decision**: Use pytest unit tests in `tests/unit/test_youtube_composed_channels.py`, contract tests in `tests/contract/test_youtube_composed_channels_contract.py`, and registration/invocation integration tests in `tests/integration/test_youtube_composed_tool_registration.py` and `tests/integration/test_youtube_tool_registration.py`. All changed or new Python functions receive reStructuredText docstrings.

**Rationale**: These are the established test boundaries for composed public tools. They provide deterministic injected-dependency coverage as well as registration and discovery confidence.

**Alternatives considered**:

- Add only handler unit tests: rejected by the constitution because public contracts and integration boundaries also require coverage.
- Add a separate test package: rejected because it would fragment established composed-tool coverage without a new architectural boundary.
