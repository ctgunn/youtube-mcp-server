# Research: Layer 2 Tool `guideCategories_list`

## Decision: Expose `guideCategories_list` as a deprecated low-level guide-category lookup tool

**Rationale**: The seed slice YT-223 requires a Layer 2 tool named `guideCategories_list` that maps directly to YouTube `guideCategories.list`. Google’s revision history says the `guideCategories` resource and `guideCategories.list` method were deprecated immediately in the September 9, 2020 update and would stop working on or after that announcement. The current YouTube Data API reference navigation omits a `guideCategories` resource while retaining active resources such as `i18nLanguages`, `i18nRegions`, and `videoCategories`. The public contract therefore needs to expose the endpoint as legacy/deprecated rather than as a recommended current taxonomy source.

**Alternatives considered**:

- Hide the tool because the endpoint is deprecated: rejected because the seed explicitly requires YT-223 and Layer 2 includes low-level compatibility/debugging tools.
- Present the endpoint as active: rejected because current official documentation and local Layer 1 metadata both mark it as deprecated or legacy.
- Replace it with `videoCategories_list`: rejected because that is a different upstream resource and a separate Layer 2 slice.

## Decision: Use API-key read auth and quota cost 1

**Rationale**: The local YT-123 Layer 1 wrapper declares `guideCategories.list` as API-key authenticated with official quota cost 1. The YouTube API reference states that requests generally use either an API key or OAuth token, while write/private-data requests require OAuth. `guideCategories.list` is a read-only legacy lookup, so API-key auth is the supported Layer 1 dependency behavior for this slice.

**Alternatives considered**:

- Require OAuth: rejected because the local Layer 1 wrapper rejects non-API-key auth and this feature is not a private-data or write operation.
- Allow mixed auth without a dependency: rejected because Layer 2 should expose the dependency-backed contract rather than invent unsupported auth modes.
- Hide quota from descriptions and examples: rejected by YT-202 and the constitution's contract-first requirement.

## Decision: Support `part` plus one selector, with a planned Layer 1 dependency update for `id` lookup if implemented

**Rationale**: The feature spec requires region-based and ID-based lookup. The local Layer 1 wrapper currently requires `part` plus `regionCode`; historical Google revision history refers to the `id` parameter for `guideCategories.list` in both batch retrieval and `notFound` error documentation. To keep the plan honest, implementation must begin with failing tests that expose the ID-lookup gap and then make the smallest Layer 1 wrapper metadata/validation update needed before publishing ID lookup through Layer 2.

**Alternatives considered**:

- Drop ID lookup from Layer 2: rejected because the approved YT-223 spec requires it.
- Implement ID lookup only in Layer 2 without changing Layer 1 metadata: rejected because Layer 2 must remain backed by Layer 1 wrapper behavior.
- Support arbitrary selectors: rejected because the public contract should stay close to the legacy endpoint and local dependency.

## Decision: Treat localization as optional and dependency-backed

**Rationale**: Historical YouTube documentation states that supported application languages can be used as the `hl` parameter when calling methods like `guideCategories.list`. The YT-223 spec requires localized text preference where supported. The implementation should expose `hl` only as an optional field with clear fallback behavior and should reject unsupported localization input without fabricating translations.

**Alternatives considered**:

- Make localization required: rejected because the core lookup is not localization-only.
- Fabricate translated category names when upstream omits them: rejected because Layer 2 must preserve near-raw endpoint results.
- Ignore localization entirely: rejected because the feature spec explicitly requires localized retrieval examples and validation.

## Decision: Return a near-raw guide-category list result with explicit legacy availability context

**Rationale**: Existing Layer 2 list tools preserve endpoint, quota, requested parts, selector context, item collections, empty results, and safe error categories. `guideCategories_list` should follow the same convention while adding a visible deprecated/unavailable state so callers can distinguish empty success, no match, deprecated endpoint, removed-resource behavior, endpoint unavailable, quota failure, and unexpected upstream failure.

**Alternatives considered**:

- Return only an availability warning: rejected because callers still need returned items when the legacy endpoint works.
- Enrich with active video categories or channel data: rejected because that crosses endpoint boundaries and violates Layer 2 scope.
- Collapse all deprecated/unavailable outcomes into `upstream_failure`: rejected because callers need actionable distinctions.

## Decision: Add a new `guide_categories` Layer 2 module

**Rationale**: There is no existing Layer 2 guide-categories module. The repository already organizes Layer 1 guide category code under `integrations/resources/guide_categories.py`; mirroring that in `tools/youtube_common/guide_categories.py` keeps legacy category handling separate from active video categories and unrelated channel/search tools.

**Alternatives considered**:

- Add the tool to `video_categories.py`: rejected because `guideCategories` and `videoCategories` are distinct resources with different lifecycle states.
- Add the tool to `channels.py`: rejected because channel category filtering is separately deprecated and not the same endpoint.
- Put endpoint-specific validation in generic shared contracts: rejected because selector, localization, and deprecated endpoint caveats belong to the concrete resource family.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: YT-201/YT-202 shared contracts and existing Layer 2 tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `deprecated_endpoint`, `endpoint_unavailable`, and `upstream_failure`. Legacy guide-category failures map naturally to those categories without exposing raw upstream diagnostics.

**Alternatives considered**:

- Preserve raw upstream error payloads only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Collapse every legacy failure into `deprecated_endpoint`: rejected because invalid request, not found, quota, unavailable, and unexpected failure are meaningfully different.
- Add a custom taxonomy for `guideCategories_list`: rejected because Layer 2 tools must share error conventions.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, Layer 1 ID-lookup alignment if needed, and default registry integration.

**Alternatives considered**:

- Implement first and add tests afterward: rejected by the constitution.
- Run only focused tests: rejected because full-suite validation is required before completion.
- Omit docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, existing YT-123 wrapper, neighboring Layer 2 tools, and official documentation resolve the endpoint identity, quota, auth mode, deprecated lifecycle state, selector dependency gap, response shape, dependencies, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-223 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/spec.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/guide_categories.py`
- Local neighboring Layer 2 plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/221-comment-threads-list/plan.md`
- Local sibling mutation plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/222-comment-threads-insert/plan.md`
- Official YouTube Data API revision history: https://developers.google.com/youtube/v3/revision_history
- Official YouTube Data API reference: https://developers.google.com/youtube/v3/docs
