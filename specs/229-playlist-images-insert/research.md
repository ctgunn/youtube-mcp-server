# Research: YT-229 Layer 2 Tool `playlistImages_insert`

## Decision: Expose one public Layer 2 tool named `playlistImages_insert`

**Rationale**: The YT-229 seed explicitly requires Layer 2 to expose `playlistImages_insert` as the low-level public tool for the upstream `playlistImages.insert` endpoint. The PRD requires one endpoint-backed Layer 2 tool per supported YouTube Data API operation, and the existing shared contracts use endpoint-style public names. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/spec.md`

**Alternatives considered**:

- Combine this with `playlistImages_list`. Rejected because listing and insertion have different request shapes, quota costs, mutation semantics, and upload requirements.
- Rename to `playlist_images_insert`. Rejected because the seed and PRD name the public Layer 2 tool `playlistImages_insert`.
- Defer public exposure to a Layer 3 workflow. Rejected because YT-229 is specifically a Layer 2 endpoint-backed tool slice.

## Decision: Reuse the existing YT-129 Layer 1 `playlistImages.insert` wrapper

**Rationale**: The Layer 1 wrapper exists under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, exposes operation key `playlistImages.insert`, requires OAuth access, requires `part`, requires `body`, requires `media`, records quota cost `50`, and keeps upload-sensitive contract notes visible. Reusing it preserves the Layer 1/Layer 2 boundary and avoids redefining upstream request execution in the public tool. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/research.md`

**Alternatives considered**:

- Add a separate Layer 2 transport path. Rejected because tools should depend on integration interfaces and not duplicate request execution, auth, quota, or upstream error logic.
- Change the Layer 1 wrapper first. Rejected because current Layer 1 metadata already matches YT-229's quota, auth, body, and media requirements.
- Mock insertion results only in Layer 2. Rejected because the public tool must be endpoint-backed through the Layer 1 capability.

## Decision: Require `part`, `body`, and `media` in the public input contract

**Rationale**: YT-129 models `playlistImages.insert` as a deterministic media-upload request with required `part`, required `body` metadata, and required `media` upload content. Existing Layer 2 tools narrow their public input schema to supported repo-local endpoint behavior and reject additional properties. The smallest testable YT-229 schema is therefore one required string `part`, one required metadata object `body`, and one required media object `media`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`

**Alternatives considered**:

- Treat `body` as optional and rely on upstream rejection. Rejected because the feature requires clear local validation.
- Treat `media` as optional for metadata-only creation. Rejected because the local Layer 1 contract requires upload content.
- Pass through arbitrary extra fields for future compatibility. Rejected because deterministic public contracts and clear invalid-request feedback are required by YT-201/YT-202 conventions.

## Decision: Represent media upload with safe descriptors and never expose raw upload content in metadata, examples, errors, or logs

**Rationale**: `playlistImages.insert` is upload-sensitive, and the constitution requires avoiding secret and unsafe diagnostic exposure. The public contract should accept a supported media payload shape for execution, but discovery metadata, examples, mapped results, validation failures, and sanitized error details must use safe summaries such as MIME type or content-reference presence rather than raw bytes, OAuth tokens, or private media content. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/.specify/memory/constitution.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/plan.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`

**Alternatives considered**:

- Echo raw upload content in validation details. Rejected because that risks leaking private media or binary payloads.
- Hide media requirements until execution. Rejected because callers must understand upload requirements before invoking the tool.
- Create a new shared upload subsystem in this slice. Rejected because one endpoint can use local validation and existing Layer 1 execution without new architecture.

## Decision: Keep quota cost `50` visible in metadata, descriptions, usage notes, examples, and results

**Rationale**: The YT-229 seed, YT-129 wrapper, and YT-229 specification agree that `playlistImages.insert` has official quota cost `50`. Existing Layer 2 tools make quota visible across discovery metadata, descriptions, examples, and near-raw results so client developers can understand cost before invocation and in returned context. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`

**Alternatives considered**:

- Put quota only in metadata. Rejected because the spec requires description and examples to visibly state quota cost.
- Recheck remote documentation during planning. Rejected because this workflow uses local feature requirements and no unresolved local discrepancy exists.
- Omit quota from successful results. Rejected because nearby Layer 2 endpoint-backed tools preserve quota context in public result wrappers.

## Decision: Model access as OAuth-required

**Rationale**: Both YT-129 and YT-229 require OAuth expectations to be visible. The public contract should reject missing OAuth locally as `authentication_failed` and map inaccessible playlist-image insertion attempts to `authorization_failed` unless the normalized upstream category provides a more specific safe category. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`

**Alternatives considered**:

- Allow API-key-only access. Rejected because repo-local contracts mark this endpoint OAuth-required.
- Hide auth constraints in implementation only. Rejected because callers must understand access limits before invoking the tool.
- Add delegated owner context in this slice. Rejected because delegation inputs are outside the YT-229 scope unless later local contracts explicitly add them.

## Decision: Preserve near-raw created-resource results with selected part, metadata, upload, auth, and quota context

**Rationale**: The feature spec requires a near-raw endpoint-backed shape that preserves returned playlist image resources, selected part context, insertion metadata context, upload context, quota context, and upstream fields. The result mapper should preserve returned `kind`, `etag`, `id`, `snippet`, and other upstream fields when present, without fabricating optional fields or adding enrichment. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/129-playlist-images-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`

**Alternatives considered**:

- Convert created playlist images into summaries only. Rejected because Layer 2 should stay close to the upstream endpoint.
- Return only an acknowledgment. Rejected because callers need created resource context for direct endpoint workflows.
- Add playlist, thumbnail, playlist-item, or media enrichment. Rejected because this slice is not a cross-endpoint or Layer 3 workflow.

## Decision: Use shared Layer 2 safe error categories and sanitize diagnostics

**Rationale**: Existing Layer 2 tools map local validation and normalized upstream failures into shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`. YT-229 should reuse that shape and sanitize diagnostics so OAuth tokens, raw media payloads, raw upstream bodies, stack traces, and unsafe request context are not exposed. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`

**Alternatives considered**:

- Raise raw upstream errors directly. Rejected because public MCP tools must provide safe, deterministic error messages.
- Introduce playlist-image-specific error categories. Rejected because shared categories are sufficient and simpler for clients.
- Include raw request or media context in details. Rejected because the constitution requires avoiding secret and unsafe diagnostic exposure.

## Decision: Extend the existing `playlist_images` Layer 2 module and register the insert descriptor in default discovery

**Rationale**: YT-228 already established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py` as the concrete Layer 2 resource-family module for `playlistImages` tools. Adding `playlistImages_insert` to that module, exporting it from `youtube_common/__init__.py`, and registering its descriptor in `dispatcher.py` is the smallest consistent public-tool path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

**Alternatives considered**:

- Put the tool in `playlists.py` or `playlist_items.py`. Rejected because playlist images are a separate resource family and endpoint.
- Create a second `playlist_images_insert.py` module. Rejected because the existing resource-family module is the cohesive home for `playlistImages` endpoint-backed tools.
- Create a broader playlist-media package. Rejected because one endpoint-backed tool does not justify a larger architecture.

## Decision: Validate with contract, unit, integration, registry, and full-suite checks

**Rationale**: The constitution requires Red-Green-Refactor, contract-first design, integration coverage, and a full repository test-suite run. YT-229 will add contract tests for metadata/examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, and final `pytest` plus `ruff check .`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/.specify/memory/constitution.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/plan.md`

**Alternatives considered**:

- Only add unit tests. Rejected because MCP-facing discovery and registry behavior require contract and integration coverage.
- Skip full-suite verification. Rejected by the constitution.
- Defer docstring checks to review. Rejected because new and changed Python functions must include reStructuredText docstrings as part of implementation.

## Clarification Closure

All planning-time clarifications for YT-229 are resolved in this research artifact. No unresolved clarification markers remain.
