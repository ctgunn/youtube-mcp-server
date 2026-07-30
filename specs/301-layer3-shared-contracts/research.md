# Research: YT-301 Layer 3 Shared Scaffolding and Contracts

## Decision: Build Layer 3 Shared Contracts as an Additive Package

Layer 3 shared contract primitives will be planned under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_layer3/`, separate from the existing Layer 2 `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/` package.

**Rationale**: Layer 2 contracts are near-raw endpoint-backed primitives. Layer 3 tools are public, higher-level, composed, normalized, ranked, filtered, and heuristic-aware. A distinct package keeps the boundary visible while still allowing Layer 3 contracts to reference Layer 2 metadata for upstream identity, auth, quota, and response-boundary facts.

**Alternatives considered**:

- Extend `youtube_common` directly: rejected because it would blur near-raw Layer 2 contracts with higher-level composed behavior.
- Add all Layer 3 contract logic to one `youtube_tools.py` file: rejected because the seed requires cohesive grouped families and warns against concentrating composed tools in one large shared file.
- Place Layer 3 contracts under `integrations/`: rejected because Layer 3 is public MCP tool contract and composition guidance, not upstream integration execution.

## Decision: Use Grouped Public Names for the Layer 3 Catalog

Layer 3 public tool names will use the PRD catalog names grouped by family: `videos_*`, `channels_*`, `playlists_*`, and `transcripts_*`. The shared naming contract must validate all 19 initial names before concrete tool slices begin.

**Rationale**: The PRD and seed both identify grouped public names as the intended Layer 3 catalog shape. Grouping makes discovery easier for MCP clients and prevents redundant provider prefixes.

**Alternatives considered**:

- Prefix every tool with `youtube_`: rejected because existing YouTube tool conventions avoid redundant provider prefixes.
- Use raw upstream endpoint names: rejected because Layer 3 tools may compose multiple lower-level operations and should not masquerade as single endpoints.
- Use free-form natural-language tool names: rejected because deterministic grouped names are easier to test, discover, and document.

## Decision: Define Shared Parameter Conventions Before Tool-Specific Schemas

Repeated Layer 3 parameters will be represented by shared conventions for IDs, queries, language, result limits, ordering, selected parts, ISO 8601 date filters, pagination, transcript match limits, sample-video limits, and fan-out bounds.

**Rationale**: Layer 3 tools reuse the same user-facing concepts across families. Defining conventions once reduces drift across YT-302+ slices and gives reviewers a single place to validate defaults, bounds, unsupported combinations, and user-facing errors.

**Alternatives considered**:

- Let each Layer 3 tool define repeated fields independently: rejected because it would recreate the drift YT-301 exists to avoid.
- Reuse raw upstream YouTube parameter names directly: rejected because Layer 3 contracts must prefer stable MCP-facing names and may combine multiple upstream concepts.
- Fully specify every tool schema in YT-301: rejected because individual tool behavior belongs to later YT-302+ slices.

## Decision: Require Response Field Provenance Categories

Every representative Layer 3 result contract must classify result fields as raw upstream, normalized, or heuristic/inferred. Heuristic or inferred fields must include basis and limitation notes.

**Rationale**: Layer 3 tools are valuable because they normalize and enrich results, but client developers and agents need to know when a field is factual upstream data versus server-shaped or inferred. Provenance categories reduce misuse of heuristic creator, contact, ranking, latest-upload, transcript-match, and playlist fan-out signals.

**Alternatives considered**:

- Return only normalized fields: rejected because callers may still need traceability to upstream values.
- Return only raw upstream fields: rejected because Layer 3 is intended to shield callers from raw YouTube response shapes.
- Allow heuristic fields without explicit disclosure: rejected because it creates misleading certainty for downstream agents.

## Decision: Centralize Ranking and Filtering Semantics

Reusable ranking and filtering concepts such as `creatorOnly`, subscriber bands, latest-upload windows, `uniqueChannels`, sample-video limits, transcript match limits, and `sortBy` will be defined in shared Layer 3 conventions with per-family applicability notes.

**Rationale**: Search, creator discovery, channel discovery, playlist search, and transcript search all need predictable semantics for filtering and ordering. Shared semantics let later tool specs state applicability without redefining the rule.

**Alternatives considered**:

- Define ranking modes only inside search tools: rejected because several channel and playlist workflows reuse ranking/filter concepts.
- Hide ranking and filtering implementation details from contracts: rejected because the PRD requires fields implemented partly in-server to be documented.
- Make all filters globally accepted by all tools: rejected because many filters are family-specific and unsupported-combination behavior must be explicit.

## Decision: Distinguish Composition Boundaries in Every Layer 3 Tool Contract

Layer 3 contracts must disclose whether a tool performs direct retrieval, normalized single-resource shaping, multi-resource composition, enrichment, server-side filtering, ranking, or fan-out.

**Rationale**: Layer 3 tools may multiply upstream quota usage and may return partial results when one lower-level dependency fails. The composition boundary gives callers and reviewers a stable way to reason about cost, auth sensitivity, partial data, and user-visible limitations before invocation.

**Alternatives considered**:

- Document only final response shape: rejected because it hides auth, quota, and partial-result implications.
- Require every Layer 3 tool to be single-resource: rejected because the PRD explicitly includes composite workflows.
- Push all composition notes to implementation comments: rejected because MCP-facing behavior belongs in public contracts and feature artifacts.

## Decision: Validate with Representative Examples, Not Concrete Public Tools

YT-301 will use representative non-executing examples from all four families and at least eight major workflow shapes: simple retrieval, search, ranked/filterable discovery, transcript retrieval, transcript search, playlist listing, playlist search, and playlist transcript fan-out.

**Rationale**: The slice must prove shared coverage before YT-302+ work starts, but it must not implement actual public Layer 3 tool behavior. Representative examples provide enough evidence for contract tests without expanding scope.

**Alternatives considered**:

- Implement `videos_getVideo` as the first example: rejected because that belongs to YT-302.
- Wait for each later slice to prove shared contracts: rejected because downstream slices need a stable dependency.
- Use only prose examples: rejected because the constitution requires testable contract and regression planning.

## Decision: Use Existing Test and Docstring Standards

Focused validation will use planned tests under `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/`, followed by full `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The constitution makes Red-Green-Refactor, integration coverage, full-suite validation, and reStructuredText docstrings non-negotiable. The existing Layer 2 shared modules already model this style.

**Alternatives considered**:

- Documentation-only validation: rejected because future public tool contracts need executable checks.
- Targeted-only tests: rejected because the constitution requires full-suite validation after final code changes.
- Relax docstring requirements for simple helpers: rejected because the constitution requires docstrings for every new or modified Python function.
