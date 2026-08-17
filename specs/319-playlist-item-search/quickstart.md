# Quickstart: Search Playlist Items

## Expected Use

Call `playlists_searchItems` when a workflow has one playlist identifier and needs a small, explainable set of matching playlist items.

```json
{
  "playlistId": "PL123",
  "query": "climate science",
  "maxResults": 10
}
```

Expect an ordered collection of matching items, the normalized query, applied limit, coverage details, and a definitive or unknown indication of additional omitted matches. Do not expect semantic or transcript search, continuation tokens, or results from outside the supplied playlist.

## Implementation Verification Sequence

1. **Red**: Add focused failing tests for strict request validation, query normalization, literal matching, matching-field order, source-order preservation, 25/50 limits, multi-page coverage, unavailable entries, empty/no-match success, safe errors, descriptor metadata, default registration, and MCP error routing.
2. **Green**: Run the focused tests after adding the smallest playlist-family handler, private bounded traversal, descriptor exports, and dispatcher registration required for them to pass:

   ```bash
   python3 -m pytest tests/unit/test_youtube_composed_playlists.py tests/contract/test_youtube_composed_playlists_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py tests/unit/test_method_routing.py
   ```

3. **Refactor**: Simplify duplicated private validation, matching, or safe error-mapping helpers only after the focused suite passes; retain or add reStructuredText docstrings for every changed Python function, class, and helper.
4. **Completion gate**: Run both repository-wide checks after the final code change and record their successful output in the pull request:

   ```bash
   python3 -m pytest
   python3 -m ruff check .
   ```

## Manual Acceptance Checks

- Search a playlist with matching titles, descriptions, channel names, and video identifiers; verify matching fields and source order.
- Search a known accessible playlist with no matching items; verify a successful empty collection.
- Search a playlist needing more than one page; verify no more than 500 entries are inspected and incomplete coverage is explicit at the cap.
- Request a limit below the number of matches; verify returned count, limit, and omission semantics.
- Try an unavailable playlist and invalid arguments; verify safe structured errors without sensitive diagnostics.
