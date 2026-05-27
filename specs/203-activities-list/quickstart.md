# Quickstart: YT-203 Layer 2 Tool `activities_list`

## Goal

Verify that the planned `activities_list` Layer 2 tool is discoverable, quota/auth-visible, selector-safe, endpoint-backed, and still aligned with the existing Layer 1 `activities.list` wrapper and shared Layer 2 contracts.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`
- Use branch `203-activities-list`
- Review:
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/spec.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/203-activities-list/contracts/activities-list-tool-contract.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/103-activities-list/`

## Red Phase

1. Add focused failing tests that prove `activities_list` is not yet discoverable as a public executable Layer 2 tool.
2. Add failing metadata checks requiring:
   - public name `activities_list`
   - upstream identity `activities.list`
   - quota cost `1`
   - mixed/conditional auth
   - selector and deprecation caveats
   - usage notes with `Quota cost: 1`
3. Add failing request validation checks for:
   - missing `part`
   - missing selector
   - multiple selectors
   - unsupported fields
   - `mine` or `home` without eligible authorization
4. Add failing result checks for:
   - returned activity items
   - successful empty item collections
   - requested parts
   - next and previous page tokens
   - safe error categories

Suggested focused command while tests are red:

```bash
python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Green Phase

1. Add the minimum `activities_list` public tool definition, input schema, metadata, usage notes, and handler adapter.
2. Register the tool through the existing dispatcher-compatible path.
3. Use the existing Layer 1 `activities.list` wrapper for endpoint behavior.
4. Preserve near-raw list results with items, requested parts, and pagination fields.
5. Map invalid requests and upstream failures to shared safe error categories.
6. Add reStructuredText docstrings to every new or changed Python function.

Run focused checks:

```bash
python3 -m pytest tests/unit/test_youtube_activities.py tests/contract/test_youtube_activities_contract.py tests/integration/test_youtube_activities_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If Layer 1 wrapper code changes, also run:

```bash
python3 -m pytest tests/contract/test_layer1_activities_contract.py tests/unit/test_layer1_foundation.py
```

If dispatcher discovery or MCP routing changes, also run:

```bash
python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py
```

## Refactor Phase

1. Remove duplication with YT-201/YT-202 shared contracts and helpers.
2. Keep endpoint-specific behavior limited to `activities_list`.
3. Confirm public examples, metadata, errors, and logs contain no credentials, tokens, stack traces, signed URLs, secret values, or raw media payloads.
4. Confirm no Layer 3 behavior was introduced.
5. Re-run focused checks after cleanup.

Final required validation:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Manual Review Checklist

- `activities_list` appears in tool discovery or registration artifacts.
- Discovery metadata includes upstream identity `activities.list`.
- Description and examples include `Quota cost: 1`.
- Auth metadata says `mixed/conditional`.
- `channelId` is documented as public channel activity access.
- `mine` and `home` are documented as requiring eligible user authorization.
- `home` includes a deprecation caveat.
- Exactly-one selector validation is covered.
- Empty item collections are successful.
- Pagination tokens are preserved.
- Error details are safe for MCP clients.
- Every new or changed Python function has a reStructuredText docstring.
