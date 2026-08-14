# Quickstart: Verify `channels_listPlaylists`

## Prerequisites

- Python 3.11 or later and repository dependencies, including Ruff.
- Public read capability only when using a live path. Never place secrets in commands, fixtures, logs, or documentation.

## Contract Summary

- Accept exactly one trimmed nonblank `channelId` and optional whole-number `maxResults` from 1 through 50, default 25.
- Verify the channel once, then make one bounded playlist listing request; do not traverse pages, rank, search, enrich, or aggregate channels.
- Preserve source order; return stable playlist identity/title and available public metadata with provenance.
- Treat a successful empty source collection for a verified channel as successful empty output; return an unavailable outcome for an unknown channel and safe errors for access, capacity, and source failures.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, integration, and routing tests for schema, validation, exact dependency call, result mapping, order, empty success, errors, discovery, exports, and registration.
2. **Green**: Add only the channel-family descriptor, validator, fixed two-read adapter, normalizer, safe mapping, export, and registration needed by those tests.
3. **Refactor**: Consolidate local helpers, keep reStructuredText docstrings on all changed Python functions, then rerun focused and full checks.

## Verification Commands

```bash
PYTHONPATH=src python3 -m pytest \
  tests/unit/test_youtube_composed_channels.py \
  tests/contract/test_youtube_composed_channels_contract.py \
  tests/integration/test_youtube_composed_tool_registration.py \
  tests/integration/test_youtube_tool_registration.py \
  tests/unit/test_method_routing.py

PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

## Review Evidence

Include failing-then-passing focused tests, discovery output proving default registration and no representative-only marker, result examples for populated/sparse/empty collections and default/minimum/maximum limits, safe error evidence without sensitive details, proof of one verification and one playlist-listing request per invocation, full-suite/lint output, and reStructuredText docstrings for every changed Python function.
