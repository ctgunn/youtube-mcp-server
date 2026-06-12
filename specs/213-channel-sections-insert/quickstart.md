# Quickstart: YT-213 Layer 2 Tool `channelSections_insert`

## Goal

Implement the public Layer 2 `channelSections_insert` MCP tool as a near-raw wrapper around the existing Layer 1 `channelSections.insert` capability.

## Prerequisites

- Branch: `213-channel-sections-insert`
- Spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/plan.md`
- Contract: `/Users/ctgunn/Projects/youtube-mcp-server/specs/213-channel-sections-insert/contracts/channel-sections-insert-tool-contract.md`
- Layer 1 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/channel_sections.py`
- Shared Layer 2 dependency: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/`
- Existing channel-sections Layer 2 module: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`

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

- `channelSections_insert` is absent from public discovery.
- No `channelSections_insert` contract builder exists.
- No insert tool descriptor or handler exists.
- Default dispatcher registration does not include `channelSections_insert`.
- OAuth validation, body validation, content-rule validation, partner-context guidance, and create-result mapping are not exposed through Layer 2.

Add or update tests to prove:

- Tool metadata includes `channelSections.insert`, quota `50`, `oauth_required` auth, required `part`, required `body`, required `body.snippet.type`, supported writable fields, partner-context caveats, maximum-section caveat, and out-of-scope boundaries.
- Input schema requires `part` and `body`, rejects unsupported part names, rejects unsupported fields, validates partner-context pairing, and documents supported section content rules.
- Missing OAuth, missing `part`, missing `body`, missing `body.snippet.type`, invalid content structure, duplicate references, capacity failures, unsupported optional parameters, and unsupported higher-level workflow fields produce safe caller-facing failures.
- Successful result mapping preserves created channel-section fields, requested parts, endpoint identity, quota cost, `created`, and safe partner context when present.

## Green Phase

Implement the minimum endpoint-specific Layer 2 behavior:

1. Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`.
2. Define constants for:
   - `CHANNEL_SECTIONS_INSERT_TOOL_NAME`
   - `CHANNEL_SECTIONS_INSERT_QUOTA_COST`
   - supported part names
   - input schema
   - description
   - usage notes
   - caveats
   - caller examples
3. Add `build_channel_sections_insert_contract()`.
4. Add validation for required `part`, supported parts, required `body`, required `body.snippet.type`, section-type-specific content details, duplicate references, required title cases, OAuth preflight, partner-context pairing, section-limit guidance, and unsupported fields.
5. Add a handler that calls the existing Layer 1 `build_channel_sections_insert_wrapper()`.
6. Add result mapping that preserves returned resource fields, requested parts, endpoint identity, quota cost, `created`, and safe partner context when present.
7. Add `build_channel_sections_insert_tool_descriptor()`.
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
- Keep the implementation scoped to `channelSections_insert`; do not add section sorting, section replacement, playlist creation, video metadata expansion, analytics, layout recommendations, channel branding, bulk editing, or enrichment.
- Confirm public metadata, examples, errors, and logs do not expose credentials, OAuth tokens, stack traces, private channel data, CMS account details, owner identifiers, or secret values.
- Confirm all new or changed Python functions have reStructuredText docstrings.

Final validation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest
python3 -m ruff check .
```

## Implementation Evidence

Record focused command output, full-suite output, lint output, docstring review notes, and safety review notes here during implementation.

- 2026-06-11: Focused quickstart verification passed with
  `python3 -m pytest tests/unit/test_youtube_channel_sections.py tests/contract/test_youtube_channel_sections_contract.py tests/integration/test_youtube_channel_sections_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`
  (`148 passed in 0.42s`).
- 2026-06-11: Dispatcher and MCP routing guard verification passed with
  `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`
  (`45 passed in 0.42s`).
- 2026-06-11: Layer 1 guard verification passed with
  `python3 -m pytest tests/contract/test_layer1_channel_sections_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py`
  (`665 passed in 2.14s`).
- 2026-06-11: Safety review found no sensitive-token strings in touched public source files.
  Docstring review found all functions documented in touched Python files.
- 2026-06-11: Full repository test suite passed with `python3 -m pytest`
  (`1934 passed in 11.58s`).
- 2026-06-11: Lint passed with `python3 -m ruff check .`
  (`All checks passed!`).

## Rollback

To rollback this slice, remove:

- `channelSections_insert` dispatcher registration.
- `channelSections_insert` Layer 2 module exports and endpoint-specific helpers from `channel_sections.py`.
- Endpoint-specific tests and examples.

Rollback must preserve YT-113 Layer 1 `channelSections.insert`, YT-201/YT-202 shared contracts, `channelSections_list`, `channels_list`, `channels_update`, and existing activities/captions/channel banner tool behavior.
