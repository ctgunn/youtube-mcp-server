# Quickstart: YT-210 Layer 2 Tool `channels_list`

## Goal

Implement the public Layer 2 `channels_list` MCP tool as a near-raw wrapper around the existing Layer 1 `channels.list` capability.

## Prerequisites

- Branch: `210-channels-list`
- Spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/plan.md`
- Contract: `/Users/ctgunn/Projects/youtube-mcp-server/specs/210-channels-list/contracts/channels-list-tool-contract.md`
- Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channels.py`
- Shared Layer 2 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`

## Red Phase

Start with failing tests before implementation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/unit/test_youtube_channels.py \
  tests/contract/test_youtube_channels_contract.py \
  tests/integration/test_youtube_channels_registration.py
```

Expected initial failures:

- `channels_list` is absent from public discovery.
- No `channels_list` contract builder exists.
- No tool descriptor or handler exists.
- Default dispatcher registration does not include `channels_list`.
- Selector validation and channel result mapping are not exposed through Layer 2.

Add or update tests to prove:

- Tool metadata includes `channels.list`, quota `1`, `mixed/conditional` auth, selectors `id`, `mine`, `forHandle`, and `forUsername`, and OAuth requirement for `mine`.
- Input schema requires `part`, requires exactly one selector, supports pagination fields, and rejects unsupported higher-level channel workflow fields.
- Missing selector, conflicting selectors, empty selectors, invalid `maxResults`, and missing OAuth for `mine` produce safe caller-facing failures.
- Successful result mapping preserves channel items, empty collections, requested parts, selected selector, and pagination fields.

## Green Phase

Implement the minimum endpoint-specific Layer 2 behavior:

1. Create `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`.
2. Define constants for:
   - `CHANNELS_LIST_TOOL_NAME`
   - `CHANNELS_LIST_QUOTA_COST`
   - selector names
   - input schema
   - description
   - usage notes
   - caveats
3. Add `build_channels_list_contract()`.
4. Add validation for required `part`, exactly one selector, non-empty selector values, `mine` OAuth preflight, optional pagination, and unsupported fields.
5. Add a handler that calls the existing Layer 1 `build_channels_list_wrapper()`.
6. Add result mapping that preserves `items`, requested parts, selected selector, `nextPageToken`, `prevPageToken`, and `pageInfo`.
7. Add `build_channels_list_tool_descriptor()`.
8. Export new symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
9. Register the descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

Every new or changed Python function must include a reStructuredText docstring covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.

## Focused Verification

Run focused checks while iterating:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/unit/test_youtube_channels.py \
  tests/contract/test_youtube_channels_contract.py \
  tests/integration/test_youtube_channels_registration.py \
  tests/unit/test_youtube_common_scaffolding.py \
  tests/contract/test_youtube_common_contract.py \
  tests/contract/test_youtube_tool_catalog_contract.py \
  tests/integration/test_youtube_tool_registration.py
```

If dispatcher discovery or MCP routing changes, also run:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/unit/test_list_tools_method.py \
  tests/unit/test_method_routing.py \
  tests/integration/test_mcp_request_flow.py
```

If Layer 1 wrapper, consumer, or response-normalizer behavior changes, also run:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/contract/test_layer1_channels_contract.py \
  tests/unit/test_layer1_foundation.py \
  tests/unit/test_youtube_transport.py
```

## Refactor Phase

After focused tests pass:

- Remove endpoint-specific duplication that belongs in shared YT-201/YT-202 helpers.
- Keep the implementation scoped to `channels_list`; do not add analytics, ranking, expansion, enrichment, or channel update behavior.
- Confirm public metadata, examples, errors, and logs do not expose credentials, OAuth tokens, stack traces, private channel data, or secret values.
- Confirm all new or changed Python functions have reStructuredText docstrings.

Final validation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest
python3 -m ruff check .
```

## Implementation Evidence

Recorded on 2026-06-08:

- Focused YT-210 validation: `python3 -m pytest tests/unit/test_youtube_channels.py tests/contract/test_youtube_channels_contract.py tests/integration/test_youtube_channels_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` passed with 99 tests.
- MCP discovery and routing guards: `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py` passed with 39 tests.
- Layer 1 guard output: `python3 -m pytest tests/contract/test_layer1_channels_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py` passed with 662 tests.
- Full repository suite output from `python3 -m pytest`: passed with 1816 tests.
- Ruff output from `python3 -m ruff check .`: passed.
- Safety review confirming public metadata, examples, mapped errors, and tests do not expose credentials, stack traces, private channel data, or secret values: passed.
- Docstring review confirming every new or modified Python function and test helper has a reStructuredText-style docstring: passed.

## Rollback

To rollback this slice, remove:

- `channels_list` dispatcher registration.
- `channels.py` Layer 2 module exports.
- Endpoint-specific tests and examples.

Rollback must preserve YT-110 Layer 1 `channels.list`, YT-201/YT-202 shared contracts, and existing activities/captions/channel-banner tool behavior.
