# Quickstart: Layer 2 Tool `videos_insert`

## Goal

Verify that YT-248 exposes the low-level `videos_insert` tool as a media-upload-oriented, endpoint-backed Layer 2 creation tool for YouTube video resources.

## Prerequisites

- Work on branch `248-videos-insert`.
- Keep the YT-248 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use test-safe media descriptors and fake wrapper payloads; do not use real credentials, signed URLs, private channel data, or raw video payloads in tests or examples.

## Red Phase

Red evidence: shared and story-level YT-248 tests were added for exports, contract metadata, representative catalog presence, default registry discovery, request validation, safe result mapping, OAuth preflight, safe error mapping, and dispatcher behavior before implementation. The focused Red run failed with 50 `videos_insert` failures before implementation symbols and registration existed.

1. Add focused failing contract tests for:
   - public tool name `videos_insert`
   - upstream identity `videos.insert`
   - quota cost `1600` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - media-constrained or limited availability state
   - required `part`
   - required `body`
   - required `media`
   - supported `uploadMode` values
   - optional `notifySubscribers`
   - optional `onBehalfOfContentOwner` delegation guidance
   - created-video upload result shape
   - safe media summary behavior
   - no automatic publishing, update, delete, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation
2. Add failing unit tests for:
   - missing `part`
   - empty or non-string `part`
   - missing `body`
   - incomplete or unsupported `body`
   - missing `media`
   - incomplete or unsupported `media`
   - metadata-only request rejection
   - media-only request rejection
   - unsupported `uploadMode`
   - invalid `notifySubscribers`
   - invalid delegation context
   - missing OAuth
   - unsupported publishing, editing, rating, thumbnail, caption, playlist, comment, transcript, analytics, recommendation, ranking, summarization, or enrichment fields
   - safe upload-result mapping
   - quota, policy, unavailable endpoint, deprecated endpoint, upstream invalid request, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of a valid authorized video creation request
   - dispatcher rejection of missing media
   - dispatcher rejection of missing body
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Extend `src/mcp_server/tools/youtube_common/videos.py`.
2. Define the smallest `videos_insert` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, OAuth-context selector, upload helper, media summary helper, and error mapper needed to pass focused tests.
3. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
4. Register the descriptor in the default tool catalog.
5. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
6. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, media-upload, upload-mode, delegation, availability, and created-resource guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw media payloads, signed URLs, or secret-bearing fields.
4. Keep search, captions, video categories, thumbnails, playlists, comments, rating mutation, analytics, recommendation, and higher-level video workflow behavior out of the videos insert path.

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

- `videos_insert` remains an upload-oriented video-resource creation tool and does not provide automatic publishing, update, delete, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or classification behavior.
- Local dispatcher validation may reject requests that miss required `part`, `body`, or `media` before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Every supported request requires OAuth-backed access.
- `uploadMode` is limited to supported modes such as `multipart` and `resumable`.
- Safe media summaries may mention descriptor shape and media type, but must not expose raw media payloads, signed URLs, or secret-bearing references.
- Availability caveats for audit, private-default behavior, release constraints, and policy refusals must stay visible in metadata and safe failures.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw media, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-248`
- focused test output for `videos_insert`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, OAuth access, media-upload requirements, upload-mode behavior, delegation behavior, availability caveats, created-resource result shape, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors

## Completed Verification

- Red: `python3 -m pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` failed as expected with 50 `videos_insert` failures before implementation.
- Focused: `python3 -m pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_tool_catalog_contract.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/integration/test_youtube_tool_registration.py` passed with 369 tests.
- Layer 1 guard: `python3 -m pytest tests/contract/test_layer1_videos_contract.py tests/unit/test_layer1_foundation.py` passed with 434 tests.
- Docstrings: AST scan confirmed every function in changed Python files has a docstring.
- Lint: `ruff check .` was unavailable on PATH; `python3 -m ruff check .` passed.
- Full suite: `python3 -m pytest` passed with 3,640 tests.
