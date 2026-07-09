# Quickstart: YT-230 Layer 2 Tool `playlistImages_update`

## Scope Guard

- Implement only the public Layer 2 `playlistImages_update` tool.
- Reuse the existing Layer 1 `playlistImages.update` wrapper from YT-130.
- Keep supported inputs to required `part`, required target-identifying `body` metadata, and required `media` replacement upload content.
- Keep quota cost `50`, OAuth-required access, upload requirements, unsupported modifier rejection, mutation result behavior, and safe error mapping visible.
- Do not implement playlist image listing, insertion, deletion, thumbnail activation, playlist management, playlist-item expansion, analytics, ranking, summarization, enrichment, or cross-endpoint behavior.

## Red

1. Add failing contract tests for `playlistImages_update` discovery metadata, input schema, quota cost `50`, OAuth-required auth, required `part`, required target-identifying `body`, required `media`, caller examples, response boundary, mutation result convention, and safe error categories.
2. Add failing unit tests for missing `part`, invalid `part`, missing target identity, missing `body`, invalid `body`, missing `media`, unsupported `media`, unsupported fields, missing OAuth, upstream auth failure mapping, quota failure mapping, missing-resource mapping, media eligibility or invalid request mapping, endpoint unavailable mapping, and near-raw updated-resource preservation.
3. Add failing integration tests proving the default registry does not yet expose `playlistImages_update` and the dispatcher cannot yet invoke it successfully.
4. Confirm all new or changed Python functions planned for the slice will need reStructuredText docstrings before Green is complete.

## Green

1. Extend `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/playlist_images.py`.
2. Define `PLAYLIST_IMAGES_UPDATE_TOOL_NAME`, quota cost `50`, supported parts, input schema, usage notes, caveats, caller examples, safe error type or shared error handling, validators, result mapper, upstream error mapper, handler builder, and descriptor builder.
3. Reuse `build_playlist_images_update_wrapper()` and construct an OAuth-required auth context for playlist-image update.
4. Export new public symbols from `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.
5. Register `build_playlist_images_update_tool_descriptor()` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/dispatcher.py`.
6. Keep examples and default local executor data safe, deterministic, and free of real tokens, raw upload bytes, private playlist data, or sensitive details.

## Refactor

1. Align naming, error categories, response-boundary metadata, and usage-note style with `playlistImages_insert`, `channelSections_update`, `captions_update`, and neighboring Layer 2 mutation tools.
2. Remove duplicate wording that belongs in shared YT-201/YT-202 helpers while preserving endpoint-specific quota/auth/body/media/target-identity caveats.
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

- Matched seed slice: `YT-230`
- Dependency assumptions: `YT-130`, `YT-201`, `YT-202`
- Focused failing tests from Red phase
- Focused passing tests after Green/Refactor
- Full `pytest` result after final code changes
- `ruff check .` result after final code changes
- Notes for any official-documentation caveats discovered during implementation
