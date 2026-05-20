# Quickstart: YT-156 Layer 1 Resource-Family Module Reorganization

## Purpose

Use this feature to reorganize completed Layer 1 YouTube Data API endpoint integration code into resource-family modules while preserving endpoint behavior, compatibility imports, auth semantics, quota metadata, request shapes, response shapes, and normalized upstream failure behavior.

## Prerequisites

- Work from `/Users/ctgunn/Projects/youtube-mcp-server` on branch `156-layer1-resource-modules`
- Keep the slice internal to Layer 1; do not add public MCP tools in this feature
- Preserve existing imports from `mcp_server.integrations`, `mcp_server.integrations.wrappers`, and `mcp_server.integrations.youtube`
- Preserve the existing shared executor, auth context, retry, observability, request-construction, and normalized error patterns
- Add or preserve reStructuredText docstrings for every new or changed Python function

## Red Phase

1. Add failing or characterization tests proving representative resource families do not yet have dedicated module access for wrapper builders, metadata, validators, and response normalizers.
2. Add failing compatibility tests proving the old import paths and new resource-family access paths must expose equivalent wrapper capabilities.
3. Add failing or characterization transport tests proving response-normalizer selection must remain equivalent when moved from broad conditional handling to explicit dispatch.
4. Add failing or characterization contract checks for representative endpoint families covering list-only, mutation, upload, delete, mixed-auth, OAuth-only, API-key, and conditional-selector behavior.

Initial setup Red evidence captured on 2026-05-20:

```text
python3 -m pytest tests/contract/test_layer1_resource_modules_contract.py tests/unit/test_layer1_resource_modules.py
Result: 1 failed, 4 passed
Failure: mcp_server.integrations.resources does not yet expose REQUIRED_RESOURCE_FAMILIES.
```

## Green Phase

1. Create the resource-family package under the existing integration layer.
2. Move one resource family at a time, starting with a small representative family before families with more endpoints or upload/mutation behavior.
3. Re-export moved wrapper classes and builder functions through compatibility facades.
4. Group endpoint-specific response normalizers by family and register them through explicit dispatch.
5. Keep shared foundations centralized and imported rather than duplicated.
6. Preserve all endpoint metadata values, request validation rules, auth behavior, quota visibility, response shapes, and normalized failure behavior.
7. Keep secrets, credentials, channel-owner identity, delegated-owner credentials, and raw media payloads out of docs, logs, normalized results, and tests.

## Refactor Phase

1. Remove duplicate transitional definitions after each family move once compatibility exports are green.
2. Tighten import boundaries to avoid circular dependencies through `mcp_server.integrations.__init__`.
3. Keep `wrappers.py` and `youtube.py` as compatibility facades or narrow shared modules rather than broad resource-owner files.
4. Align names, docstrings, and review surfaces so resource-family ownership is easy to audit.
5. Run focused Layer 1 tests after practical groups, then complete full repository verification.

## Suggested Verification Commands

From `/Users/ctgunn/Projects/youtube-mcp-server`:

```bash
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_activities_contract.py tests/contract/test_layer1_captions_contract.py tests/contract/test_layer1_channels_contract.py tests/contract/test_layer1_comments_contract.py tests/contract/test_layer1_playlist_items_contract.py tests/contract/test_layer1_videos_contract.py tests/contract/test_layer1_watermarks_contract.py tests/contract/test_layer1_metadata_contract.py tests/contract/test_layer1_consumer_contract.py
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_*_contract.py
python3 -m pytest
python3 -m ruff check .
```

Final implementation verification evidence captured on 2026-05-20:

```text
python3 -m pytest tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_*_contract.py
Result: 749 passed
python3 -m pytest tests/unit/test_layer1_foundation.py tests/unit/test_layer1_resource_modules.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_*_contract.py
Result: 1171 passed
python3 -m pytest
Result: 1502 passed
python3 -m ruff check .
Result: All checks passed
```

Public MCP and hosted transport review: implementation changes are confined to the internal Layer 1 integration package and Layer 1 tests/docs. No public MCP tool registration, hosted route, FastAPI endpoint, or MCP transport surface was added or changed.

## Review Checklist

- Resource-family modules exist for every family in the YT-156 scope
- Existing compatibility imports continue to resolve
- Old and new access paths expose equivalent wrapper review surfaces
- Response normalizer dispatch is explicit and auditable
- Shared foundations remain centralized
- No endpoint contract intentionally changes
- Resource-family tests cover representative behavior before and after moves
- New or changed Python functions have reStructuredText docstrings
- No public MCP tool or hosted transport behavior is introduced
- Final evidence includes `python3 -m pytest` and `python3 -m ruff check .`
