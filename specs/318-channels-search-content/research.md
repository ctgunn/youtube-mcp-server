# Research: YT-318 Channel Content Search

## Decision: Extend the existing concrete channels family

**Decision**: Add the public schema, validation, direct-search mapping, result normalization, metadata, handler, and descriptor to `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/channels.py`; export its public symbols through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_composed/__init__.py`; and default-register it in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

**Rationale**: The Layer 3 catalog already assigns `channels_searchContent` to the channels family. That family owns executable channel tools, injected lower-layer dependencies, public metadata, safe errors, and dispatcher integration.

**Alternatives considered**:

- Create a generic composed-search service: rejected because one thin channel-specific workflow does not justify a new abstraction or boundary.
- Add this behavior to Layer 2 `search_list`: rejected because callers need a concise channel-content contract, not another near-raw endpoint variant.
- Place it in the videos family: rejected because the public request starts with a required channel identity and the declared catalog places it with channels.

## Decision: Use one direct channel-constrained video search

**Decision**: Call the existing `search_list` handler once with `part=snippet`, the normalized query, the normalized channel identifier, `type=video`, validated `maxResults`, and the selected `order`. Forward a supplied language preference as the existing relevance-language input. Do not expose a continuation input.

**Rationale**: The PRD maps this tool primarily to `search.list`, and the existing Layer 2 boundary already provides configured public-read execution, safe errors, and bounded search behavior. Restricting to videos produces a coherent content identity and avoids any claim that unrelated resource types are returned.

**Alternatives considered**:

- Resolve the uploads collection and filter it locally: rejected because it changes the contract to a composite listing/filtering workflow and adds unnecessary calls.
- Call an integration wrapper or HTTP client directly: rejected because it bypasses the required lower-layer interface, configured auth, observability, quota handling, and safe errors.
- Offer page-token traversal: rejected because the feature specifies a bounded result set and no continuation contract; it would broaden scope and complicate reproducibility.

## Decision: Preserve direct-search semantics and upstream ordering

**Decision**: Normalize usable source records in their received order, retain the first usable occurrence of each video identifier, then apply the final cap. The contract declares that the lower-layer source performs matching and ordering; the new tool performs only request shaping, public result normalization, association defense, duplicate/malformed omission, and response-context shaping.

**Rationale**: The feature explicitly requires documentation distinguishing direct upstream search from composite enrichment or filtering. Upstream ordering is the only ranking applied, and a stable result contract still requires protection against malformed or out-of-scope records.

**Alternatives considered**:

- Locally re-rank by date or views: rejected because it would contradict the direct-search contract and create a second ordering definition.
- Enrich each video with details or channel metadata: rejected because no requested requirement needs it and it would add latency, quota, and partial-result behavior.
- Return every raw source record unchanged: rejected because it can violate the channel-only and normalized-public-result guarantees.

## Decision: Require a scoped BCP 47 language preference

**Decision**: Accept an optional trimmed BCP 47 language tag, reject malformed values before search, forward valid values only as a relevance hint, and report the applied preference in response context and metadata.

**Rationale**: The feature specification requires language refinement but explicitly does not promise language-only results. A scoped validator gives callers actionable failures while preserving a simple public contract.

**Alternatives considered**:

- Accept any nonblank language string: rejected because it makes invalid calls non-deterministic and violates the explicit language-tag requirement.
- Guarantee language-matched results: rejected because a relevance hint cannot ensure language classification or availability.
- Add locale, region, caption, or transcript filters: rejected because they are not in the feature scope and would change matching semantics.

## Decision: Normalize only public, channel-associated video records

**Decision**: Map a usable video reference and publicly available snippet fields into a normalized item with `videoId`, `contentType`, `title`, `description`, `publishedAt`, `channelId`, `channelTitle`, and `thumbnails` when available. Retain only records whose available source channel identity equals the requested channel identity; omit malformed, duplicate, or mismatched records and disclose only a safe aggregate omission count and category.

**Rationale**: This proves the channel-association success criterion, avoids fabricating optional values, and prevents an abnormal source record from being presented as requested-channel content. Aggregate disclosure lets clients judge completeness without leaking record identities or raw source data.

**Alternatives considered**:

- Return mismatched records because the upstream query was channel-scoped: rejected because the public tool must independently guarantee channel association.
- Fail the complete request on one malformed record: rejected because a remaining collection can be correct and useful.
- Expose omitted record identifiers or source details: rejected because they may reveal unavailable content or unsafe source data.

## Decision: Map lower-layer failures to the established safe Layer 3 taxonomy

**Decision**: Translate lower-layer search failures to `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, or `upstream_failure`, preserving only sanitized diagnostic details. A failed required search is a whole-request error; a successful source response with no matches is a successful empty result.

**Rationale**: Existing composed tools already map lower-layer categories and sanitize details. This keeps errors machine-readable and actionable without exposing credentials, stack traces, raw upstream bodies, or private access details.

**Alternatives considered**:

- Surface Layer 2 error categories unchanged: rejected because that leaks lower-layer contract terminology into the Layer 3 boundary.
- Return a partial collection after the required search call fails: rejected because it would represent incomplete data as a completed search.
- Use text-only errors: rejected because MCP clients need stable category data for recovery.

## Decision: Validate contract, registration, and safe behavior through Red-Green-Refactor

**Decision**: Add failing unit tests before implementation for request normalization, exact lower-layer call construction, result association and normalization, cap/order/language handling, empty results, omissions, and errors; add contract tests for discovery/schema/metadata; add integration tests for injected execution and default registration; and run focused, full-suite, and lint checks after the implementation work.

**Rationale**: This meets the constitution's mandatory TDD, contract-first, integration, documentation, and full-suite requirements while providing deterministic evidence for a public MCP tool.

**Alternatives considered**:

- Test only the handler: rejected because descriptor discovery and dispatcher registration are public contract boundaries.
- Test only live public data: rejected because controlled records are required to prove validation, omission, and error behavior deterministically.
- Run only focused tests: rejected because the constitution requires final full-repository regression evidence.
