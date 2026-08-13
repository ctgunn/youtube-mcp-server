# Quickstart: YT-311 Playlist Items

## Goal

Use this guide to verify that planning is complete before generating implementation tasks for `playlists_getPlaylistItems`.

## Review the Plan Artifacts

```bash
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/spec.md
sed -n '1,520p' /Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/plan.md
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/research.md
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/data-model.md
sed -n '1,460p' /Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/contracts/playlists-get-playlist-items-contract.md
```

## Confirm the Contract Before Tasking

- `playlists_getPlaylistItems` requires one nonblank `playlistId`; `maxResults` is optional, defaults to 25, and accepts only whole numbers from 1 through 50.
- The implementation performs exactly one `playlistItems.list` lookup using `snippet`, `contentDetails`, and `status`; it accepts no continuation input and does not traverse additional pages.
- A successful result preserves exposed source playlist order and returns concise available item fields, normalized availability state, returned count, applied limit, limited indication, collection context, and provenance.
- An exposed unavailable item stays in order and does not receive invented details.
- A successful source response with no entries is a successful empty collection; lower-layer unavailable, access, capacity, and source failures remain distinguishable safe errors.
- The feature introduces no persistence, source client, transport change, ranking, search, per-video enrichment, transcript retrieval, or playlist mutation.
- New paths, symbols, and test names follow the established composed-playlists convention.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and routing tests for validation, default/bounds, one exact lower lookup, source order, complete/sparse/unavailable item mapping, empty success, limited indication, safe errors, discovery, and default registration.
2. **Green**: Add only the descriptor, validation, one-listing adapter, normalizer, safe error mapper, exports, and registration needed for those tests.
3. **Refactor**: Consolidate repeated mapping and sanitization logic, retain reStructuredText docstrings on all changed Python functions, then rerun focused and full checks.

## Planned Verification Commands

Run focused checks during implementation:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/unit/test_youtube_composed_playlists.py \
  tests/contract/test_youtube_composed_playlists_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/unit/test_method_routing.py
```

Run these after the final code change:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

## Review Evidence

Pull-request review should include:

- The matched seed slice, `YT-311`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving the concrete `playlists_getPlaylistItems` descriptor is registered without a representative-only marker.
- Result evidence for populated, sparse, empty, limited, and unavailable-entry collections; invalid input; and every safe error category.
- Confirmation that each invocation performs exactly one lower-layer listing with the applied limit.
- Passing full-suite and lint output.
- Confirmation that all new or changed Python functions and test helpers have reStructuredText docstrings.
