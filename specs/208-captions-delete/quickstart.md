# Quickstart: YT-208 Layer 2 Tool `captions_delete`

## Goal

Verify that the planned `captions_delete` Layer 2 tool is discoverable, quota/auth/deletion/delegation-visible, metadata-safe, endpoint-backed, and still aligned with the existing Layer 1 `captions.delete` wrapper and shared Layer 2 contracts.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server`
- Use branch `208-captions-delete`
- Review:
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/spec.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/208-captions-delete/contracts/captions-delete-tool-contract.md`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/201-layer2-shared-contracts/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/202-layer2-metadata-standards/`
  - `/Users/ctgunn/Projects/youtube-mcp-server/specs/108-captions-delete/`

## Red Phase

1. Add focused failing tests that prove `captions_delete` is not yet discoverable as a public executable Layer 2 tool.
2. Add failing metadata checks requiring:
   - public name `captions_delete`
   - upstream identity `captions.delete`
   - quota cost `50`
   - OAuth-required auth
   - required caption track `id`
   - optional `onBehalfOfContentOwner` delegation caveat
   - no request body
   - destructive deletion behavior
   - no-content deletion acknowledgment response context
   - usage notes with `Quota cost: 50`
3. Add failing request validation checks for:
   - missing `id`
   - blank `id`
   - unsupported fields
   - request body or unsupported deletion options
   - missing OAuth authorization
   - delegated content-owner context without eligible authorization
4. Add failing result checks for:
   - deletion acknowledgment
   - endpoint identity and quota cost
   - safe caption track id summary
   - no-body success context
   - safe delegation summary when supplied
   - no fabricated deleted caption resource fields
   - safe error categories

Suggested focused command while tests are red:

```bash
python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py
```

## Green Phase

1. Add the minimum `captions_delete` public tool definition, input schema, metadata, usage notes, and handler adapter.
2. Register the tool through the existing dispatcher-compatible path.
3. Use the existing Layer 1 `captions.delete` wrapper for endpoint behavior.
4. Preserve near-raw deletion acknowledgment results with caption track id, endpoint identity, quota cost, safe deletion summary, no-body success indicators, and safe delegation context.
5. Map invalid requests, OAuth failures, delegation failures, missing captions, insufficient permissions, upstream `captionNotFound`, upstream `forbidden`, unavailable service, quota exhaustion, and unexpected upstream failures to shared safe error categories.
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
2. Keep endpoint-specific behavior limited to `captions_delete`.
3. Confirm public examples, metadata, errors, and logs contain no credentials, tokens, stack traces, signed URLs, secret values, raw private caption content, binary payloads, deleted-resource internals, or sensitive delegated-owner details.
4. Confirm no Layer 3 transcript summarization, caption listing, caption creation, caption update, caption download, deletion undo, recovery, language ranking, enrichment, local translation, or heuristic behavior was introduced.
5. Re-run focused checks after cleanup.

Final required validation:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Manual Review Checklist

- `captions_delete` appears in tool discovery or registration artifacts.
- Discovery metadata includes upstream identity `captions.delete`.
- Description and examples include `Quota cost: 50`.
- Auth metadata says `oauth_required`.
- `id` is required and represents the caption track identifier.
- `onBehalfOfContentOwner` is documented as optional delegation context requiring eligible OAuth authorization.
- No request body is accepted.
- Destructive deletion behavior is visible before invocation.
- Successful result shape acknowledges deletion and no-body upstream success without fabricating deleted resource data.
- Upstream `forbidden` and `captionNotFound` outcomes map to safe caller-facing categories.
- Error details are safe for MCP clients.
- Every new or changed Python function has a reStructuredText docstring.

## Implementation Evidence

- Focused YT-208 validation: `python3 -m pytest tests/unit/test_youtube_captions.py tests/contract/test_youtube_captions_contract.py tests/integration/test_youtube_captions_registration.py tests/unit/test_youtube_common_scaffolding.py tests/contract/test_youtube_common_contract.py tests/contract/test_youtube_tool_catalog_contract.py tests/integration/test_youtube_tool_registration.py` passed with 205 tests.
- Dispatcher routing guard: `python3 -m pytest tests/unit/test_list_tools_method.py tests/unit/test_method_routing.py tests/integration/test_mcp_request_flow.py` passed with 37 tests because dispatcher discovery changed.
- Layer 1 guard: not rerun as a separate focused command because `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/resources/captions.py` was not changed; the full repository run covered Layer 1 tests.
- Full suite: `python3 -m pytest` passed with 1,743 tests.
- Lint: `python3 -m ruff check .` passed.
- Safety review: public metadata, examples, errors, and touched tests were reviewed for secret-bearing fields, raw private caption content, binary payload exposure, and deleted-resource internals; only expected auth-mode/test-fixture vocabulary and explicit negative assertions were present.
- Docstring review: AST scan of touched Python files reported every function has a reStructuredText docstring.
