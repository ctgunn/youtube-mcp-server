# Quickstart: `commentThreads_list`

## Goal

Verify the YT-221 plan and future implementation for the public Layer 2 `commentThreads_list` MCP tool.

## Expected Tool Contract

- Tool name: `commentThreads_list`
- Endpoint: `commentThreads.list`
- Quota cost: `1`
- Auth: API-key public retrieval, with access-sensitive caveats for moderation-status usage and inaccessible resources
- Required input: `part`
- Required selector: exactly one of `videoId`, `allThreadsRelatedToChannelId`, or `id`
- Optional input with non-`id` selectors: `maxResults`, `moderationStatus`, `order`, `pageToken`, `searchTerms`, `textFormat`
- Optional input with `id`: `textFormat` only from the optional set
- Request body: unsupported
- Result: near-raw comment-thread list payload with safe operation context, requested parts, selector, pagination context, supported option context, text-format context, and returned comment-thread items

## Example Calls

Video-based thread retrieval:

```json
{
  "part": "snippet,replies",
  "videoId": "video-123"
}
```

Channel-related thread retrieval:

```json
{
  "part": "snippet",
  "allThreadsRelatedToChannelId": "channel-123"
}
```

ID-based thread retrieval:

```json
{
  "part": "id,snippet",
  "id": "thread-123"
}
```

Paginated video-based retrieval:

```json
{
  "part": "snippet",
  "videoId": "video-123",
  "maxResults": 25,
  "pageToken": "NEXT_PAGE"
}
```

Ordered and searched retrieval:

```json
{
  "part": "snippet",
  "videoId": "video-123",
  "order": "relevance",
  "searchTerms": "launch"
}
```

Plain-text retrieval:

```json
{
  "part": "snippet",
  "videoId": "video-123",
  "textFormat": "plainText"
}
```

Access-sensitive moderation-status retrieval:

```json
{
  "part": "snippet",
  "videoId": "video-123",
  "moderationStatus": "heldForReview"
}
```

Unsupported conflicting selectors:

```json
{
  "part": "snippet",
  "videoId": "video-123",
  "id": "thread-123"
}
```

Expected conflicting-selector category: `invalid_request`.

Unsupported pagination with ID selector:

```json
{
  "part": "snippet",
  "id": "thread-123",
  "maxResults": 25
}
```

Expected pagination-with-ID category: `invalid_request`.

## Red Checks To Add First

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py -k list
PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_comment_threads.py -k list
PYTHONPATH=src python3 -m pytest tests/integration/test_youtube_comment_threads_registration.py -k list
```

These checks should fail before implementation because `commentThreads_list` symbols, contract metadata, handler behavior, and registry integration are not yet present.

## Green Implementation Targets

1. Add `COMMENT_THREADS_LIST_*` constants, schema, description, usage notes, caveats, examples, and error type in `src/mcp_server/tools/youtube_common/comment_threads.py`.
2. Add contract, result mapper, validator, auth helper, upstream-error mapper, handler builder, descriptor builder, and default list transport.
3. Export symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Add representative contract entry in `src/mcp_server/tools/youtube_common/examples.py` if required by existing representative coverage.
5. Register the descriptor in the default dispatcher.

## Final Verification

Run focused checks:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Run required full checks:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

Review evidence should include passing focused output, full-suite output, lint output, and confirmation that all new or changed Python functions have reStructuredText docstrings.

## Implementation Evidence

- Red scaffold suite observed failing before implementation with `ModuleNotFoundError: No module named 'mcp_server.tools.youtube_common.comment_threads'`.
- US1 focused suite passed after Green implementation: `53 passed`.
- US2 metadata suite passed with explicit import path: `75 passed`.
- US3 validation and safe-error suite passed: `53 passed`.
- Full focused feature suite passed: `161 passed`.
- Full repository suite passed: `2291 passed`.
- Ruff passed: `All checks passed!`.
- New and changed Python functions in the Layer 2 module, Layer 1 metadata adjustment, registry/export wiring, and test fakes have reStructuredText docstrings where applicable.
