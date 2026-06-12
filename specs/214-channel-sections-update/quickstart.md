# Quickstart: YT-214 Layer 2 Tool `channelSections_update`

## Goal

Implement the public Layer 2 `channelSections_update` MCP tool as a near-raw wrapper around the existing Layer 1 `channelSections.update` capability.

## Prerequisites

- Branch: `214-channel-sections-update`
- Spec: `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/spec.md`
- Plan: `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/plan.md`
- Contract: `/Users/ctgunn/Projects/youtube-mcp-server/specs/214-channel-sections-update/contracts/channel-sections-update-tool-contract.md`
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

- `channelSections_update` is absent from public discovery.
- No `channelSections_update` contract builder exists.
- No update tool descriptor or handler exists.
- Default dispatcher registration does not include `channelSections_update`.
- OAuth validation, `body.id` validation, body validation, content-rule validation, partner-context guidance, overwrite-sensitive update guidance, and update-result mapping are not exposed through Layer 2.

Add or update tests to prove:

- Tool metadata includes `channelSections.update`, quota `50`, `oauth_required` auth, required `part`, required `body`, required `body.id`, required `body.snippet.type`, supported writable fields, overwrite behavior, partner-context caveats, and out-of-scope boundaries.
- Input schema requires `part` and `body`, rejects unsupported part names, rejects unsupported fields, validates partner-context usage, and documents supported section content rules.
- Missing OAuth, missing `part`, missing `body`, missing `body.id`, missing `body.snippet.type`, invalid writable fields, invalid content structure, duplicate references, missing target sections, not-editable sections, unsupported optional parameters, and unsupported higher-level workflow fields produce safe caller-facing failures.
- Successful result mapping preserves updated channel-section fields, requested parts, endpoint identity, quota cost, `updated`, and safe partner context when present.

## Green Phase

Implement the minimum endpoint-specific Layer 2 behavior:

1. Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`.
2. Define constants for:
   - `CHANNEL_SECTIONS_UPDATE_TOOL_NAME`
   - `CHANNEL_SECTIONS_UPDATE_QUOTA_COST`
   - supported part names
   - input schema
   - description
   - usage notes
   - caveats
   - caller examples
3. Add `build_channel_sections_update_contract()`.
4. Add validation for required `part`, supported parts, required `body`, required `body.id`, required `body.snippet.type`, section-type-specific content details, duplicate references, required title cases, OAuth preflight, partner-context usage, overwrite-sensitive update guidance, and unsupported fields.
5. Add a handler that calls the existing Layer 1 `build_channel_sections_update_wrapper()`.
6. Add result mapping that preserves returned resource fields, requested parts, endpoint identity, quota cost, `updated`, and safe partner context when present.
7. Add `build_channel_sections_update_tool_descriptor()`.
8. Export new symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
9. Register the descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
10. Add or update representative catalog examples in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/examples.py` if the YT-201/YT-202 catalog alignment checks require `channelSections_update` coverage.

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
- Keep the implementation scoped to `channelSections_update`; do not add section sorting, patch semantics, multi-section replacement, playlist creation, video metadata expansion, analytics, layout recommendations, channel branding, bulk editing, or enrichment.
- Confirm public metadata, examples, errors, and logs do not expose credentials, OAuth tokens, stack traces, private channel data, CMS account details, owner identifiers, or secret values.
- Confirm overwrite-sensitive update behavior is visible before invocation.
- Confirm all new or changed Python functions have reStructuredText docstrings.

Final validation:

```bash
cd /Users/ctgunn/Projects/youtube-mcp-server
python3 -m pytest
python3 -m ruff check .
```

## Implementation Evidence

Record focused command output, full-suite output, lint output, docstring review notes, and safety review notes here during implementation.

- 2026-06-12: Focused channel-sections/update, catalog, registry, and routing checks passed:
  `python3 -m pytest tests/unit/test_youtube_common_scaffolding.py tests/unit/test_youtube_channel_sections.py tests/contract/test_youtube_channel_sections_contract.py tests/integration/test_youtube_channel_sections_registration.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/unit/test_method_routing.py` -> 183 passed.
- 2026-06-12: Quickstart focused metadata/registration command passed:
  `python3 -m pytest tests/unit/test_youtube_channel_sections.py tests/contract/test_youtube_channel_sections_contract.py tests/integration/test_youtube_channel_sections_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` -> 189 passed.
- 2026-06-12: Dispatcher and MCP routing guard command passed:
  `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py` -> 46 passed.
- 2026-06-12: Layer 1 channel-sections guard command passed:
  `python3 -m pytest tests/contract/test_layer1_channel_sections_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py` -> 665 passed.
- 2026-06-12: Safety review found credential-like strings only in deliberate safe-error test fixtures and non-secret placeholder examples; public update metadata/results/errors do not expose OAuth tokens, CMS account details, owner identifiers, stack traces, or private channel data.
- 2026-06-12: Docstring review confirmed new and modified Python functions in `channel_sections.py`, `examples.py`, `__init__.py`, `dispatcher.py`, and the Layer 1 validator have reStructuredText-style docstrings where functions are introduced or behavior is changed.
- 2026-06-12: Full repository test suite passed: `python3 -m pytest` -> 1976 passed.
- 2026-06-12: Lint passed: `python3 -m ruff check .` -> All checks passed.

## Rollback

To rollback this slice, remove:

- `channelSections_update` dispatcher registration.
- `channelSections_update` Layer 2 module exports and endpoint-specific helpers from `channel_sections.py`.
- Endpoint-specific tests and examples.

Rollback must preserve YT-114 Layer 1 `channelSections.update`, YT-201/YT-202 shared contracts, `channelSections_list`, `channelSections_insert`, `channels_list`, `channels_update`, and existing activities/captions/channel banner tool behavior.
