# Quickstart: Layer 2 Tool `playlistItems_list`

## Goal

Implement and verify the public Layer 2 MCP tool `playlistItems_list` for near-raw YouTube `playlistItems.list` access.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Use branch `232-playlist-items-list`.
- Treat `YT-132`, `YT-201`, and `YT-202` as dependencies.
- Keep the tool scoped to one endpoint-backed list operation.
- Add or preserve reStructuredText docstrings for every new or changed Python function.

## Expected Files

Planning artifacts:

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/spec.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/plan.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/research.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/contracts/playlistItems_list.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/232-playlist-items-list/quickstart.md`

Likely implementation targets:

- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_items.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_playlist_items_contract.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_playlist_items.py`
- `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_playlist_items_registration.py`
- Existing shared catalog, common contract, and dispatcher registration tests as needed.

## Red Phase

Start with failing tests that prove `playlistItems_list` is not yet available or not complete.

Add focused expectations for:

- Public exports of `PLAYLIST_ITEMS_LIST_*` symbols.
- Tool name `playlistItems_list`.
- Upstream operation identity `playlistItems.list`.
- Official quota cost `1`.
- API-key access disclosure for the supported selector set.
- Required `part`.
- Exactly one supported selector: `playlistId` or `id`.
- Playlist-scoped pagination with valid `pageToken` and `maxResults`.
- Selector-incompatible paging rejection.
- Examples for playlist-scoped retrieval, paginated traversal, identifier lookup, empty success, invalid requests, access failure, and out-of-scope workflow rejection.
- Registry discovery and dispatcher execution.
- Safe error categories without leaked credential or raw upstream details.

Run the focused tests and confirm they fail for the missing feature before implementation.

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Green Phase

Implement the smallest behavior needed to pass the focused tests.

Expected minimum:

- Add `playlist_items.py` under `src/mcp_server/tools/youtube_common/`.
- Define `PLAYLIST_ITEMS_LIST_TOOL_NAME`, quota, supported selectors, supported parts, input schema, description, usage notes, caveats, and caller examples.
- Build the public `playlistItems_list` contract and descriptor.
- Validate `part`, selectors, paging, unsupported fields, and access boundaries.
- Use the existing Layer 1 `build_playlist_items_list_wrapper()`.
- Map successful populated and empty playlist-item list results into the shared Layer 2 result shape.
- Map validation, access, quota, missing-resource, unavailable-service, deprecated-behavior, and unexpected upstream failures to safe shared categories.
- Export the public symbols from `mcp_server.tools.youtube_common`.
- Register the descriptor in the default dispatcher registry.

Run focused tests until they pass.

```bash
pytest tests/contract/test_youtube_playlist_items_contract.py tests/unit/test_youtube_playlist_items.py tests/integration/test_youtube_playlist_items_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Refactor Phase

After focused tests pass:

- Remove duplicate validation or metadata code that belongs in shared YT-201/YT-202 helpers.
- Keep `playlist_items.py` cohesive and limited to playlist-item endpoint tools.
- Re-check docstrings for every new or changed Python function.
- Confirm examples and metadata remain caller-facing and safe.
- Confirm no playlist item mutation, playlist search, video enrichment, transcript retrieval, analytics, ranking, summarization, recommendation, or cross-endpoint behavior slipped in.

Run final validation:

```bash
pytest
ruff check .
```

## Manual Review Checklist

- `playlistItems_list` is discoverable through the default registry.
- Tool discovery metadata shows `playlistItems.list` and quota cost `1`.
- The public contract discloses API-key access expectations for the supported selector set.
- Valid `playlistId` requests return list results and preserve paging context when present.
- Valid `id` requests return list results without implying playlist traversal.
- Empty valid results are successful empty collections.
- Missing `part`, invalid `part`, missing selector, conflicting selectors, invalid identifiers, invalid paging, unsupported fields, and out-of-scope workflow requests fail clearly.
- Safe errors do not leak credentials, tokens, stack traces, or raw upstream diagnostics.
- New or changed Python functions include reStructuredText docstrings.
