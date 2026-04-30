# Research: YT-134 Layer 1 Endpoint `playlistItems.update`

## Decision: Model `playlistItems.update` as an OAuth-required write wrapper with one deterministic `part` plus `body` request shape

**Rationale**: Local product artifacts already define `playlistItems.update` as `Auth: oauth_required` and describe the inputs as `part` plus a playlist-item resource body. The current Layer 1 write-wrapper pattern uses required `part` and `body` fields with endpoint-specific validation rather than loosely shaped update payloads, which keeps the contract reviewable and consistent with nearby update-style features. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/134-playlist-items-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/111-channels-update-wrapper/research.md`

**Alternatives considered**:

- Treat `playlistItems.update` as mixed or conditional auth. Rejected because no local artifact indicates a public update path.
- Allow arbitrary update payloads without a stable `body` field. Rejected because existing Layer 1 patterns keep write wrappers deterministic and reviewable.
- Split playlist-item updates into multiple wrapper variants by writable part. Rejected because the repository pattern remains one wrapper per endpoint slice.

## Decision: Keep the minimum supported update contract centered on `part=snippet` with `body.id` plus writable `body.snippet` data

**Rationale**: The feature specification requires one required playlist-item identifier, one writable-part selection, and supported writable update data. The smallest contract that satisfies those requirements and fits the existing playlist-item creation precedent is a `snippet`-scoped update body that identifies the existing playlist item through `body.id` and carries writable playlist-item fields through `body.snippet`. That keeps endpoint identity, target-resource identity, and writable-change intent visible in one reviewable request shape. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/134-playlist-items-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/133-playlist-items-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/133-playlist-items-insert/research.md`

**Alternatives considered**:

- Accept identifier-only requests and rely on upstream rejection for missing writable data. Rejected because YT-134 requires deterministic validation before execution.
- Require only `body.id` and leave all writable-field semantics implicit. Rejected because maintainers need reviewable guidance about what update data is actually supported.
- Promise support for every possible playlist-item update field immediately. Rejected because the repository's Layer 1 planning pattern favors a smaller reviewable contract per endpoint slice.

## Decision: Require the minimum writable `snippet` payload to preserve playlist and referenced-video identity, while treating optional update fields as out of scope unless explicitly documented

**Rationale**: The safest reviewable update contract is one where the writable body makes the updated playlist-item identity and core playlist/video association explicit through `body.snippet.playlistId` and `body.snippet.resourceId.videoId`, just as the insert slice already centers those fields. This preserves enough context for downstream layers to understand what was updated and allows clear validation when unsupported writable fields are attempted. Optional fields such as `snippet.position` should remain outside the guaranteed contract unless the wrapper explicitly documents support for them. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/134-playlist-items-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/133-playlist-items-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`

**Alternatives considered**:

- Support `snippet.position` and other writable fields automatically in the initial slice. Rejected because it broadens validation and failure-surface scope without being required by the current feature.
- Leave optional-field behavior unresolved until implementation. Rejected because Phase 0 must close planning-time contract questions.
- Silently ignore unsupported writable fields for forward compatibility. Rejected because higher-layer callers need explicit unsupported-boundary behavior.

## Decision: Keep request validation deterministic and reject unsupported field combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-134 explicitly requires missing identifiers, missing writable data, unsupported writable fields, and incompatible auth to fail clearly. The clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/134-playlist-items-update/spec.md`

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's existing wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that would make higher-layer reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the Layer 1 foundation rejects unexpected fields by design.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, normalized upstream update failures, and successful update outcomes

**Rationale**: The YT-134 spec requires downstream callers to distinguish malformed requests, missing OAuth access, unsupported writable-field boundaries, and validly shaped authorized requests that still fail upstream because the playlist item is missing, unwritable, or otherwise ineligible for update. The smallest consistent approach is to preserve separate normalized failure categories such as `invalid_request`, access-related failure, and upstream update rejection while keeping successful update outcomes distinct. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/134-playlist-items-update/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/research.md`

**Alternatives considered**:

- Flatten malformed requests and upstream rejections into one generic failure bucket. Rejected because caller remediation differs depending on whether the request is incomplete, unauthorized, or rejected after execution.
- Treat all validly shaped authorized requests as success regardless of upstream outcome. Rejected because that would erase meaningful failure boundaries required by the spec.
- Add a broader failure taxonomy at planning time. Rejected because the spec does not require extra categories beyond clear separation of the major outcome types.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 playlist-item test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring mutation wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent playlist-item slices with minimal duplication. This is the smallest extension path for one OAuth-required playlist-item update endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_items_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new playlist-items integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts separating wrapper identity from auth and writable-boundary guidance

**Rationale**: Nearby mutation-oriented Layer 1 slices separate wrapper-level metadata requirements from more specific auth and write-boundary guidance. Reusing that split for YT-134 keeps one contract focused on wrapper identity and response expectations and a second focused on required update inputs, OAuth requirements, supported writable-field boundaries, and failure interpretation, which will be helpful for later playlist-item update planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/contracts/layer1-playlist-images-update-auth-media-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/133-playlist-items-insert/contracts/layer1-playlist-items-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/133-playlist-items-insert/contracts/layer1-playlist-items-insert-auth-write-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and update-boundary behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint playlist-items contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-134 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
