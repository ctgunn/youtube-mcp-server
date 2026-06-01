# Quickstart: YT-205 Layer 2 Tool `captions_insert`

## Goal

Verify that the planned `captions_insert` Layer 2 tool is discoverable, quota/auth/upload-visible, metadata-safe, endpoint-backed, and still aligned with the existing Layer 1 `captions.insert` wrapper and shared Layer 2 contracts.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`
- Use branch `205-captions-insert`
- Review:
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/spec.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/205-captions-insert/contracts/captions-insert-tool-contract.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/105-captions-insert/`

## Red Phase

1. Add focused failing tests that prove `captions_insert` is not yet discoverable as a public executable Layer 2 tool.
2. Add failing metadata checks requiring:
   - public name `captions_insert`
   - upstream identity `captions.insert`
   - quota cost `400`
   - OAuth-required auth
   - media-upload requirement
   - caption metadata requirements
   - delegated content-owner caveat
   - deprecated `sync` caveat when supported
   - usage notes with `Quota cost: 400`
3. Add failing request validation checks for:
   - missing `part`
   - missing `body`
   - missing `body.snippet.videoId`
   - missing `body.snippet.language`
   - missing `body.snippet.name`
   - missing `media`
   - unsupported media descriptors
   - unsupported fields
   - missing OAuth authorization
   - delegated content-owner context without eligible authorization
4. Add failing result checks for:
   - returned created caption resource
   - requested parts
   - safe metadata summary
   - safe media summary without raw content
   - endpoint identity and quota cost
   - safe error categories

Suggested focused command while tests are red:

```bash
python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Green Phase

1. Add the minimum `captions_insert` public tool definition, input schema, metadata, usage notes, and handler adapter.
2. Register the tool through the existing dispatcher-compatible path.
3. Use the existing Layer 1 `captions.insert` wrapper for endpoint behavior.
4. Preserve near-raw created caption-resource results with requested parts, endpoint identity, quota cost, safe metadata summary, safe media summary, and safe delegation context.
5. Map invalid requests, OAuth failures, delegation failures, duplicate-caption conflicts, media-upload failures, and upstream failures to shared safe error categories.
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
2. Keep endpoint-specific behavior limited to `captions_insert`.
3. Confirm public examples, metadata, errors, and logs contain no credentials, tokens, stack traces, signed URLs, secret values, caption file contents, or raw media payloads.
4. Confirm no Layer 3 transcript download, language ranking, enrichment, translation, or heuristic behavior was introduced.
5. Re-run focused checks after cleanup.

Final required validation:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Manual Review Checklist

- `captions_insert` appears in tool discovery or registration artifacts.
- Discovery metadata includes upstream identity `captions.insert`.
- Description and examples include `Quota cost: 400`.
- Auth metadata says `oauth_required`.
- `part`, caption metadata body, and caption media input are required.
- `body.snippet.videoId`, `body.snippet.language`, and `body.snippet.name` are required.
- `onBehalfOfContentOwner` is documented as optional delegation context requiring eligible OAuth authorization.
- `sync`, if accepted, is marked deprecated and is not promoted as the normal path.
- Created caption-resource fields are preserved.
- Error details are safe for MCP clients.
- Every new or changed Python function has a reStructuredText docstring.

## Implementation Evidence

- Focused captions, catalog, discovery, registration, and routing checks passed with `94 passed`.
- Ruff validation passed with `python3 -m ruff check .`.
- Layer 1 caption wrapper code was not changed for this slice; the Layer 2 tool reuses the existing `captions.insert` wrapper.
- Public examples and tests use safe placeholder caption content and do not include real credentials, tokens, signed URLs, or private caption files.
