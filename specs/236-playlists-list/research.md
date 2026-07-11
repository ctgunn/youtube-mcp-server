# Research: YT-236 Layer 2 Tool `playlists_list`

## Decision: Expose `playlists_list` as a concrete Layer 2 playlists resource-family tool

**Rationale**: The seed slice requires public Layer 2 exposure of `playlists.list`, and the repository already declares `playlists` as a required YouTube resource family in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/families.py`. There is no existing Layer 2 `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py` module, so the narrowest cohesive implementation is to add that family module and register only `playlists_list` for this slice.

**Alternatives considered**:
- Add `playlists_list` to `playlist_items.py` or `playlist_images.py`. Rejected because those modules represent different upstream resource families and would blur endpoint ownership.
- Use only a representative descriptor from shared family scaffolding. Rejected because YT-236 requires an executable public endpoint-backed Layer 2 tool, not only catalog metadata.
- Modify Layer 1 only. Rejected because YT-136 already owns the internal `playlists.list` wrapper and YT-236 is explicitly public Layer 2 work.

## Decision: Reuse the existing Layer 1 `build_playlists_list_wrapper()`

**Rationale**: The local Layer 1 wrapper in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/playlists.py` already models `playlists.list` with resource `playlists`, method `list`, `GET /youtube/v3/playlists`, quota cost `1`, conditional auth, required `part`, selectors `channelId`, `id`, and `mine`, and selector-aware paging rules. Reusing it keeps upstream request execution, quota metadata, and access validation in the Layer 1 dependency rather than redefining a parallel upstream contract.

**Alternatives considered**:
- Duplicate YouTube request shaping in Layer 2. Rejected because Layer 2 should depend on Layer 1 wrappers and avoid duplicating execution, auth, quota, and upstream error behavior.
- Expand the Layer 1 wrapper during this slice. Rejected unless tests expose a missing export or metadata defect, because the YT-236 scope is the public Layer 2 tool.

## Decision: Require `part` plus exactly one selector from `channelId`, `id`, or `mine`

**Rationale**: The YT-136 wrapper and YT-236 spec both center the supported request shape on required part selection and exactly one supported selector. `channelId` retrieves playlists for a channel, `id` performs direct playlist lookup, and `mine` retrieves owner-scoped playlists for the authorized user. Exactly-one validation prevents ambiguous precedence and makes no-match results distinct from malformed requests.

**Alternatives considered**:
- Allow multiple selectors and pick a precedence order. Rejected because it would hide caller mistakes and diverge from adjacent Layer 2 list-tool validation.
- Support additional undocumented selectors. Rejected because the feature must remain close to the supported Layer 1 wrapper contract and endpoint inventory.
- Make `part` optional with a default. Rejected because upstream list semantics and existing Layer 2 tools make part selection caller-visible.

## Decision: Model access as conditional by selector

**Rationale**: The local YT-136 wrapper documents public lookup through `channelId` and `id`, and owner-scoped retrieval through `mine` with OAuth-backed access. The Layer 2 contract must expose that conditional access boundary in metadata, descriptions, usage notes, examples, and safe error categories so callers can choose a valid selector before invocation.

**Alternatives considered**:
- Mark the whole tool as API-key-only. Rejected because that would hide the owner-scoped `mine` path.
- Mark the whole tool as OAuth-only. Rejected because that would incorrectly raise the access burden for public `channelId` and `id` retrieval.
- Split `mine` into a separate public tool. Rejected because the upstream endpoint and existing Layer 1 wrapper support one selector-based `playlists.list` operation.

## Decision: Preserve pagination for collection-style selectors and reject selector-incompatible paging

**Rationale**: `channelId` and `mine` are collection-style retrieval modes, so the public contract should allow supported `pageToken` and `maxResults` inputs and preserve returned page context. Direct `id` lookup is deterministic and should reject paging inputs unless a shared contract deliberately permits them. This mirrors existing Layer 2 list tools that treat paging as selector-aware.

**Alternatives considered**:
- Allow paging for every selector. Rejected because `id` lookup does not naturally represent paginated traversal.
- Ignore unsupported paging inputs. Rejected because silent ignores can make callers believe a page boundary was honored when it was not.
- Remove pagination entirely. Rejected because the seed explicitly requires filter and pagination behavior to be documented clearly.

## Decision: Return a near-raw list result with safe context

**Rationale**: Layer 2 tools should remain close to upstream endpoint behavior while adding MCP-usable structure. The result should preserve returned playlist items, selected parts, selector context, pagination context, quota cost, access context, endpoint identity, successful empty collections, and safe upstream failure categories without fabricating playlist item, video, image, channel, transcript, ranking, or analytics data.

**Alternatives considered**:
- Return only raw upstream JSON. Rejected because shared Layer 2 conventions require quota, selector, access, response, and error context for clients.
- Enrich playlists with videos, items, thumbnails, transcripts, or rankings. Rejected because those workflows belong to separate endpoint or Layer 3 features.

## Decision: Follow existing Layer 2 test and export patterns from playlist-items and playlist-images tools

**Rationale**: Existing Layer 2 modules expose constants, input schemas, usage notes, caveats, examples, contract builders, handlers, descriptors, validators, result mappers, safe tool errors, public package exports, shared catalog entries, and default registry descriptors. YT-236 should add the same surfaces for `playlists_list` with focused contract, unit, integration, catalog, dispatcher, and scaffold coverage.

**Alternatives considered**:
- Add only integration tests. Rejected by the constitution and existing project practice because public tool contracts need unit, contract, and integration coverage.
- Add broad cross-resource refactors before implementing the tool. Rejected because this slice can be delivered by a narrow new family module plus exports and registration.

## Decision: Require reStructuredText docstrings for any new or changed Python functions

**Rationale**: The constitution requires every new or modified Python function to include a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. This applies to production helpers and test fake methods touched during implementation.

**Alternatives considered**:
- Rely on module-level documentation only. Rejected because the constitution specifically requires function-level docstrings for changed Python functions.
- Defer docstrings to a cleanup task without test evidence. Rejected because docstring compliance is a planning and review gate.
