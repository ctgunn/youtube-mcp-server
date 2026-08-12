# Quickstart: YT-310 Playlist Details

## Goal

Use this guide to verify that planning is complete before generating implementation tasks for `playlists_getPlaylist`.

## Review the Plan Artifacts

```bash
sed -n '1,300p' /Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/spec.md
sed -n '1,420p' /Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/plan.md
sed -n '1,320p' /Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/research.md
sed -n '1,320p' /Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/data-model.md
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/contracts/playlists-get-playlist-contract.md
```

## Confirm the Contract Before Tasking

- `playlists_getPlaylist` requires exactly one nonblank `playlistId` and accepts no other input.
- The implementation makes one direct `playlists.list` lookup using `snippet`, `contentDetails`, and `status`; it does not paginate or retrieve playlist entries.
- A successful result returns the playlist identifier and only available public title, description, creator attribution, publication time, thumbnails, privacy visibility, and item count.
- The result includes provenance and scope context that distinguish caller-facing normalized fields and direct clients needing entries to `playlists_getPlaylistItems`.
- An empty lookup maps to `unavailable_resource` without exposing the private, deleted, restricted, or not-found reason.
- The feature introduces no persistence, source client, transport change, ranking, filtering, fan-out, or playlist-item traversal.
- New paths, symbols, and test names follow the established composed-family convention.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and routing tests for validation, one direct lookup, complete and sparse mapping, provenance and scope, unavailable lookup, safe error translation, discovery, and default registration.
2. **Green**: Add only the descriptor, validation, one-lookup adapter, normalizer, safe error mapper, exports, and registration needed for those tests.
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

- The matched seed slice, `YT-310`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving the concrete `playlists_getPlaylist` descriptor is registered without a representative-only marker.
- Result evidence for a populated playlist, sparse public metadata, unavailable playlist behavior, no playlist entries, provenance, and every safe error category.
- Confirmation that the implementation performs one lower-level lookup per invocation.
- Passing full-suite and lint output.
- Confirmation that all new or changed Python functions have reStructuredText docstrings.
