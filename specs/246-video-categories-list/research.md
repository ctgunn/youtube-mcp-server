# Research: Layer 2 Tool `videoCategories_list`

## Decision: Expose `videoCategories_list` as an active low-level video-category lookup tool

**Rationale**: The seed slice YT-246 requires a Layer 2 tool named `videoCategories_list` that maps directly to YouTube `videoCategories.list`. The project PRD defines Layer 2 as a low-level public MCP layer for direct endpoint access, debugging, and power-user workflows, and the local Layer 1 YT-146 wrapper already models `videoCategories.list` as an active category lookup dependency.

**Alternatives considered**:

- Replace this with higher-level category recommendation: rejected because Layer 2 must stay close to one upstream endpoint and the feature spec excludes recommendation, ranking, analytics, summarization, and enrichment.
- Reuse deprecated `guideCategories_list`: rejected because `guideCategories` and `videoCategories` are distinct resource families with different lifecycle states.
- Hide the tool behind a Layer 3 workflow: rejected because the seed explicitly requires public Layer 2 exposure.

## Decision: Use API-key read access and quota cost 1

**Rationale**: The YT-246 seed identifies the official quota-unit cost as `1`, and the local YT-146 Layer 1 wrapper declares API-key auth with quota cost `1`. The requirements inventory also lists `videoCategories_list` as `Auth: api_key`, `Quota: 1`, and a near-raw category lookup payload.

**Alternatives considered**:

- Require OAuth: rejected because the dependency-backed Layer 1 wrapper rejects non-API-key auth and the endpoint is read-only reference-data lookup.
- Allow mixed auth without a dependency: rejected because Layer 2 should expose the dependency-backed contract rather than invent unsupported auth modes.
- Omit quota from examples: rejected by YT-202 and the constitution's contract-first requirement.

## Decision: Support `part` plus exactly one selector from `id` or `regionCode`, with optional `hl`

**Rationale**: The local Layer 1 wrapper accepts required `part`, optional `id`, optional `regionCode`, optional `hl`, and enforces exactly one selector from `id` or `regionCode`. The feature spec requires category identifier lookup, region lookup, optional display-language behavior, and rejection of ambiguous or conflicting selector requests. This shape is also consistent with existing list-style Layer 2 tools that preserve upstream part/selector concepts.

**Alternatives considered**:

- Require only `regionCode`: rejected because the YT-246 spec and local Layer 1 wrapper both include category ID lookup.
- Allow both selectors and let upstream decide precedence: rejected because that would create ambiguous caller behavior and violates the spec's exactly-one-selector boundary.
- Support paging, ordering, search text, video IDs, or channel IDs: rejected because the local inventory for this endpoint lists only `part`, `id`, `regionCode`, and `hl`.

## Decision: Treat localization as optional display-language guidance

**Rationale**: The local Layer 1 wrapper treats `hl` as optional display-language guidance, and the feature spec requires localized category labels to be preserved when returned without fabricating translations. Layer 2 should expose `hl` as optional, validate malformed localization input locally where possible, and preserve upstream fallback behavior as a successful lookup when the request is otherwise valid.

**Alternatives considered**:

- Make `hl` required: rejected because category lookup is primarily selected by `id` or `regionCode`, and the dependency treats display language as optional.
- Fabricate localized category labels when upstream omits them: rejected because Layer 2 results must remain near-raw.
- Ignore localization entirely: rejected because the seed requires localization considerations to be documented clearly.

## Decision: Return a near-raw video-category list result with explicit selector, region, localization, quota, and access context

**Rationale**: YT-201/YT-202 and existing list tools preserve endpoint identity, quota, requested parts, selector context, item collections, empty results, and safe error categories. `videoCategories_list` should follow the same convention while keeping returned category resources close to upstream fields.

**Alternatives considered**:

- Return only a simplified category-name list: rejected because Layer 2 should preserve near-raw endpoint semantics and selected parts.
- Enrich results with popularity, recommendations, or video counts: rejected because that crosses endpoint and Layer 2 boundaries.
- Treat empty item collections as failures: rejected because a valid lookup can return no items and the spec requires empty success to be distinguishable.

## Decision: Add a new `video_categories` Layer 2 module

**Rationale**: The repository already reserves `video_categories` in the shared Layer 2 family registry and has a matching Layer 1 resource module. There is no existing concrete Layer 2 `video_categories.py` module. Adding one keeps active video-category lookup separate from deprecated guide categories, videos, search, localization infrastructure, and higher-level category workflows.

**Alternatives considered**:

- Add the tool to `guide_categories.py`: rejected because that module is for deprecated guide-category lookup and has different availability semantics.
- Add the tool to `videos.py` or `search.py`: rejected because those modules represent different upstream resource families.
- Put endpoint-specific validation in generic shared contracts: rejected because selector, region, localization, and category-list caveats belong to the concrete resource family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: Existing Layer 2 tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure`. Video-category validation and upstream failures fit this shared taxonomy without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error payloads only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every failed lookup into `upstream_failure`: rejected because invalid input, access failure, quota exhaustion, unavailable endpoint, and unexpected failure are meaningfully different to callers.
- Add a custom video-category error taxonomy: rejected because Layer 2 tools must share error conventions.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, lint, and docstring evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable, requires full repository test-suite execution after final code changes, and requires reStructuredText docstrings for every new or changed Python function. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**:

- Implement first and add tests afterward: rejected by the constitution.
- Run only focused tests: rejected because full-suite validation is required before completion.
- Omit docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, requirements inventory, current codebase, YT-146 Layer 1 wrapper, and neighboring Layer 2 tools resolve endpoint identity, quota, auth mode, request shape, selector behavior, localization behavior, response shape, dependencies, registration placement, validation boundaries, and verification expectations.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-246 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local requirements inventory: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/246-video-categories-list/spec.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/video_categories.py`
- Local Layer 2 family registry: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`
- Local neighboring Layer 2 module: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/guide_categories.py`
- Local neighboring Layer 2 plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/plan.md`
