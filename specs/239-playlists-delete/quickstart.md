# Quickstart: YT-239 Layer 2 Tool `playlists_delete`

## Goal

Verify that `playlists_delete` is exposed as a public Layer 2 MCP tool for `playlists.delete`, with quota cost `50`, OAuth-required access disclosure, required target playlist identity, destructive deletion acknowledgment handling, repeat-delete caveat, and safe validation/error boundaries.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Use branch `239-playlists-delete`.
- Keep YT-139, YT-201, and YT-202 assumptions available for review.
- Add or preserve reStructuredText docstrings for every new or changed Python function.

## Red Phase Checks

Start by adding failing tests that prove the tool is not complete until all required surfaces exist:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_playlists_contract.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_playlists_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected red findings before implementation:
- `playlists_delete` public symbols are missing.
- `playlists_delete` is absent from default registry discovery.
- Metadata does not yet expose `playlists.delete`, quota cost `50`, OAuth requirement, target playlist identity, destructive deletion warning, deletion acknowledgment shape, repeat-delete caveat, examples, and caveats.
- Request validation and result mapping for playlist deletion are missing.

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
  "id": "PL123"
}
```

Representative invalid calls:

```json
{}
```

```json
{
  "id": ""
}
```

```json
{
  "id": "PL123",
  "part": "snippet"
}
```

```json
{
  "id": "PL123",
  "body": {
    "snippet": {
      "title": "Unsupported delete body"
    }
  }
}
```

```json
{
  "id": "PL123",
  "restore": true
}
```

## Review Expectations

Discovery metadata must show:
- Tool name `playlists_delete`
- Upstream operation `playlists.delete`
- Quota cost `50`
- OAuth-backed access requirement
- Required target playlist `id`
- Successful calls delete user-visible playlists
- Deletion acknowledgment result shape
- Repeat-delete caveat
- Safe failure categories
- Out-of-scope workflow boundaries

Successful results must preserve:
- Endpoint identity
- Quota cost
- Safe target context
- OAuth access context
- Deletion acknowledgment

Failures must distinguish:
- Local validation failures
- Missing or insufficient OAuth access
- Quota failures
- Missing, already-deleted, or inaccessible playlist outcomes
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
- Matched seed slice `YT-239`
- Focused passing output for `playlists_delete`
- Full-suite passing output from `pytest`
- Code-quality passing output from `ruff check .`
- Confirmation that every new or changed Python function has a reStructuredText docstring
