# Quickstart: YT-241 Layer 2 Tool `subscriptions_list`

## Goal

Verify that `subscriptions_list` is exposed as a public Layer 2 MCP tool for `subscriptions.list`, with quota cost `1`, conditional access disclosure, required part selection, supported selectors, pagination and ordering behavior, empty-result handling, and safe validation/error boundaries.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Use branch `241-subscriptions-list`.
- Keep YT-141, YT-201, and YT-202 assumptions available for review.
- Add or preserve reStructuredText docstrings for every new or changed Python function.

## Red Phase Checks

Start by adding failing tests that prove the tool is not complete until all required surfaces exist:

```bash
PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_subscriptions_contract.py tests/unit/test_youtube_subscriptions.py tests/integration/test_youtube_subscriptions_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

Expected red findings before implementation:
- `subscriptions_list` public symbols are missing.
- `subscriptions_list` is absent from default registry discovery.
- Metadata does not yet expose `subscriptions.list`, quota cost `1`, conditional access, selectors, pagination, ordering, examples, and caveats.
- Request validation and result mapping for subscriptions are missing.

## Green Phase Checks

Implement the smallest endpoint-backed tool surface needed for:

- Public module `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/subscriptions.py`
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
  "id": "subscription-123"
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
  "part": "subscriberSnippet",
  "myRecentSubscribers": true,
  "maxResults": 25
}
```

```json
{
  "part": "subscriberSnippet",
  "mySubscribers": true,
  "order": "relevance"
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
  "mine": true
}
```

```json
{
  "part": "snippet",
  "mine": false
}
```

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "maxResults": 51
}
```

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "order": "newest"
}
```

```json
{
  "part": "snippet",
  "channelId": "UC123",
  "includeChannelStatistics": true
}
```

## Review Expectations

Discovery metadata must show:
- Tool name `subscriptions_list`
- Upstream operation `subscriptions.list`
- Quota cost `1`
- Conditional access:
  - `channelId` and `id` use public-compatible lookup
  - `mine`, `myRecentSubscribers`, and `mySubscribers` require OAuth-backed access
- Required `part`
- Supported selectors `channelId`, `id`, `mine`, `myRecentSubscribers`, and `mySubscribers`
- Pagination and ordering behavior
- Empty successful collection behavior
- Private subscriber and visibility caveats
- Safe failure categories
- Out-of-scope workflow boundaries

Successful results must preserve:
- Endpoint identity
- Quota cost
- Requested parts
- Selector context
- Access context
- Pagination context when applicable
- Returned subscription items, including empty collections

Failures must distinguish:
- Local validation failures
- User-context access failures
- Quota failures
- Missing subscriber or subscription target outcomes
- Account closed or suspended outcomes
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
- Matched seed slice `YT-241`
- Focused passing output for `subscriptions_list`
- Full-suite passing output from `pytest`
- Code-quality passing output from `ruff check .`
- Confirmation that every new or changed Python function has a reStructuredText docstring
