# Quickstart: YT-237 Layer 2 Tool `playlists_insert`

## Goal

Verify that `playlists_insert` is exposed as a public Layer 2 MCP tool for `playlists.insert`, with quota cost `50`, OAuth-required access disclosure, required part selection, required writable playlist title, mutation-result handling, duplicate-create caveat, and safe validation/error boundaries.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Use branch `237-playlists-insert`.
- Keep YT-137, YT-201, and YT-202 assumptions available for review.
- Add or preserve reStructuredText docstrings for every new or changed Python function.

## Red Phase Checks

Start by adding failing tests that prove the tool is not complete until all required surfaces exist:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected red findings before implementation:
- `playlists_insert` public symbols are missing.
- `playlists_insert` is absent from default registry discovery.
- Metadata does not yet expose `playlists.insert`, quota cost `50`, OAuth requirement, writable create semantics, mutation warning, duplicate-create caveat, examples, and caveats.
- Request validation and result mapping for playlist creation are missing.

## Green Phase Checks

Implement the smallest endpoint-backed tool surface needed for:

- Existing public module `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlists.py`
- Public exports from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`
- Default dispatcher registration in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`
- Shared catalog or example inclusion where the current catalog pattern requires it
- Focused contract, unit, and integration tests

Representative successful call:

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Research playlist"
    }
  }
}
```

Representative invalid calls:

```json
{
  "body": {
    "snippet": {
      "title": "Research playlist"
    }
  }
}
```

```json
{
  "part": "status",
  "body": {
    "snippet": {
      "title": "Research playlist"
    }
  }
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
  "body": {
    "snippet": {}
  }
}
```

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Research playlist",
      "description": "Unsupported by this slice"
    }
  }
}
```

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "title": "Research playlist"
    }
  },
  "insertPlaylistItems": true
}
```

## Review Expectations

Discovery metadata must show:
- Tool name `playlists_insert`
- Upstream operation `playlists.insert`
- Quota cost `50`
- OAuth-backed access requirement
- Required `part`
- Required `body.snippet.title`
- Successful calls create user-visible playlists
- Duplicate-create caveat
- Safe failure categories
- Out-of-scope workflow boundaries

Successful results must preserve:
- Endpoint identity
- Quota cost
- Requested parts
- Safe creation context
- OAuth access context
- Returned created playlist resource

Failures must distinguish:
- Local validation failures
- Missing or insufficient OAuth access
- Quota failures
- Forbidden create outcomes
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
- Matched seed slice `YT-237`
- Focused passing output for `playlists_insert`
- Full-suite passing output from `pytest`
- Code-quality passing output from `ruff check .`
- Confirmation that every new or changed Python function has a reStructuredText docstring
