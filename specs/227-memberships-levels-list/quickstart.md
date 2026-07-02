# Quickstart: YT-227 Layer 2 Tool `membershipsLevels_list`

## Scope Guard

- Implement only the public Layer 2 `membershipsLevels_list` tool.
- Reuse the existing Layer 1 `membershipsLevels.list` wrapper from YT-127.
- Keep supported inputs to `part=snippet`.
- Keep quota cost `1`, OAuth-required owner access, owner-only visibility, channel-membership constraints, unsupported modifier rejection, and empty-result success behavior visible.
- Do not implement channel member listing, subscriber lookup, membership administration, delegated owner management, analytics, ranking, summarization, enrichment, or cross-endpoint behavior.

## Red

1. Add failing contract tests for `membershipsLevels_list` discovery metadata, input schema, quota cost `1`, OAuth-required auth, owner-only/channel-membership caveats, examples, response boundary, and safe error categories.
2. Add failing unit tests for missing `part`, invalid `part`, unsupported fields, unsupported paging/filter/delegation inputs, missing OAuth, upstream auth failure mapping, quota failure mapping, endpoint unavailable mapping, empty successful results, and near-raw result preservation.
3. Add failing integration tests proving the default registry does not yet expose `membershipsLevels_list` and the dispatcher cannot yet invoke it successfully.
4. Confirm all new or changed Python functions planned for the slice will need reStructuredText docstrings before Green is complete.

## Green

1. Add `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/memberships_levels.py`.
2. Define `MEMBERSHIPS_LEVELS_LIST_TOOL_NAME`, quota cost `1`, supported parts, input schema, usage notes, caveats, caller examples, safe error type, validators, result mapper, upstream error mapper, handler builder, and descriptor builder.
3. Reuse `build_memberships_levels_list_wrapper()` and construct an OAuth-required auth context for owner-scoped execution.
4. Export new public symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
5. Register `build_memberships_levels_list_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
6. Keep examples and default local executor data safe, deterministic, and free of real tokens or sensitive details.

## Refactor

1. Align naming, error categories, response-boundary metadata, and usage-note style with `members_list` and neighboring Layer 2 list tools.
2. Remove duplicate wording that belongs in shared YT-201/YT-202 helpers while preserving endpoint-specific quota/auth/access caveats.
3. Verify every new or changed Python function has a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
4. Keep Layer 1 changes out of scope unless focused tests reveal a missing export or metadata gap.

## Focused Verification

```bash
pytest tests/contract/test_youtube_memberships_levels_contract.py tests/unit/test_youtube_memberships_levels.py tests/integration/test_youtube_memberships_levels_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Full Verification

```bash
pytest
ruff check .
```

## Review Evidence

- Matched seed slice: `YT-227`
- Dependency assumptions: `YT-127`, `YT-201`, `YT-202`
- Focused failing tests from Red phase
- Focused passing tests after Green/Refactor
- Full `pytest` result after final code changes
- `ruff check .` result after final code changes
- Notes for any official-documentation caveats discovered during implementation
