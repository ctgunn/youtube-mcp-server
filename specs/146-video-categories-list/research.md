# Research: YT-146 Layer 1 Endpoint `videoCategories.list`

## Decision: Support one deterministic request shape using `part` plus exactly one selector from `id` or `regionCode`, with optional `hl`

**Rationale**: The local tool inventory for `videoCategories.list` names `part`, `id`, `regionCode`, and `hl` as the supported inputs, while the YT-146 spec emphasizes region-specific lookup behavior and clear request boundaries. The smallest contract that preserves both the local inventory and deterministic Layer 1 validation is one required `part` value, exactly one selector from `id` or `regionCode`, and an optional `hl` display-language hint that does not replace the primary selector. This keeps the wrapper broad enough for category-id review and region browsing without permitting ambiguous multi-selector requests. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/146-video-categories-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Support only `part` plus `regionCode`. Rejected because the local tool inventory explicitly includes `id`, and omitting it would narrow the wrapper below the repo-documented endpoint surface.
- Require both `id` and `regionCode`. Rejected because that creates an unnecessary dependency between two distinct lookup modes and would not be a deterministic selector boundary.
- Treat `hl` as required. Rejected because the local tool inventory does not elevate `hl` to a required selector, and optional display-language guidance keeps the wrapper simpler.

## Decision: Keep pagination and other undocumented modifiers out of scope for this slice

**Rationale**: The in-repo tool inventory for `videoCategories.list` does not call out paging, ordering, or other modifiers beyond `part`, `id`, `regionCode`, and `hl`. Existing Layer 1 request shapes reject undocumented fields rather than silently forwarding them. Limiting this slice to the documented local inputs keeps the wrapper narrowly aligned to the repository scope and avoids inventing support boundaries that later slices would need to unwind. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Add common list-style modifiers such as `pageToken` or `maxResults`. Rejected because those are not part of the in-repo request inventory for this endpoint.
- Accept undocumented fields and pass them through. Rejected because undocumented passthrough weakens reviewability and testability.
- Delay request-shape decisions until implementation. Rejected because the constitution requires contract-first planning.

## Decision: Model `videoCategories.list` as an active API-key wrapper with explicit selector and region notes rather than a lifecycle caveat

**Rationale**: The local tool inventory marks `videoCategories.list` with `Auth: api_key`, and the YT-146 seed requires the 1-unit quota cost and region-specific lookup behavior to be documented. Unlike `guideCategories.list`, neither the seed nor the local tool inventory calls out deprecation or inconsistent platform behavior for `videoCategories.list`. The smallest repo-consistent choice is therefore `auth_mode=api_key`, `quota_cost=1`, the standard active lifecycle, and maintainer-facing notes that explain selector usage, region behavior, and optional `hl` guidance. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Add a deprecated or limited lifecycle state similar to `guideCategories.list`. Rejected because the repo-local requirements do not call out a lifecycle caveat for this endpoint.
- Keep selector and region guidance only in planning artifacts. Rejected because maintainers need the lookup purpose visible in wrapper review surfaces during implementation and reuse.
- Put quota visibility only in tests. Rejected because the seed requires metadata and docstring visibility.

## Decision: Keep quota cost `1`, API-key access, selector rules, and region guidance visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The YT-146 seed requires the official quota cost of `1` to be recorded in method metadata and method comments or docstrings, and the spec requires maintainers to determine supported inputs, access expectations, and region behavior without reading implementation details. Existing Layer 1 slices keep these decisions discoverable through wrapper metadata, consumer summaries, and feature-local contracts, so YT-146 should follow that same review pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/146-video-categories-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep region guidance only in the spec. Rejected because maintainers and higher-layer authors need the reuse guidance visible in implementation-adjacent review surfaces.
- Omit higher-layer summary coverage. Rejected because nearby Layer 1 slices use consumer summaries to prove reviewable downstream reuse.
- Record auth expectations only in the plan. Rejected because reviewable wrapper metadata is the shared repo-local pattern.

## Decision: Preserve explicit boundaries between invalid request shapes and successful retrieval outcomes, including empty results

**Rationale**: The YT-146 spec requires downstream callers to distinguish malformed requests from valid video-category lookups, and it explicitly treats valid empty results as a separate case from invalid input. Existing Layer 1 retrieval work already keeps valid empty lists on the success path rather than treating them as failures. The smallest useful split for this endpoint is therefore to keep invalid-request failures explicit while keeping successful retrievals with zero or more items on the success path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/146-video-categories-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/research.md`

**Alternatives considered**:

- Treat empty results as a failure state. Rejected because a valid request with zero returned items is not the same as an invalid request.
- Flatten empty results and validation failures into a generic failure bucket. Rejected because caller remediation differs when the selector shape is wrong versus when the lookup simply returns no items.
- Add a more specialized failure taxonomy at planning time. Rejected because the spec does not require additional categories for this slice.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites, with one new feature-specific contract test module

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent Layer 1 retrieval slices with minimal duplication. A dedicated `test_layer1_video_categories_contract.py` module is the smallest clean place to assert the feature-local contract files for selector and region behavior without overloading the legacy or localization contract suites. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new category-utilities integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Reuse `test_layer1_localization_contract.py` directly. Rejected because `videoCategories.list` combines selector and region semantics that do not map cleanly to the localization-only contract suite.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-behavior pattern

**Rationale**: Nearby Layer 1 slices separate wrapper-level metadata requirements from more specific selector, auth, or behavioral interpretation guidance. Reusing that split for YT-146 keeps one contract focused on wrapper identity and request boundaries and a second focused on selector choice, region behavior, optional `hl` interpretation, and empty-result handling, which will be helpful for later video-catalog and regional browsing planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/145-video-abuse-report-reasons/contracts/layer1-video-abuse-report-reasons-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/146-video-categories-list/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because selector behavior and wrapper requirements become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint video-category contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-146 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
