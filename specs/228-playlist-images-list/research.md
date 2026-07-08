# Research: YT-228 Layer 2 Tool `playlistImages_list`

## Decision: Expose one public Layer 2 tool named `playlistImages_list`

**Rationale**: The YT-228 seed explicitly requires Layer 2 to expose `playlistImages_list` as the low-level public tool for the upstream `playlistImages.list` endpoint. The PRD requires one endpoint-backed Layer 2 tool per supported YouTube Data API operation, and the existing shared contracts use endpoint-style public names. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/spec.md`

**Alternatives considered**:

- Combine this with playlist item or playlist listing tools. Rejected because YT-228 owns playlist-image listing and those tools expose different upstream resources.
- Rename to `playlist_images_list`. Rejected because the seed and PRD name the public Layer 2 tool `playlistImages_list`.
- Defer public exposure to a Layer 3 workflow. Rejected because YT-228 is specifically a Layer 2 endpoint-backed tool slice.

## Decision: Reuse the existing YT-128 Layer 1 `playlistImages.list` wrapper

**Rationale**: The Layer 1 wrapper already exists under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, exposes operation key `playlistImages.list`, requires OAuth access, requires `part`, records quota cost `1`, supports `playlistId` and `id` as exclusive selectors, restricts paging to `playlistId`, rejects undocumented modifiers, and preserves empty result sets as successful outcomes. Reusing it preserves the Layer 1/Layer 2 boundary and avoids redefining upstream request execution in the public tool. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`

**Alternatives considered**:

- Add a separate Layer 2 transport path. Rejected because tools should depend on integration interfaces and not duplicate request execution, auth, quota, or upstream error logic.
- Change the Layer 1 wrapper first. Rejected because current Layer 1 metadata already matches YT-228's quota, auth, selector, and paging requirements.
- Mock playlist-image results only in Layer 2. Rejected because the public tool must be endpoint-backed through the Layer 1 capability.

## Decision: Support required `part` plus exactly one selector from `playlistId` or `id`

**Rationale**: YT-128 models `playlistImages.list` as a deterministic request with required `part` and exactly one selector from `playlistId` or `id`. Existing Layer 2 tools narrow their public input schema to supported repo-local endpoint behavior and reject additional properties. The smallest testable YT-228 schema is therefore one required string `part`, optional selector fields `playlistId` and `id`, and validation that exactly one selector is present. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`

**Alternatives considered**:

- Treat selectors as optional. Rejected because the endpoint contract requires one lookup mode.
- Allow both selectors together. Rejected because selector ambiguity weakens testability and conflicts with the Layer 1 contract.
- Pass through unknown selector fields for future compatibility. Rejected because deterministic public contracts and clear invalid-request feedback are required by YT-201/YT-202 conventions.

## Decision: Allow paging only for `playlistId` lookup

**Rationale**: The Layer 1 YT-128 contract allows `pageToken` and `maxResults` only for playlist-scoped retrieval and rejects paging for direct `id` lookup. YT-228 should preserve that boundary in the public Layer 2 contract so direct image lookup stays deterministic and playlist-scoped retrieval can handle multiple image resources. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/contracts/layer1-playlist-images-list-filter-modes-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/validators/playlist_images.py`

**Alternatives considered**:

- Allow paging for both selector modes. Rejected because direct ID lookup does not need list-style paging and the local Layer 1 contract rejects it.
- Reject all paging to keep the request shape smaller. Rejected because playlist-scoped retrieval supports paging in the existing Layer 1 contract.
- Allow undocumented paging flags to pass through when present. Rejected because undocumented passthrough weakens contract reviewability.

## Decision: Keep quota cost `1` visible in metadata, descriptions, usage notes, examples, and results

**Rationale**: The YT-228 seed, YT-128 wrapper, and YT-228 specification agree that `playlistImages.list` has official quota cost `1`. Existing Layer 2 tools make quota visible across discovery metadata, descriptions, examples, and near-raw results so client developers can understand cost before invocation and in returned context. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_images.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py`

**Alternatives considered**:

- Put quota only in metadata. Rejected because the spec requires description and examples to visibly state quota cost.
- Recheck remote documentation during planning. Rejected because this workflow uses local feature requirements and no unresolved local discrepancy exists.
- Omit quota from successful results. Rejected because nearby Layer 2 endpoint-backed tools preserve quota context in public result wrappers.

## Decision: Model access as OAuth-required

**Rationale**: Both YT-128 and YT-228 require OAuth expectations to be visible. The public contract should reject missing OAuth locally as `authentication_failed` and map inaccessible playlist-image data to `authorization_failed` unless the normalized upstream category provides a more specific safe category. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py`

**Alternatives considered**:

- Allow API-key-only access. Rejected because repo-local contracts mark this endpoint OAuth-required.
- Hide auth constraints in implementation only. Rejected because callers must understand access limits before invoking the tool.
- Add delegated owner context in this slice. Rejected because delegation inputs are outside the YT-228 scope.

## Decision: Preserve near-raw list results with selected part, selector, paging, and empty-success semantics

**Rationale**: The feature spec requires a near-raw endpoint-backed shape that preserves returned playlist image resources, selected part context, selected lookup context, paging context when applicable, quota context, and upstream fields. YT-128 also treats empty playlist-image collections as valid success when request shape and access are valid. The result mapper should preserve returned `items`, `kind`, `etag`, `nextPageToken`, `prevPageToken`, and `pageInfo` when present, without fabricating optional fields or adding enrichment. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/128-playlist-images-list/research.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`

**Alternatives considered**:

- Convert playlist images into summaries. Rejected because Layer 2 should stay close to the upstream endpoint.
- Treat empty `items` as an error. Rejected because a valid request may return no matching playlist images.
- Add playlist, playlist-item, thumbnail, or media enrichment. Rejected because this slice is not a cross-endpoint or Layer 3 workflow.

## Decision: Use shared Layer 2 safe error categories and sanitize diagnostics

**Rationale**: Existing Layer 2 tools map local validation and normalized upstream failures into shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`. YT-228 should reuse that shape and sanitize diagnostics so OAuth tokens, raw upstream bodies, stack traces, and unsafe request context are not exposed. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/conventions.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py`

**Alternatives considered**:

- Raise raw upstream errors directly. Rejected because public MCP tools must provide safe, deterministic error messages.
- Introduce playlist-image-specific error categories. Rejected because shared categories are sufficient and simpler for clients.
- Include raw request context in details. Rejected because the constitution requires avoiding secret and unsafe diagnostic exposure.

## Decision: Add a new `playlist_images` Layer 2 module and register it in default discovery

**Rationale**: The shared family list already includes `playlist_images`, Layer 1 resource modules use that family name, and the existing list-tool pattern places endpoint-backed public behavior in one concrete resource-family module. Adding `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`, exporting it from `youtube_common/__init__.py`, and registering its descriptor in `dispatcher.py` is the smallest consistent public-tool path. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`

**Alternatives considered**:

- Put the tool in `playlists.py` or `playlist_items.py`. Rejected because playlist images are a separate resource family and endpoint.
- Put the tool only in dispatcher. Rejected because public contracts, validation, result mapping, and tests belong in a cohesive resource-family module.
- Create a broader playlist-media package. Rejected because one endpoint-backed tool does not justify a larger architecture.

## Decision: Validate with contract, unit, integration, registry, and full-suite checks

**Rationale**: The constitution requires Red-Green-Refactor, contract-first design, integration coverage, and a full repository test-suite run. YT-228 will add contract tests for metadata/examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, and final `pytest` plus `ruff check .`. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/.specify/memory/constitution.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/228-playlist-images-list/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/227-memberships-levels-list/plan.md`

**Alternatives considered**:

- Only add unit tests. Rejected because MCP-facing discovery and registry behavior require contract and integration coverage.
- Skip full-suite verification. Rejected by the constitution.
- Defer docstring checks to review. Rejected because new and changed Python functions must include reStructuredText docstrings as part of implementation.

## Clarification Closure

All planning-time clarifications for YT-228 are resolved in this research artifact. No unresolved clarification markers remain.
