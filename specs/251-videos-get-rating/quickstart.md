# Quickstart: Layer 2 Tool `videos_getRating`

## Goal

Verify that YT-251 exposes the low-level `videos_getRating` tool as an OAuth-required, endpoint-backed Layer 2 read tool for retrieving the authenticated caller's current rating state for one or more YouTube videos.

## Prerequisites

- Work on branch `251-videos-get-rating`.
- Keep the YT-251 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use fake wrapper payloads and test-safe video identifiers; do not use real credentials, private channel data, tokens, authorization headers, raw upstream diagnostics, or live YouTube calls in tests or examples.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `videos_getRating`
   - upstream identity `videos.getRating`
   - quota cost `1` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - required `id`
   - one-to-fifty comma-separated video identifier boundary
   - optional `onBehalfOfContentOwner` partner delegation caveat if exposed
   - returned rating values `like`, `dislike`, `none`, and `unspecified`
   - `none` and `unspecified` as successful lookup states
   - no request body
   - per-video rating lookup success result
   - no rating mutation, rating history, aggregate rating counts, metadata lookup/update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or cross-endpoint aggregation
2. Add failing unit tests for:
   - missing `id`
   - empty or non-string `id`
   - duplicate identifiers
   - more than fifty identifiers
   - malformed comma-delimited identifiers
   - request body rejection
   - unsupported top-level fields
   - invalid `onBehalfOfContentOwner` values if exposed
   - missing OAuth
   - safe per-video lookup result mapping for `like`, `dislike`, `none`, and `unspecified`
   - quota, authorization, forbidden, not-found, unavailable endpoint, deprecated endpoint, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of valid authorized single-video lookup
   - dispatcher invocation of valid authorized multi-video lookup
   - dispatcher preservation of successful unrated or unspecified outcomes
   - dispatcher rejection of missing identity
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Extend `src/mcp_server/tools/youtube_common/videos.py`.
2. Define the smallest `videos_getRating` constants, schema, contract builder, descriptor builder, examples, validator, handler, result mapper, OAuth-context selector, default executor, and error mapper needed to pass focused tests.
3. Import and use `build_videos_get_rating_wrapper()` from the existing Layer 1 videos resource module.
4. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
5. Register the descriptor in the default tool catalog.
6. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, identifier, returned rating-state, delegation, no-body, and per-video lookup guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw request context, authorization headers, or secret-bearing fields.
4. Keep rating mutation, rating history, aggregate rating counts, metadata lookup/update, upload, deletion, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, and higher-level video workflow behavior out of the videos rating lookup path.

## Focused Verification

```bash
pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If implementation touches the Layer 1 videos wrapper, also run:

```bash
pytest tests/contract/test_layer1_videos_contract.py tests/contract/test_layer1_metadata_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `videos_getRating` remains a low-level viewer-rating lookup tool and does not provide rating mutation, rating history, aggregate rating counts, metadata lookup/update, upload, deletion, abuse reporting, thumbnails, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, or classification behavior.
- Local dispatcher validation may reject requests that miss required `id` before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Every supported request requires OAuth-backed access.
- The supported `id` shape is one to fifty unique comma-separated YouTube video identifiers.
- `onBehalfOfContentOwner`, if supported publicly, is partner-only OAuth delegation context and must not imply public or API-key access.
- Returned ratings include `like`, `dislike`, `none`, and `unspecified`.
- `none` and `unspecified` are successful lookup outcomes and must not be confused with validation, missing-resource, or access failures.
- Successful lookup behavior is represented by structured per-video rating outcomes, not by a refreshed video resource or mutation acknowledgment.
- Safe result summaries may mention requested video identities, returned ratings, quota cost, access mode, and lookup outcome, but must not expose credentials, authorization headers, raw upstream diagnostics, or secret-bearing context.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

- 2026-07-23 Red check:
  `python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py`
  failed during collection because `mcp_server.tools.youtube_common.videos` did not yet export `VIDEOS_GET_RATING_CALLER_EXAMPLES`.
- 2026-07-23 Focused Green check:
  `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py`
  passed with 591 tests after adding the Layer 2 `videos_getRating` descriptor, validation, execution, result mapping, exports, catalog entry, safe errors, metadata, and examples.
- 2026-07-23 Focused verification command from this quickstart:
  `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py`
  passed with 591 tests.
- 2026-07-23 Code quality:
  `ruff check .` was not available on PATH in this shell; `PYTHONPATH=src python3 -m ruff check .` passed.
- 2026-07-23 Full repository verification:
  `PYTHONPATH=src python3 -m pytest` passed with 3862 tests.
- 2026-07-23 Docstring review:
  AST review confirmed all functions/classes in `src/mcp_server/tools/youtube_common/videos.py` and `tests/unit/test_youtube_videos.py` have docstrings after the YT-251 changes.

Pull request notes should include:

- matched seed slice `YT-251`
- focused test output for `videos_getRating`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, OAuth access, identifier boundaries, optional partner delegation caveat, returned rating states, no-request-body behavior, per-video result shape, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors
