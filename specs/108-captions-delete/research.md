# Research: YT-108 Layer 1 Endpoint `captions.delete`

## Decision: Require one caption track identifier and allow only optional delegated ownership context

**Rationale**: The YT-108 seed defines the feature as a real `DELETE /captions` request, which implies a single delete target rather than selector-style listing or download modifiers. The current Layer 1 pattern keeps request contracts deterministic with `EndpointRequestShape.validate_arguments()`, and nearby caption wrappers already treat `onBehalfOfContentOwner` as optional delegation rather than a second wrapper mode. The smallest consistent request contract is therefore one required caption-track identifier plus optional `onBehalfOfContentOwner`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`

**Alternatives considered**:

- Require `part` on delete requests. Rejected because the seed describes `DELETE /captions`, unlike the list, insert, and update wrappers that explicitly require `part`.
- Reuse `body`-based update-style inputs. Rejected because delete is a single-target destructive operation, not a resource-body mutation.
- Allow arbitrary extra query arguments for future flexibility. Rejected because the current Layer 1 request-shape contract rejects undocumented fields by design.

## Decision: Model `captions.delete` as `oauth_required` with ownership-sensitive notes

**Rationale**: Every existing caption-management write path in the repository is modeled as `oauth_required`, and the YT-108 seed explicitly calls out OAuth and content-owner delegation behavior. Deletion is more sensitive than listing or downloading, so the wrapper metadata and contract artifacts should make it visible that authorized access alone may still be insufficient if the caller lacks ownership or management rights over the target caption track. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/contracts/layer1-captions-update-auth-media-contract.md`

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact describes an API-key or public selector path for caption deletion.
- Runtime-only ownership handling without metadata notes. Rejected because later caption-management work needs the boundary visible before code inspection.
- Separate delegated-delete auth mode. Rejected because the repository models delegation as notes and optional input, not a new auth enum.

## Decision: Keep delegation as optional guidance, not a separate delete mode

**Rationale**: Existing caption slices consistently describe `onBehalfOfContentOwner` as optional delegation context layered on top of OAuth-required access. Reusing that pattern for delete keeps the internal contract uniform across `captions.list`, `captions.insert`, `captions.update`, and `captions.download`, while still making partner-managed deletion expectations reviewable. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/104-captions-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/research.md`

**Alternatives considered**:

- Create a dedicated delegated-delete wrapper. Rejected because the current Layer 1 pattern keeps one wrapper per endpoint slice.
- Ignore delegation for YT-108. Rejected because the seed explicitly requires delegation behavior to be documented.
- Treat delegation as a replacement for OAuth. Rejected because existing caption contracts treat delegation as additive context only.

## Decision: Make quota cost `50` visible in metadata, docstrings, and contract artifacts

**Rationale**: The YT-108 seed requires the official quota cost of `50` to appear in metadata and method comments or docstrings. Existing caption features use wrapper metadata review surfaces, feature-local contracts, and tests to keep quota reviewable without requiring external documentation, and YT-108 should follow that same repository pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`

**Alternatives considered**:

- Keep quota visibility only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Rely on upstream YouTube docs for quota review. Rejected because nearby caption slices keep quota discoverable inside repository artifacts.

## Decision: Preserve a distinct failure boundary between access-related and target-not-found delete failures

**Rationale**: The YT-108 spec requires downstream callers to distinguish permission, ownership, and identifier problems. The current integration layer already normalizes upstream failures and the `captions.download` artifacts explicitly preserve access-versus-not-found distinction. Deletion should follow that precedent so destructive failure handling stays reviewable and later higher layers can react differently to access denial, ownership mismatch, and missing targets. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

**Alternatives considered**:

- Flatten all delete failures into one generic not-found outcome. Rejected because it would hide ownership and permission problems.
- Treat already-missing caption tracks as successful no-op deletes. Rejected because the spec requires clear failure distinction for downstream callers.
- Return ambiguous success with warning metadata. Rejected because the existing executor model already separates success and failure outcomes cleanly.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder pattern used by all current caption wrappers, `youtube.py` is the transport seam that handles endpoint path and method construction, `consumer.py` provides the higher-layer review surface pattern used in caption features, and the current unit, contract, integration, and transport tests already cover caption operations with minimal duplication. This is the smallest extension path for one more caption endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_captions_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Introduce a new caption-delete module immediately. Rejected because one endpoint slice does not justify a new abstraction boundary.
- Limit validation to unit tests only. Rejected because the constitution requires integration and regression coverage across contract boundaries.
- Defer higher-layer delete review surfaces to later features. Rejected because the repository already uses consumer summaries to prove wrapper reviewability for caption operations.
