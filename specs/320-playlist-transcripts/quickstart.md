# Quickstart: YT-320 Playlist Video Transcript Aggregation

## Goal

Use this guide to verify that planning is complete before generating implementation tasks for `playlists_getVideoTranscripts`.

## Review the Plan Artifacts

```bash
sed -n '1,560p' /Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/spec.md
sed -n '1,760p' /Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/plan.md
sed -n '1,420p' /Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/research.md
sed -n '1,460p' /Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/data-model.md
sed -n '1,560p' /Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/contracts/playlists-get-video-transcripts-contract.md
```

## Confirm the Contract Before Tasking

- `playlists_getVideoTranscripts` requires one nonblank `playlistId`; `language` is optional; `maxResults` defaults to 10 and accepts only whole numbers from 1 through 50.
- A request resolves language in the order explicit input, configured `YOUTUBE_TRANSCRIPT_LANG`, then English, and forwards that exact language to every eligible timestamped-caption retrieval.
- The implementation performs exactly one `playlistItems.list` lookup using `snippet`, `contentDetails`, and `status`; it accepts no continuation input and does not traverse additional pages.
- The applied limit bounds both the source items considered and caption retrieval attempts. It makes no caption attempt for unavailable playlist items.
- Results preserve source playlist order, return timestamped segments only for successful items, preserve safe mixed per-video outcomes, and include a fan-out summary. A next-page signal is the only indication that more items were not attempted.
- The feature introduces no persistence, source client, transport change, transcript generation or translation, public fallback provider, ranking, search, or unbounded background work.
- The implementation must not change the existing timestamped-caption tool's no-language fallback behavior.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and routing tests for strict validation; default/bounds; language resolution; one exact playlist lookup; capped source-order fan-out; unavailable entries; timestamped segments; empty playlist; mixed per-video errors; safe details; metadata; and default registration.
2. **Green**: Add only the playlists-family descriptor, validator, language resolver, one-listing adapter, per-video outcome mapper, fan-out summary, exports, and registration required for those tests.
3. **Refactor**: Consolidate local mapping and safe-error logic; retain reStructuredText docstrings on all new or changed Python functions and test helpers; then rerun focused and full checks.

## Planned Verification Commands

Run focused checks during implementation:

```bash
PYTHONPATH=src python3 -m pytest \
  tests/unit/test_youtube_composed_playlists.py \
  tests/unit/test_youtube_composed_transcripts.py \
  tests/contract/test_youtube_composed_playlists_contract.py \
  tests/contract/test_youtube_composed_transcripts_contract.py \
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

- The matched seed slice, `YT-320`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving the concrete `playlists_getVideoTranscripts` descriptor is registered without a representative-only marker.
- Result evidence for explicit, configured-default, and English-fallback language requests; available, empty, unavailable, restricted, capacity-limited, and source-failure video outcomes; empty and bounded playlists; invalid input; and playlist-level safe errors.
- Recording-handler evidence of one playlist listing, source-order preservation, no more caption attempts than the applied limit, and no caption attempt for an unavailable playlist item.
- Passing full-suite and lint output after the final code and documentation changes.
- Confirmation that every new or changed Python function and test helper has a reStructuredText docstring.
