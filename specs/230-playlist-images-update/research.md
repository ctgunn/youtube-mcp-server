# Research: YT-230 Layer 2 Tool `playlistImages_update`

## Decision: Expose one public Layer 2 tool named `playlistImages_update`

**Rationale**: The YT-230 seed explicitly requires Layer 2 to expose `playlistImages_update` as the low-level public tool for the upstream `playlistImages.update` endpoint. The PRD requires one endpoint-backed Layer 2 tool per supported YouTube Data API operation, and the existing shared contracts use endpoint-style public names. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/230-playlist-images-update/spec.md`

**Alternatives considered**:

- Combine this with `playlistImages_insert`. Rejected because insertion and update have different target identity requirements, mutation semantics, examples, and failure modes.
- Rename to `playlist_images_update`. Rejected because the seed and PRD name the public Layer 2 tool `playlistImages_update`.
- Defer public exposure to a Layer 3 workflow. Rejected because YT-230 is specifically a Layer 2 endpoint-backed tool slice.

## Decision: Reuse the existing YT-130 Layer 1 `playlistImages.update` wrapper

**Rationale**: The Layer 1 wrapper exists under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, exposes operation key `playlistImages.update`, requires OAuth access, requires `part`, requires `body`, requires `media`, records quota cost `50`, and documents target identity through `body.id` plus owning playlist context through `body.snippet.playlistId`. Reusing it preserves the Layer 1/Layer 2 boundary and avoids redefining upstream request execution in the public tool. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/130-playlist-images-update/spec.md`

**Alternatives considered**:

- Add a separate Layer 2 transport path. Rejected because tools should depend on integration interfaces and not duplicate request execution, auth, quota, or upstream error logic.
- Change the Layer 1 wrapper first. Rejected because current Layer 1 metadata already matches YT-230's quota, auth, body, and media requirements.
- Mock update results only in Layer 2. Rejected because the public tool must be endpoint-backed through the Layer 1 capability.

## Decision: Require `part`, target-identifying `body`, and `media` in the public input contract

**Rationale**: YT-130 models `playlistImages.update` as a deterministic media-update request with required `part`, required `body` metadata identifying the target playlist image, and required `media` upload content. Existing Layer 2 tools narrow their public input schema to supported repo-local endpoint behavior and reject additional properties. The smallest testable YT-230 schema is therefore one required string `part`, one required metadata object `body`, and one required media object `media`.

**Alternatives considered**:

- Treat `body.id` as optional and rely on upstream rejection. Rejected because the feature requires clear local validation and target identity is central to update semantics.
- Treat `media` as optional for metadata-only update. Rejected because the local Layer 1 contract requires update media content.
- Pass through arbitrary extra fields for future compatibility. Rejected because deterministic public contracts and clear invalid-request feedback are required by YT-201/YT-202 conventions.

## Decision: Use `body.id` and `body.snippet.playlistId` as the local target identity boundary

**Rationale**: The existing Layer 1 wrapper notes that `body.id` identifies the existing playlist image and `body.snippet.playlistId` preserves owning playlist context. Requiring both makes caller intent explicit, supports safer result context, and helps distinguish missing-target validation failures from upstream missing-resource or authorization failures.

**Alternatives considered**:

- Require only `body.id`. Rejected because the Layer 1 notes explicitly preserve owning playlist context and update examples should show the caller what playlist boundary is being changed.
- Accept a top-level `id` selector. Rejected because the Layer 1 update wrapper models identity inside `body`, and Layer 2 should not redefine the upstream wrapper contract.
- Infer target identity from media metadata. Rejected because media payloads are not a reliable or safe identity source.

## Decision: Represent media upload with safe descriptors and never expose raw upload content in metadata, examples, errors, or logs

**Rationale**: `playlistImages.update` is upload-sensitive, and the constitution requires avoiding secret and unsafe diagnostic exposure. The public contract should accept a supported media payload shape for execution, but discovery metadata, examples, mapped results, validation failures, and sanitized error details must use safe summaries such as MIME type or content-reference presence rather than raw bytes, OAuth tokens, or private media content. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/.specify/memory/constitution.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/229-playlist-images-insert/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`

**Alternatives considered**:

- Echo raw upload content in validation details. Rejected because that risks leaking private media or binary payloads.
- Hide media requirements until execution. Rejected because callers must understand upload requirements before invoking the tool.
- Create a new shared upload subsystem in this slice. Rejected because one endpoint can use local validation and existing Layer 1 execution without new architecture.

## Decision: Keep quota cost `50` visible in metadata, descriptions, usage notes, examples, and results

**Rationale**: The YT-230 seed, YT-130 wrapper, and YT-230 specification agree that `playlistImages.update` has official quota cost `50`. Existing Layer 2 tools make quota visible across discovery metadata, descriptions, examples, and near-raw results so client developers can understand cost before invocation and in returned context.

**Alternatives considered**:

- Put quota only in metadata. Rejected because the spec requires description and examples to visibly state quota cost.
- Recheck remote documentation during planning. Rejected because this workflow uses local feature requirements and no unresolved local discrepancy exists.
- Omit quota from successful results. Rejected because nearby Layer 2 endpoint-backed tools preserve quota context in public result wrappers.

## Decision: Model access as OAuth-required

**Rationale**: Both YT-130 and YT-230 require OAuth expectations to be visible. The public contract should reject missing OAuth locally as `authentication_failed` and map inaccessible playlist-image updates to `authorization_failed` unless the normalized upstream category provides a more specific safe category.

**Alternatives considered**:

- Allow API-key-only access. Rejected because repo-local contracts mark this endpoint OAuth-required.
- Hide auth constraints in implementation only. Rejected because callers must understand access limits before invoking the tool.
- Add delegated owner context in this slice. Rejected because delegation inputs are outside the YT-230 scope unless later local contracts explicitly add them.

## Decision: Preserve near-raw updated-resource results with selected part, metadata, upload, auth, and quota context

**Rationale**: The feature spec requires a near-raw endpoint-backed shape that preserves returned playlist image resources, selected part context, update metadata context, upload context, quota context, and upstream fields. The result mapper should preserve returned `kind`, `etag`, `id`, `snippet`, and other upstream fields when present, without fabricating optional fields or adding enrichment.

**Alternatives considered**:

- Convert updated playlist images into summaries only. Rejected because Layer 2 should stay close to the upstream endpoint.
- Return only an acknowledgment. Rejected because callers need updated resource context for direct endpoint workflows.
- Add playlist, thumbnail, playlist-item, or media enrichment. Rejected because this slice is not a cross-endpoint or Layer 3 workflow.

## Decision: Use shared Layer 2 safe error categories and sanitize diagnostics

**Rationale**: Existing Layer 2 tools map local validation and normalized upstream failures into shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`. YT-230 should reuse that shape and sanitize diagnostics so OAuth tokens, raw media payloads, raw upstream bodies, stack traces, and unsafe request context are not exposed.

**Alternatives considered**:

- Raise raw upstream errors directly. Rejected because public MCP tools must provide safe, deterministic error messages.
- Introduce playlist-image-specific error categories. Rejected because shared categories are sufficient and simpler for clients.
- Include raw request or media context in details. Rejected because the constitution requires avoiding secret and unsafe diagnostic exposure.

## Decision: Extend the existing `playlist_images` Layer 2 module and register the update descriptor in default discovery

**Rationale**: YT-228 and YT-229 already established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py` as the concrete Layer 2 resource-family module for `playlistImages` tools. Adding `playlistImages_update` to that module, exporting it from `youtube_common/__init__.py`, and registering its descriptor in `dispatcher.py` is the smallest consistent public-tool path.

**Alternatives considered**:

- Put the tool in `playlists.py` or `playlist_items.py`. Rejected because playlist images are a separate resource family and endpoint.
- Create a second `playlist_images_update.py` module. Rejected because the existing resource-family module is the cohesive home for `playlistImages` endpoint-backed tools.
- Create a broader playlist-media package. Rejected because one endpoint-backed tool does not justify a larger architecture.

## Decision: Validate with contract, unit, integration, registry, and full-suite checks

**Rationale**: The constitution requires Red-Green-Refactor, contract-first design, integration coverage, and a full repository test-suite run. YT-230 will add contract tests for metadata/examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, and final `pytest` plus `ruff check .`.

**Alternatives considered**:

- Only add unit tests. Rejected because MCP-facing discovery and registry behavior require contract and integration coverage.
- Skip full-suite verification. Rejected by the constitution.
- Defer docstring checks to review. Rejected because new and changed Python functions must include reStructuredText docstrings as part of implementation.

## Clarification Closure

All planning-time clarifications for YT-230 are resolved in this research artifact. No unresolved clarification markers remain.
