# Quickstart: YT-206 Layer 2 Tool `captions_update`

## Goal

Verify that the planned `captions_update` Layer 2 tool is discoverable, quota/auth/update/media-visible, metadata-safe, endpoint-backed, and still aligned with the existing Layer 1 `captions.update` wrapper and shared Layer 2 contracts.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`
- Use branch `206-captions-update`
- Review:
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/spec.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/206-captions-update/contracts/captions-update-tool-contract.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/106-captions-update/`

## Red Phase

1. Add focused failing tests that prove `captions_update` is not yet discoverable as a public executable Layer 2 tool.
2. Add failing metadata checks requiring:
   - public name `captions_update`
   - upstream identity `captions.update`
   - quota cost `450`
   - OAuth-required auth
   - required update body
   - optional media-replacement support
   - delegated content-owner caveat
   - deprecated `sync` caveat when supported
   - usage notes with `Quota cost: 450`
3. Add failing request validation checks for:
   - missing `part`
   - missing `body`
   - missing `body.id`
   - media without body
   - unsupported media descriptors
   - unsupported fields
   - missing OAuth authorization
   - delegated content-owner context without eligible authorization
   - deprecated `sync` supplied in an unsupported shape
4. Add failing result checks for:
   - returned updated caption resource
   - requested parts
   - safe update summary
   - safe media summary without raw content when media is supplied
   - endpoint identity and quota cost
   - safe error categories

Suggested focused command while tests are red:

```bash
python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Green Phase

1. Add the minimum `captions_update` public tool definition, input schema, metadata, usage notes, and handler adapter.
2. Register the tool through the existing dispatcher-compatible path.
3. Use the existing Layer 1 `captions.update` wrapper for endpoint behavior.
4. Preserve near-raw updated caption-resource results with requested parts, endpoint identity, quota cost, safe update summary, safe media summary when media is supplied, and safe delegation context.
5. Map invalid requests, OAuth failures, delegation failures, missing captions, media-upload failures, upstream `contentRequired`, and unexpected upstream failures to shared safe error categories.
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
2. Keep endpoint-specific behavior limited to `captions_update`.
3. Confirm public examples, metadata, errors, and logs contain no credentials, tokens, stack traces, signed URLs, secret values, caption file contents, or raw media payloads.
4. Confirm no Layer 3 transcript download, caption creation, language ranking, enrichment, translation, or heuristic behavior was introduced.
5. Re-run focused checks after cleanup.

Final required validation:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Implementation Evidence

- Focused YT-206 validation on 2026-06-01:
  `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py`
  passed with 174 tests.
- Secret and content-safety review found only safe placeholder OAuth parameter names and deliberate sanitizer fixtures; no API keys, OAuth tokens, stack traces in public output, signed URLs, raw media payloads, caption file contents, or secret values were added.
- Docstring review confirmed every new or changed `captions_update` function and class has a reStructuredText docstring.
- Full repository validation on 2026-06-01: `python3 -m pytest` passed with 1675 tests.
- Code-quality validation on 2026-06-01: `python3 -m ruff check .` passed with no findings.

## Manual Review Checklist

- `captions_update` appears in tool discovery or registration artifacts.
- Discovery metadata includes upstream identity `captions.update`.
- Description and examples include `Quota cost: 450`.
- Auth metadata says `oauth_required`.
- `part` and caption update body are required.
- `body.id` is required.
- `body.snippet.isDraft` is supported where draft-status updates are supported.
- Replacement `media` is optional and only accepted with a valid update body.
- `onBehalfOfContentOwner` is documented as optional delegation context requiring eligible OAuth authorization.
- `sync`, if accepted, is marked deprecated and is not promoted as the normal path.
- Updated caption-resource fields are preserved.
- Error details are safe for MCP clients.
- Every new or changed Python function has a reStructuredText docstring.
