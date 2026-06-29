# Quickstart: `commentThreads_insert`

## Goal

Verify the YT-222 plan and future implementation for the public Layer 2 `commentThreads_insert` MCP tool.

## Expected Tool Contract

- Tool name: `commentThreads_insert`
- Endpoint: `commentThreads.insert`
- Quota cost: `50`
- Auth: OAuth-required write access; API-key-only access is unsupported
- Required input: `part`
- Required body: `body.snippet.channelId`, `body.snippet.videoId`, and `body.snippet.topLevelComment.snippet.textOriginal`
- Optional input: `onBehalfOfContentOwner` only with eligible delegated OAuth authorization
- Result: near-raw created comment-thread payload with safe operation context, requested parts, target context, OAuth context, optional delegation context, and returned comment-thread resource
- Out of scope: thread listing, reply creation, comment update, moderation, deletion, generated responses, ranking, summarization, enrichment, analytics, and cross-endpoint aggregation

## Example Calls

Authorized top-level comment creation:

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Great walkthrough."
        }
      }
    }
  }
}
```

Delegated owner context:

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Posting from the channel team."
        }
      }
    }
  },
  "onBehalfOfContentOwner": "CONTENT_OWNER_ID"
}
```

Unsupported reply creation shape:

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "parentId": "comment-parent-123",
      "textOriginal": "This belongs to comments_insert."
    }
  }
}
```

Expected reply-shape category: `invalid_request`.

Missing top-level comment text:

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {}
      }
    }
  }
}
```

Expected missing-text category: `invalid_request`.

Missing OAuth context:

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "channelId": "channel-123",
      "videoId": "video-123",
      "topLevelComment": {
        "snippet": {
          "textOriginal": "Top-level comment text"
        }
      }
    }
  }
}
```

Expected missing-OAuth category when no eligible OAuth context is available: `authentication_failed`.

## Red Checks To Add First

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py -k insert
PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_comment_threads.py -k insert
PYTHONPATH=src python3 -m pytest tests/integration/test_youtube_comment_threads_registration.py -k insert
```

These checks should fail before implementation because `commentThreads_insert` symbols, contract metadata, handler behavior, examples, and registry integration are not yet present.

## Green Implementation Targets

1. Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/comment_threads.py` with `COMMENT_THREADS_INSERT_*` constants, schema, description, usage notes, caveats, examples, error type, contract builder, validator, OAuth helper, result mapper, upstream-error mapper, handler builder, descriptor builder, and default insert transport.
2. Export the new symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
3. Register `build_comment_threads_insert_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
4. Add representative contract entry in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` if required by existing representative coverage.
5. Preserve the Layer 1 dependency on `build_comment_threads_insert_wrapper()` from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/comment_threads.py`.

Run focused tests until they pass:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Refactor Phase

Clean up duplication while preserving behavior:

- Keep `comment_threads.py` cohesive with `commentThreads_list` and `commentThreads_insert` grouped clearly.
- Preserve reStructuredText docstrings for every new or changed Python function.
- Keep public metadata and errors free of API keys, OAuth tokens, stack traces, raw upstream diagnostics, and unsafe credential details.
- Keep out-of-scope behavior out of the tool: thread listing, reply creation, updates, moderation, deletion, generated responses, sentiment, ranking, summarization, enrichment, analytics, and cross-endpoint aggregation.

Run final verification:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

## Manual Review Checklist

- `commentThreads_insert` appears in default tool discovery.
- Metadata shows `commentThreads.insert`, quota cost `50`, auth mode `oauth_required`, and active availability.
- Input schema requires `part`, `body.snippet.channelId`, `body.snippet.videoId`, and `body.snippet.topLevelComment.snippet.textOriginal`.
- Examples cover authorized top-level thread creation, delegated context, missing OAuth, missing part, missing target channel, missing target video, missing top-level comment text, unsupported reply create shape, unsupported option, disabled comments, and missing target failure.
- Successful results return a near-raw created comment-thread result and do not fabricate unrelated data.
- Safe errors distinguish invalid request, missing OAuth, insufficient authorization, quota, missing channel, missing video, disabled comments, endpoint unavailable, and unexpected upstream failure.

## Verification Evidence

Recorded during implementation on 2026-06-29:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_comment_threads_contract.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_comment_threads_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
# 204 passed

PYTHONPATH=src python3 -m pytest
# 2334 passed

PYTHONPATH=src python3 -m ruff check .
# All checks passed
```
