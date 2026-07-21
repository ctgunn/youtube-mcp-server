# Research: Layer 2 Tool `videos_list`

## Decision: Expose `videos_list` as an active low-level video retrieval tool

**Rationale**: The seed slice YT-247 requires a Layer 2 tool named `videos_list` that maps directly to YouTube `videos.list`. The PRD defines Layer 2 as a low-level public MCP layer for direct endpoint access, debugging, and power-user workflows, and the local Layer 1 YT-147 wrapper already models `videos.list` as an active video retrieval dependency.

**Alternatives considered**:

- Replace this with higher-level video search or research: rejected because Layer 2 must stay close to one upstream endpoint and the feature spec excludes search, transcript retrieval, ranking, analytics, summarization, and enrichment.
- Fold the work into `search_list`: rejected because `search.list` returns search result references, while `videos.list` returns video resources by explicit selector modes.
- Hide the tool behind a Layer 3 workflow: rejected because the seed explicitly requires public Layer 2 exposure.

## Decision: Use quota cost 1 and conditional access by selector

**Rationale**: The YT-247 seed identifies the official quota-unit cost as `1`, and the local YT-147 Layer 1 wrapper declares quota cost `1` with conditional auth. The wrapper accepts API-key access for `id` and `chart` retrieval and OAuth-required access for caller-specific `myRating` retrieval.

**Alternatives considered**:

- Require OAuth for every selector: rejected because the dependency-backed Layer 1 wrapper treats `id` and `chart` as API-key-compatible read paths.
- Allow API-key access for `myRating`: rejected because the Layer 1 wrapper requires OAuth for caller-specific rating retrieval.
- Omit quota from examples: rejected by YT-202 and the constitution's contract-first requirement.

## Decision: Support `part` plus exactly one selector from `id`, `chart`, or `myRating`

**Rationale**: The local Layer 1 wrapper requires `part`, allows selector fields `id`, `chart`, and `myRating`, and enforces exactly one active selector. The feature spec requires clear part selection and filter modes. Preserving this exact selector model keeps the Layer 2 tool aligned with the internal dependency and prevents ambiguous mixed-selector requests.

**Alternatives considered**:

- Support only direct `id` lookup: rejected because the seed and Layer 1 wrapper identify chart and other supported selectors as part of the videos-list contract.
- Allow multiple selectors and let upstream decide precedence: rejected because that would create ambiguous caller behavior and violates the spec's exactly-one-selector boundary.
- Add search query, transcript, upload, update, delete, analytics, or ranking inputs: rejected because those belong to separate endpoint or higher-level tools.

## Decision: Limit pagination and refinements to compatible selector modes

**Rationale**: The local Layer 1 wrapper allows `pageToken` and `maxResults` only for `chart` and `myRating` collection lookups, and treats `regionCode` and `videoCategoryId` as chart-only refinements. Direct `id` lookup is not a collection traversal path. Layer 2 validation should make these boundaries visible before execution.

**Alternatives considered**:

- Accept pagination for every selector: rejected because direct ID lookup is not a paginated collection traversal and silent acceptance would confuse clients.
- Remove pagination entirely: rejected because the Layer 1 wrapper and feature spec include pagination behavior for eligible collection selectors.
- Allow `regionCode` and `videoCategoryId` with every selector: rejected because the Layer 1 wrapper documents them as chart-only refinements.

## Decision: Return a near-raw video-list result with selector, pagination, quota, and access context

**Rationale**: YT-201/YT-202 and existing list tools preserve endpoint identity, quota, requested parts, selector context, item collections, empty results, and safe error categories. `videos_list` should follow the same convention while keeping returned video resources close to upstream fields and preserving returned pagination tokens where applicable.

**Alternatives considered**:

- Return only a simplified video summary: rejected because Layer 2 should preserve near-raw endpoint semantics and selected parts.
- Enrich results with transcripts, analytics, recommendations, or rankings: rejected because that crosses endpoint and Layer 2 boundaries.
- Treat empty item collections as failures: rejected because a valid accessible lookup can return no items and the spec requires empty success to be distinguishable.

## Decision: Add a new `videos` Layer 2 module

**Rationale**: The repository already reserves `videos` in the shared Layer 2 family registry and has a matching Layer 1 resource module. There is no existing concrete Layer 2 `videos.py` module. Adding one keeps direct video retrieval separate from search, captions, video categories, thumbnails, mutations, analytics, recommendations, and higher-level video workflows.

**Alternatives considered**:

- Add the tool to `search.py`: rejected because search is a distinct endpoint with different quota and result semantics.
- Add the tool to `video_categories.py`: rejected because video category lookup is a reference-data resource family, not video resource retrieval.
- Put endpoint-specific validation in generic shared contracts: rejected because selector, auth, chart refinement, pagination, and video-list caveats belong to the concrete resource family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: Existing Layer 2 tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure`. Video-list validation and upstream failures fit this shared taxonomy without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error payloads only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every failed lookup into `upstream_failure`: rejected because invalid input, access failure, quota exhaustion, unavailable endpoint, and unexpected failure are meaningfully different to callers.
- Add a custom video-list error taxonomy: rejected because Layer 2 tools must share error conventions.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, lint, and docstring evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable, requires full repository test-suite execution after final code changes, and requires reStructuredText docstrings for every new or changed Python function. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**:

- Implement first and add tests afterward: rejected by the constitution.
- Run only focused tests: rejected because full-suite validation is required before completion.
- Omit docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, PRD, current codebase, YT-147 Layer 1 wrapper, and neighboring Layer 2 tools resolve endpoint identity, quota, auth mode, request shape, selector behavior, pagination behavior, response shape, dependencies, registration placement, validation boundaries, and verification expectations.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-247 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local tool inventory: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/247-videos-list/spec.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/videos.py`
- Local Layer 2 family registry: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- Local neighboring Layer 2 module: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`
- Local neighboring Layer 2 module: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/video_categories.py`
- Local neighboring Layer 2 plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/plan.md`
