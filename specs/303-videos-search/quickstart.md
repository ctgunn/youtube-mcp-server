# Quickstart: Verify `videos_searchVideos`

## Prerequisites

- Python 3.11 or later is available.
- The repository dependencies and lint tool are installed.
- A configured runtime has public YouTube API-key capability when testing against the live integration path. Do not place secrets in commands, test fixtures, logs, or documentation.

## Install

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pip install -e . ruff
```

## Verify the Public Contract and Behavior

After implementation, run the focused feature suite:

```bash
python3 -m pytest \
  tests/unit/test_youtube_composed_videos.py \
  tests/contract/test_youtube_composed_videos_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py
```

The focused suite must demonstrate:

- query-only video search and an empty successful result;
- validation of all public parameters, bounds, time windows, and unknown fields;
- subscriber, latest-upload, creator, and unique-channel refinement;
- all five ranking modes with deterministic ties;
- safe partial-enrichment and lower-layer error behavior;
- executable descriptor discovery and default dispatcher registration.

Verify the Layer 3 error categories serialize safely through the MCP protocol:

```bash
python3 -m pytest tests/unit/test_method_routing.py
```

## Review Discovery Expectations

Confirm the discovered `videos_searchVideos` descriptor has:

- the exact public input schema from [the contract](./contracts/videos-search-videos.md);
- no `representativeOnly` marker;
- a `ranked_enrichment` composition boundary;
- disclosed `search.list`, `channels.list`, and conditional `playlistItems.list` dependencies, quota/auth caveats, boundedness, partial-result policy, field provenance, creator heuristic, and safe error categories.

## Final Repository Evidence

Before considering the feature complete, run the full required checks from `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pytest
ruff check .
```

Both commands must pass after the final code and docstring changes. The pull request should include the Red-Green-Refactor evidence and confirm that every new or changed Python function has a reStructuredText docstring.
