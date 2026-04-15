# Research: YT-115 Layer 1 Endpoint `channelSections.delete`

## Decision: Require one channel-section identifier and allow only optional delegated owner context

**Rationale**: The local feature spec defines YT-115 as a real `DELETE /channelSections` request, which implies one delete target rather than selector-style lookup or body-based mutation. Existing internal delete-wrapper precedent for `captions.delete` uses one required target identifier with optional delegation inputs, and the current Layer 1 request-shape contract rejects undocumented fields by design. The smallest consistent request contract is therefore one required channel-section identifier plus optional `onBehalfOfContentOwner` and `onBehalfOfContentOwnerChannel` guidance. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md`

**Alternatives considered**:

- Require `part` on delete requests. Rejected because the local seed and neighboring delete-wrapper pattern treat delete as a single-target destructive operation rather than a partial-resource mutation.
- Reuse `body`-based update-style inputs. Rejected because delete is not a writable resource-body update path.
- Allow arbitrary extra query fields for flexibility. Rejected because current Layer 1 wrappers use deterministic request shapes and reject undocumented inputs.

## Decision: Model `channelSections.delete` as an OAuth-required owner-scoped delete wrapper

**Rationale**: The YT-115 seed explicitly requires OAuth expectations to be documented, and neighboring channel-section write wrappers already model mutation paths as `oauth_required`. Deleting a channel section is at least as ownership-sensitive as insert or update, so the wrapper metadata and contracts should make it explicit that authorized access is mandatory and that public API-key-only deletion is out of scope. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/research.md`

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact describes a public delete path for channel-section removal.
- Runtime-only auth handling without metadata notes. Rejected because maintainers need the boundary visible before code inspection.
- Separate delegated-delete auth mode. Rejected because the repository models delegation as optional inputs and notes rather than a separate auth enum.

## Decision: Keep partner delegation as optional guidance, not a separate delete mode

**Rationale**: Existing write wrappers in this repository describe `onBehalfOfContentOwner` and related channel-owner delegation inputs as optional context layered on top of OAuth-required access. Reusing that pattern for `channelSections.delete` keeps the internal contract uniform across channel-section insert, update, and this delete slice while still making partner-managed deletion expectations reviewable. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/113-channel-sections-insert/contracts/layer1-channel-sections-insert-auth-write-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/contracts/layer1-channel-sections-update-auth-write-contract.md`

**Alternatives considered**:

- Create a dedicated delegated-delete wrapper. Rejected because the repository uses one wrapper per endpoint slice.
- Omit delegation guidance entirely. Rejected because the local spec explicitly calls for supported delegation context to remain reviewable.
- Treat delegation as a replacement for OAuth. Rejected because existing contracts treat delegation as additive context only.

## Decision: Make quota cost `50` and destructive delete expectations visible in metadata, docstrings, and contract artifacts

**Rationale**: The YT-115 seed requires the official quota cost of `50` to be recorded in metadata and method comments or docstrings. Existing Layer 1 slices keep quota discoverable through wrapper metadata review surfaces, feature-local contracts, and tests. YT-115 should follow that same repository pattern while also surfacing that the operation is destructive and target-specific. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md`

**Alternatives considered**:

- Keep quota visibility only in planning docs. Rejected because the seed requires metadata and docstring visibility.
- Rely on external YouTube documentation for quota review. Rejected because nearby wrapper slices keep quota discoverable inside repository artifacts.
- Document destructive behavior only in tests. Rejected because maintainers need a reviewable contract before reading test code.

## Decision: Preserve distinct failure boundaries between auth failures, invalid delete shapes, and target-state or upstream delete failures

**Rationale**: The YT-115 spec requires downstream callers to distinguish invalid delete requests from missing authorization or ineligible target sections. Existing Layer 1 delete and update planning already treats boundary clarity as part of the wrapper contract. The smallest useful split is to keep auth failures, local validation failures, and target-state or normalized upstream failures separate so later layers can choose whether to correct input, request access, retry, or stop. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/115-channel-sections-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/114-channel-sections-update/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

**Alternatives considered**:

- Flatten all delete failures into one generic invalid-request outcome. Rejected because caller remediation differs between auth, shape, and target-state problems.
- Treat already-missing sections as successful no-op deletes. Rejected because the local spec calls for explicit target-state interpretation guidance.
- Over-specialize local failure categories beyond the feature need. Rejected because one clear split between validation, auth, and target-state or upstream failures is sufficient for higher-layer planning.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific builder pattern used by channel sections and delete wrappers, `youtube.py` is the transport seam for request construction and normalized delete payloads, `consumer.py` already exposes higher-layer summaries for `channelSections.list`, `insert`, and `update`, and the existing unit, contract, integration, and transport tests already cover nearby channel-section operations with minimal duplication. This is the smallest extension path for one more channel-sections endpoint slice. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channel_sections_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new dedicated module just for channel-section delete orchestration. Rejected because one endpoint slice does not justify new architecture.
- Limit validation to metadata-only tests. Rejected because the constitution requires integration and regression coverage.
- Skip higher-layer summary updates. Rejected because channel-sections features already use consumer summaries to prove downstream reviewability.

## Clarification Closure

All planning-time clarifications for YT-115 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
