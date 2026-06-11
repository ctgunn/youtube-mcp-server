# Quickstart: YT-212 Layer 2 Tool `channelSections_list`

## Goal

Implement the public Layer 2 `channelSections_list` MCP tool as a near-raw wrapper around the existing Layer 1 `channelSections.list` capability.

## Prerequisites

- Branch: `212-channel-sections-list`
- Spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/plan.md`
- Contract: `/Users/ctgunn/Projects/youtube-mcp-server/specs/212-channel-sections-list/contracts/channel-sections-list-tool-contract.md`
- Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`
- Shared Layer 2 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`

## Red Phase

Start with failing tests before implementation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/unit/test_youtube_channel_sections.py \
  tests/contract/test_youtube_channel_sections_contract.py \
  tests/integration/test_youtube_channel_sections_registration.py
```

Expected initial failures:

- `channelSections_list` is absent from public discovery.
- No `channelSections_list` contract builder exists.
- No tool descriptor or handler exists.
- Default dispatcher registration does not include `channelSections_list`.
- Selector validation, caveat disclosure, and channel-section result mapping are not exposed through Layer 2.

Add or update tests to prove:

- Tool metadata includes `channelSections.list`, quota `1`, `mixed/conditional` auth, selectors `channelId`, `id`, and `mine`, OAuth requirement for `mine`, deprecated `hl` caveat, and content-owner partner caveat.
- Input schema requires `part`, requires exactly one selector, rejects unsupported selectors and higher-level workflow fields, and documents optional pagination support only if retained.
- Missing selector, conflicting selectors, empty selectors, invalid `mine`, unsupported pagination fields when unsupported, and missing OAuth for `mine` produce safe caller-facing failures.
- Successful result mapping preserves channel-section items, empty collections, requested parts, selected selector, caveat context, and optional continuation fields when present.

## Green Phase

Implement the minimum endpoint-specific Layer 2 behavior:

1. Create `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`.
2. Define constants for:
   - `CHANNEL_SECTIONS_LIST_TOOL_NAME`
   - `CHANNEL_SECTIONS_LIST_QUOTA_COST`
   - selector names
   - input schema
   - description
   - usage notes
   - caveats
3. Add `build_channel_sections_list_contract()`.
4. Add validation for required `part`, exactly one selector, non-empty selector values, `mine` OAuth preflight, deprecated `hl` caveat visibility, content-owner partner caveat handling, optional pagination compatibility, and unsupported fields.
5. Add a handler that calls the existing Layer 1 `build_channel_sections_list_wrapper()`.
6. Add result mapping that preserves `items`, requested parts, selected selector, caveats, and optional returned continuation fields when present.
7. Add `build_channel_sections_list_tool_descriptor()`.
8. Export new symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
9. Register the descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

Every new or changed Python function must include a reStructuredText docstring covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.

## Focused Verification

Run focused checks while iterating:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/unit/test_youtube_channel_sections.py \
  tests/contract/test_youtube_channel_sections_contract.py \
  tests/integration/test_youtube_channel_sections_registration.py \
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

If Layer 1 wrapper, consumer, validator, or response-normalizer behavior changes, also run:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/contract/test_layer1_channel_sections_contract.py \
  tests/unit/test_layer1_foundation.py \
  tests/unit/test_youtube_transport.py
```

## Refactor Phase

After focused tests pass:

- Remove endpoint-specific duplication that belongs in shared YT-201/YT-202 helpers.
- Keep the implementation scoped to `channelSections_list`; do not add playlist item expansion, video metadata expansion, channel analytics, layout recommendations, section mutations, or enrichment.
- Confirm public metadata, examples, errors, and logs do not expose credentials, OAuth tokens, stack traces, private channel data, CMS account details, or secret values.
- Confirm all new or changed Python functions have reStructuredText docstrings.

Final validation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest
python3 -m ruff check .
```

## Implementation Evidence

Record focused command output, full-suite output, lint output, docstring review notes, and safety review notes here during implementation.

- Focused quickstart and YouTube metadata regression:
  `python3 -m pytest tests/unit/test_youtube_channel_sections.py tests/contract/test_youtube_channel_sections_contract.py tests/integration/test_youtube_channel_sections_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py -q`
  passed with `107 passed`.
- Dispatcher and MCP routing guard:
  `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py -q`
  passed with `44 passed`.
- Layer 1 guard group:
  `python3 -m pytest tests/contract/test_layer1_channel_sections_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py -q`
  passed with `665 passed`.
- Full repository validation:
  `python3 -m pytest`
  passed with `1892 passed`.
- Lint validation:
  `python3 -m ruff check .`
  passed with `All checks passed!`.
- Safety/docstring review:
  Public `channelSections_list` metadata, examples, mapped errors, and source implementation were reviewed for token, stack trace, private channel, CMS account, and secret leakage. Changed Python functions/classes were checked for reStructuredText docstrings.

## Rollback

To rollback this slice, remove:

- `channelSections_list` dispatcher registration.
- `channelSections_list` Layer 2 module exports and endpoint-specific helpers from `channel_sections.py`.
- Endpoint-specific tests and examples.

Rollback must preserve YT-112 Layer 1 `channelSections.list`, YT-201/YT-202 shared contracts, `channels_list`, `channels_update`, and existing activities/captions/channel banner tool behavior.
