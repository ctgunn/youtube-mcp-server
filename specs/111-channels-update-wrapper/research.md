# Research: YT-111 Layer 1 Endpoint `channels.update`

## Decision: Model `channels.update` as an OAuth-required write wrapper with one deterministic `part` plus `body` request shape

**Rationale**: Local product artifacts already define `channels.update` as `Auth: oauth_required` and describe the inputs as a writable channel resource body plus `part`. The current Layer 1 write-wrapper precedent uses required `part` and `body` fields with endpoint-specific validation rather than loosely shaped update payloads. This keeps the contract reviewable and consistent with `captions.update`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/spec.md`

**Alternatives considered**:

- Treat `channels.update` as mixed or conditional auth. Rejected because no local artifact indicates a public update path.
- Allow arbitrary update payloads without a stable `body` field. Rejected because existing Layer 1 patterns keep write wrappers deterministic and reviewable.
- Split channel updates into multiple wrapper variants by writable part. Rejected because the repo pattern remains one wrapper per endpoint slice.

## Decision: Represent writable-part limitations as explicit contract-visible rules rather than runtime-only behavior, with `brandingSettings` and `localizations` as the supported write surface for this slice

**Rationale**: The feature seed explicitly requires writable resource-part limitations to be documented in the wrapper contract, and the Layer 1 metadata standards require maintainers to understand boundary conditions before reading implementation details. The clean fit is to keep supported writable parts, read-only exclusions, and part-to-body alignment visible in wrapper notes and companion contract artifacts. This slice keeps the supported surface narrow and reviewable by allowing `brandingSettings` and `localizations`, which also aligns with the channel-banner handoff already documented elsewhere in the repository. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/102-layer1-metadata-standards/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/research.md`

**Alternatives considered**:

- Hide writable-part rules inside code only. Rejected because maintainers need reviewable contract guidance before reuse.
- Put writable-part rules only in tests. Rejected because tests prove behavior but do not serve as the canonical contract surface.
- Treat any provided part as tentatively supported until implementation decides otherwise. Rejected because the spec calls for clear unsupported-write failures.

## Decision: Validate that the selected writable `part` aligns with the provided update `body` and reject unsupported write shapes before execution

**Rationale**: Existing `EndpointRequestShape.validate_arguments()` already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators with stable `ValueError` messages. YT-111 requires unsupported or read-only update shapes to fail clearly before they are treated as supported wrapper usage, so request-shape validation is the smallest and safest enforcement point. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/spec.md`

**Alternatives considered**:

- Forward mismatched part/body combinations upstream and rely on upstream errors. Rejected because downstream callers need deterministic Layer 1 boundaries.
- Silently coerce the update body to match the selected part. Rejected because hidden coercion weakens the contract and complicates debugging.
- Accept extra fields for forward compatibility. Rejected because current Layer 1 patterns reject unexpected fields by design.

## Decision: Keep `channels.update` as a standard JSON `PUT` request without introducing new transport abstractions

**Rationale**: The current transport layer already supports `PUT` requests with JSON bodies generically, and nothing in the local artifacts indicates that `channels.update` needs a multipart or upload-specific transport path. The smallest implementation seam is to add endpoint-specific wrapper metadata and request validators while reusing the existing request builder. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`

**Alternatives considered**:

- Add a new dedicated transport helper for `channels.update`. Rejected because the shared `PUT` path already exists.
- Model `channels.update` like an upload endpoint. Rejected because local inventory describes a writable body plus `part`, not media upload.
- Delay transport assumptions until implementation. Rejected because the planning artifact must resolve technical unknowns before tasking.

## Decision: Preserve distinct failure boundaries for authorization, invalid update shape, and unsupported writable-part requests

**Rationale**: YT-111 explicitly requires downstream callers to distinguish authorization failures, incomplete or invalid bodies, and unsupported writable-part requests. Existing Layer 1 work already treats boundary clarity as a reusable contract property, and collapsing these failures would weaken higher-layer recovery decisions. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/110-channels-list-wrapper/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/research.md`

**Alternatives considered**:

- Flatten all invalid writes into one generic failure. Rejected because caller remediation differs between auth problems and request-shape problems.
- Treat unsupported writable-part updates as upstream-only failures. Rejected because the wrapper contract must make unsupported local boundaries explicit.
- Over-specialize failure categories beyond the feature needs. Rejected because the smallest useful split is auth vs invalid write shape vs unsupported write boundary.

## Decision: Keep the implementation seam centered on the existing integration wrapper, consumer, and transport modules with contract coverage under the channel-focused test suite

**Rationale**: Recent endpoint slices show a stable extension path through `wrappers.py`, `youtube.py`, optional consumer summaries, and the Layer 1 unit, transport, integration, and contract tests. Reusing that seam is the smallest and safest approach for a single update wrapper. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_channels_contract.py`

**Alternatives considered**:

- Add a new `channels.py` integration module immediately. Rejected because one endpoint slice does not justify new architecture.
- Limit validation to unit tests only. Rejected because the constitution requires integration and regression coverage.
- Put all endpoint-specific assertions into generic metadata tests only. Rejected because writable-part and auth-write boundaries are channel-specific and need focused contract coverage.

## Decision: Keep channel-specific review notes visible, including how `channelBanners.insert` output can feed later `channels.update` usage

**Rationale**: Existing channel-banner notes already preserve the returned banner URL for later `channels.update` reuse, which indicates downstream channel-management work benefits from reviewable cross-feature guidance. YT-111 should keep similar channel-specific notes visible so higher-layer authors can understand likely write inputs without reverse-engineering implementation. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`

**Alternatives considered**:

- Omit channel-specific notes and focus only on generic write semantics. Rejected because channel-management reuse is part of the feature’s rationale.
- Put banner-related guidance only in the banner feature. Rejected because YT-111 maintainers should understand cross-slice reuse from the update contract as well.
- Expand this feature into banner-management orchestration. Rejected because that exceeds the endpoint-wrapper scope.

## Clarification Closure

All planning-time clarifications for YT-111 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
