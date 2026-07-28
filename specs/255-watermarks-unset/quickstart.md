# Quickstart: Layer 2 Tool `watermarks_unset`

## Goal

Verify that YT-255 exposes the low-level `watermarks_unset` tool as an OAuth-required, endpoint-backed Layer 2 mutation tool for removing one target YouTube channel watermark.

## Prerequisites

- Work on branch `255-watermarks-unset`.
- Keep the YT-255 spec, plan, research, data model, and contract open for reference.
- Do not start implementation until Red tests exist for contract, validation, result, error, export, and registration behavior.
- Use fake wrapper payloads and test-safe channel identifiers; do not use real credentials, private channel data, tokens, authorization headers, raw upstream diagnostics, live YouTube calls, real uploaded media, or real watermark targets in tests or examples.

## Red Phase

1. Add focused failing contract tests for:
   - public tool name `watermarks_unset`
   - upstream identity `watermarks.unset`
   - quota cost `50` in metadata, description, usage notes, and examples
   - OAuth-required access mode
   - required `channelId`
   - no `body`, no `media`, and no media upload boundary
   - rejected `onBehalfOfContentOwner` in this slice
   - sparse watermark-removal acknowledgment success result
   - no-removal-possible behavior
   - no upload, lookup, update, banner, thumbnail, video, analytics, recommendation, ranking, summarization, enrichment, automated branding, or cross-endpoint aggregation
2. Add failing unit tests for:
   - non-object arguments
   - missing `channelId`
   - empty or non-string `channelId`
   - ambiguous multi-target `channelId` where locally detectable
   - supplied `body`
   - supplied `media`
   - metadata-only and media-only requests
   - unsupported top-level fields
   - rejected `onBehalfOfContentOwner`
   - missing OAuth
   - safe sparse acknowledgment mapping
   - no-removal-possible mapping
   - quota, authorization, forbidden, not-found, unavailable endpoint, deprecated endpoint, upstream refusal, conflict, and unexpected failure mapping
3. Add failing integration tests for:
   - default registry discovery
   - dispatcher invocation of valid authorized watermark removal
   - dispatcher preservation of target and quota context
   - dispatcher rejection of missing channel, body, media, partner delegation, and unsupported fields
   - dispatcher rejection or safe categorization of missing OAuth
   - safe error detail sanitization

## Green Phase

1. Extend `src/mcp_server/tools/youtube_common/watermarks.py`.
2. Define the smallest `watermarks_unset` constants, schema, contract builder, descriptor builder, examples, validator, handler, acknowledgment result mapper, OAuth-context selector, default executor, and error mapper needed to pass focused tests.
3. Import and use `build_watermarks_unset_wrapper()` from the existing Layer 1 watermarks resource module.
4. Export the new symbols from `src/mcp_server/tools/youtube_common/__init__.py`.
5. Register the descriptor in the default tool catalog.
6. Replace the representative shared catalog/example placeholder with the concrete `build_watermarks_unset_contract()` if the placeholder is still present.
7. Add or preserve reStructuredText docstrings for every new or changed Python function.

## Refactor Phase

1. Remove duplicated helper logic that belongs in shared Layer 2 contracts.
2. Keep quota, OAuth, target `channelId`, no-upload boundary, sparse acknowledgment, no-removal-possible behavior, partner-delegation boundary, and unsupported-workflow guidance visible but centralized enough to avoid drift across metadata, examples, and errors.
3. Confirm safe public metadata contains no API keys, OAuth tokens, stack traces, raw upstream diagnostics, raw request context, authorization headers, secret-bearing fields, raw media content, or private authorization details.
4. Keep watermark upload, placement updates, channel lookup/update, banner upload, thumbnail upload, video management, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, automated branding, and higher-level workflow behavior out of the watermark-unset path.

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

- `watermarks_unset` remains a low-level watermark removal tool and does not provide watermark upload, placement updates, channel lookup/update, banner upload, thumbnail upload, video workflows, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, enrichment, automated branding, or cross-endpoint aggregation.
- Local dispatcher validation may reject requests that miss required `channelId` before the concrete handler runs; concrete handler validation still produces the shared safe category when invoked directly.
- Every supported request requires OAuth-backed access.
- The supported request requires exactly one target channel `channelId`.
- `body`, `media`, watermark metadata, and media upload content are unsupported for this unset tool.
- `onBehalfOfContentOwner` is rejected or left unexposed in this slice because the existing Layer 1 wrapper leaves partner delegation outside the guaranteed boundary.
- Successful watermark-unset behavior is represented by a structured sparse acknowledgment, not by refreshed channel branding metadata, media hosting URLs, watermark lookup state, analytics result, or automated branding workflow.
- No-current-watermark, already-removed, not-found, or no-removal-possible outcomes must remain distinct from successful removal.
- Safe result summaries may mention target channel identity, quota cost, access mode, no-upload behavior, and acknowledgment outcome, but must not expose credentials, authorization headers, raw media content, raw upstream diagnostics, secret-bearing context, or private authorization details.
- Safe error detail sanitization strips API keys, OAuth tokens, authorization headers, raw request/body diagnostics, raw media content, stack traces, signed URLs, and secret-bearing fields before errors are exposed to callers.

## Review Evidence

Pull request notes should include:

- matched seed slice `YT-255`
- Red checkpoint showing focused tests fail because the concrete Layer 2 `watermarks_unset` surface is absent or incomplete before implementation
  - `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/integration/test_youtube_watermarks_registration.py tests/contract/test_youtube_watermarks_contract.py tests/unit/test_youtube_watermarks.py` collected 272 items, then failed during collection with missing `WatermarksUnsetToolError`, `WATERMARKS_UNSET_CALLER_EXAMPLES`, and `WATERMARKS_UNSET_INPUT_SCHEMA` imports.
- Green checkpoint showing focused `watermarks_unset` contract, unit, registration, and catalog tests pass
  - Bare `pytest ...` was not available on PATH in this shell (`/bin/bash: pytest: command not found`), so the equivalent `PYTHONPATH=src python3 -m pytest tests/contract/test_youtube_watermarks_contract.py tests/unit/test_youtube_watermarks.py tests/integration/test_youtube_watermarks_registration.py tests/contract/test_youtube_common_contract.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` was used and passed: 443 passed in 1.49s.
- code-quality checkpoint from `ruff check .`
  - Bare `ruff` was not available on PATH in this shell, so the equivalent `python3 -m ruff check .` was used and passed.
- full-suite checkpoint from `pytest`
  - The equivalent `PYTHONPATH=src python3 -m pytest` passed: 4203 passed in 17.01s.
- confirmation that every new or changed Python function has a reStructuredText docstring
  - Reviewed changed production and test helper functions with `rg`; every new or modified function/helper in the touched Python files has a reStructuredText-style docstring.
- confirmation that quota cost, OAuth access, required `channelId`, no-upload boundary, sparse acknowledgment behavior, no-removal-possible behavior, rejected partner delegation, safe error categories, and out-of-scope workflow boundaries are visible in metadata, caveats, examples, and safe errors
  - Confirmed by focused contract, catalog, registration, and unit coverage for YT-255.
