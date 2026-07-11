# Quickstart: YT-236 Layer 2 Tool `playlists_list`

## Goal

Verify that `playlists_list` is exposed as a public Layer 2 MCP tool for `playlists.list`, with quota cost `1`, conditional access disclosure, required part selection, supported selectors, pagination behavior, empty-result handling, and safe validation/error boundaries.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Use branch `236-playlists-list`.
- Keep YT-136, YT-201, and YT-202 assumptions available for review.
- Add or preserve reStructuredText docstrings for every new or changed Python function.

## Red Phase Checks

Start by adding failing tests that prove the tool is not complete until all required surfaces exist:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected red findings before implementation:
- `playlists_list` public symbols are missing.
- `playlists_list` is absent from default registry discovery.
- Metadata does not yet expose `playlists.list`, quota cost `1`, conditional access, selectors, pagination, examples, and caveats.
- Request validation and result mapping for playlists are missing.

## Green Phase Checks

Implement the smallest endpoint-backed tool surface needed for:

- Public module `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- Public exports from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- Default dispatcher registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- Shared catalog or example inclusion where the current catalog pattern requires it
- Focused contract, unit, and integration tests

Representative successful calls:

```json
{
  "part": "snippet,contentDetails",
  "channelId": "UC123"
}
```

```json
{
  "part": "id,snippet",
  "id": "PL123"
}
```

```json
{
  "part": "snippet",
  "mine": true
}
```

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "pageToken": "NEXT_PAGE",
  "maxResults": 25
}
```

Representative invalid calls:

```json
{
  "channelId": "UC123"
}
```

```json
{
  "part": "statistics",
  "channelId": "UC123"
}
```

```json
{
  "part": "snippet"
}
```

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "id": "PL123"
}
```

```json
{
  "part": "snippet",
  "id": "PL123",
  "pageToken": "NEXT_PAGE"
}
```

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "includePlaylistItems": true
}
```

## Review Expectations

Discovery metadata must show:
- Tool name `playlists_list`
- Upstream operation `playlists.list`
- Quota cost `1`
- Conditional access:
  - `channelId` and `id` use public lookup
  - `mine` requires OAuth-backed access
- Required `part`
- Selectors `channelId`, `id`, and `mine`
- Selector-specific pagination behavior
- Empty successful collection behavior
- Safe failure categories
- Out-of-scope workflow boundaries

Successful results must preserve:
- Endpoint identity
- Quota cost
- Requested parts
- Selector context
- Access context
- Pagination context when applicable
- Returned playlist items, including empty collections

Failures must distinguish:
- Local validation failures
- Owner-scoped access failures
- Quota failures
- Missing resource or no-match outcomes
- Upstream unavailable or unexpected failures

Failures must not expose:
- API keys
- OAuth tokens
- Authorization headers
- Raw upstream response bodies
- Stack traces
- Secret-bearing request context

## Refactor and Final Verification

After implementation and cleanup, run:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
PYTHONPATH=src python3 -m pytest
python3 -m ruff check .
```

Completion evidence must include:
- Matched seed slice `YT-236`
- Focused passing output for `playlists_list`
- Full-suite passing output from `pytest`
- Code-quality passing output from `ruff check .`
- Confirmation that every new or changed Python function has a reStructuredText docstring
