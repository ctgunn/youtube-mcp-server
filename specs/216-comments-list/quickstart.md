# Quickstart: `comments_list`

## Goal

Verify the YT-216 plan and future implementation for the public Layer 2 `comments_list` MCP tool.

## Expected Tool Contract

- Tool name: `comments_list`
- Endpoint: `comments.list`
- Quota cost: `1`
- Auth: mixed or conditional, with access-sensitive limitations documented
- Required input: `part`
- Required selector: exactly one of `id` or `parentId`
- Optional input with `parentId`: `maxResults`, `pageToken`, `textFormat`
- Request body: unsupported
- Result: near-raw comment list payload with safe operation context, requested parts, selector, pagination context, text-format context, and returned comment items

## Example Calls

ID-based comment retrieval:

```json
{
  "part": "id,snippet",
  "id": "comment-123"
}
```

Parent-comment reply retrieval:

```json
{
  "part": "snippet",
  "parentId": "comment-parent-123"
}
```

Paginated parent-comment reply retrieval:

```json
{
  "part": "snippet",
  "parentId": "comment-parent-123",
  "maxResults": 25,
  "pageToken": "NEXT_PAGE"
}
```

Plain-text reply retrieval:

```json
{
  "part": "snippet",
  "parentId": "comment-parent-123",
  "textFormat": "plainText"
}
```

Unsupported conflicting selectors:

```json
{
  "part": "snippet",
  "id": "comment-123",
  "parentId": "comment-parent-123"
}
```

Expected conflicting-selector category: `invalid_request`.

Unsupported pagination with ID selector:

```json
{
  "part": "snippet",
  "id": "comment-123",
  "maxResults": 25
}
```

Expected pagination-with-ID category: `invalid_request`.

## Red Checks To Add First

```bash
pytest tests/contract/test_youtube_comments_contract.py -k list
pytest tests/unit/test_youtube_comments.py -k list
pytest tests/integration/test_youtube_comments_registration.py -k list
```

These checks should fail before implementation because `comments_list` symbols, contract metadata, handler behavior, and registry integration are not yet present.

## Green Implementation Targets

1. Add `COMMENTS_LIST_*` constants, schema, description, usage notes, caveats, examples, and error type in `src/mcp_server/tools/youtube_common/comments.py`.
2. Add contract, result mapper, validator, auth helper, upstream-error mapper, handler builder, descriptor builder, and default list transport.
3. Export symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Add representative contract entry in `src/mcp_server/tools/youtube_common/examples.py` if required by existing representative coverage.
5. Register the descriptor in the default dispatcher.

## Final Verification

Run focused checks:

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py
```

Run required full checks:

```bash
pytest
ruff check .
```

Review evidence should include passing focused output, full-suite output, lint output, and confirmation that all new or changed Python functions have reStructuredText docstrings.

## Verification Evidence

- Focused feature verification: `python3 -m pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py` passed with 93 tests on 2026-06-15.
- Lint verification: `python3 -m ruff check .` passed on 2026-06-15.
- Full repository verification: `python3 -m pytest` passed with 2058 tests on 2026-06-15.
- Documentation review: new and changed Python functions in `src/mcp_server/tools/youtube_common/comments.py` include reStructuredText docstrings covering inputs, outputs, selector behavior, auth behavior, pagination behavior, text-format behavior, safe no-match behavior, and result shape.
