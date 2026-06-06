# Quickstart: YT-207 Layer 2 Tool `captions_download`

## Goal

Verify that the planned `captions_download` Layer 2 tool is discoverable, quota/auth/permission/conversion-visible, metadata-safe, endpoint-backed, and still aligned with the existing Layer 1 `captions.download` wrapper and shared Layer 2 contracts.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`
- Use branch `207-captions-download`
- Review:
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/spec.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/207-captions-download/contracts/captions-download-tool-contract.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/107-captions-download/`

## Red Phase

1. Add focused failing tests that prove `captions_download` is not yet discoverable as a public executable Layer 2 tool.
2. Add failing metadata checks requiring:
   - public name `captions_download`
   - upstream identity `captions.download`
   - quota cost `200`
   - OAuth-required auth
   - permission-to-edit caveat
   - required caption track `id`
   - optional `tfmt` values `sbv`, `scc`, `srt`, `ttml`, and `vtt`
   - optional `tlang` ISO 639-1-style language guidance
   - delegated content-owner caveat
   - binary downloaded-content response context
   - usage notes with `Quota cost: 200`
3. Add failing request validation checks for:
   - missing `id`
   - blank `id`
   - unsupported `tfmt`
   - malformed `tlang`
   - unsupported fields
   - missing OAuth authorization
   - delegated content-owner context without eligible authorization
4. Add failing result checks for:
   - downloaded caption content or supported safe content representation
   - content type or content-form indicator
   - requested format and requested language context
   - endpoint identity and quota cost
   - safe download summary
   - safe delegation summary when supplied
   - safe error categories

Suggested focused command while tests are red:

```bash
python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Green Phase

1. Add the minimum `captions_download` public tool definition, input schema, metadata, usage notes, and handler adapter.
2. Register the tool through the existing dispatcher-compatible path.
3. Use the existing Layer 1 `captions.download` wrapper for endpoint behavior.
4. Preserve near-raw downloaded-content results with caption track id, requested `tfmt`, requested `tlang`, endpoint identity, quota cost, safe download summary, safe content-form indicators, and safe delegation context.
5. Map invalid requests, OAuth failures, delegation failures, missing captions, insufficient permissions, upstream `couldNotConvert`, upstream `captionNotFound`, upstream `forbidden`, unavailable service, quota exhaustion, and unexpected upstream failures to shared safe error categories.
6. Add reStructuredText docstrings to every new or changed Python function.

Run focused checks:

```bash
python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

If Layer 1 wrapper code changes, also run:

```bash
python3 -m pytest tests/contract/test_layer1_captions_contract.py tests/unit/test_layer1_foundation.py
```

If dispatcher discovery or MCP routing changes, also run:

```bash
python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py
```

## Refactor Phase

1. Remove duplication with YT-201/YT-202 shared contracts and helpers.
2. Keep endpoint-specific behavior limited to `captions_download`.
3. Confirm public examples, metadata, errors, and logs contain no credentials, tokens, stack traces, signed URLs, secret values, raw private caption content, or binary payloads.
4. Confirm no Layer 3 transcript summarization, caption listing, caption creation, caption update, caption deletion, language ranking, enrichment, local translation, or heuristic behavior was introduced.
5. Re-run focused checks after cleanup.

Final required validation:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Manual Review Checklist

- `captions_download` appears in tool discovery or registration artifacts.
- Discovery metadata includes upstream identity `captions.download`.
- Description and examples include `Quota cost: 200`.
- Auth metadata says `oauth_required`.
- Permission guidance states that caption download requires eligible access and permission to edit the video.
- `id` is required and represents the caption track identifier.
- `tfmt` is optional and limited to `sbv`, `scc`, `srt`, `ttml`, and `vtt`.
- `tlang` is optional and documented as an ISO 639-1-style two-letter language code.
- `onBehalfOfContentOwner` is documented as optional delegation context requiring eligible OAuth authorization.
- Downloaded-content fields preserve content form, requested conversion context, endpoint identity, and quota cost.
- Upstream `couldNotConvert`, `forbidden`, and `captionNotFound` outcomes map to safe caller-facing categories.
- Error details are safe for MCP clients.
- Every new or changed Python function has a reStructuredText docstring.

## Implementation Evidence

- Focused YT-207 validation on 2026-06-02:
  `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py`
  passed with 198 tests.
- Secret and content-safety review found only safe placeholder auth parameter names and existing API-key auth-mode labels; no API keys, OAuth token values, stack traces in public output, signed URLs, raw private caption content, binary payloads, or secret values were added.
- Docstring review confirmed every new or changed `captions_download` function and class has a reStructuredText docstring.
- Full repository validation on 2026-06-02: `python3 -m pytest` passed with 1711 tests.
- Code-quality validation on 2026-06-02: `python3 -m ruff check .` passed with no findings.
