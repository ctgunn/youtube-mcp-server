# Research: YT-237 Layer 2 Tool `playlists_insert`

## Decision: Expose `playlists_insert` in the existing Layer 2 playlists resource family

**Rationale**: The seed slice requires public Layer 2 exposure of `playlists.insert`, and YT-236 already established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py` as the public playlists resource-family module. The narrowest cohesive implementation is to extend that module with insert-specific constants, validation, result mapping, contract metadata, examples, descriptor, handler, exports, and registry integration.

**Alternatives considered**:
- Add `playlists_insert` to `playlist_items.py` or `playlist_images.py`. Rejected because those modules represent different upstream resource families and would blur endpoint ownership.
- Create a second playlists insert-only module. Rejected because the existing playlists family already owns the resource family and can hold adjacent endpoint tools without a broad refactor.
- Modify Layer 1 only. Rejected because YT-137 already owns the internal `playlists.insert` wrapper and YT-237 is explicitly public Layer 2 work.

## Decision: Reuse the existing Layer 1 `build_playlists_insert_wrapper()`

**Rationale**: The local Layer 1 wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlists.py` already models `playlists.insert` with resource `playlists`, method `insert`, `POST /youtube/v3/playlists`, quota cost `50`, OAuth-required auth, required `part`, required `body`, and validation for the supported `body.snippet.title` create path. Reusing it keeps upstream request execution, quota metadata, and auth validation in the Layer 1 dependency rather than redefining a parallel upstream contract.

**Alternatives considered**:
- Duplicate YouTube request shaping in Layer 2. Rejected because Layer 2 should depend on Layer 1 wrappers and avoid duplicating execution, auth, quota, and upstream error behavior.
- Expand the Layer 1 wrapper during this slice. Rejected unless tests expose a missing export or metadata defect, because the YT-237 scope is the public Layer 2 tool.

## Decision: Require `part` plus `body.snippet.title` for the supported create path

**Rationale**: The YT-137 wrapper documents `part` and `body` as required inputs, keeps `part=snippet` explicit, and requires `body.snippet.title` for the minimum supported playlist creation path. The public Layer 2 contract should preserve that boundary so callers know which writable inputs create a playlist and which optional write fields are unsupported unless deliberately added later.

**Alternatives considered**:
- Accept any upstream playlist resource body. Rejected because the local Layer 1 wrapper deliberately constrains the write surface for this slice.
- Make `part` optional with a default. Rejected because the wrapper and public contract need the caller to acknowledge the writable part selection.
- Support `status`, `description`, or localization by default. Rejected because the Layer 1 wrapper marks these as unsupported optional write fields unless the contract is deliberately expanded.

## Decision: Model access as OAuth-required for all calls

**Rationale**: Playlist creation mutates an authorized user's channel state and the Layer 1 wrapper requires `oauth_required` auth. The Layer 2 contract must expose the OAuth requirement in metadata, descriptions, usage notes, examples, and safe error categories so callers can identify access needs before spending quota or attempting creation.

**Alternatives considered**:
- Allow API-key access for public playlist creation. Rejected because `playlists.insert` is a user-authorized mutation.
- Split authorization by request field. Rejected because the endpoint requires OAuth for the supported create operation.

## Decision: Return a near-raw created-resource mutation result with safe context

**Rationale**: Layer 2 tools should remain close to upstream endpoint behavior while adding MCP-usable structure. The result should preserve returned playlist fields, requested parts, safe creation context, quota cost, auth mode, endpoint identity, and safe upstream failure categories without fabricating playlist item, video, image, channel, transcript, ranking, recommendation, or analytics data.

**Alternatives considered**:
- Return only raw upstream JSON. Rejected because shared Layer 2 conventions require quota, auth, response, and error context for clients.
- Enrich the created playlist with items, videos, thumbnails, transcripts, or rankings. Rejected because those workflows belong to separate endpoint or Layer 3 features.

## Decision: Document duplicate-create caveat rather than adding idempotency

**Rationale**: `playlists_insert` is a low-level endpoint-backed mutation. Retrying after a timeout or unclear upstream outcome may create another playlist, and this slice does not include a higher-level duplicate lookup or idempotency key workflow. The contract should warn callers without adding behavior outside the upstream insert operation.

**Alternatives considered**:
- Add duplicate detection before creation. Rejected because it would require extra endpoint calls and higher-level workflow semantics outside YT-237.
- Promise idempotent retry behavior. Rejected because the shared contract and upstream insert behavior do not provide that guarantee for this slice.

## Decision: Follow existing Layer 2 mutation test and export patterns

**Rationale**: Existing Layer 2 modules expose constants, input schemas, usage notes, caveats, examples, contract builders, handlers, descriptors, validators, result mappers, safe tool errors, public package exports, shared catalog entries, and default registry descriptors. YT-237 should add the same surfaces for `playlists_insert` with focused contract, unit, integration, catalog, dispatcher, and scaffold coverage.

**Alternatives considered**:
- Add only integration tests. Rejected by the constitution and existing project practice because public tool contracts need unit, contract, and integration coverage.
- Add broad cross-resource refactors before implementing the tool. Rejected because this slice can be delivered by narrow additions to the existing playlists family plus exports and registration.

## Decision: Require reStructuredText docstrings for any new or changed Python functions

**Rationale**: The constitution requires every new or modified Python function to include a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. This applies to production helpers and test fake methods touched during implementation.

**Alternatives considered**:
- Rely on module-level documentation only. Rejected because the constitution specifically requires function-level docstrings for changed Python functions.
- Defer docstrings to cleanup without test or review evidence. Rejected because docstring compliance is a planning and review gate.
