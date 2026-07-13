# Quickstart: YT-240 Layer 2 Tool `search_list`

## Goal

Verify that `search_list` is exposed as a public Layer 2 MCP tool for `search.list`, with quota cost `100`, conditional access disclosure, required supported baseline search inputs, supported filter and pagination behavior, empty-result handling, no-hydration response boundaries, and safe validation/error categories.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Use branch `240-search-list`.
- Keep YT-140, YT-201, and YT-202 assumptions available for review.
- Add or preserve reStructuredText docstrings for every new or changed Python function.

## Red Phase Checks

Start by adding failing tests that prove the concrete tool is not complete until all required surfaces exist:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_search_contract.py tests/unit/test_youtube_search.py tests/integration/test_youtube_search_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected red findings before implementation:
- `search_list` concrete public symbols are missing.
- `search_list` is absent from default registry discovery as an endpoint-backed handler.
- Metadata does not yet expose `search.list`, quota cost `100`, conditional auth, required inputs, supported filters, pagination, empty-result behavior, no-hydration boundary, examples, and caveats.
- Request validation and result mapping for search listing are missing.
- The shared catalog still uses only a representative placeholder for `search_list`.

## Green Phase Checks

Implement the smallest endpoint-backed tool surface needed for:

- New public module `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/search.py`
- Public exports from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- Default dispatcher registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- Shared catalog or example replacement where the current catalog pattern requires it
- Focused contract, unit, and integration tests

Representative successful public call:

```json
{
  "part": "snippet",
  "q": "mcp server"
}
```

Representative type-filtered call:

```json
{
  "part": "snippet",
  "q": "mcp server",
  "type": "video"
}
```

Representative restricted call:

```json
{
  "part": "snippet",
  "q": "private uploads",
  "forMine": true
}
```

Representative paginated call:

```json
{
  "part": "snippet",
  "q": "mcp server",
  "pageToken": "NEXT_PAGE",
  "maxResults": 25
}
```

Representative invalid calls:

```json
{
  "part": "snippet"
}
```

```json
{
  "q": "mcp server"
}
```

```json
{
  "part": "snippet",
  "q": "mcp server",
  "forMine": true,
  "forDeveloper": true
}
```

```json
{
  "part": "snippet",
  "q": "mcp server",
  "videoDuration": "short"
}
```

```json
{
  "part": "snippet",
  "q": "mcp server",
  "includeTranscript": true
}
```

## Review Expectations

Discovery metadata must show:
- Tool name `search_list`
- Upstream operation `search.list`
- Quota cost `100`
- Conditional public and restricted access behavior
- Required supported inputs `part` and `q`
- Supported filter categories and pagination behavior
- Empty-result success behavior
- Search references are not hydrated resources
- Safe failure categories
- Out-of-scope workflow boundaries

Successful results must preserve:
- Endpoint identity
- Quota cost
- Safe query and filter context
- Safe access path context
- Search result records returned by the endpoint
- Empty-result status when no items are returned
- Pagination context when present

Failures must distinguish:
- Local validation failures
- Missing or insufficient access
- Quota failures
- Invalid upstream requests
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
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_search_contract.py tests/unit/test_youtube_search.py tests/integration/test_youtube_search_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
PYTHONPATH=src python3 -m pytest
python3 -m ruff check .
```

Completion evidence must include:
- Matched seed slice `YT-240`
- Focused passing output for `search_list`
- Full-suite passing output from `pytest`
- Code-quality passing output from `ruff check .`
- Confirmation that every new or changed Python function has a reStructuredText docstring
