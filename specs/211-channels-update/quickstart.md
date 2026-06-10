# Quickstart: YT-211 Layer 2 Tool `channels_update`

## Goal

Implement the public Layer 2 `channels_update` MCP tool as a near-raw wrapper around the existing Layer 1 `channels.update` capability.

## Prerequisites

- Branch: `211-channels-update`
- Spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/plan.md`
- Contract: `/Users/ctgunn/Projects/youtube-mcp-server/specs/211-channels-update/contracts/channels-update-tool-contract.md`
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

- `channels_update` is absent from public discovery.
- No `channels_update` contract builder exists.
- No tool descriptor or handler exists.
- Default dispatcher registration does not include `channels_update`.
- OAuth-required validation and updated-channel result mapping are not exposed through Layer 2.

Add or update tests to prove:

- Tool metadata includes `channels.update`, quota `50`, `oauth_required`, supported writable parts, overwrite warning, and banner boundary.
- Input schema requires `part` and `body`.
- Missing OAuth, missing body, missing `body.id`, unsupported part, multiple parts, part-to-body mismatch, read-only fields, and unsupported channel workflow fields produce safe caller-facing failures.
- Successful update mapping preserves returned channel resource fields, selected writable part, requested parts, endpoint identity, and quota cost.

## Green Phase

Implement the minimum endpoint-specific Layer 2 behavior:

1. Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channels.py`.
2. Define constants for:
   - `CHANNELS_UPDATE_TOOL_NAME`
   - `CHANNELS_UPDATE_QUOTA_COST`
   - supported writable parts
   - input schema
   - description
   - usage notes
   - caveats
3. Add `build_channels_update_contract()`.
4. Add validation for required OAuth, required `part`, one supported writable part, required `body`, required `body.id`, part-to-body alignment, unsupported fields, read-only fields, and unsupported delegation fields while delegation remains outside this slice.
5. Add a handler that calls the existing Layer 1 `build_channels_update_wrapper()`.
6. Add updated-resource mapping that preserves returned channel fields and safe operation context.
7. Add `build_channels_update_tool_descriptor()`.
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

If Layer 1 wrapper behavior, validators, consumers, or normalizers change, also run:

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
- Keep the implementation scoped to `channels_update`; do not add channel lookup, banner upload, analytics, video expansion, playlist expansion, or multi-step channel management.
- Confirm public metadata, examples, errors, and logs do not expose credentials, stack traces, private channel data, sensitive channel body values, or secret values.
- Confirm all new or changed Python functions have reStructuredText docstrings.

Final validation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest
python3 -m ruff check .
```

## Implementation Evidence

Record focused command output, full-suite output, lint output, docstring review notes, and safety review notes here during implementation.

- 2026-06-09: `python3 -m pytest tests/unit/test_youtube_channels.py tests/contract/test_youtube_channels_contract.py tests/integration/test_youtube_channels_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py -q` -> 134 passed.
- 2026-06-09: `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py -q` -> 41 passed.
- 2026-06-09: `python3 -m pytest tests/contract/test_layer1_channels_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py -q` -> 662 passed.
- 2026-06-09: `python3 -m pytest` -> 1853 passed.
- 2026-06-09: `python3 -m ruff check .` -> All checks passed.
- 2026-06-09: Public metadata and mapped errors reviewed for credential, OAuth token, stack trace, private channel data, sensitive body, or secret leakage; no leaks found in YT-211 surfaces.
- 2026-06-09: New and modified Python functions in the YT-211 implementation include reStructuredText-style docstrings with parameters, return values, and raised error notes where relevant.

## Rollback

To rollback this slice, remove:

- `channels_update` dispatcher registration.
- `channels_update` Layer 2 module exports and endpoint-specific helpers from `channels.py`.
- Endpoint-specific tests and examples.

Rollback must preserve YT-111 Layer 1 `channels.update`, YT-201/YT-202 shared contracts, `channels_list`, and existing activities/captions/channel banner tool behavior.
