# Quickstart: YT-209 Layer 2 Tool `channelBanners_insert`

## Goal

Implement the public Layer 2 `channelBanners_insert` MCP tool as a near-raw wrapper around the existing Layer 1 `channelBanners.insert` capability.

## Prerequisites

- Branch: `209-channel-banners-insert`
- Spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/plan.md`
- Contract: `/Users/ctgunn/Projects/youtube-mcp-server/specs/209-channel-banners-insert/contracts/channel-banners-insert-tool-contract.md`
- Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_banners.py`
- Shared Layer 2 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`

## Red Phase

Start with failing tests before implementation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/unit/test_youtube_channel_banners.py \
  tests/contract/test_youtube_channel_banners_contract.py \
  tests/integration/test_youtube_channel_banners_registration.py
```

Expected initial failures:

- `channelBanners_insert` is absent from public discovery.
- No `channelBanners_insert` contract builder exists.
- No tool descriptor or handler exists.
- Default dispatcher registration does not include `channelBanners_insert`.
- Media validation and upload-result mapping are not exposed through Layer 2.

Add or update tests to prove:

- Tool metadata includes `channelBanners.insert`, quota `50`, `oauth_required`, media requirement, and `onBehalfOfContentOwner` notes.
- Input schema requires `media` and rejects unsupported metadata/body fields.
- Missing media, invalid MIME type, oversized media, unsupported image-editing options, and missing OAuth paths produce safe caller-facing failures.
- Successful upload mapping preserves returned `channelBanner` fields and returned URL without exposing raw image payloads.

## Green Phase

Implement the minimum endpoint-specific Layer 2 behavior:

1. Create `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_banners.py`.
2. Define constants for:
   - `CHANNEL_BANNERS_INSERT_TOOL_NAME`
   - `CHANNEL_BANNERS_INSERT_QUOTA_COST`
   - input schema
   - description
   - usage notes
   - caveats
3. Add `build_channel_banners_insert_contract()`.
4. Add validation for required media input, supported MIME types, safe size limits, unsupported fields, and optional delegation context.
5. Add a handler that calls the existing Layer 1 `build_channel_banners_insert_wrapper()`.
6. Add upload-result mapping that preserves returned `kind`, `etag`, `url`, and safe operation context.
7. Add `build_channel_banners_insert_tool_descriptor()`.
8. Export new symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
9. Register the descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.

Every new or changed Python function must include a reStructuredText docstring covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.

## Focused Verification

Run focused checks while iterating:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/unit/test_youtube_channel_banners.py \
  tests/contract/test_youtube_channel_banners_contract.py \
  tests/integration/test_youtube_channel_banners_registration.py \
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

If Layer 1 wrapper behavior or validators change, also run:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest \
  tests/contract/test_layer1_channel_banners_contract.py \
  tests/unit/test_layer1_foundation.py
```

## Refactor Phase

After focused tests pass:

- Remove endpoint-specific duplication that belongs in shared YT-201/YT-202 helpers.
- Keep the implementation scoped to `channelBanners_insert`; do not add active banner publication or `channels.update`.
- Confirm public metadata, examples, errors, and logs do not expose credentials, raw image payloads, binary content, private channel data, signed URLs, stack traces, or secret values.
- Confirm all new or changed Python functions have reStructuredText docstrings.

Final validation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest
python3 -m ruff check .
```

## Implementation Evidence

- Focused YT-209 validation passed: `99 passed in 0.42s`.
- MCP discovery and routing guards passed after dispatcher registration changes: `37 passed in 0.28s`.
- Layer 1 guard command was not required because no Layer 1 wrapper or validator files changed during implementation.
- Full repository suite passed: `1780 passed in 10.90s`.
- Ruff passed: `All checks passed!`.
- Safety review confirmed public metadata, examples, mapped errors, and tests do not expose credentials, stack traces, signed URLs, raw image payloads, binary payloads, private channel data, or secret values.
- Docstring review confirmed every new or modified Python function and test helper has a reStructuredText-style docstring.

## Rollback

To rollback this slice, remove:

- `channelBanners_insert` dispatcher registration.
- `channel_banners.py` Layer 2 module exports.
- Endpoint-specific tests and examples.

Rollback must preserve YT-109 Layer 1 `channelBanners.insert`, YT-201/YT-202 shared contracts, and existing activities/captions tool behavior.
