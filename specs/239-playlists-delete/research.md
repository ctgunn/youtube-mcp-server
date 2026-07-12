# Research: YT-239 Layer 2 Tool `playlists_delete`

## Decision: Expose `playlists_delete` in the existing Layer 2 playlists resource family

**Rationale**: The seed slice requires public Layer 2 exposure of `playlists.delete`, and YT-236/YT-237/YT-238 already established `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py` as the public playlists resource-family module. The narrowest cohesive implementation is to extend that module with delete-specific constants, validation, deletion acknowledgment mapping, contract metadata, examples, descriptor, handler, exports, and registry integration.

**Alternatives considered**:
- Add `playlists_delete` to `playlist_items.py` or `playlist_images.py`. Rejected because those modules represent different upstream resource families and would blur endpoint ownership.
- Create a second playlists delete-only module. Rejected because the existing playlists family already owns list, insert, and update endpoint tools and can hold the adjacent delete tool without a broad refactor.
- Modify Layer 1 only. Rejected because YT-139 already owns the internal `playlists.delete` wrapper and YT-239 is explicitly public Layer 2 work.

## Decision: Reuse the existing Layer 1 `build_playlists_delete_wrapper()`

**Rationale**: The local Layer 1 wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlists.py` already models `playlists.delete` with resource `playlists`, method `delete`, destructive request semantics, quota cost `50`, OAuth-required auth, and required playlist `id`. Reusing it keeps upstream request execution, quota metadata, and auth validation in the Layer 1 dependency rather than redefining a parallel upstream contract.

**Alternatives considered**:
- Duplicate request execution or upstream shaping in Layer 2. Rejected because Layer 2 should depend on Layer 1 wrappers and avoid duplicating execution, auth, quota, and upstream error behavior.
- Expand the Layer 1 wrapper during this slice. Rejected unless tests expose a missing export or metadata defect, because the YT-239 scope is the public Layer 2 tool.

## Decision: Require exactly one target playlist `id`

**Rationale**: The YT-139 wrapper documents `id` as the required input for the playlist being deleted. The public Layer 2 contract should preserve that boundary so deletion is never ambiguous, caller-visible examples stay simple, and validation can reject body, part, selector, paging, playlist-item, playlist-image, video, transcript, analytics, and higher-level workflow fields before execution.

**Alternatives considered**:
- Accept a request body carrying playlist identity. Rejected because the delete wrapper and endpoint contract use `id`.
- Accept list-style selectors such as `channelId` or `mine`. Rejected because those belong to `playlists_list` and would make deletion scope ambiguous.
- Allow batch deletion. Rejected because the feature is one low-level endpoint invocation per call and should not add orchestration semantics.

## Decision: Model access as OAuth-required for all calls

**Rationale**: Playlist deletion removes a user-visible playlist and the Layer 1 wrapper requires OAuth-backed access. The Layer 2 contract must expose the OAuth requirement in metadata, descriptions, usage notes, examples, quickstart, and safe error categories so callers can identify access needs before spending quota or attempting deletion.

**Alternatives considered**:
- Allow API-key access for playlist deletion. Rejected because deletion is a user-authorized mutation.
- Split authorization by request field. Rejected because the supported operation requires OAuth for every valid request.

## Decision: Return a deletion acknowledgment with safe target context

**Rationale**: Delete operations may not return a deleted resource body. Layer 2 should remain close to endpoint behavior while adding MCP-usable structure, so the result should acknowledge deletion, preserve endpoint identity, quota cost, safe target `id`, and safe auth mode, and avoid fabricating playlist, playlist item, video, image, transcript, analytics, recommendation, restore, rollback, or enrichment data.

**Alternatives considered**:
- Return only raw upstream output. Rejected because shared Layer 2 conventions require quota, auth, response, and error context for clients.
- Fabricate a deleted playlist resource from request input. Rejected because the endpoint does not provide a returned playlist body and fabricated data would mislead callers.
- Enrich the deletion result by looking up playlist data before deletion. Rejected because it would add extra endpoint calls and higher-level workflow behavior outside YT-239.

## Decision: Document repeat-delete caveat rather than adding idempotency, restore, or rollback

**Rationale**: `playlists_delete` is a low-level endpoint-backed destructive mutation. Retrying after a timeout or unclear upstream outcome may encounter a missing-resource response if the first deletion succeeded. This slice should warn callers about that caveat without promising idempotent success, restore, rollback, conflict detection, or playlist-versioning behavior.

**Alternatives considered**:
- Add pre-delete lookup and post-delete verification. Rejected because it would require extra endpoint calls and broaden the feature beyond direct endpoint exposure.
- Promise idempotent deletion success for missing targets. Rejected because missing-resource semantics should remain distinguishable from confirmed successful deletion.
- Add restore or rollback behavior. Rejected because the shared contract and endpoint behavior do not provide that guarantee for this slice.

## Decision: Follow existing Layer 2 mutation and delete test/export patterns

**Rationale**: Existing Layer 2 modules expose constants, input schemas, usage notes, caveats, examples, contract builders, handlers, descriptors, validators, result mappers, safe tool errors, public package exports, shared catalog entries, and default registry descriptors. YT-239 should add the same surfaces for `playlists_delete` with focused contract, unit, integration, catalog, dispatcher, and scaffold coverage.

**Alternatives considered**:
- Add only integration tests. Rejected by the constitution and existing project practice because public tool contracts need unit, contract, and integration coverage.
- Add broad cross-resource refactors before implementing the tool. Rejected because this slice can be delivered by narrow additions to the existing playlists family plus exports and registration.

## Decision: Require reStructuredText docstrings for any new or changed Python functions

**Rationale**: The constitution requires every new or modified Python function to include a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. This applies to production helpers and test fake methods touched during implementation.

**Alternatives considered**:
- Rely on module-level documentation only. Rejected because the constitution specifically requires function-level docstrings for changed Python functions.
- Defer docstrings to cleanup without test or review evidence. Rejected because docstring compliance is a planning and review gate.

## Clarification Closure

All planning-time clarifications for YT-239 are resolved in this research artifact. No unresolved clarification markers remain.
