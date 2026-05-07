# Research: YT-144 Layer 1 Endpoint `thumbnails.set`

## Decision: Require one stable target field plus one stable media-upload field in the minimum `thumbnails.set` request contract

**Rationale**: Local artifacts are consistent that `thumbnails.set` is an upload-oriented update endpoint whose input centers on `videoId` plus media-upload input. The YT-144 spec and the tool inventory both define the endpoint as taking `videoId` plus upload input, so the minimum contract should require one reviewable `videoId` field and one reviewable `media` upload field rather than exposing target-only or upload-only paths. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Allow `videoId`-only requests and rely on upstream rejection. Rejected because YT-144 explicitly requires invalid shapes to be rejected or clearly flagged before execution.
- Model every possible upstream field in the initial contract. Rejected because the existing Layer 1 pattern favors a smaller reviewable contract per endpoint slice.
- Treat upload content as optional for the first slice. Rejected because that would contradict the local tool inventory and the YT-144 spec.

## Decision: Keep the request shape deterministic and reject unsupported combinations before execution

**Rationale**: The current Layer 1 contract model already enforces required fields, rejects unexpected fields, and supports endpoint-specific validators. YT-144 explicitly calls for missing `videoId`, missing upload input, and malformed upload payloads to fail clearly. The clean fit is to define a narrow allowed field set and validate it in the wrapper contract before the executor runs. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`

**Alternatives considered**:

- Forward loosely shaped requests upstream and document caveats only in markdown. Rejected because the repo's existing wrapper pattern uses `EndpointRequestShape.validate_arguments()` to make boundaries enforceable.
- Silently coerce incomplete requests into a supported shape. Rejected because that weakens the Layer 1 contract and makes later Layer 2 and Layer 3 reuse ambiguous.
- Accept arbitrary extra fields for future compatibility. Rejected because the current Layer 1 foundation rejects unexpected fields by design.

## Decision: Treat upload requirements as part of the wrapper contract, not a transport-only detail

**Rationale**: YT-144 acceptance criteria call out media-upload requirements as wrapper-contract material, and nearby upload-oriented slices already keep auth and upload semantics visible in wrapper metadata and contract artifacts before implementation details are inspected. For YT-144, upload semantics should be equally reviewable so higher layers know they must provide both a target `videoId` and upload content before reusing the wrapper. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`

**Alternatives considered**:

- Hide upload requirements inside transport code or executor logic. Rejected because maintainers are supposed to understand the contract before reading implementation.
- Put upload guidance only in tests. Rejected because tests prove behavior but do not provide the intended maintainer-facing contract surface.
- Split upload semantics into a second wrapper. Rejected because YT-144 is scoped to one endpoint-specific Layer 1 wrapper.

## Decision: Model `thumbnails.set` as `oauth_required`, not mixed or public

**Rationale**: The local tool inventory explicitly marks `thumbnails_set` as `Auth: oauth_required`, and the Layer 1 standards require each wrapper to record auth mode in metadata for downstream reuse. Nothing in the repo suggests an API-key path for this endpoint, so the smallest consistent fit is `AuthMode.OAUTH_REQUIRED`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`

**Alternatives considered**:

- Mixed or conditional auth. Rejected because no local artifact indicates selector-dependent public access for this thumbnail-update endpoint.
- API-key auth. Rejected because the local tool inventory explicitly says `oauth_required`.

## Decision: Keep optional upload modifiers out of the minimum supported contract unless they are explicitly documented in repository-local artifacts

**Rationale**: The YT-144 spec frames optional modifiers as in-scope only when the wrapper explicitly documents them as supported. The local tool inventory for `thumbnails.set` names `videoId` plus media-upload inputs but does not identify additional required optional modifiers, so the smallest stable plan is to center the initial contract on `videoId` and `media`, then document all other fields as outside the promised slice unless implementation research later adds them deliberately. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/tool-specs.md`

**Alternatives considered**:

- Accept optional modifiers speculatively for flexibility. Rejected because speculative support weakens the contract-first boundary.
- Document likely upstream modifiers now without local evidence. Rejected because the plan should stay anchored to repository-local requirements and the current feature scope.
- Leave optional-modifier behavior unresolved until implementation. Rejected because Phase 0 must close planning-time contract questions.

## Decision: Use generic upload-payload validation unless repository-local evidence requires stricter endpoint-specific image constraints

**Rationale**: Existing upload-style wrappers use different validation depths depending on what the repository already documents. `channelBanners.insert` carries explicit local image-size and MIME rules, while `playlistImages.insert` only requires reviewable `media` mapping presence. YT-144 currently has repository-local requirements for a required upload payload but no checked-in thumbnail-specific size or MIME policy, so the smallest evidence-based plan is to require a non-empty `media` mapping with visible upload semantics and avoid inventing constraints not yet captured in the repo. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`

**Alternatives considered**:

- Reuse the banner-specific 16:9 and 6 MB rules. Rejected because those constraints are documented for `channelBanners.insert`, not `thumbnails.set`.
- Skip upload validation entirely and trust runtime failures. Rejected because YT-144 requires clear rejection or flagging of unsupported upload shapes.
- Invent thumbnail-specific limits without repository evidence. Rejected because the plan should not claim unsupported upstream specifics.

## Decision: Make quota cost `50` visible in metadata, docstrings, consumer summaries, and feature-local contract artifacts

**Rationale**: The YT-144 seed requires the official quota cost of `50` to appear in method metadata and method comments or docstrings. Existing endpoint slices use wrapper review surfaces, feature-local contracts, and higher-layer summaries to keep quota visible without relying on external docs, and `thumbnails.set` should follow that same pattern. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Keep quota only in tests or planning docs. Rejected because the seed requires maintainer-visible wrapper-level quota documentation.
- Rely on external docs for quota awareness. Rejected because the repo requires quota visibility inside repository artifacts.

## Decision: Normalize success as a thumbnail-update acknowledgment that preserves the targeted video identity

**Rationale**: Local requirements describe `thumbnails.set` as an upload-style update whose successful outcome must preserve enough request context for downstream layers to identify which video thumbnail changed. The best fit with existing upload-oriented helpers is a compact normalized result that keeps `videoId`, a stable update indicator, and any returned thumbnail URL when available, rather than a bare boolean or an unprocessed upstream payload. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`

**Alternatives considered**:

- Return only a generic boolean. Rejected because downstream reuse needs the targeted video identity to remain visible.
- Return a full raw upstream payload without normalization. Rejected because the Layer 1 pattern favors stable summary-friendly result fields.
- Treat the response exactly like `channelBanners.insert`. Rejected because YT-144 must keep the target video identity visible, not only the returned upload URL.

## Decision: Preserve explicit boundaries between invalid request shapes, access failures, target-video failures, normalized upstream update failures, and successful thumbnail updates

**Rationale**: The YT-144 spec requires downstream callers to distinguish malformed requests, missing OAuth access, and validly shaped authorized requests that still fail because the video is unavailable, not writable, or otherwise ineligible for thumbnail updates. The current integration layer already separates local validation from normalized upstream failures, so the smallest consistent approach is to preserve separate normalized failure categories such as `invalid_request`, `auth`, `target_video`, and `upstream_service` while keeping successful thumbnail-update acknowledgments distinct. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/spec.md`

**Alternatives considered**:

- Flatten malformed requests and upstream rejections into one generic failure bucket. Rejected because caller remediation differs depending on whether the request is incomplete, unauthorized, or rejected after execution.
- Treat all validly shaped authorized requests as success regardless of upstream outcome. Rejected because that would erase meaningful failure boundaries required by the spec.
- Reuse only a generic `not_found` category. Rejected because the spec explicitly calls for a broader target-video boundary that may include ownership or eligibility restrictions in addition to pure absence.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring upload wrappers, `youtube.py` is the transport seam for request construction and normalized response parsing, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent upload-oriented Layer 1 slices with minimal duplication. This is the smallest extension path for one OAuth-required thumbnail update endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new thumbnail-specific integration submodule for one endpoint slice. Rejected because one wrapper does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts mirroring the existing wrapper-plus-auth-upload pattern

**Rationale**: Nearby upload-oriented Layer 1 slices separate wrapper-level metadata requirements from more specific auth and upload-boundary guidance. Reusing that split for YT-144 keeps one contract focused on wrapper identity and request boundaries and a second focused on required update inputs, OAuth requirements, unsupported upload shapes, and failure interpretation, which will be helpful for later thumbnail and video-management work. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/109-channel-banners-insert/contracts/layer1-channel-banners-insert-wrapper-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/contracts/layer1-playlist-images-insert-auth-upload-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/144-thumbnails-set/spec.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and upload/auth behavior become harder to review cleanly together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint thumbnails contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-144 are resolved in this research artifact. No `NEEDS CLARIFICATION` markers remain.
