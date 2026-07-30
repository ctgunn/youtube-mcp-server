# Quickstart: YT-302 Video Details

## Goal

Use this guide to verify that planning is complete before generating implementation tasks for `videos_getVideo`.

## Review the Plan Artifacts

```bash
sed -n '1,280p' /Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/spec.md
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/plan.md
sed -n '1,280p' /Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/research.md
sed -n '1,320p' /Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/data-model.md
sed -n '1,360p' /Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/contracts/videos-get-video-contract.md
```

## Confirm the Contract Before Tasking

- `videos_getVideo` requires one nonblank `videoId` and permits only optional `parts`.
- The only allowed part values are `snippet`, `contentDetails`, `statistics`, `status`, and `topicDetails`.
- The default response includes all available core fields; optional groups are additive.
- The tool maps an empty lookup to `unavailable_resource` without exposing the underlying cause.
- The result is one normalized video, not a lower-level collection envelope.
- The feature introduces no persistence, new source integration, fan-out, ranking, or enrichment.
- New paths, symbols, and test names follow the established composed-family convention.

## Expected Red-Green-Refactor Flow

1. **Red**: Add failing unit, contract, and integration tests for core retrieval, requested part groups, validation, unavailable lookup, safe error translation, discovery, and default registration.
2. **Green**: Add only the descriptor, validation, one-lookup adapter, normalization, safe error mapping, exports, and registration needed for those tests.
3. **Refactor**: Consolidate repeated mapping and sanitization logic, retain reStructuredText docstrings on all changed Python functions, then rerun focused and full checks.

## Planned Verification Commands

Run focused checks during implementation:

```bash
PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_composed_videos.py tests/contract/test_youtube_composed_videos_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py
```

Run these after the final code change:

```bash
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src python3 -m ruff check .
```

## Review Evidence

Pull-request review should include:

- The matched seed slice, `YT-302`.
- Failing-test evidence before implementation and passing focused-test evidence after it.
- Discovery output proving the concrete `videos_getVideo` descriptor is registered without a representative-only marker.
- Result evidence for default fields, every optional part mapping, sparse source fields, unavailable video behavior, and safe error categories.
- Confirmation that the implementation performs one lower-level lookup per invocation.
- Passing full-suite and lint output.
- Confirmation that all new or changed Python functions have reStructuredText docstrings.
