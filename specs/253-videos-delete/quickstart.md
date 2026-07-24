# Quickstart: Layer 2 Tool `videos_delete`

## Goal

Verify that YT-253 exposes the low-level `videos_delete` tool as an OAuth-required, endpoint-backed Layer 2 mutation tool for deleting one target YouTube video.

## Prerequisites

- Work on branch `253-videos-delete`.
- Keep the YT-253 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use fake wrapper payloads and test-safe video identifiers; do not use real credentials, private channel data, tokens, authorization headers, raw upstream diagnostics, live YouTube calls, or real deletion targets in tests or examples.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `videos_delete`
   - upstream identity `videos.delete`
   - quota cost `50` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - required `id`
   - no request body
   - rejected `onBehalfOfContentOwner` in this slice
   - no-content deletion acknowledgment success result
   - destructive-action guidance
   - no listing, lookup, update, upload, rating, abuse reporting, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, recovery, policy review, or cross-endpoint aggregation
2. Add failing unit tests for:
   - non-object arguments
   - missing `id`
   - empty or non-string `id`
   - ambiguous multi-target `id` where locally detectable
   - supplied `body`
   - unsupported top-level fields
   - rejected `onBehalfOfContentOwner`
   - missing OAuth
   - safe no-content acknowledgment mapping
   - quota, authorization, forbidden, not-found, unavailable endpoint, deprecated endpoint, upstream refusal, conflict, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of valid authorized deletion
   - dispatcher preservation of target context
   - dispatcher rejection of missing target, body, partner delegation, and unsupported fields
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Extend `src/mcp_server/tools/youtube_common/videos.py`.
2. Define the smallest `videos_delete` constants, schema, contract builder, descriptor builder, examples, validator, handler, acknowledgment result mapper, OAuth-context selector, default executor, and error mapper needed to pass focused tests.
3. Import and use `build_videos_delete_wrapper()` from the existing Layer 1 videos resource module.
4. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
5. Register the descriptor in the default tool catalog.
6. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, target `id`, no-body rule, no-content acknowledgment, destructive-action semantics, partner-delegation boundary, and unsupported-workflow guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw request context, authorization headers, secret-bearing fields, or private authorization details.
4. Keep listing, metadata lookup/update, upload, rating lookup/mutation, abuse reporting, thumbnails, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, recovery, and higher-level video workflow behavior out of the videos delete path.

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

- `videos_delete` remains a low-level deletion tool and does not provide listing, metadata lookup/update, upload, rating lookup/mutation, abuse reporting, thumbnails, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, recovery, or policy enforcement behavior.
- Local dispatcher validation may reject requests that miss required `id` before the concrete handler runs; concrete handler validation still produces the shared `invalid_request` category when invoked directly.
- Every supported request requires OAuth-backed access.
- The supported request requires exactly one target video `id`.
- No request body is supported in this slice.
- `onBehalfOfContentOwner` is rejected or left unexposed in this slice because the existing Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Successful delete behavior is represented by a structured no-content acknowledgment, not by a refreshed video resource, recovery state, analytics result, abuse-report outcome, or content-management workflow.
- Safe result summaries may mention target video identity, quota cost, access mode, destructive-action context, and acknowledgment outcome, but must not expose credentials, authorization headers, raw upstream diagnostics, secret-bearing context, or private authorization details.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw request/body diagnostics, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-253`
- Red checkpoint: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py` stopped during collection with `ImportError: cannot import name 'VIDEOS_DELETE_CALLER_EXAMPLES' from 'mcp_server.tools.youtube_common.videos'`, confirming the missing Layer 2 `videos_delete` surface before implementation.
- Focused green checkpoint: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/integration/test_youtube_videos_registration.py tests/contract/test_youtube_videos_contract.py tests/unit/test_youtube_videos.py` completed with `753 passed in 2.86s` after implementation.
- Code-quality checkpoint: `ruff check .` was not on PATH, so `PYTHONPATH=src python3 -m ruff check .` was used and completed with `All checks passed!`.
- Full-suite checkpoint: `PYTHONPATH=src python3 -m pytest` completed with `4024 passed in 16.33s`.
- focused test output for `videos_delete`
- full repository `pytest` output after final code changes
- `ruff check .` output
- confirmation that every new or changed Python function has a reStructuredText docstring
- confirmation that quota cost, OAuth access, target-only request boundary, no-body behavior, no-content acknowledgment behavior, rejected partner delegation, destructive-action guidance, safe error categories, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors
