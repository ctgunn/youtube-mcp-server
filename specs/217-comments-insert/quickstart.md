# Quickstart: Layer 2 Tool `comments_insert`

## Prerequisites

- Work from repository root: `/Users/ctgunn/Projects/youtube-mcp-server`
- Branch: `217-comments-insert`
- Read the feature artifacts:
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/spec.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/plan.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/217-comments-insert/contracts/comments-insert-tool-contract.md`

## Red Phase

Add failing tests before implementation:

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected initial failures should show that `comments_insert` is not yet exposed through the concrete comments module, shared exports, metadata contracts, examples, registration, and default tool catalog.

## Green Phase

Implement only the minimum required behavior:

1. Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comments.py` with `comments_insert` constants, schema, examples, contract builder, validator, result mapper, handler, descriptor, and safe error mapping.
2. Export the new symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
3. Register `build_comments_insert_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
4. Preserve the Layer 1 dependency on `build_comments_insert_wrapper()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comments.py`.

Run the focused tests until they pass:

```bash
pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Refactor Phase

Clean up duplication while preserving behavior:

- Keep `comments.py` cohesive with `comments_list` and `comments_insert` grouped clearly.
- Preserve reStructuredText docstrings for every new or changed Python function.
- Keep public metadata and errors free of API keys, OAuth tokens, stack traces, raw upstream diagnostics, and unsafe credential details.
- Keep out-of-scope behavior out of the tool: top-level comment-thread creation, listing, updates, moderation, deletion, generated replies, sentiment, ranking, summarization, and enrichment.

Run final verification:

```bash
pytest
ruff check .
```

## Manual Review Checklist

- `comments_insert` appears in default tool discovery.
- Metadata shows `comments.insert`, quota cost `50`, auth mode `oauth_required`, and active availability.
- Input schema requires `part`, `body.snippet.parentId`, and `body.snippet.textOriginal`.
- Examples cover authorized reply creation, delegated context, missing OAuth, missing part, missing parent comment, missing reply text, unsupported top-level create shape, unsupported option, and parent-comment failure.
- Successful results return a near-raw created comment result and do not fabricate unrelated data.
- Safe errors distinguish invalid request, missing OAuth, insufficient authorization, quota, missing parent comment, endpoint unavailable, and unexpected upstream failure.

## Verification Evidence

Recorded on 2026-06-18 from `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comments_contract.py tests/unit/test_youtube_comments.py tests/integration/test_youtube_comments_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
# 163 passed in 0.55s

python3 -m ruff check .
# All checks passed.

PYTHONPATH=src python3 -m pytest
# 2097 passed in 10.88s
```
