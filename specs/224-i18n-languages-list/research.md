# Research: Layer 2 Tool `i18nLanguages_list`

## Decision: Expose `i18nLanguages_list` as an active low-level localization-language lookup tool

**Rationale**: The seed slice YT-224 requires a Layer 2 tool named `i18nLanguages_list` that maps directly to YouTube `i18nLanguages.list`. The current official YouTube Data API reference includes `i18nLanguages.list` as an active endpoint that returns application languages supported by YouTube. Unlike `guideCategories.list`, this endpoint is present in current reference navigation and has no deprecation caveat in the local seed or official page.

**Alternatives considered**:

- Hide the tool behind higher-level localization workflows: rejected because Layer 2 requires one public endpoint-backed tool per supported upstream resource method.
- Present it as a translation or language detection tool: rejected because the endpoint returns application-language reference data only.
- Mark it deprecated by analogy with guide categories: rejected because current official documentation and local requirements do not support that lifecycle state.

## Decision: Use API-key read auth and quota cost 1

**Rationale**: The local YT-124 Layer 1 wrapper declares `i18nLanguages.list` as API-key authenticated with official quota cost 1. The current official reference states the method costs 1 quota unit. The endpoint is read-only reference-data lookup, so API-key auth is the dependency-backed Layer 1 behavior for this slice.

**Alternatives considered**:

- Require OAuth: rejected because the local Layer 1 wrapper rejects non-API-key auth and this feature is not a private-data or write operation.
- Allow mixed auth without a dependency: rejected because Layer 2 should expose dependency-backed behavior rather than invent unsupported auth modes.
- Hide quota from descriptions and examples: rejected by YT-202 and the constitution's contract-first requirement.

## Decision: Require `part` and support optional `hl` in the public Layer 2 contract

**Rationale**: The current official endpoint requires `part`, expects the value `snippet`, and documents `hl` as optional with default `en_US`. YT-224 requires clear localization lookup usage. The public Layer 2 tool should therefore require `part`, accept optional `hl`, and document display-language fallback behavior. This keeps the public contract close to the upstream endpoint.

**Alternatives considered**:

- Require `hl` in Layer 2 because YT-124 did: rejected because YT-224 is a public endpoint-backed tool and should follow the current official endpoint shape unless there is a stronger project constraint.
- Omit `hl`: rejected because localization display behavior is the main endpoint-specific option and the seed requires localization lookup usage documentation.
- Support additional filters or selectors: rejected because the official endpoint only defines `part` and `hl` query parameters for this method.

## Decision: Plan a narrow Layer 1 dependency alignment if `hl` remains required locally

**Rationale**: The existing Layer 1 localization wrapper currently declares `part` and `hl` as required for deterministic YT-124 coverage. That is stricter than the current official endpoint and the YT-224 public contract. Implementation should begin with failing tests that expose the mismatch, then make the smallest Layer 1 metadata/validation update needed to support optional `hl` while preserving existing valid `part` plus `hl` behavior.

**Alternatives considered**:

- Work around Layer 1 by always injecting `hl=en_US` in Layer 2: rejected unless tests show it is the smallest safe compatibility path, because it hides the public request shape from the dependency.
- Leave Layer 1 unchanged and require `hl` publicly: rejected because it would diverge from the current official endpoint.
- Rewrite the localization Layer 1 family broadly: rejected because this slice only needs dependency alignment for `i18nLanguages.list`.

## Decision: Return a near-raw localization-language list result with active availability context

**Rationale**: Existing Layer 2 list tools preserve endpoint, quota, requested parts, optional selector/localization context, item collections, empty results, and safe error categories. `i18nLanguages_list` should follow the same convention while using active availability context and preserving the upstream list response fields: `kind`, `etag`, and `items` containing `i18nLanguage` resources.

**Alternatives considered**:

- Return only a simplified list of language names: rejected because Layer 2 tools should stay close to upstream responses.
- Enrich languages with regions, captions, or translation availability: rejected because that crosses endpoint boundaries and violates Layer 2 scope.
- Treat empty item collections as errors: rejected because the feature spec requires successful empty results to remain distinct from failures.

## Decision: Add a new `localization` Layer 2 module

**Rationale**: There is no existing Layer 2 localization module. The repository already organizes Layer 1 localization code under `integrations/resources/localization.py` for `i18nLanguages` and `i18nRegions`; mirroring that in `tools/youtube_common/localization.py` keeps localization reference tools cohesive and prepares for YT-225 without mixing these tools into guide categories, captions, search, or channel modules.

**Alternatives considered**:

- Add the tool to `guide_categories.py`: rejected because guide categories are legacy category resources, not localization reference resources.
- Add the tool to `examples.py` or generic shared contracts only: rejected because endpoint-specific validation, examples, result mapping, and handler behavior belong in a concrete resource-family module.
- Create a dedicated `i18n_languages.py`: rejected because the Layer 1 family groups `i18nLanguages` and `i18nRegions` together as localization, and the same grouping can support the next adjacent slice.

## Decision: Map validation and upstream failures to shared safe Layer 2 categories

**Rationale**: YT-201/YT-202 shared contracts and existing Layer 2 tools use safe public categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`. The official `i18nLanguages.list` page defines no method-specific errors, so general upstream errors should map to those shared categories without exposing raw diagnostics.

**Alternatives considered**:

- Preserve raw upstream error payloads only: rejected because public MCP clients need stable shared categories and safe diagnostics.
- Add method-specific error names: rejected because the official method does not define unique error messages.
- Collapse every upstream failure into `upstream_failure`: rejected because auth, quota, invalid request, and availability failures are meaningfully different to callers.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, Layer 1 optional-`hl` alignment if needed, and default registry integration.

**Alternatives considered**:

- Implement first and add tests afterward: rejected by the constitution.
- Run only focused tests: rejected because full-suite validation is required before completion.
- Omit docstring work from planning: rejected because every new or changed Python function must have a reStructuredText docstring.

## Decision: No unresolved clarifications remain

**Rationale**: The seed, feature spec, constitution, current codebase, existing YT-124 wrapper, neighboring Layer 2 tools, and current official documentation resolve the endpoint identity, quota, auth mode, active lifecycle state, response shape, dependency gap, and validation boundaries.

**Alternatives considered**:

- Ask for additional scope confirmation: rejected because the feature description explicitly names YT-224 and the seed provides enough scope detail.

## Sources

- Local seed: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`
- Local feature spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/224-i18n-languages-list/spec.md`
- Local Layer 1 wrapper: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/localization.py`
- Local neighboring Layer 2 plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/223-guidecategories-list/plan.md`
- Official YouTube Data API `i18nLanguages.list` reference: https://developers.google.com/youtube/v3/docs/i18nLanguages/list
- Official YouTube Data API `i18nLanguage` resource reference: https://developers.google.com/youtube/v3/docs/i18nLanguages
