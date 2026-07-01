# Quickstart: YT-226 Layer 2 Tool `members_list`

## Prerequisites

- Work on branch `226-members-list`.
- Keep the feature scoped to `members_list`; do not implement `membershipsLevels_list`, subscriber lookup, member administration, delegated owner management, analytics, ranking, summarization, or enrichment.
- Use the existing Layer 1 `members.list` wrapper from YT-126.
- Preserve reStructuredText docstrings for every new or changed Python function.

## Red Phase

1. Add failing contract tests for public metadata, schema, examples, quota cost `2`, OAuth-required access, owner-only/channel-membership caveats, and safe metadata.
2. Add failing unit tests for valid `all_current`, valid `updates`, paged retrieval, empty success mapping, missing `part`, invalid `part`, missing `mode`, invalid `mode`, invalid `maxResults`, empty `pageToken`, unsupported fields, unsupported filters, and safe upstream error mapping.
3. Add failing integration tests proving `members_list` is not yet registered in the default dispatcher and cannot yet execute through the registry.
4. Add failing shared-export tests for `MEMBERS_LIST_*` symbols in `mcp_server.tools.youtube_common`.

## Green Phase

1. Add `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/members.py`.
2. Define `members_list` constants, input schema, examples, caveats, safe error type, validator, result mapper, upstream error mapper, contract builder, handler builder, and descriptor builder.
3. Reuse `build_members_list_wrapper()` and OAuth-required auth context for execution.
4. Export public symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
5. Register the descriptor in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
6. Update Layer 1 quota metadata from `1` to `2` only if focused tests prove the existing review surface would otherwise contradict the public official quota contract.

## Refactor Phase

1. Compare naming, metadata, examples, result shape, and safe error behavior with `comments_list`, `i18nRegions_list`, and `guideCategories_list`.
2. Remove duplicated helper logic that belongs in existing shared conventions without broadening the public tool scope.
3. Confirm new or changed functions have reStructuredText docstrings covering purpose, inputs, outputs, raised errors, and side effects where relevant.
4. Keep unsupported official filters, delegation fields, subscriber lookup, membership-level lookup, and analytics out of scope unless a later Layer 1 contract revision explicitly adds them.

## Focused Verification

```bash
pytest tests/contract/test_youtube_members_contract.py tests/unit/test_youtube_members.py tests/integration/test_youtube_members_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Expected Review Evidence

- Matched seed slice `YT-226`
- Current official quota check for `members.list` showing quota cost `2`
- Focused `members_list` test output
- Full-suite `pytest` output after final changes
- `ruff check .` output
- Notes explaining that `hasAccessToLevel` and `filterByMemberChannelId` remain unsupported until the Layer 1 contract exposes them

## Implementation Notes

- The public `members_list` metadata, examples, handler results, and touched Layer 1 review surface align to quota cost `2`.
- The earlier seed and YT-126 artifacts used quota cost `1`; this feature records the discrepancy and treats the current official quota cost as authoritative for public discovery.
- `hasAccessToLevel`, `filterByMemberChannelId`, delegation fields, subscriber lookup, analytics, ranking, summarization, and enrichment are rejected as unsupported request fields in this slice.
- Local smoke verification compiled the new members module and exercised descriptor discovery, dispatcher execution, validation failures, safe upstream error mapping, and Layer 1 quota propagation.
