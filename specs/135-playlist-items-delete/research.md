# Research: YT-135 Layer 1 Endpoint `playlistItems.delete`

## Decision: Support one deterministic delete request shape using one required playlist-item identifier

**Rationale**: Local requirements for YT-135 consistently describe `playlistItems.delete` as an OAuth-required delete operation whose input is the playlist-item identifier. Unlike the neighboring insert and update wrappers, the delete slice does not require `part` or `body`, and there is no repository-local requirement for optional delegation fields. The smallest contract that satisfies the spec is therefore one required `id` field that targets one playlist item for one delete attempt. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Require `part` by default. Rejected because local requirements for YT-135 identify the playlist-item identifier as the supported delete input and do not define `part` as mandatory for this slice.
- Reuse the update-style `body` shape. Rejected because that would widen the contract beyond the documented delete boundary.
- Add delegation fields speculatively. Rejected because current playlist-item wrappers do not expose them and YT-135 does not require them.

## Decision: Keep the request shape deterministic and reject unsupported fields before execution

**Rationale**: The existing Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-135 explicitly requires missing identifiers and unsupported request shapes to fail clearly, so the clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`

**Alternatives considered**:

- Forward loosely shaped delete requests upstream and document caveats only in markdown. Rejected because the repo's wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce malformed requests into a supported delete shape. Rejected because that weakens the Layer 1 contract and makes later Layer 2 and Layer 3 reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the current Layer 1 foundation rejects unexpected fields by design.

## Decision: Model `playlistItems.delete` as `oauth_required`, not mixed or public

**Rationale**: The local tool inventory explicitly marks `playlistItems.delete` as `Auth: oauth_required`, and the feature spec requires the OAuth requirement to be reviewable in maintainer-facing artifacts. Existing playlist-item mutation wrappers already enforce OAuth-only access, so the smallest consistent fit is `AuthMode.OAUTH_REQUIRED`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact indicates selector-dependent public access for this delete endpoint.
- API-key auth. Rejected because the local tool inventory explicitly says `oauth_required`.
- Leave auth behavior implicit in tests only. Rejected because maintainers need the access boundary visible in review surfaces and wrapper notes.

## Decision: Normalize success as a deletion acknowledgment that preserves the targeted playlist-item identity

**Rationale**: Local requirements describe `playlistItems.delete` output as a deletion acknowledgment payload and the feature spec requires successful outcomes to preserve enough request context for downstream layers to identify which playlist item was deleted. The best fit with existing delete helpers is therefore a small synthetic success result such as `playlistItemId` plus `isDeleted`, rather than returning the removed playlist-item resource or a bare boolean. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Return a full playlist-item payload after deletion. Rejected because the local tool inventory describes an acknowledgment-style outcome instead.
- Return only a generic boolean. Rejected because downstream reuse needs the targeted playlist-item identity to remain visible.
- Reuse plain `id` instead of `playlistItemId`. Rejected because neighboring higher-layer summaries prefer resource-specific identity keys.

## Decision: Keep optional delete modifiers out of the minimum supported contract unless they are explicitly documented in repository-local artifacts

**Rationale**: The YT-135 spec frames optional delete modifiers as in-scope only when the wrapper explicitly documents them as supported. The local tool inventory for `playlistItems.delete` names only the playlist-item identifier, so the smallest stable plan is to center the initial contract on `id`, then document all other top-level fields as outside the promised slice unless implementation work adds them deliberately. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Accept optional modifiers speculatively for flexibility. Rejected because speculative support weakens the contract-first boundary.
- Document likely upstream modifiers now without local evidence. Rejected because the plan should stay anchored to repository-local requirements and the current feature scope.
- Leave optional-modifier behavior unresolved until implementation. Rejected because Phase 0 must close planning-time contract questions.

## Decision: Make quota cost `50` visible in metadata, docstrings, consumer summaries, and feature-local contract artifacts

**Rationale**: The YT-135 seed requires the official quota cost of `50` to appear in method metadata and method comments or docstrings. Existing endpoint slices use wrapper review surfaces, feature-local contracts, and higher-layer summaries to keep quota visible without relying on external docs, and `playlistItems.delete` should follow that same pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep quota only in tests or planning docs. Rejected because the seed requires maintainer-visible wrapper-level quota documentation.
- Rely on external docs for quota awareness. Rejected because the repo requires quota visibility inside repository artifacts.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, target-state failures, and normalized upstream delete failures

**Rationale**: The YT-135 spec requires downstream callers to distinguish malformed requests, missing OAuth access, and validly shaped authorized requests that still fail because the playlist item is missing, already removed, unwritable, or rejected upstream. The current integration layer already separates local validation from normalized upstream failures, so the smallest consistent approach is to preserve separate normalized failure categories such as `invalid_request`, access-related failure, target-state or not-found failure, and upstream delete failure while keeping successful deletion acknowledgments distinct. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/120-comments-delete/research.md`

**Alternatives considered**:

- Flatten malformed requests and upstream rejections into one generic failure bucket. Rejected because caller remediation differs depending on whether the request is incomplete, unauthorized, or rejected after execution.
- Treat all validly shaped authorized requests as success regardless of upstream outcome. Rejected because that would erase meaningful failure boundaries required by the spec.
- Add a broader failure taxonomy at planning time. Rejected because the spec does not require extra categories beyond clear separation of the major outcome types.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 playlist-item test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and auth-validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent playlist-item and delete-oriented Layer 1 slices with minimal duplication. This is the smallest extension path for one OAuth-required playlist-item delete endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new playlist-items integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-auth-delete pattern

**Rationale**: Nearby playlist-item slices separate wrapper-level metadata requirements from more specific mutation-boundary guidance, while neighboring delete-oriented slices use an auth-delete contract to keep destructive-operation rules reviewable. Reusing that split for YT-135 keeps one contract focused on wrapper identity and request boundaries and a second focused on required delete input, OAuth requirements, unsupported delete shapes, and failure interpretation, which will be helpful for later playlist-item planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/134-playlist-items-update/contracts/layer1-playlist-items-update-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/131-playlist-images-delete/contracts/layer1-playlist-images-delete-auth-delete-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/135-playlist-items-delete/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and delete/auth behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint playlist-items contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-135 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
