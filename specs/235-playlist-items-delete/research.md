# Research: YT-235 Layer 2 Tool `playlistItems_delete`

## Decision: Expose one public Layer 2 tool named `playlistItems_delete`

**Rationale**: The YT-235 seed explicitly requires Layer 2 to expose `playlistItems_delete` as the low-level public tool for the upstream `playlistItems.delete` endpoint. The PRD requires one endpoint-backed Layer 2 tool per supported YouTube Data API operation, and the existing shared contracts use endpoint-style public names. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/requirements/PRD.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/235-playlist-items-delete/spec.md`

**Alternatives considered**:

- Combine this with `playlistItems_update`. Rejected because update and delete have different inputs, response shapes, destructive semantics, examples, and failure modes.
- Rename to `playlist_items_delete`. Rejected because the seed and PRD name the public Layer 2 tool `playlistItems_delete`.
- Defer public exposure to a Layer 3 playlist workflow. Rejected because YT-235 is specifically a Layer 2 endpoint-backed tool slice.

## Decision: Reuse the existing YT-135 Layer 1 `playlistItems.delete` wrapper

**Rationale**: The Layer 1 wrapper exists under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlist_items.py`, exposes operation key `playlistItems.delete`, requires OAuth access, requires one `id`, records quota cost `50`, and keeps destructive target-state-sensitive deletion guidance visible. Reusing it preserves the Layer 1/Layer 2 boundary and avoids redefining upstream request execution in the public tool.

**Alternatives considered**:

- Add a separate Layer 2 transport path. Rejected because tools should depend on integration interfaces and not duplicate request execution, auth, quota, or upstream error logic.
- Change the Layer 1 wrapper first. Rejected because current Layer 1 metadata already matches YT-235's quota, auth, and identifier requirements.
- Mock delete results only in Layer 2. Rejected because the public tool must be endpoint-backed through the Layer 1 capability.

## Decision: Require only `id` in the public input contract

**Rationale**: YT-135 models `playlistItems.delete` as a deterministic deletion request with one required playlist item identifier and no supported body, part selection, playlist metadata payload, paging, or listing selectors. Existing Layer 2 tools narrow their public input schema to supported repo-local endpoint behavior and reject additional properties. The smallest testable YT-235 schema is therefore one required non-empty string `id`.

**Alternatives considered**:

- Allow `part` for consistency with list/insert/update. Rejected because delete does not return selected resource sections and accepting `part` would imply unsupported behavior.
- Allow a request body for future delete metadata. Rejected because the local Layer 1 contract requires only `id`.
- Pass through arbitrary extra fields for future compatibility. Rejected because deterministic public contracts and clear invalid-request feedback are required by YT-201/YT-202 conventions.

## Decision: Return a deletion acknowledgment rather than a deleted resource

**Rationale**: `playlistItems.delete` may complete without a resource body. The public Layer 2 result should preserve endpoint identity, quota cost, target identifier context, auth mode, and deletion outcome without fabricating deleted playlist-item fields.

**Alternatives considered**:

- Return an `item` resource from request context. Rejected because that would fabricate resource data not returned by the delete operation.
- Return only an empty object. Rejected because callers need target identifier, quota, and operation context to interpret destructive outcomes.
- Fetch the deleted resource before or after deletion. Rejected because this slice must remain one endpoint-backed Layer 2 tool and avoid cross-endpoint behavior.

## Decision: Keep quota cost `50` visible in metadata, descriptions, usage notes, examples, and results

**Rationale**: The YT-235 seed, YT-135 wrapper, and YT-235 specification agree that `playlistItems.delete` has official quota cost `50`. Existing Layer 2 tools make quota visible across discovery metadata, descriptions, examples, and near-raw results so client developers can understand cost before invocation and in returned context.

**Alternatives considered**:

- Put quota only in metadata. Rejected because the spec requires description and examples to visibly state quota cost.
- Recheck remote documentation during planning. Rejected because this workflow uses local feature requirements and no unresolved local discrepancy exists.
- Omit quota from successful results. Rejected because nearby Layer 2 endpoint-backed tools preserve quota context in public result wrappers.

## Decision: Model access as OAuth-required

**Rationale**: Both YT-135 and YT-235 require OAuth expectations to be visible. The public contract should reject missing OAuth locally as `authentication_failed` and map inaccessible playlist-item deletes to `authorization_failed` unless the normalized upstream category provides a more specific safe category.

**Alternatives considered**:

- Allow API-key-only access. Rejected because repo-local contracts mark this endpoint OAuth-required.
- Hide auth constraints in implementation only. Rejected because callers must understand access limits before invoking the tool.
- Add delegated owner context in this slice. Rejected because delegation inputs are outside the YT-235 scope unless later local contracts explicitly add them.

## Decision: Use shared Layer 2 safe error categories and sanitize diagnostics

**Rationale**: Existing Layer 2 tools map local validation and normalized upstream failures into shared safe categories such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, `deprecated`, and `upstream_failure`. YT-235 should reuse that shape and sanitize diagnostics so OAuth tokens, API keys, raw upstream bodies, stack traces, and unsafe request context are not exposed.

**Alternatives considered**:

- Raise raw upstream errors directly. Rejected because public MCP tools must provide safe, deterministic error messages.
- Introduce playlist-item-specific error categories. Rejected because shared categories are sufficient and simpler for clients.
- Include raw request or auth context in details. Rejected because the constitution requires avoiding secret and unsafe diagnostic exposure.

## Decision: Extend the existing `playlist_items` Layer 2 module and register the delete descriptor in default discovery

**Rationale**: YT-232 through YT-234 already established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py` as the concrete Layer 2 resource-family module for `playlistItems` tools. Adding `playlistItems_delete` to that module, exporting it from `youtube_common/__init__.py`, and registering its descriptor in `dispatcher.py` is the smallest consistent public-tool path.

**Alternatives considered**:

- Put the tool in `playlists.py` or `playlist_images.py`. Rejected because playlist items are a separate resource family and endpoint.
- Create a second `playlist_items_delete.py` module. Rejected because the existing resource-family module is the cohesive home for `playlistItems` endpoint-backed tools.
- Create a broader playlist-management package. Rejected because one endpoint-backed tool does not justify a larger architecture.

## Decision: Validate with contract, unit, integration, registry, and full-suite checks

**Rationale**: The constitution requires Red-Green-Refactor, contract-first design, integration coverage, and a full repository test-suite run. YT-235 will add contract tests for metadata/examples, unit tests for validation/result/error mapping, integration tests for registry discovery and dispatcher execution, and final `pytest` plus `ruff check .`.

**Alternatives considered**:

- Only add unit tests. Rejected because MCP-facing discovery and registry behavior require contract and integration coverage.
- Skip full-suite verification. Rejected by the constitution.
- Defer docstring checks to review. Rejected because new and changed Python functions must include reStructuredText docstrings as part of implementation.

## Clarification Closure

All planning-time clarifications for YT-235 are resolved in this research artifact. No unresolved clarification markers remain.
