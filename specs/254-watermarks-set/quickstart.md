# Quickstart: Layer 2 Tool `watermarks_set`

## Goal

Verify that YT-254 exposes the low-level `watermarks_set` tool as an OAuth-required, endpoint-backed Layer 2 upload mutation tool for setting one target YouTube channel watermark.

## Prerequisites

- Work on branch `254-watermarks-set`.
- Keep the YT-254 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use fake wrapper payloads and test-safe channel identifiers; do not use real credentials, private channel data, tokens, authorization headers, raw upstream diagnostics, live YouTube calls, real uploaded media, or real watermark targets in tests or examples.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `watermarks_set`
   - upstream identity `watermarks.set`
   - quota cost `50` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - required `channelId`
   - required `body` with timing and position metadata
   - required `media` with MIME type and content
   - accepted media types and 10 MB upload boundary
   - rejected `onBehalfOfContentOwner` in this slice
   - sparse watermark-update acknowledgment success result
   - no removal, lookup, update, banner, thumbnail, video, analytics, recommendation, ranking, summarization, enrichment, automated branding, or cross-endpoint aggregation
2. Add failing unit tests for:
   - non-object arguments
   - missing `channelId`
   - empty or non-string `channelId`
   - ambiguous multi-target `channelId` where locally detectable
   - missing or non-object `body`
   - missing or empty `body.timing`
   - missing or empty `body.position`
   - invalid `body.targetChannelId`
   - missing or non-object `media`
   - missing or unsupported `media.mimeType`
   - missing, empty, or oversized `media.content`
   - metadata-only and media-only requests
   - unsupported top-level fields
   - rejected `onBehalfOfContentOwner`
   - missing OAuth
   - safe sparse acknowledgment mapping
   - quota, authorization, forbidden, not-found, unsupported upload, unavailable endpoint, deprecated endpoint, upstream refusal, conflict, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of valid authorized watermark update
   - dispatcher preservation of target, metadata, upload, and quota context
   - dispatcher rejection of missing channel, body, media, partner delegation, and unsupported fields
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Add `src/mcp_server/tools/youtube_common/watermarks.py`.
2. Define the smallest `watermarks_set` constants, schema, contract builder, descriptor builder, examples, validator, handler, acknowledgment result mapper, OAuth-context selector, default executor, and error mapper needed to pass focused tests.
3. Import and use `build_watermarks_set_wrapper()` from the existing Layer 1 watermarks resource module.
4. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
5. Register the descriptor in the default tool catalog.
6. Add or update the representative shared catalog/example entry if needed so discovery describes the concrete endpoint-backed tool.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, target `channelId`, required `body`, required `media`, media MIME types, 10 MB upload limit, sparse acknowledgment, partner-delegation boundary, and unsupported-workflow guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw request context, authorization headers, secret-bearing fields, raw media content, or private authorization details.
4. Keep watermark removal, channel lookup/update, banner upload, thumbnail upload, video management, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, automated branding, and higher-level workflow behavior out of the watermark-set path.

## Focused Verification

```bash
pytest tests/contract/test_youtube_watermarks_contract.py tests/unit/test_youtube_watermarks.py tests/integration/test_youtube_watermarks_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If implementation touches the Layer 1 watermarks wrapper, also run:

```bash
pytest tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py
```

## Final Verification

```bash
pytest
ruff check .
```

## Implementation Notes

- `watermarks_set` remains a low-level watermark upload tool and does not provide watermark removal, channel lookup/update, banner upload, thumbnail upload, video workflows, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, automated branding, or cross-endpoint aggregation.
- Local dispatcher validation may reject requests that miss required `channelId`, `body`, or `media` before the concrete handler runs; concrete handler validation still produces the shared safe category when invoked directly.
- Every supported request requires OAuth-backed access.
- The supported request requires exactly one target channel `channelId`, one watermark metadata `body`, and one media upload `media`.
- `body.timing` and `body.position` are required.
- `media.mimeType` and `media.content` are required.
- The supported media boundary follows Layer 1: `image/jpeg`, `image/png`, `application/octet-stream`, and the 10 MB upload maximum.
- `onBehalfOfContentOwner` is rejected or left unexposed in this slice because the existing Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Successful watermark-set behavior is represented by a structured sparse acknowledgment, not by refreshed channel branding metadata, media hosting URLs, watermark lookup state, analytics result, or automated branding workflow.
- Safe result summaries may mention target channel identity, quota cost, access mode, watermark metadata presence, upload MIME type, and acknowledgment outcome, but must not expose credentials, authorization headers, raw media content, raw upstream diagnostics, secret-bearing context, or private authorization details.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw request/body diagnostics, raw media content, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-254`
- Red checkpoint: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/integration/test_youtube_watermarks_registration.py tests/contract/test_youtube_watermarks_contract.py tests/unit/test_youtube_watermarks.py` failed during collection with `ModuleNotFoundError: No module named 'mcp_server.tools.youtube_common.watermarks'` before implementation.
- Red checkpoint showing focused tests fail because the concrete Layer 2 `watermarks_set` surface is absent or incomplete before implementation
- Green checkpoint: `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_watermarks_contract.py tests/unit/test_youtube_watermarks.py tests/integration/test_youtube_watermarks_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` passed with 358 tests.
- focused green checkpoint for `watermarks_set` contract, unit, registration, and catalog tests
- code-quality checkpoint from `python3 -m ruff check .`: all checks passed
- full-suite checkpoint from `PYTHONPATH=src python3 -m pytest`: 4118 tests passed
- confirmation that every new or changed Python function has a reStructuredText docstring: AST docstring scan passed for `src/mcp_server/tools/youtube_common/watermarks.py`, `tests/unit/test_youtube_watermarks.py`, `tests/contract/test_youtube_watermarks_contract.py`, and `tests/integration/test_youtube_watermarks_registration.py`
- confirmation that quota cost, OAuth access, required `channelId`, required `body`, required `media`, supported upload boundary, sparse acknowledgment behavior, rejected partner delegation, safe error categories, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors
