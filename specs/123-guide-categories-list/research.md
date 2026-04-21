# Research: YT-123 Layer 1 Endpoint `guideCategories.list`

## Decision: Support exactly one deterministic request shape using `part` plus `regionCode`

**Rationale**: The local tool inventory for `guideCategories.list` identifies `part` and `regionCode` as the relevant request inputs, and the YT-123 spec frames this slice around region-specific guide-category lookup rather than a broad near-raw parameter surface. The smallest stable wrapper contract is therefore one required `part` field plus one required `regionCode` field, with no additional selector ambiguity or silent fallback behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Treat `regionCode` as optional. Rejected because the local tool inventory names it as part of the request shape and the feature spec expects a region-specific lookup path.
- Allow broader arbitrary query fields for future flexibility. Rejected because current Layer 1 request shapes reject undocumented inputs by design.
- Support multiple region inputs in one request. Rejected because one deterministic region lookup per request is simpler and matches the current endpoint-slice pattern.

## Decision: Keep optional modifiers out of scope for this slice

**Rationale**: Unlike nearby list endpoints, the local tool inventory for `guideCategories.list` does not call out pagination, ordering, or additional lookup modifiers. Limiting this slice to `part` plus `regionCode` keeps the internal wrapper narrowly aligned to the documented repository scope and avoids inventing support boundaries that later slices would need to unwind. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Add common list-style modifiers such as `maxResults` or `pageToken`. Rejected because those are not part of the in-repo request inventory for this endpoint.
- Accept undocumented fields and pass them through. Rejected because undocumented passthrough weakens reviewability and testability.
- Delay request-shape decisions until implementation. Rejected because the constitution requires contract-first planning.

## Decision: Model `guideCategories.list` as an API-key wrapper with a deprecated lifecycle state and an explicit unavailable-behavior caveat

**Rationale**: The local tool inventory marks `guideCategories.list` with `Auth: api_key`, while the seed explicitly requires the wrapper contract to flag the method as deprecated or unavailable in current platform behavior where official docs say so. The existing metadata model supports reviewable lifecycle states such as `deprecated`, `limited`, and `inconsistent-docs`; choosing `deprecated` with a maintainer-facing caveat note best matches the documented expectation that the endpoint is not recommended for general reuse and may be unavailable in current platform behavior. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/spec.md`

**Alternatives considered**:

- Mark the wrapper as `limited` instead of `deprecated`. Rejected because the seed language is stronger and explicitly references deprecated or unavailable current behavior.
- Mark the wrapper as `inconsistent-docs`. Rejected because the in-repo requirement is to surface a deprecated-or-unavailable caveat, not primarily to record documentation inconsistency.
- Leave lifecycle state `active` and only mention caveats in prose. Rejected because the metadata standard expects lifecycle reviewability in wrapper metadata itself.

## Decision: Keep quota cost `1`, API-key access, and lifecycle caveat visible in metadata, docstrings, consumer summaries, and feature-local contracts

**Rationale**: The YT-123 seed requires the official quota cost of `1` to be recorded in method metadata and method comments or docstrings, and the spec requires maintainers to determine supported inputs, standard access expectations, and the lifecycle caveat without reading implementation details. Existing Layer 1 slices keep these decisions discoverable through wrapper metadata, consumer summaries, and feature-local contracts, so YT-123 should follow that same review pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep lifecycle guidance only in planning artifacts. Rejected because maintainers need the caveat visible in wrapper review surfaces during implementation and reuse.
- Put quota visibility only in tests. Rejected because the seed requires metadata and docstring visibility.
- Omit higher-layer summary coverage. Rejected because nearby Layer 1 slices use consumer summaries to prove reviewable downstream reuse.

## Decision: Preserve explicit boundaries between invalid request shapes, lifecycle-aware unavailable outcomes, and successful empty results

**Rationale**: The YT-123 spec requires downstream callers to distinguish malformed requests from cases where the endpoint is deprecated, unavailable, or otherwise not usable in the current platform context. Existing Layer 1 retrieval work already keeps valid empty lists on the success path rather than treating them as failures. The smallest useful split for this endpoint is therefore to keep invalid-request failures, lifecycle-aware unavailable outcomes, and successful retrievals with zero or more items as distinct reviewable states. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/123-guide-categories-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/121-comment-threads-list/research.md`

This plan uses the stable internal category `lifecycle_unavailable` for validly shaped `guideCategories.list` requests that fail because the endpoint is deprecated or unavailable in current platform behavior, while keeping malformed requests on `invalid_request` and empty result sets on the success path.

**Alternatives considered**:

- Flatten lifecycle-aware failures into generic invalid-request outcomes. Rejected because caller remediation differs when the request shape is wrong versus when the endpoint itself is no longer generally usable.
- Treat empty results as lifecycle failure evidence. Rejected because a valid request with zero items is not the same as an unavailable endpoint.
- Over-specialize many lifecycle failure categories. Rejected because one explicit lifecycle-aware unavailable boundary is sufficient for this slice.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, and the existing unit, contract, integration, and transport tests cover adjacent Layer 1 retrieval slices with minimal duplication. This is the smallest extension path for one lifecycle-caveated reference-data endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new legacy-categories integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-behavior pattern

**Rationale**: Nearby Layer 1 slices separate wrapper-level metadata requirements from more specific auth, selector, or behavioral interpretation guidance. Reusing that split for YT-123 keeps one contract focused on wrapper identity and request boundaries and a second focused on region lookup and lifecycle-aware behavior, which will be helpful for later legacy-category and localization planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/112-channel-sections-list-wrapper/contracts/layer1-channel-sections-list-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/122-comment-threads-insert/contracts/layer1-comment-threads-insert-auth-write-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because lifecycle guidance and wrapper requirements become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint legacy-categories contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-123 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
