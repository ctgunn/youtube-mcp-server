# Research: YT-124 Layer 1 Endpoint `i18nLanguages.list`

## Decision: Support exactly one deterministic request shape using `part` plus `hl`

**Rationale**: The local tool inventory for `i18nLanguages.list` identifies `part` and `hl` as the relevant request inputs, and the YT-124 spec frames this slice around localization-language lookup rather than a broad near-raw parameter surface. The smallest stable wrapper contract is therefore one required `part` field plus one required `hl` field, with no selector ambiguity or silent fallback behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/124-i18n-languages-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Treat `hl` as optional. Rejected because the local tool inventory names it as part of the supported localization-language lookup contract and the spec expects the display-language context to remain visible.
- Allow broader arbitrary query fields for future flexibility. Rejected because current Layer 1 request shapes reject undocumented inputs by design.
- Support multiple localization-language views in one request. Rejected because one deterministic lookup per request is simpler and matches the current endpoint-slice pattern.

## Decision: Keep optional modifiers out of scope for this slice

**Rationale**: Unlike some nearby list endpoints, the local tool inventory for `i18nLanguages.list` does not call out pagination, ordering, or additional lookup modifiers. Limiting this slice to `part` plus `hl` keeps the internal wrapper narrowly aligned to the documented repository scope and avoids inventing support boundaries that later slices would need to unwind. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/124-i18n-languages-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Add common list-style modifiers such as `pageToken` or `maxResults`. Rejected because those are not part of the in-repo request inventory for this endpoint.
- Accept undocumented fields and pass them through. Rejected because undocumented passthrough weakens reviewability and testability.
- Delay request-shape decisions until implementation. Rejected because the constitution requires contract-first planning.

## Decision: Model `i18nLanguages.list` as an active API-key wrapper with localization guidance in maintainer-facing notes

**Rationale**: The local tool inventory marks `i18nLanguages.list` with `Auth: api_key`, while the YT-124 seed requires the wrapper contract to document localization-lookup usage and quota visibility. The existing metadata model supports reviewable lifecycle states when needed, but nothing in the seed or tool inventory requires a caveated lifecycle state for this endpoint. The smallest repo-consistent choice is therefore `auth_mode=api_key`, `quota_cost=1`, the standard active lifecycle, and localization guidance recorded in wrapper notes and contracts instead of a lifecycle caveat. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/spec.md`

**Alternatives considered**:

- Add a reviewable lifecycle state with a caveat note. Rejected because the repo-local requirements do not call out deprecation, limited availability, or documentation inconsistency for `i18nLanguages.list`.
- Keep localization guidance only in planning artifacts. Rejected because maintainers need the lookup purpose visible in wrapper review surfaces during implementation and reuse.
- Put quota visibility only in tests. Rejected because the seed requires metadata and docstring visibility.

## Decision: Keep quota cost `1`, API-key access, and localization guidance visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The YT-124 seed requires the official quota cost of `1` to be recorded in method metadata and method comments or docstrings, and the spec requires maintainers to determine supported inputs, API-key access expectations, and localization-lookup purpose without reading implementation details. Existing Layer 1 slices keep these decisions discoverable through wrapper metadata, consumer summaries, and feature-local contracts, so YT-124 should follow that same review pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/124-i18n-languages-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep localization guidance only in the spec. Rejected because maintainers and higher-layer authors need the reuse guidance visible in implementation-adjacent review surfaces.
- Omit higher-layer summary coverage. Rejected because nearby Layer 1 slices use consumer summaries to prove reviewable downstream reuse.
- Record auth expectations only in the plan. Rejected because reviewable wrapper metadata is the shared repo-local pattern.

## Decision: Preserve explicit boundaries between invalid request shapes and successful retrieval outcomes, including empty results

**Rationale**: The YT-124 spec requires downstream callers to distinguish malformed requests from valid localization lookups, and it explicitly treats valid empty results as a separate case from invalid input. Existing Layer 1 retrieval work already keeps valid empty lists on the success path rather than treating them as failures. The smallest useful split for this endpoint is therefore to keep invalid-request failures explicit while keeping successful retrievals with zero or more items on the success path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/124-i18n-languages-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/research.md`

**Alternatives considered**:

- Treat empty results as a failure state. Rejected because a valid request with zero returned items is not the same as an invalid request.
- Flatten empty results and validation failures into a generic failure bucket. Rejected because caller remediation differs when the request shape is wrong versus when the lookup simply returns no items.
- Add a more specialized failure taxonomy at planning time. Rejected because the spec does not require additional categories for this slice.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent Layer 1 retrieval slices with minimal duplication. This is the smallest extension path for one localization-reference endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new localization integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-behavior pattern

**Rationale**: Nearby Layer 1 slices separate wrapper-level metadata requirements from more specific selector, auth, or behavioral interpretation guidance. Reusing that split for YT-124 keeps one contract focused on wrapper identity and request boundaries and a second focused on localization lookup usage and empty-result interpretation, which will be helpful for later localization planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/contracts/layer1-guide-categories-list-region-lifecycle-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because localization behavior and wrapper requirements become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint localization contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-124 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
