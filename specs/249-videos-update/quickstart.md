# Quickstart: Layer 2 Tool `videos_update`

## Goal

Verify that YT-249 exposes the low-level `videos_update` tool as an OAuth-required, endpoint-backed Layer 2 mutation tool for YouTube video resources.

## Prerequisites

- Work on branch `249-videos-update`.
- Keep the YT-249 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use fake wrapper payloads and test-safe video identifiers; do not use real credentials, private channel data, tokens, authorization headers, or raw upstream diagnostics in tests or examples.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `videos_update`
   - upstream identity `videos.update`
   - quota cost `50` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - required `part`
   - required `body`
   - supported writable part `snippet`
   - required `body.id`
   - required `body.snippet.title`
   - optional `onBehalfOfContentOwner` delegation guidance
   - updated-video mutation result shape
   - replacement-oriented update-semantics caveat
   - no media upload, media replacement, automatic publishing, create, delete, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation
2. Add failing unit tests for:
   - missing `part`
   - empty or non-string `part`
   - unsupported or read-only `part`
   - missing `body`
   - missing or blank `body.id`
   - missing `body.snippet`
   - missing or blank `body.snippet.title`
   - unsupported body fields
   - unsupported snippet fields
   - invalid delegation context
   - missing OAuth
   - unsupported upload, publishing, create, delete, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, or enrichment fields
   - safe updated-resource result mapping
   - quota, policy, not-found, unavailable endpoint, deprecated endpoint, upstream invalid request, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of a valid authorized video update request
   - dispatcher rejection of missing identity
   - dispatcher rejection of missing writable part
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Extend `src/mcp_server/tools/youtube_common/videos.py`.
2. Define the smallest `videos_update` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, OAuth-context selector, update-body helper, writable-part helper, safe delegation helper, and error mapper needed to pass focused tests.
3. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Register the descriptor in the default tool catalog.
5. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
6. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, writable-part, update-body, replacement-semantics, delegation, and updated-resource guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw request context, authorization headers, or secret-bearing fields.
4. Keep search, captions, video categories, thumbnails, playlists, comments, rating mutation, analytics, recommendation, and higher-level video workflow behavior out of the videos update path.

## Focused Verification

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If implementation touches the Layer 1 videos wrapper, also run:

```bash
pytest tests/contract/test_layer1_videos_contract.py tests/unit/test_layer1_foundation.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `videos_update` remains a low-level video-resource update tool and does not provide media upload, media replacement, transcoding, automatic publishing, create, delete, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or classification behavior.
- Local dispatcher validation may reject requests that miss required `part` or `body` before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Every supported request requires OAuth-backed access.
- The current supported update path is `part=snippet` with `body.id` and `body.snippet.title`.
- Replacement-oriented update semantics for included parts must remain visible in metadata, examples, and caveats.
- Safe result summaries may mention target video identity, requested parts, accepted update fields, and mutation outcome, but must not expose credentials, authorization headers, raw upstream diagnostics, or secret-bearing context.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-249`
- focused test output for `videos_update`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, OAuth access, writable-part requirements, update-body requirements, replacement-semantics caveats, delegation behavior, updated-resource result shape, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors

## Completed Verification Evidence

- Initial Red command using `pytest ...` failed locally because `pytest` was not on PATH; `python3 -m pytest ...` is the available local test runner.
- Focused YT-249 verification passed with `python3 -m pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`: 440 passed.
- Code-quality verification passed with `python3 -m ruff check .`: all checks passed.
- Full repository verification passed with `python3 -m pytest`: 3711 passed.
- Layer 1 guard verification was reviewed and not run separately because no Layer 1 source files changed for YT-249.
- Changed Python functions and test helper methods were reviewed for reStructuredText docstrings.
- `git status --short` contains the intended YT-249 source, test, and spec artifacts plus a pre-existing unrelated `AGENTS.md` modification that was left untouched.
