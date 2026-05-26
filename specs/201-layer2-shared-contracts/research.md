# Research: YT-201 Shared YouTube Scaffolding and Contracts

## Decision: Keep Shared YouTube Contracts Additive and Centralized

YouTube tool foundation shared contract records, naming helpers, metadata validation, representative examples, and registration guidance should be introduced as additive scaffolding in the existing Python MCP service. The slice should not add concrete YouTube endpoint tool behavior beyond representative contract examples.

**Rationale**: YT-201 is a foundation slice for YT-203 through YT-255. The feature spec explicitly requires later endpoint slices to depend on these shared contracts without redefining cross-cutting rules. Keeping the shared pieces additive avoids changing existing MCP tools, hosted transport, or Layer 1 behavior before endpoint-specific work begins.

**Alternatives considered**:

- Implement the first real endpoint tool in this slice: rejected because YT-201 is the shared scaffolding slice, while individual endpoint-backed tools start at YT-203.
- Put all YouTube endpoint behavior in one broad shared module: rejected because the seed requires resource-family cohesion and avoidance of one large endpoint-tool file.
- Create a separate service or package for YouTube tool foundation: rejected because the existing MCP service and Layer 1 resource-family modules already provide the needed boundaries.

## Decision: Use `resource_method` Public Tool Names Without `youtube_`

YouTube public tool names should derive directly from YouTube resource-method pairs using `resource_method`, such as `videos_list`, `playlists_insert`, `comments_setModerationStatus`, and `videos_getRating`. CamelCase upstream method suffixes remain recognizable after the underscore.

**Rationale**: Both the PRD and tool specs define the naming pattern. Preserving camelCase suffixes avoids ambiguity for upstream methods whose official names are meaningful, while omitting `youtube_` keeps public names concise and resource-grouped.

**Alternatives considered**:

- Prefix every tool with `youtube_`: rejected because the seed explicitly says not to add the redundant prefix.
- Convert every method suffix to snake_case: rejected because examples such as `comments_setModerationStatus` and `videos_getRating` preserve upstream recognizability.
- Use endpoint path names instead of resource-method names: rejected because YouTube Data API documentation and the Layer 1 metadata model are organized by resource and method.

## Decision: Keep Inputs Near-Raw With Shared Validation Guidance

YouTube tool input contracts should stay close to upstream request parameters while documenting common MCP-facing validation rules for required fields, selector exclusivity, bounded values, pagination, `part` selection, request bodies, media inputs, and mutation acknowledgments.

**Rationale**: shared YouTube tool foundation is the lower-level public layer for direct endpoint access, debugging, and power-user workflows. Near-raw inputs let callers map from upstream documentation to MCP calls, while shared validation avoids inconsistent schema behavior across endpoint slices.

**Alternatives considered**:

- Hide upstream parameters behind higher-level friendly names: rejected because that belongs to Layer 3-style tools, not YouTube tool foundation.
- Pass arbitrary request dictionaries through without validation: rejected because MCP discovery must expose usable schemas and safe, deterministic errors.
- Define fully endpoint-specific validation only in each endpoint spec: rejected because selector and pagination patterns would drift across the catalog.

## Decision: Preserve Near-Raw Outputs With Light MCP Wrappers Only When Useful

YouTube tool results should preserve upstream-visible items, requested parts, paging tokens, mutation acknowledgments, and relevant raw fields. Light wrapper fields are allowed only when they improve MCP clarity, such as naming the upstream endpoint, attaching safe metadata, or wrapping downloaded content for transport-safe delivery.

**Rationale**: The product differentiates YouTube tool foundation from Layer 3. YouTube tools must remain close to upstream semantics and must not masquerade as a composed, heuristic, enriched, or research-oriented tool. MCP consumers still need predictable structured results and safe handling for downloaded or media-related payloads.

**Alternatives considered**:

- Return only raw upstream JSON with no metadata: rejected because callers need auth/quota/caveat and endpoint identity context in discovery and review surfaces.
- Normalize all outputs into high-level domain objects: rejected because that would blur the line between YouTube tool foundation and Layer 3.
- Create a different result shape per resource family: rejected because cross-catalog callers need consistent list, mutation, download, and error patterns.

## Decision: Standardize Auth, Quota, Caveat, and Error Categories

Every YouTube tool contract should expose upstream identity, auth mode, official quota-unit cost, and deprecation or availability caveats when applicable. Shared error categories should cover authentication failure, authorization failure, quota exhaustion, missing resource, invalid request, deprecated endpoint, unavailable endpoint, and unexpected upstream failure.

**Rationale**: Tool discovery must let callers understand whether a tool requires API key access, OAuth, or conditional credentials, and how expensive the call is before invoking it. Stable error categories keep MCP clients from relying on raw upstream text and reduce leakage risk.

**Alternatives considered**:

- Let endpoint slices describe auth and quota in prose only: rejected because later tools need machine-checkable metadata and consistent review evidence.
- Surface raw upstream errors directly: rejected because secrets, stack traces, or provider-specific details could leak and because caller-facing categories would drift.
- Treat mixed auth as a single auth mode: rejected because list endpoints often differ by selector or caller context.

## Decision: Validate Representative Endpoint Shapes Before Endpoint Slices

YT-201 should include representative examples for a simple read endpoint, paginated list endpoint, camelCase method, OAuth-only endpoint, mutation endpoint, upload or media-related endpoint, high-quota endpoint, and deprecated or availability-constrained endpoint.

**Rationale**: The YouTube tool foundation inventory is broad, and later endpoint slices should not rediscover the same shape decisions. Representative examples prove the shared contract can cover the catalog without implementing every endpoint in the shared slice.

**Alternatives considered**:

- Wait for each endpoint slice to discover its own shape: rejected because it defeats the purpose of shared scaffolding.
- Model every endpoint in full during YT-201: rejected because it would become endpoint implementation by another name.
- Use only `videos_list` as the representative example: rejected because it does not exercise OAuth-only, mutation, media, high-quota, camelCase, or constrained endpoint concerns.

## Decision: Organize Future Endpoint Tools by Resource Family

Later YouTube endpoint slices should place tool definitions, input contracts, handlers, response expectations, tests, examples, and caveat notes by YouTube resource family while using centralized shared YouTube contract helpers.

**Rationale**: YT-156 already established resource-family organization for Layer 1. Keeping YouTube tool foundation aligned with that structure makes it easier to trace a public endpoint-backed tool down to its Layer 1 wrapper and avoids a monolithic public-tool module.

**Alternatives considered**:

- Store every YouTube tool in one shared file: rejected because it would recreate the broad-file maintainability problem.
- Create one isolated package per endpoint: rejected because it fragments shared family behavior and makes related endpoints harder to review.
- Put YouTube tools inside Layer 1 modules: rejected because Layer 1 is internal integration and shared YouTube tool foundation is public MCP-facing behavior.

## Decision: Require Red-Green-Refactor, Full-Suite Verification, and reStructuredText Docstrings

Implementation must start with failing or characterization tests for shared YouTube contracts, then add the minimum shared scaffolding required to pass, then refactor and run targeted checks followed by `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The constitution makes Red-Green-Refactor, full-suite validation, integration/regression coverage, and reStructuredText docstrings non-negotiable. Planning these constraints now prevents later endpoint slices from inheriting under-specified shared helpers.

**Alternatives considered**:

- Treat YT-201 as documentation-only and skip code-oriented test planning: rejected because the shared scaffolding may introduce reusable helpers or metadata records that need test coverage.
- Run only focused YouTube tool foundation tests: rejected because the constitution requires a full repository test-suite run after final changes.
- Add docstrings only to public helpers: rejected because the constitution requires every new or modified Python function.
