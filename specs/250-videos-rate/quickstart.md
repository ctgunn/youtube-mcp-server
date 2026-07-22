# Quickstart: Layer 2 Tool `videos_rate`

## Goal

Verify that YT-250 exposes the low-level `videos_rate` tool as an OAuth-required, endpoint-backed Layer 2 mutation tool for applying, changing, or clearing the authenticated caller's YouTube video rating.

## Prerequisites

- Work on branch `250-videos-rate`.
- Keep the YT-250 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use fake wrapper payloads and test-safe video identifiers; do not use real credentials, private channel data, tokens, authorization headers, raw upstream diagnostics, or live rating mutations in tests or examples.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `videos_rate`
   - upstream identity `videos.rate`
   - quota cost `50` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - required `id`
   - required `rating`
   - supported rating actions `like`, `dislike`, and `none`
   - `none` as explicit clear-rating semantics
   - no request body
   - acknowledgment-style success result
   - no current-rating lookup, rating history, aggregate rating counts, metadata update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation
2. Add failing unit tests for:
   - missing `id`
   - empty or non-string `id`
   - missing `rating`
   - empty, non-string, differently cased, duplicated, conflicting, or unsupported `rating`
   - request body rejection
   - unsupported top-level fields
   - missing OAuth
   - safe rating acknowledgment mapping for `like`, `dislike`, and `none`
   - quota, invalid rating, unverified email, purchase-required, disabled rating, forbidden, not-found, unavailable endpoint, deprecated endpoint, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of valid authorized `like`, `dislike`, and `none` rating requests
   - dispatcher rejection of missing identity
   - dispatcher rejection of missing rating
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Extend `src/mcp_server/tools/youtube_common/videos.py`.
2. Define the smallest `videos_rate` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, OAuth-context selector, default no-content executor, and error mapper needed to pass focused tests.
3. Import and use `build_videos_rate_wrapper()` from the existing Layer 1 videos resource module.
4. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
5. Register the descriptor in the default tool catalog.
6. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, rating-state, clear-rating, no-body, and acknowledgment guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw request context, authorization headers, or secret-bearing fields.
4. Keep current-rating lookup, rating history, aggregate rating counts, metadata update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, and higher-level video workflow behavior out of the videos rating path.

## Focused Verification

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If implementation touches the Layer 1 videos wrapper, also run:

```bash
pytest tests/contract/test_layer1_videos_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `videos_rate` remains a low-level video-rating mutation tool and does not provide current-rating lookup, rating history, aggregate rating counts, metadata update, upload, deletion, abuse reporting, thumbnails, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, or classification behavior.
- Local dispatcher validation may reject requests that miss required `id` or `rating` before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Every supported request requires OAuth-backed access.
- Supported rating actions are `like`, `dislike`, and `none`.
- `none` clears the authenticated caller's prior rating and must not be confused with omitted `rating`.
- Successful rating behavior is represented by a structured mutation acknowledgment, including no-content success semantics, not by a refreshed video resource.
- Safe result summaries may mention target video identity, requested rating action, quota cost, access mode, and mutation outcome, but must not expose credentials, authorization headers, raw upstream diagnostics, or secret-bearing context.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

- 2026-07-22 Red check:
  `python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py`
  failed during collection because `mcp_server.tools.youtube_common.videos` did not yet export `VIDEOS_RATE_CALLER_EXAMPLES`.
- The bare `pytest` command was not on PATH in this shell; verification used `python3 -m pytest`, which reported `pytest 9.0.2`.
- 2026-07-22 Focused verification:
  `python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py`
  passed with 521 tests.
- 2026-07-22 Code quality:
  `python3 -m ruff check .` passed. The bare `ruff` command was not on PATH in this shell.
- 2026-07-22 Full repository verification:
  `python3 -m pytest` passed with 3792 tests.
- No Layer 1 files changed for YT-250, so the optional Layer 1 guard verification was not required.

Pull request notes should include:

- matched seed slice `YT-250`
- focused test output for `videos_rate`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, OAuth access, rating-state values, clear-rating semantics, no-request-body behavior, acknowledgment result shape, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors
