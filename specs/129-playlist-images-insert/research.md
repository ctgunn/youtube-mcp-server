# Research: YT-129 Layer 1 Endpoint `playlistImages.insert`

## Decision: Require one stable metadata field plus one stable media-upload field in the minimum `playlistImages.insert` request contract

**Rationale**: Local artifacts are consistent that `playlistImages.insert` is a creation endpoint that requires metadata plus media-upload input. The feature spec and the tool inventory both define the endpoint as taking metadata plus media-upload inputs, so the minimum contract should require one reviewable `body` metadata payload field and one reviewable `media` upload field rather than exposing metadata-only or upload-only paths. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Allow metadata-only requests and rely on upstream rejection. Rejected because YT-129 explicitly requires invalid shapes to be rejected or clearly flagged before execution.
- Model every possible upstream field in the initial contract. Rejected because the existing Layer 1 pattern favors a smaller reviewable contract per endpoint slice.
- Treat upload content as optional for the first slice. Rejected because that would contradict the local tool inventory and the YT-129 spec.

## Decision: Keep the request shape deterministic and reject unsupported combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-129 explicitly calls for missing metadata, missing upload input, and malformed upload payloads to fail clearly. The clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's existing wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that weakens the Layer 1 contract and makes later Layer 2 and Layer 3 reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the current Layer 1 foundation rejects unexpected fields by design.

## Decision: Treat upload requirements as part of the wrapper contract, not a transport-only detail

**Rationale**: YT-129 acceptance criteria call out media-upload requirements as wrapper-contract material, and nearby upload-oriented slices already keep auth and upload semantics visible in wrapper metadata and contract artifacts before implementation details are inspected. For YT-129, upload semantics should be equally reviewable so higher layers know they must provide both playlist-image metadata and upload content before reusing the wrapper. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/research.md`

**Alternatives considered**:

- Hide upload requirements inside transport code or executor logic. Rejected because maintainers are supposed to understand the contract before reading implementation.
- Put upload guidance only in tests. Rejected because tests prove behavior but do not provide the intended maintainer-facing contract surface.
- Split upload semantics into a second wrapper. Rejected because YT-129 is scoped to one endpoint-specific Layer 1 wrapper.

## Decision: Model `playlistImages.insert` as `oauth_required`, not mixed or public

**Rationale**: The local tool inventory explicitly marks `playlistImages_insert` as `Auth: oauth_required`, and the Layer 1 standards require each wrapper to record auth mode in metadata for downstream reuse. Nothing in the repo suggests an API-key path for this endpoint, so the smallest consistent fit is `AuthMode.OAUTH_REQUIRED`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact indicates selector-dependent public access for this creation endpoint.
- API-key auth. Rejected because the local tool inventory explicitly says `oauth_required`.

## Decision: Keep optional create modifiers out of the minimum supported contract unless they are explicitly documented in repository-local artifacts

**Rationale**: The YT-129 spec frames optional modifiers as in-scope only when the wrapper explicitly documents them as supported. The local tool inventory for `playlistImages.insert` names metadata plus media-upload inputs but does not identify additional required optional modifiers, so the smallest stable plan is to center the initial contract on `part`, `body`, and `media`, then document all other fields as outside the promised slice unless implementation research later adds them deliberately. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Accept optional modifiers speculatively for flexibility. Rejected because speculative support weakens the contract-first boundary.
- Document likely upstream modifiers now without local evidence. Rejected because the plan should stay anchored to repository-local requirements and the current feature scope.
- Leave optional-modifier behavior unresolved until implementation. Rejected because Phase 0 must close planning-time contract questions.

## Decision: Make quota cost `50` visible in metadata, docstrings, consumer summaries, and feature-local contract artifacts

**Rationale**: The YT-129 seed requires the official quota cost of `50` to appear in method metadata and method comments or docstrings. Existing endpoint slices use wrapper review surfaces, feature-local contracts, and higher-layer summaries to keep quota visible without relying on external docs, and `playlistImages.insert` should follow that same pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep quota only in tests or planning docs. Rejected because the PRD and seed require maintainer-visible wrapper-level quota documentation.
- Rely on external docs for quota awareness. Rejected because the repo requires quota visibility inside repository artifacts.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, normalized upstream create failures, and successful creation outcomes

**Rationale**: The YT-129 spec requires downstream callers to distinguish malformed requests, missing OAuth access, and validly shaped authorized requests that still fail upstream for resource-specific reasons. The current integration layer already separates local validation from normalized upstream failures, so the smallest consistent approach is to preserve separate normalized failure categories such as `invalid_request` and access-related failure while leaving authorized upstream rejections distinct from successful creation outcomes. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/research.md`

**Alternatives considered**:

- Flatten malformed requests and upstream rejections into one generic failure bucket. Rejected because caller remediation differs depending on whether the request is incomplete, unauthorized, or rejected after execution.
- Treat all validly shaped authorized requests as success regardless of upstream outcome. Rejected because that would erase meaningful failure boundaries required by the spec.
- Add a broader failure taxonomy at planning time. Rejected because the spec does not require extra categories beyond clear separation of the major outcome types.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent upload-oriented Layer 1 slices with minimal duplication. This is the smallest extension path for one OAuth-required playlist-image creation endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_playlist_images_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new playlist-images integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-auth-upload pattern

**Rationale**: Nearby upload-oriented Layer 1 slices separate wrapper-level metadata requirements from more specific auth and upload-boundary guidance. Reusing that split for YT-129 keeps one contract focused on wrapper identity and request boundaries and a second focused on required create inputs, OAuth requirements, unsupported upload shapes, and failure interpretation, which will be helpful for later playlist-image planning. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/contracts/layer1-captions-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-auth-upload-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and upload/auth behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint playlist-images contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-129 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
