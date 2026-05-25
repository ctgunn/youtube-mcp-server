# Research: YT-202 Layer 2 Tool Metadata, Naming, and Quota Standards

## Decision: Extend YT-201 Rather Than Redefining Shared Layer 2 Scaffolding

YT-202 should build additively on the existing shared Layer 2 primitives in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`. It should tighten metadata, naming, quota, auth, availability, usage-note, and response-boundary requirements without replacing YT-201's broader input, response, error, and resource-family scaffolding.

**Rationale**: YT-201 already introduced the shared Layer 2 contract foundation and representative examples. YT-202 is narrower: it defines the public metadata and caller-visible standards that every endpoint-backed tool must satisfy before later endpoint slices begin.

**Alternatives considered**:

- Create a parallel Layer 2 metadata package: rejected because it would split shared rules across competing locations.
- Fold all YT-202 behavior into documentation only: rejected because later endpoint slices need machine-checkable metadata expectations and contract tests.
- Implement concrete endpoint-backed tools in YT-202: rejected because endpoint tools begin in YT-203 and later slices.

## Decision: Require a Complete Metadata Record for Every Layer 2 Tool

Every Layer 2 endpoint-backed tool definition should expose public tool name, upstream resource, upstream method, stable operation identity, official quota-unit cost, auth mode, availability state, caveats, description text, usage notes, and response-boundary classification.

**Rationale**: The feature spec requires client developers to inspect a tool and understand endpoint identity, cost, access requirements, and caveats before invocation. The existing YT-201 contract covers most of this surface; YT-202 adds explicit availability state, usage-note visibility, and response-boundary classification.

**Alternatives considered**:

- Keep availability and usage notes as optional prose: rejected because reviewers need consistent validation and callers need predictable pre-invocation visibility.
- Use only upstream operation metadata from Layer 1: rejected because Layer 1 is internal and does not define public MCP descriptions or usage notes.
- Put quota and auth only in external docs: rejected because discovery and representative examples must be sufficient for MCP clients and reviewers.

## Decision: Preserve `resource_method` Naming With Official Method Casing

Layer 2 public names should continue to derive from upstream resource-method pairs using `resource_method`, with no redundant `youtube_` prefix and with official camelCase method suffixes preserved when meaningful.

**Rationale**: The PRD, tool specs, seed, and YT-201 artifacts all align on names such as `videos_list`, `playlists_insert`, `comments_setModerationStatus`, and `videos_getRating`. Preserving official method casing helps callers map public tools back to YouTube Data API documentation.

**Alternatives considered**:

- Convert all suffixes to snake_case: rejected because it diverges from existing project examples and obscures official method names.
- Prefix every tool with `youtube_`: rejected because the product context already makes the provider obvious and the seed explicitly rejects the prefix.
- Invent friendlier domain names: rejected because Layer 2 is the near-raw endpoint layer; friendlier composed naming belongs to Layer 3.

## Decision: Make Quota Visible in Metadata, Description, and Usage Notes

Official quota-unit cost should be present in the structured metadata record, in caller-facing tool descriptions, and in example or usage notes. High-cost tools should include explicit warnings before invocation.

**Rationale**: Layer 2 callers and future Layer 3 authors must reason about direct endpoint cost and composition cost. Multiple visibility targets reduce the chance that an MCP client or reviewer misses cost implications.

**Alternatives considered**:

- Metadata-only quota disclosure: rejected because descriptions and examples are often the first discovery surfaces users see.
- Description-only quota disclosure: rejected because tests and downstream tooling need machine-checkable cost.
- Estimate quota dynamically at runtime only: rejected because official per-call cost is static contract information for the endpoints in scope.

## Decision: Use Explicit Auth Mode and Availability State Vocabularies

Auth mode should remain one of `api_key`, `oauth_required`, or `mixed/conditional`. Availability state should be explicit enough to distinguish active, deprecated, unavailable, region-constrained, owner-only, media-constrained, and documentation-caveat cases.

**Rationale**: YT-201 already established auth modes. YT-202 needs availability visibility so constrained or deprecated endpoints do not look like ordinary active tools in discovery or examples.

**Alternatives considered**:

- Represent all caveats as free-form text only: rejected because tests and future endpoint slices need stable categories.
- Treat owner-only and OAuth-required as the same concept: rejected because OAuth is a credential mode, while owner-only describes an endpoint or selector constraint.
- Hide deprecated or constrained endpoints until implementation: rejected because Layer 2 catalog planning must preserve endpoint visibility while warning callers.

## Decision: Classify Response Boundaries Before Endpoint Implementation

Representative Layer 2 responses should be classified as near-raw, lightly reshaped for MCP clarity, or out of Layer 2 scope. Light reshaping is allowed for endpoint identity, safe metadata, pagination clarity, mutation acknowledgments, and safe content wrappers; higher-level composition, ranking, enrichment, or heuristics are out of scope.

**Rationale**: Layer 2 and Layer 3 are both public layers but serve different needs. This boundary lets future Layer 3 authors compose Layer 2 tools without mistaking lightly wrapped endpoint output for enriched research results.

**Alternatives considered**:

- Allow each endpoint slice to define its own response boundary: rejected because response semantics would drift across the catalog.
- Return raw upstream JSON only: rejected because MCP clients still need safe wrapper fields for metadata and content transport.
- Normalize Layer 2 into higher-level domain models: rejected because that belongs to Layer 3.

## Decision: Validate At Least 10 Representative Resource-Method Examples

YT-202 should validate at least 10 representative examples spanning simple reads, paginated reads, camelCase names, OAuth-only operations, mixed-auth operations, mutations, media operations, high-quota operations, availability-constrained endpoints, and non-list response shapes.

**Rationale**: The Layer 2 inventory is broad, and the standards need proof across endpoint shapes before YT-203 through YT-255 rely on them. Ten examples is large enough to cover the required diversity without modeling every endpoint in detail.

**Alternatives considered**:

- Validate only the four named examples from the spec: rejected because that would miss media, high-quota, constrained, mutation, and non-list shapes.
- Model the full YT-203 through YT-255 inventory in YT-202: rejected because that would turn this standards slice into endpoint planning or implementation.
- Use generated placeholder examples: rejected because representative examples must be meaningful enough for reviewers and future endpoint authors.

## Decision: Keep Verification Constitution-Driven

Implementation must start with failing or characterization tests, add the minimum shared metadata standard needed to pass, then refactor and run focused checks before `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The constitution makes Red-Green-Refactor, full-suite validation, integration/regression coverage, and reStructuredText docstrings mandatory. YT-202 changes shared standards that future endpoint slices will depend on, so weak validation would spread quickly.

**Alternatives considered**:

- Treat YT-202 as docs-only and skip code test planning: rejected because the feature includes validation expectations and likely shared metadata helpers.
- Run only focused Layer 2 tests: rejected because the constitution requires full-suite validation after final code changes.
- Add docstrings only to public functions: rejected because the constitution requires every new or modified Python function.
