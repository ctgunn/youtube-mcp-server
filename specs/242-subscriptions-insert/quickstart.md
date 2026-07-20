# Quickstart: YT-242 Layer 2 Tool `subscriptions_insert`

## Goal

Verify that `subscriptions_insert` is exposed as a public Layer 2 MCP tool for `subscriptions.insert`, with quota cost `50`, OAuth-required access disclosure, required `part=snippet`, required target channel body, mutation-result handling, duplicate/ineligible target caveats, and safe validation/error boundaries.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Use branch `242-subscriptions-insert`.
- Keep YT-142, YT-201, and YT-202 assumptions available for review.
- Add or preserve reStructuredText docstrings for every new or changed Python function.

## Red Phase Checks

Start by adding failing tests that prove the tool is not complete until all required surfaces exist:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected red findings before implementation:
- `subscriptions_insert` public symbols are missing.
- `subscriptions_insert` is absent from default registry discovery.
- Metadata does not yet expose `subscriptions.insert`, quota cost `50`, OAuth requirement, writable create semantics, target channel requirement, mutation warning, duplicate/ineligible target caveats, examples, and caveats.
- Request validation and result mapping for subscription creation are missing.

## Green Phase Checks

Implement the smallest endpoint-backed tool surface needed for:

- Existing public module `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
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
      "resourceId": {
        "channelId": "UC123"
      }
    }
  }
}
```

Representative successful call with explicit resource kind:

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "kind": "youtube#channel",
        "channelId": "UC123"
      }
    }
  }
}
```

Representative invalid calls:

```json
{
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      }
    }
  }
}
```

```json
{
  "part": "contentDetails",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      }
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
    "snippet": {
      "resourceId": {}
    }
  }
}
```

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "kind": "youtube#playlist",
        "channelId": "UC123"
      }
    }
  }
}
```

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      },
      "title": "Unsupported by this slice"
    }
  }
}
```

```json
{
  "part": "snippet",
  "body": {
    "snippet": {
      "resourceId": {
        "channelId": "UC123"
      }
    }
  },
  "deleteExistingSubscription": true
}
```

## Review Expectations

Discovery metadata must show:
- Tool name `subscriptions_insert`
- Upstream operation `subscriptions.insert`
- Quota cost `50`
- OAuth-backed access requirement
- Required `part=snippet`
- Required `body.snippet.resourceId.channelId`
- Optional `body.snippet.resourceId.kind` boundary
- Successful calls create subscription relationships for the authorized account
- Duplicate and ineligible target caveats
- Safe failure categories
- Out-of-scope workflow boundaries

Successful results must preserve:
- Endpoint identity
- Quota cost
- Requested parts
- Safe target channel context
- OAuth access context
- Returned created subscription resource

Failures must distinguish:
- Local validation failures
- Missing or insufficient OAuth access
- Duplicate or ineligible target failures
- Quota failures
- Authorization failures
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
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
PYTHONPATH=src python3 -m pytest
python3 -m ruff check .
```

Completion evidence must include:
- Matched seed slice `YT-242`
- Focused passing output for `subscriptions_insert`
- Full-suite passing output from `pytest`
- Code-quality passing output from `ruff check .`
- Confirmation that every new or changed Python function has a reStructuredText docstring
