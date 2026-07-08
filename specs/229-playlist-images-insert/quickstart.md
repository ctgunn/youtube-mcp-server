# Quickstart: YT-229 Layer 2 Tool `playlistImages_insert`

## Scope Guard

- Implement only the public Layer 2 `playlistImages_insert` tool.
- Reuse the existing Layer 1 `playlistImages.insert` wrapper from YT-129.
- Keep supported inputs to required `part`, required `body` metadata, and required `media` upload content.
- Keep quota cost `50`, OAuth-required access, upload requirements, unsupported modifier rejection, mutation result behavior, and safe error mapping visible.
- Do not implement playlist image listing, update, deletion, thumbnail activation, playlist management, playlist-item expansion, analytics, ranking, summarization, enrichment, or cross-endpoint behavior.

## Red

1. Add failing contract tests for `playlistImages_insert` discovery metadata, input schema, quota cost `50`, OAuth-required auth, required `part`, required `body`, required `media`, caller examples, response boundary, mutation result convention, and safe error categories.
2. Add failing unit tests for missing `part`, invalid `part`, missing `body`, invalid `body`, missing `media`, unsupported `media`, unsupported fields, missing OAuth, upstream auth failure mapping, quota failure mapping, media eligibility or invalid request mapping, endpoint unavailable mapping, and near-raw created-resource preservation.
3. Add failing integration tests proving the default registry does not yet expose `playlistImages_insert` and the dispatcher cannot yet invoke it successfully.
4. Confirm all new or changed Python functions planned for the slice will need reStructuredText docstrings before Green is complete.

## Green

1. Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`.
2. Define `PLAYLIST_IMAGES_INSERT_TOOL_NAME`, quota cost `50`, supported parts, input schema, usage notes, caveats, caller examples, safe error type or shared error handling, validators, result mapper, upstream error mapper, handler builder, and descriptor builder.
3. Reuse `build_playlist_images_insert_wrapper()` and construct an OAuth-required auth context for playlist-image insertion.
4. Export new public symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
5. Register `build_playlist_images_insert_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
6. Keep examples and default local executor data safe, deterministic, and free of real tokens, raw upload bytes, private playlist data, or sensitive details.

## Refactor

1. Align naming, error categories, response-boundary metadata, and usage-note style with `playlistImages_list`, `channelBanners_insert`, `captions_insert`, and neighboring Layer 2 mutation tools.
2. Remove duplicate wording that belongs in shared YT-201/YT-202 helpers while preserving endpoint-specific quota/auth/body/media caveats.
3. Verify every new or changed Python function has a reStructuredText docstring documenting purpose, inputs, outputs, raised errors when relevant, and side effects when relevant.
4. Keep Layer 1 changes out of scope unless focused tests reveal a missing export or metadata gap.

## Focused Verification

```bash
python3 -m pytest tests/contract/test_youtube_playlist_images_contract.py tests/unit/test_youtube_playlist_images.py tests/integration/test_youtube_playlist_images_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Full Verification

```bash
python3 -m pytest
python3 -m ruff check .
```

## Review Evidence

- Matched seed slice: `YT-229`
- Dependency assumptions: `YT-129`, `YT-201`, `YT-202`
- Focused failing tests from Red phase
- Focused passing tests after Green/Refactor
- Full `pytest` result after final code changes
- `ruff check .` result after final code changes
- Notes for any official-documentation caveats discovered during implementation
